from uuid import UUID

from app.domain.enums import CategoryType
from app.schemas.common import APIModel, ResourceRef


class CategoryCreateRequest(APIModel):
    name: str
    type: CategoryType


class CategoryUpdateRequest(APIModel):
    name: str | None = None
    type: CategoryType | None = None


class CategoryRead(CategoryCreateRequest):
    id: UUID


class CategoryDeleteResponse(ResourceRef):
    status: str
