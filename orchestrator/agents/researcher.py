"""
Researcher Agent Node (MCP Tool Invocation & Knowledge Extraction)
Author: Vivek Jaiswal <vivekjais16@gmail.com>
Senior Software Engineer — Python | Django | FastAPI | Generative AI & Agentic AI
"""

from typing import Dict, Any
from orchestrator.config.schemas import AgentRole
from orchestrator.state.agent_state import AgentState
from orchestrator.agents.base import BaseAgent
from orchestrator.mcp.client import mcp_client


class ResearcherAgent(BaseAgent):
    """Executes semantic search and MCP tool calls to compile contextual research."""

    def __init__(self):
        super().__init__(
            role=AgentRole.RESEARCHER,
            system_prompt="You are the Senior Systems Researcher. Query MCP tools to retrieve technical specifications.",
        )

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        task = state["task"]

        # Call MCP tools
        search_res = mcp_client.call_tool("web_search", {"query": task})
        vector_res = mcp_client.call_tool("vector_search", {"query": task, "collection": "system_design"})

        notes = [
            f"Specification: {search_res['result'].get('snippet')}",
            f"Architecture Guidance: {vector_res['result']['matches'][0]['content']}",
        ]

        thought = self.create_thought(
            thought=f"Retrieved 2 authoritative sources via Model Context Protocol (MCP).",
            action="Compile research notes",
            tool_name="mcp.web_search, mcp.vector_search",
            tool_output={"sources_found": 2, "confidence": 0.95},
        )

        return {
            "research_notes": notes,
            "next_agent": "supervisor",
            "execution_trace": [thought],
        }
