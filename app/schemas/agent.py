from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.actions import ActionRequest, ActionResult


class AgentType(str, Enum):
    """Available OpsMind AI agents."""

    SUPERVISOR = "supervisor"
    PLANNER = "planner"
    GITHUB = "github"
    CLICKUP = "clickup"
    GMAIL = "gmail"
    RESEARCH = "research"
    SYNTHESIZER = "synthesizer"
    CRITIC = "critic"


class AgentStatus(str, Enum):
    """Agent execution status."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRequest(BaseModel):
    """Request sent to an agent."""

    agent_type: AgentType

    task: str

    context: dict = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Response returned by an agent."""

    agent_type: AgentType

    status: AgentStatus

    message: str

    data: dict | None = None

    actions: list[ActionRequest] = Field(default_factory=list)

    action_results: list[ActionResult] = Field(default_factory=list)