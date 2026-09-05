from fastapi import APIRouter, Depends

from app.api.deps import require_current_user
from app.core.security import CurrentUser

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("")
def list_workspaces(current_user: CurrentUser = Depends(require_current_user)) -> dict[str, object]:
    return {
        "items": [],
        "user_id": str(current_user.id),
    }


@router.post("")
def create_workspace(current_user: CurrentUser = Depends(require_current_user)) -> dict[str, str]:
    return {
        "status": "todo",
        "user_id": str(current_user.id),
    }


@router.get("/{workspace_id}")
def get_workspace(workspace_id: str) -> dict[str, str]:
    return {
        "workspace_id": workspace_id,
        "status": "todo",
    }


@router.post("/{workspace_id}/members")
def add_workspace_member(workspace_id: str) -> dict[str, str]:
    return {
        "workspace_id": workspace_id,
        "status": "todo",
    }


@router.delete("/{workspace_id}/members/{user_id}")
def remove_workspace_member(workspace_id: str, user_id: str) -> dict[str, str]:
    return {
        "workspace_id": workspace_id,
        "user_id": user_id,
        "status": "todo",
    }
