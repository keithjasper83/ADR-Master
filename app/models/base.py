"""Database models."""
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text

from app.db.database import Base


class CompilationJob(Base):
    """Compilation job model."""

    __tablename__ = "compilation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    draft_path = Column(String, nullable=False)
    status = Column(String, nullable=False)  # queued, running, completed, failed
    logs = Column(JSON, default=list)
    output_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = Column(Text, nullable=True)


class ADRMetadata(Base):
    """ADR metadata model."""

    __tablename__ = "adr_metadata"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, nullable=False)  # Draft, Accepted, Superseded, Deprecated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sha256 = Column(String, nullable=True)
    linked_features = Column(JSON, default=list)  # MCP feature IDs


class Integration(Base):
    """Integration/plugin model."""

    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    hooks = Column(JSON, default=list)  # List of hook names
    config = Column(JSON, default=dict)
    enabled = Column(String, nullable=False, default="true")
    created_at = Column(DateTime, default=datetime.utcnow)


class ActionLog(Base):
    """Action log model."""

    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True, nullable=True)
    user = Column(String, nullable=True)
    action = Column(String, nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sha256 = Column(String, nullable=True)
