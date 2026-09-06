from uuid import UUID, uuid4

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember


def test_list_workspaces_returns_current_user_items(
    client: TestClient,
    workspace: Workspace,
    workspace_member: WorkspaceMember,
) -> None:
    _ = workspace_member

    response = client.get("/v1/workspaces")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "items": [
            {
                "id": str(workspace.id),
                "name": "Household",
                "base_currency": "USD",
            }
        ],
        "user_id": "00000000-0000-0000-0000-000000000001",
    }


def test_create_workspace_creates_owner_membership(client: TestClient, db_session: Session) -> None:
    response = client.post(
        "/v1/workspaces",
        json={
            "name": "Trip",
            "base_currency": "JPY",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    workspace_id = UUID(response.json()["id"])
    assert response.json() == {
        "id": str(workspace_id),
        "name": "Trip",
        "base_currency": "JPY",
    }
    member = db_session.get(WorkspaceMember, (workspace_id, UUID("00000000-0000-0000-0000-000000000001")))
    assert member is not None
    assert member.role == "owner"


def test_get_workspace_returns_workspace_for_member(client: TestClient, workspace: Workspace, workspace_member: WorkspaceMember) -> None:
    _ = workspace_member

    response = client.get(f"/v1/workspaces/{workspace.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(workspace.id),
        "name": "Household",
        "base_currency": "USD",
    }


def test_get_workspace_returns_not_found_for_non_member(client: TestClient, workspace: Workspace) -> None:
    response = client.get(f"/v1/workspaces/{workspace.id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "workspace not found"}


def test_add_workspace_member_requires_owner_role(
    client: TestClient,
    db_session: Session,
    workspace: Workspace,
    workspace_member: WorkspaceMember,
    other_user: User,
) -> None:
    _ = workspace_member

    response = client.post(
        f"/v1/workspaces/{workspace.id}/members",
        json={
            "user_id": str(other_user.id),
            "role": "member",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["workspace_id"] == str(workspace.id)
    assert response.json()["user_id"] == str(other_user.id)
    assert response.json()["role"] == "member"


def test_remove_workspace_member_deletes_membership(
    client: TestClient,
    db_session: Session,
    workspace: Workspace,
    workspace_member: WorkspaceMember,
    other_user: User,
) -> None:
    _ = workspace_member
    removable = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=other_user.id,
        role="member",
    )
    db_session.add(removable)
    db_session.commit()

    response = client.delete(f"/v1/workspaces/{workspace.id}/members/{other_user.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(other_user.id),
        "workspace_id": str(workspace.id),
        "status": "deleted",
    }
    assert db_session.get(WorkspaceMember, (workspace.id, other_user.id)) is None
