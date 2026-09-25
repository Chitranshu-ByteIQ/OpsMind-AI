from langgraph.graph import StateGraph, START, END

from app.graph.state import OpsMindState

from app.graph.nodes import (
    local_lookup_node,
    route_after_local_lookup,
    supervisor_node,
    planner_node,
    github_node,
    clickup_node,
    gmail_node,
    research_node,
    multi_source_node,
    synthesizer_node,
    critic_node,
    route_after_critic,
)

from app.graph.edges import route_agent


def build_workflow():
    """
    Build and compile the OpsMind AI workflow.
    """

    graph = StateGraph(OpsMindState)

    # -------------------------
    # Add nodes
    # -------------------------

    graph.add_node(
        "supervisor",
        supervisor_node,
    )

    graph.add_node(
        "planner",
        planner_node,
    )

    graph.add_node(
        "github",
        github_node,
    )

    graph.add_node(
        "clickup",
        clickup_node,
    )

    graph.add_node(
        "gmail",
        gmail_node,
    )

    graph.add_node("local_lookup", local_lookup_node)
    graph.add_node(
        "research",
        research_node,
    )
    graph.add_node("multi_source", multi_source_node)

    graph.add_node(
        "synthesizer",
        synthesizer_node,
    )
    graph.add_node("critic", critic_node)

    # -------------------------
    # Starting point
    # -------------------------

    graph.add_edge(
        START,
        "local_lookup",
    )
    graph.add_conditional_edges("local_lookup", route_after_local_lookup, {"supervisor": "supervisor", "end": END})

    # -------------------------
    # Supervisor → Planner
    # -------------------------

    graph.add_edge(
        "supervisor",
        "planner",
    )

    # -------------------------
    # Planner → Agent
    # -------------------------

    graph.add_conditional_edges(
        "planner",
        route_agent,
        {
            "github": "github",
            "clickup": "clickup",
            "gmail": "gmail",
            "research": "research",
            "multi_source": "multi_source",
        },
    )

    # -------------------------
    # Agent → Synthesizer
    # -------------------------

    graph.add_edge(
        "github",
        "synthesizer",
    )

    graph.add_edge(
        "clickup",
        "synthesizer",
    )

    graph.add_edge(
        "gmail",
        "synthesizer",
    )

    graph.add_edge(
        "research",
        "synthesizer",
    )
    graph.add_edge("multi_source", "synthesizer")

    # -------------------------
    # Synthesizer → End
    # -------------------------

    graph.add_edge(
        "synthesizer",
        "critic",
    )
    graph.add_conditional_edges("critic", route_after_critic, {"planner": "planner", "end": END})

    return graph.compile()


workflow = build_workflow()
