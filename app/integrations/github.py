import requests

from app.config import settings
from app.schemas.github import (
    GitHubIssue,
    GitHubPullRequest,
    GitHubRepository,
)


class GitHubIntegration:
    """Client for interacting with the GitHub API."""

    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get(self, endpoint: str):
        """Send a GET request to GitHub."""

        response = requests.get(
            f"{self.BASE_URL}{endpoint}",
            headers=self.headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def get_authenticated_user(self) -> dict:
        """Get the authenticated GitHub user."""

        return self._get("/user")

    def get_repositories(
        self,
        per_page: int = 30,
    ) -> list[GitHubRepository]:
        """Get repositories accessible to the authenticated user."""

        data = self._get(
            f"/user/repos?per_page={per_page}"
        )

        repositories = []

        for repo in data:
            repositories.append(
                GitHubRepository(
                    name=repo["name"],
                    full_name=repo["full_name"],
                    description=repo.get("description"),
                    url=repo["html_url"],
                    private=repo["private"],
                    default_branch=repo.get(
                        "default_branch",
                        "main",
                    ),
                )
            )

        return repositories

    def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
    ) -> list[GitHubIssue]:
        """Get issues from a repository."""

        data = self._get(
            f"/repos/{owner}/{repo}/issues"
            f"?state={state}"
        )

        issues = []

        for issue in data:

            # GitHub returns pull requests through
            # the issues endpoint as well.
            if "pull_request" in issue:
                continue

            issues.append(
                GitHubIssue(
                    number=issue["number"],
                    title=issue["title"],
                    state=issue["state"],
                    url=issue["html_url"],
                    repository=f"{owner}/{repo}",
                    author=(
                        issue["user"]["login"]
                        if issue.get("user")
                        else None
                    ),
                    assignee=(
                        issue["assignee"]["login"]
                        if issue.get("assignee")
                        else None
                    ),
                    labels=[
                        label["name"]
                        for label in issue.get(
                            "labels",
                            [],
                        )
                    ],
                    created_at=issue.get("created_at"),
                    updated_at=issue.get("updated_at"),
                )
            )

        return issues

    def get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
    ) -> list[GitHubPullRequest]:
        """Get pull requests from a repository."""

        data = self._get(
            f"/repos/{owner}/{repo}/pulls"
            f"?state={state}"
        )

        pull_requests = []

        for pr in data:
            pull_requests.append(
                GitHubPullRequest(
                    number=pr["number"],
                    title=pr["title"],
                    state=pr["state"],
                    url=pr["html_url"],
                    repository=f"{owner}/{repo}",
                    author=(
                        pr["user"]["login"]
                        if pr.get("user")
                        else None
                    ),
                    reviewers=[],
                    created_at=pr.get("created_at"),
                    updated_at=pr.get("updated_at"),
                )
            )

        return pull_requests