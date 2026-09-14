"""
Comprehensive Unit & Integration Test Suite for LangGraph Multi-Agent Orchestrator
Author: Vivek Jaiswal <vivekjais16@gmail.com>
Senior Software Engineer — Python | Django | FastAPI | Generative AI & Agentic AI
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from fastapi.testclient import TestClient
from orchestrator.config.schemas import TaskStatus, AgentRole
from orchestrator.mcp.client import mcp_client
from orchestrator.graph.workflow import run_orchestration, agent_graph
from orchestrator.api.server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_mcp_client_tool_registration():
    """Verify MCP tools are discovered with valid schemas."""
    tools = mcp_client.list_tools()
    assert len(tools) >= 3
    tool_names = [t["name"] for t in tools]
    assert "web_search" in tool_names
    assert "code_sandbox" in tool_names
    assert "vector_search" in tool_names


def test_mcp_web_search_and_sandbox_execution():
    """Verify MCP tool calls execute deterministically."""
    search_res = mcp_client.call_tool("web_search", {"query": "LangGraph state machine"})
    assert search_res["status"] == "success"
    assert "LangGraph" in search_res["result"]["snippet"]

    sandbox_res = mcp_client.call_tool("code_sandbox", {"code": "def hello():\n    return 'world'", "language": "python"})
    assert sandbox_res["status"] == "success"
    assert sandbox_res["result"]["success"] is True


@pytest.mark.asyncio
async def test_langgraph_multi_agent_end_to_end_orchestration():
    """Verify end-to-end multi-agent graph execution with reflection validation."""
    task = "Build a high-throughput async pipeline with Redis checkpointer"
    response = await run_orchestration(task, thread_id="test_suite_run_01")

    assert response.thread_id == "test_suite_run_01"
    assert response.status == TaskStatus.COMPLETED
    assert response.critique_score >= 0.85
    assert len(response.execution_trace) >= 4

    # Verify agent sequence: supervisor -> researcher -> coder -> critic -> supervisor
    agents_visited = [t.agent for t in response.execution_trace]
    assert AgentRole.SUPERVISOR in agents_visited
    assert AgentRole.RESEARCHER in agents_visited
    assert AgentRole.CODER in agents_visited
    assert AgentRole.CRITIC in agents_visited


def test_api_health_endpoint(client):
    """Verify backend health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "LangGraph" in data["service"]
    assert "Vivek Jaiswal" in data["author"]


def test_api_mcp_tools_endpoint(client):
    """Verify MCP schemas endpoint."""
    response = client.get("/api/v1/mcp/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) >= 3


def test_api_orchestrate_post_endpoint(client):
    """Verify synchronous REST orchestration endpoint."""
    payload = {
        "task": "Design an MCP tool transport with FastAPI SSE",
        "thread_id": "test_api_thread_101",
    }
    response = client.post("/api/v1/orchestrate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["thread_id"] == "test_api_thread_101"
    assert data["status"] == TaskStatus.COMPLETED
    assert data["critique_score"] >= 0.85
    assert len(data["execution_trace"]) > 0


def test_api_dashboard_html_render(client):
    """Verify Mission Control dashboard HTML renders successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "LangGraph Multi-Agent Orchestrator" in response.text
    assert "Vivek Jaiswal" in response.text
    assert "Mission Control" in response.text
