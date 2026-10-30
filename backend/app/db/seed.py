from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import AsyncSessionLocal
from backend.app.models import Permission, Role, RolePermission

DEFAULT_PERMISSIONS = [
    ("users:create", "users", "create"),
    ("users:read", "users", "read"),
    ("users:update", "users", "update"),
    ("users:delete", "users", "delete"),
    ("roles:create", "roles", "create"),
    ("roles:read", "roles", "read"),
    ("roles:update", "roles", "update"),
    ("roles:delete", "roles", "delete"),
    ("permissions:create", "permissions", "create"),
    ("permissions:read", "permissions", "read"),
    ("projects:create", "projects", "create"),
    ("projects:read", "projects", "read"),
    ("projects:update", "projects", "update"),
    ("projects:delete", "projects", "delete"),
]


async def seed_permissions(db: AsyncSession) -> None:
    for code, resource, action in DEFAULT_PERMISSIONS:
        result = await db.execute(select(Permission).where(Permission.code == code))
        permission = result.scalar_one_or_none()

        if not permission:
            db.add(
                Permission(
                    code=code,
                    resource=resource,
                    action=action,
                )
            )

    await db.flush()


async def seed_roles(db: AsyncSession) -> None:
    default_roles = {
        "Admin": "Full system access",
        "Manager": "Manage users and projects",
        "Employee": "Basic project access",
    }

    for name, description in default_roles.items():
        result = await db.execute(select(Role).where(Role.name == name))
        role = result.scalar_one_or_none()

        if not role:
            db.add(
                Role(
                    name=name,
                    description=description,
                    is_system=True,
                )
            )

    await db.flush()


async def assign_default_permissions(db: AsyncSession) -> None:
    result = await db.execute(select(Role))
    roles = result.scalars().all()

    result = await db.execute(select(Permission))
    permissions = result.scalars().all()

    permission_map = {permission.code: permission.id for permission in permissions}

    role_permissions = {
        "Admin": list(permission_map.keys()),
        "Manager": [
            "users:read",
            "users:update",
            "projects:create",
            "projects:read",
            "projects:update",
            "projects:delete",
        ],
        "Employee": [
            "projects:read",
        ],
    }

    required_permission_codes = {code for code, _, _ in DEFAULT_PERMISSIONS} | {
        permission_code
        for permission_codes in role_permissions.values()
        for permission_code in permission_codes
    }
    missing_permissions = required_permission_codes - permission_map.keys()
    if missing_permissions:
        raise RuntimeError(
            "Cannot assign default role permissions; missing permissions: "
            + ", ".join(sorted(missing_permissions))
        )

    result = await db.execute(
        select(RolePermission.role_id, RolePermission.permission_id)
    )
    existing_assignments = set(result.tuples().all())

    for role in roles:
        allowed_permissions = role_permissions.get(role.name, [])

        for permission_code in allowed_permissions:
            permission_id = permission_map[permission_code]
            assignment = (role.id, permission_id)
            if assignment not in existing_assignments:
                db.add(
                    RolePermission(
                        role_id=role.id,
                        permission_id=permission_id,
                    )
                )
                existing_assignments.add(assignment)

    await db.flush()


async def seed_database() -> None:
    async with AsyncSessionLocal() as db:
        try:
            await seed_permissions(db)
            await seed_roles(db)
            await assign_default_permissions(db)

            await db.commit()
            print("Database seeded successfully!")

        except Exception:
            await db.rollback()
            raise


if __name__ == "__main__":
    import asyncio

    asyncio.run(seed_database())
