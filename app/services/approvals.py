from __future__ import annotations

from uuid import uuid4
from typing import Any

from app.data.store import actions, append_action, now_iso, write_json
from app.integrations.clickup import ClickUpIntegration


def propose_clickup_task(*, list_id: str, name: str, description: str = "") -> dict[str, Any]:
    record = {"id": str(uuid4()), "status": "pending", "action": "create_clickup_task", "target": {"list_id": list_id}, "proposed": {"name": name, "description": description}, "created_at": now_iso(), "result": None}
    append_action(record)
    return record


def pending_actions() -> list[dict[str, Any]]:
    return [record for record in actions() if record.get("status") == "pending"]


def decide(action_id: str, approve: bool) -> dict[str, Any] | None:
    records = actions()
    record = next((item for item in records if item.get("id") == action_id), None)
    if not record or record.get("status") != "pending":
        return None
    if not approve:
        record.update({"status": "rejected", "decided_at": now_iso()})
    else:
        try:
            task = ClickUpIntegration().create_task(record["target"]["list_id"], record["proposed"]["name"], record["proposed"]["description"])
            record.update({"status": "completed", "decided_at": now_iso(), "result": {"id": task.get("id"), "url": task.get("url")}})
        except Exception as exc:
            record.update({"status": "failed", "decided_at": now_iso(), "result": {"error": str(exc)}})
    write_json("system", "actions.json", value=records)
    return record
