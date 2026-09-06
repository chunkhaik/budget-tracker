from typing import Any, cast
from uuid import UUID

from sqlmodel import Session, select

from app.domain.enums import RelationSelectionMode
from app.models.relation import WorkspaceRelation
from app.models.transaction import Transaction
from app.models.workspace import WorkspaceMember
from app.schemas.relation import RelationRuleDefinition


class RelationBuilder:
    def build_preview(self, session: Session, relation: WorkspaceRelation | None) -> dict[str, Any]:
        if relation is None:
            return {"items": [], "selection_mode": None}

        items = self.list_transactions(session, relation)
        return {
            "items": items,
            "selection_mode": relation.selection_mode,
            "rule_definition": relation.rule_definition,
        }

    def list_transactions(self, session: Session, relation: WorkspaceRelation) -> list[Transaction]:
        transaction_model = cast(Any, Transaction)
        member_model = cast(Any, WorkspaceMember)
        statement = (
            select(Transaction)
            .join(member_model, member_model.user_id == transaction_model.user_id)
            .where(member_model.workspace_id == relation.workspace_id)
            .where(transaction_model.deleted_at.is_(None))
        )

        rule = self._rule_definition(relation)
        if rule.user_ids:
            statement = statement.where(transaction_model.user_id.in_(rule.user_ids))
        if rule.category_ids:
            statement = statement.where(transaction_model.category_id.in_(rule.category_ids))
        if rule.from_ts is not None:
            statement = statement.where(transaction_model.transaction_at >= rule.from_ts)
        if rule.to is not None:
            statement = statement.where(transaction_model.transaction_at <= rule.to)
        if rule.amount_min is not None:
            statement = statement.where(transaction_model.amount >= rule.amount_min)
        if rule.amount_max is not None:
            statement = statement.where(transaction_model.amount <= rule.amount_max)
        if rule.currencies:
            statement = statement.where(transaction_model.currency.in_(rule.currencies))
        if rule.transaction_ids:
            statement = statement.where(transaction_model.transaction_id.in_(rule.transaction_ids))
        if rule.include_transaction_ids:
            statement = statement.where(transaction_model.transaction_id.in_(rule.include_transaction_ids))
        if rule.exclude_transaction_ids:
            statement = statement.where(~transaction_model.transaction_id.in_(rule.exclude_transaction_ids))
        for note in rule.note_contains:
            statement = statement.where(transaction_model.note.contains(note))

        if relation.selection_mode == RelationSelectionMode.MANUAL:
            manual_ids = list(self._manual_transaction_ids(relation))
            if not manual_ids:
                return []
            statement = statement.where(transaction_model.id.in_(manual_ids))

        items = list(session.exec(statement))
        if relation.selection_mode == RelationSelectionMode.HYBRID:
            manual_ids = set(self._manual_transaction_ids(relation))
            for item in items:
                manual_ids.discard(item.id)
            if manual_ids:
                manual_statement = select(Transaction).where(
                    transaction_model.id.in_(manual_ids),
                    transaction_model.deleted_at.is_(None),
                )
                items.extend(list(session.exec(manual_statement)))
        return items

    def _rule_definition(self, relation: WorkspaceRelation) -> RelationRuleDefinition:
        raw = relation.rule_definition or {}
        return RelationRuleDefinition.model_validate(raw)

    def _manual_transaction_ids(self, relation: WorkspaceRelation) -> list[int]:
        raw = relation.rule_definition or {}
        ids = raw.get("manual_transaction_ids", [])
        return [int(item) for item in ids]
