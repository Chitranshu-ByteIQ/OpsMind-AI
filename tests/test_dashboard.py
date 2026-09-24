from datetime import datetime, timedelta, timezone

from app.analytics.aggregator import UnifiedWorkData
from app.analytics.metrics import build_attention, build_summary


def test_dashboard_metrics_and_attention_are_deterministic():
    data = UnifiedWorkData(
        tasks=[{"name": "Late task", "due_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(), "priority": "high", "url": None}],
        pull_requests=[{"title": "Review me", "url": "https://example.test/pr"}],
        messages=[{"subject": "Unread", "is_read": False}],
        availability={"github": True, "clickup": True, "gmail": True, "research": True},
    )
    summary = build_summary(data)
    assert summary["overdue_tasks"] == {"value": 1, "available": True}
    assert summary["high_priority_tasks"] == {"value": 1, "available": True}
    assert len(build_attention(data)) == 3


def test_unavailable_source_never_invents_metric():
    data = UnifiedWorkData(tasks=[{"name": "Task"}], availability={"github": False, "clickup": False, "gmail": False, "research": True})
    assert build_summary(data)["open_tasks"] == {"value": None, "available": False}
