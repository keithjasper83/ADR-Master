"""Database models."""
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Table
from sqlalchemy.orm import relationship

from app.db.database import Base

# Association table for many-to-many relationship between users and projects
project_members = Table(
    'project_members',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('role', String, nullable=False, default='member'),  # owner, member, viewer
    Column('joined_at', DateTime, default=datetime.utcnow)
)


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Optional for API key only users
    api_key = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = relationship('Project', secondary=project_members, back_populates='members')
    owned_projects = relationship('Project', back_populates='owner', foreign_keys='Project.owner_id')


class Project(Base):
    """Project model."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    root_path = Column(String, nullable=False)
    adr_path = Column(String, nullable=False)
    draft_path = Column(String, nullable=False)
    visibility = Column(String, nullable=False, default='private')  # private, public
    project_secret = Column(String, unique=True, index=True, nullable=False)  # For invitations
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # GitHub repository info (optional)
    repo_provider = Column(String, nullable=True)  # github
    repo_owner = Column(String, nullable=True)
    repo_name = Column(String, nullable=True)
    repo_branch = Column(String, nullable=True, default='main')
    repo_credentials = Column(Text, nullable=True)  # Encrypted

    # Relationships
    owner = relationship('User', back_populates='owned_projects', foreign_keys=[owner_id])
    members = relationship('User', secondary=project_members, back_populates='projects')
    adrs = relationship('ADRMetadata', back_populates='project')


class CompilationJob(Base):
    """Compilation job model."""

    __tablename__ = "compilation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
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
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    file_path = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    slug = Column(String, index=True, nullable=False)
    status = Column(String, nullable=False)  # Draft, Proposed, Accepted, Rejected, Superseded
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sha256 = Column(String, nullable=True)
    linked_features = Column(JSON, default=list)  # MCP feature IDs

    # Relationships
    project = relationship('Project', back_populates='adrs')


class ProjectInvitation(Base):
    """Project invitation model."""

    __tablename__ = "project_invitations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    inviter_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False, default='member')
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Integration(Base):
    """Integration/plugin model."""

    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)  # Null = global
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    hooks = Column(JSON, default=list)  # List of hook names
    config = Column(JSON, default=dict)
    enabled = Column(String, nullable=False, default="true")
    created_at = Column(DateTime, default=datetime.utcnow)


class ActionLog(Base):
    """Action log model."""

    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    job_id = Column(String, index=True, nullable=True)
    action = Column(String, nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sha256 = Column(String, nullable=True)
