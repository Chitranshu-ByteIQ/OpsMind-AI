from datetime import datetime

from pydantic import BaseModel, Field


class ClickUpTask(BaseModel):
    """ClickUp task information."""

    id: str
    name: str
    description: str | None = None
    status: str
    priority: str | None = None
    url: str | None = None

    assignees: list[str] = Field(default_factory=list)
    assignee_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    due_date: datetime | None = None
    date_created: datetime | None = None
    date_updated: datetime | None = None


class ClickUpList(BaseModel):
    """ClickUp list information."""

    id: str
    name: str
    url: str | None = None


class ClickUpSpace(BaseModel):
    """ClickUp space information."""

    id: str
    name: str
