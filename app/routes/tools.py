from fastapi import APIRouter, Query

from app.integrations.clickup import ClickUpIntegration
from app.integrations.github import GitHubIntegration
from app.tools.gmail_tools import get_gmail
from app.integrations.tavily import TavilyIntegration

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.get("/github/repositories")
def github_repositories(): return [item.model_dump(mode="json") for item in GitHubIntegration().get_repositories()]

@router.get("/github/issues")
def github_issues(owner: str, repo: str, state: str = "open"): return [item.model_dump(mode="json") for item in GitHubIntegration().get_issues(owner, repo, state)]

@router.get("/github/pull-requests")
def github_pull_requests(owner: str, repo: str, state: str = "open"): return [item.model_dump(mode="json") for item in GitHubIntegration().get_pull_requests(owner, repo, state)]

@router.get("/clickup/teams")
def clickup_teams(): return ClickUpIntegration().get_teams()

@router.get("/clickup/spaces/{team_id}")
def clickup_spaces(team_id: str): return [item.model_dump(mode="json") for item in ClickUpIntegration().get_spaces(team_id)]

@router.get("/clickup/lists/{space_id}")
def clickup_lists(space_id: str): return [item.model_dump(mode="json") for item in ClickUpIntegration().get_lists(space_id)]

@router.get("/clickup/tasks/{list_id}")
def clickup_tasks(list_id: str): return [item.model_dump(mode="json") for item in ClickUpIntegration().get_tasks(list_id)]

@router.get("/gmail/search")
def gmail_search(query: str = "newer_than:7d", max_results: int = Query(default=20, le=50)): return [item.model_dump(mode="json") for item in get_gmail().search_messages(query, max_results)]

@router.get("/gmail/{message_id}")
def gmail_message(message_id: str):
    item = get_gmail().get_message(message_id)
    return item.model_dump(mode="json") if item else {"message": "Gmail message not found."}

@router.get("/research/search")
def research_search(query: str, max_results: int = Query(default=5, le=10)): return TavilyIntegration().search(query, max_results)
