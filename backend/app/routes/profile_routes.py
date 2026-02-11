"""
Async Profile management routes for MongoDB/Beanie.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from app.models import User, UserProfile
from app.schemas import ProfileCreate, ProfileUpdate, ProfileResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """Get the current user's profile from MongoDB."""
    profile = await UserProfile.find_one(UserProfile.user_id == str(current_user.id))
    if not profile:
        # Fallback: create empty profile if missing
        profile = UserProfile(user_id=str(current_user.id), email=current_user.email)
        await profile.insert()
    
    # Map _id manually for the response model if necessary (handled by alias)
    # We return the object directly; Beanie/Pydantic v2 handles alias automatically
    return profile


@router.post("/", response_model=ProfileResponse)
async def create_or_update_profile(
    data: ProfileCreate,
    current_user: User = Depends(get_current_user),
):
    """Create or replace user profile in MongoDB."""
    profile = await UserProfile.find_one(UserProfile.user_id == str(current_user.id))
    
    if profile:
        # Update existing using Pydantic model_dump
        update_data = data.model_dump()
        update_data["updated_at"] = datetime.utcnow()
        await profile.set(update_data)
    else:
        # Create new
        profile = UserProfile(user_id=str(current_user.id), **data.model_dump())
        await profile.insert()
        
    return profile


@router.put("/", response_model=ProfileResponse)
async def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update user profile fields in MongoDB."""
    profile = await UserProfile.find_one(UserProfile.user_id == str(current_user.id))
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Create one first.")

    update_data = data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    await profile.set(update_data)
    
    return profile
