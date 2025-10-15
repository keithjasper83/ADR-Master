# ADR-Master

**Offline-capable ADR Editor with MCP Integration and Agentic Workflow**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

ADR-Master is a powerful, offline-capable Architecture Decision Records (ADR) editor that helps teams author, visualize, refine, lint, and promote ADRs using MADR templates. It features MCP integration for project/feature awareness and LLM-powered compilation for enhanced ADR quality.

## Features

- 📝 **MADR-based ADR Editor** with live preview and syntax hints
- 🤖 **LLM-powered compilation** for ADR improvement and refinement
- 🔍 **Smart linting** with MADR structure validation
- 📊 **Diff and promote** workflow for moving ADRs from draft to final
- 🔌 **MCP integration** (client) for project and feature awareness
- 🚀 **GitHub sync** with PR creation support
- 🧩 **Plugin system** for extensibility
- 💾 **Offline-first** design - works without internet
- 🐳 **Docker & Devcontainer** ready

## Quick Start

### Using Docker

```bash
# Build and run
docker build -t adr-master .
docker run -p 8000:8000 -v $(pwd)/ADR:/app/ADR adr-master

# Visit http://localhost:8000
```

### Using Devcontainer

1. Open in VS Code with Remote-Containers extension
2. Reopen in container
3. Application starts automatically

### Local Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run application
uvicorn app.main:app --reload

# Or use Make
make dev
make run
```

## Configuration

Create a `.env` file (see `.env.example`):

```env
# Working directory
WORKDIR=/app

# MCP Integration (optional)
MCP_BASE_URL=http://localhost:3000/api
MCP_TOKEN=your-token

# LLM Endpoint (local/offline)
LLM_ENDPOINT=http://localhost:11434/api/generate

# GitHub Integration (optional)
GITHUB_TOKEN=your-github-token

# Database
DATABASE_URL=sqlite:///./adr_master.db
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ADR-Master Web UI                     │
│              (HTMX + Alpine.js + Tailwind)               │
├─────────────────────────────────────────────────────────┤
│                   FastAPI REST API                       │
│  /api/adr | /api/mcp | /api/projects | /api/integrations│
├─────────────────────────────────────────────────────────┤
│              Core Services Layer                         │
│  ADR Service | MCP Client | LLM Service | GitHub Service│
├─────────────────────────────────────────────────────────┤
│         SQLite Database (Jobs, Metadata, Logs)          │
└─────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
   /ADR & /ADR/Draft    MCP Server (external)   LLM (local)
```

## ADR Workflow

1. **Create Draft** → Generate MADR-formatted draft in `/ADR/Draft`
2. **Edit & Refine** → Use built-in editor with live preview
3. **Compile** → Send to LLM for improvement (async job)
4. **Lint** → Validate structure and content
5. **Promote** → Move to `/ADR` with status change to "Accepted"
6. **Sync** → Push to GitHub with optional PR creation

## API Endpoints

### ADR Operations
- `POST /api/adr/draft` - Create new draft
- `POST /api/adr/compile` - Start async compilation
- `GET /api/adr/jobs/{job_id}` - Check job status
- `POST /api/adr/lint` - Validate ADR
- `POST /api/adr/promote` - Promote to final
- `POST /api/adr/sync` - Sync with GitHub

### MCP Integration
- `GET /api/mcp/config` - MCP connection status
- `GET /api/mcp/projects` - List projects
- `GET /api/mcp/features` - List features
- `POST /api/mcp/proposals` - Submit proposal

### Project & Integrations
- `POST /api/projects/index` - Index local project
- `GET /api/integrations/` - List integrations
- `POST /api/integrations/` - Register integration

Full API docs: http://localhost:8000/docs

## MCP Tools Export

ADR-Master includes a thin MCP tools adapter (`mcp_tools/`) that exposes core functions as MCP-compatible tools for other MCP servers to integrate:

- `adr.generate` - Generate new ADR draft
- `adr.compile` - Compile with LLM
- `adr.lint` - Validate ADR
- `adr.promote` - Promote to final
- `adr.sync` - Sync with remote

**Note:** ADR-Master is NOT an MCP server itself. See `mcp_tools/README.md` for integration details.

## Plugin Development

Create custom plugins to enhance ADR workflows:

```python
from app.schemas.integration import IntegrationCreate
import httpx

