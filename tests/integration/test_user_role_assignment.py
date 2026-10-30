import os
import uuid

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost/test",
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")

import pytest
from fastapi.testclient import TestClient

from backend.app.db.session import get_db
from backend.app.main import app
from backend.app.repositories.permission_repository import PermissionRepository
from backend.app.schemas.auth import RegisterRequest
from backend.app.services.auth_service import AuthService
from backend.app.services.user_role_service import UserRoleService


@pytest.fixture
def api_client(monkeypatch):
    admin = type("UserStub", (), {"id": uuid.uuid4()})()
    normal_user = type("UserStub", (), {"id": uuid.uuid4()})()
    assignment_calls = []

    async def override_get_db():
        yield object()

    async def get_current_user(db, token):
        users_by_token = {
            "admin-token": admin,
            "user-token": normal_user,
        }
        if token not in users_by_token:
            raise ValueError("Invalid token")
        return users_by_token[token]

    async def get_user_permissions(db, user_id):
        if user_id == admin.id:
            return {"roles:assign"}
        return set()

    async def assign_role(*, db, user_id, role_id):
        assignment_calls.append((user_id, role_id))
        return type(
            "UserRoleStub",
            (),
            {"user_id": user_id, "role_id": role_id},
        )()

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(AuthService, "get_current_user", get_current_user)
    monkeypatch.setattr(
        PermissionRepository,
        "get_user_permissions",
        get_user_permissions,
    )
    monkeypatch.setattr(UserRoleService, "assign_role", assign_role)

    try:
        with TestClient(app) as client:
            yield client, admin, normal_user, assignment_calls
    finally:
        app.dependency_overrides.clear()


def test_admin_can_assign_role(api_client):
    client, _, normal_user, assignment_calls = api_client
    role_id = uuid.uuid4()

    response = client.post(
        f"/api/v1/admin/users/{normal_user.id}/roles",
        headers={"Authorization": "Bearer admin-token"},
        json={"role_id": str(role_id)},
    )

    assert response.status_code == 201
    assert response.json() == {
        "message": "Role assigned successfully",
        "user_id": str(normal_user.id),
        "role_id": str(role_id),
    }
    assert assignment_calls == [(normal_user.id, role_id)]


def test_regular_user_cannot_assign_role(api_client):
    client, _, normal_user, assignment_calls = api_client
    role_id = uuid.uuid4()

    response = client.post(
        f"/api/v1/admin/users/{normal_user.id}/roles",
        headers={"Authorization": "Bearer user-token"},
        json={"role_id": str(role_id)},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "You do not have permission to perform this action"
    )
    assert assignment_calls == []


def test_registration_schema_does_not_accept_role_id():
    assert "role_id" not in RegisterRequest.model_fields
