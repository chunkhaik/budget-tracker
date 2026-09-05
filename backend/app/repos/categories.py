from uuid import UUID

from sqlmodel import Session, select

from app.models.category import Category


class CategoryRepository:
    def list_for_user(self, session: Session, user_id: UUID) -> list[Category]:
        statement = select(Category).where(Category.user_id == user_id)
        return list(session.exec(statement))
