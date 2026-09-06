from uuid import UUID

from sqlmodel import Session, select

from app.models.category import Category


class CategoryRepository:
    def list_for_user(self, session: Session, user_id: UUID) -> list[Category]:
        statement = select(Category).where(Category.user_id == user_id)
        return list(session.exec(statement))

    def get_for_user(self, session: Session, category_id: UUID, user_id: UUID) -> Category | None:
        statement = select(Category).where(Category.id == category_id, Category.user_id == user_id)
        return session.exec(statement).first()

    def create(self, session: Session, category: Category) -> Category:
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    def save(self, session: Session, category: Category) -> Category:
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    def delete(self, session: Session, category: Category) -> None:
        session.delete(category)
        session.commit()
