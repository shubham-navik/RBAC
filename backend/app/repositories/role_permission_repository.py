from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import RolePermission, Permission


class RolePermissionRepository:

    @staticmethod
    async def assign_permission(
        db: AsyncSession,
        role_id,
        permission_id,
    ):
        result = await db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )

        existing = result.scalar_one_or_none()

        if existing:
            return existing

        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
        )

        db.add(role_permission)
        await db.commit()
        await db.refresh(role_permission)

        return role_permission

    @staticmethod
    async def get_role_permissions(
        db: AsyncSession,
        role_id,
    ):
        result = await db.execute(
            select(Permission)
            .join(
                RolePermission,
                RolePermission.permission_id == Permission.id,
            )
            .where(RolePermission.role_id == role_id)
        )

        return result.scalars().all()