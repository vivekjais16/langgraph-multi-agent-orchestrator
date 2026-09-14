"""
Model Context Protocol (MCP) Client Transport
Author: Vivek Jaiswal <vivekjais16@gmail.com>
Senior Software Engineer — Python | Django | FastAPI | Generative AI & Agentic AI
"""

from typing import Dict, Any, List, Optional
import json
from orchestrator.config.settings import settings
from orchestrator.mcp.tools import mcp_web_search, mcp_code_sandbox, mcp_vector_search


class ModelContextProtocolClient:
    """Client transport connecting LangGraph agent nodes to standard MCP tool servers."""

    def __init__(self, server_url: Optional[str] = None):
        self.server_url = server_url or settings.MCP_SERVER_URL
        self._local_registry = {
            "web_search": mcp_web_search,
            "code_sandbox": mcp_code_sandbox,
            "vector_search": mcp_vector_search,
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return MCP JSON-RPC tool schemas."""
        return [
            {
                "name": "web_search",
                "description": "Search architectural documentation and benchmarks",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
            {
                "name": "code_sandbox",
                "description": "Execute syntax check and lint analysis on code",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "language": {"type": "string", "default": "python"},
                    },
                    "required": ["code"],
                },
            },
            {
                "name": "vector_search",
                "description": "Perform semantic similarity lookup against vector stores",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "collection": {"type": "string", "default": "engineering_docs"},
                    },
                    "required": ["query"],
                },
            },
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke an MCP tool with standard JSON-RPC response formatting."""
        if name in self._local_registry:
            tool_fn = self._local_registry[name]
            result = tool_fn(**arguments)
            return {
                "jsonrpc": "2.0",
                "tool": name,
                "result": result,
                "status": "success",
            }
        return {
            "jsonrpc": "2.0",
            "tool": name,
            "error": f"Tool '{name}' not found in MCP registry",
            "status": "error",
        }


# Global shared MCP client instance
mcp_client = ModelContextProtocolClient()
