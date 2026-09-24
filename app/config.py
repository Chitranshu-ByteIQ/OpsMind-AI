from pydantic_settings import BaseSettings, SettingsConfigDict

import os 
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # LLM
    groq_api_key: str = os.getenv('GROQ_API_KEY')
    groq_model: str = os.getenv('GROQ_MODEL')

    # GitHub
    github_token: str = os.getenv('GITHUB_TOKEN')


    # ClickUp
    clickup_api_token: str = os.getenv('CLICKUP_API_TOKEN')

    # Tavily
    tavily_api_key: str = os.getenv('TAVILY_API_KEY')

    # Application
    app_name: str = "OpsMind AI"
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()