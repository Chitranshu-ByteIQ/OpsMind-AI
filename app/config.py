from pydantic_settings import BaseSettings, SettingsConfigDict

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
if not os.path.exists(".env") and os.path.exists(".env "):
    load_dotenv(".env ")


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # LLM
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    groq_model: Optional[str] = os.getenv("GROQ_MODEL")

    # GitHub
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")


    # ClickUp
    clickup_api_token: Optional[str] = os.getenv("CLICKUP_API_TOKEN")

    # Tavily
    tavily_api_key: Optional[str] = os.getenv("TAVILY_API_KEY")

    # Application
    app_name: str = "OpsMind AI"
    environment: str = "development"
    cors_origins: str = "http://localhost:8501,http://127.0.0.1:8501"

    model_config = SettingsConfigDict(
        env_file=(".env", ".env "),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()