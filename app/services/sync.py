from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable

from app.data.store import save_source_failure, save_source_success, save_sync_state
from app.integrations.clickup import ClickUpIntegration
from app.integrations.github import GitHubIntegration
from app.tools.gmail_tools import get_gmail

logger = logging.getLogger(__name__)


def _dump(items: list[Any]) -> list[dict[str, Any]]:
    return [item.model_dump(mode="json") if hasattr(item, "model_dump") else item for item in items]


def sync_gmail() -> dict[str, Any]:
    logger.info("Refreshing Gmail data")
    messages = _dump(get_gmail().search_messages("newer_than:30d", max_results=100))
    return save_source_success("gmail", {"messages.json": messages})


def sync_github() -> dict[str, Any]:
    logger.info("Refreshing GitHub data")
    client = GitHubIntegration()
    user = client.get_authenticated_user()
    repositories = client.get_repositories(per_page=100)
    issues: list[Any] = []
    pull_requests: list[Any] = []
    for repository in repositories:
        owner, name = repository.full_name.split("/", 1)
        issues.extend(client.get_issues(owner, name))
        pull_requests.extend(client.get_pull_requests(owner, name))
    return save_source_success("github", {"repositories.json": _dump(repositories), "issues.json": _dump(issues), "pull_requests.json": _dump(pull_requests), "activity.json": []}, details={"authenticated_user": user.get("login")})


def sync_clickup() -> dict[str, Any]:
    logger.info("Refreshing personalized ClickUp data")
    client = ClickUpIntegration()
    user = client.get_authenticated_user()
    user_id = str(user.get("user", user).get("id", ""))
    tasks: list[Any] = []
    for team in client.get_teams().get("teams", []):
        for space in client.get_spaces(str(team["id"])):
            for work_list in client.get_lists(space.id):
                tasks.extend(client.get_tasks(work_list.id))
    normalized = _dump(tasks)
    mine = [task for task in normalized if user_id and user_id in {str(value) for value in task.get("assignee_ids", [])}]
    return save_source_success("clickup", {"tasks.json": mine}, details={"authenticated_user": user.get("user", user), "visible_task_count": len(normalized), "confirmed_assigned_count": len(mine)})


def refresh_all() -> dict[str, Any]:
    logger.info("Refresh started")
    operations: dict[str, Callable[[], dict[str, Any]]] = {"gmail": sync_gmail, "github": sync_github, "clickup": sync_clickup}
    results: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="opsmind-sync") as executor:
        futures = {executor.submit(operation): source for source, operation in operations.items()}
        for future in as_completed(futures):
            source = futures[future]
            try:
                results[source] = future.result()
                logger.info("Refresh succeeded for %s", source)
            except Exception as exc:
                logger.exception("Refresh failed for %s", source)
                results[source] = save_source_failure(source, exc)
    save_sync_state(results)
    logger.info("Refresh completed: %s", {name: result["status"] for name, result in results.items()})
    return {"sources": results}
