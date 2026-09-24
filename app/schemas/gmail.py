from datetime import datetime

from pydantic import BaseModel, Field


class GmailMessage(BaseModel):
    """Gmail message information."""

    id: str
    thread_id: str

    sender: str
    recipients: list[str] = Field(default_factory=list)

    subject: str
    body: str | None = None

    snippet: str | None = None

    received_at: datetime | None = None

    labels: list[str] = Field(default_factory=list)

    is_read: bool = True