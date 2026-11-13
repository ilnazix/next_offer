from app import health


def test_health_reports_ok_when_dependencies_are_reachable(client, monkeypatch):
    monkeypatch.setattr(health, "check_database", lambda: True)
    monkeypatch.setattr(health, "check_rabbitmq", lambda: True)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "checks": {"database": "ok", "rabbitmq": "ok"},
    }


def test_health_reports_degraded_when_database_is_unreachable(client, monkeypatch):
    monkeypatch.setattr(health, "check_database", lambda: False)
    monkeypatch.setattr(health, "check_rabbitmq", lambda: True)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "checks": {"database": "error", "rabbitmq": "ok"},
    }


def test_health_reports_degraded_when_broker_is_unreachable(client, monkeypatch):
    monkeypatch.setattr(health, "check_database", lambda: True)
    monkeypatch.setattr(health, "check_rabbitmq", lambda: False)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "checks": {"database": "ok", "rabbitmq": "error"},
    }
