import uuid
from typing import Any, cast

from app.schemas.commands import (
    TransactionCreateCommand,
    TransactionDeleteCommand,
    TransactionUpdateCommand,
)
from app.worker.tasks.transactions import (
    _create_when_missing,
    _delete_when_missing,
    _update_when_missing,
)


class DummySession:
    pass


def build_create_command() -> TransactionCreateCommand:
    return TransactionCreateCommand(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000000000101"),
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        amount=1200,
        currency="USD",
        transaction_at=1725580800123,
        operation_key="1725580800123_a0000000-0000-0000-0000-000000000000",
    )


def build_update_command() -> TransactionUpdateCommand:
    return TransactionUpdateCommand(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000000000101"),
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        amount=2400,
        operation_key="1725580800124_b0000000-0000-0000-0000-000000000000",
    )


def build_delete_command() -> TransactionDeleteCommand:
    return TransactionDeleteCommand(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000000000101"),
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        operation_key="1725580800125_c0000000-0000-0000-0000-000000000000",
    )


def test_update_when_missing_returns_none() -> None:
    _update_when_missing(cast(Any, DummySession()), build_update_command())


def test_create_and_delete_missing_handlers_delegate_to_repository(monkeypatch: Any) -> None:
    session = cast(Any, DummySession())
    create_command = build_create_command()
    delete_command = build_delete_command()
    calls: list[tuple[str, Any, Any]] = []

    def fake_create(current_session: Any, current_command: TransactionCreateCommand) -> str:
        calls.append(("create", current_session, current_command))
        return "created"

    def fake_delete(current_session: Any, current_command: TransactionDeleteCommand) -> str:
        calls.append(("delete", current_session, current_command))
        return "deleted"

    monkeypatch.setattr("app.worker.tasks.transactions.repo.create_from_command", fake_create)
    monkeypatch.setattr("app.worker.tasks.transactions.repo.create_delete_tombstone", fake_delete)

    assert _create_when_missing(session, create_command) == "created"
    assert _delete_when_missing(session, delete_command) == "deleted"
    assert calls == [
        ("create", session, create_command),
        ("delete", session, delete_command),
    ]
