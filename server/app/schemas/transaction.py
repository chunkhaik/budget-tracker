from uuid import UUID

from pydantic import Field

from app.schemas.common import APIModel


class TransactionBase(APIModel):
    category_id: UUID | None = None
    amount: int
    currency: str = Field(min_length=3, max_length=3)
    transaction_at: int
    note: str | None = None


class TransactionCreateRequest(TransactionBase):
    pass


class TransactionUpdateRequest(APIModel):
    category_id: UUID | None = None
    amount: int | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    transaction_at: int | None = None
    note: str | None = None


class TransactionRead(TransactionBase):
    transaction_id: UUID
    version: int
    deleted_at: int | None = None
