import time
from typing import Protocol
from uuid import UUID, uuid4

from app.core.security import CurrentUser
from app.schemas.commands import (
    TransactionCreateCommand,
    TransactionDeleteCommand,
    TransactionUpdateCommand,
)
from app.schemas.transaction import TransactionCreateRequest, TransactionUpdateRequest
from app.services.command_publisher import CommandPublisher
from app.services.operation_keys import build_operation_key


class TransactionPublisher(Protocol):
    def publish_create(self, command: TransactionCreateCommand) -> str: ...

    def publish_update(self, command: TransactionUpdateCommand) -> str: ...

    def publish_delete(self, command: TransactionDeleteCommand) -> str: ...


class TransactionCommandService:
    def __init__(self, publisher: TransactionPublisher | None = None) -> None:
        self.publisher = publisher or CommandPublisher()

    def queue_create(self, current_user: CurrentUser, payload: TransactionCreateRequest) -> tuple[str, str]:
        message_id = uuid4()
        operation_key = build_operation_key(timestamp_ms=int(time.time() * 1000), message_id=message_id)
        transaction_id = uuid4()
        command = TransactionCreateCommand(
            **payload.model_dump(),
            message_id=message_id,
            operation_key=operation_key,
            transaction_id=transaction_id,
            user_id=current_user.id,
        )
        task_id = self.publisher.publish_create(command)
        return str(transaction_id), task_id

    def queue_update(
        self,
        current_user: CurrentUser,
        transaction_id: UUID,
        payload: TransactionUpdateRequest,
    ) -> str:
        message_id = uuid4()
        operation_key = build_operation_key(timestamp_ms=int(time.time() * 1000), message_id=message_id)
        command = TransactionUpdateCommand(
            **payload.model_dump(exclude_none=True),
            message_id=message_id,
            operation_key=operation_key,
            transaction_id=transaction_id,
            user_id=current_user.id,
        )
        return self.publisher.publish_update(command)

    def queue_delete(self, current_user: CurrentUser, transaction_id: UUID) -> str:
        message_id = uuid4()
        operation_key = build_operation_key(timestamp_ms=int(time.time() * 1000), message_id=message_id)
        command = TransactionDeleteCommand(
            message_id=message_id,
            operation_key=operation_key,
            transaction_id=transaction_id,
            user_id=current_user.id,
        )
        return self.publisher.publish_delete(command)
