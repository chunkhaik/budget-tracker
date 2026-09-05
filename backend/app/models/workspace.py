from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint
from sqlmodel import Field, SQLModel

from app.domain.enums import WorkspaceRole
from app.models.base import UUIDPrimaryKeyModel


class Workspace(UUIDPrimaryKeyModel, table=True):
    __tablename__ = "workspaces"

    name: str = Field(nullable=False, max_length=255)
    base_currency: str = Field(nullable=False, min_length=3, max_length=3)


class WorkspaceMember(SQLModel, table=True):
    __tablename__ = "workspace_members"
    __table_args__ = (PrimaryKeyConstraint("workspace_id", "user_id"),)

    workspace_id: UUID = Field(foreign_key="workspaces.id", nullable=False)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    role: WorkspaceRole = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
