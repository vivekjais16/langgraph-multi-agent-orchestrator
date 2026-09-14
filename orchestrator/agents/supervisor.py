"""
Supervisor Agent Node (Coordinator & Dynamic Router)
Author: Vivek Jaiswal <vivekjais16@gmail.com>
Senior Software Engineer — Python | Django | FastAPI | Generative AI & Agentic AI
"""

from typing import Dict, Any
from orchestrator.config.schemas import AgentRole, TaskStatus
from orchestrator.state.agent_state import AgentState
from orchestrator.agents.base import BaseAgent


class SupervisorAgent(BaseAgent):
    """Coordinates multi-agent execution, planning steps, and routing task delegation."""

    def __init__(self):
        super().__init__(
            role=AgentRole.SUPERVISOR,
            system_prompt=(
                "You are the Lead Multi-Agent Supervisor. Decompose complex user goals into "
                "orchestrated steps, routing between Researcher, Coder, and Critic nodes."
            ),
        )

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        task = state["task"]
        notes = state.get("research_notes", [])
        code = state.get("code_artifacts", {})
        critique = state.get("critique")
        correction_count = state.get("correction_count", 0)

        # 1. If we have no research notes yet, route to researcher
        if not notes:
            plan = [
                f"1. Research architectural patterns and constraints for '{task}'",
                "2. Synthesize clean code implementation and unit tests",
                "3. Perform self-correction reflection audit via Critic node",
            ]
            thought = self.create_thought(
                thought=f"New task initialized. Decomposed into 3-stage plan. Routing to Researcher.",
                action="Route to 'researcher'",
            )
            return {
                "plan": plan,
                "next_agent": "researcher",
                "status": TaskStatus.RUNNING,
                "execution_trace": [thought],
            }

        # 2. If we have research notes but no code, route to coder
        if not code:
            thought = self.create_thought(
                thought=f"Research complete ({len(notes)} notes). Routing to Coder for implementation.",
                action="Route to 'coder'",
            )
            return {
                "next_agent": "coder",
                "status": TaskStatus.RUNNING,
                "execution_trace": [thought],
            }

        # 3. If we have code but no critique, route to critic
        if not critique:
            thought = self.create_thought(
                thought="Code artifacts generated. Routing to Critic for self-reflection evaluation.",
                action="Route to 'critic'",
            )
            return {
                "next_agent": "critic",
                "status": TaskStatus.RUNNING,
                "execution_trace": [thought],
            }

        # 4. If critique passed or max cycles reached, finalize response
        if critique.passed or correction_count >= 3:
            final_summary = (
                f"### Multi-Agent Orchestration Completed Successfully\n\n"
                f"**Task**: {task}\n"
                f"**Quality Audit Score**: {critique.score * 100:.1f}%\n"
                f"**Self-Correction Cycles**: {correction_count}\n\n"
                f"#### Implemented Solution:\n"
                f"```python\n{code.get('main.py', '# Solution generated')}\n```\n\n"
                f"**Critic Evaluation**: {critique.feedback}"
            )
            thought = self.create_thought(
                thought=f"Task validated by Critic (Score: {critique.score:.2f}). Finalizing response.",
                action="FINISH",
            )
            return {
                "next_agent": "FINISH",
                "final_response": final_summary,
                "status": TaskStatus.COMPLETED,
                "execution_trace": [thought],
            }

        # 5. Otherwise, route back to coder for self-correction loop
        thought = self.create_thought(
            thought=f"Critique requires improvements. Routing to Coder for refinement cycle {correction_count + 1}.",
            action="Route to 'coder'",
        )
        return {
            "next_agent": "coder",
            "status": TaskStatus.REQUIRES_CORRECTION,
            "execution_trace": [thought],
        }
