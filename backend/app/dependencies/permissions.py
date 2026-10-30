from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.v1.auth import bearer_scheme
from backend.app.services.auth_service import AuthService
from backend.app.repositories.permission_repository import (
    PermissionRepository,
)


def require_permission(permission_code: str):

    async def permission_checker(
        credentials=Depends(bearer_scheme),
        db: AsyncSession = Depends(get_db),
    ):
        try:
            user = await AuthService.get_current_user(
                db=db,
                token=credentials.credentials,
            )

            permissions = await PermissionRepository.get_user_permissions(
                db=db,
                user_id=user.id,
            )

            if permission_code not in permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to perform this action",
                )

            return user

        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(error),
            )

    return permission_checker