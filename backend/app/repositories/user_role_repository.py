from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import UserRole, Role


class UserRoleRepository:

    @staticmethod
    async def assign_role(
        db: AsyncSession,
        user_id,
        role_id,
    ):
        result = await db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )

        existing = result.scalar_one_or_none()

        if existing:
            return existing

        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
        )

        db.add(user_role)
        await db.commit()
        await db.refresh(user_role)

        return user_role

    @staticmethod
    async def get_user_roles(
        db: AsyncSession,
        user_id,
    ):
        result = await db.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )

        return result.scalars().all()

    @staticmethod
    async def remove_role(
        db: AsyncSession,
        user_id,
        role_id,
    ):
        result = await db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )

        user_role = result.scalar_one_or_none()

        if not user_role:
            return False

        await db.delete(user_role)
        await db.commit()

        return True