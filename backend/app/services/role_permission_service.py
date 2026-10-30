from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.role_repository import RoleRepository
from backend.app.repositories.permission_repository import (
    PermissionRepository,
)
from backend.app.repositories.role_permission_repository import (
    RolePermissionRepository,
)


class RolePermissionService:

    @staticmethod
    async def assign_permission(
        db: AsyncSession,
        role_id,
        permission_id,
    ):
        role = await RoleRepository.get_by_id(db, role_id)

        if not role:
            raise ValueError("Role not found")

        permission = await PermissionRepository.get_by_code(db, permission_id) \
            if isinstance(permission_id, str) else None

        if permission is None:
            from backend.app.models import Permission
            from sqlalchemy import select

            result = await db.execute(
                select(Permission).where(Permission.id == permission_id)
            )
            permission = result.scalar_one_or_none()

        if not permission:
            raise ValueError("Permission not found")

        return await RolePermissionRepository.assign_permission(
            db=db,
            role_id=role_id,
            permission_id=permission.id,
        )

    @staticmethod
    async def get_role_permissions(db: AsyncSession, role_id):
        role = await RoleRepository.get_by_id(db, role_id)

        if not role:
            raise ValueError("Role not found")

        return await RolePermissionRepository.get_role_permissions(
            db, role_id
        )