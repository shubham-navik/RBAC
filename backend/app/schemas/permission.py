from pydantic import BaseModel, Field
from uuid import UUID


class PermissionCreate(BaseModel):
    code: str = Field(min_length=3, max_length=100)
    resource: str = Field(min_length=2, max_length=100)
    action: str = Field(min_length=2, max_length=50)
    description: str | None = None


class PermissionResponse(BaseModel):
    id: UUID
    code: str
    resource: str
    action: str
    description: str | None

    model_config = {"from_attributes": True}