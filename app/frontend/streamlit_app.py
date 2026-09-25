"""Streamlit client for the OpsMind FastAPI backend."""
from __future__ import annotations

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
    payload = api_get("/api/dashboard/summary")
    details = api_get("/api/dashboard/details")
    if "_error" in payload:
        st.warning(payload["_error"])
        return
    if "_error" in details:
        st.warning(details["_error"])
        return

    sync = payload.get("sync", {})
    header, refresh_area = st.columns([3, 1])
    with header:
        st.title("OpsMind AI")
        st.caption("Personal Work Command Center")
        st.caption(f"Last synced: {sync.get('last_sync') or 'Never'}")
    with refresh_area:
        st.write("")
        st.write("")
        if st.button("Refresh Data", use_container_width=True):
            with st.spinner("Retrieving and saving work data..."):
                result = api_post("/api/dashboard/refresh")
            if "_error" in result:
                st.error(result["_error"])
            else:
                failed = [name for name, value in result["sources"].items() if value["status"] == "failed"]
                (st.warning if failed else st.success)(f"Refresh complete.{' Failed sources: ' + ', '.join(failed) if failed else ''}")
            st.rerun()

    _render_profile(details.get("profile", {}), payload.get("sources", {}))
    _render_metrics(payload.get("metrics", {}), details)
    _render_distributions(details)
    _render_source_tables(details)
    _render_pending_actions()


def _render_profile(profile: dict[str, Any], sources: dict[str, dict[str, Any]]) -> None:
    st.subheader("Person")
    avatar, identity, accounts = st.columns([1, 2, 3])
    with avatar:
        if profile.get("avatar_url"):
            st.image(profile["avatar_url"], width=92)
        else:
            st.markdown(f"### {profile.get('initials') or 'User'}")
    with identity:
        st.markdown(f"### {profile.get('name') or 'Unknown user'}")
        st.write(profile.get("email") or "Email unavailable")
        st.caption(f"Timezone: {profile.get('timezone') or 'Unavailable'}")
    with accounts:
        account_rows = [
            {"System": "ClickUp", "Account": profile.get("clickup_user_id") or "Unavailable", "Status": _source_status(sources, "clickup")},
            {"System": "GitHub", "Account": profile.get("github_user") or "Unavailable", "Status": _source_status(sources, "github")},
            {"System": "Gmail", "Account": profile.get("gmail_account_hint") or profile.get("email") or "Unavailable", "Status": _source_status(sources, "gmail")},
        ]
        st.dataframe(account_rows, hide_index=True, use_container_width=True)


def _render_metrics(metrics: dict[str, dict[str, Any]], details: dict[str, Any]) -> None:
    st.subheader("Source Snapshot")
    columns = st.columns(6)
    labels = [
        ("ClickUp tasks", details.get("clickup", {}).get("total_tasks")),
        ("Overdue", _metric_value(metrics, "overdue_tasks")),
        ("High priority", _metric_value(metrics, "high_priority_tasks")),
        ("Unread Gmail", _metric_value(metrics, "unread_email")),
        ("Repositories", details.get("github", {}).get("repository_count")),
        ("Open PRs", _metric_value(metrics, "open_pull_requests")),
    ]
    for column, (label, value) in zip(columns, labels):
        column.metric(label, value if value is not None else "-")


def _render_distributions(details: dict[str, Any]) -> None:
    st.subheader("Distribution")
    clickup_tab, gmail_tab, github_tab = st.tabs(["ClickUp", "Gmail", "GitHub"])
    with clickup_tab:
        left, middle, right = st.columns(3)
        _bar_chart(left, "By status", details.get("clickup", {}).get("status_distribution", []))
        _bar_chart(middle, "By priority", details.get("clickup", {}).get("priority_distribution", []))
        _bar_chart(right, "By tag", details.get("clickup", {}).get("tag_distribution", []))
    with gmail_tab:
        left, right = st.columns(2)
        _bar_chart(left, "By sender domain", details.get("gmail", {}).get("sender_distribution", []))
        _bar_chart(right, "By label", details.get("gmail", {}).get("label_distribution", []))
    with github_tab:
        github = details.get("github", {})
        left, middle, right = st.columns(3)
        left.metric("Repositories", github.get("repository_count", 0))
        middle.metric("Open issues", github.get("issue_count", 0))
        right.metric("Open pull requests", github.get("pull_request_count", 0))


