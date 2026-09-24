from app.agents.runtime import get_llm
from app.tools.github_tools import (
    get_github_repositories,
    get_github_issues,
    get_github_pull_requests,
    get_github_user,
)


github_tools = [
    get_github_repositories,
    get_github_issues,
    get_github_pull_requests,
    get_github_user,
]


def get_github_agent():
    return get_llm(temperature=0), github_tools