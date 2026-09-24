from app.integrations.clickup import ClickUpIntegration


def test_clickup_timestamp_is_utc():
    result = ClickUpIntegration._timestamp_to_datetime("0")
    assert result.isoformat() == "1970-01-01T00:00:00+00:00"
