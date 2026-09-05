import uuid

from app.core.security import build_dev_current_user
from app.schemas.commands import (
    TransactionCreateCommand,
    TransactionDeleteCommand,
    TransactionUpdateCommand,
)
from app.schemas.transaction import TransactionCreateRequest, TransactionUpdateRequest
from app.services.transactions import TransactionCommandService


class StubPublisher:
    def __init__(self) -> None:
        self.last_command: TransactionCreateCommand | TransactionUpdateCommand | TransactionDeleteCommand | None = None

    def publish_create(self, command: TransactionCreateCommand) -> str:
        self.last_command = command
        return "task-create-1"

    def publish_update(self, command: TransactionUpdateCommand) -> str:
        self.last_command = command
        return "task-update-1"

    def publish_delete(self, command: TransactionDeleteCommand) -> str:
        self.last_command = command
        return "task-delete-1"


def test_queue_create_builds_command_for_current_user() -> None:
    publisher = StubPublisher()
    service = TransactionCommandService(publisher=publisher)
    current_user = build_dev_current_user()

    transaction_id, task_id = service.queue_create(
        current_user=current_user,
        payload=TransactionCreateRequest(
            amount=1200,
            currency="USD",
            transaction_at=1725580800123,
            note="coffee",
        ),
    )

    assert task_id == "task-create-1"
    assert uuid.UUID(transaction_id)
    assert publisher.last_command is not None
    assert publisher.last_command.user_id == current_user.id
    assert publisher.last_command.currency == "USD"
    assert publisher.last_command.operation_key


def test_queue_update_builds_partial_command_for_current_user() -> None:
    publisher = StubPublisher()
    service = TransactionCommandService(publisher=publisher)
    current_user = build_dev_current_user()
    transaction_id = uuid.uuid4()

    task_id = service.queue_update(
        current_user=current_user,
        transaction_id=transaction_id,
        payload=TransactionUpdateRequest(
            amount=2400,
            note="lunch",
        ),
    )

    assert task_id == "task-update-1"
    assert publisher.last_command is not None
    assert publisher.last_command.transaction_id == transaction_id
    assert publisher.last_command.user_id == current_user.id
    assert publisher.last_command.amount == 2400
    assert publisher.last_command.note == "lunch"
    assert publisher.last_command.currency is None
    assert publisher.last_command.operation_key


def test_queue_delete_builds_delete_command_for_current_user() -> None:
    publisher = StubPublisher()
    service = TransactionCommandService(publisher=publisher)
    current_user = build_dev_current_user()
    transaction_id = uuid.uuid4()

    task_id = service.queue_delete(
        current_user=current_user,
        transaction_id=transaction_id,
    )

    assert task_id == "task-delete-1"
    assert publisher.last_command is not None
    assert publisher.last_command.transaction_id == transaction_id
    assert publisher.last_command.user_id == current_user.id
    assert publisher.last_command.amount == 0
    assert publisher.last_command.currency == "USD"
    assert publisher.last_command.transaction_at == 0
    assert publisher.last_command.note is None
    assert publisher.last_command.operation_key
