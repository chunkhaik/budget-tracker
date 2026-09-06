from uuid import UUID

from sqlmodel import Session, select

from app.models.relation import WorkspaceRelation, WorkspaceRelationTransaction


class RelationRepository:
    def list_for_workspace(self, session: Session, workspace_id: UUID) -> list[WorkspaceRelation]:
        statement = select(WorkspaceRelation).where(WorkspaceRelation.workspace_id == workspace_id)
        return list(session.exec(statement))

    def get_for_workspace(self, session: Session, workspace_id: UUID, relation_id: UUID) -> WorkspaceRelation | None:
        statement = select(WorkspaceRelation).where(
            WorkspaceRelation.workspace_id == workspace_id,
            WorkspaceRelation.id == relation_id,
        )
        return session.exec(statement).first()

    def create(self, session: Session, relation: WorkspaceRelation) -> WorkspaceRelation:
        session.add(relation)
        session.commit()
        session.refresh(relation)
        return relation

    def save(self, session: Session, relation: WorkspaceRelation) -> WorkspaceRelation:
        session.add(relation)
        session.commit()
        session.refresh(relation)
        return relation

    def list_manual_transaction_pks(self, session: Session, relation_id: UUID) -> list[int]:
        statement = select(WorkspaceRelationTransaction.transaction_pk).where(
            WorkspaceRelationTransaction.relation_id == relation_id
        )
        return list(session.exec(statement))
