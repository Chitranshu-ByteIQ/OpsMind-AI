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


def dashboard() -> None:
    st.title("OpsMind AI")
    st.caption("AI Command Center")
    payload = api_get("/api/dashboard/summary")
    if "_error" in payload:
        st.warning(payload["_error"])
        return
    metrics = payload["metrics"]
    columns = st.columns(5)
    labels = [("open_tasks", "Open Tasks"), ("open_issues", "Issues"), ("open_pull_requests", "PRs"), ("unread_email", "Emails"), ("attention_items", "Attention")]
    for column, (key, label) in zip(columns, labels):
        item = metrics[key]
        column.metric(label, item["value"] if item["available"] else "—")
    st.subheader("AI Executive Summary")
    insights = api_get("/api/dashboard/insights").get("items", [])
    for insight in insights:
        st.info(insight["message"])
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
