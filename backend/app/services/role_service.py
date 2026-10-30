from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.role_repository import RoleRepository


class RoleService:

    @staticmethod
    async def create_role(
        db: AsyncSession,
        name: str,
        description: str | None,
    ):
        existing_role = await RoleRepository.get_by_name(db, name)

        if existing_role:
            raise ValueError("Role already exists")

        return await RoleRepository.create(
            db=db,
            name=name,
            description=description,
        )

    @staticmethod
    async def get_role(db: AsyncSession, role_id):
        role = await RoleRepository.get_by_id(db, role_id)

        if not role:
            raise ValueError("Role not found")

        return role

    @staticmethod
    async def get_all_roles(db: AsyncSession):
        return await RoleRepository.get_all(db)