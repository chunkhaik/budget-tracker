import uuid

import pytest

from app.services.operation_keys import OperationKeyError, build_operation_key, is_newer_operation, parse_operation_key


def test_build_operation_key_uses_padded_timestamp() -> None:
    message_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

    operation_key = build_operation_key(timestamp_ms=1725580800123, message_id=message_id)

    assert operation_key == "1725580800123_550e8400-e29b-41d4-a716-446655440000"


def test_parse_operation_key_returns_timestamp_and_message_id() -> None:
    timestamp, message_id = parse_operation_key("1725580800123_550e8400-e29b-41d4-a716-446655440000")

    assert timestamp == 1725580800123
    assert message_id == "550e8400-e29b-41d4-a716-446655440000"


def test_parse_operation_key_rejects_invalid_value() -> None:
    with pytest.raises(OperationKeyError):
        parse_operation_key("bad-key")


def test_is_newer_operation_compares_timestamp_then_message_id() -> None:
    assert is_newer_operation(
        incoming_key="1725580800124_10000000-0000-0000-0000-000000000000",
        stored_key="1725580800123_ffffffff-ffff-ffff-ffff-ffffffffffff",
    )
    assert is_newer_operation(
        incoming_key="1725580800123_b0000000-0000-0000-0000-000000000000",
        stored_key="1725580800123_a0000000-0000-0000-0000-000000000000",
    )
    assert not is_newer_operation(
        incoming_key="1725580800123_a0000000-0000-0000-0000-000000000000",
        stored_key="1725580800123_b0000000-0000-0000-0000-000000000000",
    )
