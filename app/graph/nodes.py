import logging

from langchain_core.messages import HumanMessage

from app.agents.clickup_agent import get_clickup_agent
from app.agents.github_agent import get_github_agent
from app.agents.gmail_agent import get_gmail_agent
from app.agents.planner import get_planner
from app.agents.research_agent import get_research_agent
from app.agents.runtime import run_tool_calling_agent
from app.agents.supervisor import get_supervisor
from app.agents.synthesizer import get_synthesizer

from app.graph.state import OpsMindState


logger = logging.getLogger(__name__)


AGENT_NAMES = ("github", "clickup", "gmail", "research")


def _requested_agents(request: str) -> list[str]:
    """Choose explicit source mentions deterministically for multi-source requests."""
    lowered = request.lower()
    selected = [name for name in AGENT_NAMES if name in lowered]
    return selected


def supervisor_node(state: OpsMindState) -> OpsMindState:
    """
    Decide which specialized agent should handle the request.
    """

    user_request = state["user_request"]

    response = get_supervisor().invoke(
        [
            HumanMessage(
                content=f"""
You are the supervisor of OpsMind AI.

Determine which specialized agent should handle this request.

Available agents:
- github
- clickup
- gmail
- research

User request:
{user_request}

Return only the agent name.
"""
            )
        ]
    )

    requested = _requested_agents(user_request)
    agent_name = response.content.strip().lower()

    if agent_name not in {
        "github",
        "clickup",
        "gmail",
        "research",
    }:
        agent_name = requested[0] if requested else "research"

    selected = requested or [agent_name]

    return {
        "next_agent": agent_name,
        "agent": agent_name,
        "selected_agents": selected,
    }


def planner_node(state: OpsMindState) -> OpsMindState:
    """
    Create a simple execution plan for the request.
    """

    user_request = state["user_request"]

    response = get_planner().invoke(
        [
            HumanMessage(
                content=f"""
Create a simple execution plan for this request.

User request:
{user_request}

Return the plan as a numbered list.
Keep it concise.
"""
            )
        ]
    )

    plan_text = response.content

    plan = [
        line.strip()
        for line in plan_text.splitlines()
        if line.strip()
    ]

    return {
        "plan": plan
    }


def github_node(state: OpsMindState) -> OpsMindState:
    """
    Execute the GitHub agent.
    """

    request = state["user_request"]

    llm, tools = get_github_agent()
    logger.info("Agent selected: github")
    result = run_tool_calling_agent(llm, tools, request)

    return {
        "agent_results": {
            "github": result
        }
    }


def clickup_node(state: OpsMindState) -> OpsMindState:
    """
    Execute the ClickUp agent.
    """

    request = state["user_request"]

    llm, tools = get_clickup_agent()
    logger.info("Agent selected: clickup")
    result = run_tool_calling_agent(llm, tools, request)

    return {
        "agent_results": {
            "clickup": result
        }
    }


def gmail_node(state: OpsMindState) -> OpsMindState:
    """
    Execute the Gmail agent.
    """

    request = state["user_request"]

    llm, tools = get_gmail_agent()
    logger.info("Agent selected: gmail")
    result = run_tool_calling_agent(llm, tools, request)

    return {
        "agent_results": {
            "gmail": result
        }
    }


def research_node(state: OpsMindState) -> OpsMindState:
    """
    Execute the research agent.
    """

    request = state["user_request"]

    llm, tools = get_research_agent()
    logger.info("Agent selected: research")
    result = run_tool_calling_agent(llm, tools, request)

    return {
        "agent_results": {
            "research": result
        }
    }


def synthesizer_node(state: OpsMindState) -> OpsMindState:
    """
    Combine the agent result into a final response.
    """

    user_request = state["user_request"]
    results = state.get("agent_results", {})

    response = get_synthesizer().invoke(
        [
            HumanMessage(
                content=f"""
You are the final response synthesizer for OpsMind AI.

User request:
{user_request}

Agent results:
{results}

Create one clear and useful response for the user.
Do not mention internal implementation details.
"""
            )
        ]
    )

    return {
        "final_response": response.content
    }


def multi_source_node(state: OpsMindState) -> OpsMindState:
    """Execute explicitly requested source agents before a single synthesis step."""
    results = {}
    node_map = {
        "github": github_node,
        "clickup": clickup_node,
        "gmail": gmail_node,
        "research": research_node,
    }
    for agent_name in state.get("selected_agents", []):
        result = node_map[agent_name](state)
        results.update(result.get("agent_results", {}))
    return {"agent_results": results, "agent": ", ".join(state.get("selected_agents", []))}
