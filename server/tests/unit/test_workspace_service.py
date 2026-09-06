from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.domain.enums import WorkspaceRole
from app.models.workspace import Workspace, WorkspaceMember
from app.repos.workspaces import WorkspaceRepository
from app.schemas.workspace import WorkspaceCreateRequest, WorkspaceMemberCreateRequest
from app.services.workspaces import WorkspaceService


class StubWorkspaceRepository(WorkspaceRepository):
    def __init__(self, items: list[Any]) -> None:
        self.items = items
        self.list_calls: list[tuple[Session, UUID]] = []
        self.workspaces: dict[UUID, Workspace] = {}
        self.members: dict[tuple[UUID, UUID], WorkspaceMember] = {}
        self.created_workspaces: list[Workspace] = []
        self.created_members: list[WorkspaceMember] = []
        self.deleted_members: list[WorkspaceMember] = []

    def list_for_user(self, session: Session, user_id: UUID) -> list[Any]:
        self.list_calls.append((session, user_id))
        return self.items

    def get(self, _session: Session, workspace_id: UUID) -> Workspace | None:
        return self.workspaces.get(workspace_id)

    def get_member(self, _session: Session, workspace_id: UUID, user_id: UUID) -> WorkspaceMember | None:
        return self.members.get((workspace_id, user_id))

    def create(self, _session: Session, workspace: Workspace) -> Workspace:
        self.created_workspaces.append(workspace)
        self.workspaces[workspace.id] = workspace
        return workspace

    def create_member(self, _session: Session, member: WorkspaceMember) -> WorkspaceMember:
        self.created_members.append(member)
        self.members[(member.workspace_id, member.user_id)] = member
        return member

    def delete_member(self, _session: Session, member: WorkspaceMember) -> None:
        self.deleted_members.append(member)
        self.members.pop((member.workspace_id, member.user_id), None)


def test_list_for_user_delegates_to_repository() -> None:
    session = cast(Session, object())
    user_id = uuid4()
    items = [object()]
    repository = StubWorkspaceRepository(items)

    result = WorkspaceService(repository=repository).list_for_user(session, user_id)

    assert result == items
    assert repository.list_calls == [(session, user_id)]


def test_create_workspace_creates_owner_membership() -> None:
    session = cast(Session, object())
    user_id = uuid4()
    repository = StubWorkspaceRepository([])

    workspace = WorkspaceService(repository=repository).create_workspace(
        session,
        user_id,
        WorkspaceCreateRequest(name="Trip", base_currency="USD"),
    )

    assert workspace.name == "Trip"
    assert repository.created_workspaces == [workspace]
    assert repository.created_members[0].workspace_id == workspace.id
    assert repository.created_members[0].user_id == user_id
    assert repository.created_members[0].role == WorkspaceRole.OWNER


def test_require_member_raises_not_found_for_non_member() -> None:
    session = cast(Session, object())
    repository = StubWorkspaceRepository([])

    with pytest.raises(HTTPException, match="workspace not found"):
        WorkspaceService(repository=repository).require_member(session, uuid4(), uuid4())


def test_require_role_raises_for_insufficient_role() -> None:
    session = cast(Session, object())
    workspace_id = uuid4()
    user_id = uuid4()
    repository = StubWorkspaceRepository([])
    repository.members[(workspace_id, user_id)] = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=user_id,
        role=WorkspaceRole.VIEWER,
    )

    with pytest.raises(HTTPException, match="insufficient workspace role"):
        WorkspaceService(repository=repository).require_role(
            session,
            workspace_id,
            user_id,
            WorkspaceRole.OWNER,
        )


def test_add_member_updates_existing_role() -> None:
    session = cast(Session, object())
    workspace_id = uuid4()
    owner_id = uuid4()
    member_id = uuid4()
    repository = StubWorkspaceRepository([])
    repository.workspaces[workspace_id] = Workspace(id=workspace_id, name="Trip", base_currency="USD")
    repository.members[(workspace_id, owner_id)] = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=owner_id,
        role=WorkspaceRole.OWNER,
    )
    existing = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=member_id,
        role=WorkspaceRole.VIEWER,
    )
    repository.members[(workspace_id, member_id)] = existing

    member = WorkspaceService(repository=repository).add_member(
        session,
        workspace_id,
        owner_id,
        WorkspaceMemberCreateRequest(user_id=member_id, role=WorkspaceRole.MEMBER),
    )

    assert member.role == WorkspaceRole.MEMBER
    assert repository.members[(workspace_id, member_id)].role == WorkspaceRole.MEMBER


def test_remove_member_deletes_member_after_owner_check() -> None:
    session = cast(Session, object())
    workspace_id = uuid4()
    owner_id = uuid4()
    member_id = uuid4()
    repository = StubWorkspaceRepository([])
    repository.members[(workspace_id, owner_id)] = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=owner_id,
        role=WorkspaceRole.OWNER,
    )
    member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=member_id,
        role=WorkspaceRole.MEMBER,
    )
    repository.members[(workspace_id, member_id)] = member

    WorkspaceService(repository=repository).remove_member(session, workspace_id, owner_id, member_id)

    assert repository.deleted_members == [member]
