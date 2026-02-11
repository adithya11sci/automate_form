"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime


# ─── Auth Schemas ────────────────────────────────────────────
class UserSignup(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    user_id: int


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    has_profile: bool = False

    class Config:
        from_attributes = True


# ─── Profile Schemas ────────────────────────────────────────
class ProfileCreate(BaseModel):
    full_name: str = ""
    register_number: str = ""
    department: str = ""
    year: str = ""
    email: str = ""
    phone: str = ""
    gender: str = ""
    college_name: str = ""
    address: str = ""
    skills: str = ""
    interests: str = ""
    bio: str = ""
    extra_fields: dict = {}


class ProfileUpdate(ProfileCreate):
    pass


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    register_number: str
    department: str
    year: str
    email: str
    phone: str
    gender: str
    college_name: str
    address: str
    skills: str
    interests: str
    bio: str
    extra_fields: dict
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Form Schemas ────────────────────────────────────────────
class FormFillRequest(BaseModel):
    form_url: str = Field(..., min_length=10)
    auto_submit: bool = False


class FormFillStatusResponse(BaseModel):
    id: int
    form_url: str
    form_title: str
    status: str
    questions_detected: int
    questions_filled: int
    ai_answers_used: int
    auto_submitted: bool
    error_message: str
    fill_log: List[Any]
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FormHistoryResponse(BaseModel):
    items: List[FormFillStatusResponse]
    total: int


# ─── Learned Mapping Schemas ────────────────────────────────
class LearnedMappingResponse(BaseModel):
    id: int
    question_text: str
    matched_field: str
    answer_value: str
    confidence: int
    times_used: int

    class Config:
        from_attributes = True
