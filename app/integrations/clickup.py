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

    def _get(self, endpoint: str):
        """Send a GET request to ClickUp."""

        response = requests.get(
            f"{self.BASE_URL}{endpoint}",
            headers=self.headers,
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
        """Get lists inside a ClickUp space."""

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
    ) -> list[ClickUpTask]:
        """Get tasks from a ClickUp list."""

        data = self._get(
            f"/list/{list_id}/task"
        )

        tasks = []

        for task in data.get("tasks", []):

            assignees = [
                user["username"]
                for user in task.get(
                    "assignees",
                    [],
                )
                if user.get("username")
            ]
            assignee_ids = [
                str(user["id"])
                for user in task.get("assignees", [])
                if user.get("id") is not None
            ]

            tags = [
                tag["name"]
                for tag in task.get(
                    "tags",
                    [],
                )
                if tag.get("name")
            ]

            due_date = task.get("due_date")
            date_created = task.get("date_created")
            date_updated = task.get("date_updated")

            tasks.append(
                ClickUpTask(
                    id=task["id"],
                    name=task["name"],
                    description=task.get(
                        "description"
                    ),
                    status=task.get(
                        "status",
                        {},
                    ).get(
                        "status"
                    ),
                    priority=(
                        task.get("priority") or {}
                    ).get("priority"),
                    url=task.get("url"),
                    assignees=assignees,
                    assignee_ids=assignee_ids,
                    tags=tags,
                    due_date=(
                        self._timestamp_to_datetime(
                            due_date
                        )
                        if due_date
                        else None
                    ),
                    date_created=(
                        self._timestamp_to_datetime(
                            date_created
                        )
                        if date_created
                        else None
                    ),
                    date_updated=(
                        self._timestamp_to_datetime(
                            date_updated
                        )
                        if date_updated
                        else None
                    ),
                )
            )

        return tasks

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
