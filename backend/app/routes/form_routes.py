"""
Async Form filling routes for MongoDB/Beanie.
"""
import asyncio
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.models import User, UserProfile, FormHistory, LearnedMapping
from app.schemas import FormFillRequest, FormFillStatusResponse, FormHistoryResponse, LearnedMappingResponse
from app.auth import get_current_user
from app.services.form_filler import FormFillerEngine
from app.services.ai_agent import get_profile_as_dict

router = APIRouter(prefix="/api/forms", tags=["Forms"])


async def _run_form_fill(user_id: str, form_url: str, auto_submit: bool, history_id: str):
    """Async Background task to run form filling."""
    try:
        # Get profile
        profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        if not profile:
            history = await FormHistory.get(history_id)
            if history:
                await history.set({
                    "status": "failed",
                    "error_message": "No profile found. Please set up your profile first.",
                    "completed_at": datetime.utcnow()
                })
            return

        # Prepare data for engine
        profile_data = get_profile_as_dict(profile)

        # Get learned mappings
        mappings = await LearnedMapping.find(LearnedMapping.user_id == user_id).to_list()
        learned = {m.question_text: m.answer_value for m in mappings}

        # Run form filler engine
        engine = FormFillerEngine(profile_data, learned)
        result = await engine.fill_form(form_url, auto_submit)

        # Update history
        history = await FormHistory.get(history_id)
        if history:
            await history.set({
                "status": result["status"],
                "form_title": result["form_title"],
                "questions_detected": result["questions_detected"],
                "questions_filled": result["questions_filled"],
                "ai_answers_used": result["ai_answers_used"],
                "auto_submitted": result["auto_submitted"],
                "error_message": result.get("error_message", ""),
                "fill_log": result["fill_log"],
                "completed_at": datetime.utcnow()
            })

        # Save new learned mappings
        for m_data in result.get("new_mappings", []):
            existing = await LearnedMapping.find_one(
                LearnedMapping.user_id == user_id,
                LearnedMapping.question_text == m_data["question"]
            )
            if existing:
                await existing.set({
                    "answer_value": m_data["value"],
                    "matched_field": m_data["field"],
                    "confidence": m_data["confidence"],
                    "times_used": existing.times_used + 1,
                    "updated_at": datetime.utcnow()
                })
            else:
                new_map = LearnedMapping(
                    user_id=user_id,
                    question_text=m_data["question"],
                    matched_field=m_data["field"],
                    answer_value=m_data["value"],
                    confidence=m_data["confidence"]
                )
                await new_map.insert()

    except Exception as e:
        print(f"❌ Background Fill Error: {e}")
        history = await FormHistory.get(history_id)
        if history:
            await history.set({
                "status": "failed",
                "error_message": str(e),
                "completed_at": datetime.utcnow()
            })


@router.post("/fill", response_model=FormFillStatusResponse)
async def start_form_fill(
    data: FormFillRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """Start filling a Google Form using MongoDB."""
    # Validate form URL
    if "docs.google.com/forms" not in data.form_url:
        raise HTTPException(status_code=400, detail="Invalid Google Form URL.")

    # Check profile exists
    profile = await UserProfile.find_one(UserProfile.user_id == str(current_user.id))
    if not profile or not profile.full_name:
        raise HTTPException(status_code=400, detail="Please set up your profile before filling forms.")

    # Create history entry
    history = FormHistory(
        user_id=str(current_user.id),
        form_url=data.form_url,
        status="filling",
        auto_submitted=data.auto_submit,
    )
    await history.insert()

    # Run in background
    background_tasks.add_task(
        _run_form_fill,
        str(current_user.id),
        data.form_url,
        data.auto_submit,
        str(history.id),
    )

    return history


@router.get("/status/{history_id}", response_model=FormFillStatusResponse)
async def get_fill_status(
    history_id: str,
    current_user: User = Depends(get_current_user),
):
    """Check fill status in MongoDB."""
    history = await FormHistory.find_one(
        FormHistory.id == history_id,
        FormHistory.user_id == str(current_user.id)
    )
    if not history:
        raise HTTPException(status_code=404, detail="Fill record not found")
    return history


@router.get("/history", response_model=FormHistoryResponse)
async def get_form_history(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
):
    """Get history from MongoDB."""
    query = FormHistory.find(FormHistory.user_id == str(current_user.id))
    total = await query.count()
    items = await query.sort("-created_at").skip(skip).limit(limit).to_list()
    return FormHistoryResponse(items=items, total=total)


@router.get("/mappings", response_model=List[LearnedMappingResponse])
async def get_learned_mappings(
    current_user: User = Depends(get_current_user),
):
    """Get all mappings from MongoDB."""
    mappings = await LearnedMapping.find(
        LearnedMapping.user_id == str(current_user.id)
    ).sort("-times_used").to_list()
    return mappings


@router.delete("/mappings/{mapping_id}")
async def delete_mapping(
    mapping_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a mapping in MongoDB."""
    mapping = await LearnedMapping.find_one(
        LearnedMapping.id == mapping_id,
        LearnedMapping.user_id == str(current_user.id)
    )
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    await mapping.delete()
    return {"message": "Mapping deleted"}
