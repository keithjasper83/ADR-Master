"""ADR database model."""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class ADRStatus(str, enum.Enum):
    """ADR status enumeration."""
    DRAFT = "draft"
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


class ADR(Base):
    """ADR (Architecture Decision Record) model."""
    
    __tablename__ = "adrs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum(ADRStatus, native_enum=False),
        nullable=False,
        default=ADRStatus.DRAFT
    )
    
    # MADR fields
    context: Mapped[str] = mapped_column(Text, nullable=True)
    decision: Mapped[str] = mapped_column(Text, nullable=True)
    consequences: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Additional fields
    options_considered: Mapped[str] = mapped_column(Text, nullable=True)
    pros_cons: Mapped[str] = mapped_column(Text, nullable=True)
    links: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Git integration
    file_path: Mapped[str] = mapped_column(String(500), nullable=True)
    git_sha: Mapped[str] = mapped_column(String(40), nullable=True)
    
    def to_dict(self):
        """Convert ADR to dictionary."""
        return {
            "id": self.id,
            "number": self.number,
            "title": self.title,
            "status": self.status,
            "context": self.context,
            "decision": self.decision,
            "consequences": self.consequences,
            "options_considered": self.options_considered,
            "pros_cons": self.pros_cons,
            "links": self.links,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "file_path": self.file_path,
            "git_sha": self.git_sha
        }
