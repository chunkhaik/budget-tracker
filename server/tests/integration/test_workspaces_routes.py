from fastapi import status
from fastapi.testclient import TestClient

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
        "items": [],
        "user_id": "00000000-0000-0000-0000-000000000001",
    }


def test_get_workspace_returns_placeholder_payload(client: TestClient, workspace: Workspace) -> None:
    response = client.get(f"/v1/workspaces/{workspace.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "workspace_id": str(workspace.id),
        "status": "todo",
    }
