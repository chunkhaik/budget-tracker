from app.worker.tasks.transactions import (
    _create_when_missing,
    _delete_when_missing,
    _update_when_missing,
)


class DummySession:
    pass


class DummyCommand:
    pass


def test_update_when_missing_returns_none() -> None:
    assert _update_when_missing(DummySession(), DummyCommand()) is None


def test_create_and_delete_missing_handlers_delegate_to_repository(monkeypatch) -> None:
    session = DummySession()
    command = DummyCommand()
    calls = []

    def fake_create(current_session, current_command):
        calls.append(("create", current_session, current_command))
        return "created"

    def fake_delete(current_session, current_command):
        calls.append(("delete", current_session, current_command))
        return "deleted"

    monkeypatch.setattr("app.worker.tasks.transactions.repo.create_from_command", fake_create)
    monkeypatch.setattr("app.worker.tasks.transactions.repo.create_delete_tombstone", fake_delete)

    assert _create_when_missing(session, command) == "created"
    assert _delete_when_missing(session, command) == "deleted"
    assert calls == [
        ("create", session, command),
        ("delete", session, command),
    ]
