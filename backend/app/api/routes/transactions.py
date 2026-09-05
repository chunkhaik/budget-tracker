from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_db_session, require_current_user
from app.core.security import CurrentUser
from app.repos.transactions import TransactionRepository
from app.schemas.transaction import TransactionCreateRequest, TransactionRead, TransactionUpdateRequest
from app.services.transactions import TransactionCommandService

router = APIRouter(prefix="/transactions", tags=["transactions"])
repo = TransactionRepository()


@router.get("")
def list_transactions(
    current_user: CurrentUser = Depends(require_current_user),
    session: Session = Depends(get_db_session),
) -> dict[str, object]:
    items = repo.list_for_user(session, current_user.id)
    return {
        "items": [TransactionRead.model_validate(item) for item in items],
        "user_id": str(current_user.id),
    }


@router.post("", status_code=status.HTTP_202_ACCEPTED)
def create_transaction(
    payload: TransactionCreateRequest,
    current_user: CurrentUser = Depends(require_current_user),
) -> dict[str, str]:
    transaction_id, task_id = TransactionCommandService().queue_create(current_user=current_user, payload=payload)
    return {
        "status": "queued",
        "task_id": task_id,
        "transaction_id": transaction_id,
    }


@router.get("/{transaction_id}")
def get_transaction(
    transaction_id: UUID,
    current_user: CurrentUser = Depends(require_current_user),
    session: Session = Depends(get_db_session),
) -> TransactionRead:
    transaction = repo.get_by_public_id(session, transaction_id)
    if transaction is None or transaction.user_id != current_user.id or transaction.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="transaction not found")
    return TransactionRead.model_validate(transaction)


@router.patch("/{transaction_id}", status_code=status.HTTP_202_ACCEPTED)
def update_transaction(
    transaction_id: UUID,
    payload: TransactionUpdateRequest,
    current_user: CurrentUser = Depends(require_current_user),
) -> dict[str, str]:
    task_id = TransactionCommandService().queue_update(
        current_user=current_user,
        transaction_id=str(transaction_id),
        payload=payload,
    )
    return {
        "status": "queued",
        "task_id": task_id,
        "transaction_id": str(transaction_id),
    }


@router.delete("/{transaction_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_transaction(
    transaction_id: UUID,
    current_user: CurrentUser = Depends(require_current_user),
) -> dict[str, str]:
    task_id = TransactionCommandService().queue_delete(
        current_user=current_user,
        transaction_id=str(transaction_id),
    )
    return {
        "status": "queued",
        "task_id": task_id,
        "transaction_id": str(transaction_id),
    }
