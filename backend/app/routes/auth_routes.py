"""
Async Authentication routes for MongoDB/Beanie.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.models import User, UserProfile
from app.schemas import UserSignup, UserLogin, TokenResponse, UserResponse
from app.auth import create_access_token, get_current_user
from app.utils.security import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: UserSignup):
    """Register a new user in MongoDB."""
    # Check if username or email already exists
    existing_username = await User.find_one(User.username == data.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    existing_email = await User.find_one(User.email == data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    await user.insert()

    # Create empty profile
    profile = UserProfile(user_id=str(user.id), email=data.email)
    await profile.insert()

    # Generate token
    token = create_access_token({"user_id": str(user.id), "username": user.username})
    return TokenResponse(
        access_token=token,
        username=user.username,
        user_id=str(user.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """Authenticate and return access token from MongoDB."""
    user = await User.find_one(User.username == data.username)
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token({"user_id": str(user.id), "username": user.username})
    return TokenResponse(
        access_token=token,
        username=user.username,
        user_id=str(user.id),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info (Async version)."""
    # Check if profile exists and is filled
    profile = await UserProfile.find_one(UserProfile.user_id == str(current_user.id))
    
    # We map the _id manually to id if needed, but UserResponse schema handles it with alias
    return UserResponse(
        _id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        has_profile=profile is not None and bool(profile.full_name),
    )
