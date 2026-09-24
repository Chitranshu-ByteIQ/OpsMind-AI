from datetime import datetime

from pydantic import BaseModel, Field


class GitHubRepository(BaseModel):
    """GitHub repository information."""

    name: str
    full_name: str
    description: str | None = None
    url: str
    private: bool = False
    default_branch: str = "main"


class GitHubIssue(BaseModel):
    """GitHub issue information."""

    number: int
    title: str
    state: str
    url: str
    repository: str
    author: str | None = None
    assignee: str | None = None
    labels: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GitHubPullRequest(BaseModel):
    """GitHub pull request information."""

    number: int
    title: str
    state: str
    url: str
    repository: str
    author: str | None = None
    reviewers: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None