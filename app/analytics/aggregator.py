from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.integrations.clickup import ClickUpIntegration
from app.integrations.github import GitHubIntegration
from app.tools.gmail_tools import get_gmail


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


def _dump(items: list[Any]) -> list[dict[str, Any]]:
    return [item.model_dump(mode="json") if hasattr(item, "model_dump") else item for item in items]


def collect_dashboard_data(*, email_query: str = "is:unread newer_than:14d") -> UnifiedWorkData:
    """Collect best-effort, read-only dashboard data without failing the entire dashboard."""
    data = UnifiedWorkData()
    try:
        github = GitHubIntegration()
        repos = github.get_repositories()
        data.repositories = _dump(repos)
        data.availability["github"] = True
        for repo in repos:
            owner, name = repo.full_name.split("/", 1)
            data.issues.extend(_dump(github.get_issues(owner, name)))
            data.pull_requests.extend(_dump(github.get_pull_requests(owner, name)))
    except Exception:
        pass
    try:
        clickup = ClickUpIntegration()
        teams = clickup.get_teams().get("teams", [])
        data.availability["clickup"] = True
        for team in teams:
            for space in clickup.get_spaces(str(team["id"])):
                for work_list in clickup.get_lists(space.id):
                    data.tasks.extend(_dump(clickup.get_tasks(work_list.id)))
    except Exception:
        data.availability["clickup"] = False
    try:
        data.messages = _dump(get_gmail().search_messages(email_query, max_results=20))
        data.availability["gmail"] = True
    except Exception:
        pass
    return data
