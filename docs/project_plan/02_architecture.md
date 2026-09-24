# Architecture

`Streamlit → FastAPI → (dashboard analytics | /chat LangGraph)`. Chat remains `Supervisor → Planner → selected specialist(s) → Synthesizer`. Tools call only read-only integration methods. The analytics layer is deterministic and uses integration responses; it never uses an LLM to fabricate metrics. Write actions remain outside the exposed API and require the existing approval guardrail.
