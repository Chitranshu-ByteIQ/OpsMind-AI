# Agent Workflow

The Planner remains an explicit LangGraph node. The supervisor selects one or more source agents deterministically from the request; each selected read-only agent executes before synthesis. The current implementation does not expose chain-of-thought. Safe metadata contains only selected agents, the plan, and tool result summaries.
