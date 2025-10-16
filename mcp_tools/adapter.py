"""MCP Tools adapter - thin wrapper around REST endpoints.

This module provides MCP tool definitions that map to our REST API endpoints.
This repo is NOT an MCP server itself - these tools are meant to be
imported and exposed by other MCP servers that want to integrate ADR capabilities.
"""
from typing import Any, Optional

import httpx


class ADRToolsAdapter:
    """Adapter exposing ADR functions as MCP-compatible tools."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize adapter with ADR-Master API base URL."""
        self.base_url = base_url

    async def adr_generate(
        self, title: str, problem: str, context: str, options: Optional[str] = None
    ) -> dict[str, Any]:
        """Generate a new ADR draft.

        Args:
            title: ADR title
            problem: Problem statement
            context: Context and background
            options: Optional considered options

        Returns:
            dict with draft_path, slug, and message
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/adr/draft",
                json={
                    "title": title,
                    "problem": problem,
                    "context": context,
                    "options": options,
                },
            )
            response.raise_for_status()
            return response.json()

    async def adr_compile(self, draft_path: str, human_notes: Optional[str] = None) -> dict[str, Any]:
        """Compile an ADR draft using LLM.

        Args:
            draft_path: Path to draft file
            human_notes: Optional notes for LLM

        Returns:
            dict with job_id and message
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/adr/compile",
                json={"draft_path": draft_path, "human_notes": human_notes},
            )
            response.raise_for_status()
            return response.json()

    async def adr_lint(self, file_path: str) -> dict[str, Any]:
        """Lint an ADR file.

        Args:
            file_path: Path to ADR file

        Returns:
            dict with valid, errors, and warnings
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/adr/lint", json={"file_path": file_path}
            )
            response.raise_for_status()
            return response.json()

    async def adr_promote(self, draft_path: str, create_pr: bool = False) -> dict[str, Any]:
        """Promote an ADR from draft to final.

        Args:
            draft_path: Path to draft file
            create_pr: Whether to create a PR

        Returns:
            dict with final_path, branch, pr_url, and message
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/adr/promote",
                json={"draft_path": draft_path, "create_pr": create_pr},
            )
            response.raise_for_status()
            return response.json()

    async def adr_sync(self, direction: str = "both") -> dict[str, Any]:
        """Sync ADR directories with remote.

        Args:
            direction: Sync direction (pull, push, or both)

        Returns:
            dict with synced_files, conflicts, and message
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/adr/sync", json={"direction": direction}
            )
            response.raise_for_status()
            return response.json()


# MCP Tool Definitions
# These would be registered with an MCP server

MCP_TOOL_DEFINITIONS = [
    {
        "name": "adr.generate",
        "description": "Generate a new ADR draft with MADR template",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "ADR title"},
                "problem": {"type": "string", "description": "Problem statement"},
                "context": {"type": "string", "description": "Context and background"},
                "options": {"type": "string", "description": "Considered options (optional)"},
            },
            "required": ["title", "problem", "context"],
        },
    },
    {
        "name": "adr.compile",
        "description": "Compile an ADR draft using LLM for improvements",
        "inputSchema": {
            "type": "object",
            "properties": {
                "draft_path": {"type": "string", "description": "Path to draft file"},
                "human_notes": {"type": "string", "description": "Optional notes for LLM"},
            },
            "required": ["draft_path"],
        },
    },
    {
        "name": "adr.lint",
        "description": "Validate ADR structure and content",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to ADR file"},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "adr.promote",
        "description": "Promote an ADR from draft to final",
        "inputSchema": {
            "type": "object",
            "properties": {
                "draft_path": {"type": "string", "description": "Path to draft file"},
                "create_pr": {"type": "boolean", "description": "Create GitHub PR (optional)"},
            },
            "required": ["draft_path"],
        },
    },
    {
        "name": "adr.sync",
        "description": "Sync ADR directories with remote repository",
        "inputSchema": {
            "type": "object",
            "properties": {
                "direction": {
                    "type": "string",
                    "enum": ["pull", "push", "both"],
                    "description": "Sync direction",
                },
            },
        },
    },
]
