from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.category import Category


def test_list_categories_returns_current_user_items(client: TestClient, category: Category) -> None:
    response = client.get("/v1/categories")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "items": [
            {
                "id": str(category.id),
                "name": "Food",
                "type": "expense",
            }
        ],
        "user_id": "00000000-0000-0000-0000-000000000001",
    }


def test_create_category_creates_user_scoped_category(client: TestClient) -> None:
    response = client.post(
        "/v1/categories",
        json={
            "name": "Rent",
            "type": "expense",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "Rent"
    assert response.json()["type"] == "expense"
    assert response.json()["id"]


def test_update_category_updates_owned_category(client: TestClient, category: Category) -> None:
    response = client.patch(
        f"/v1/categories/{category.id}",
        json={"name": "Dining"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(category.id),
        "name": "Dining",
        "type": "expense",
    }


def test_update_category_returns_not_found_for_other_users_category(
    client: TestClient,
    db_session: Session,
    other_user_category: Category,
) -> None:
    response = client.patch(
        f"/v1/categories/{other_user_category.id}",
        json={"name": "Nope"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "category not found"}

    db_session.refresh(other_user_category)
    assert other_user_category.name == "Salary"


def test_delete_category_deletes_owned_category(client: TestClient, category: Category, db_session: Session) -> None:
    response = client.delete(f"/v1/categories/{category.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(category.id),
        "status": "deleted",
    }
    assert db_session.get(Category, category.id) is None


def test_delete_category_returns_not_found_for_missing_record(client: TestClient) -> None:
    response = client.delete(f"/v1/categories/{uuid4()}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "category not found"}
