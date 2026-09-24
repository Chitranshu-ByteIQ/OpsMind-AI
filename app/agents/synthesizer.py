from app.agents.runtime import get_llm


def get_synthesizer():
    return get_llm(temperature=0)