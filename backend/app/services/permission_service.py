from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.permission_repository import (
    PermissionRepository,
)


class PermissionService:

    @staticmethod
    async def create_permission(
        db: AsyncSession,
        code: str,
        resource: str,
        action: str,
        description: str | None,
    ):
        existing_permission = await PermissionRepository.get_by_code(
            db, code
        )

        if existing_permission:
            raise ValueError("Permission already exists")

        return await PermissionRepository.create(
            db=db,
            code=code,
            resource=resource,
            action=action,
            description=description,
        )

    @staticmethod
    async def get_all_permissions(db: AsyncSession):
        return await PermissionRepository.get_all(db)