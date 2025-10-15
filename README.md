# ADR-Master

Creation of ADR documents with AI assistance and agentic workflow at its heart

## ADR-Workbench

**ADR-Workbench** is an offline-capable FastAPI + HTMX + Tailwind web application for authoring, refining, linting, and syncing MADR-style Architecture Decision Records (ADRs).

### Features

#### Core Features
- 📝 **ADR Authoring**: Create and edit ADRs in MADR (Markdown Any Decision Records) format
- ✅ **Linting & Validation**: Real-time quality checks and best practice validation
- 🚀 **Offline-Capable**: Works completely offline with local SQLite database
- 🎨 **Modern UI**: FastAPI + HTMX + Tailwind CSS for a responsive, interactive experience

#### Advanced Features
- 🤖 **LLM Integration**: Generate and refine ADRs using OpenAI or Anthropic
- 🔄 **Async Job Processing**: Background jobs for LLM compilation and GitHub operations
- 🌐 **MCP Client**: Connect to existing Model Context Protocol endpoints for project/features data
- 🔌 **Plugin System**: Extend functionality with custom plugins
- 📤 **GitHub PR Promotion**: Create pull requests directly from ADRs
- 🛠️ **MCP Tool Exports**: Expose ADR operations as MCP tools

### Quick Start

#### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the application
open http://localhost:8000
```

#### Using Python

```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Build CSS
npm run build:css

# Run the application
python -m app.main

# Or use uvicorn directly
uvicorn app.main:app --reload
```

#### Using DevContainer

1. Open the project in VS Code
2. Click "Reopen in Container" when prompted
3. The application will start automatically on port 8000

### Project Structure

```
ADR-Master/
├── app/
│   ├── models/          # Database models (ADR, Job)
│   ├── routers/         # API routes (adrs, jobs, mcp, plugins, ui)
│   ├── services/        # Business logic (ADR, LLM, GitHub, Lint, Job)
│   ├── mcp/            # MCP client and tool exports
│   ├── plugins/        # Plugin system
│   ├── templates/      # HTML templates
│   ├── static/         # CSS, JS, and static assets
│   ├── config.py       # Application configuration
│   ├── database.py     # Database setup
│   └── main.py         # FastAPI application
├── docs/adr/           # ADR markdown files
├── plugins/            # Custom plugins
├── tests/              # Test files
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
└── requirements.txt    # Python dependencies
```

### Configuration

Create a `.env` file in the root directory:

```env
# Application
DEBUG=false
APP_NAME=ADR-Workbench

# Database
DATABASE_URL=sqlite+aiosqlite:///./adr_workbench.db

# MCP Client
MCP_ENDPOINT=http://localhost:8080/mcp

# LLM
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_DEFAULT_BRANCH=main

# ADR Settings
ADR_DIRECTORY=./docs/adr
ADR_TEMPLATE=madr
```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### UI Routes
- `GET /` - Home page
- `GET /adrs` - List ADRs
- `GET /adrs/new` - Create new ADR
- `GET /adrs/{id}` - View ADR details
- `GET /adrs/{id}/edit` - Edit ADR
- `GET /adrs/{id}/lint` - Lint results

#### API Routes
- `POST /api/adrs` - Create ADR
- `GET /api/adrs` - List ADRs
- `GET /api/adrs/{id}` - Get ADR
- `PUT /api/adrs/{id}` - Update ADR
- `DELETE /api/adrs/{id}` - Delete ADR
- `POST /api/adrs/compile` - Compile ADR with LLM
- `POST /api/adrs/{id}/github-pr` - Create GitHub PR

#### Job Routes
- `POST /api/jobs` - Create async job
- `GET /api/jobs` - List jobs
- `GET /api/jobs/{id}` - Get job status

#### MCP Routes
- `GET /api/mcp/health` - Check MCP endpoint health
- `POST /api/mcp/query` - Query MCP data
- `GET /api/mcp/exports` - List exported tools
- `POST /api/mcp/exports/{tool}` - Execute exported tool

#### Plugin Routes
- `GET /api/plugins` - List plugins
- `POST /api/plugins/load` - Load plugins
- `POST /api/plugins/{name}/enable` - Enable plugin
- `POST /api/plugins/{name}/disable` - Disable plugin

### Plugin Development

Create a plugin by adding a Python file to the `plugins/` directory:

```python
from app.plugins.base import Plugin, PluginMetadata

class MyPlugin(Plugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="My Plugin",
            version="1.0.0",
            description="Custom plugin functionality"
        )
    
    async def on_adr_create(self, adr_data: dict) -> dict:
        # Hook into ADR creation
        print(f"Creating ADR: {adr_data['title']}")
        return adr_data
```

### MCP Integration

ADR-Workbench can:
- **Connect as a client** to existing MCP endpoints for project/features data
- **Export tools** that other MCP clients can use

Example MCP client usage:

```python
from app.mcp.client import get_mcp_client

client = get_mcp_client()
result = await client.query_project_data("project-123")
```

### Development

#### Run Tests

```bash
pytest tests/ -v --cov=app
```

#### Lint Code

```bash
ruff check app/
black app/
mypy app/
```

#### Build CSS

```bash
npm run build:css
# or for development with watch
npm run watch:css
```

### Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Frontend**: HTMX, Tailwind CSS
- **Database**: SQLite (async with aiosqlite)
- **LLM**: OpenAI, Anthropic
- **GitHub**: PyGithub
- **MCP**: Model Context Protocol support
- **Container**: Docker, Docker Compose, DevContainer

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### License

MIT License - See LICENSE file for details

### Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/keithjasper83/ADR-Master).
