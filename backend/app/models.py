"""
Beanie MongoDB models for the application.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field, EmailStr


class User(Document):
    """User authentication model."""
    username: Indexed(str, unique=True)
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"


class UserProfile(Document):
    """User profile data used for form filling."""
    user_id: Indexed(str, unique=True)  # Link to User ID
    
    # Required fields
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

    # Extra fields for flexibility
    extra_fields: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "user_profiles"


class FormHistory(Document):
    """History of filled Google Forms."""
    user_id: Indexed(str)
    form_url: str
    form_title: str = ""
    status: str = "pending"  # pending, filling, completed, failed
    questions_detected: int = 0
    questions_filled: int = 0
    ai_answers_used: int = 0
    auto_submitted: bool = False
    error_message: str = ""
    fill_log: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Settings:
        name = "form_history"


class LearnedMapping(Document):
    """Learned question-to-field mappings for smarter future filling."""
    user_id: Indexed(str)
    question_text: str
    matched_field: str  # Profile field name or "ai_generated"
    answer_value: str = ""
    confidence: int = 100  # 0-100
    times_used: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "learned_mappings"
