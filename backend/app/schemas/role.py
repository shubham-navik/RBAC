from pydantic import BaseModel, Field
from uuid import UUID


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None


class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    is_active: bool
    is_system: bool

    model_config = {"from_attributes": True}