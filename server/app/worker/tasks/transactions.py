import logging
from collections.abc import Callable
from typing import Protocol
from uuid import UUID

from sqlmodel import Session

from app.core.db import engine
from app.models.transaction import Transaction
from app.repos.transactions import TransactionRepository
from app.repos.users import UserRepository
from app.schemas.commands import (
    TransactionCreateCommand,
    TransactionDeleteCommand,
    TransactionUpdateCommand,
)
from app.worker.celery_app import celery_app
from app.worker.consumers.transaction_commands import TransactionCommandConsumer

logger = logging.getLogger(__name__)
consumer = TransactionCommandConsumer()
repo = TransactionRepository()
user_repo = UserRepository()


class TransactionCommandProtocol(Protocol):
    transaction_id: UUID
    operation_key: str
    user_id: UUID


def _apply_command(
    *,
    payload: dict,
    load_command: Callable[[dict], TransactionCommandProtocol],
    apply_when_missing: Callable[[Session, TransactionCommandProtocol], Transaction | None],
    apply_when_present: Callable[[Session, Transaction, TransactionCommandProtocol], Transaction],
) -> dict[str, str]:
    command = load_command(payload)

    with Session(engine) as session:
        transaction = repo.get_by_public_id(session, command.transaction_id)
        stored_key = transaction.last_operation_key if transaction else None
        if not consumer.should_apply(incoming_key=command.operation_key, stored_key=stored_key):
            logger.info(
                "ignored stale transaction command",
                extra={
                    "transaction_id": str(command.transaction_id),
                    "operation_key": command.operation_key,
                    "stored_operation_key": stored_key,
                },
            )
            return {
                "status": "ignored",
                "transaction_id": str(command.transaction_id),
            }

        if transaction is None:
            if user_repo.get(session, command.user_id) is None:
                logger.info(
                    "ignored transaction command for missing user",
                    extra={
                        "transaction_id": str(command.transaction_id),
                        "user_id": str(command.user_id),
                        "operation_key": command.operation_key,
                    },
                )
                return {
                    "status": "ignored",
                    "transaction_id": str(command.transaction_id),
                }

            transaction = apply_when_missing(session, command)
            if transaction is None:
                logger.info(
                    "ignored transaction command for missing record",
                    extra={
                        "transaction_id": str(command.transaction_id),
                        "operation_key": command.operation_key,
                    },
                )
                return {
                    "status": "ignored",
                    "transaction_id": str(command.transaction_id),
                }
        else:
            transaction = apply_when_present(session, transaction, command)

        session.commit()
        logger.info(
            "applied transaction command",
            extra={
                "transaction_id": str(transaction.transaction_id),
                "operation_key": transaction.last_operation_key,
                "version": transaction.version,
                "deleted_at": transaction.deleted_at,
            },
        )
        return {
            "status": "applied",
            "transaction_id": str(transaction.transaction_id),
        }


def _create_when_missing(session: Session, command: TransactionCommandProtocol) -> Transaction:
    return repo.create_from_command(session, TransactionCreateCommand.model_validate(command))


def _update_when_missing(_: Session, __: TransactionCommandProtocol) -> None:
    return None


def _delete_when_missing(session: Session, command: TransactionCommandProtocol) -> Transaction:
    return repo.create_delete_tombstone(session, TransactionDeleteCommand.model_validate(command))


def _apply_create_when_present(
    session: Session,
    transaction: Transaction,
    command: TransactionCommandProtocol,
) -> Transaction:
    return repo.apply_create(session, transaction, TransactionCreateCommand.model_validate(command))


def _apply_update_when_present(
    session: Session,
    transaction: Transaction,
    command: TransactionCommandProtocol,
) -> Transaction:
    return repo.apply_update(session, transaction, TransactionUpdateCommand.model_validate(command))


def _apply_delete_when_present(
    session: Session,
    transaction: Transaction,
    command: TransactionCommandProtocol,
) -> Transaction:
    return repo.apply_delete(session, transaction, TransactionDeleteCommand.model_validate(command))


@celery_app.task(name="app.worker.tasks.transactions.handle_create_transaction")
def handle_create_transaction(*, payload: dict) -> dict[str, str]:
    return _apply_command(
        payload=payload,
        load_command=consumer.load_create,
        apply_when_missing=_create_when_missing,
        apply_when_present=_apply_create_when_present,
    )


@celery_app.task(name="app.worker.tasks.transactions.handle_update_transaction")
def handle_update_transaction(*, payload: dict) -> dict[str, str]:
    return _apply_command(
        payload=payload,
        load_command=consumer.load_update,
        apply_when_missing=_update_when_missing,
        apply_when_present=_apply_update_when_present,
    )


@celery_app.task(name="app.worker.tasks.transactions.handle_delete_transaction")
def handle_delete_transaction(*, payload: dict) -> dict[str, str]:
    return _apply_command(
        payload=payload,
        load_command=consumer.load_delete,
        apply_when_missing=_delete_when_missing,
        apply_when_present=_apply_delete_when_present,
    )
