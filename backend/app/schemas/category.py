from app.domain.enums import CategoryType
from app.schemas.common import APIModel


class CategoryCreateRequest(APIModel):
    name: str
    type: CategoryType


class CategoryRead(CategoryCreateRequest):
    id: str
