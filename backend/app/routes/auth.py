from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth_controller import forgot_password, login_user, signup_user
from app.database import get_db
from app.schemas.common import APIResponse
from app.schemas.user import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registers a new traveler account, hashes password using bcrypt,
    and returns a signed JWT access token.
    """
    result = await signup_user(db=db, payload=payload)
    return APIResponse(
        success=True,
        data=result,
        message="User account created successfully",
    )


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and return JWT",
)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticates a user with email and password and returns a signed 7-day JWT access token.
    """
    result = await login_user(db=db, payload=payload)
    return APIResponse(
        success=True,
        data=result,
        message="Login successful",
    )


@router.post(
    "/forgot-password",
    response_model=APIResponse[ForgotPasswordResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate password reset token",
)
async def request_password_reset(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generates a password reset token for the specified user email.
    """
    result = await forgot_password(db=db, payload=payload)
    return APIResponse(
        success=True,
        data=result,
        message="Password reset instructions generated",
    )
