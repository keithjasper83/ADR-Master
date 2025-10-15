# MCP Integration Guide

ADR-Master acts as an **MCP client/consumer** to integrate with external MCP servers for project and feature awareness.

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   ADR-Master    │         │   MCP Server    │
│  (MCP Client)   │<------->│   (External)    │
└─────────────────┘         └─────────────────┘
        │                           │
        │ REST API Calls            │
        │                           │
        ├─ GET /projects            │
        ├─ GET /features            │
        └─ POST /proposals          │
```

## Configuration

### Environment Variables

```env
MCP_BASE_URL=http://your-mcp-server:3000/api
MCP_TOKEN=your-authentication-token  # Optional
```

### Testing Connection

```bash
# Check MCP status
curl http://localhost:8000/api/mcp/config

# Expected response:
{
  "mcp_base_url": "http://your-mcp-server:3000/api",
  "has_token": true,
  "connected": true
}
```

## MCP Server Requirements

Your MCP server should implement these endpoints:

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

### GET /projects

List all projects.

**Response:**
```json
{
  "projects": [
    {
      "id": "proj-123",
      "name": "My Project",
      "description": "Project description",
      "metadata": {}
    }
  ]
}
```

### GET /features

List features, optionally filtered by project.

**Query Parameters:**
- `project` (optional): Project ID to filter by

**Response:**
```json
{
  "features": [
    {
      "id": "feat-456",
      "project_id": "proj-123",
      "name": "Feature Name",
      "description": "Feature description",
      "tags": ["tag1", "tag2"],
      "metadata": {}
    }
  ]
}
```

### POST /proposals

Submit a proposal with ADR and optional patch.

**Request:**
```json
{
  "adr_path": "/app/ADR/001-decision.md",
  "feature_ids": ["feat-456", "feat-789"],
  "summary": "Proposal summary",
  "patch_content": "diff --git a/file.py..."
}
```

**Response:**
```json
{
  "proposal_id": "prop-999",
  "status": "submitted"
}
```

## Using MCP Integration

### In the UI

1. **Open ADR-Master**: Navigate to http://localhost:8000
2. **Check connection**: Look at footer for MCP status
3. **Browse projects**: Right panel shows MCP projects
4. **Select project**: Dropdown to filter features
5. **Link features**: Click "Link" to associate features with ADRs
6. **Submit proposals**: Use proposals page to send ADRs upstream

### Via API

#### List Projects

```bash
curl http://localhost:8000/api/mcp/projects
```

#### List Features

```bash
curl "http://localhost:8000/api/mcp/features?project=proj-123"
```

#### Submit Proposal

```bash
curl -X POST http://localhost:8000/api/mcp/proposals \
  -H "Content-Type: application/json" \
  -d '{
    "adr_path": "/app/ADR/001-decision.md",
    "feature_ids": ["feat-456"],
    "summary": "Implement feature using decision from ADR-001",
    "patch_content": null
  }'
```

## Authentication

If your MCP server requires authentication:

```env
MCP_TOKEN=your-jwt-token-or-api-key
```

ADR-Master will send the token as:
```
Authorization: Bearer your-jwt-token-or-api-key
```

## Error Handling

### Connection Failed

```json
{
  "mcp_base_url": "http://your-mcp-server:3000/api",
  "has_token": true,
  "connected": false
}
```

**Troubleshooting:**
1. Check MCP server is running
2. Verify `MCP_BASE_URL` is correct
3. Test endpoint: `curl $MCP_BASE_URL/health`
4. Check firewall/network access

### Authentication Failed

**Error:** 401 Unauthorized

**Solution:**
1. Verify `MCP_TOKEN` is set correctly
2. Check token hasn't expired
3. Confirm token has required permissions

### Feature Not Found

**Error:** 404 Not Found

**Solution:**
1. Ensure project/feature IDs are correct
2. Check user has access to the resource
3. Verify MCP server data is synced

## Working Without MCP

ADR-Master works fully without MCP:

1. Set `MCP_BASE_URL=` (empty)
2. All ADR operations continue normally
3. MCP panel shows "Not configured"
4. Manual feature tracking still possible

## Example MCP Server

Here's a minimal Flask MCP server for testing:

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/projects')
def projects():
    return jsonify({
        "projects": [
            {
                "id": "proj-1",
                "name": "Test Project",
                "description": "A test project",
                "metadata": {}
            }
        ]
    })

@app.route('/api/features')
def features():
    project_id = request.args.get('project')
    return jsonify({
        "features": [
            {
                "id": "feat-1",
                "project_id": "proj-1",
                "name": "Test Feature",
                "description": "A test feature",
                "tags": ["test"],
                "metadata": {}
            }
        ]
    })

@app.route('/api/proposals', methods=['POST'])
def proposals():
    data = request.json
    return jsonify({
        "proposal_id": "prop-1",
        "status": "submitted"
    })

if __name__ == '__main__':
    app.run(port=3000)
```

Run with: `python mcp_server.py`

Then configure ADR-Master:
```env
MCP_BASE_URL=http://localhost:3000/api
```

## Best Practices

1. **Health checks**: Regularly verify MCP connection
2. **Error handling**: Handle MCP unavailability gracefully
3. **Caching**: Consider caching project/feature data
4. **Retry logic**: Implement retries for transient failures
5. **Logging**: Log MCP interactions for debugging

## Security

### Network Security
- Use HTTPS for production MCP servers
- Consider VPN for remote MCP access
- Implement rate limiting

### Authentication
- Use short-lived tokens
- Rotate tokens regularly
- Store tokens securely (environment variables)

### Data Privacy
- Don't send sensitive code in proposals
- Review patch content before submission
- Use private MCP servers for internal projects

## Troubleshooting

### Cannot connect to MCP server

```bash
# Test connectivity
curl -v $MCP_BASE_URL/health

# Check DNS resolution
nslookup your-mcp-server

# Test with authentication
curl -H "Authorization: Bearer $MCP_TOKEN" $MCP_BASE_URL/health
```

### Timeout errors

Increase timeout in code or contact MCP server admin:

```python
# In app/services/mcp_client.py
async with httpx.AsyncClient(timeout=30.0) as client:
    # Increase from default 5.0 to 30.0
```

### Proposal submission fails

1. Check ADR file exists
2. Verify feature IDs are valid
3. Review proposal payload format
4. Check MCP server logs

## Future Enhancements

- [ ] Offline mode with cached MCP data
- [ ] Bidirectional sync (MCP → ADR-Master)
- [ ] Webhook support for MCP events
- [ ] Multiple MCP server support
- [ ] GraphQL support alongside REST

## Support

For MCP integration issues:
- Check MCP server documentation
- Review ADR-Master logs: `./_logs/`
- Test endpoints independently
- Contact MCP server administrators
