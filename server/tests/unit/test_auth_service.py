from app.services.auth import AuthService


def test_get_current_user_returns_dev_current_user() -> None:
    current_user = AuthService().get_current_user()

    assert str(current_user.id) == "00000000-0000-0000-0000-000000000001"
    assert current_user.email == "dev-user@example.com"
    assert current_user.display_name == "Dev User"
