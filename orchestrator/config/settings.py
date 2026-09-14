"""
Configuration Settings for LangGraph Multi-Agent Orchestrator
Author: Vivek Jaiswal <vivekjais16@gmail.com>
Senior Software Engineer — Python | Django | FastAPI | Generative AI & Agentic AI
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class OrchestratorSettings(BaseSettings):
    """Application-wide settings with environment variable override support."""
    
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # LLM Settings
    OPENAI_API_KEY: Optional[str] = "sk-mock-development-key"
    OPENAI_MODEL: str = "gpt-4-turbo"
    TEMPERATURE: float = 0.2

    # Redis Checkpointer / Memory
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Model Context Protocol (MCP) Transports
    MCP_SERVER_URL: str = "http://localhost:8001/sse"
    MCP_TIMEOUT_SECONDS: float = 15.0

    # Evaluation & Reflection Loop Controls
    CRITIC_PASS_THRESHOLD: float = 0.85
    MAX_CORRECTION_CYCLES: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = OrchestratorSettings()
