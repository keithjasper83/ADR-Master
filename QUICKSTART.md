# ADR-Workbench Quick Start Guide

Get started with ADR-Workbench in under 5 minutes!

## Option 1: Docker (Recommended)

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/keithjasper83/ADR-Master.git
cd ADR-Master

# Start with Docker Compose
docker-compose up

# Open your browser
open http://localhost:8000
```

That's it! The application is running with all features available.

## Option 2: Local Python

If you prefer to run locally:

```bash
# Clone the repository
git clone https://github.com/keithjasper83/ADR-Master.git
cd ADR-Master

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install

# Build CSS
npm run build:css

# Run the application
uvicorn app.main:app --reload

# Open your browser
open http://localhost:8000
```

## First Steps

### 1. Create Your First ADR

1. Click the **"New ADR"** button in the top-right corner
2. Fill in the form:
   - **Title**: "Use PostgreSQL for User Data"
   - **Context**: "We need a reliable database for storing user information..."
   - **Decision**: "We will use PostgreSQL as our primary database..."
   - **Consequences**: "Pros: ACID compliance, mature ecosystem. Cons: Additional infrastructure..."
3. Click **"Create ADR"**

### 2. Lint Your ADR

1. From the ADR list, click **"Lint"** next to your ADR
2. Review the linting results
3. Fix any issues by clicking **"Fix Issues"**

### 3. View Your ADR

1. Click on the ADR title to view the full details
2. See all sections formatted nicely
3. Use **"View Markdown"** to see the MADR format

## Optional: Enable Advanced Features

### LLM Integration (AI-Powered ADR Generation)

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys) or [Anthropic](https://console.anthropic.com/)
2. Copy `.env.example` to `.env`
3. Add your API key:
   ```
   OPENAI_API_KEY=sk-...
   ```
4. Restart the application
5. Use the **"Use LLM"** button when creating ADRs

### GitHub Integration (Create PRs from ADRs)

1. Create a [GitHub Personal Access Token](https://github.com/settings/tokens)
2. Add to `.env`:
   ```
   GITHUB_TOKEN=ghp_...
   ```
3. Restart the application
4. Click **"Create GitHub PR"** on any ADR

### MCP Integration (Connect to External Data)

1. Set up an MCP server (or use an existing one)
2. Add to `.env`:
   ```
   MCP_ENDPOINT=http://localhost:8080/mcp
   ```
3. Restart the application
4. Query project/features data via API or plugins

## Common Tasks

### View All ADRs

Navigate to: http://localhost:8000/adrs

Filter by status:
- Draft
- Proposed
- Accepted
- Rejected

### Edit an ADR

1. Go to the ADR detail page
2. Click **"Edit"**
3. Make your changes
4. Click **"Update ADR"**

### Delete an ADR

1. Go to the ADR detail page
2. Click **"Delete"**
3. Confirm the action

### Monitor Background Jobs

Navigate to: http://localhost:8000/jobs

See status of:
- LLM compilations
- GitHub PR creations
- Linting jobs

### Manage Plugins

Navigate to: http://localhost:8000/plugins

- View loaded plugins
- Enable/disable plugins
- Reload plugins after changes

## API Usage

ADR-Workbench provides a full REST API:

### Create an ADR via API

```bash
curl -X POST http://localhost:8000/api/adrs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Use Docker for Development",
    "context": "We need consistent development environments",
    "decision": "We will use Docker containers for all development",
    "consequences": "Easier onboarding, consistent environments"
  }'
```

### List ADRs via API

```bash
curl http://localhost:8000/api/adrs
```

### Get ADR by ID

```bash
curl http://localhost:8000/api/adrs/1
```

### Lint an ADR via API

```bash
curl -X POST http://localhost:8000/api/adrs/1/lint
```

### Generate ADR with LLM via API

```bash
curl -X POST http://localhost:8000/api/adrs/compile \
  -H "Content-Type: application/json" \
  -d '{
    "context": "We need to choose a frontend framework",
    "requirements": "Must be modern, well-documented, and have strong community support"
  }'
```

## Explore API Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Try out all endpoints directly from your browser!

## Working Offline

ADR-Workbench is designed to work completely offline:

1. All data is stored locally in SQLite
2. The web UI works without internet
3. Only optional features (LLM, GitHub) require internet

To work offline:
- Simply don't configure API keys
- All core ADR features work without any external services

## Creating Plugins

Extend ADR-Workbench with custom plugins:

1. Create a Python file in `plugins/`:

```python
# plugins/my_plugin.py

from app.plugins.base import Plugin, PluginMetadata

class MyPlugin(Plugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="My Plugin",
            version="1.0.0",
            description="Custom functionality"
        )
    
    async def on_adr_create(self, adr_data: dict) -> dict:
        print(f"ADR created: {adr_data['title']}")
        return adr_data
```

2. Restart the application (or use the Plugin Reload feature)
3. Your plugin is now active!

## Keyboard Shortcuts

While using the web interface:

- `Ctrl/Cmd + K`: Quick search (coming soon)
- `N`: New ADR
- `E`: Edit current ADR
- `L`: Lint current ADR

## Tips & Tricks

### 1. Auto-numbering

ADRs are automatically numbered sequentially (ADR-0001, ADR-0002, etc.)

### 2. Status Workflow

Recommended status progression:
```
draft → proposed → accepted/rejected
```

### 3. Link ADRs

Reference other ADRs in the "Links" field:
```
- Supersedes ADR-0001
- Related to ADR-0005
```

### 4. Use Templates

The "Options Considered" and "Pros/Cons" sections help structure decisions:
```
## Options Considered

1. Option A
2. Option B
3. Option C

## Pros and Cons

### Option A
Pros: X, Y
Cons: Z

### Option B
...
```

### 5. Consistent Formatting

Use the Lint feature regularly to maintain consistent quality across all ADRs.

## Troubleshooting

### Port 8000 Already in Use

Change the port:
```bash
uvicorn app.main:app --reload --port 8001
```

### Database Locked Error

If using SQLite, only one process can write at a time. Make sure you don't have multiple instances running.

### CSS Not Loading

Make sure you've built the CSS:
```bash
npm run build:css
```

### Module Not Found Errors

Ensure you're in the virtual environment:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

And dependencies are installed:
```bash
pip install -r requirements.txt
```

## Next Steps

Now that you're up and running:

1. **Read the full documentation**: Check out [README.md](README.md) for detailed features
2. **Explore the architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
3. **Development guide**: Read [DEVELOPMENT.md](DEVELOPMENT.md) for contributing
4. **Example ADR**: Look at [docs/adr/ADR-0001-use-madr-format.md](docs/adr/ADR-0001-use-madr-format.md)
5. **Try plugins**: Explore the example plugin in `plugins/example_plugin.py`

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/keithjasper83/ADR-Master/issues)
- **Documentation**: Check the `/docs` folder
- **API Docs**: http://localhost:8000/docs

## Sample Workflow

Here's a complete workflow from idea to published ADR:

1. **Brainstorm** - Think about the decision you need to make
2. **Create Draft** - Use the web UI or API to create a draft ADR
3. **AI Assist** (optional) - Use LLM to help structure your thoughts
4. **Lint** - Check for quality issues
5. **Refine** - Edit based on linting feedback
6. **Propose** - Change status to "proposed"
7. **Review** - Share with team (via GitHub PR or export)
8. **Accept** - Change status to "accepted"
9. **Publish** - Create GitHub PR to add to repository

Congratulations! You've successfully set up and started using ADR-Workbench. Happy decision documenting! 🎉
