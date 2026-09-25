"""Streamlit client for the OpsMind FastAPI backend."""
import os
from typing import Any

import requests
import streamlit as st


API_URL = os.getenv("OPSMIND_API_URL", "http://127.0.0.1:8000").rstrip("/")


def api_get(path: str) -> dict[str, Any]:
    try:
        response = requests.get(f"{API_URL}{path}", timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"_error": "Backend unavailable or source data could not be loaded.", "detail": str(exc)}


def api_chat(message: str) -> dict[str, Any]:
    try:
        response = requests.post(f"{API_URL}/chat", json={"message": message}, timeout=90)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {"success": False, "message": "OpsMind could not reach the backend."}


def api_post(path: str) -> dict[str, Any]:
    try:
        response = requests.post(f"{API_URL}{path}", timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"_error": "Refresh could not complete.", "detail": str(exc)}


def dashboard() -> None:
    st.title("OpsMind AI")
    st.caption("Personal Work Command Center")
    payload = api_get("/api/dashboard/summary")
    if "_error" in payload:
        st.warning(payload["_error"])
        return
    sync = payload.get("sync", {})
    top_left, top_right = st.columns([3, 1])
    top_left.caption(f"Last synced: {sync.get('last_sync') or 'Never'}")
    if top_right.button("🔄 Refresh Data", use_container_width=True):
        with st.spinner("Retrieving and saving work data…"):
            result = api_post("/api/dashboard/refresh")
        if "_error" in result:
            st.error(result["_error"])
        else:
            failed = [name for name, value in result["sources"].items() if value["status"] == "failed"]
            (st.warning if failed else st.success)(f"Refresh complete.{' Failed sources: ' + ', '.join(failed) if failed else ''}")
        st.rerun()
    metrics = payload["metrics"]
    columns = st.columns(4)
    labels = [("unread_email", "Unread Gmail"), ("open_pull_requests", "Open PRs"), ("overdue_tasks", "Overdue Tasks"), ("high_priority_tasks", "High Priority")]
    for column, (key, label) in zip(columns, labels):
        item = metrics[key]
        column.metric(label, item["value"] if item["available"] else "—")
    st.subheader("Work overview")
    insights = api_get("/api/dashboard/insights").get("items", [])
    for insight in insights:
        st.info(insight["message"])
    with st.expander("Data status", expanded=False):
        for source, status in payload.get("sources", {}).items():
            st.write(f"{source.title()}: {status.get('status', 'not synced')} · {status.get('item_count', 0)} items")
            if status.get("last_error"):
                st.warning(f"{source.title()}: {status['last_error']} (previous data preserved: {status.get('preserved_previous_data', False)})")
    pending = api_get("/api/dashboard/actions/pending").get("items", [])
    if pending:
        st.subheader("Approval required")
        for action in pending:
            st.write(f"Create ClickUp task **{action['proposed']['name']}** in list `{action['target']['list_id']}`")
            approve, reject = st.columns(2)
            if approve.button("Approve", key=f"approve-{action['id']}"):
                result = api_post(f"/api/dashboard/actions/{action['id']}/approve")
                st.success("Action completed." if result.get("status") == "completed" else f"Action result: {result.get('status', 'unknown')}")
                st.rerun()
            if reject.button("Reject", key=f"reject-{action['id']}"):
                api_post(f"/api/dashboard/actions/{action['id']}/reject")
                st.info("Action rejected.")
                st.rerun()
    left, right = st.columns(2)
    with left:
        st.subheader("Needs Attention")
        for item in api_get("/api/dashboard/attention").get("items", []):
            st.write(f"• **{item['title']}** — {item['kind'].replace('_', ' ')}")
    with right:
        st.subheader("Activity")
        for item in api_get("/api/dashboard/activity").get("items", [])[:8]:
            st.write(f"• {item['source']}: {item['title']}")


def chat() -> None:
    st.title("Ask OpsMind")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.write(message["content"])
    prompt = st.chat_input("What needs my attention today?")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Running OpsMind workflow…"):
                answer = api_chat(prompt)
            st.write(answer["message"])
            data = answer.get("data", {})
            if data.get("plan"):
                with st.expander("Workflow activity"):
                    st.write("Selected agent(s):", answer.get("agent", "unknown"))
                    st.write("Plan:", data["plan"])
        st.session_state.messages.append({"role": "assistant", "content": answer["message"]})


def attention() -> None:
    st.title("Needs Attention")
    for item in api_get("/api/dashboard/attention").get("items", []): st.write(f"**{item['title']}** · {item['severity']} · {item['source']}")


def agent_activity() -> None:
    st.title("Agent Activity")
    for item in api_get("/api/dashboard/agents").get("items", []): st.write(f"✓ {item['name']} — {item['status']}")


st.set_page_config(page_title="OpsMind AI", page_icon="◉", layout="wide")
with st.sidebar:
    st.title("OpsMind AI")
    page = st.radio("Navigate", ["Dashboard", "Agent Chat", "Needs Attention", "Agent Activity"])
    st.divider()
    st.caption("Connected Systems")
    health = api_get("/health")
    backend_state = "Connected" if "_error" not in health else "Unavailable"
    for system in ("GitHub", "ClickUp", "Gmail", "Research"):
        st.write(f"{system}: {backend_state}")

{"Dashboard": dashboard, "Agent Chat": chat, "Needs Attention": attention, "Agent Activity": agent_activity}[page]()
