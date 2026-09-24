from langchain_core.tools import tool

from app.integrations.clickup import ClickUpIntegration


clickup = ClickUpIntegration()


@tool
def get_clickup_teams():
    """Get ClickUp teams available to the authenticated user."""

    return clickup.get_teams()


@tool
def get_clickup_spaces(team_id: str):
    """
    Get spaces belonging to a ClickUp team.

    Use this tool to discover the workspace structure
    before looking for lists and tasks.
    """

    spaces = clickup.get_spaces(team_id)

    return [space.model_dump() for space in spaces]


@tool
def get_clickup_lists(space_id: str):
    """
    Get lists belonging to a ClickUp space.

    Use this tool to discover where ClickUp tasks are organized.
    """

    lists = clickup.get_lists(space_id)

    return [item.model_dump() for item in lists]


@tool
def get_clickup_tasks(list_id: str):
    """
    Get tasks from a ClickUp list.

    Use this tool to inspect current work, task status,
    priorities, assignees, tags, and due dates.
    """

    tasks = clickup.get_tasks(list_id)

    return [task.model_dump() for task in tasks]