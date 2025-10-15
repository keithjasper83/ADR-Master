# ADR-Workbench Architecture

## Overview

ADR-Workbench is a modern web application built with FastAPI, HTMX, and Tailwind CSS for managing Architecture Decision Records (ADRs) in the MADR format. The application is designed to be offline-capable, extensible, and developer-friendly.

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with automatic API documentation
- **SQLAlchemy**: Async ORM for database operations
- **SQLite**: Lightweight, file-based database (via aiosqlite)
- **Pydantic**: Data validation and settings management
- **Python 3.11+**: Modern Python features and async/await support

### Frontend
- **HTMX**: Modern HTML-first approach to dynamic UIs
- **Tailwind CSS**: Utility-first CSS framework
- **Jinja2**: Server-side HTML templating
- **Vanilla JavaScript**: Minimal client-side JavaScript for interactivity

### Infrastructure
- **Docker**: Containerization for consistent environments
- **Docker Compose**: Multi-container orchestration
- **DevContainer**: VS Code development container support

## Architecture Layers

### 1. Data Layer (Models)

Located in `app/models/`, this layer defines the database schema:

- **ADR Model** (`adr.py`): Stores ADR content, metadata, and status
  - Fields: title, status, context, decision, consequences, etc.
  - Enums: ADRStatus (draft, proposed, accepted, rejected, deprecated, superseded)
  
- **Job Model** (`job.py`): Tracks async background jobs
  - Fields: job_type, status, input/output data, timestamps
  - Enums: JobType (llm_compile, github_pr, lint, sync, mcp_query)
  - Enums: JobStatus (pending, running, completed, failed, cancelled)

### 2. Service Layer (Business Logic)

Located in `app/services/`, this layer implements core functionality:

- **ADRService**: CRUD operations, MADR formatting, parsing
- **LLMService**: Integration with OpenAI and Anthropic for AI-powered ADR generation
- **GitHubService**: Create PRs, sync ADRs from repositories
- **LintService**: Validate ADRs against quality rules and best practices
- **JobService**: Manage async job lifecycle and processing

### 3. API Layer (Routers)

Located in `app/routers/`, this layer exposes HTTP endpoints:

- **ADRs Router** (`adrs.py`): 
  - `POST /api/adrs` - Create ADR
  - `GET /api/adrs` - List ADRs
  - `GET /api/adrs/{id}` - Get ADR details
  - `PUT /api/adrs/{id}` - Update ADR
  - `DELETE /api/adrs/{id}` - Delete ADR
  - `POST /api/adrs/compile` - Generate ADR with LLM
  - `POST /api/adrs/{id}/github-pr` - Create GitHub PR
  - `POST /api/adrs/{id}/lint` - Lint ADR

- **Jobs Router** (`jobs.py`):
  - `POST /api/jobs` - Create background job
  - `GET /api/jobs` - List jobs
  - `GET /api/jobs/{id}` - Get job status
  - `POST /api/jobs/{id}/cancel` - Cancel job

- **MCP Router** (`mcp.py`):
  - `GET /api/mcp/health` - Check MCP endpoint health
  - `POST /api/mcp/query` - Query project/features data
  - `GET /api/mcp/exports` - List exported tools
  - `POST /api/mcp/exports/{tool}` - Execute exported tool

- **Plugins Router** (`plugins.py`):
  - `GET /api/plugins` - List plugins
  - `POST /api/plugins/load` - Load/reload plugins
  - `POST /api/plugins/{name}/enable` - Enable plugin
  - `POST /api/plugins/{name}/disable` - Disable plugin
  - `POST /api/plugins/{name}/command` - Execute plugin command

- **UI Router** (`ui.py`):
  - `GET /` - Home page
  - `GET /adrs` - ADR list page
  - `GET /adrs/new` - Create ADR form
  - `GET /adrs/{id}` - ADR detail page
  - `GET /adrs/{id}/edit` - Edit ADR form
  - `GET /adrs/{id}/lint` - Lint results page
  - `GET /jobs`, `/plugins`, `/settings` - Other pages

