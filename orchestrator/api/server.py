"""
FastAPI Real-Time Gateway & WebSocket Server for LangGraph Orchestrator
Author: Vivek Jaiswal <vivekjais16@gmail.com>
Senior Software Engineer — Python | Django | FastAPI | Generative AI & Agentic AI
"""

from typing import List, Dict, Any
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader

from orchestrator.config.settings import settings
from orchestrator.config.schemas import (
    OrchestrationRequest,
    OrchestrationResponse,
    AgentRole,
    TaskStatus,
)
from orchestrator.graph.workflow import run_orchestration, agent_graph
from orchestrator.mcp.client import mcp_client

app = FastAPI(
    title="LangGraph Multi-Agent Orchestrator API",
    version="2.4.0",
    description="Enterprise Multi-Agent Platform with LangGraph, Model Context Protocol (MCP), and Reflection Loops.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """Verify backend and multi-agent graph readiness."""
    return {
        "status": "online",
        "service": "LangGraph Multi-Agent Orchestrator",
        "engine": "LangGraph v0.0.30 StateGraph",
        "mcp_tools_available": len(mcp_client.list_tools()),
        "author": "Vivek Jaiswal <vivekjais16@gmail.com>",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
async def render_dashboard():
    """Serve the real-time agent mission control dashboard."""
    template = jinja_env.get_template("dashboard.html")
    tools = mcp_client.list_tools()
    return HTMLResponse(content=template.render(tools=tools, settings=settings))


@app.get("/api/v1/mcp/tools", tags=["Model Context Protocol"])
async def get_mcp_tools():
    """List registered MCP JSON-RPC tool schemas."""
    return {
        "mcp_version": "2024-11-05",
        "tools": mcp_client.list_tools(),
    }


@app.post("/api/v1/orchestrate", response_model=OrchestrationResponse, status_code=status.HTTP_200_OK, tags=["Orchestration"])
async def orchestrate_task(payload: OrchestrationRequest):
    """Execute the multi-agent state graph with cyclic self-healing reflection loops."""
    try:
        response = await run_orchestration(payload.task, payload.thread_id)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}",
        )


@app.websocket("/ws/orchestrate")
async def websocket_orchestrate(websocket: WebSocket):
    """Real-time WebSocket streaming agent thoughts, MCP tool calls, and reflection evaluations."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            task = data.get("task", "Analyze system architecture")
            thread_id = data.get("thread_id", "ws_session_01")

            await websocket.send_json({
                "type": "GRAPH_STARTED",
                "task": task,
                "thread_id": thread_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            # Execute run
            response = await run_orchestration(task, thread_id)

            # Stream execution trace events
            for thought in response.execution_trace:
                await websocket.send_json({
                    "type": "NODE_TRANSITION",
                    "agent": thought.agent,
                    "thought": thought.thought,
                    "action": thought.action_taken,
                    "tool": thought.tool_name,
                    "output": thought.tool_output,
                    "timestamp": thought.timestamp.isoformat(),
                })
                await asyncio.sleep(0.15)  # Simulated sub-second streaming cadence

            await websocket.send_json({
                "type": "GRAPH_COMPLETED",
                "final_output": response.final_output,
                "critique_score": response.critique_score,
                "correction_cycles": response.correction_cycles,
                "status": response.status,
            })
    except WebSocketDisconnect:
        pass
