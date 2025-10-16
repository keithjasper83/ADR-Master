# MCP Tools Adapter

This module provides a thin adapter that exposes ADR-Master functionality as MCP tools.

## Important Note

**ADR-Master is NOT an MCP server.** This adapter is provided for **other MCP servers** that want to integrate ADR capabilities.

## Architecture

- ADR-Master: FastAPI application with REST API
- This adapter: Thin wrapper that calls the REST API
- MCP Server (external): Registers these tools and exposes them via MCP protocol

## Usage

### From an MCP Server

```python
from mcp_tools.adapter import ADRToolsAdapter, MCP_TOOL_DEFINITIONS

# Initialize adapter pointing to ADR-Master API
adapter = ADRToolsAdapter(base_url="http://localhost:8000")

# Register tools with your MCP server
for tool_def in MCP_TOOL_DEFINITIONS:
    mcp_server.register_tool(tool_def)

# When tool is called, route to adapter
@mcp_server.on_tool_call("adr.generate")
async def handle_adr_generate(params):
    return await adapter.adr_generate(**params)
```

## Available Tools

### adr.generate
Generate a new ADR draft with MADR template.

**Parameters:**
- `title` (required): ADR title
- `problem` (required): Problem statement
- `context` (required): Context and background
- `options` (optional): Considered options

**Returns:** `{draft_path, slug, message}`

### adr.compile
Compile an ADR draft using LLM for improvements.

**Parameters:**
- `draft_path` (required): Path to draft file
- `human_notes` (optional): Notes for LLM

**Returns:** `{job_id, message}`

### adr.lint
Validate ADR structure and content.

**Parameters:**
- `file_path` (required): Path to ADR file

**Returns:** `{valid, errors, warnings}`

### adr.promote
Promote an ADR from draft to final.

**Parameters:**
- `draft_path` (required): Path to draft file
- `create_pr` (optional): Create GitHub PR

**Returns:** `{final_path, branch, pr_url, message}`

### adr.sync
Sync ADR directories with remote repository.

**Parameters:**
- `direction` (optional): Sync direction (pull, push, or both)

**Returns:** `{synced_files, conflicts, message}`

## Example Integration

See `examples/mcp_server_integration.py` for a complete example of integrating these tools with an MCP server.

## API Endpoint Mapping

| MCP Tool | REST Endpoint |
|----------|---------------|
| adr.generate | POST /api/adr/draft |
| adr.compile | POST /api/adr/compile |
| adr.lint | POST /api/adr/lint |
| adr.promote | POST /api/adr/promote |
| adr.sync | POST /api/adr/sync |

## Requirements

The adapter requires ADR-Master to be running and accessible at the configured base URL.

## License

MIT
