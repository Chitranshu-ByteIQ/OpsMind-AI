from langchain_core.tools import tool

from app.data.store import load_source, source_metadata


@tool
def get_github_repositories():
    """Get repositories accessible to the authenticated GitHub user."""
    
    return load_source("github", "repositories.json")


@tool
def get_github_issues(
    owner: str,
    repo: str,
    state: str = "open",
):
    """
    Get issues from a GitHub repository.

    Use this tool to inspect open or closed issues,
    bugs, tasks, and other repository work items.
    """

    return [item for item in load_source("github", "issues.json") if item.get("repository") == f"{owner}/{repo}" and item.get("state") == state]


@tool
def get_github_pull_requests(
    owner: str,
    repo: str,
    state: str = "open",
):
    """
    Get pull requests from a GitHub repository.

    Use this tool to inspect active or closed pull requests
    and understand current development activity.
    """

    return [item for item in load_source("github", "pull_requests.json") if item.get("repository") == f"{owner}/{repo}" and item.get("state") == state]


@tool
def get_github_user():
    """Get information about the authenticated GitHub user."""

    return {"login": source_metadata("github").get("authenticated_user"), "data_source": "local"}
