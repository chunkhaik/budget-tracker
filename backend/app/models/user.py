from sqlmodel import Field, SQLModel

from app.models.base import UUIDPrimaryKeyModel


class User(UUIDPrimaryKeyModel, table=True):
    __tablename__ = "users"

    email: str = Field(nullable=False, unique=True, index=True, max_length=255)
    display_name: str = Field(nullable=False, max_length=255)


class ApiKey(SQLModel, table=False):
    """Placeholder auth persistence model for a later Supabase/API-key pass."""
