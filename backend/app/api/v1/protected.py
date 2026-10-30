from fastapi import APIRouter, Depends

from backend.app.dependencies.permissions import require_permission

router = APIRouter(prefix="/protected", tags=["Authorization"])


@router.get("/users")
async def read_users(
    current_user=Depends(require_permission("users:read")),
):
    return {
        "message": "You can read users",
        "user_id": str(current_user.id),
    }


@router.post("/users")
async def create_user(
    current_user=Depends(require_permission("users:create")),
):
    return {
        "message": "You can create users",
        "user_id": str(current_user.id),
    }


@router.delete("/users")
async def delete_users(
    current_user=Depends(require_permission("users:delete")),
):
    return {
        "message": "You can delete users",
        "user_id": str(current_user.id),
    }