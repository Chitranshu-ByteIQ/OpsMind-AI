from app.agents.runtime import get_llm
from app.tools.gmail_tools import (
    search_gmail_messages,
    get_gmail_message,
)


gmail_tools = [
    search_gmail_messages,
    get_gmail_message,
]


def get_gmail_agent():
    return get_llm(temperature=0), gmail_tools