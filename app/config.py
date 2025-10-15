"""Application configuration."""
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    app_name: str = "ADR-Master"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Paths
    workdir: Path = Path.cwd()
    adr_dir: Path = Path.cwd() / "ADR"
    adr_draft_dir: Path = Path.cwd() / "ADR" / "Draft"
    log_dir: Path = Path.cwd() / "_logs"

    # Database
    database_url: str = "sqlite:///./adr_master.db"

    # MCP Integration
    mcp_base_url: Optional[str] = None
    mcp_token: Optional[str] = None

    # LLM
    llm_endpoint: str = "http://localhost:11434/api/generate"

    # GitHub
    github_token: Optional[str] = None

    # Security
    csrf_secret: str = "change-me-in-production"
    cors_enabled: bool = False
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    log_level: str = "INFO"

    def __init__(self, **kwargs):  # type: ignore
        super().__init__(**kwargs)
        # Ensure directories exist
        self.adr_dir.mkdir(parents=True, exist_ok=True)
        self.adr_draft_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
