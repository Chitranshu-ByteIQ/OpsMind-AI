from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DATA_ROOT = Path("data")
SOURCES = ("gmail", "github", "clickup")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(*parts: str) -> Path:
    return DATA_ROOT.joinpath(*parts)


def read_json(*parts: str, default: Any) -> Any:
    path = _path(*parts)
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def write_json(*parts: str, value: Any) -> None:
    path = _path(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(value, file, ensure_ascii=False, indent=2, default=str)
    temporary.replace(path)


def load_source(source: str, filename: str) -> list[dict[str, Any]]:
    return read_json(source, filename, default=[])


def source_metadata(source: str) -> dict[str, Any]:
    return read_json(source, "metadata.json", default={"source": source, "status": "not_synced", "item_count": 0})


def sync_state() -> dict[str, Any]:
    return read_json("system", "sync_state.json", default={"last_sync": None, "sources": {}})


def save_source_success(source: str, files: dict[str, list[dict[str, Any]]], *, details: dict[str, Any] | None = None) -> dict[str, Any]:
    count = 0
    for filename, items in files.items():
        write_json(source, filename, value=items)
        count += len(items)
    metadata = {"source": source, "status": "success", "last_successful_sync": now_iso(), "last_error": None, "item_count": count, **(details or {})}
    write_json(source, "metadata.json", value=metadata)
    return metadata


def save_source_failure(source: str, error: Exception | str) -> dict[str, Any]:
    previous = source_metadata(source)
    metadata = {**previous, "source": source, "status": "failed", "last_attempt": now_iso(), "last_error": str(error), "preserved_previous_data": bool(previous.get("last_successful_sync"))}
    write_json(source, "metadata.json", value=metadata)
    return metadata


def save_sync_state(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    state = {"last_sync": now_iso(), "sources": results}
    write_json("system", "sync_state.json", value=state)
    return state


def append_action(record: dict[str, Any]) -> None:
    records = read_json("system", "actions.json", default=[])
    records.append(record)
    write_json("system", "actions.json", value=records)


def actions() -> list[dict[str, Any]]:
    return read_json("system", "actions.json", default=[])
