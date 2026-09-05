from sqlmodel import Session

from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.repos.workspaces import WorkspaceRepository


def test_list_for_user_returns_joined_workspace_memberships(
    db_session: Session,
    workspace_member: WorkspaceMember,
    workspace: Workspace,
    other_user: User,
) -> None:
    _ = workspace_member
    _ = other_user

    items = WorkspaceRepository().list_for_user(db_session, workspace_member.user_id)

    assert [item.id for item in items] == [workspace.id]


def test_get_member_returns_matching_workspace_member(
    db_session: Session,
    workspace_member: WorkspaceMember,
) -> None:
    item = WorkspaceRepository().get_member(
        db_session,
        workspace_member.workspace_id,
        workspace_member.user_id,
    )

    assert item is not None
    assert item.role == workspace_member.role
