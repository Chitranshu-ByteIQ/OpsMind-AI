from app.agents.runtime import get_llm
from app.tools.clickup_tools import (
    get_clickup_teams,
    get_clickup_spaces,
    get_clickup_lists,
    get_clickup_tasks,
)


clickup_tools = [
    get_clickup_teams,
    get_clickup_spaces,
    get_clickup_lists,
    get_clickup_tasks,
]


def get_clickup_agent():
    return get_llm(temperature=0), clickup_tools