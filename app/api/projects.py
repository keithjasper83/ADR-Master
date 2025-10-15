"""Projects API endpoints."""
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class IndexRequest(BaseModel):
    """Request to index a project."""

    path: str


class IndexResponse(BaseModel):
    """Response for indexing."""

    indexed_files: int
    message: str


@router.post("/index", response_model=IndexResponse)
async def index_project(request: IndexRequest):
    """Index a local repository for symbols and file listing."""
    try:
        project_path = Path(request.path)
        
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project path not found")
        
        # Simple file counting (could be extended with tree-sitter later)
        file_extensions = [".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".c"]
        files = []
        
        for ext in file_extensions:
            files.extend(project_path.rglob(f"*{ext}"))
        
        return IndexResponse(
            indexed_files=len(files), message=f"Indexed {len(files)} files from project"
        )
    except Exception as e:
        logger.error(f"Failed to index project: {e}")
        raise HTTPException(status_code=500, detail=str(e))
