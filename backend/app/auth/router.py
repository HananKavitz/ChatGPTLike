"""Authentication endpoints"""
import logging
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import User
from ..schemas import Token, UserLogin, UserRegister, UserResponse, UserUpdate
from ..auth.dependencies import get_current_user
from ..auth.security import create_access_token, get_password_hash, verify_password

logger = logging.getLogger(__name__)


class ApiKeyVerify(BaseModel):
    """Schema for API key verification"""
    api_key: str
    provider: str = "openai"  # 'openai' or 'anthropic'

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        openai_model=settings.OPENAI_DEFAULT_MODEL
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()

    # Verify credentials
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user settings"""
    if user_update.llm_provider is not None:
        current_user.llm_provider = user_update.llm_provider

    if user_update.openai_api_key is not None:
        current_user.openai_api_key = user_update.openai_api_key

    if user_update.openai_model is not None:
        current_user.openai_model = user_update.openai_model

    if user_update.anthropic_api_key is not None:
        current_user.anthropic_api_key = user_update.anthropic_api_key

    if user_update.anthropic_model is not None:
        current_user.anthropic_model = user_update.anthropic_model

    if user_update.openrouter_api_key is not None:
        current_user.openrouter_api_key = user_update.openrouter_api_key

    if user_update.openrouter_model is not None:
        current_user.openrouter_model = user_update.openrouter_model

    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/verify-api-key")
async def verify_api_key(
    verify_data: ApiKeyVerify,
    current_user: User = Depends(get_current_user)
):
    """Verify if an LLM API key is valid"""
    logger.info(f"Verifying {verify_data.provider} API key for user {current_user.id}")

    try:
        from ..chat.providers.factory import LLMProviderFactory

        # Create a provider instance for verification
        provider = LLMProviderFactory.create(verify_data.provider, verify_data.api_key)

        # Verify the key
        is_valid = await provider.verify_api_key()

        if is_valid:
            logger.info(f"{verify_data.provider} API key verification successful for user {current_user.id}")
            return {
                "valid": True,
                "message": f"{verify_data.provider.capitalize()} API key is valid",
                "provider": verify_data.provider
            }
        else:
            logger.error(f"{verify_data.provider} API key verification failed for user {current_user.id}")
            return {
                "valid": False,
                "message": f"Invalid {verify_data.provider.capitalize()} API key",
                "provider": verify_data.provider
            }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"{verify_data.provider} API key verification failed for user {current_user.id}: {error_msg}", exc_info=True)

        if "401" in error_msg or "Unauthorized" in error_msg:
            return {
                "valid": False,
                "message": f"Invalid {verify_data.provider.capitalize()} API key",
                "provider": verify_data.provider
            }
        elif "429" in error_msg or "quota" in error_msg.lower():
            return {
                "valid": False,
                "message": "API key has no credits or quota exceeded"
            }
        else:
            return {
                "valid": False,
                "message": f"API key verification failed: {error_msg}"
            }
