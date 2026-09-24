from langchain_core.tools import tool

from app.integrations.tavily import TavilyIntegration


tavily = TavilyIntegration()


@tool
def search_web(
    query: str,
    max_results: int = 5,
):
    """
    Search the web using Tavily.

    Use this tool when current external information,
    research, documentation, news, or web knowledge is required.
    """

    return tavily.search(
        query=query,
        max_results=max_results,
    )


@tool
def research_web(
    query: str,
    max_results: int = 5,
):
    """
    Search the web and return a summarized answer
    together with supporting search results.
    """

    return tavily.search_with_answer(
        query=query,
        max_results=max_results,
    )