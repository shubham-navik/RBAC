import uuid
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from backend.app.core.security import hash_password, verify_password
from backend.app.core.redis import redis_client
from backend.app.models import User, Session


refresh_hasher = PasswordHasher()


class AuthService:

    @staticmethod
    async def register(
        db: AsyncSession,
        email: str,
        password: str,
        full_name: str | None,
    ):
        result = await db.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError("Email already registered")

        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def login(
        db: AsyncSession,
        email: str,
        password: str,
    ):
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is inactive")

        session_id = uuid.uuid4()

        access_token = create_access_token(
            user.id,
            session_id,
        )

        refresh_token = create_refresh_token(
            user.id,
            session_id,
        )

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        session = Session(
            id=session_id,
            user_id=user.id,
            refresh_token_hash=refresh_hasher.hash(refresh_token),
            expires_at=expires_at,
        )

        db.add(session)
        await db.commit()

        ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        try:
            await redis_client.set(
                f"session:{session_id}",
                str(user.id),
                ex=ttl,
            )
        except Exception:
            await db.delete(session)
            await db.commit()
            raise RuntimeError("Unable to create session")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    async def get_current_user(
        db: AsyncSession,
        token: str,
    ):
        try:
            payload = decode_token(token)

            if payload.get("type") != "access":
                raise ValueError("Invalid token type")

            user_id = uuid.UUID(payload["sub"])
            session_id = uuid.UUID(payload["sid"])

        except Exception:
            raise ValueError("Invalid or expired access token")

        redis_user_id = await redis_client.get(
            f"session:{session_id}"
        )

        if redis_user_id != str(user_id):
            raise ValueError("Session expired or revoked")

        result = await db.execute(
            select(User).where(User.id == user_id)
        )

        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        return user

    @staticmethod
    async def logout(
        db: AsyncSession,
        token: str,
    ):
        try:
            payload = decode_token(token)

            if payload.get("type") != "access":
                raise ValueError("Invalid token type")

            session_id = uuid.UUID(payload["sid"])

        except Exception:
            raise ValueError("Invalid or expired access token")

        result = await db.execute(
            select(Session).where(Session.id == session_id)
        )

        session = result.scalar_one_or_none()

        if session and session.revoked_at is None:
            session.revoked_at = datetime.now(timezone.utc)
            await db.commit()

        await redis_client.delete(f"session:{session_id}")

        return {"message": "Logged out successfully"}