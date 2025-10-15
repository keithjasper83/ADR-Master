"""MCP API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.database import get_db
from app.mcp.client import get_mcp_client
from app.mcp.tools import MCPToolExporter

router = APIRouter(prefix="/api/mcp", tags=["mcp"])


class MCPQueryRequest(BaseModel):
    """Request model for MCP query."""
    project_id: str
    query_type: str  # 'project' or 'features'
    filters: Optional[Dict[str, Any]] = None


class MCPToolCallRequest(BaseModel):
    """Request model for MCP tool call."""
    tool_name: str
    parameters: Dict[str, Any]


@router.get("/health")
async def mcp_health():
    """Check MCP endpoint health."""
    mcp_client = get_mcp_client()
    is_healthy = await mcp_client.health_check()
    
    return {
        "healthy": is_healthy,
        "endpoint": mcp_client.endpoint
    }


@router.get("/tools")
async def list_mcp_tools():
    """List available MCP tools from endpoint."""
    mcp_client = get_mcp_client()
    result = await mcp_client.list_tools()
    
    if not result.get("success"):
        raise HTTPException(status_code=503, detail=result.get("error"))
    
    return result


@router.post("/query")
async def query_mcp(request: MCPQueryRequest):
    """Query data from MCP endpoint."""
    mcp_client = get_mcp_client()
    
    if request.query_type == "project":
        result = await mcp_client.query_project_data(request.project_id)
    elif request.query_type == "features":
        result = await mcp_client.query_features(request.project_id, request.filters)
    else:
        raise HTTPException(status_code=400, detail="Invalid query type")
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/tools/call")
async def call_mcp_tool(request: MCPToolCallRequest):
    """Call a tool on the MCP endpoint."""
    mcp_client = get_mcp_client()
    result = await mcp_client.call_tool(request.tool_name, request.parameters)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/exports")
async def get_exported_tools():
    """Get tools exported by ADR-Workbench."""
    exporter = MCPToolExporter()
    return {
        "tools": exporter.get_tool_definitions()
    }


@router.post("/exports/{tool_name}")
async def execute_exported_tool(
    tool_name: str,
    parameters: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Execute an exported ADR-Workbench tool."""
    exporter = MCPToolExporter()
    result = await exporter.execute_tool(tool_name, db, **parameters)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result
