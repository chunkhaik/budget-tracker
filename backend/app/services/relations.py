from uuid import UUID

from sqlmodel import Session

from app.models.relation import WorkspaceRelation
from app.repos.relations import RelationRepository
from app.services.relation_builder import RelationBuilder


class RelationService:
    def __init__(
        self,
        repository: RelationRepository | None = None,
        relation_builder: RelationBuilder | None = None,
    ) -> None:
        self.repository = repository or RelationRepository()
        self.relation_builder = relation_builder or RelationBuilder()

    def list_for_workspace(self, session: Session, workspace_id: UUID) -> list[WorkspaceRelation]:
        return self.repository.list_for_workspace(session, workspace_id)
