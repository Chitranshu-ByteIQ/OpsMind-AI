from fastapi import APIRouter

from app.analytics.aggregator import collect_dashboard_data
from app.analytics.insights import build_insights
from app.analytics.metrics import build_activity, build_attention, build_summary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

def _data(): return collect_dashboard_data()

@router.get("/summary")
def summary():
    data = _data()
    return {"metrics": build_summary(data), "connections": data.availability}

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
