from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from app.domain.enums import CategoryType
from app.models.base import UUIDPrimaryKeyModel


class Category(UUIDPrimaryKeyModel, table=True):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_categories_user_name"),)

    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    name: str = Field(nullable=False, max_length=255)
    type: CategoryType = Field(nullable=False)
