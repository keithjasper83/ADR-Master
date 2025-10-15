# Development Guide for ADR-Workbench

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/keithjasper83/ADR-Master.git
cd ADR-Master
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Install Node Dependencies

```bash
npm install
```

### 4. Build CSS

```bash
# Build CSS once
npm run build:css

# Or watch for changes during development
npm run watch:css
```

### 5. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# (Most features work without API keys for local development)
```

## Running the Application

### Development Mode

```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m app.main
```

The application will be available at:
- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Docker Mode

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### DevContainer Mode (VS Code)

1. Install "Remote - Containers" extension
2. Open project in VS Code
3. Click "Reopen in Container" when prompted
4. The application will start automatically

## Project Structure

```
ADR-Master/
├── app/
│   ├── models/           # Database models
│   │   ├── adr.py       # ADR model
│   │   └── job.py       # Job tracking model
│   ├── routers/         # API routes
│   │   ├── adrs.py      # ADR endpoints
│   │   ├── jobs.py      # Job endpoints
│   │   ├── mcp.py       # MCP endpoints
│   │   ├── plugins.py   # Plugin endpoints
│   │   └── ui.py        # Web UI routes
│   ├── services/        # Business logic
│   │   ├── adr_service.py    # ADR operations
│   │   ├── llm_service.py    # LLM integration
│   │   ├── github_service.py # GitHub operations
│   │   ├── lint_service.py   # Linting
│   │   └── job_service.py    # Job management
│   ├── mcp/            # MCP integration
│   │   ├── client.py   # MCP client
│   │   └── tools.py    # MCP tool exports
│   ├── plugins/        # Plugin system
│   │   ├── base.py     # Plugin base class
│   │   └── manager.py  # Plugin manager
│   ├── templates/      # Jinja2 HTML templates
│   ├── static/         # CSS, JS, assets
│   ├── config.py       # Configuration
│   ├── database.py     # Database setup
│   └── main.py         # FastAPI app
├── docs/adr/           # ADR files
├── plugins/            # Custom plugins
├── tests/              # Test files
├── requirements.txt    # Python dependencies
├── package.json        # Node dependencies
├── Dockerfile          # Docker config
└── docker-compose.yml  # Docker Compose config
```

## Development Workflow

### 1. Database

The application uses SQLite by default. On first run, the database is created automatically.

To reset the database:
```bash
rm adr_workbench.db
python -m app.main  # Recreates database
```

### 2. Making Changes

#### Backend (Python)

1. Make changes to Python files in `app/`
2. The application will auto-reload (if running with `--reload`)
3. Test your changes via the web UI or API docs

#### Frontend (HTML/CSS)

1. Edit HTML templates in `app/templates/`
2. Edit CSS in `app/static/css/input.css`
3. Run `npm run build:css` or keep `npm run watch:css` running
4. Refresh the browser

#### JavaScript

1. Edit `app/static/js/app.js`
2. Refresh the browser

### 3. Creating a Plugin

Create a new Python file in `plugins/` directory:

```python
# plugins/my_plugin.py

from app.plugins.base import Plugin, PluginMetadata

class MyPlugin(Plugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="My Plugin",
            version="1.0.0",
            description="My custom plugin",
            author="Your Name"
        )
    
    async def on_adr_create(self, adr_data: dict) -> dict:
        # Custom logic when ADR is created
        print(f"ADR created: {adr_data['title']}")
        return adr_data
```

The plugin will be loaded automatically on application startup.

### 4. Adding MCP Integration

To connect to an MCP server:

1. Set `MCP_ENDPOINT` in `.env`:
   ```
   MCP_ENDPOINT=http://localhost:8080/mcp
   ```

2. Use the MCP client in your code:
   ```python
   from app.mcp.client import get_mcp_client
   
   client = get_mcp_client()
   result = await client.query_project_data("project-id")
   ```

### 5. LLM Integration

To use LLM features:

1. Add API keys to `.env`:
   ```
   OPENAI_API_KEY=sk-...
   # or
   ANTHROPIC_API_KEY=sk-ant-...
   ```

2. Use the LLM service:
   ```python
   from app.services.llm_service import LLMService
   
   result = await LLMService.compile_adr(
       context="Problem description",
       requirements="Solution requirements"
   )
   ```

### 6. GitHub Integration

To create PRs from ADRs:

1. Create a GitHub Personal Access Token with `repo` scope
2. Add to `.env`:
   ```
   GITHUB_TOKEN=ghp_...
   ```

3. Use via API or UI

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_adr_service.py

# Run in verbose mode
pytest -v
```

### Writing Tests

Create test files in `tests/` directory following the pattern:

```python
# tests/test_my_feature.py

import pytest
from app.services.my_service import MyService

@pytest.mark.asyncio
async def test_my_feature():
    result = await MyService.do_something()
    assert result is not None
```

## Code Quality

### Linting

```bash
# Check code style with ruff
ruff check app/

# Format code with black
black app/

# Type checking with mypy
mypy app/
```

### Pre-commit Hooks

(Optional) Set up pre-commit hooks to automatically check code quality:

```bash
pip install pre-commit
pre-commit install
```

## Troubleshooting

### Database Issues

If you encounter database errors:
```bash
# Reset database
rm adr_workbench.db
python -m app.main
```

### CSS Not Updating

Make sure to rebuild CSS:
```bash
npm run build:css
```

Or run watch mode:
```bash
npm run watch:css
```

### Port Already in Use

Change the port in the run command:
```bash
uvicorn app.main:app --reload --port 8001
```

### Import Errors

Make sure you're in the virtual environment:
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

And dependencies are installed:
```bash
pip install -r requirements.txt
```

## API Development

### Adding New Endpoints

1. Create/edit a router file in `app/routers/`
2. Add the endpoint function
3. Include the router in `app/main.py`

Example:

```python
# app/routers/my_router.py

from fastapi import APIRouter

router = APIRouter(prefix="/api/my-feature", tags=["my-feature"])

@router.get("/")
async def list_items():
    return {"items": []}
```

```python
# app/main.py

from app.routers import my_router

app.include_router(my_router.router)
```

### Testing API Endpoints

Use the interactive API docs at http://localhost:8000/docs to test endpoints.

Or use curl:
```bash
curl http://localhost:8000/api/adrs
```

## Deployment

### Production Build

```bash
# Install production dependencies only
pip install -r requirements.txt --no-dev

# Build optimized CSS
npm run build:css

# Run with production settings
export DEBUG=false
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment

```bash
docker build -t adr-workbench .
docker run -p 8000:8000 adr-workbench
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Add tests for new functionality
5. Run tests and linting
6. Commit your changes: `git commit -am 'Add new feature'`
7. Push to the branch: `git push origin feature/my-feature`
8. Create a Pull Request

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [HTMX Documentation](https://htmx.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [MADR Template](https://adr.github.io/madr/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/keithjasper83/ADR-Master/issues)
- Check existing documentation
- Review example code in the repository
