from app.agents.runtime import get_llm


def test_llm_factory_requires_configuration(monkeypatch):
    monkeypatch.setattr("app.agents.runtime.settings.groq_api_key", None)
    monkeypatch.setattr("app.agents.runtime.settings.groq_model", None)
    try:
        get_llm()
    except RuntimeError as exc:
        assert "LLM configuration" in str(exc)
    else:
        raise AssertionError("Missing configuration should not create an LLM")
