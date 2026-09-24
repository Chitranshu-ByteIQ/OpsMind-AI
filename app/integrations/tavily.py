import requests

from app.config import settings


class TavilyIntegration:
    """Client for interacting with the Tavily API."""

    BASE_URL = "https://api.tavily.com/search"

    def __init__(self):
        self.api_key = settings.tavily_api_key

    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
    ) -> list[dict]:
        """Search the web using Tavily."""

        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_answer": True,
        }

        response = requests.post(
            self.BASE_URL,
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "results",
            []
        )

    def search_with_answer(
        self,
        query: str,
        max_results: int = 5,
    ) -> dict:
        """Return Tavily search results and generated answer."""

        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_answer": True,
        }

        response = requests.post(
            self.BASE_URL,
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return {
            "answer": data.get("answer"),
            "results": data.get(
                "results",
                [],
            ),
        }