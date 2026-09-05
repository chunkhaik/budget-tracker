from uuid import UUID

from sqlmodel import Session

from app.models.workspace import Workspace
from app.repos.workspaces import WorkspaceRepository


class WorkspaceService:
    def __init__(self, repository: WorkspaceRepository | None = None) -> None:
        self.repository = repository or WorkspaceRepository()

    def list_for_user(self, session: Session, user_id: UUID) -> list[Workspace]:
        return self.repository.list_for_user(session, user_id)
