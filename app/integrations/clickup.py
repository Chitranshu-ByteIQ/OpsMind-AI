from __future__ import annotations

from typing import Any

import requests

from app.config import settings
from app.schemas.clickup import (
    ClickUpList,
    ClickUpSpace,
    ClickUpTask,
)


class ClickUpIntegration:
    """Client for interacting with the ClickUp API."""

    BASE_URL = "https://api.clickup.com/api/v2"

    def __init__(self):
        self.headers = {
            "Authorization": settings.clickup_api_token,
            "Content-Type": "application/json",
        }

    def _get(self, endpoint: str, *, params: list[tuple[str, Any]] | dict[str, Any] | None = None):
        """Send a GET request to ClickUp."""

        response = requests.get(
            f"{self.BASE_URL}{endpoint}",
            headers=self.headers,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def _post(self, endpoint: str, payload: dict) -> dict:
        response = requests.post(f"{self.BASE_URL}{endpoint}", headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def create_task(self, list_id: str, name: str, description: str = "") -> dict:
        """Create a ClickUp task. Call only after an explicit human approval."""
        return self._post(f"/list/{list_id}/task", {"name": name, "description": description})

    def get_teams(self) -> dict:
        """Get ClickUp teams/workspaces."""

        return self._get("/team")

    def get_authenticated_user(self) -> dict:
        """Return the user represented by the configured ClickUp token."""
        return self._get("/user")

    def get_spaces(
        self,
        team_id: str,
    ) -> list[ClickUpSpace]:
        """Get spaces inside a ClickUp workspace."""

        data = self._get(
            f"/team/{team_id}/space"
        )

        spaces = []

        for space in data.get("spaces", []):
            spaces.append(
                ClickUpSpace(
                    id=space["id"],
                    name=space["name"],
                )
            )

        return spaces

    def get_lists(
        self,
        space_id: str,
    ) -> list[ClickUpList]:
        """Get folderless lists inside a ClickUp space."""

        data = self._get(
            f"/space/{space_id}/list"
        )

        lists = []

        for item in data.get("lists", []):
            lists.append(
                ClickUpList(
                    id=item["id"],
                    name=item["name"],
                    url=item.get("url"),
                )
            )

        return lists

    def get_tasks(
        self,
        list_id: str,
        *,
        assignee_ids: list[str] | None = None,
        include_closed: bool = False,
    ) -> list[ClickUpTask]:
        """Get tasks from a ClickUp list."""

        params: list[tuple[str, Any]] = [
            ("archived", "false"),
            ("subtasks", "true"),
            ("include_timl", "true"),
            ("include_closed", str(include_closed).lower()),
        ]
        for assignee_id in assignee_ids or []:
            params.append(("assignees[]", assignee_id))

        return self._get_paginated_tasks(f"/list/{list_id}/task", params)

    def get_filtered_team_tasks(
        self,
        team_id: str,
        *,
        assignee_ids: list[str] | None = None,
        include_closed: bool = False,
    ) -> list[ClickUpTask]:
        """Get tasks matching filters anywhere in a ClickUp workspace."""

        params: list[tuple[str, Any]] = [
            ("subtasks", "true"),
            ("include_closed", str(include_closed).lower()),
            ("order_by", "updated"),
            ("reverse", "true"),
        ]
        for assignee_id in assignee_ids or []:
            params.append(("assignees[]", assignee_id))

        return self._get_paginated_tasks(f"/team/{team_id}/task", params)

    def _get_paginated_tasks(self, endpoint: str, params: list[tuple[str, Any]]) -> list[ClickUpTask]:
        tasks: list[ClickUpTask] = []
        page = 0

        while True:
            data = self._get(endpoint, params=[*params, ("page", page)])
            page_tasks = data.get("tasks", [])
            tasks.extend(self._task_from_api(task) for task in page_tasks)

            if len(page_tasks) < 100:
                break
            page += 1

        return tasks

    def _task_from_api(self, task: dict[str, Any]) -> ClickUpTask:
        assignees = [
            user["username"]
            for user in task.get("assignees", [])
            if user.get("username")
        ]
        assignee_ids = [
            str(user["id"])
            for user in task.get("assignees", [])
            if user.get("id") is not None
        ]
        tags = [
            tag["name"]
            for tag in task.get("tags", [])
            if tag.get("name")
        ]

        due_date = task.get("due_date")
        date_created = task.get("date_created")
        date_updated = task.get("date_updated")

        return ClickUpTask(
            id=task["id"],
            name=task["name"],
            description=task.get("description"),
            status=task.get("status", {}).get("status") or "unknown",
            priority=(task.get("priority") or {}).get("priority"),
            url=task.get("url"),
            assignees=assignees,
            assignee_ids=assignee_ids,
            tags=tags,
            due_date=(
                self._timestamp_to_datetime(due_date)
                if due_date
                else None
            ),
            date_created=(
                self._timestamp_to_datetime(date_created)
                if date_created
                else None
            ),
            date_updated=(
                self._timestamp_to_datetime(date_updated)
                if date_updated
                else None
            ),
        )

    @staticmethod
    def _timestamp_to_datetime(
        timestamp: str | int,
    ):
        """Convert ClickUp millisecond timestamp."""

        from datetime import datetime, timezone

        return datetime.fromtimestamp(
            int(timestamp) / 1000,
            tz=timezone.utc,
        )
