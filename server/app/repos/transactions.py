import time
from typing import Any, cast
from uuid import UUID

from sqlalchemy import desc
from sqlmodel import Session, select

from app.models.transaction import Transaction
from app.schemas.commands import (
    TransactionCreateCommand,
    TransactionDeleteCommand,
    TransactionUpdateCommand,
)


class TransactionRepository:
    def current_timestamp_ms(self) -> int:
        return int(time.time() * 1000)

    def list_for_user(self, session: Session, user_id: UUID) -> list[Transaction]:
        transaction_model = cast(Any, Transaction)
        statement = (
            select(Transaction)
            .where(transaction_model.user_id == user_id)
            .where(transaction_model.deleted_at.is_(None))
            .order_by(desc(transaction_model.transaction_at))
        )
        return list(session.exec(statement))

    def get_by_public_id(self, session: Session, transaction_id: UUID) -> Transaction | None:
        transaction_model = cast(Any, Transaction)
        statement = select(Transaction).where(transaction_model.transaction_id == transaction_id)
        return session.exec(statement).first()

    def create_from_command(
        self,
        session: Session,
        command: TransactionCreateCommand,
    ) -> Transaction:
        now_ms = self.current_timestamp_ms()
        transaction = Transaction(
            transaction_id=command.transaction_id,
            user_id=command.user_id,
            category_id=command.category_id,
            amount=command.amount,
            currency=command.currency,
            transaction_at=command.transaction_at,
            note=command.note,
            last_operation_key=command.operation_key,
            version=1,
            deleted_at=None,
            created_at=now_ms,
            updated_at=now_ms,
        )
        session.add(transaction)
        session.flush()
        return transaction

    def apply_create(
        self,
        session: Session,
        transaction: Transaction,
        command: TransactionCreateCommand,
    ) -> Transaction:
        self._apply_full_state(
            transaction,
            category_id=command.category_id,
            amount=command.amount,
            currency=command.currency,
            transaction_at=command.transaction_at,
            note=command.note,
        )
        transaction.user_id = command.user_id
        transaction.last_operation_key = command.operation_key
        transaction.deleted_at = None
        transaction.version += 1
        transaction.updated_at = self.current_timestamp_ms()
        session.add(transaction)
        session.flush()
        return transaction

    def apply_update(
        self,
        session: Session,
        transaction: Transaction,
        command: TransactionUpdateCommand,
    ) -> Transaction:
        if command.category_id is not None:
            transaction.category_id = command.category_id
        if command.amount is not None:
            transaction.amount = command.amount
        if command.currency is not None:
            transaction.currency = command.currency
        if command.transaction_at is not None:
            transaction.transaction_at = command.transaction_at
        if command.note is not None:
            transaction.note = command.note
        transaction.last_operation_key = command.operation_key
        transaction.version += 1
        transaction.updated_at = self.current_timestamp_ms()
        session.add(transaction)
        session.flush()
        return transaction

    def create_delete_tombstone(
        self,
        session: Session,
        command: TransactionDeleteCommand,
    ) -> Transaction:
        now_ms = self.current_timestamp_ms()
        transaction = Transaction(
            transaction_id=command.transaction_id,
            user_id=command.user_id,
            category_id=command.category_id,
            amount=command.amount,
            currency=command.currency,
            transaction_at=command.transaction_at,
            note=command.note,
            last_operation_key=command.operation_key,
            version=1,
            deleted_at=now_ms,
            created_at=now_ms,
            updated_at=now_ms,
        )
        session.add(transaction)
        session.flush()
        return transaction

    def apply_delete(
        self,
        session: Session,
        transaction: Transaction,
        command: TransactionDeleteCommand,
    ) -> Transaction:
        now_ms = self.current_timestamp_ms()
        transaction.last_operation_key = command.operation_key
        transaction.version += 1
        transaction.deleted_at = now_ms
        transaction.updated_at = now_ms
        session.add(transaction)
        session.flush()
        return transaction

    def _apply_full_state(
        self,
        transaction: Transaction,
        *,
        category_id: UUID | None,
        amount: int,
        currency: str,
        transaction_at: int,
        note: str | None,
    ) -> None:
        transaction.category_id = category_id
        transaction.amount = amount
        transaction.currency = currency
        transaction.transaction_at = transaction_at
        transaction.note = note
