from uuid import UUID

from sqlmodel import Session

from app.domain.enums import WorkspaceRole
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


def test_get_returns_workspace_by_id(db_session: Session, workspace: Workspace) -> None:
    item = WorkspaceRepository().get(db_session, workspace.id)

    assert item is not None
    assert item.id == workspace.id


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


def test_create_persists_workspace(db_session: Session) -> None:
    workspace = Workspace(name="Trip", base_currency="USD")

    created = WorkspaceRepository().create(db_session, workspace)

    assert created.id is not None
    assert db_session.get(Workspace, created.id) is not None


def test_create_member_persists_workspace_member(db_session: Session, workspace: Workspace, user: User) -> None:
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user.id,
        role=WorkspaceRole.MEMBER,
    )

    created = WorkspaceRepository().create_member(db_session, member)

    assert created.workspace_id == workspace.id
    assert created.user_id == user.id


def test_delete_member_removes_workspace_member(db_session: Session, workspace_member: WorkspaceMember) -> None:
    WorkspaceRepository().delete_member(db_session, workspace_member)

    item = WorkspaceRepository().get_member(
        db_session,
        workspace_member.workspace_id,
        workspace_member.user_id,
    )
    assert item is None
