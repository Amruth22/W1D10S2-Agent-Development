"""
Pydantic models for FastAPI Research Agent API
Defines request/response schemas and validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ResearchPriority(str, Enum):
    """Research task priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatusEnum(str, Enum):
    """Task status enumeration"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResearchRequest(BaseModel):
    """Research request model"""
    query: str = Field(
        ...,
        description="Research query or question",
        min_length=3,
        max_length=1000,
        example="Analyze the latest trends in artificial intelligence for 2024"
    )
    priority: ResearchPriority = Field(
        default=ResearchPriority.NORMAL,
        description="Task priority level"
    )
    max_iterations: Optional[int] = Field(
        default=10,
        description="Maximum agent iterations",
        ge=1,
        le=20
    )
    include_sources: bool = Field(
        default=True,
        description="Include source citations in results"
    )
    create_report: bool = Field(
        default=False,
        description="Generate a formatted research report"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Research the impact of quantum computing on cybersecurity",
                "priority": "normal",
                "max_iterations": 10,
                "include_sources": True,
                "create_report": True
            }
        }


class ResearchResponse(BaseModel):
    """Research response model"""
    task_id: str = Field(
        ...,
        description="Unique task identifier"
    )
    status: TaskStatusEnum = Field(
        ...,
        description="Current task status"
    )
    message: str = Field(
        ...,
        description="Response message"
    )
    estimated_time: Optional[str] = Field(
        None,
        description="Estimated completion time"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "queued",
                "message": "Research request submitted successfully",
                "estimated_time": "30-120 seconds"
            }
        }


class TaskStatus(BaseModel):
    """Task status model"""
    task_id: str = Field(
        ...,
        description="Unique task identifier"
    )
    status: TaskStatusEnum = Field(
        ...,
        description="Current task status"
    )
    query: str = Field(
        ...,
        description="Original research query"
    )
    created_at: str = Field(
        ...,
        description="Task creation timestamp"
    )
    completed_at: Optional[str] = Field(
        None,
        description="Task completion timestamp"
    )
    progress: int = Field(
        ...,
        description="Progress percentage (0-100)",
        ge=0,
        le=100
    )
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "processing",
                "query": "Research quantum computing trends",
                "created_at": "2024-01-16T10:30:00",
                "completed_at": None,
                "progress": 50
            }
        }


class ResearchResult(BaseModel):
    """Research result model"""
    task_id: str = Field(
        ...,
        description="Unique task identifier"
    )
    status: TaskStatusEnum = Field(
        ...,
        description="Task status"
    )
    query: str = Field(
        ...,
        description="Original research query"
    )
    result: Optional[str] = Field(
        None,
        description="Research findings and analysis"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if task failed"
    )
    created_at: str = Field(
        ...,
        description="Task creation timestamp"
    )
    completed_at: Optional[str] = Field(
        None,
        description="Task completion timestamp"
    )
    files_generated: Optional[List[str]] = Field(
        default_factory=list,
        description="List of generated report files"
    )
    sources: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Research sources and citations"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "completed",
                "query": "Research quantum computing trends",
                "result": "Quantum computing is experiencing rapid advancement...",
                "error": None,
                "created_at": "2024-01-16T10:30:00",
                "completed_at": "2024-01-16T10:32:15",
                "files_generated": ["quantum_computing_report_20240116_103215.md"],
                "sources": []
            }
        }


class TaskList(BaseModel):
    """Task list model"""
    total_tasks: int = Field(
        ...,
        description="Total number of tasks"
    )
    tasks: List[Dict[str, Any]] = Field(
        ...,
        description="List of tasks with basic information"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "total_tasks": 3,
                "tasks": [
                    {
                        "task_id": "123e4567-e89b-12d3-a456-426614174000",
                        "status": "completed",
                        "query": "Research quantum computing trends",
                        "created_at": "2024-01-16T10:30:00"
                    }
                ]
            }
        }


class HealthCheck(BaseModel):
    """Health check model"""
    status: str = Field(
        ...,
        description="Service health status"
    )
    timestamp: str = Field(
        ...,
        description="Health check timestamp"
    )
    rabbitmq_connected: bool = Field(
        ...,
        description="RabbitMQ connection status"
    )
    agent_available: bool = Field(
        ...,
        description="Research agent availability"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-16T10:30:00",
                "rabbitmq_connected": True,
                "agent_available": True
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(
        ...,
        description="Error message"
    )
    error_code: Optional[str] = Field(
        None,
        description="Specific error code"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Error timestamp"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Task not found",
                "error_code": "TASK_NOT_FOUND",
                "timestamp": "2024-01-16T10:30:00"
            }
        }


class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    task_id: str = Field(
        ...,
        description="Task identifier"
    )
    status: TaskStatusEnum = Field(
        ...,
        description="Current task status"
    )
    progress: int = Field(
        ...,
        description="Progress percentage",
        ge=0,
        le=100
    )
    timestamp: str = Field(
        ...,
        description="Message timestamp"
    )
    message: Optional[str] = Field(
        None,
        description="Optional status message"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "processing",
                "progress": 75,
                "timestamp": "2024-01-16T10:30:00",
                "message": "Analyzing research data..."
            }
        }