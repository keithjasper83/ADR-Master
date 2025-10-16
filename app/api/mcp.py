"""MCP API endpoints."""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.schemas.mcp import MCPConfig, MCPFeature, MCPProject, ProposalRequest, ProposalResponse
from app.services.mcp_client import MCPClient

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/config", response_model=MCPConfig)
async def get_mcp_config():
    """Get MCP configuration and status."""
    client = MCPClient()
    
    connected = False
    if client.is_configured():
        connected = await client.test_connection()
    
    return MCPConfig(
        mcp_base_url=client.base_url,
        has_token=client.token is not None,
        connected=connected,
    )


@router.get("/projects", response_model=list[MCPProject])
async def get_projects():
    """Get list of projects from MCP."""
    try:
        client = MCPClient()
        projects = await client.get_projects()
        return projects
    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/features", response_model=list[MCPFeature])
async def get_features(project: Optional[str] = None):
    """Get list of features from MCP."""
    try:
        client = MCPClient()
        features = await client.get_features(project)
        return features
    except Exception as e:
        logger.error(f"Failed to get features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/proposals", response_model=ProposalResponse)
async def submit_proposal(request: ProposalRequest):
    """Submit a proposal to MCP."""
    try:
        client = MCPClient()
        proposal_id = await client.submit_proposal(
            request.adr_path, request.feature_ids, request.summary, request.patch_content
        )
        
        if not proposal_id:
            raise HTTPException(status_code=500, detail="Failed to submit proposal")
        
        return ProposalResponse(proposal_id=proposal_id, message="Proposal submitted successfully")
    except Exception as e:
        logger.error(f"Failed to submit proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))
