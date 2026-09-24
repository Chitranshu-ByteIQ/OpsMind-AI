from app.graph.edges import route_agent


def test_route_agent_uses_selected_single_agent():
    assert route_agent({"next_agent": "github", "selected_agents": ["github"]}) == "github"


def test_route_agent_uses_multi_source_branch():
    assert route_agent({"selected_agents": ["github", "gmail"]}) == "multi_source"
