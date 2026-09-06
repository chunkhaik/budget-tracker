from uuid import UUID

from sqlalchemy import and_
from sqlmodel import Session, select

from app.models.workspace import Workspace, WorkspaceMember


class WorkspaceRepository:
    def list_for_user(self, session: Session, user_id: UUID) -> list[Workspace]:
        statement = (
            select(Workspace)
            .join(
                WorkspaceMember,
                and_(
                    WorkspaceMember.workspace_id == Workspace.id,
                    WorkspaceMember.user_id == user_id,
                ),
            )
        )
        return list(session.exec(statement))

    def get(self, session: Session, workspace_id: UUID) -> Workspace | None:
        return session.get(Workspace, workspace_id)

    def get_member(self, session: Session, workspace_id: UUID, user_id: UUID) -> WorkspaceMember | None:
        statement = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        return session.exec(statement).first()

    def create(self, session: Session, workspace: Workspace) -> Workspace:
        session.add(workspace)
        session.commit()
        session.refresh(workspace)
        return workspace

    def create_member(self, session: Session, member: WorkspaceMember) -> WorkspaceMember:
        session.add(member)
        session.commit()
        session.refresh(member)
        return member

    def delete_member(self, session: Session, member: WorkspaceMember) -> None:
        session.delete(member)
        session.commit()