### 4. Integration Layer

#### MCP Integration (`app/mcp/`)

The Model Context Protocol (MCP) integration provides:

- **MCP Client** (`client.py`): Connect to external MCP servers as a client
  - Query project data
  - Query features data
  - Call remote tools
  - Health checking

- **MCP Tool Exporter** (`tools.py`): Export ADR-Workbench features as MCP tools
  - List ADRs
  - Get ADR
  - Create ADR
  - Lint ADR
  - Format ADR as MADR

#### Plugin System (`app/plugins/`)

Extensible plugin architecture:

- **Plugin Base** (`base.py`): Abstract base class for plugins
  - Metadata definition
  - Lifecycle hooks (on_load, on_unload)
  - Event hooks (on_adr_create, on_adr_update, on_adr_lint, etc.)
  - Custom command execution

- **Plugin Manager** (`manager.py`): Plugin lifecycle management
  - Dynamic plugin loading from `plugins/` directory
  - Plugin enable/disable
  - Hook execution across all plugins
  - Plugin command routing

### 5. Presentation Layer (Templates & Static)

#### Templates (`app/templates/`)

Server-rendered HTML using Jinja2:

- **base.html**: Common layout with navigation and footer
- **index.html**: Landing page with feature overview
- **adrs_list.html**: ADR listing with filtering
- **adr_detail.html**: ADR full view with actions
- **adr_form.html**: Create/edit ADR form
- **lint_results.html**: Linting results display
- **jobs.html**: Background jobs dashboard
- **plugins.html**: Plugin management interface
- **settings.html**: Application configuration
- **error.html**: Error page

#### Static Assets (`app/static/`)

- **CSS**: Tailwind-based styling (input.css, output.css)
- **JavaScript**: Client-side interactivity (app.js)
  - HTMX event handling
  - Notification system
  - Form validation
  - Auto-save functionality

## Key Design Patterns

### 1. Async/Await Throughout

All I/O operations use async/await:
- Database queries (async SQLAlchemy)
- HTTP calls (httpx)
- LLM API calls (async clients)
- File operations (aiosqlite)

### 2. Dependency Injection

FastAPI's dependency injection for:
- Database sessions (`get_db`)
- Configuration (`Settings`)
- Singletons (MCP client, Plugin manager)

### 3. Service Layer Pattern

Business logic separated from HTTP layer:
- Services are reusable across different contexts
- Easy to test in isolation
- Clear separation of concerns

### 4. Repository Pattern (via SQLAlchemy)

Database access abstracted through SQLAlchemy:
- Type-safe queries
- Relationship management
- Migration support (via Alembic)

### 5. Plugin Architecture

Hook-based plugin system:
- Plugins register for lifecycle events
- Minimal coupling to core application
- Dynamic loading and unloading

### 6. HTMX for Progressive Enhancement

Server-rendered HTML with HTMX for interactivity:
- No complex client-side state management
- Fast initial page loads
- Graceful degradation
- SEO-friendly

## Data Flow

### Creating an ADR

```
User fills form → 
  HTMX POST to /api/adrs → 
    Plugin hooks (on_adr_create) → 
      ADRService.create_adr() → 
        SQLAlchemy insert → 
          Database commit → 
            Return ADR JSON → 
              HTMX updates DOM
```

### LLM Compilation (Async)

```
User requests compilation → 
  POST /api/jobs (LLM_COMPILE) → 
    Create Job record → 
      Background task started → 
        LLMService.compile_adr() → 
          OpenAI/Anthropic API call → 
            Update Job status → 
              User polls /api/jobs/{id} → 
                HTMX updates UI with result
```

### GitHub PR Creation

```
User clicks "Create PR" → 
  POST /api/adrs/{id}/github-pr → 
    GitHubService.create_pr_for_adr() → 
      Format ADR as MADR → 
        GitHub API: create branch → 
          GitHub API: commit file → 
            GitHub API: create PR → 
              Return PR URL → 
                Update UI with link
```

## Configuration Management

Environment-based configuration via Pydantic Settings:

