from fastapi import APIRouter

router = APIRouter(
    prefix="/workspaces/{workspace_id}/relations/{relation_id}/analytics",
    tags=["analytics"],
)


@router.get("/spending")
def get_spending(workspace_id: str, relation_id: str) -> dict[str, object]:
    return {
        "workspace_id": workspace_id,
        "relation_id": relation_id,
        "metric": "spending",
        "items": [],
    }


@router.get("/trends")
def get_trends(workspace_id: str, relation_id: str) -> dict[str, object]:
    return {
        "workspace_id": workspace_id,
        "relation_id": relation_id,
        "metric": "trends",
        "items": [],
    }


@router.get("/breakdown")
def get_breakdown(workspace_id: str, relation_id: str) -> dict[str, object]:
    return {
        "workspace_id": workspace_id,
        "relation_id": relation_id,
        "metric": "breakdown",
        "items": [],
    }
