# API Reference

Complete API reference for ADR-Master.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required. For production, implement behind reverse proxy with authentication.

## Health & Status

### GET /healthz

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "adr-master"
}
```

### GET /api/docs

Redirects to interactive Swagger UI documentation.

## ADR Operations

### POST /api/adr/draft

Create a new ADR draft.

**Request Body:**
```json
{
  "title": "Use GraphQL for API",
  "problem": "Need flexible API for multiple clients",
  "context": "Mobile and web apps with different data needs",
  "options": "REST vs GraphQL vs gRPC",
  "decision_hint": "Prefer GraphQL for flexibility",
  "references": ["https://graphql.org"]
}
```

**Response:**
```json
{
  "draft_path": "/app/ADR/Draft/001-use-graphql-for-api.md",
  "slug": "001-use-graphql-for-api.md",
  "message": "Draft created successfully"
}
```

### POST /api/adr/compile

Start async compilation job to improve ADR with LLM.

**Request Body:**
```json
{
  "draft_path": "/app/ADR/Draft/001-use-graphql-for-api.md",
  "human_notes": "Focus on performance trade-offs"
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Compilation job started"
}
```

### GET /api/adr/jobs/{job_id}

Check compilation job status.

**Parameters:**
- `job_id` (path): Job UUID

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "logs": [
    "Job created at 2024-01-15T10:30:00",
    "Starting compilation...",
    "LLM processing complete",
    "Draft updated successfully"
  ],
  "output_path": "/app/ADR/Draft/001-use-graphql-for-api.md",
  "error_message": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

**Status Values:**
- `queued`: Job waiting to start
- `running`: Job in progress
- `completed`: Job finished successfully
- `failed`: Job encountered error

### POST /api/adr/lint

Validate ADR structure and content.

**Request Body:**
```json
{
  "file_path": "/app/ADR/Draft/001-use-graphql-for-api.md"
}
```

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Decision summary exceeds 280 characters"
  ]
}
```

**Common Errors:**
- "Filename must match format: NNN-title.md"
- "Missing required section: Context"
- "Invalid status: Draft"
- "File not found: /path/to/file.md"

### POST /api/adr/promote

Promote ADR from draft to final.

**Request Body:**
```json
{
  "draft_path": "/app/ADR/Draft/001-use-graphql-for-api.md",
  "create_pr": true
}
```

**Response:**
```json
{
  "final_path": "/app/ADR/001-use-graphql-for-api.md",
  "branch": "adr/001-use-graphql-for-api",
  "pr_url": "https://github.com/org/repo/compare/adr/001-use-graphql-for-api",
  "message": "ADR promoted successfully"
}
```

### POST /api/adr/sync

Sync ADR directories with remote repository.

**Request Body:**
```json
{
  "direction": "both"
}
```

**Parameters:**
- `direction`: `pull`, `push`, or `both`

**Response:**
```json
{
  "synced_files": [
    "Pulled latest changes",
    "ADR/001-decision.md",
    "ADR/Draft/002-draft.md"
  ],
  "conflicts": [],
  "message": "Sync completed"
}
```

## MCP Integration

### GET /api/mcp/config

Get MCP configuration and connection status.

**Response:**
```json
{
  "mcp_base_url": "http://mcp-server:3000/api",
  "has_token": true,
  "connected": true
}
```

### GET /api/mcp/projects

List all projects from MCP server.

**Response:**
```json
[
  {
    "id": "proj-123",
    "name": "My Project",
    "description": "Project description",
    "metadata": {}
  }
]
```

### GET /api/mcp/features

List features, optionally filtered by project.

**Query Parameters:**
- `project` (optional): Project ID

**Response:**
```json
[
  {
    "id": "feat-456",
    "project_id": "proj-123",
    "name": "User Authentication",
    "description": "Implement OAuth2 authentication",
    "tags": ["auth", "security"],
    "metadata": {
      "priority": "high",
      "assignee": "john@example.com"
    }
  }
]
```

### POST /api/mcp/proposals

Submit a proposal to MCP server.

**Request Body:**
```json
{
  "adr_path": "/app/ADR/001-use-oauth2.md",
  "feature_ids": ["feat-456"],
  "summary": "Proposal to implement OAuth2 based on ADR-001",
  "patch_content": "diff --git a/auth.py b/auth.py\n..."
}
```

**Response:**
```json
{
  "proposal_id": "prop-789",
  "message": "Proposal submitted successfully"
}
```

## Projects

### POST /api/projects/index

Index a local repository for symbols and files.

**Request Body:**
```json
{
  "path": "/path/to/project"
}
```

