from langchain_core.tools import tool

from app.integrations.github import GitHubIntegration


github = GitHubIntegration()


@tool
def get_github_repositories():
    """Get repositories accessible to the authenticated GitHub user."""
    
    repositories = github.get_repositories()

    return [repository.model_dump() for repository in repositories]


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

    issues = github.get_issues(
        owner=owner,
        repo=repo,
        state=state,
    )

    return [issue.model_dump() for issue in issues]


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

    pull_requests = github.get_pull_requests(
        owner=owner,
        repo=repo,
        state=state,
    )

    return [pull_request.model_dump() for pull_request in pull_requests]


@tool
def get_github_user():
    """Get information about the authenticated GitHub user."""

    return github.get_authenticated_user()