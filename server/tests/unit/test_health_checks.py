from app.health.checks import build_health_payload


def test_build_health_payload_uses_settings_metadata() -> None:
    payload = build_health_payload(status="ok")

    assert payload == {
        "status": "ok",
        "app": "budget-tracker",
        "env": "development",
    }
