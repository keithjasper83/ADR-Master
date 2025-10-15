"""Plugin API routes."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from app.plugins.manager import get_plugin_manager

router = APIRouter(prefix="/api/plugins", tags=["plugins"])


class PluginCommandRequest(BaseModel):
    """Request model for plugin command."""
    command: str
    parameters: Dict[str, Any] = {}


@router.get("/")
async def list_plugins():
    """List all loaded plugins."""
    plugin_manager = get_plugin_manager()
    return plugin_manager.list_plugins()


@router.post("/load")
async def load_plugins():
    """Load all plugins from plugin directory."""
    plugin_manager = get_plugin_manager()
    await plugin_manager.load_plugins()
    return {
        "success": True,
        "plugins": plugin_manager.list_plugins()
    }


@router.post("/{plugin_name}/reload")
async def reload_plugin(plugin_name: str):
    """Reload a specific plugin."""
    plugin_manager = get_plugin_manager()
    success = await plugin_manager.reload_plugin(plugin_name)
    
    if not success:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    return {"success": True}


@router.post("/{plugin_name}/enable")
async def enable_plugin(plugin_name: str):
    """Enable a plugin."""
    plugin_manager = get_plugin_manager()
    success = plugin_manager.enable_plugin(plugin_name)
    
    if not success:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    return {"success": True}


@router.post("/{plugin_name}/disable")
async def disable_plugin(plugin_name: str):
    """Disable a plugin."""
    plugin_manager = get_plugin_manager()
    success = plugin_manager.disable_plugin(plugin_name)
    
    if not success:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    return {"success": True}


@router.post("/{plugin_name}/command")
async def execute_plugin_command(
    plugin_name: str,
    request: PluginCommandRequest
):
    """Execute a custom command on a plugin."""
    plugin_manager = get_plugin_manager()
    result = await plugin_manager.execute_plugin_command(
        plugin_name,
        request.command,
        **request.parameters
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result
