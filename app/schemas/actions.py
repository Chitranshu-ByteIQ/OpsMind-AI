from enum import Enum

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Supported actions in OpsMind AI."""

    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SEND = "send"


class ActionStatus(str, Enum):
    """Action execution status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class ActionRequest(BaseModel):
    """Action proposed by an agent."""

    action_type: ActionType
    tool_name: str

    description: str

    parameters: dict = Field(default_factory=dict)

    requires_approval: bool = True


class ActionResult(BaseModel):
    """Result of an executed action."""

    action_type: ActionType
    tool_name: str

    status: ActionStatus

    message: str

    data: dict | None = None