def _render_source_tables(details: dict[str, Any]) -> None:
    st.subheader("Structured Details")
    tasks_tab, mail_tab, repo_tab = st.tabs(["ClickUp Tasks", "Gmail Messages", "GitHub Repositories"])
    with tasks_tab:
        rows = [_task_row(task) for task in details.get("clickup", {}).get("tasks", [])]
        st.dataframe(
            rows,
            hide_index=True,
            use_container_width=True,
            column_config={"URL": st.column_config.LinkColumn("URL")},
        )
    with mail_tab:
        rows = [_message_row(message) for message in details.get("gmail", {}).get("messages", [])]
        st.dataframe(rows, hide_index=True, use_container_width=True)
    with repo_tab:
        rows = [_repo_row(repo) for repo in details.get("github", {}).get("repositories", [])]
        st.dataframe(
            rows,
            hide_index=True,
            use_container_width=True,
            column_config={"URL": st.column_config.LinkColumn("URL")},
        )


def _render_pending_actions() -> None:
    pending = api_get("/api/dashboard/actions/pending").get("items", [])
    if not pending:
        return
    st.subheader("Approval Required")
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


def _bar_chart(container: Any, title: str, rows: list[dict[str, Any]]) -> None:
    container.markdown(f"**{title}**")
    if not rows:
        container.caption("No data")
        return
    container.bar_chart(rows, x="label", y="count", height=220)


def _metric_value(metrics: dict[str, dict[str, Any]], key: str) -> int | None:
    item = metrics.get(key, {})
    return item.get("value") if item.get("available", True) else None


def _source_status(sources: dict[str, dict[str, Any]], source: str) -> str:
    status = sources.get(source, {}).get("status") or "not synced"
    count = sources.get(source, {}).get("item_count", 0)
    return f"{status} ({count})"


def _task_row(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "Task": task.get("name"),
        "Status": task.get("status"),
        "Priority": task.get("priority") or "none",
        "Due": _short_date(task.get("due_date")),
        "Updated": _short_date(task.get("date_updated")),
        "Tags": ", ".join(task.get("tags") or []),
        "Assignees": ", ".join(task.get("assignees") or []),
        "URL": task.get("url"),
    }


def _message_row(message: dict[str, Any]) -> dict[str, Any]:
    labels = message.get("labels") or []
    return {
        "Read": "Yes" if message.get("is_read", True) else "No",
        "Sender": message.get("sender"),
        "Subject": message.get("subject"),
        "Received": _short_date(message.get("received_at")),
        "Labels": ", ".join(labels[:4]),
        "Snippet": message.get("snippet"),
    }


def _repo_row(repo: dict[str, Any]) -> dict[str, Any]:
    return {
        "Repository": repo.get("full_name") or repo.get("name"),
        "Private": "Yes" if repo.get("private") else "No",
        "Branch": repo.get("default_branch"),
        "Description": repo.get("description"),
        "URL": repo.get("url"),
    }


def _short_date(value: str | None) -> str | None:
    if not value:
        return None
    return str(value).replace("T", " ").replace("Z", " UTC")[:19]


def chat() -> None:
    st.title("Ask OpsMind")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    prompt = st.chat_input("What needs my attention today?")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Running OpsMind workflow..."):
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
    for item in api_get("/api/dashboard/attention").get("items", []):
        st.write(f"**{item['title']}** - {item['severity']} - {item['source']}")


def agent_activity() -> None:
    st.title("Agent Activity")
    for item in api_get("/api/dashboard/agents").get("items", []):
        st.write(f"{item['name']} - {item['status']}")


st.set_page_config(page_title="OpsMind AI", layout="wide")
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
