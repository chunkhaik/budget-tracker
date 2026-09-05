from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.domain.enums import RelationSelectionMode
from app.models.base import UUIDPrimaryKeyModel


class WorkspaceRelation(UUIDPrimaryKeyModel, table=True):
    __tablename__ = "workspace_relations"
    __table_args__ = (UniqueConstraint("workspace_id", "name", name="uq_relations_workspace_name"),)

    workspace_id: UUID = Field(foreign_key="workspaces.id", nullable=False, index=True)
    name: str = Field(nullable=False, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    selection_mode: RelationSelectionMode = Field(nullable=False)
    rule_definition: dict | None = Field(default=None, sa_type=JSONB)
    created_by_user_id: UUID = Field(foreign_key="users.id", nullable=False)


class WorkspaceRelationTransaction(SQLModel, table=True):
    __tablename__ = "workspace_relation_transactions"
    __table_args__ = (PrimaryKeyConstraint("relation_id", "transaction_pk"),)

    relation_id: UUID = Field(foreign_key="workspace_relations.id", nullable=False)
    transaction_pk: int = Field(foreign_key="transactions.id", nullable=False, index=True)
    added_by_user_id: UUID = Field(foreign_key="users.id", nullable=False)
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
