from typing import Any

from app.models.relation import WorkspaceRelation


class RelationBuilder:
    def build_preview(self, relation: WorkspaceRelation | None) -> dict[str, Any]:
        if relation is None:
            return {"items": [], "selection_mode": None}

        return {
            "items": [],
            "selection_mode": relation.selection_mode,
            "rule_definition": relation.rule_definition,
        }
