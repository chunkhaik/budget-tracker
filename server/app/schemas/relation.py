from uuid import UUID

from pydantic import Field

from app.domain.enums import RelationSelectionMode
from app.schemas.common import APIModel


class RelationRuleDefinition(APIModel):
    user_ids: list[UUID] = Field(default_factory=list)
    category_ids: list[UUID] = Field(default_factory=list)
    from_ts: int | None = Field(default=None, alias="from")
    to: int | None = None
    amount_min: int | None = None
    amount_max: int | None = None
    currencies: list[str] = Field(default_factory=list)
    note_contains: list[str] = Field(default_factory=list)
    transaction_ids: list[UUID] = Field(default_factory=list)
    include_transaction_ids: list[UUID] = Field(default_factory=list)
    exclude_transaction_ids: list[UUID] = Field(default_factory=list)


class RelationCreateRequest(APIModel):
    name: str
    description: str | None = None
    selection_mode: RelationSelectionMode
    rule_definition: RelationRuleDefinition | None = None


class RelationRead(RelationCreateRequest):
    id: UUID
