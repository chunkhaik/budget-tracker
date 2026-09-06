from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.domain.enums import RelationSelectionMode
from app.models.relation import WorkspaceRelation


def create_relation(db_session: Session, workspace, user, rule_definition=None) -> WorkspaceRelation:
    relation = WorkspaceRelation(
        workspace_id=workspace.id,
        name="Trip Spend",
        selection_mode=RelationSelectionMode.DYNAMIC,
        rule_definition=rule_definition,
        created_by_user_id=user.id,
    )
    db_session.add(relation)
    db_session.commit()
    return relation


def test_spending_returns_grouped_amounts(
    client: TestClient,
    db_session: Session,
    workspace,
    workspace_member,
    user,
    transaction_factory,
) -> None:
    _ = workspace_member
    transaction_factory(amount=1200)
    transaction_factory(amount=800)
    relation = create_relation(db_session, workspace, user, {"currencies": ["USD"]})

    response = client.get(
        f"/v1/workspaces/{workspace.id}/relations/{relation.id}/analytics/spending?currency=USD"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "workspace_id": str(workspace.id),
        "relation_id": str(relation.id),
        "metric": "spending",
        "items": [{"key": "total", "amount": 2000, "currency": "USD"}],
    }


def test_trends_rejects_mixed_currency_without_filter(
    client: TestClient,
    db_session: Session,
    workspace,
    workspace_member,
    user,
) -> None:
    _ = workspace_member
    relation = create_relation(db_session, workspace, user)

    response = client.get(f"/v1/workspaces/{workspace.id}/relations/{relation.id}/analytics/trends")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "mixed-currency aggregation requires a currency filter or currency grouping"
    }


def test_breakdown_groups_by_category_by_default(
    client: TestClient,
    db_session: Session,
    workspace,
    workspace_member,
    user,
    category,
    transaction_factory,
) -> None:
    _ = workspace_member
    transaction_factory(category_id=category.id, amount=900)
    relation = create_relation(db_session, workspace, user, {"category_ids": [str(category.id)]})

    response = client.get(
        f"/v1/workspaces/{workspace.id}/relations/{relation.id}/analytics/breakdown?currency=USD"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "workspace_id": str(workspace.id),
        "relation_id": str(relation.id),
        "metric": "breakdown",
        "items": [{"key": str(category.id), "amount": 900, "currency": "USD"}],
    }
