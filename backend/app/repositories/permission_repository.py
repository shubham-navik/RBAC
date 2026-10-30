from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Permission, Role, RolePermission, UserRole


class PermissionRepository:

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str):
        result = await db.execute(
            select(Permission).where(Permission.code == code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(select(Permission))
        return result.scalars().all()

    @staticmethod
    async def create(
        db: AsyncSession,
        code: str,
        resource: str,
        action: str,
        description: str | None,
    ):
        permission = Permission(
            code=code,
            resource=resource,
            action=action,
            description=description,
        )
        db.add(permission)
        await db.commit()
        await db.refresh(permission)
        return permission

    @staticmethod
    async def get_user_permissions(db: AsyncSession, user_id):

        result = await db.execute(
            select(Permission.code)
            .join(
                RolePermission,
                RolePermission.permission_id == Permission.id,
            )
            .join(
                UserRole,
                UserRole.role_id == RolePermission.role_id,
            )
            .join(
                Role,
                Role.id == UserRole.role_id,
            )
            .where(
                UserRole.user_id == user_id,
                Role.is_active.is_(True),
            )
            .distinct()
        )

        return set(result.scalars().all())