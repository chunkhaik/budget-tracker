from uuid import UUID

from sqlmodel import Session, select

from app.models.workspace import Workspace, WorkspaceMember


class WorkspaceRepository:
    def list_for_user(self, session: Session, user_id: UUID) -> list[Workspace]:
        statement = (
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user_id)
        )
        return list(session.exec(statement))

    def get_member(self, session: Session, workspace_id: UUID, user_id: UUID) -> WorkspaceMember | None:
        statement = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        return session.exec(statement).first()
