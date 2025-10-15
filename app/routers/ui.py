"""UI routes for web interface."""

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.services.adr_service import ADRService
from app.services.lint_service import LintService
from app.models.adr import ADRStatus

router = APIRouter(tags=["ui"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/adrs", response_class=HTMLResponse)
async def adrs_page(
    request: Request,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """ADR list page."""
    status_filter = ADRStatus(status) if status else None
    adrs = await ADRService.list_adrs(db, status=status_filter)
    
    return templates.TemplateResponse(
        "adrs_list.html",
        {
            "request": request,
            "adrs": adrs,
            "current_status": status
        }
    )


@router.get("/adrs/new", response_class=HTMLResponse)
async def new_adr_page(request: Request):
    """New ADR page."""
    return templates.TemplateResponse("adr_form.html", {"request": request, "adr": None})


@router.get("/adrs/{adr_id}", response_class=HTMLResponse)
async def adr_detail(
    request: Request,
    adr_id: int,
    db: AsyncSession = Depends(get_db)
):
    """ADR detail page."""
    adr = await ADRService.get_adr(db, adr_id)
    if not adr:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "ADR not found"},
            status_code=404
        )
    
    return templates.TemplateResponse(
        "adr_detail.html",
        {"request": request, "adr": adr}
    )


@router.get("/adrs/{adr_id}/edit", response_class=HTMLResponse)
async def edit_adr_page(
    request: Request,
    adr_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Edit ADR page."""
    adr = await ADRService.get_adr(db, adr_id)
    if not adr:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "ADR not found"},
            status_code=404
        )
    
    return templates.TemplateResponse(
        "adr_form.html",
        {"request": request, "adr": adr}
    )


@router.get("/adrs/{adr_id}/lint", response_class=HTMLResponse)
async def lint_adr_page(
    request: Request,
    adr_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Lint ADR page."""
    adr = await ADRService.get_adr(db, adr_id)
    if not adr:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "ADR not found"},
            status_code=404
        )
    
    issues = LintService.lint_adr(adr)
    summary = LintService.get_lint_summary(issues)
    
    return templates.TemplateResponse(
        "lint_results.html",
        {
            "request": request,
            "adr": adr,
            "summary": summary
        }
    )


@router.get("/jobs", response_class=HTMLResponse)
async def jobs_page(request: Request):
    """Jobs page."""
    return templates.TemplateResponse("jobs.html", {"request": request})


@router.get("/plugins", response_class=HTMLResponse)
async def plugins_page(request: Request):
    """Plugins page."""
    return templates.TemplateResponse("plugins.html", {"request": request})


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page."""
    return templates.TemplateResponse("settings.html", {"request": request})
