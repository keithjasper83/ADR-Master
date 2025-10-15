"""ADR API routes."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel
from app.database import get_db
from app.models.adr import ADR, ADRStatus
from app.services.adr_service import ADRService
from app.services.lint_service import LintService
from app.services.llm_service import LLMService
from app.services.github_service import GitHubService
from app.plugins.manager import get_plugin_manager

router = APIRouter(prefix="/api/adrs", tags=["adrs"])


class ADRCreate(BaseModel):
    """Request model for creating ADR."""
    title: str
    status: Optional[ADRStatus] = ADRStatus.DRAFT
    context: Optional[str] = ""
    decision: Optional[str] = ""
    consequences: Optional[str] = ""
    options_considered: Optional[str] = None
    pros_cons: Optional[str] = None
    links: Optional[str] = None


class ADRUpdate(BaseModel):
    """Request model for updating ADR."""
    title: Optional[str] = None
    status: Optional[ADRStatus] = None
    context: Optional[str] = None
    decision: Optional[str] = None
    consequences: Optional[str] = None
    options_considered: Optional[str] = None
    pros_cons: Optional[str] = None
    links: Optional[str] = None


class LLMCompileRequest(BaseModel):
    """Request model for LLM compilation."""
    context: str
    requirements: str
    provider: Optional[str] = None
    model: Optional[str] = None


class GitHubPRRequest(BaseModel):
    """Request model for GitHub PR creation."""
    repo_name: str
    base_branch: Optional[str] = None


@router.post("/", status_code=201)
async def create_adr(
    adr_data: ADRCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new ADR."""
    # Execute plugin hooks
    plugin_manager = get_plugin_manager()
    modified_data = await plugin_manager.execute_hook(
        "on_adr_create",
        adr_data=adr_data.model_dump(),
        default_value=adr_data.model_dump()
    )
    
    adr = await ADRService.create_adr(
        db,
        title=modified_data.get("title"),
        status=modified_data.get("status", ADRStatus.DRAFT),
        context=modified_data.get("context", ""),
        decision=modified_data.get("decision", ""),
        consequences=modified_data.get("consequences", "")
    )
    
    # Update additional fields
    if modified_data.get("options_considered"):
        adr.options_considered = modified_data["options_considered"]
    if modified_data.get("pros_cons"):
        adr.pros_cons = modified_data["pros_cons"]
    if modified_data.get("links"):
        adr.links = modified_data["links"]
    
    await db.commit()
    
    return adr.to_dict()


@router.get("/")
async def list_adrs(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List ADRs with optional filtering."""
    status_filter = ADRStatus(status) if status else None
    adrs = await ADRService.list_adrs(db, status=status_filter, limit=limit, offset=offset)
    return [adr.to_dict() for adr in adrs]


@router.get("/{adr_id}")
async def get_adr(
    adr_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific ADR."""
    adr = await ADRService.get_adr(db, adr_id)
    if not adr:
        raise HTTPException(status_code=404, detail="ADR not found")
    return adr.to_dict()


@router.put("/{adr_id}")
async def update_adr(
    adr_id: int,
    adr_data: ADRUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an ADR."""
    # Execute plugin hooks
    plugin_manager = get_plugin_manager()
    modified_data = await plugin_manager.execute_hook(
        "on_adr_update",
        adr_id=adr_id,
        adr_data=adr_data.model_dump(exclude_none=True),
        default_value=adr_data.model_dump(exclude_none=True)
    )
    
    adr = await ADRService.update_adr(db, adr_id, **modified_data)
    if not adr:
        raise HTTPException(status_code=404, detail="ADR not found")
    
    await db.commit()
    return adr.to_dict()


@router.delete("/{adr_id}")
async def delete_adr(
    adr_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an ADR."""
    success = await ADRService.delete_adr(db, adr_id)
    if not success:
        raise HTTPException(status_code=404, detail="ADR not found")
    await db.commit()
    return {"success": True}


@router.get("/{adr_id}/markdown")
async def get_adr_markdown(
    adr_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get ADR as MADR markdown."""
    adr = await ADRService.get_adr(db, adr_id)
    if not adr:
        raise HTTPException(status_code=404, detail="ADR not found")
    
    markdown = ADRService.format_as_madr(adr)
    return {"markdown": markdown}


@router.post("/{adr_id}/lint")
async def lint_adr(
    adr_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Lint an ADR for issues."""
    adr = await ADRService.get_adr(db, adr_id)
    if not adr:
        raise HTTPException(status_code=404, detail="ADR not found")
    
    issues = LintService.lint_adr(adr)
    
    # Execute plugin hooks
    plugin_manager = get_plugin_manager()
    issues = await plugin_manager.execute_hook(
        "on_adr_lint",
        adr_id=adr_id,
        issues=[i.to_dict() for i in issues],
        default_value=[i.to_dict() for i in issues]
    )
    
    summary = LintService.get_lint_summary([LintService.LintIssue(**i) for i in issues])
    return summary


@router.post("/compile")
async def compile_adr_with_llm(
    request: LLMCompileRequest
):
    """Compile an ADR using LLM."""
    result = await LLMService.compile_adr(
        context=request.context,
        requirements=request.requirements,
        provider=request.provider,
        model=request.model
    )
    return result


@router.post("/{adr_id}/github-pr")
async def create_github_pr(
    adr_id: int,
    request: GitHubPRRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a GitHub PR for an ADR."""
    adr = await ADRService.get_adr(db, adr_id)
    if not adr:
        raise HTTPException(status_code=404, detail="ADR not found")
    
    github_service = GitHubService()
    result = await github_service.create_pr_for_adr(
        repo_name=request.repo_name,
        adr=adr,
        base_branch=request.base_branch
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
