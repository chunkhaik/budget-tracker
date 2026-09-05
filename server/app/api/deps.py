from collections.abc import Generator

from fastapi import Depends
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import CurrentUser, build_dev_current_user
from app.services.auth import AuthService


SessionDep = Depends(get_session)


def get_db_session() -> Generator[Session, None, None]:
    yield from get_session()


def get_auth_service() -> AuthService:
    return AuthService()


def get_current_user(auth_service: AuthService = Depends(get_auth_service)) -> CurrentUser:
    return auth_service.get_current_user()


def require_current_user(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return current_user


def get_dev_user() -> CurrentUser:
    return build_dev_current_user()
