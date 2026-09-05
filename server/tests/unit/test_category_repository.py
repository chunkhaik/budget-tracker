from sqlmodel import Session

from app.models.category import Category
from app.models.user import User
from app.repos.categories import CategoryRepository


def test_list_for_user_returns_only_categories_for_requested_user(
    db_session: Session,
    category: Category,
    other_user: User,
) -> None:
    _ = other_user

    items = CategoryRepository().list_for_user(
        db_session,
        category.user_id,
    )

    assert [item.name for item in items] == ["Food"]
