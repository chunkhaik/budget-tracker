from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.commands import TransactionCreateCommand
from app.worker.tasks.transactions import handle_create_transaction


def build_create_payload(*, user_id: UUID) -> dict[str, Any]:
    return TransactionCreateCommand(
        transaction_id=uuid4(),
        user_id=user_id,
        category_id=None,
        amount=1200,
        currency="USD",
        transaction_at=1725580800123,
        note="coffee",
        operation_key=f"1725580800123_{uuid4()}",
    ).model_dump(mode="json")


def test_handle_create_transaction_ignores_missing_user(
    sqlite_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.worker.tasks.transactions.engine", sqlite_engine)

    result = handle_create_transaction(
        payload=build_create_payload(
            user_id=UUID("00000000-0000-0000-0000-000000000001"),
        )
    )

    assert result["status"] == "ignored"

    with Session(sqlite_engine) as session:
        assert session.exec(select(Transaction)).all() == []


def test_handle_create_transaction_persists_record_when_user_exists(
    sqlite_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.worker.tasks.transactions.engine", sqlite_engine)
    user_id = UUID("00000000-0000-0000-0000-000000000001")
    payload = build_create_payload(user_id=user_id)

    with Session(sqlite_engine) as session:
        session.add(
            User(
                id=user_id,
                email="dev-user@example.com",
                display_name="Dev User",
            )
        )
        session.commit()

    result = handle_create_transaction(payload=payload)

    assert result == {
        "status": "applied",
        "transaction_id": payload["transaction_id"],
    }
    with Session(sqlite_engine) as session:
        transaction = session.exec(select(Transaction)).one()

    assert transaction.transaction_id == UUID(cast(str, payload["transaction_id"]))
    assert transaction.user_id == user_id
    assert transaction.amount == 1200
    assert transaction.note == "coffee"
