from typing import Any, cast
from uuid import UUID

from sqlalchemy import and_
from sqlmodel import Session, select

from app.models.workspace import Workspace, WorkspaceMember


class WorkspaceRepository:
    def list_for_user(self, session: Session, user_id: UUID) -> list[Workspace]:
        workspace_model = cast(Any, Workspace)
        workspace_member_model = cast(Any, WorkspaceMember)
        statement = (
            select(Workspace)
            .join(
                WorkspaceMember,
                and_(
                    workspace_member_model.workspace_id == workspace_model.id,
                    workspace_member_model.user_id == user_id,
                ),
            )
        )
        return list(session.exec(statement))

    def get_member(self, session: Session, workspace_id: UUID, user_id: UUID) -> WorkspaceMember | None:
        workspace_member_model = cast(Any, WorkspaceMember)
        statement = select(WorkspaceMember).where(
            workspace_member_model.workspace_id == workspace_id,
            workspace_member_model.user_id == user_id,
        )
        return session.exec(statement).first()
