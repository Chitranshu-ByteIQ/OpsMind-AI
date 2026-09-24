from app.graph.state import OpsMindState


def route_agent(state: OpsMindState) -> str:
    """
    Route the workflow to the selected specialized agent.
    """

    if len(state.get("selected_agents", [])) > 1:
        return "multi_source"

    agent = state.get("next_agent", "research")

    routes = {
        "github": "github",
        "clickup": "clickup",
        "gmail": "gmail",
        "research": "research",
        "multi_source": "multi_source",
    }

    return routes.get(agent, "research")
