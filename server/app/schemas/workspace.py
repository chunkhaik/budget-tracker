from datetime import datetime
from uuid import UUID

from app.domain.enums import WorkspaceRole
from app.schemas.common import APIModel, ResourceRef


class WorkspaceCreateRequest(APIModel):
    name: str
    base_currency: str


class WorkspaceRead(WorkspaceCreateRequest):
    id: UUID


class WorkspaceMemberCreateRequest(APIModel):
    user_id: UUID
    role: WorkspaceRole


class WorkspaceMemberRead(APIModel):
    workspace_id: UUID
    user_id: UUID
    role: WorkspaceRole
    created_at: datetime


class WorkspaceMemberDeleteResponse(ResourceRef):
    status: str
    workspace_id: UUID
