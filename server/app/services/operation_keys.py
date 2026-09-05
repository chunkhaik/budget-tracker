from uuid import UUID, uuid4

from app.domain.constants import (
    TRANSACTION_OPERATION_KEY_SEPARATOR,
    TRANSACTION_OPERATION_TIMESTAMP_WIDTH,
)


class OperationKeyError(ValueError):
    """Raised when an operation key is malformed."""


def build_operation_key(*, timestamp_ms: int, message_id: UUID | None = None) -> str:
    current_message_id = message_id or uuid4()
    return (
        f"{timestamp_ms:0{TRANSACTION_OPERATION_TIMESTAMP_WIDTH}d}"
        f"{TRANSACTION_OPERATION_KEY_SEPARATOR}{current_message_id}"
    )


def parse_operation_key(operation_key: str) -> tuple[int, str]:
    try:
        timestamp, message_id = operation_key.split(TRANSACTION_OPERATION_KEY_SEPARATOR, maxsplit=1)
    except ValueError as exc:
        raise OperationKeyError("operation_key must contain exactly one separator") from exc

    if len(timestamp) != TRANSACTION_OPERATION_TIMESTAMP_WIDTH or not timestamp.isdigit():
        raise OperationKeyError("operation_key timestamp must be a zero-padded 13-digit integer")

    return int(timestamp), message_id


def is_newer_operation(*, incoming_key: str, stored_key: str) -> bool:
    incoming_timestamp, incoming_message_id = parse_operation_key(incoming_key)
    stored_timestamp, stored_message_id = parse_operation_key(stored_key)

    if incoming_timestamp != stored_timestamp:
        return incoming_timestamp > stored_timestamp

    return incoming_message_id > stored_message_id
