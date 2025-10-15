"""MCP tool exports for ADR-Workbench."""

from typing import Dict, Any, List, Callable
from app.models.adr import ADR, ADRStatus
from app.services.adr_service import ADRService
from app.services.lint_service import LintService
import json


class MCPToolExporter:
    """Exports ADR-Workbench functionality as MCP tools."""
    
    def __init__(self):
        """Initialize tool exporter."""
        self.tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, Callable]:
        """Register available tools."""
        return {
            "list_adrs": self.list_adrs_tool,
            "get_adr": self.get_adr_tool,
            "create_adr": self.create_adr_tool,
            "lint_adr": self.lint_adr_tool,
            "format_adr": self.format_adr_tool
        }
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions in MCP format."""
        return [
            {
                "name": "list_adrs",
                "description": "List all ADRs with optional status filter",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["draft", "proposed", "accepted", "rejected", "deprecated", "superseded"],
                            "description": "Filter by ADR status"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 100,
                            "description": "Maximum number of ADRs to return"
                        }
                    }
                }
            },
            {
                "name": "get_adr",
                "description": "Get a specific ADR by ID or number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "ADR ID"
                        },
                        "number": {
                            "type": "integer",
                            "description": "ADR number"
                        }
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "create_adr",
                "description": "Create a new ADR",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "ADR title"
                        },
                        "context": {
                            "type": "string",
                            "description": "Context and problem statement"
                        },
                        "decision": {
                            "type": "string",
                            "description": "Decision made"
                        },
                        "consequences": {
                            "type": "string",
                            "description": "Consequences of the decision"
                        }
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "lint_adr",
                "description": "Lint an ADR for issues",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "adr_id": {
                            "type": "integer",
                            "description": "ADR ID to lint"
                        }
                    },
                    "required": ["adr_id"]
                }
            },
            {
                "name": "format_adr",
                "description": "Format an ADR as MADR markdown",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "adr_id": {
                            "type": "integer",
                            "description": "ADR ID to format"
                        }
                    },
                    "required": ["adr_id"]
                }
            }
        ]
    
    async def list_adrs_tool(self, db, **params) -> Dict[str, Any]:
        """List ADRs tool implementation."""
        status = params.get("status")
        limit = params.get("limit", 100)
        
        if status:
            status = ADRStatus(status)
        
        adrs = await ADRService.list_adrs(db, status=status, limit=limit)
        return {
            "success": True,
            "adrs": [adr.to_dict() for adr in adrs]
        }
    
    async def get_adr_tool(self, db, **params) -> Dict[str, Any]:
        """Get ADR tool implementation."""
        adr_id = params.get("id")
        number = params.get("number")
        
        if adr_id:
            adr = await ADRService.get_adr(db, adr_id)
        elif number:
            adr = await ADRService.get_adr_by_number(db, number)
        else:
            return {
                "success": False,
                "error": "Either 'id' or 'number' parameter is required"
            }
        
        if not adr:
            return {
                "success": False,
                "error": "ADR not found"
            }
        
        return {
            "success": True,
            "adr": adr.to_dict()
        }
    
    async def create_adr_tool(self, db, **params) -> Dict[str, Any]:
        """Create ADR tool implementation."""
        title = params.get("title")
        context = params.get("context", "")
        decision = params.get("decision", "")
        consequences = params.get("consequences", "")
        
        adr = await ADRService.create_adr(
            db,
            title=title,
            context=context,
            decision=decision,
            consequences=consequences
        )
        
        return {
            "success": True,
            "adr": adr.to_dict()
        }
    
    async def lint_adr_tool(self, db, **params) -> Dict[str, Any]:
        """Lint ADR tool implementation."""
        adr_id = params.get("adr_id")
        adr = await ADRService.get_adr(db, adr_id)
        
        if not adr:
            return {
                "success": False,
                "error": "ADR not found"
            }
        
        issues = LintService.lint_adr(adr)
        summary = LintService.get_lint_summary(issues)
        
        return {
            "success": True,
            "lint_results": summary
        }
    
    async def format_adr_tool(self, db, **params) -> Dict[str, Any]:
        """Format ADR tool implementation."""
        adr_id = params.get("adr_id")
        adr = await ADRService.get_adr(db, adr_id)
        
        if not adr:
            return {
                "success": False,
                "error": "ADR not found"
            }
        
        markdown = ADRService.format_as_madr(adr)
        
        return {
            "success": True,
            "markdown": markdown
        }
    
    async def execute_tool(self, tool_name: str, db, **params) -> Dict[str, Any]:
        """Execute a tool by name."""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found"
            }
        
        return await self.tools[tool_name](db, **params)
