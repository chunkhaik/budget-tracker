from dataclasses import dataclass
from uuid import UUID

from app.core.config import get_settings


@dataclass(frozen=True)
class CurrentUser:
    id: UUID
    email: str
    display_name: str


class AuthPlaceholderError(RuntimeError):
    """Raised when auth plumbing is called without a dev fallback."""


def build_dev_current_user() -> CurrentUser:
    settings = get_settings()
    return CurrentUser(
        id=UUID(settings.dev_current_user_id),
        email=settings.dev_current_user_email,
        display_name=settings.dev_current_user_name,
    )
