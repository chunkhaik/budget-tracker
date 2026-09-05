from uuid import UUID

from app.domain.enums import WorkspaceRole
from app.schemas.common import APIModel


class WorkspaceCreateRequest(APIModel):
    name: str
    base_currency: str


class WorkspaceMemberRequest(APIModel):
    user_id: UUID
    role: WorkspaceRole


class WorkspaceRead(WorkspaceCreateRequest):
    id: UUID
