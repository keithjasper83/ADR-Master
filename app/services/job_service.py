"""Service for job management."""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job, JobStatus, JobType
from datetime import datetime
import asyncio


class JobService:
    """Service for managing async jobs."""
    
    @staticmethod
    async def create_job(
        db: AsyncSession,
        job_type: JobType,
        adr_id: Optional[int] = None,
        input_data: Optional[str] = None
    ) -> Job:
        """Create a new job."""
        job = Job(
            job_type=job_type,
            status=JobStatus.PENDING,
            adr_id=adr_id,
            input_data=input_data
        )
        db.add(job)
        await db.flush()
        return job
    
    @staticmethod
    async def get_job(db: AsyncSession, job_id: int) -> Optional[Job]:
        """Get job by ID."""
        result = await db.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_jobs(
        db: AsyncSession,
        status: Optional[JobStatus] = None,
        job_type: Optional[JobType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Job]:
        """List jobs with optional filtering."""
        query = select(Job)
        if status:
            query = query.where(Job.status == status)
        if job_type:
            query = query.where(Job.job_type == job_type)
        query = query.order_by(Job.created_at.desc()).limit(limit).offset(offset)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_job_status(
        db: AsyncSession,
        job_id: int,
        status: JobStatus,
        output_data: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[Job]:
        """Update job status."""
        job = await JobService.get_job(db, job_id)
        if not job:
            return None
        
        job.status = status
        
        if status == JobStatus.RUNNING and not job.started_at:
            job.started_at = datetime.utcnow()
        
        if status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            job.completed_at = datetime.utcnow()
        
        if output_data:
            job.output_data = output_data
        
        if error_message:
            job.error_message = error_message
        
        await db.flush()
        return job
    
    @staticmethod
    async def cancel_job(db: AsyncSession, job_id: int) -> bool:
        """Cancel a job."""
        job = await JobService.get_job(db, job_id)
        if not job or job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            return False
        
        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.utcnow()
        await db.flush()
        return True
    
    @staticmethod
    async def cleanup_old_jobs(
        db: AsyncSession,
        days: int = 30
    ) -> int:
        """Clean up completed jobs older than specified days."""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(Job).where(
                Job.status.in_([JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]),
                Job.completed_at < cutoff_date
            )
        )
        jobs = result.scalars().all()
        
        for job in jobs:
            await db.delete(job)
        
        await db.flush()
        return len(jobs)
