from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_db_session, require_current_user
from app.core.security import CurrentUser
from app.schemas.category import CategoryCreateRequest
from app.services.categories import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("")
def list_categories(
    current_user: CurrentUser = Depends(require_current_user),
    session: Session = Depends(get_db_session),
) -> dict[str, object]:
    items = CategoryService().list_for_user(session, current_user.id)
    return {
        "items": items,
        "user_id": str(current_user.id),
    }


@router.post("")
def create_category(
    payload: CategoryCreateRequest,
    current_user: CurrentUser = Depends(require_current_user),
) -> dict[str, str]:
    return {
        "status": "todo",
        "name": payload.name,
        "user_id": str(current_user.id),
    }


@router.patch("/{category_id}")
def update_category(category_id: UUID) -> dict[str, str]:
    return {
        "status": "todo",
        "category_id": str(category_id),
    }


@router.delete("/{category_id}")
def delete_category(category_id: UUID) -> dict[str, str]:
    return {
        "status": "todo",
        "category_id": str(category_id),
    }
