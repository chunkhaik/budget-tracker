from uuid import UUID, uuid4

from pydantic import Field

from app.domain.enums import TransactionCommandType
from app.schemas.transaction import TransactionCreateRequest, TransactionUpdateRequest


class TransactionCommandBase(TransactionCreateRequest):
    command_type: TransactionCommandType
    message_id: UUID = Field(default_factory=uuid4)
    operation_key: str
    user_id: UUID


class TransactionCreateCommand(TransactionCommandBase):
    command_type: TransactionCommandType = TransactionCommandType.CREATE
    transaction_id: UUID


class TransactionUpdateCommand(TransactionUpdateRequest):
    command_type: TransactionCommandType = TransactionCommandType.UPDATE
    message_id: UUID = Field(default_factory=uuid4)
    operation_key: str
    transaction_id: UUID
    user_id: UUID


class TransactionDeleteCommand(TransactionCommandBase):
    command_type: TransactionCommandType = TransactionCommandType.DELETE
    transaction_id: UUID

    category_id: UUID | None = None
    amount: int = 0
    currency: str = "USD"
    transaction_at: int = 0
    note: str | None = None
