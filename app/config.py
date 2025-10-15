"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    app_name: str = "ADR-Workbench"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./adr_workbench.db"
    
    # MCP Client
    mcp_endpoint: Optional[str] = None
    mcp_timeout: int = 30
    
    # LLM
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4"
    
    # GitHub
    github_token: Optional[str] = None
    github_default_branch: str = "main"
    
    # ADR Settings
    adr_directory: str = "./docs/adr"
    adr_template: str = "madr"
    
    # Async Processing
    max_concurrent_jobs: int = 5
    job_timeout: int = 300


settings = Settings()