# Register plugin
async with httpx.AsyncClient() as client:
    await client.post(
        "http://localhost:8000/api/integrations/",
        json={
            "name": "My Plugin",
            "description": "Custom ADR enhancement",
            "hooks": ["on_draft_create", "on_compile_post"],
            "config": {}
        }
    )
```

Available hooks:
- `on_draft_create` - After draft creation
- `on_compile_post` - After LLM compilation
- `on_promote_pre` - Before promotion
- `on_sync_post` - After sync

See `examples/plugin_example.py` for complete example.

## Development

### Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Or using make
make dev
```

### Testing

```bash
# Run tests with coverage
make test

# Run without coverage requirement
pytest -v

# Using nox
nox
```

### Linting & Formatting

```bash
make lint        # Run ruff
make format      # Format with black and ruff
make type-check  # Run mypy
make security    # Run bandit
```

### CI Gates

All commits must pass:
- ✅ ruff (linting)
- ✅ black (formatting)
- ✅ mypy (type checking)
- ✅ pytest (≥90% coverage)
- ✅ bandit (security)

## Offline Operation

ADR-Master works completely offline:

1. **No external dependencies** except configured endpoints
2. **Local LLM** support (Ollama, llama.cpp, etc.)
3. **File-based storage** (SQLite + markdown files)
4. **Optional integrations** (MCP, GitHub) - work without them
5. **Air-gap friendly** - no telemetry or external calls

### Running Offline

```bash
# Without MCP integration
unset MCP_BASE_URL

# With local LLM (Ollama example)
# Install: https://ollama.ai
ollama run llama2

# ADR-Master will use http://localhost:11434/api/generate
```

## Directory Structure

```
ADR-Master/
├── app/                    # Main application
│   ├── api/               # API endpoints
│   ├── core/              # Core business logic
│   ├── db/                # Database setup
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business services
│   ├── templates/         # HTML templates
│   └── static/            # Static assets
├── mcp_tools/             # MCP tools adapter
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── examples/              # Example plugins and templates
├── docs/                  # Additional documentation
├── ADR/                   # Final ADRs
│   └── Draft/            # Draft ADRs
├── _logs/                # Application logs
└── pyproject.toml        # Project configuration
```

## Examples

### Create Draft via API

```bash
curl -X POST http://localhost:8000/api/adr/draft \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Use GraphQL for API",
    "problem": "Need flexible API for multiple clients",
    "context": "Mobile and web apps with different data needs"
  }'
```

### Compile with LLM

```bash
curl -X POST http://localhost:8000/api/adr/compile \
  -H "Content-Type: application/json" \
  -d '{
    "draft_path": "/app/ADR/Draft/003-use-graphql.md",
    "human_notes": "Focus on performance implications"
  }'
```

### Check Job Status

```bash
curl http://localhost:8000/api/adr/jobs/{job_id}
```

## Troubleshooting

### LLM Not Working
- Check `LLM_ENDPOINT` is set correctly
- Verify LLM service is running (e.g., `ollama list`)
- Test endpoint: `curl -X POST $LLM_ENDPOINT -d '{"model":"llama2","prompt":"test"}'`

### MCP Connection Failed
- Verify `MCP_BASE_URL` is accessible
- Check `MCP_TOKEN` if authentication required
- Test: `curl -H "Authorization: Bearer $MCP_TOKEN" $MCP_BASE_URL/health`

### Database Locked
- Only one writer at a time (SQLite limitation)
- Restart application if process died mid-transaction

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Roadmap (V2)

- [ ] Tree-sitter integration for code-aware previews
- [ ] LibCST/ts-morph for code diffs tied to ADRs
- [ ] Web Workers for heavy operations
- [ ] Real-time collaboration (optional)
- [ ] ADR templates library
- [ ] Export to PDF/HTML
- [ ] ADR dependency graph visualization
- [ ] Advanced search and filtering
- [ ] Automated ADR suggestions from code changes

## Support

- Documentation: See `docs/` directory
- Issues: GitHub Issues
- Discussions: GitHub Discussions

---

Built with ❤️ for teams who value architecture documentation
