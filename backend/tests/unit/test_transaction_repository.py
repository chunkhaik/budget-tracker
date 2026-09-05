import uuid

from app.repos.transactions import TransactionRepository
from app.schemas.commands import (
    TransactionCreateCommand,
    TransactionDeleteCommand,
    TransactionUpdateCommand,
)


class FakeSession:
    def __init__(self) -> None:
        self.added = []
        self.flush_count = 0

    def add(self, obj) -> None:
        self.added.append(obj)

    def flush(self) -> None:
        self.flush_count += 1


class StubTransaction:
    def __init__(self) -> None:
        self.transaction_id = uuid.uuid4()
        self.user_id = uuid.uuid4()
        self.category_id = uuid.uuid4()
        self.amount = 1200
        self.currency = "USD"
        self.transaction_at = 1725580800123
        self.note = "coffee"
        self.last_operation_key = "1725580800123_a0000000-0000-0000-0000-000000000000"
        self.version = 1
        self.deleted_at = None
        self.created_at = 1725580800123
        self.updated_at = 1725580800123


class TestTransactionRepository(TransactionRepository):
    def __init__(self, *, now_ms: int) -> None:
        super().__init__()
        self.now_ms = now_ms

    def current_timestamp_ms(self) -> int:
        return self.now_ms


def build_create_command() -> TransactionCreateCommand:
    return TransactionCreateCommand(
        transaction_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        category_id=uuid.uuid4(),
        amount=1200,
        currency="USD",
        transaction_at=1725580800123,
        note="coffee",
        operation_key="1725580800123_a0000000-0000-0000-0000-000000000000",
    )


def build_update_command() -> TransactionUpdateCommand:
    return TransactionUpdateCommand(
        transaction_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        amount=2400,
        note="lunch",
        operation_key="1725580800124_b0000000-0000-0000-0000-000000000000",
    )


def build_delete_command() -> TransactionDeleteCommand:
    return TransactionDeleteCommand(
        transaction_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        operation_key="1725580800125_c0000000-0000-0000-0000-000000000000",
    )


def test_create_from_command_builds_new_transaction() -> None:
    repo = TestTransactionRepository(now_ms=1725580800999)
    session = FakeSession()
    command = build_create_command()

    transaction = repo.create_from_command(session, command)

    assert transaction.transaction_id == command.transaction_id
    assert transaction.user_id == command.user_id
    assert transaction.category_id == command.category_id
    assert transaction.amount == command.amount
    assert transaction.currency == command.currency
    assert transaction.transaction_at == command.transaction_at
    assert transaction.note == command.note
    assert transaction.last_operation_key == command.operation_key
    assert transaction.version == 1
    assert transaction.deleted_at is None
    assert transaction.created_at == 1725580800999
    assert transaction.updated_at == 1725580800999
    assert session.added == [transaction]
    assert session.flush_count == 1


def test_apply_create_overwrites_existing_transaction_state() -> None:
    repo = TestTransactionRepository(now_ms=1725580800999)
    session = FakeSession()
    transaction = StubTransaction()
    command = build_create_command()

    updated = repo.apply_create(session, transaction, command)

    assert updated is transaction
    assert transaction.user_id == command.user_id
    assert transaction.category_id == command.category_id
    assert transaction.amount == command.amount
    assert transaction.currency == command.currency
    assert transaction.transaction_at == command.transaction_at
    assert transaction.note == command.note
    assert transaction.last_operation_key == command.operation_key
    assert transaction.deleted_at is None
    assert transaction.version == 2
    assert transaction.updated_at == 1725580800999
    assert session.added == [transaction]
    assert session.flush_count == 1


def test_apply_update_changes_only_fields_present_in_command() -> None:
    repo = TestTransactionRepository(now_ms=1725580800999)
    session = FakeSession()
    transaction = StubTransaction()
    original_category_id = transaction.category_id
    original_currency = transaction.currency
    original_transaction_at = transaction.transaction_at

    updated = repo.apply_update(session, transaction, build_update_command())

    assert updated is transaction
    assert transaction.category_id == original_category_id
    assert transaction.amount == 2400
    assert transaction.currency == original_currency
    assert transaction.transaction_at == original_transaction_at
    assert transaction.note == "lunch"
    assert transaction.last_operation_key == "1725580800124_b0000000-0000-0000-0000-000000000000"
    assert transaction.version == 2
    assert transaction.updated_at == 1725580800999
    assert session.added == [transaction]
    assert session.flush_count == 1


def test_create_delete_tombstone_builds_deleted_transaction() -> None:
    repo = TestTransactionRepository(now_ms=1725580800999)
    session = FakeSession()
    command = build_delete_command()

    transaction = repo.create_delete_tombstone(session, command)

    assert transaction.transaction_id == command.transaction_id
    assert transaction.user_id == command.user_id
    assert transaction.amount == 0
    assert transaction.currency == "USD"
    assert transaction.transaction_at == 0
    assert transaction.note is None
    assert transaction.last_operation_key == command.operation_key
    assert transaction.version == 1
    assert transaction.deleted_at == 1725580800999
    assert transaction.created_at == 1725580800999
    assert transaction.updated_at == 1725580800999
    assert session.added == [transaction]
    assert session.flush_count == 1


def test_apply_delete_marks_existing_transaction_deleted() -> None:
    repo = TestTransactionRepository(now_ms=1725580800999)
    session = FakeSession()
    transaction = StubTransaction()

    updated = repo.apply_delete(session, transaction, build_delete_command())

    assert updated is transaction
    assert transaction.last_operation_key == "1725580800125_c0000000-0000-0000-0000-000000000000"
    assert transaction.version == 2
    assert transaction.deleted_at == 1725580800999
    assert transaction.updated_at == 1725580800999
    assert session.added == [transaction]
    assert session.flush_count == 1
