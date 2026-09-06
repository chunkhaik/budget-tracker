import sys
from collections.abc import Iterator
from itertools import count
from pathlib import Path
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, Table, text
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_db_session, require_current_user
from app.core.security import CurrentUser, build_dev_current_user
from app.domain.enums import CategoryType, WorkspaceRole
from app.main import app
from app.models.category import Category
from app.models.relation import WorkspaceRelation, WorkspaceRelationTransaction
from app.models.transaction import Transaction
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

TEST_TABLES: list[Table] = [
    cast(Table, getattr(User, "__table__")),
    cast(Table, getattr(Category, "__table__")),
    cast(Table, getattr(Workspace, "__table__")),
    cast(Table, getattr(WorkspaceMember, "__table__")),
    cast(Table, getattr(Transaction, "__table__")),
    cast(Table, getattr(WorkspaceRelation, "__table__")),
    cast(Table, getattr(WorkspaceRelationTransaction, "__table__")),
]


@pytest.fixture
def sqlite_engine() -> Iterator[Engine]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys=ON"))
        connection.commit()
    SQLModel.metadata.create_all(engine, tables=TEST_TABLES)
    try:
        yield engine
    finally:
        SQLModel.metadata.drop_all(engine, tables=list(reversed(TEST_TABLES)))


@pytest.fixture
def db_session(sqlite_engine: Engine) -> Iterator[Session]:
    with Session(sqlite_engine) as session:
        yield session


@pytest.fixture
def current_user() -> CurrentUser:
    return build_dev_current_user()


@pytest.fixture
def user(db_session: Session, current_user: CurrentUser) -> User:
    record = db_session.get(User, current_user.id)
    if record is not None:
        return record

    record = User(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
    )
    db_session.add(record)
    db_session.commit()
    return record


@pytest.fixture
def other_user(db_session: Session) -> User:
    record = User(
        id=UUID("00000000-0000-0000-0000-000000000002"),
        email="other-user@example.com",
        display_name="Other User",
    )
    db_session.add(record)
    db_session.commit()
    return record


@pytest.fixture
def category(db_session: Session, user: User) -> Category:
    record = Category(
        user_id=user.id,
        name="Food",
        type=CategoryType.EXPENSE,
    )
    db_session.add(record)
    db_session.commit()
    return record


@pytest.fixture
def other_user_category(db_session: Session, other_user: User) -> Category:
    record = Category(
        user_id=other_user.id,
        name="Salary",
        type=CategoryType.INCOME,
    )
    db_session.add(record)
    db_session.commit()
    return record


@pytest.fixture
def workspace(db_session: Session) -> Workspace:
    record = Workspace(
        name="Household",
        base_currency="USD",
    )
    db_session.add(record)
    db_session.commit()
    return record


@pytest.fixture
def workspace_member(db_session: Session, workspace: Workspace, user: User) -> WorkspaceMember:
    record = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user.id,
        role=WorkspaceRole.OWNER,
    )
    db_session.add(record)
    db_session.commit()
    return record


@pytest.fixture
def transaction_factory(db_session: Session, user: User, category: Category) -> Any:
    ids = count(1)

    def create_transaction(**overrides: Any) -> Transaction:
        values = {
            "id": next(ids),
            "transaction_id": uuid4(),
            "user_id": user.id,
            "category_id": category.id,
            "amount": 1200,
            "currency": "USD",
            "transaction_at": 1725580800123,
            "note": "coffee",
            "last_operation_key": f"1725580800123_{uuid4()}",
            "version": 1,
            "deleted_at": None,
            "created_at": 1725580800123,
            "updated_at": 1725580800123,
        }
        values.update(overrides)
        record = Transaction(**values)
        db_session.add(record)
        db_session.commit()
        return record

    return create_transaction


@pytest.fixture
def client(db_session: Session, current_user: CurrentUser) -> Iterator[TestClient]:
    if db_session.get(User, current_user.id) is None:
        db_session.add(
            User(
                id=current_user.id,
                email=current_user.email,
                display_name=current_user.display_name,
            )
        )
        db_session.commit()

    def override_db_session() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[require_current_user] = lambda: current_user
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
