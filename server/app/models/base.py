from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class TimestampedModel(SQLModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)


class UUIDPrimaryKeyModel(TimestampedModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
