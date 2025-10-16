"""MCP schemas."""
from typing import Any, Optional

from pydantic import BaseModel


class MCPConfig(BaseModel):
    """MCP configuration."""

    mcp_base_url: Optional[str]
    has_token: bool
    connected: bool


class MCPProject(BaseModel):
    """MCP project."""

    id: str
    name: str
    description: Optional[str] = None
    metadata: dict[str, Any] = {}


class MCPFeature(BaseModel):
    """MCP feature."""

    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    tags: list[str] = []
    metadata: dict[str, Any] = {}


class ProposalRequest(BaseModel):
    """Proposal request."""

    adr_path: str
    feature_ids: list[str]
    summary: str
    patch_content: Optional[str] = None


class ProposalResponse(BaseModel):
    """Proposal response."""

    proposal_id: str
    message: str
