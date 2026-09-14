"""
LangGraph Multi-Agent Workflow Definition & Compilation
Author: Vivek Jaiswal <vivekjais16@gmail.com>
Senior Software Engineer — Python | Django | FastAPI | Generative AI & Agentic AI
"""

from typing import Dict, Any, Optional
import uuid
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from orchestrator.config.schemas import TaskStatus, OrchestrationResponse
from orchestrator.state.agent_state import AgentState
from orchestrator.agents.supervisor import SupervisorAgent
from orchestrator.agents.researcher import ResearcherAgent
from orchestrator.agents.coder import CoderAgent
from orchestrator.agents.critic import CriticAgent


def route_supervisor(state: AgentState) -> str:
    """Conditional router resolving next node based on supervisor decision."""
    next_node = state.get("next_agent", "FINISH")
    if next_node == "FINISH":
        return END
    return next_node


def create_orchestrator_graph():
    """Build and compile the multi-agent cyclic state graph."""
    workflow = StateGraph(AgentState)

    # Instantiate Nodes
    supervisor = SupervisorAgent()
    researcher = ResearcherAgent()
    coder = CoderAgent()
    critic = CriticAgent()

    # Add Nodes to Graph
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("researcher", researcher)
    workflow.add_node("coder", coder)
    workflow.add_node("critic", critic)

    # Set Entry Point
    workflow.set_entry_point("supervisor")

    # Dynamic Routing from Supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "researcher": "researcher",
            "coder": "coder",
            "critic": "critic",
            END: END,
        },
    )

    # Worker nodes return back to Supervisor
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("coder", "supervisor")
    workflow.add_edge("critic", "supervisor")

    # Compile with memory checkpointer for conversational threads
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app


# Pre-compiled multi-agent graph
agent_graph = create_orchestrator_graph()


async def run_orchestration(task: str, thread_id: Optional[str] = None) -> OrchestrationResponse:
    """Execute multi-agent graph with thread checkpointing and reflection loop."""
    tid = thread_id or f"thread_{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": tid}}

    initial_state: AgentState = {
        "task": task,
        "thread_id": tid,
        "plan": [],
        "research_notes": [],
        "code_artifacts": {},
        "critique": None,
        "correction_count": 0,
        "execution_trace": [],
        "next_agent": "supervisor",
        "final_response": None,
        "status": TaskStatus.PENDING,
    }

    final_state = await agent_graph.ainvoke(initial_state, config=config)

    critique = final_state.get("critique")
    score = critique.score if critique else 1.0

    return OrchestrationResponse(
        thread_id=tid,
        status=final_state.get("status", TaskStatus.COMPLETED),
        original_task=task,
        final_output=final_state.get("final_response", "Task completed without summary."),
        correction_cycles=final_state.get("correction_count", 0),
        critique_score=score,
        execution_trace=final_state.get("execution_trace", []),
    )
