from app.agents.runtime import get_llm


def get_planner():
    return get_llm(temperature=0.7)