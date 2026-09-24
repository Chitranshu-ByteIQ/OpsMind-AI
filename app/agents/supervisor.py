from app.agents.runtime import get_llm


def get_supervisor():
    return get_llm(temperature=0)