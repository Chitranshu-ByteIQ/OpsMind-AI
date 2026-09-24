from app.agents.runtime import get_llm
from app.tools.tavily_tools import (
    search_web,
    research_web,
)


research_tools = [
    search_web,
    research_web,
]


def get_research_agent():
    return get_llm(temperature=0), research_tools