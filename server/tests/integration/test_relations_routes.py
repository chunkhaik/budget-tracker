from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.domain.enums import RelationSelectionMode
from app.models.relation import WorkspaceRelation


def test_list_relations_returns_workspace_relations(
    client: TestClient,
    db_session: Session,
    workspace,
    workspace_member,
    user,
) -> None:
    _ = workspace_member
    relation = WorkspaceRelation(
        workspace_id=workspace.id,
        name="Trip Spend",
        selection_mode=RelationSelectionMode.DYNAMIC,
        rule_definition={"currencies": ["USD"]},
        created_by_user_id=user.id,
    )
    db_session.add(relation)
    db_session.commit()

    response = client.get(f"/v1/workspaces/{workspace.id}/relations")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "workspace_id": str(workspace.id),
        "items": [
            {
                "id": str(relation.id),
                "name": "Trip Spend",
                "description": None,
                "selection_mode": "dynamic",
                "rule_definition": {"user_ids": [], "category_ids": [], "from": None, "to": None, "amount_min": None, "amount_max": None, "currencies": ["USD"], "note_contains": [], "transaction_ids": [], "include_transaction_ids": [], "exclude_transaction_ids": []},
            }
        ],
    }


def test_create_relation_persists_relation(client: TestClient, workspace, workspace_member, db_session: Session) -> None:
    _ = workspace_member

    response = client.post(
        f"/v1/workspaces/{workspace.id}/relations",
        json={
            "name": "Trip Spend",
            "selection_mode": "dynamic",
            "rule_definition": {"currencies": ["USD"]},
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "Trip Spend"
    assert response.json()["selection_mode"] == "dynamic"


def test_preview_relation_returns_matching_transactions(
    client: TestClient,
    workspace,
    workspace_member,
    transaction_factory,
) -> None:
    _ = workspace_member
    keep = transaction_factory(note="trip dinner")
    transaction_factory(note="groceries")

    response = client.post(
        f"/v1/workspaces/{workspace.id}/relations/preview",
        json={
            "name": "Trip Spend",
            "selection_mode": "dynamic",
            "rule_definition": {"note_contains": ["trip"]},
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["workspace_id"] == str(workspace.id)
    assert [item["transaction_id"] for item in response.json()["items"]] == [str(keep.transaction_id)]
