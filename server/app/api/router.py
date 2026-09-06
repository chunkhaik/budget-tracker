from fastapi import APIRouter

from app.api.routes import analytics, categories, health, relations, transactions, workspaces
from app.core.config import get_settings

settings = get_settings()

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(transactions.router, prefix=settings.api_v1_prefix)
api_router.include_router(categories.router, prefix=settings.api_v1_prefix)
api_router.include_router(workspaces.router, prefix=settings.api_v1_prefix)
api_router.include_router(relations.router, prefix=settings.api_v1_prefix)
api_router.include_router(analytics.router, prefix=settings.api_v1_prefix)
