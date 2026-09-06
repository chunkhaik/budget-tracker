from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.deps import get_db_session, require_current_user
from app.core.security import CurrentUser
from app.schemas.category import (
    CategoryCreateRequest,
    CategoryDeleteResponse,
    CategoryRead,
    CategoryUpdateRequest,
)
from app.schemas.common import UserItemsResponse
from app.services.categories import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])
service = CategoryService()


@router.get("")
def list_categories(
    current_user: CurrentUser = Depends(require_current_user),
    session: Session = Depends(get_db_session),
) -> UserItemsResponse:
    items = service.list_for_user(session, current_user.id)
    return UserItemsResponse(
        items=[CategoryRead.model_validate(item).model_dump(mode="json") for item in items],
        user_id=str(current_user.id),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreateRequest,
    current_user: CurrentUser = Depends(require_current_user),
    session: Session = Depends(get_db_session),
) -> CategoryRead:
    category = service.create_for_user(session, current_user.id, payload)
    return CategoryRead.model_validate(category)


@router.patch("/{category_id}")
def update_category(
    category_id: UUID,
    payload: CategoryUpdateRequest,
    current_user: CurrentUser = Depends(require_current_user),
    session: Session = Depends(get_db_session),
) -> CategoryRead:
    category = service.update_for_user(session, category_id, current_user.id, payload)
    return CategoryRead.model_validate(category)


@router.delete("/{category_id}")
def delete_category(
    category_id: UUID,
    current_user: CurrentUser = Depends(require_current_user),
    session: Session = Depends(get_db_session),
) -> CategoryDeleteResponse:
    service.delete_for_user(session, category_id, current_user.id)
    return CategoryDeleteResponse(id=category_id, status="deleted")
