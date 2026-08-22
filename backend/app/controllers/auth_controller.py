from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.auth import (
    create_access_token,
    create_reset_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import ForgotPasswordRequest, UserCreate, UserLogin


async def signup_user(db: AsyncSession, payload: UserCreate) -> dict:
    """
    Registers a new user, hashes their password with bcrypt,
    and returns a JWT token along with user profile data.
    """
    # Check if email is already taken
    existing = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists",
        )

    # Hash the password and create the user
    hashed = hash_password(payload.password)
    user = User(
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        password_hash=hashed,
        profile_photo=payload.profile_photo,
        language=payload.language or "en",
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Generate JWT token
    token = create_access_token(data={"sub": user.id, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }


async def login_user(db: AsyncSession, payload: UserLogin) -> dict:
    """
    Authenticates a user with email and password,
    returning a signed JWT token on success.
    """
    result = await db.execute(select(User).where(User.email == payload.email.lower().strip()))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.id, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }


async def forgot_password(db: AsyncSession, payload: ForgotPasswordRequest) -> dict:
    """
    Generates a password reset token for a valid account email.
    """
    result = await db.execute(select(User).where(User.email == payload.email.lower().strip()))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found",
        )

    reset_token = create_reset_token(email=user.email)
    return {
        "reset_token": reset_token,
        "message": f"Password reset token generated successfully for {user.email}",
    }
