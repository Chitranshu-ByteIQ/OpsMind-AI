from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    success: bool
    message: str
    agent: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class HealthResponse(BaseModel):
    status: str
    environment: str


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error: str