"""MCP client for connecting to external MCP servers."""

from typing import Optional, Dict, Any, List
import httpx
from app.config import settings
import asyncio


class MCPClient:
    """Client for connecting to MCP endpoints."""
    
    def __init__(self, endpoint: Optional[str] = None, timeout: int = 30):
        """Initialize MCP client."""
        self.endpoint = endpoint or settings.mcp_endpoint
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def query_project_data(self, project_id: str) -> Dict[str, Any]:
        """Query project data from MCP endpoint."""
        if not self.endpoint:
            return {
                "success": False,
                "error": "MCP endpoint not configured"
            }
        
        try:
            response = await self.client.post(
                f"{self.endpoint}/query",
                json={
                    "type": "project",
                    "id": project_id
                }
            )
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json()
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def query_features(self, project_id: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Query features data from MCP endpoint."""
        if not self.endpoint:
            return {
                "success": False,
                "error": "MCP endpoint not configured"
            }
        
        try:
            response = await self.client.post(
                f"{self.endpoint}/query",
                json={
                    "type": "features",
                    "project_id": project_id,
                    "filters": filters or {}
                }
            )
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json()
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools from MCP endpoint."""
        if not self.endpoint:
            return {
                "success": False,
                "error": "MCP endpoint not configured"
            }
        
        try:
            response = await self.client.get(f"{self.endpoint}/tools")
            response.raise_for_status()
            return {
                "success": True,
                "tools": response.json()
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a tool on the MCP endpoint."""
        if not self.endpoint:
            return {
                "success": False,
                "error": "MCP endpoint not configured"
            }
        
        try:
            response = await self.client.post(
                f"{self.endpoint}/tools/{tool_name}",
                json=parameters
            )
            response.raise_for_status()
            return {
                "success": True,
                "result": response.json()
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> bool:
        """Check if MCP endpoint is available."""
        if not self.endpoint:
            return False
        
        try:
            response = await self.client.get(f"{self.endpoint}/health")
            return response.status_code == 200
        except Exception:
            return False


# Singleton instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get or create MCP client singleton."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
