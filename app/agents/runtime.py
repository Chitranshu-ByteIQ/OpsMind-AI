import logging
from collections.abc import Sequence
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import BaseTool
from langchain_groq import ChatGroq
from langgraph.prebuilt import ToolNode

from app.config import settings


logger = logging.getLogger(__name__)


def get_llm(*, temperature: float = 0) -> ChatGroq:
    """Create the LLM only when a workflow request needs it."""

    if not settings.groq_api_key or not settings.groq_model:
        raise RuntimeError(
            "LLM configuration is missing. Set GROQ_API_KEY and GROQ_MODEL."
        )

    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=temperature,
    )


def run_tool_calling_agent(
    llm: BaseChatModel,
    tools: Sequence[BaseTool],
    request: str,
    *,
    max_iterations: int = 4,
) -> dict[str, Any]:
    """Run an LLM and dispatch its tool calls until it returns an answer."""

    agent = llm.bind_tools(list(tools))
    tool_node = ToolNode(list(tools))
    messages: list[BaseMessage] = [HumanMessage(content=request)]
    tool_results: list[Any] = []

    for _ in range(max_iterations):
        response = agent.invoke(messages)
        messages.append(response)

        if not isinstance(response, AIMessage) or not response.tool_calls:
            return {
                "text": _message_text(response),
                "tool_results": tool_results,
            }

        logger.info("Executing %d tool call(s)", len(response.tool_calls))
        tool_state = tool_node.invoke({"messages": messages})
        tool_messages = tool_state["messages"]
        messages.extend(tool_messages)
        tool_results.extend(message.content for message in tool_messages)

    raise RuntimeError("The agent exceeded the maximum tool-calling iterations.")


def _message_text(message: BaseMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    return str(content)