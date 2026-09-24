from pathlib import Path


def test_streamlit_frontend_has_backend_contract():
    source = Path("app/frontend/streamlit_app.py").read_text(encoding="utf-8")
    assert "streamlit" in source
    assert "/chat" in source
    assert "/api/dashboard/summary" in source
