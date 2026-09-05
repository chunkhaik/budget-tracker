from fastapi import APIRouter

router = APIRouter(prefix="/workspaces/{workspace_id}/relations", tags=["relations"])


@router.get("")
def list_relations(workspace_id: str) -> dict[str, object]:
    return {
        "items": [],
        "workspace_id": workspace_id,
    }


@router.post("")
def create_relation(workspace_id: str) -> dict[str, str]:
    return {
        "workspace_id": workspace_id,
        "status": "todo",
    }


@router.get("/{relation_id}")
def get_relation(workspace_id: str, relation_id: str) -> dict[str, str]:
    return {
        "workspace_id": workspace_id,
        "relation_id": relation_id,
    }


@router.patch("/{relation_id}")
def update_relation(workspace_id: str, relation_id: str) -> dict[str, str]:
    return {
        "workspace_id": workspace_id,
        "relation_id": relation_id,
        "status": "todo",
    }


@router.get("/{relation_id}/transactions")
def list_relation_transactions(workspace_id: str, relation_id: str) -> dict[str, object]:
    return {
        "workspace_id": workspace_id,
        "relation_id": relation_id,
        "items": [],
    }


@router.post("/preview")
def preview_relation(workspace_id: str) -> dict[str, object]:
    return {
        "workspace_id": workspace_id,
        "items": [],
        "status": "todo",
    }
