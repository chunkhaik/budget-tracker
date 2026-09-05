from app.schemas.commands import (
    TransactionCreateCommand,
    TransactionDeleteCommand,
    TransactionUpdateCommand,
)
from app.services.operation_keys import is_newer_operation


class TransactionCommandConsumer:
    def should_apply(self, *, incoming_key: str, stored_key: str | None) -> bool:
        if stored_key is None:
            return True
        return is_newer_operation(incoming_key=incoming_key, stored_key=stored_key)

    def load_create(self, payload: dict) -> TransactionCreateCommand:
        return TransactionCreateCommand.model_validate(payload)

    def load_update(self, payload: dict) -> TransactionUpdateCommand:
        return TransactionUpdateCommand.model_validate(payload)

    def load_delete(self, payload: dict) -> TransactionDeleteCommand:
        return TransactionDeleteCommand.model_validate(payload)
