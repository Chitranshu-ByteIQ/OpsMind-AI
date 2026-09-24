from fastapi.testclient import TestClient

from app.main import app


def test_system_routes():
    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert client.get("/health").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_dashboard_routes_with_mocked_data(monkeypatch):
    from app.analytics.aggregator import UnifiedWorkData
    import app.routes.dashboard as dashboard

    monkeypatch.setattr(dashboard, "_data", lambda: UnifiedWorkData(availability={"github": False, "clickup": False, "gmail": False, "research": True}))
    response = TestClient(app).get("/api/dashboard/summary")
    assert response.status_code == 200
    assert response.json()["metrics"]["open_tasks"]["available"] is False
