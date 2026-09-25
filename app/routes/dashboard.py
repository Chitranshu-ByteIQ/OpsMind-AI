from __future__ import annotations

from collections import Counter
from email.utils import parseaddr
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.analytics.aggregator import collect_dashboard_data
from app.analytics.insights import build_insights
from app.analytics.metrics import build_activity, build_attention, build_summary
from app.data.store import source_metadata, sync_state
from app.services.approvals import decide, pending_actions, propose_clickup_task
from app.services.sync import refresh_all

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _data():
    return collect_dashboard_data()


@router.get("/summary")
def summary():
    data = _data()
    return {
        "metrics": build_summary(data),
        "connections": data.availability,
        "sync": sync_state(),
        "sources": {name: source_metadata(name) for name in ("gmail", "github", "clickup")},
    }


@router.get("/details")
def details():
    data = _data()
    sources = {name: source_metadata(name) for name in ("gmail", "github", "clickup")}
    return {
        "profile": _person_profile(sources, data.messages),
        "clickup": {
            "tasks": data.tasks,
            "status_distribution": _count_rows(data.tasks, "status"),
            "priority_distribution": _count_rows(data.tasks, "priority", default="none"),
            "tag_distribution": _tag_rows(data.tasks),
            "assignee_distribution": _list_count_rows(data.tasks, "assignees"),
            "total_tasks": len(data.tasks),
        },
        "gmail": {
            "messages": _message_rows(data.messages),
            "sender_distribution": _sender_rows(data.messages),
            "label_distribution": _list_count_rows(data.messages, "labels"),
            "unread_count": sum(not message.get("is_read", True) for message in data.messages),
            "total_messages": len(data.messages),
        },
        "github": {
            "repositories": data.repositories,
            "issues": data.issues,
            "pull_requests": data.pull_requests,
            "repository_count": len(data.repositories),
            "issue_count": len(data.issues),
            "pull_request_count": len(data.pull_requests),
        },
    }


@router.post("/refresh")
def refresh():
    """Explicitly retrieve and persist snapshots before the next dashboard read."""
    return refresh_all()


class ClickUpTaskProposal(BaseModel):
    list_id: str
    name: str
    description: str = ""


@router.get("/actions/pending")
def pending():
    return {"items": pending_actions()}


@router.post("/actions/clickup-task")
def propose_task(proposal: ClickUpTaskProposal):
    return propose_clickup_task(**proposal.model_dump())


@router.post("/actions/{action_id}/approve")
def approve(action_id: str):
    return decide(action_id, True) or {"error": "Action is not pending."}


@router.post("/actions/{action_id}/reject")
def reject(action_id: str):
    return decide(action_id, False) or {"error": "Action is not pending."}


@router.get("/attention")
def attention():
    return {"items": build_attention(_data())}


@router.get("/activity")
def activity():
    return {"items": build_activity(_data())}


@router.get("/workload")
def workload():
    data = _data()
    return {"open_tasks": len(data.tasks) if data.availability["clickup"] else None, "available": data.availability["clickup"]}


@router.get("/trends")
def trends():
    return {"items": [], "available": False, "message": "Historical storage is not implemented yet."}


@router.get("/insights")
def insights():
    return {"items": build_insights(_data())}


@router.get("/agents")
def agents():
    return {"items": [{"name": name, "status": "available"} for name in ["Supervisor", "Planner", "GitHub Agent", "ClickUp Agent", "Gmail Agent", "Research Agent", "Synthesizer"]]}


def _person_profile(sources: dict[str, dict[str, Any]], messages: list[dict[str, Any]]) -> dict[str, Any]:
    clickup_user = sources.get("clickup", {}).get("authenticated_user") or {}
    gmail_email = _first_recipient_email(messages)
    return {
        "name": clickup_user.get("username") or sources.get("github", {}).get("authenticated_user") or "Unknown user",
        "email": clickup_user.get("email") or gmail_email,
        "timezone": clickup_user.get("timezone"),
        "initials": clickup_user.get("initials"),
        "avatar_url": clickup_user.get("profilePicture"),
        "clickup_user_id": clickup_user.get("id"),
        "github_user": sources.get("github", {}).get("authenticated_user"),
        "gmail_account_hint": gmail_email,
    }


def _first_recipient_email(messages: list[dict[str, Any]]) -> str | None:
    for message in messages:
        for recipient in message.get("recipients", []):
            _, email = parseaddr(str(recipient))
            if email:
                return email
    return None


def _count_rows(items: list[dict[str, Any]], key: str, *, default: str = "unknown") -> list[dict[str, Any]]:
    counter = Counter(str(item.get(key) or default).strip().lower() for item in items)
    return _counter_rows(counter)


def _list_count_rows(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for item in items:
        values = item.get(key) or []
        if not values:
            counter["none"] += 1
        for value in values:
            counter[str(value)] += 1
    return _counter_rows(counter)


def _tag_rows(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [row for row in _list_count_rows(tasks, "tags") if row["label"] != "none"]
    return rows or [{"label": "untagged", "count": len(tasks)}]


def _sender_rows(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for message in messages:
        sender = str(message.get("sender") or "unknown")
        _, email = parseaddr(sender)
        counter[email.split("@")[-1] if "@" in email else sender] += 1
    return _counter_rows(counter, limit=8)


def _counter_rows(counter: Counter[str], *, limit: int | None = None) -> list[dict[str, Any]]:
    rows = [{"label": label, "count": count} for label, count in counter.most_common(limit)]
    return rows


def _message_rows(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "sender": message.get("sender"),
            "subject": message.get("subject") or "(no subject)",
            "received_at": message.get("received_at"),
            "is_read": message.get("is_read", True),
            "labels": message.get("labels", []),
            "snippet": message.get("snippet"),
        }
        for message in messages
    ]
