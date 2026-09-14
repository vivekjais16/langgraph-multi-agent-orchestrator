"""
Base Agent Definition and LLM Inference Abstraction
Author: Vivek Jaiswal <vivekjais16@gmail.com>
Senior Software Engineer — Python | Django | FastAPI | Generative AI & Agentic AI
"""

from typing import Dict, Any, List, Optional
from orchestrator.config.settings import settings
from orchestrator.config.schemas import AgentRole, AgentThought


class BaseAgent:
    """Base class providing shared reasoning and execution primitives for graph nodes."""

    def __init__(self, role: AgentRole, system_prompt: str):
        self.role = role
        self.system_prompt = system_prompt

    def create_thought(
        self,
        thought: str,
        action: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_input: Optional[Dict[str, Any]] = None,
        tool_output: Optional[Dict[str, Any]] = None,
    ) -> AgentThought:
        """Construct a structured trace event for state propagation."""
        return AgentThought(
            agent=self.role,
            thought=thought,
            action_taken=action,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
        )
