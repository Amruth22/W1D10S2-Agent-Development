"""
FastAPI Application with Background Tasks
Simple implementation without external message queues
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid
import asyncio
from datetime import datetime
import os
import sys

# Import our research agent
from agents.research_agent import LangChainResearchAgent

# Initialize FastAPI app
app = FastAPI(
    title="LangChain Research Agent API",
    description="AI Research Assistant with Background Task Processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for task results
task_storage: Dict[str, Dict[str, Any]] = {}


# Pydantic models
class ResearchRequest(BaseModel):
    query: str = Field(
        ...,
        description="Research query or question",
        min_length=3,
        max_length=1000,
        example="Analyze the latest trends in artificial intelligence"
    )
    max_iterations: Optional[int] = Field(
        default=10,
        description="Maximum agent iterations",
        ge=1,
        le=20
    )
    create_report: bool = Field(
        default=False,
        description="Generate a formatted research report"
    )


class ResearchResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_time: Optional[str] = None


class TaskStatus(BaseModel):
    task_id: str
    status: str
    query: str
    created_at: str
    completed_at: Optional[str] = None
    progress: int


class TaskResult(BaseModel):
    task_id: str
    status: str
    query: str
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    files_generated: Optional[List[str]] = None


# Background task function
def process_research_task(task_id: str, query: str, max_iterations: int = 10, create_report: bool = False):
    """
    Background task to process research requests
    
    Args:
        task_id: Unique task identifier
        query: Research query
        max_iterations: Maximum agent iterations
        create_report: Whether to create a report
    """
    try:
        print(f"Starting research task {task_id}: {query[:50]}...")
        
        # Update task status to processing
        task_storage[task_id]["status"] = "processing"
        task_storage[task_id]["progress"] = 25
        
        # Initialize research agent
        agent = LangChainResearchAgent()
        
        # Update progress
        task_storage[task_id]["progress"] = 50
        
        # Conduct research
        result = agent.research(query)
        
        # Update progress
        task_storage[task_id]["progress"] = 75
        
        # Get generated files if any
        files_generated = []
        try:
            files_info = agent.list_generated_files()
            if files_info and files_info != "No files generated yet":
                files_generated = [line.strip() for line in files_info.split('\n') if line.strip() and not line.startswith('REPORTS') and not line.startswith('DATA')]
        except:
            files_generated = []
        
        # Update task with results
        task_storage[task_id].update({
            "status": "completed",
            "result": result,
            "completed_at": datetime.now().isoformat(),
            "files_generated": files_generated,
            "progress": 100
        })
        
        print(f"Research task {task_id} completed successfully")
        
    except Exception as e:
        # Update task with error
        error_msg = str(e)
        task_storage[task_id].update({
            "status": "failed",
            "error": error_msg,
            "completed_at": datetime.now().isoformat(),
            "progress": 100
        })
        
        print(f"Research task {task_id} failed: {error_msg}")


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LangChain Research Agent API",
        "version": "1.0.0",
        "framework": "FastAPI with Background Tasks",
        "endpoints": {
            "research": "/research",
            "status": "/research/{task_id}/status",
            "results": "/research/{task_id}",
            "list": "/research",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_tasks": len([t for t in task_storage.values() if t["status"] == "processing"]),
        "total_tasks": len(task_storage)
    }


@app.post("/research", response_model=ResearchResponse)
async def submit_research_request(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Submit a research request for background processing
    
    Args:
        request: Research request with query and parameters
        background_tasks: FastAPI background tasks
        
    Returns:
        ResearchResponse with task_id and status
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        task_storage[task_id] = {
            "task_id": task_id,
            "status": "queued",
            "query": request.query,
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None,
            "progress": 0,
            "files_generated": []
        }
        
        # Add background task
        background_tasks.add_task(
            process_research_task,
            task_id,
            request.query,
            request.max_iterations,
            request.create_report
        )
        
        print(f"Research task {task_id} queued: {request.query[:50]}...")
        
        return ResearchResponse(
            task_id=task_id,
            status="queued",
            message="Research request submitted successfully",
            estimated_time="30-120 seconds"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit research request: {str(e)}")


@app.get("/research/{task_id}/status", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """
    Get the status of a research task
    
    Args:
        task_id: Unique task identifier
        
    Returns:
        TaskStatus with current status and metadata
    """
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = task_storage[task_id]
    
    return TaskStatus(
        task_id=task_id,
        status=task_data["status"],
        query=task_data["query"],
        created_at=task_data["created_at"],
        completed_at=task_data.get("completed_at"),
        progress=task_data.get("progress", 0)
    )


@app.get("/research/{task_id}", response_model=TaskResult)
async def get_research_results(task_id: str):
    """
    Get the results of a research task
    
    Args:
        task_id: Unique task identifier
        
    Returns:
        TaskResult with research results or current status
    """
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = task_storage[task_id]
    
    return TaskResult(
        task_id=task_id,
        status=task_data["status"],
        query=task_data["query"],
        result=task_data.get("result"),
        error=task_data.get("error"),
        created_at=task_data["created_at"],
        completed_at=task_data.get("completed_at"),
        files_generated=task_data.get("files_generated", [])
    )


@app.get("/research")
async def list_research_tasks():
    """List all research tasks with their current status"""
    tasks = []
    for task_data in task_storage.values():
        tasks.append({
            "task_id": task_data["task_id"],
            "status": task_data["status"],
            "query": task_data["query"][:100] + "..." if len(task_data["query"]) > 100 else task_data["query"],
            "created_at": task_data["created_at"],
            "progress": task_data.get("progress", 0)
        })
    
    return {
        "total_tasks": len(tasks),
        "tasks": sorted(tasks, key=lambda x: x["created_at"], reverse=True)
    }


@app.delete("/research/{task_id}")
async def cancel_research_task(task_id: str):
    """Cancel a research task (if still queued)"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = task_storage[task_id]
    
    if task_data["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed or failed task")
    
    if task_data["status"] == "queued":
        task_storage[task_id]["status"] = "cancelled"
        task_storage[task_id]["completed_at"] = datetime.now().isoformat()
        task_storage[task_id]["progress"] = 100
        return {"message": "Task cancelled successfully"}
    else:
        raise HTTPException(status_code=400, detail="Cannot cancel task in progress")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("FastAPI Research Agent API started successfully!")
    print("Available endpoints:")
    print("  POST /research - Submit research request")
    print("  GET /research/{task_id} - Get research results")
    print("  GET /research/{task_id}/status - Get task status")
    print("  GET /research - List all tasks")
    print("  GET /health - Health check")
    print("  GET /docs - API documentation")
    print(f"Server running at: http://localhost:8000")
    print(f"API Documentation: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    print("FastAPI Research Agent API shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )