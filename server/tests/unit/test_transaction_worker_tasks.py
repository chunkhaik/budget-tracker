import uuid
from typing import Any, cast

from app.models.transaction import Transaction
from app.schemas.commands import (
    TransactionCreateCommand,
    TransactionDeleteCommand,
    TransactionUpdateCommand,
)
from app.worker.tasks.transactions import (
    _apply_command,
    _create_when_missing,
    _delete_when_missing,
    _update_when_missing,
)


class DummySession:
    def __init__(self) -> None:
        self.commit_count = 0

    def commit(self) -> None:
        self.commit_count += 1


class DummySessionContext:
    def __init__(self, session: DummySession) -> None:
        self.session = session

    def __enter__(self) -> DummySession:
        return self.session

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None


class DummyCommand:
    def __init__(
        self,
        *,
        transaction_id: uuid.UUID,
        operation_key: str,
        user_id: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000001"),
    ) -> None:
        self.transaction_id = transaction_id
        self.operation_key = operation_key
        self.user_id = user_id


class StubTransaction:
    def __init__(self) -> None:
        self.transaction_id = uuid.uuid4()
        self.last_operation_key = "1725580800123_a0000000-0000-0000-0000-000000000000"
        self.version = 1
        self.deleted_at = None


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


def test_apply_command_ignores_stale_command(monkeypatch: Any) -> None:
    session = DummySession()
    command = DummyCommand(
        transaction_id=uuid.uuid4(),
        operation_key="1725580800122_a0000000-0000-0000-0000-000000000000",
    )
    existing = StubTransaction()

    monkeypatch.setattr("app.worker.tasks.transactions.Session", lambda _: DummySessionContext(session))
    monkeypatch.setattr("app.worker.tasks.transactions.repo.get_by_public_id", lambda *_: existing)
    monkeypatch.setattr("app.worker.tasks.transactions.user_repo.get", lambda *_: object())
    monkeypatch.setattr("app.worker.tasks.transactions.consumer.should_apply", lambda **_: False)

    result = _apply_command(
        payload={},
        load_command=lambda _: command,
        apply_when_missing=lambda *_: None,
        apply_when_present=lambda *_: cast(Transaction, existing),
    )

    assert result == {
        "status": "ignored",
        "transaction_id": str(command.transaction_id),
    }
    assert session.commit_count == 0


def test_apply_command_ignores_missing_user(monkeypatch: Any) -> None:
    session = DummySession()
    command = DummyCommand(
        transaction_id=uuid.uuid4(),
        operation_key="1725580800124_b0000000-0000-0000-0000-000000000000",
    )

    monkeypatch.setattr("app.worker.tasks.transactions.Session", lambda _: DummySessionContext(session))
    monkeypatch.setattr("app.worker.tasks.transactions.repo.get_by_public_id", lambda *_: None)
    monkeypatch.setattr("app.worker.tasks.transactions.user_repo.get", lambda *_: None)
    monkeypatch.setattr("app.worker.tasks.transactions.consumer.should_apply", lambda **_: True)

    result = _apply_command(
        payload={},
        load_command=lambda _: command,
        apply_when_missing=lambda *_: cast(Transaction, StubTransaction()),
        apply_when_present=lambda *_: cast(Transaction, StubTransaction()),
    )

    assert result == {
        "status": "ignored",
        "transaction_id": str(command.transaction_id),
    }
    assert session.commit_count == 0


def test_apply_command_applies_missing_command_and_commits(monkeypatch: Any) -> None:
    session = DummySession()
    command = DummyCommand(
        transaction_id=uuid.uuid4(),
        operation_key="1725580800124_b0000000-0000-0000-0000-000000000000",
    )
    created = StubTransaction()
    created.transaction_id = command.transaction_id
    created.last_operation_key = command.operation_key

    monkeypatch.setattr("app.worker.tasks.transactions.Session", lambda _: DummySessionContext(session))
    monkeypatch.setattr("app.worker.tasks.transactions.repo.get_by_public_id", lambda *_: None)
    monkeypatch.setattr(
        "app.worker.tasks.transactions.user_repo.get",
        lambda *_: object(),
    )
    monkeypatch.setattr("app.worker.tasks.transactions.consumer.should_apply", lambda **_: True)

    result = _apply_command(
        payload={},
        load_command=lambda _: command,
        apply_when_missing=lambda *_: cast(Transaction, created),
        apply_when_present=lambda *_: cast(Transaction, created),
    )

    assert result == {
        "status": "applied",
        "transaction_id": str(command.transaction_id),
    }
    assert session.commit_count == 1


def test_apply_command_ignores_missing_update_when_handler_returns_none(monkeypatch: Any) -> None:
    session = DummySession()
    command = DummyCommand(
        transaction_id=uuid.uuid4(),
        operation_key="1725580800124_b0000000-0000-0000-0000-000000000000",
    )

    monkeypatch.setattr("app.worker.tasks.transactions.Session", lambda _: DummySessionContext(session))
    monkeypatch.setattr("app.worker.tasks.transactions.repo.get_by_public_id", lambda *_: None)
    monkeypatch.setattr("app.worker.tasks.transactions.user_repo.get", lambda *_: object())
    monkeypatch.setattr("app.worker.tasks.transactions.consumer.should_apply", lambda **_: True)

    result = _apply_command(
        payload={},
        load_command=lambda _: command,
        apply_when_missing=lambda *_: None,
        apply_when_present=lambda *_: cast(Transaction, StubTransaction()),
    )

    assert result == {
        "status": "ignored",
        "transaction_id": str(command.transaction_id),
    }
    assert session.commit_count == 0
