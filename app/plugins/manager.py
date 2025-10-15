"""Plugin manager."""

from typing import Dict, List, Optional, Any
from app.plugins.base import Plugin
import importlib
import os
import sys


class PluginManager:
    """Manages plugins for ADR-Workbench."""
    
    def __init__(self, plugin_dir: str = "./plugins"):
        """Initialize plugin manager."""
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Plugin] = {}
        self._hooks_enabled = True
    
    async def load_plugins(self) -> None:
        """Load all plugins from plugin directory."""
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir, exist_ok=True)
            return
        
        # Add plugin directory to Python path
        if self.plugin_dir not in sys.path:
            sys.path.insert(0, self.plugin_dir)
        
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]
                await self.load_plugin(module_name)
    
    async def load_plugin(self, module_name: str) -> bool:
        """Load a specific plugin."""
        try:
            module = importlib.import_module(module_name)
            
            # Look for Plugin class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Plugin) and 
                    attr != Plugin):
                    plugin = attr()
                    await plugin.on_load()
                    self.plugins[plugin.metadata.name] = plugin
                    print(f"Loaded plugin: {plugin.metadata.name} v{plugin.metadata.version}")
                    return True
            
            return False
        except Exception as e:
            print(f"Failed to load plugin {module_name}: {str(e)}")
            return False
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin."""
        if plugin_name not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_name]
        await plugin.on_unload()
        del self.plugins[plugin_name]
        return True
    
    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a specific plugin."""
        if plugin_name in self.plugins:
            await self.unload_plugin(plugin_name)
        
        # Find module name (simplified - assumes plugin name matches module)
        module_name = plugin_name.lower().replace(' ', '_')
        return await self.load_plugin(module_name)
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a specific plugin."""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins."""
        return [
            {
                "name": plugin.metadata.name,
                "version": plugin.metadata.version,
                "description": plugin.metadata.description,
                "author": plugin.metadata.author,
                "enabled": plugin.metadata.enabled
            }
            for plugin in self.plugins.values()
        ]
    
    async def execute_hook(self, hook_name: str, *args, **kwargs) -> Any:
        """Execute a hook across all enabled plugins."""
        if not self._hooks_enabled:
            return kwargs.get('default_value')
        
        result = kwargs.get('default_value')
        
        for plugin in self.plugins.values():
            if not plugin.metadata.enabled:
                continue
            
            method = getattr(plugin, hook_name, None)
            if method and callable(method):
                try:
                    result = await method(*args, **kwargs)
                except Exception as e:
                    print(f"Plugin {plugin.metadata.name} hook {hook_name} failed: {str(e)}")
        
        return result
    
    async def execute_plugin_command(
        self,
        plugin_name: str,
        command: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a custom command on a specific plugin."""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return {
                "success": False,
                "error": f"Plugin '{plugin_name}' not found"
            }
        
        if not plugin.metadata.enabled:
            return {
                "success": False,
                "error": f"Plugin '{plugin_name}' is disabled"
            }
        
        return await plugin.execute_command(command, **kwargs)
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.metadata.enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.metadata.enabled = False
            return True
        return False


# Singleton instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get or create plugin manager singleton."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
