from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.deps import get_db_session, require_current_user, require_workspace_member
from app.core.security import CurrentUser
from app.schemas.common import WorkspaceItemsResponse, WorkspaceRelationItemsResponse, WorkspaceRelationResponse
from app.schemas.relation import RelationCreateRequest, RelationRead, RelationUpdateRequest
from app.schemas.transaction import TransactionRead
from app.services.relations import RelationService

router = APIRouter(prefix="/workspaces/{workspace_id}/relations", tags=["relations"])
service = RelationService()


@router.get("")
def list_relations(
    workspace_id: UUID,
    current_user: CurrentUser = Depends(require_workspace_member),
    session: Session = Depends(get_db_session),
) -> WorkspaceItemsResponse:
    items = service.list_for_workspace(session, workspace_id, current_user.id)
    return WorkspaceItemsResponse(
        items=[RelationRead.model_validate(item).model_dump(mode="json", by_alias=True) for item in items],
        workspace_id=str(workspace_id),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_relation(
    workspace_id: UUID,
    payload: RelationCreateRequest,
    current_user: CurrentUser = Depends(require_workspace_member),
    session: Session = Depends(get_db_session),
) -> RelationRead:
    relation = service.create_for_workspace(session, workspace_id, current_user.id, payload)
    return RelationRead.model_validate(relation)


@router.get("/{relation_id}")
def get_relation(
    workspace_id: UUID,
    relation_id: UUID,
    current_user: CurrentUser = Depends(require_workspace_member),
    session: Session = Depends(get_db_session),
) -> RelationRead:
    relation = service.get_for_workspace(session, workspace_id, relation_id, current_user.id)
    return RelationRead.model_validate(relation)


@router.patch("/{relation_id}")
def update_relation(
    workspace_id: UUID,
    relation_id: UUID,
    payload: RelationUpdateRequest,
    current_user: CurrentUser = Depends(require_workspace_member),
    session: Session = Depends(get_db_session),
) -> RelationRead:
    relation = service.update_for_workspace(session, workspace_id, relation_id, current_user.id, payload)
    return RelationRead.model_validate(relation)


@router.get("/{relation_id}/transactions")
def list_relation_transactions(
    workspace_id: UUID,
    relation_id: UUID,
    current_user: CurrentUser = Depends(require_workspace_member),
    session: Session = Depends(get_db_session),
) -> WorkspaceRelationItemsResponse:
    items = service.list_transactions(session, workspace_id, relation_id, current_user.id)
    return WorkspaceRelationItemsResponse(
        workspace_id=str(workspace_id),
        relation_id=str(relation_id),
        items=[TransactionRead.model_validate(item).model_dump(mode="json") for item in items],
    )


@router.post("/preview")
def preview_relation(
    workspace_id: UUID,
    payload: RelationCreateRequest,
    current_user: CurrentUser = Depends(require_workspace_member),
    session: Session = Depends(get_db_session),
) -> WorkspaceRelationResponse | dict[str, object]:
    preview = service.preview(session, workspace_id, current_user.id, payload)
    return {
        "workspace_id": str(workspace_id),
        "items": [TransactionRead.model_validate(item).model_dump(mode="json") for item in preview["items"]],
        "selection_mode": preview["selection_mode"],
        "rule_definition": preview["rule_definition"],
    }
