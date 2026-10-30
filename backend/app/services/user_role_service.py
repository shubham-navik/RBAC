from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import User
from backend.app.repositories.role_repository import RoleRepository
from backend.app.repositories.user_role_repository import UserRoleRepository


class UserRoleService:

    @staticmethod
    async def assign_role(
        db: AsyncSession,
        user_id,
        role_id,
    ):
        user = await db.get(User, user_id)

        if not user:
            raise ValueError("User not found")

        role = await RoleRepository.get_by_id(db, role_id)

        if not role:
            raise ValueError("Role not found")

        if not role.is_active:
            raise ValueError("Cannot assign an inactive role")

        return await UserRoleRepository.assign_role(
            db=db,
            user_id=user_id,
            role_id=role_id,
        )

    @staticmethod
    async def get_user_roles(
        db: AsyncSession,
        user_id,
    ):
        user = await db.get(User, user_id)

        if not user:
            raise ValueError("User not found")

        return await UserRoleRepository.get_user_roles(db, user_id)

    @staticmethod
    async def remove_role(
        db: AsyncSession,
        user_id,
        role_id,
    ):
        user = await db.get(User, user_id)

        if not user:
            raise ValueError("User not found")

        return await UserRoleRepository.remove_role(
            db=db,
            user_id=user_id,
            role_id=role_id,
        )