from typing import Any, cast
from uuid import UUID, uuid4

from sqlmodel import Session

from app.repos.workspaces import WorkspaceRepository
from app.services.workspaces import WorkspaceService


class StubWorkspaceRepository(WorkspaceRepository):
    def __init__(self, items: list[Any]) -> None:
        self.items = items
        self.calls: list[tuple[Session, UUID]] = []

    def list_for_user(self, session: Session, user_id: UUID) -> list[Any]:
        self.calls.append((session, user_id))
        return self.items


def test_list_for_user_delegates_to_repository() -> None:
    session = cast(Session, object())
    user_id = uuid4()
    items = [object()]
    repository = StubWorkspaceRepository(items)

    result = WorkspaceService(repository=repository).list_for_user(session, user_id)

    assert result == items
    assert repository.calls == [(session, user_id)]
