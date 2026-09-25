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
    local_response: str
    critic_result: dict[str, Any]
    replan_attempts: int

    # Error information
    error: str
