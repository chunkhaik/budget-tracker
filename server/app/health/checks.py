from app.core.config import get_settings


settings = get_settings()


def build_health_payload(*, status: str) -> dict[str, str]:
    return {
        "status": status,
        "app": settings.app_name,
        "env": settings.app_env,
    }
