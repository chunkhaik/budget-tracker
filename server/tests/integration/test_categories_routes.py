from fastapi import status
from fastapi.testclient import TestClient

from app.models.category import Category


def test_list_categories_returns_current_user_items(client: TestClient, category: Category) -> None:
    response = client.get("/v1/categories")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "items": [
            {
                "id": str(category.id),
                "created_at": category.created_at.isoformat(),
                "updated_at": category.updated_at.isoformat(),
                "user_id": "00000000-0000-0000-0000-000000000001",
                "name": "Food",
                "type": "expense",
            }
        ],
        "user_id": "00000000-0000-0000-0000-000000000001",
    }
