from uuid import UUID

from sqlmodel import Session, select

from app.models.relation import WorkspaceRelation


class RelationRepository:
    def list_for_workspace(self, session: Session, workspace_id: UUID) -> list[WorkspaceRelation]:
        statement = select(WorkspaceRelation).where(WorkspaceRelation.workspace_id == workspace_id)
        return list(session.exec(statement))
