from fastapi import APIRouter

from app.analytics.aggregator import collect_dashboard_data
from app.analytics.insights import build_insights
from app.analytics.metrics import build_activity, build_attention, build_summary
from app.data.store import source_metadata, sync_state
from app.services.sync import refresh_all
from app.services.approvals import decide, pending_actions, propose_clickup_task
from pydantic import BaseModel

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

def _data(): return collect_dashboard_data()

@router.get("/summary")
def summary():
    data = _data()
    return {"metrics": build_summary(data), "connections": data.availability, "sync": sync_state(), "sources": {name: source_metadata(name) for name in ("gmail", "github", "clickup")}}

@router.post("/refresh")
def refresh():
    """Explicitly retrieve and persist snapshots before the next dashboard read."""
    return refresh_all()

class ClickUpTaskProposal(BaseModel):
    list_id: str
    name: str
    description: str = ""

@router.get("/actions/pending")
def pending(): return {"items": pending_actions()}

@router.post("/actions/clickup-task")
def propose_task(proposal: ClickUpTaskProposal): return propose_clickup_task(**proposal.model_dump())

@router.post("/actions/{action_id}/approve")
def approve(action_id: str): return decide(action_id, True) or {"error": "Action is not pending."}

@router.post("/actions/{action_id}/reject")
def reject(action_id: str): return decide(action_id, False) or {"error": "Action is not pending."}

@router.get("/attention")
def attention(): return {"items": build_attention(_data())}

@router.get("/activity")
def activity(): return {"items": build_activity(_data())}

@router.get("/workload")
def workload():
    data = _data()
    return {"open_tasks": len(data.tasks) if data.availability["clickup"] else None, "available": data.availability["clickup"]}

@router.get("/trends")
def trends(): return {"items": [], "available": False, "message": "Historical storage is not implemented yet."}

@router.get("/insights")
def insights(): return {"items": build_insights(_data())}

@router.get("/agents")
def agents(): return {"items": [{"name": name, "status": "available"} for name in ["Supervisor", "Planner", "GitHub Agent", "ClickUp Agent", "Gmail Agent", "Research Agent", "Synthesizer"]]}
