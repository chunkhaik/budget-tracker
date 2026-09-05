from sqlmodel import Session

from app.models.user import User
from app.repos.users import UserRepository


def test_get_returns_user_by_id(db_session: Session, user: User) -> None:
    item = UserRepository().get(db_session, user.id)

    assert item is not None
    assert item.email == user.email


def test_get_by_email_returns_matching_user(db_session: Session, user: User) -> None:
    item = UserRepository().get_by_email(db_session, user.email)

    assert item is not None
    assert item.id == user.id
