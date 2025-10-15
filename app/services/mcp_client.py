"""MCP client service."""
import logging
from typing import Optional

import httpx

from app.config import get_settings
from app.schemas.mcp import MCPFeature, MCPProject

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP REST client."""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.mcp_base_url
        self.token = self.settings.mcp_token

    def is_configured(self) -> bool:
        """Check if MCP is configured."""
        return self.base_url is not None

    async def test_connection(self) -> bool:
        """Test MCP connection."""
        if not self.is_configured():
            return False
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers = {}
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                
                response = await client.get(f"{self.base_url}/health", headers=headers)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"MCP connection test failed: {e}")
            return False

    async def get_projects(self) -> list[MCPProject]:
        """Get list of projects from MCP."""
        if not self.is_configured():
            return []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {}
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                
                response = await client.get(f"{self.base_url}/projects", headers=headers)
                response.raise_for_status()
                
                data = response.json()
                return [MCPProject(**project) for project in data.get("projects", [])]
        except Exception as e:
            logger.error(f"Failed to get projects from MCP: {e}")
            return []

    async def get_features(self, project_id: Optional[str] = None) -> list[MCPFeature]:
        """Get list of features from MCP."""
        if not self.is_configured():
            return []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {}
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                
                params = {}
                if project_id:
                    params["project"] = project_id
                
                response = await client.get(
                    f"{self.base_url}/features", headers=headers, params=params
                )
                response.raise_for_status()
                
                data = response.json()
                return [MCPFeature(**feature) for feature in data.get("features", [])]
        except Exception as e:
            logger.error(f"Failed to get features from MCP: {e}")
            return []

    async def submit_proposal(
        self, adr_path: str, feature_ids: list[str], summary: str, patch_content: Optional[str]
    ) -> Optional[str]:
        """Submit a proposal to MCP."""
        if not self.is_configured():
            raise ValueError("MCP not configured")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {}
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                
                payload = {
                    "adr_path": adr_path,
                    "feature_ids": feature_ids,
                    "summary": summary,
                    "patch_content": patch_content,
                }
                
                response = await client.post(
                    f"{self.base_url}/proposals", headers=headers, json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                return data.get("proposal_id")
        except Exception as e:
            logger.error(f"Failed to submit proposal to MCP: {e}")
            raise
