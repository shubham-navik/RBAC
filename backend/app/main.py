from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.api.v1.health import router as health_router
from backend.app.core.config import settings
from backend.app.core.redis import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    description="Scalable, database-driven Role-Based Access Control API",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.include_router(
    health_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/")
async def root():
    return {
        "message": "RBAC System API is running",
        "docs": "/docs",
    }