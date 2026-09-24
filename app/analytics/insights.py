from app.analytics.aggregator import UnifiedWorkData
from app.analytics.metrics import build_attention


def build_insights(data: UnifiedWorkData) -> list[dict[str, str]]:
    """Factual, deterministic observations; LLM narrative is intentionally separate."""
    attention = build_attention(data)
    if not attention:
        return [{"type": "status", "message": "No deterministic attention signals were found in available sources."}]
    return [{"type": "attention", "message": f"{len(attention)} item(s) meet configured attention signals."}]
