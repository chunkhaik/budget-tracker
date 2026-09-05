from app.core.security import CurrentUser, build_dev_current_user


class AuthService:
    """Placeholder auth adapter until Supabase auth is wired."""

    def get_current_user(self) -> CurrentUser:
        return build_dev_current_user()
