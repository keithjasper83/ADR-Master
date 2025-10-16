"""Health check endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "adr-master"}


@router.get("/api/docs")
async def api_docs():
    """API documentation redirect."""
    from fastapi.responses import RedirectResponse
    
    return RedirectResponse(url="/docs")
