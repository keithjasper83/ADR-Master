"""Example plugin for ADR-Workbench."""

from app.plugins.base import Plugin, PluginMetadata
from typing import Dict, Any


class ExamplePlugin(Plugin):
    """Example plugin that demonstrates the plugin system."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Example Plugin",
            version="1.0.0",
            description="Demonstrates plugin hooks and custom commands",
            author="ADR-Workbench Team",
            enabled=True
        )
    
    async def on_load(self) -> None:
        """Called when plugin is loaded."""
        print(f"[{self.metadata.name}] Plugin loaded successfully!")
    
    async def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        print(f"[{self.metadata.name}] Plugin unloaded")
    
    async def on_adr_create(self, adr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called when ADR is created."""
        print(f"[{self.metadata.name}] ADR created: {adr_data.get('title')}")
        
        # Example: Auto-tag ADRs with certain keywords
        title = adr_data.get('title', '').lower()
        if 'security' in title:
            links = adr_data.get('links', '')
            adr_data['links'] = links + "\n- Tagged: #security"
        
        return adr_data
    
    async def on_adr_lint(self, adr_id: int, issues: list) -> list:
        """Hook called when ADR is linted."""
        print(f"[{self.metadata.name}] Linting ADR {adr_id}, found {len(issues)} issues")
        
        # Example: Add custom lint rule
        # You could inspect the ADR and add custom issues here
        
        return issues
    
    async def execute_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute a custom plugin command."""
        if command == "hello":
            return {
                "success": True,
                "message": f"Hello from {self.metadata.name}!"
            }
        elif command == "stats":
            return {
                "success": True,
                "stats": {
                    "version": self.metadata.version,
                    "enabled": self.metadata.enabled
                }
            }
        else:
            return {
                "success": False,
                "error": f"Unknown command: {command}"
            }
