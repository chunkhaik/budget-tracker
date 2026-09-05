from uuid import UUID

from sqlmodel import Session, select

from app.models.user import User


class UserRepository:
    def get(self, session: Session, user_id: UUID) -> User | None:
        return session.get(User, user_id)

    def get_by_email(self, session: Session, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()
