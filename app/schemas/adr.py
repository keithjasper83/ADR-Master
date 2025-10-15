"""ADR schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateDraftRequest(BaseModel):
    """Request to create a new ADR draft."""

    title: str = Field(..., min_length=1, max_length=200)
    problem: str = Field(..., min_length=10)
    context: str = Field(..., min_length=10)
    options: Optional[str] = None
    decision_hint: Optional[str] = None
    references: Optional[list[str]] = None


class CreateDraftResponse(BaseModel):
    """Response for draft creation."""

    draft_path: str
    slug: str
    message: str


class CompileRequest(BaseModel):
    """Request to compile an ADR draft."""

    draft_path: str
    human_notes: Optional[str] = None


class CompileResponse(BaseModel):
    """Response for compilation request."""

    job_id: str
    message: str


class JobStatusResponse(BaseModel):
    """Job status response."""

    job_id: str
    status: str
    logs: list[str]
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class LintRequest(BaseModel):
    """Request to lint an ADR."""

    file_path: str


class LintResult(BaseModel):
    """Lint result."""

    valid: bool
    errors: list[str]
    warnings: list[str]


class PromoteRequest(BaseModel):
    """Request to promote an ADR."""

    draft_path: str
    create_pr: bool = False


class PromoteResponse(BaseModel):
    """Response for promotion."""

    final_path: str
    branch: Optional[str] = None
    pr_url: Optional[str] = None
    message: str


class SyncRequest(BaseModel):
    """Request to sync ADRs."""

    direction: str = Field(..., pattern="^(pull|push|both)$")


class SyncResponse(BaseModel):
    """Response for sync operation."""

    synced_files: list[str]
    conflicts: list[str]
    message: str