```python
# .env file
DEBUG=false
DATABASE_URL=sqlite+aiosqlite:///./adr_workbench.db
MCP_ENDPOINT=http://localhost:8080/mcp
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...
```

Accessed via:
```python
from app.config import settings
settings.database_url  # Type-safe access
```

## Database Schema

### ADRs Table

```sql
CREATE TABLE adrs (
    id INTEGER PRIMARY KEY,
    number INTEGER UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL,
    context TEXT,
    decision TEXT,
    consequences TEXT,
    options_considered TEXT,
    pros_cons TEXT,
    links TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    file_path VARCHAR(500),
    git_sha VARCHAR(40)
);
```

### Jobs Table

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    job_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    adr_id INTEGER,
    input_data TEXT,
    output_data TEXT,
    error_message TEXT,
    created_at DATETIME NOT NULL,
    started_at DATETIME,
    completed_at DATETIME
);
```

## Security Considerations

1. **API Keys**: Stored in environment variables, never committed
2. **Input Validation**: Pydantic models validate all input
3. **SQL Injection**: Prevented by SQLAlchemy parameterized queries
4. **XSS**: Jinja2 auto-escapes HTML
5. **CORS**: Configurable via middleware
6. **Secrets**: GitHub tokens, API keys in .env (gitignored)

## Scalability Considerations

Current design is optimized for single-user/small-team use:

- **SQLite**: File-based, suitable for <100GB data
- **Single process**: uvicorn with --workers for multiple processes
- **No external dependencies**: Works completely offline

To scale:

1. **Database**: Switch to PostgreSQL via DATABASE_URL
2. **Caching**: Add Redis for job queue
3. **Load Balancing**: Multiple uvicorn workers behind nginx
4. **File Storage**: Move ADR files to S3/object storage
5. **Background Jobs**: Use Celery instead of FastAPI background tasks

## Extension Points

### 1. Custom Lint Rules

Extend `LintService` to add custom validation:

```python
class CustomLintService(LintService):
    @staticmethod
    def lint_adr(adr: ADR) -> List[LintIssue]:
        issues = LintService.lint_adr(adr)
        # Add custom rules
        return issues
```

### 2. Additional LLM Providers

Add new providers to `LLMService`:

```python
@staticmethod
async def _call_custom_llm(prompt: str, model: str):
    # Implementation
    pass
```

### 3. Custom ADR Templates

Modify `ADRService.format_as_madr()` to support different templates.

### 4. Plugins

Create plugins for:
- Custom linting rules
- ADR templates
- Integration with other tools
- Workflow automation

## Testing Strategy

### Unit Tests

Test individual services:
```python
@pytest.mark.asyncio
async def test_create_adr(db_session):
    adr = await ADRService.create_adr(...)
    assert adr.id is not None
```

### Integration Tests

Test API endpoints:
```python
def test_api_create_adr(client):
    response = client.post("/api/adrs", json={...})
    assert response.status_code == 201
```

### Plugin Tests

Test plugin hooks:
```python
@pytest.mark.asyncio
async def test_plugin_hook():
    plugin = MyPlugin()
    result = await plugin.on_adr_create({...})
    assert result["title"] == "Modified"
```

## Deployment Options

### 1. Local Development

```bash
uvicorn app.main:app --reload
```

### 2. Docker

```bash
docker-compose up
```

### 3. Cloud (Example: Heroku, Railway, Render)

```bash
# Procfile
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 4. Self-Hosted (systemd service)

```ini
[Unit]
Description=ADR-Workbench
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/adr-workbench
ExecStart=/opt/adr-workbench/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## Future Enhancements

Potential additions:
- [ ] Real-time collaboration (WebSockets)
- [ ] ADR version history
- [ ] Export to PDF/Word
- [ ] Import from other ADR formats
- [ ] Search with full-text indexing
- [ ] Analytics dashboard
- [ ] Slack/Teams integration
- [ ] Custom workflows
- [ ] Role-based access control
- [ ] ADR templates library

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [HTMX Documentation](https://htmx.org/)
- [MADR Format](https://adr.github.io/madr/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