**Response:**
```json
{
  "indexed_files": 42,
  "message": "Indexed 42 files from project"
}
```

## Integrations

### GET /api/integrations/

List all registered integrations.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Risk Analyzer",
    "description": "Analyzes ADRs for potential risks",
    "hooks": ["on_draft_create", "on_compile_post"],
    "config": {
      "risk_threshold": "medium"
    },
    "enabled": true
  }
]
```

### POST /api/integrations/

Register a new integration.

**Request Body:**
```json
{
  "name": "Risk Analyzer",
  "description": "Analyzes ADRs for potential risks",
  "hooks": ["on_draft_create", "on_compile_post"],
  "config": {
    "risk_threshold": "medium",
    "auto_analyze": true
  }
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Risk Analyzer",
  "description": "Analyzes ADRs for potential risks",
  "hooks": ["on_draft_create", "on_compile_post"],
  "config": {
    "risk_threshold": "medium",
    "auto_analyze": true
  },
  "enabled": true
}
```

**Available Hooks:**
- `on_draft_create`: Called after draft creation
- `on_compile_post`: Called after LLM compilation
- `on_promote_pre`: Called before promotion
- `on_sync_post`: Called after sync operation

### DELETE /api/integrations/{integration_id}

Delete an integration.

**Parameters:**
- `integration_id` (path): Integration ID

**Response:**
```json
{
  "message": "Integration deleted successfully"
}
```

## Error Responses

All endpoints may return error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

## Rate Limiting

Currently no rate limiting implemented. For production, implement at reverse proxy level.

## WebSocket Support

Currently not implemented. Future versions may add WebSocket for:
- Real-time compilation progress
- Live collaboration
- Change notifications

## Examples

### Complete ADR Workflow

```bash
# 1. Create draft
DRAFT=$(curl -s -X POST http://localhost:8000/api/adr/draft \
  -H "Content-Type: application/json" \
  -d '{"title":"Use Redis for Caching","problem":"Need fast cache","context":"High traffic app"}' \
  | jq -r '.draft_path')

# 2. Compile with LLM
JOB=$(curl -s -X POST http://localhost:8000/api/adr/compile \
  -H "Content-Type: application/json" \
  -d "{\"draft_path\":\"$DRAFT\"}" \
  | jq -r '.job_id')

# 3. Wait for compilation
while true; do
  STATUS=$(curl -s http://localhost:8000/api/adr/jobs/$JOB | jq -r '.status')
  echo "Status: $STATUS"
  [ "$STATUS" = "completed" ] && break
  sleep 2
done

# 4. Lint
curl -s -X POST http://localhost:8000/api/adr/lint \
  -H "Content-Type: application/json" \
  -d "{\"file_path\":\"$DRAFT\"}" | jq

# 5. Promote
curl -s -X POST http://localhost:8000/api/adr/promote \
  -H "Content-Type: application/json" \
  -d "{\"draft_path\":\"$DRAFT\",\"create_pr\":false}" | jq
```

### Working with MCP

```bash
# List projects
curl -s http://localhost:8000/api/mcp/projects | jq

# Get features for project
PROJECT_ID="proj-123"
curl -s "http://localhost:8000/api/mcp/features?project=$PROJECT_ID" | jq

# Submit proposal
curl -s -X POST http://localhost:8000/api/mcp/proposals \
  -H "Content-Type: application/json" \
  -d '{
    "adr_path": "/app/ADR/001-decision.md",
    "feature_ids": ["feat-456"],
    "summary": "Implement feature based on ADR-001",
    "patch_content": null
  }' | jq
```

## Client Libraries

### Python

```python
import httpx

class ADRMasterClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    async def create_draft(self, title, problem, context):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/adr/draft",
                json={"title": title, "problem": problem, "context": context}
            )
            return response.json()
    
    async def lint(self, file_path):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/adr/lint",
                json={"file_path": file_path}
            )
            return response.json()

# Usage
client = ADRMasterClient()
result = await client.create_draft(
    "Use PostgreSQL",
    "Need relational database",
    "Application needs ACID compliance"
)
```

### JavaScript/TypeScript

```typescript
class ADRMasterClient {
  constructor(private baseUrl: string = 'http://localhost:8000') {}
  
  async createDraft(title: string, problem: string, context: string) {
    const response = await fetch(`${this.baseUrl}/api/adr/draft`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({title, problem, context})
    });
    return response.json();
  }
}

// Usage
const client = new ADRMasterClient();
const result = await client.createDraft(
  'Use PostgreSQL',
  'Need relational database',
  'Application needs ACID compliance'
);
```

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can:
- Browse all endpoints
- Try out requests
- See request/response schemas
- Download OpenAPI spec
