"""Projects API endpoints."""
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.utils import generate_invitation_token, generate_project_secret
from app.config import get_settings
from app.db.database import get_db
from app.models.base import Project, ProjectInvitation, User, project_members

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class ProjectCreate(BaseModel):
    """Create project request."""

    name: str
    description: Optional[str] = None
    root_path: str
    visibility: str = "private"


class ProjectResponse(BaseModel):
    """Project response."""

    id: int
    name: str
    slug: str
    description: Optional[str]
    root_path: str
    adr_path: str
    draft_path: str
    visibility: str
    project_secret: str
    owner_id: int
    member_count: int

    class Config:
        from_attributes = True


class InviteRequest(BaseModel):
    """Invitation request."""

    email: str
    role: str = "member"


class JoinRequest(BaseModel):
    """Join project request."""

    project_secret: str


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all projects accessible to current user."""
    # Get all projects where user is owner or member
    projects = (
        db.query(Project)
        .join(project_members, Project.id == project_members.c.project_id, isouter=True)
        .filter(
            (Project.owner_id == current_user.id) | (project_members.c.user_id == current_user.id)
        )
        .distinct()
        .all()
    )
    
    result = []
    for project in projects:
        result.append(
            ProjectResponse(
                id=project.id,
                name=project.name,
                slug=project.slug,
                description=project.description,
                root_path=project.root_path,
                adr_path=project.adr_path,
                draft_path=project.draft_path,
                visibility=project.visibility,
                project_secret=project.project_secret,
                owner_id=project.owner_id,
                member_count=len(project.members),
            )
        )
    
    return result


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new project."""
    # Generate slug from name
    slug = request.name.lower().replace(" ", "-").replace("_", "-")
    
    # Check if slug already exists
    existing = db.query(Project).filter(Project.slug == slug).first()
    if existing:
        slug = f"{slug}-{current_user.id}"
    
    # Create project directories
    root_path = Path(request.root_path)
    adr_path = root_path / "ADR"
    draft_path = adr_path / "Draft"
    
    adr_path.mkdir(parents=True, exist_ok=True)
    draft_path.mkdir(parents=True, exist_ok=True)
    
    # Create project
    project = Project(
        name=request.name,
        slug=slug,
        description=request.description,
        root_path=str(root_path),
        adr_path=str(adr_path),
        draft_path=str(draft_path),
        visibility=request.visibility,
        project_secret=generate_project_secret(),
        owner_id=current_user.id,
    )
    
    db.add(project)
    db.flush()
    
    # Add owner as member with owner role
    stmt = project_members.insert().values(
        user_id=current_user.id, project_id=project.id, role="owner"
    )
    db.execute(stmt)
    
    db.commit()
    db.refresh(project)
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        slug=project.slug,
        description=project.description,
        root_path=project.root_path,
        adr_path=project.adr_path,
        draft_path=project.draft_path,
        visibility=project.visibility,
        project_secret=project.project_secret,
        owner_id=project.owner_id,
        member_count=1,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get project details."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    is_member = (
        db.query(project_members)
        .filter(
            project_members.c.project_id == project_id,
            project_members.c.user_id == current_user.id,
        )
        .first()
    )
    
    if project.owner_id != current_user.id and not is_member:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        slug=project.slug,
        description=project.description,
        root_path=project.root_path,
        adr_path=project.adr_path,
        draft_path=project.draft_path,
        visibility=project.visibility,
        project_secret=project.project_secret,
        owner_id=project.owner_id,
        member_count=len(project.members),
    )


@router.post("/{project_id}/invite")
async def invite_user(
    project_id: int,
    request: InviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Invite a user to the project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Only owner can invite
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only project owner can invite users")
    
    # Create invitation
    invitation = ProjectInvitation(
        project_id=project_id,
        inviter_id=current_user.id,
        email=request.email,
        role=request.role,
        token=generate_invitation_token(),
        expires_at=datetime.utcnow() + timedelta(days=settings.invitation_expiration_days),
    )
    
    db.add(invitation)
    db.commit()
    
    invitation_link = f"{settings.base_url}/join/{invitation.token}"
    
    return {
        "message": "Invitation created",
        "invitation_link": invitation_link,
        "expires_at": invitation.expires_at,
    }


@router.post("/{project_id}/join")
async def join_project_with_secret(
    project_id: int,
    request: JoinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Join a project using the project secret."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify project secret
    if project.project_secret != request.project_secret:
        raise HTTPException(status_code=403, detail="Invalid project secret")
    
    # Check if already a member
    existing = (
        db.query(project_members)
        .filter(
            project_members.c.project_id == project_id,
            project_members.c.user_id == current_user.id,
        )
        .first()
    )
    
    if existing:
        return {"message": "Already a member of this project"}
    
    # Add user as member
    stmt = project_members.insert().values(
        user_id=current_user.id, project_id=project_id, role="member"
    )
    db.execute(stmt)
    db.commit()
    
    return {"message": "Successfully joined project"}


@router.delete("/{project_id}")
async def delete_project(
    project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Delete a project (metadata only, files preserved)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Only owner can delete
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only project owner can delete")
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted"}
