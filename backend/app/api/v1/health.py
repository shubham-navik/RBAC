from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from backend.app.core.redis import redis_client
from backend.app.db.session import AsyncSessionLocal

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "rbac-system",
    }


@router.get("/health/db")
async def database_health():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from exc


@router.get("/health/redis")
async def redis_health():
    try:
        await redis_client.ping()

        return {
            "status": "healthy",
            "redis": "connected",
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Redis connection failed",
        ) from exc