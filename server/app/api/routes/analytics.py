from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import get_db_session, require_workspace_member
from app.core.security import CurrentUser
from app.schemas.analytics import AnalyticsQuery
from app.schemas.common import AnalyticsItemsResponse
from app.services.analytics import AnalyticsQueryError, AnalyticsService
from app.services.relations import RelationService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/relations/{relation_id}/analytics",
    tags=["analytics"],
)
analytics_service = AnalyticsService()
relation_service = RelationService()


def build_query(
    group_by: str | None = Query(default=None),
    currency: str | None = Query(default=None),
    from_ts: int | None = Query(default=None),
    to_ts: int | None = Query(default=None),
) -> AnalyticsQuery:
    return AnalyticsQuery(group_by=group_by, currency=currency, from_ts=from_ts, to_ts=to_ts)


@router.get("/spending")
def get_spending(
    workspace_id: UUID,
    relation_id: UUID,
    query: AnalyticsQuery = Depends(build_query),
    current_user: CurrentUser = Depends(require_workspace_member),
    session: Session = Depends(get_db_session),
) -> AnalyticsItemsResponse:
    try:
        items = analytics_service.spending(session, relation_service, workspace_id, relation_id, current_user.id, query)
    except AnalyticsQueryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AnalyticsItemsResponse(
        workspace_id=str(workspace_id),
        relation_id=str(relation_id),
        metric="spending",
        items=[item.model_dump(mode="json") for item in items],
    )


@router.get("/trends")
def get_trends(
    workspace_id: UUID,
    relation_id: UUID,
    query: AnalyticsQuery = Depends(build_query),
    current_user: CurrentUser = Depends(require_workspace_member),
    session: Session = Depends(get_db_session),
) -> AnalyticsItemsResponse:
    try:
        items = analytics_service.trends(session, relation_service, workspace_id, relation_id, current_user.id, query)
    except AnalyticsQueryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AnalyticsItemsResponse(
        workspace_id=str(workspace_id),
        relation_id=str(relation_id),
        metric="trends",
        items=[item.model_dump(mode="json") for item in items],
    )


@router.get("/breakdown")
def get_breakdown(
    workspace_id: UUID,
    relation_id: UUID,
    query: AnalyticsQuery = Depends(build_query),
    current_user: CurrentUser = Depends(require_workspace_member),
    session: Session = Depends(get_db_session),
) -> AnalyticsItemsResponse:
    try:
        items = analytics_service.breakdown(session, relation_service, workspace_id, relation_id, current_user.id, query)
    except AnalyticsQueryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AnalyticsItemsResponse(
        workspace_id=str(workspace_id),
        relation_id=str(relation_id),
        metric="breakdown",
        items=[item.model_dump(mode="json") for item in items],
    )
