"""
Data Schemas and Contracts for LangGraph Multi-Agent Orchestrator
Author: Vivek Jaiswal <vivekjais16@gmail.com>
Senior Software Engineer — Python | Django | FastAPI | Generative AI & Agentic AI
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    SUPERVISOR = "supervisor"
    RESEARCHER = "researcher"
    CODER = "coder"
    CRITIC = "critic"
    SYSTEM = "system"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    REQUIRES_CORRECTION = "requires_correction"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentThought(BaseModel):
    """Structured thought emitted by an agent node during state transitions."""
    agent: AgentRole
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    thought: str
    action_taken: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None


class CritiqueResult(BaseModel):
    """Critique analysis evaluated by the reflection node."""
    score: float = Field(..., ge=0.0, le=1.0, description="Quality score from 0.0 to 1.0")
    passed: bool
    feedback: str
    suggested_improvements: List[str] = Field(default_factory=list)


class OrchestrationRequest(BaseModel):
    """Incoming user execution request."""
    task: str = Field(..., min_length=3, description="Goal or question for multi-agent execution")
    thread_id: Optional[str] = Field(None, description="Thread ID for persistent memory checkpointing")
    stream: bool = Field(default=False, description="Whether to stream token events over WebSocket")


class OrchestrationResponse(BaseModel):
    """Complete summary response of the multi-agent graph run."""
    thread_id: str
    status: TaskStatus
    original_task: str
    final_output: str
    correction_cycles: int
    critique_score: float
    execution_trace: List[AgentThought] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
