from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.data.store import load_source, source_metadata


@dataclass
class UnifiedWorkData:
    repositories: list[dict[str, Any]] = field(default_factory=list)
    issues: list[dict[str, Any]] = field(default_factory=list)
    pull_requests: list[dict[str, Any]] = field(default_factory=list)
    tasks: list[dict[str, Any]] = field(default_factory=list)
    messages: list[dict[str, Any]] = field(default_factory=list)
    availability: dict[str, bool] = field(
        default_factory=lambda: {"github": False, "clickup": False, "gmail": False, "research": True}
    )


def collect_dashboard_data() -> UnifiedWorkData:
    """Load persisted snapshots only; dashboard rendering never calls external APIs."""
    metadata = {source: source_metadata(source) for source in ("github", "clickup", "gmail")}
    return UnifiedWorkData(
        repositories=load_source("github", "repositories.json"),
        issues=load_source("github", "issues.json"),
        pull_requests=load_source("github", "pull_requests.json"),
        tasks=load_source("clickup", "tasks.json"),
        messages=load_source("gmail", "messages.json"),
        availability={"github": metadata["github"].get("status") in {"success", "failed"} and bool(metadata["github"].get("last_successful_sync")), "clickup": metadata["clickup"].get("status") in {"success", "failed"} and bool(metadata["clickup"].get("last_successful_sync")), "gmail": metadata["gmail"].get("status") in {"success", "failed"} and bool(metadata["gmail"].get("last_successful_sync")), "research": True},
    )
