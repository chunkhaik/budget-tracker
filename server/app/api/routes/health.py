from fastapi import APIRouter

from app.health.checks import build_health_payload

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return build_health_payload(status="ok")


@router.get("/ping")
def ready() -> dict[str, str]:
    return build_health_payload(status="pong")
