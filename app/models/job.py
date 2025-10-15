"""Job tracking database model."""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class JobStatus(str, enum.Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    """Job type enumeration."""
    LLM_COMPILE = "llm_compile"
    GITHUB_PR = "github_pr"
    LINT = "lint"
    SYNC = "sync"
    MCP_QUERY = "mcp_query"


class Job(Base):
    """Job tracking model for async operations."""
    
    __tablename__ = "jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_type: Mapped[str] = mapped_column(
        SQLEnum(JobType, native_enum=False),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(JobStatus, native_enum=False),
        nullable=False,
        default=JobStatus.PENDING
    )
    
    # Job details
    adr_id: Mapped[int] = mapped_column(Integer, nullable=True)
    input_data: Mapped[str] = mapped_column(Text, nullable=True)
    output_data: Mapped[str] = mapped_column(Text, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert Job to dictionary."""
        return {
            "id": self.id,
            "job_type": self.job_type,
            "status": self.status,
            "adr_id": self.adr_id,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
