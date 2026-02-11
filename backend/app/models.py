"""
SQLAlchemy ORM models for the application.
"""
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """User authentication model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    form_history = relationship("FormHistory", back_populates="user", cascade="all, delete-orphan")
    learned_mappings = relationship("LearnedMapping", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    """User profile data used for form filling."""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Required fields
    full_name = Column(String(255), default="")
    register_number = Column(String(100), default="")
    department = Column(String(200), default="")
    year = Column(String(50), default="")
    email = Column(String(255), default="")
    phone = Column(String(50), default="")
    gender = Column(String(50), default="")
    college_name = Column(String(300), default="")
    address = Column(Text, default="")
    skills = Column(Text, default="")
    interests = Column(Text, default="")
    bio = Column(Text, default="")

    # Extra fields stored as JSON for flexibility
    extra_fields = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")


class FormHistory(Base):
    """History of filled Google Forms."""
    __tablename__ = "form_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    form_url = Column(String(500), nullable=False)
    form_title = Column(String(500), default="")
    status = Column(String(50), default="pending")  # pending, filling, completed, failed
    questions_detected = Column(Integer, default=0)
    questions_filled = Column(Integer, default=0)
    ai_answers_used = Column(Integer, default=0)
    auto_submitted = Column(Boolean, default=False)
    error_message = Column(Text, default="")
    fill_log = Column(JSON, default=list)  # Detailed log of each field
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="form_history")


class LearnedMapping(Base):
    """Learned question-to-field mappings for smarter future filling."""
    __tablename__ = "learned_mappings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_text = Column(String(500), nullable=False)
    matched_field = Column(String(100), nullable=False)  # Profile field name or "ai_generated"
    answer_value = Column(Text, default="")
    confidence = Column(Integer, default=100)  # 0-100
    times_used = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="learned_mappings")
