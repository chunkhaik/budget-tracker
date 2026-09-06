from uuid import uuid4

from sqlmodel import Session

from app.domain.enums import CategoryType
from app.models.category import Category
from app.models.user import User
from app.repos.categories import CategoryRepository


def test_list_for_user_returns_only_categories_for_requested_user(
    db_session: Session,
    category: Category,
    other_user: User,
) -> None:
    other_category = Category(
        user_id=other_user.id,
        name="Salary",
        type=CategoryType.INCOME,
    )
    db_session.add(other_category)
    db_session.commit()

    items = CategoryRepository().list_for_user(
        db_session,
        category.user_id,
    )

    assert [item.name for item in items] == ["Food"]


def test_get_for_user_returns_matching_owned_category(db_session: Session, category: Category) -> None:
    item = CategoryRepository().get_for_user(db_session, category.id, category.user_id)

    assert item is not None
    assert item.id == category.id


def test_get_for_user_returns_none_for_other_owner(
    db_session: Session,
    category: Category,
    other_user: User,
) -> None:
    item = CategoryRepository().get_for_user(db_session, category.id, other_user.id)

    assert item is None


def test_create_persists_category(db_session: Session, user: User) -> None:
    category = Category(user_id=user.id, name="Rent", type=CategoryType.EXPENSE)

    created = CategoryRepository().create(db_session, category)

    assert created.id is not None
    assert db_session.get(Category, created.id) is not None


def test_save_persists_category_changes(db_session: Session, category: Category) -> None:
    category.name = "Dining"

    saved = CategoryRepository().save(db_session, category)

    assert saved.name == "Dining"
    db_session.refresh(category)
    assert category.name == "Dining"


def test_delete_removes_category(db_session: Session, category: Category) -> None:
    CategoryRepository().delete(db_session, category)

    assert db_session.get(Category, category.id) is None
