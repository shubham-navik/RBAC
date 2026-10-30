from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Role


class RoleRepository:

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str):
        result = await db.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, role_id):
        result = await db.execute(
            select(Role).where(Role.id == role_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(select(Role))
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, name: str, description: str | None):
        role = Role(name=name, description=description)
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role