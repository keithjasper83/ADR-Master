"""Plugin system for ADR-Workbench."""

from app.plugins.manager import PluginManager
from app.plugins.base import Plugin, PluginMetadata

__all__ = ["PluginManager", "Plugin", "PluginMetadata"]
