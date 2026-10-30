from pydantic import BaseModel
from uuid import UUID


class AssignRoleRequest(BaseModel):
    role_id: UUID


class UserRoleResponse(BaseModel):
    id: UUID
    name: str
    description: str | None

    model_config = {"from_attributes": True}