"""Base plugin interface."""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from abc import ABC, abstractmethod


class PluginMetadata(BaseModel):
    """Plugin metadata."""
    name: str
    version: str
    description: str
    author: Optional[str] = None
    enabled: bool = True


class Plugin(ABC):
    """Base plugin class."""
    
    def __init__(self):
        """Initialize plugin."""
        self.metadata = self.get_metadata()
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass
    
    async def on_load(self) -> None:
        """Called when plugin is loaded."""
        pass
    
    async def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        pass
    
    async def on_adr_create(self, adr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called when ADR is created."""
        return adr_data
    
    async def on_adr_update(self, adr_id: int, adr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called when ADR is updated."""
        return adr_data
    
    async def on_adr_lint(self, adr_id: int, issues: list) -> list:
        """Hook called when ADR is linted."""
        return issues
    
    async def on_job_create(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called when job is created."""
        return job_data
    
    async def on_job_complete(self, job_id: int, result: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called when job is completed."""
        return result
    
    async def execute_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute a custom plugin command."""
        return {
            "success": False,
            "error": "Command not implemented"
        }
