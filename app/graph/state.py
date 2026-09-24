from typing import TypedDict, Any


class OpsMindState(TypedDict, total=False):
    # Original user request
    user_request: str

    # Supervisor decision
    next_agent: str
    agent: str
    selected_agents: list[str]

    # Planner output
    plan: list[str]

    # Results returned by agents
    agent_results: dict[str, Any]

    # Final synthesized response
    final_response: str

    # Error information
    error: str
