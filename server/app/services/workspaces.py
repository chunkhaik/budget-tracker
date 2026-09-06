from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app.domain.enums import WorkspaceRole
from app.domain.permissions import has_workspace_role
from app.models.workspace import Workspace, WorkspaceMember
from app.repos.workspaces import WorkspaceRepository
from app.schemas.workspace import WorkspaceCreateRequest, WorkspaceMemberCreateRequest


class WorkspaceService:
    def __init__(self, repository: WorkspaceRepository | None = None) -> None:
        self.repository = repository or WorkspaceRepository()

    def list_for_user(self, session: Session, user_id: UUID) -> list[Workspace]:
        return self.repository.list_for_user(session, user_id)

    def create_workspace(self, session: Session, user_id: UUID, payload: WorkspaceCreateRequest) -> Workspace:
        workspace = self.repository.create(
            session,
            Workspace(
                name=payload.name,
                base_currency=payload.base_currency,
            ),
        )
        self.repository.create_member(
            session,
            WorkspaceMember(
                workspace_id=workspace.id,
                user_id=user_id,
                role=WorkspaceRole.OWNER,
            ),
        )
        return workspace

    def require_workspace(self, session: Session, workspace_id: UUID) -> Workspace:
        workspace = self.repository.get(session, workspace_id)
        if workspace is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="workspace not found")
        return workspace

    def require_member(self, session: Session, workspace_id: UUID, user_id: UUID) -> WorkspaceMember:
        member = self.repository.get_member(session, workspace_id, user_id)
        if member is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="workspace not found")
        return member

    def require_role(
        self,
        session: Session,
        workspace_id: UUID,
        user_id: UUID,
        required_role: WorkspaceRole,
    ) -> WorkspaceMember:
        member = self.require_member(session, workspace_id, user_id)
        if not has_workspace_role(member.role, required_role):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient workspace role")
        return member

    def add_member(
        self,
        session: Session,
        workspace_id: UUID,
        current_user_id: UUID,
        payload: WorkspaceMemberCreateRequest,
    ) -> WorkspaceMember:
        self.require_workspace(session, workspace_id)
        self.require_role(session, workspace_id, current_user_id, WorkspaceRole.OWNER)
        existing = self.repository.get_member(session, workspace_id, payload.user_id)
        if existing is not None:
            existing.role = payload.role
            return self.repository.create_member(session, existing)
        return self.repository.create_member(
            session,
            WorkspaceMember(
                workspace_id=workspace_id,
                user_id=payload.user_id,
                role=payload.role,
            ),
        )

    def remove_member(self, session: Session, workspace_id: UUID, current_user_id: UUID, user_id: UUID) -> None:
        self.require_role(session, workspace_id, current_user_id, WorkspaceRole.OWNER)
        member = self.require_member(session, workspace_id, user_id)
        self.repository.delete_member(session, member)
