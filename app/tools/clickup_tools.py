from langchain_core.tools import tool

from app.data.store import load_source


@tool
def get_clickup_teams():
    """Get ClickUp teams available to the authenticated user."""

    return {"message": "Workspace discovery is performed during Refresh Data.", "data_source": "local"}


@tool
def get_clickup_spaces(team_id: str):
    """
    Get spaces belonging to a ClickUp team.

    Use this tool to discover the workspace structure
    before looking for lists and tasks.
    """

    return []


@tool
def get_clickup_lists(space_id: str):
    """
    Get lists belonging to a ClickUp space.

    Use this tool to discover where ClickUp tasks are organized.
    """

    return []


@tool
def get_clickup_tasks(list_id: str):
    """
    Get tasks from a ClickUp list.

    Use this tool to inspect current work, task status,
    priorities, assignees, tags, and due dates.
    """

    return load_source("clickup", "tasks.json")
