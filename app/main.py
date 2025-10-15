"""Main FastAPI application."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import adr, healthz, integrations, mcp, projects
from app.config import get_settings
from app.db.database import engine, init_db
from app.models import base  # noqa: F401 - needed for model registration

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    settings = get_settings()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    # Ensure required directories exist
    settings.adr_dir.mkdir(parents=True, exist_ok=True)
    settings.adr_draft_dir.mkdir(parents=True, exist_ok=True)
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Application startup complete")
    
    yield
    
    # Cleanup
    logger.info("Application shutdown")
    engine.dispose()


app = FastAPI(
    title="ADR-Master",
    description="Offline-capable ADR Editor with MCP integration",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
settings = get_settings()
if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Setup templates
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Include routers
app.include_router(healthz.router, tags=["Health"])
app.include_router(adr.router, prefix="/api/adr", tags=["ADR"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["MCP"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])


@app.get("/", response_class=HTMLResponse)
async def index():
    """Root endpoint - main UI."""
    from fastapi import Request
    
    request = Request(scope={"type": "http", "headers": []})
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/settings", response_class=HTMLResponse)
async def settings_page():
    """Settings page."""
    from fastapi import Request
    
    request = Request(scope={"type": "http", "headers": []})
    return templates.TemplateResponse("settings.html", {"request": request})


@app.get("/proposals", response_class=HTMLResponse)
async def proposals_page():
    """Proposals page."""
    from fastapi import Request
    
    request = Request(scope={"type": "http", "headers": []})
    return templates.TemplateResponse("proposals.html", {"request": request})


@app.get("/integrations", response_class=HTMLResponse)
async def integrations_page():
    """Integrations page."""
    from fastapi import Request
    
    request = Request(scope={"type": "http", "headers": []})
    return templates.TemplateResponse("integrations.html", {"request": request})
