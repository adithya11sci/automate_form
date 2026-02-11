"""
Form filling routes — submit form link, check status, view history.
"""
import asyncio
import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserProfile, FormHistory, LearnedMapping
from app.schemas import FormFillRequest, FormFillStatusResponse, FormHistoryResponse, LearnedMappingResponse
from app.auth import get_current_user
from app.services.form_filler import FormFillerEngine
from app.services.ai_agent import get_profile_as_dict

router = APIRouter(prefix="/api/forms", tags=["Forms"])


def _run_form_fill(user_id: int, form_url: str, auto_submit: bool, history_id: int):
    """Background task to run form filling."""
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        # Get profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            history = db.query(FormHistory).filter(FormHistory.id == history_id).first()
            if history:
                history.status = "failed"
                history.error_message = "No profile found. Please set up your profile first."
                db.commit()
            return

        profile_data = get_profile_as_dict(profile)

        # Get learned mappings
        mappings = db.query(LearnedMapping).filter(LearnedMapping.user_id == user_id).all()
        learned = {m.question_text: m.answer_value for m in mappings}

        # Run form filler
        engine = FormFillerEngine(profile_data, learned)
        result = asyncio.run(engine.fill_form(form_url, auto_submit))

        # Update history
        history = db.query(FormHistory).filter(FormHistory.id == history_id).first()
        if history:
            history.status = result["status"]
            history.form_title = result["form_title"]
            history.questions_detected = result["questions_detected"]
            history.questions_filled = result["questions_filled"]
            history.ai_answers_used = result["ai_answers_used"]
            history.auto_submitted = result["auto_submitted"]
            history.error_message = result.get("error_message", "")
            history.fill_log = result["fill_log"]
            history.completed_at = datetime.datetime.utcnow()
            db.commit()

        # Save new learned mappings
        for mapping in result.get("new_mappings", []):
            existing = db.query(LearnedMapping).filter(
                LearnedMapping.user_id == user_id,
                LearnedMapping.question_text == mapping["question"],
            ).first()
            if existing:
                existing.answer_value = mapping["value"]
                existing.matched_field = mapping["field"]
                existing.confidence = mapping["confidence"]
                existing.times_used += 1
            else:
                new_map = LearnedMapping(
                    user_id=user_id,
                    question_text=mapping["question"],
                    matched_field=mapping["field"],
                    answer_value=mapping["value"],
                    confidence=mapping["confidence"],
                )
                db.add(new_map)
        db.commit()

    except Exception as e:
        history = db.query(FormHistory).filter(FormHistory.id == history_id).first()
        if history:
            history.status = "failed"
            history.error_message = str(e)
            history.completed_at = datetime.datetime.utcnow()
            db.commit()
    finally:
        db.close()


@router.post("/fill", response_model=FormFillStatusResponse)
def start_form_fill(
    data: FormFillRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start filling a Google Form (runs in background)."""
    # Validate form URL
    if "docs.google.com/forms" not in data.form_url:
        raise HTTPException(status_code=400, detail="Invalid Google Form URL. Must contain 'docs.google.com/forms'.")

    # Check profile exists
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile or not profile.full_name:
        raise HTTPException(status_code=400, detail="Please set up your profile before filling forms.")

    # Create history entry
    history = FormHistory(
        user_id=current_user.id,
        form_url=data.form_url,
        status="filling",
        auto_submitted=data.auto_submit,
    )
    db.add(history)
    db.commit()
    db.refresh(history)

    # Run in background
    background_tasks.add_task(
        _run_form_fill,
        current_user.id,
        data.form_url,
        data.auto_submit,
        history.id,
    )

    return history


@router.get("/status/{history_id}", response_model=FormFillStatusResponse)
def get_fill_status(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check the status of a form fill operation."""
    history = db.query(FormHistory).filter(
        FormHistory.id == history_id,
        FormHistory.user_id == current_user.id,
    ).first()
    if not history:
        raise HTTPException(status_code=404, detail="Form fill record not found")
    return history


@router.get("/history", response_model=FormHistoryResponse)
def get_form_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
):
    """Get form fill history for current user."""
    query = db.query(FormHistory).filter(FormHistory.user_id == current_user.id)
    total = query.count()
    items = query.order_by(FormHistory.created_at.desc()).offset(skip).limit(limit).all()
    return FormHistoryResponse(items=items, total=total)


@router.get("/mappings", response_model=List[LearnedMappingResponse])
def get_learned_mappings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all learned question-answer mappings for current user."""
    mappings = db.query(LearnedMapping).filter(
        LearnedMapping.user_id == current_user.id
    ).order_by(LearnedMapping.times_used.desc()).all()
    return mappings


@router.delete("/mappings/{mapping_id}")
def delete_mapping(
    mapping_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a learned mapping."""
    mapping = db.query(LearnedMapping).filter(
        LearnedMapping.id == mapping_id,
        LearnedMapping.user_id == current_user.id,
    ).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    db.delete(mapping)
    db.commit()
    return {"message": "Mapping deleted"}
