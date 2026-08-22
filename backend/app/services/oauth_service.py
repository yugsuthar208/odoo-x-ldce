import httpx
import uuid
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.middleware.auth import create_access_token, hash_password


class OAuthService:
    """Service for managing OAuth2 Social Logins with Google and GitHub."""

    @staticmethod
    async def process_oauth_login(
        db: AsyncSession,
        provider: str,
        provider_user_id: str,
        email: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> tuple[User, str]:
        """
        Finds or creates a user matching the OAuth credentials and issues a JWT token.
        """
        stmt = select(User).where(User.email == email.lower())
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            # Create new user via OAuth
            user = User(
                id=str(uuid.uuid4()),
                email=email.lower(),
                password_hash=hash_password(str(uuid.uuid4())), # Random unusable password
                name=full_name or email.split("@")[0].capitalize(),
                profile_photo=avatar_url or f"https://api.dicebear.com/7.x/bottts/svg?seed={email}",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        # Generate JWT access token
        access_token = create_access_token(data={"sub": user.id, "email": user.email})
        return user, access_token
