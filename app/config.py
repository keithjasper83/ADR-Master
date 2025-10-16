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
    app_version: str = "0.2.0"
    debug: bool = False
    environment: str = "production"  # development, production

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    base_url: str = "http://localhost:8000"

    # Paths
    workdir: Path = Path.cwd()
    log_dir: Path = Path.cwd() / "_logs"
    data_dir: Path = Path.cwd() / "data"  # For project data

    # Database
    database_url: str = "sqlite:///./adr_master.db"

    # Authentication & Security
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    invitation_expiration_days: int = 7
    
    # Session
    session_cookie_name: str = "adr_session"
    session_cookie_secure: bool = True
    session_cookie_samesite: str = "lax"

    # MCP Integration (optional - online service)
    mcp_base_url: Optional[str] = None
    mcp_token: Optional[str] = None

    # LLM (optional - online service)
    llm_endpoint: str = "http://localhost:11434/api/generate"

    # Security
    cors_enabled: bool = True
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    log_level: str = "INFO"

    def __init__(self, **kwargs):  # type: ignore
        super().__init__(**kwargs)
        # Ensure directories exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
