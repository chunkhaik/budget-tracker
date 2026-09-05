import logging

from app.core.config import get_settings
from app.schemas.commands import (
    TransactionCreateCommand,
    TransactionDeleteCommand,
    TransactionUpdateCommand,
)
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


class CommandPublisher:
    def publish_create(self, command: TransactionCreateCommand) -> str:
        task = celery_app.send_task(
            "app.worker.tasks.transactions.handle_create_transaction",
            kwargs={"payload": command.model_dump(mode="json")},
            queue=settings.transaction_queue_name,
        )
        logger.info("published transaction create command", extra={"task_id": task.id})
        return str(task.id)

    def publish_update(self, command: TransactionUpdateCommand) -> str:
        task = celery_app.send_task(
            "app.worker.tasks.transactions.handle_update_transaction",
            kwargs={"payload": command.model_dump(mode="json")},
            queue=settings.transaction_queue_name,
        )
        logger.info("published transaction update command", extra={"task_id": task.id})
        return str(task.id)

    def publish_delete(self, command: TransactionDeleteCommand) -> str:
        task = celery_app.send_task(
            "app.worker.tasks.transactions.handle_delete_transaction",
            kwargs={"payload": command.model_dump(mode="json")},
            queue=settings.transaction_queue_name,
        )
        logger.info("published transaction delete command", extra={"task_id": task.id})
        return str(task.id)
