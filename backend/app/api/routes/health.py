from fastapi import APIRouter

from app.health.checks import build_health_payload

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return build_health_payload(status="ok")


@router.get("/readyz")
def readyz() -> dict[str, str]:
    return build_health_payload(status="ready")
