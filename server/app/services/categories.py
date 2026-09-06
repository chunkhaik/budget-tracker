from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.category import Category
from app.repos.categories import CategoryRepository
from app.schemas.category import CategoryCreateRequest, CategoryUpdateRequest


class CategoryService:
    def __init__(self, repository: CategoryRepository | None = None) -> None:
        self.repository = repository or CategoryRepository()

    def list_for_user(self, session: Session, user_id: UUID) -> list[Category]:
        return self.repository.list_for_user(session, user_id)

    def create_for_user(self, session: Session, user_id: UUID, payload: CategoryCreateRequest) -> Category:
        category = Category(
            user_id=user_id,
            name=payload.name,
            type=payload.type,
        )
        return self.repository.create(session, category)

    def update_for_user(
        self,
        session: Session,
        category_id: UUID,
        user_id: UUID,
        payload: CategoryUpdateRequest,
    ) -> Category:
        category = self.require_for_user(session, category_id, user_id)
        if payload.name is not None:
            category.name = payload.name
        if payload.type is not None:
            category.type = payload.type
        category.updated_at = datetime.now(timezone.utc)
        return self.repository.save(session, category)

    def delete_for_user(self, session: Session, category_id: UUID, user_id: UUID) -> None:
        category = self.require_for_user(session, category_id, user_id)
        self.repository.delete(session, category)

    def require_for_user(self, session: Session, category_id: UUID, user_id: UUID) -> Category:
        category = self.repository.get_for_user(session, category_id, user_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="category not found")
        return category
