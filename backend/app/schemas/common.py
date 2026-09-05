from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ResourceRef(APIModel):
    id: UUID


class QueuedCommandResponse(APIModel):
    status: str
    task_id: str
    transaction_id: str


class TodoResponse(APIModel):
    status: str


class UserItemsResponse(APIModel):
    items: list[Any]
    user_id: str


class WorkspaceItemsResponse(APIModel):
    items: list[Any]
    workspace_id: str


class WorkspaceTodoResponse(TodoResponse):
    workspace_id: str


class WorkspaceRelationResponse(APIModel):
    workspace_id: str
    relation_id: str


class WorkspaceRelationItemsResponse(APIModel):
    workspace_id: str
    relation_id: str
    items: list[Any]


class AnalyticsItemsResponse(APIModel):
    workspace_id: str
    relation_id: str
    metric: str
    items: list[Any]
