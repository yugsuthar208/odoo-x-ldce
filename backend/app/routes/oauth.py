from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.oauth_service import OAuthService
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth/oauth", tags=["Authentication - OAuth2 Social Login"])


class OAuthCallbackRequest(BaseModel):
    """Payload for completing OAuth authentication."""
    provider: str  # 'google' or 'github'
    code: str
    redirect_uri: Optional[str] = None
    # For testing / direct exchange simulation
    mock_email: Optional[EmailStr] = None
    mock_name: Optional[str] = None


class OAuthTokenResponse(BaseModel):
    """Response containing access token and user profile."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut


@router.get("/{provider}/authorize", summary="Get OAuth Authorization URL")
async def get_oauth_authorize_url(provider: str, redirect_uri: Optional[str] = None):
    """
    Returns the OAuth2 authorization URL for redirecting the user to Google or GitHub.
    """
    prov = provider.lower()
    if prov == "google":
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id=GOOGLE_CLIENT_ID&response_type=code&scope=openid%20email%20profile&redirect_uri={redirect_uri or 'http://localhost:5173/auth/callback'}"
    elif prov == "github":
        auth_url = f"https://github.com/login/oauth/authorize?client_id=GITHUB_CLIENT_ID&scope=user:email&redirect_uri={redirect_uri or 'http://localhost:5173/auth/callback'}"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported OAuth provider: '{provider}'")

    return {"provider": prov, "authorization_url": auth_url}


@router.post("/callback", response_model=OAuthTokenResponse, summary="Exchange OAuth code for JWT access token")
async def oauth_callback(
    payload: OAuthCallbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Exchanges the OAuth authorization code for user profile information, creates or logs in
    the corresponding user, and returns a valid JWT access token.
    """
    prov = payload.provider.lower()
    if prov not in ["google", "github"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported OAuth provider: '{prov}'")

    # In production with actual CLIENT_ID/SECRET, exchange code with Google/GitHub token endpoint.
    # For local/testing/sandbox, we extract or simulate the user profile:
    email = payload.mock_email or f"oauth_user_{payload.code[:8]}@{prov}.com"
    full_name = payload.mock_name or f"{prov.capitalize()} Traveler"
    avatar_url = f"https://api.dicebear.com/7.x/identicon/svg?seed={email}"

    user, token = await OAuthService.process_oauth_login(
        db=db,
        provider=prov,
        provider_user_id=payload.code,
        email=email,
        full_name=full_name,
        avatar_url=avatar_url,
    )

    return OAuthTokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )
