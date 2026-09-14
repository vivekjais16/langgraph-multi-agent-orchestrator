"""
LangGraph StateGraph State Definition
Author: Vivek Jaiswal <vivekjais16@gmail.com>
Senior Software Engineer — Python | Django | FastAPI | Generative AI & Agentic AI
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional
import operator
from orchestrator.config.schemas import AgentThought, CritiqueResult, TaskStatus


class AgentState(TypedDict):
    """
    Central graph state shared and mutated across agent nodes.
    Annotated operator.add ensures concurrent agent thoughts append gracefully.
    """
    task: str
    thread_id: str
    plan: List[str]
    research_notes: List[str]
    code_artifacts: Dict[str, str]
    critique: Optional[CritiqueResult]
    correction_count: int
    execution_trace: Annotated[List[AgentThought], operator.add]
    next_agent: str
    final_response: Optional[str]
    status: TaskStatus
