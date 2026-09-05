from app.worker.consumers.transaction_commands import TransactionCommandConsumer


class StubConsumer(TransactionCommandConsumer):
    pass


def test_should_apply_accepts_first_command_without_stored_key() -> None:
    consumer = StubConsumer()

    assert consumer.should_apply(
        incoming_key="1725580800123_a0000000-0000-0000-0000-000000000000",
        stored_key=None,
    )


def test_should_apply_rejects_older_command_when_stored_key_exists() -> None:
    consumer = StubConsumer()

    assert not consumer.should_apply(
        incoming_key="1725580800123_a0000000-0000-0000-0000-000000000000",
        stored_key="1725580800124_a0000000-0000-0000-0000-000000000000",
    )
