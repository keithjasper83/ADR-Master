"""ADR API endpoints."""
import asyncio
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.adr import (
    CompileRequest,
    CompileResponse,
    CreateDraftRequest,
    CreateDraftResponse,
    JobStatusResponse,
    LintRequest,
    LintResult,
    PromoteRequest,
    PromoteResponse,
    SyncRequest,
    SyncResponse,
)
from app.services.adr_service import ADRService
from app.services.github_service import GitHubService
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/draft", response_model=CreateDraftResponse)
async def create_draft(request: CreateDraftRequest, db: Session = Depends(get_db)):
    """Create a new ADR draft."""
    try:
        service = ADRService(db)
        draft_path, slug = service.create_draft(request)
        
        return CreateDraftResponse(
            draft_path=draft_path, slug=slug, message="Draft created successfully"
        )
    except Exception as e:
        logger.error(f"Failed to create draft: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compile", response_model=CompileResponse)
async def compile_draft(
    request: CompileRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """Compile an ADR draft using LLM (async)."""
    try:
        service = ADRService(db)
        job_id = service.create_compilation_job(request.draft_path, request.human_notes)
        
        # Start background compilation
        llm_service = LLMService(db)
        background_tasks.add_task(llm_service.compile_adr, job_id)
        
        return CompileResponse(job_id=job_id, message="Compilation job started")
    except Exception as e:
        logger.error(f"Failed to start compilation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Get compilation job status."""
    service = ADRService(db)
    job = service.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        logs=job.logs,
        output_path=job.output_path,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.post("/lint", response_model=LintResult)
async def lint_adr(request: LintRequest, db: Session = Depends(get_db)):
    """Lint an ADR file."""
    try:
        service = ADRService(db)
        result = service.lint_adr(request.file_path)
        return result
    except Exception as e:
        logger.error(f"Failed to lint ADR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/promote", response_model=PromoteResponse)
async def promote_adr(request: PromoteRequest, db: Session = Depends(get_db)):
    """Promote an ADR from draft to final."""
    try:
        service = ADRService(db)
        final_path = service.promote_adr(request.draft_path)
        
        branch = None
        pr_url = None
        
        if request.create_pr:
            github_service = GitHubService()
            
            # Extract slug from path
            from pathlib import Path
            
            slug = Path(final_path).stem
            
            # Create branch
            branch = github_service.create_adr_branch(slug)
            
            # Commit and push
            if branch:
                message = f"Add ADR: {slug}"
                github_service.commit_and_push([final_path], message)
                
                # Note: Actual PR creation would require GitHub API
                pr_url = f"https://github.com/YOUR_ORG/YOUR_REPO/compare/{branch}"
        
        return PromoteResponse(
            final_path=final_path,
            branch=branch,
            pr_url=pr_url,
            message="ADR promoted successfully",
        )
    except Exception as e:
        logger.error(f"Failed to promote ADR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync", response_model=SyncResponse)
async def sync_adrs(request: SyncRequest):
    """Sync ADR directories with remote."""
    try:
        github_service = GitHubService()
        synced_files, conflicts = github_service.sync_adr_directories(request.direction)
        
        return SyncResponse(
            synced_files=synced_files,
            conflicts=conflicts,
            message="Sync completed" if not conflicts else "Sync completed with conflicts",
        )
    except Exception as e:
        logger.error(f"Failed to sync ADRs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
