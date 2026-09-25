from app.integrations.clickup import ClickUpIntegration


def test_clickup_timestamp_is_utc():
    result = ClickUpIntegration._timestamp_to_datetime("0")
    assert result.isoformat() == "1970-01-01T00:00:00+00:00"


def test_clickup_filtered_team_tasks_are_assignee_scoped(monkeypatch):
    client = ClickUpIntegration()
    calls = []

    def fake_get(endpoint, *, params=None):
        calls.append((endpoint, params))
        return {
            "tasks": [
                {
                    "id": "task-1",
                    "name": "Assigned task",
                    "status": {"status": "to do"},
                    "assignees": [{"id": 123, "username": "User One"}],
                    "tags": [],
                }
            ]
        }

    monkeypatch.setattr(client, "_get", fake_get)

    tasks = client.get_filtered_team_tasks("team-1", assignee_ids=["123"])

    assert tasks[0].id == "task-1"
    endpoint, params = calls[0]
    assert endpoint == "/team/team-1/task"
    assert ("assignees[]", "123") in params
    assert ("page", 0) in params


def test_clickup_list_tasks_include_pagination_and_multilist(monkeypatch):
    client = ClickUpIntegration()
    calls = []

    def fake_get(endpoint, *, params=None):
        calls.append((endpoint, params))
        return {"tasks": []}

    monkeypatch.setattr(client, "_get", fake_get)

    assert client.get_tasks("list-1", assignee_ids=["123"]) == []
    endpoint, params = calls[0]
    assert endpoint == "/list/list-1/task"
    assert ("assignees[]", "123") in params
    assert ("include_timl", "true") in params
    assert ("page", 0) in params
