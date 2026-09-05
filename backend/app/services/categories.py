from uuid import UUID

from sqlmodel import Session

from app.models.category import Category
from app.repos.categories import CategoryRepository


class CategoryService:
    def __init__(self, repository: CategoryRepository | None = None) -> None:
        self.repository = repository or CategoryRepository()

    def list_for_user(self, session: Session, user_id: UUID) -> list[Category]:
        return self.repository.list_for_user(session, user_id)
