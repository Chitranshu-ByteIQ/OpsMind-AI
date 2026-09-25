from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.data.store import load_source


def gmail_messages() -> list[dict[str, Any]]:
    return load_source("gmail", "messages.json")


def latest_email() -> dict[str, Any] | None:
    return max(gmail_messages(), key=lambda item: item.get("received_at") or "", default=None)


def find_email(message_id: str) -> dict[str, Any] | None:
    return next((item for item in gmail_messages() if item.get("id") == message_id), None)


def clickup_tasks() -> list[dict[str, Any]]:
    return load_source("clickup", "tasks.json")


def overdue_tasks() -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc)
    result = []
    for task in clickup_tasks():
        try:
            due = datetime.fromisoformat(str(task.get("due_date")).replace("Z", "+00:00"))
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            if due < now and "complete" not in str(task.get("status", "")).lower():
                result.append(task)
        except (ValueError, TypeError):
            continue
    return result


def simple_local_answer(request: str) -> str | None:
    lowered = request.lower()
    if "last email" in lowered or "latest email" in lowered:
        email = latest_email()
        if not email:
            return "No persisted Gmail messages are available yet. Use Refresh Data to retrieve them."
        return f"Using local persisted Gmail data, your latest email is from {email.get('sender') or 'an unknown sender'}: {email.get('subject') or '(no subject)'} ({email.get('received_at') or 'time unavailable'})."
    if "overdue" in lowered and "clickup" in lowered:
        tasks = overdue_tasks()
        if not tasks:
            return "Using local persisted ClickUp data, you have no overdue tasks (or no task snapshot is available)."
        return "Using local persisted ClickUp data, your overdue tasks are: " + "; ".join(task.get("name", "Untitled task") for task in tasks[:10])
    return None
