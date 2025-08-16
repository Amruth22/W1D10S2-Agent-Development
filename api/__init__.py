"""
FastAPI + RabbitMQ Research Agent API Package
Professional AI Research Assistant with asynchronous processing
"""

from .main import app
from .models import (
    ResearchRequest,
    ResearchResponse,
    TaskStatus,
    ResearchResult,
    TaskList,
    HealthCheck,
    ErrorResponse,
    WebSocketMessage,
    ResearchPriority,
    TaskStatusEnum
)
from .message_queue import (
    ResearchTaskPublisher,
    ResearchTaskConsumer,
    ResearchTaskManager,
    RabbitMQConfig
)
from .config import settings, get_settings

__version__ = "1.0.0"
__author__ = "LangChain Research Agent Team"
__description__ = "FastAPI + RabbitMQ integration for LangChain Research Agent"

__all__ = [
    # FastAPI app
    "app",
    
    # Models
    "ResearchRequest",
    "ResearchResponse", 
    "TaskStatus",
    "ResearchResult",
    "TaskList",
    "HealthCheck",
    "ErrorResponse",
    "WebSocketMessage",
    "ResearchPriority",
    "TaskStatusEnum",
    
    # Message Queue
    "ResearchTaskPublisher",
    "ResearchTaskConsumer", 
    "ResearchTaskManager",
    "RabbitMQConfig",
    
    # Configuration
    "settings",
    "get_settings"
]