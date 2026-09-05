from uuid import UUID

from sqlalchemy import BigInteger, Index, UniqueConstraint, text
from sqlmodel import Field, SQLModel


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint("transaction_id", name="uq_transactions_transaction_id"),
        Index(
            "ix_transactions_user_transaction_at_active",
            "user_id",
            "transaction_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_transactions_user_category_transaction_at_active",
            "user_id",
            "category_id",
            "transaction_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_transactions_currency_transaction_at_active",
            "currency",
            "transaction_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: int | None = Field(default=None, primary_key=True, sa_type=BigInteger)
    transaction_id: UUID = Field(nullable=False, unique=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    category_id: UUID | None = Field(default=None, foreign_key="categories.id")
    amount: int = Field(nullable=False, sa_type=BigInteger)
    currency: str = Field(nullable=False, min_length=3, max_length=3)
    transaction_at: int = Field(nullable=False, sa_type=BigInteger)
    note: str | None = Field(default=None, max_length=2000)
    last_operation_key: str = Field(nullable=False, max_length=128)
    version: int = Field(default=1, nullable=False, sa_type=BigInteger)
    deleted_at: int | None = Field(default=None, sa_type=BigInteger)
    created_at: int = Field(nullable=False, sa_type=BigInteger)
    updated_at: int = Field(nullable=False, sa_type=BigInteger)
