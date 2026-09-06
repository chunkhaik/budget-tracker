from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.relation import WorkspaceRelation
from app.repos.relations import RelationRepository
from app.schemas.relation import RelationCreateRequest, RelationUpdateRequest
from app.services.relation_builder import RelationBuilder
from app.services.workspaces import WorkspaceService


class RelationService:
    def __init__(
        self,
        repository: RelationRepository | None = None,
        relation_builder: RelationBuilder | None = None,
        workspace_service: WorkspaceService | None = None,
    ) -> None:
        self.repository = repository or RelationRepository()
        self.relation_builder = relation_builder or RelationBuilder()
        self.workspace_service = workspace_service or WorkspaceService()

    def list_for_workspace(self, session: Session, workspace_id: UUID, user_id: UUID) -> list[WorkspaceRelation]:
        self.workspace_service.require_member(session, workspace_id, user_id)
        return self.repository.list_for_workspace(session, workspace_id)

    def create_for_workspace(
        self,
        session: Session,
        workspace_id: UUID,
        user_id: UUID,
        payload: RelationCreateRequest,
    ) -> WorkspaceRelation:
        self.workspace_service.require_member(session, workspace_id, user_id)
        relation = WorkspaceRelation(
            workspace_id=workspace_id,
            name=payload.name,
            description=payload.description,
            selection_mode=payload.selection_mode,
            rule_definition=payload.rule_definition.model_dump(by_alias=True) if payload.rule_definition else None,
            created_by_user_id=user_id,
        )
        return self.repository.create(session, relation)

    def get_for_workspace(self, session: Session, workspace_id: UUID, relation_id: UUID, user_id: UUID) -> WorkspaceRelation:
        self.workspace_service.require_member(session, workspace_id, user_id)
        relation = self.repository.get_for_workspace(session, workspace_id, relation_id)
        if relation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="relation not found")
        return relation

    def update_for_workspace(
        self,
        session: Session,
        workspace_id: UUID,
        relation_id: UUID,
        user_id: UUID,
        payload: RelationUpdateRequest,
    ) -> WorkspaceRelation:
        relation = self.get_for_workspace(session, workspace_id, relation_id, user_id)
        if payload.name is not None:
            relation.name = payload.name
        if payload.description is not None:
            relation.description = payload.description
        if payload.selection_mode is not None:
            relation.selection_mode = payload.selection_mode
        if payload.rule_definition is not None:
            relation.rule_definition = payload.rule_definition.model_dump(by_alias=True)
        relation.updated_at = datetime.now(timezone.utc)
        return self.repository.save(session, relation)

    def preview(self, session: Session, workspace_id: UUID, user_id: UUID, payload: RelationCreateRequest) -> dict:
        self.workspace_service.require_member(session, workspace_id, user_id)
        relation = WorkspaceRelation(
            workspace_id=workspace_id,
            name=payload.name,
            description=payload.description,
            selection_mode=payload.selection_mode,
            rule_definition=payload.rule_definition.model_dump(by_alias=True) if payload.rule_definition else None,
            created_by_user_id=user_id,
        )
        return self.relation_builder.build_preview(session, relation)

    def list_transactions(self, session: Session, workspace_id: UUID, relation_id: UUID, user_id: UUID) -> list:
        relation = self.get_for_workspace(session, workspace_id, relation_id, user_id)
        return self.relation_builder.list_transactions(session, relation)
