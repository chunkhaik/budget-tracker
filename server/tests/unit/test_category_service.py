from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.domain.enums import CategoryType
from app.models.category import Category
from app.repos.categories import CategoryRepository
from app.schemas.category import CategoryCreateRequest, CategoryUpdateRequest
from app.services.categories import CategoryService


class StubCategoryRepository(CategoryRepository):
    def __init__(self, items: list[Any]) -> None:
        self.items = items
        self.list_calls: list[tuple[Session, UUID]] = []
        self.get_calls: list[tuple[Session, UUID, UUID]] = []
        self.created: list[Category] = []
        self.saved: list[Category] = []
        self.deleted: list[Category] = []
        self.by_id: dict[tuple[UUID, UUID], Category] = {}

    def list_for_user(self, session: Session, user_id: UUID) -> list[Any]:
        self.list_calls.append((session, user_id))
        return self.items

    def get_for_user(self, session: Session, category_id: UUID, user_id: UUID) -> Category | None:
        self.get_calls.append((session, category_id, user_id))
        return self.by_id.get((category_id, user_id))

    def create(self, _session: Session, category: Category) -> Category:
        self.created.append(category)
        return category

    def save(self, _session: Session, category: Category) -> Category:
        self.saved.append(category)
        return category

    def delete(self, _session: Session, category: Category) -> None:
        self.deleted.append(category)


def test_list_for_user_delegates_to_repository() -> None:
    session = cast(Session, object())
    user_id = uuid4()
    items = [object()]
    repository = StubCategoryRepository(items)

    result = CategoryService(repository=repository).list_for_user(session, user_id)

    assert result == items
    assert repository.list_calls == [(session, user_id)]


def test_create_for_user_builds_category_and_delegates() -> None:
    session = cast(Session, object())
    user_id = uuid4()
    repository = StubCategoryRepository([])

    category = CategoryService(repository=repository).create_for_user(
        session,
        user_id,
        CategoryCreateRequest(name="Rent", type=CategoryType.EXPENSE),
    )

    assert category.user_id == user_id
    assert category.name == "Rent"
    assert category.type == CategoryType.EXPENSE
    assert repository.created == [category]


def test_update_for_user_updates_only_present_fields() -> None:
    session = cast(Session, object())
    user_id = uuid4()
    category_id = uuid4()
    category = Category(user_id=user_id, name="Food", type=CategoryType.EXPENSE)
    category.id = category_id
    repository = StubCategoryRepository([])
    repository.by_id[(category_id, user_id)] = category

    updated = CategoryService(repository=repository).update_for_user(
        session,
        category_id,
        user_id,
        CategoryUpdateRequest(name="Dining"),
    )

    assert updated is category
    assert category.name == "Dining"
    assert category.type == CategoryType.EXPENSE
    assert repository.saved == [category]


def test_delete_for_user_delegates_after_lookup() -> None:
    session = cast(Session, object())
    user_id = uuid4()
    category_id = uuid4()
    category = Category(user_id=user_id, name="Food", type=CategoryType.EXPENSE)
    category.id = category_id
    repository = StubCategoryRepository([])
    repository.by_id[(category_id, user_id)] = category

    CategoryService(repository=repository).delete_for_user(session, category_id, user_id)

    assert repository.deleted == [category]


def test_require_for_user_raises_not_found_for_missing_category() -> None:
    session = cast(Session, object())
    repository = StubCategoryRepository([])

    with pytest.raises(HTTPException, match="category not found"):
        CategoryService(repository=repository).require_for_user(session, uuid4(), uuid4())
