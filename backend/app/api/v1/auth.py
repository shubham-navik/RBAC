from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.schemas.auth import RegisterRequest, LoginRequest
from backend.app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])

bearer_scheme = HTTPBearer()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await AuthService.register(
            db=db,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
        )

        return {
            "message": "User registered successfully",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
            },
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.post("/login")
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await AuthService.login(
            db=db,
            email=request.email,
            password=request.password,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        )


@router.get("/me")
async def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await AuthService.get_current_user(
            db=db,
            token=credentials.credentials,
        )

        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await AuthService.logout(
            db=db,
            token=credentials.credentials,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        )