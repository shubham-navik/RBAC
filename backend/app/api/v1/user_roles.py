from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.dependencies.permissions import require_permission
from backend.app.models import User
from backend.app.schemas.user_role import AssignRoleRequest
from backend.app.services.user_role_service import UserRoleService

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin - User Roles"],
)


@router.post("/{user_id}/roles", status_code=status.HTTP_201_CREATED)
async def assign_role(
    user_id: UUID,
    request: AssignRoleRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_permission("roles:assign"))],
):
    try:
        await UserRoleService.assign_role(
            db=db,
            user_id=user_id,
            role_id=request.role_id,
        )
    except ValueError as error:
        error_status = (
            status.HTTP_404_NOT_FOUND
            if str(error) in {"User not found", "Role not found"}
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=error_status,
            detail=str(error),
        ) from error

    return {
        "message": "Role assigned successfully",
        "user_id": str(user_id),
        "role_id": str(request.role_id),
    }
