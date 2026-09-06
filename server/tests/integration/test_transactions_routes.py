from typing import Any
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient


def test_list_transactions_returns_only_current_user_items(client: TestClient, transaction_factory: Any) -> None:
    keep = transaction_factory(note="coffee")
    transaction_factory(note="deleted", deleted_at=1725580800999)

    response = client.get("/v1/transactions")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "items": [
            {
                "transaction_id": str(keep.transaction_id),
                "category_id": str(keep.category_id),
                "amount": 1200,
                "currency": "USD",
                "transaction_at": 1725580800123,
                "note": "coffee",
                "version": 1,
                "deleted_at": None,
            }
        ],
        "user_id": "00000000-0000-0000-0000-000000000001",
    }


def test_get_transaction_returns_not_found_for_missing_record(client: TestClient) -> None:
    response = client.get(f"/v1/transactions/{uuid4()}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "transaction not found"}


def test_get_transaction_returns_current_user_record(client: TestClient, transaction_factory: Any) -> None:
    transaction = transaction_factory(note="rent")

    response = client.get(f"/v1/transactions/{transaction.transaction_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "transaction_id": str(transaction.transaction_id),
        "category_id": str(transaction.category_id),
        "amount": 1200,
        "currency": "USD",
        "transaction_at": 1725580800123,
        "note": "rent",
        "version": 1,
        "deleted_at": None,
    }
