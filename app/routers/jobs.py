"""Job API routes."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.job import Job, JobStatus, JobType
from app.services.job_service import JobService
from app.services.llm_service import LLMService
from app.services.github_service import GitHubService
from app.services.adr_service import ADRService
import json

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class JobCreate(BaseModel):
    """Request model for creating job."""
    job_type: JobType
    adr_id: Optional[int] = None
    input_data: Optional[dict] = None


async def process_llm_job(job_id: int, db: AsyncSession):
    """Process LLM compilation job."""
    job = await JobService.get_job(db, job_id)
    if not job:
        return
    
    await JobService.update_job_status(db, job_id, JobStatus.RUNNING)
    await db.commit()
    
    try:
        input_data = json.loads(job.input_data) if job.input_data else {}
        result = await LLMService.compile_adr(
            context=input_data.get("context", ""),
            requirements=input_data.get("requirements", ""),
            provider=input_data.get("provider"),
            model=input_data.get("model")
        )
        
        await JobService.update_job_status(
            db,
            job_id,
            JobStatus.COMPLETED if result.get("success") else JobStatus.FAILED,
            output_data=json.dumps(result),
            error_message=result.get("error")
        )
    except Exception as e:
        await JobService.update_job_status(
            db,
            job_id,
            JobStatus.FAILED,
            error_message=str(e)
        )
    finally:
        await db.commit()


async def process_github_job(job_id: int, db: AsyncSession):
    """Process GitHub PR job."""
    job = await JobService.get_job(db, job_id)
    if not job:
        return
    
    await JobService.update_job_status(db, job_id, JobStatus.RUNNING)
    await db.commit()
    
    try:
        input_data = json.loads(job.input_data) if job.input_data else {}
        adr = await ADRService.get_adr(db, job.adr_id)
        
        if not adr:
            raise Exception("ADR not found")
        
        github_service = GitHubService()
        result = await github_service.create_pr_for_adr(
            repo_name=input_data.get("repo_name"),
            adr=adr,
            base_branch=input_data.get("base_branch")
        )
        
        await JobService.update_job_status(
            db,
            job_id,
            JobStatus.COMPLETED if result.get("success") else JobStatus.FAILED,
            output_data=json.dumps(result),
            error_message=result.get("error")
        )
    except Exception as e:
        await JobService.update_job_status(
            db,
            job_id,
            JobStatus.FAILED,
            error_message=str(e)
        )
    finally:
        await db.commit()


@router.post("/", status_code=201)
async def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create a new async job."""
    input_json = json.dumps(job_data.input_data) if job_data.input_data else None
    
    job = await JobService.create_job(
        db,
        job_type=job_data.job_type,
        adr_id=job_data.adr_id,
        input_data=input_json
    )
    await db.commit()
    
    # Schedule background processing
    if job_data.job_type == JobType.LLM_COMPILE:
        background_tasks.add_task(process_llm_job, job.id, db)
    elif job_data.job_type == JobType.GITHUB_PR:
        background_tasks.add_task(process_github_job, job.id, db)
    
    return job.to_dict()


@router.get("/")
async def list_jobs(
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List jobs with optional filtering."""
    status_filter = JobStatus(status) if status else None
    type_filter = JobType(job_type) if job_type else None
    
    jobs = await JobService.list_jobs(
        db,
        status=status_filter,
        job_type=type_filter,
        limit=limit,
        offset=offset
    )
    return [job.to_dict() for job in jobs]


@router.get("/{job_id}")
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific job."""
    job = await JobService.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.to_dict()


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a job."""
    success = await JobService.cancel_job(db, job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found or already completed")
    await db.commit()
    return {"success": True}
