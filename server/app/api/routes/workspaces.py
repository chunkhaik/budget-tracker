from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.deps import get_db_session, require_current_user, require_workspace_member
from app.core.security import CurrentUser
from app.schemas.common import UserItemsResponse
from app.schemas.workspace import (
    WorkspaceCreateRequest,
    WorkspaceMemberCreateRequest,
    WorkspaceMemberDeleteResponse,
    WorkspaceMemberRead,
    WorkspaceRead,
)
from app.services.workspaces import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["workspaces"])
service = WorkspaceService()


@router.get("")
def list_workspaces(
    current_user: CurrentUser = Depends(require_current_user),
    session: Session = Depends(get_db_session),
) -> UserItemsResponse:
    items = service.list_for_user(session, current_user.id)
    return UserItemsResponse(
        items=[WorkspaceRead.model_validate(item).model_dump(mode="json") for item in items],
        user_id=str(current_user.id),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreateRequest,
    current_user: CurrentUser = Depends(require_current_user),
    session: Session = Depends(get_db_session),
) -> WorkspaceRead:
    workspace = service.create_workspace(session, current_user.id, payload)
    return WorkspaceRead.model_validate(workspace)


@router.get("/{workspace_id}")
def get_workspace(
    workspace_id: UUID,
    _: CurrentUser = Depends(require_workspace_member),
    session: Session = Depends(get_db_session),
) -> WorkspaceRead:
    workspace = service.require_workspace(session, workspace_id)
    return WorkspaceRead.model_validate(workspace)


@router.post("/{workspace_id}/members", status_code=status.HTTP_201_CREATED)
def add_workspace_member(
    workspace_id: UUID,
    payload: WorkspaceMemberCreateRequest,
    current_user: CurrentUser = Depends(require_current_user),
    session: Session = Depends(get_db_session),
) -> WorkspaceMemberRead:
    member = service.add_member(session, workspace_id, current_user.id, payload)
    return WorkspaceMemberRead.model_validate(member)


@router.delete("/{workspace_id}/members/{user_id}")
def remove_workspace_member(
    workspace_id: UUID,
    user_id: UUID,
    current_user: CurrentUser = Depends(require_current_user),
    session: Session = Depends(get_db_session),
) -> WorkspaceMemberDeleteResponse:
    service.remove_member(session, workspace_id, current_user.id, user_id)
    return WorkspaceMemberDeleteResponse(id=user_id, workspace_id=workspace_id, status="deleted")
