from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.analytics.aggregator import UnifiedWorkData


def metric(value: int | None, available: bool) -> dict[str, Any]:
    return {"value": value if available else None, "available": available}


def build_summary(data: UnifiedWorkData) -> dict[str, dict[str, Any]]:
    return {
        "open_issues": metric(len(data.issues), data.availability["github"]),
        "open_pull_requests": metric(len(data.pull_requests), data.availability["github"]),
        "open_tasks": metric(len(data.tasks), data.availability["clickup"]),
        "overdue_tasks": metric(sum(_is_overdue(task) for task in data.tasks), data.availability["clickup"]),
        "high_priority_tasks": metric(sum(_is_high_priority(task) for task in data.tasks), data.availability["clickup"]),
        "unread_email": metric(sum(not message.get("is_read", True) for message in data.messages), data.availability["gmail"]),
        "attention_items": metric(len(build_attention(data)), any(data.availability.values())),
    }


def build_attention(data: UnifiedWorkData) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for task in data.tasks:
        if _is_overdue(task):
            items.append({"source": "clickup", "kind": "overdue_task", "title": task["name"], "url": task.get("url"), "severity": "high"})
        elif _is_high_priority(task):
            items.append({"source": "clickup", "kind": "high_priority_task", "title": task["name"], "url": task.get("url"), "severity": "medium"})
    for pull_request in data.pull_requests:
        items.append({"source": "github", "kind": "open_pull_request", "title": pull_request["title"], "url": pull_request.get("url"), "severity": "medium"})
    for message in data.messages:
        if not message.get("is_read", True):
            items.append({"source": "gmail", "kind": "unread_email", "title": message.get("subject") or "(no subject)", "url": None, "severity": "low"})
    return items


def build_activity(data: UnifiedWorkData) -> list[dict[str, Any]]:
    activity = []
    for item in [*data.issues, *data.pull_requests, *data.tasks]:
        activity.append({"source": "github" if "repository" in item else "clickup", "title": item.get("title") or item.get("name"), "updated_at": item.get("updated_at") or item.get("date_updated")})
    return sorted(activity, key=lambda item: item["updated_at"] or "", reverse=True)[:25]


def _is_high_priority(task: dict[str, Any]) -> bool:
    return str(task.get("priority") or "").lower() in {"urgent", "high"}


def _is_overdue(task: dict[str, Any]) -> bool:
    due = task.get("due_date")
    if not due:
        return False
    try:
        parsed = datetime.fromisoformat(str(due).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed < datetime.now(timezone.utc)
    except ValueError:
        return False
