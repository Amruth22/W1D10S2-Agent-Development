"""
FastAPI Application for LangChain Research Agent
Provides REST API endpoints with RabbitMQ integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import asyncio
import json
from datetime import datetime
import os

# Import our research agent
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.research_agent import LangChainResearchAgent

# Import message queue components
from .message_queue import ResearchTaskPublisher, ResearchTaskConsumer
from .models import ResearchRequest, ResearchResponse, TaskStatus

# Initialize FastAPI app
app = FastAPI(
    title="LangChain Research Agent API",
    description="Professional AI Research Assistant with RabbitMQ integration",
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

# Global components
task_publisher = None
task_results: Dict[str, Dict[str, Any]] = {}  # In-memory storage for demo


@app.on_event("startup")
async def startup_event():
    """Initialize RabbitMQ connections on startup"""
    global task_publisher
    try:
        task_publisher = ResearchTaskPublisher()
        await task_publisher.connect()
        print("✅ FastAPI + RabbitMQ Research Agent API started successfully!")
        print("📚 Available endpoints:")
        print("  • POST /research - Submit research request")
        print("  • GET /research/{task_id} - Get research results")
        print("  • GET /research/{task_id}/status - Get task status")
        print("  • GET /health - Health check")
        print("  • GET /docs - API documentation")
    except Exception as e:
        print(f"❌ Failed to initialize RabbitMQ: {e}")
        print("⚠️  API will run in direct mode (no queue)")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown"""
    global task_publisher
    if task_publisher:
        await task_publisher.close()
    print("👋 FastAPI Research Agent API shutdown complete")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LangChain Research Agent API",
        "version": "1.0.0",
        "framework": "FastAPI + RabbitMQ + LangChain",
        "endpoints": {
            "research": "/research",
            "status": "/research/{task_id}/status",
            "results": "/research/{task_id}",
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
        "rabbitmq_connected": task_publisher is not None and task_publisher.connection is not None,
        "agent_available": True
    }


@app.post("/research", response_model=ResearchResponse)
async def submit_research_request(request: ResearchRequest):
    """
    Submit a research request for asynchronous processing
    
    Args:
        request: Research request with query and optional parameters
        
    Returns:
        ResearchResponse with task_id and status
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Create task data
        task_data = {
            "task_id": task_id,
            "query": request.query,
            "priority": request.priority,
            "max_iterations": request.max_iterations,
            "include_sources": request.include_sources,
            "create_report": request.create_report,
            "timestamp": datetime.now().isoformat()
        }
        
        # Initialize task status
        task_results[task_id] = {
            "status": "queued",
            "query": request.query,
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        
        # Publish to RabbitMQ if available, otherwise process directly
        if task_publisher and task_publisher.connection:
            await task_publisher.publish_research_task(task_data)
            print(f"📤 Research task {task_id} queued: {request.query[:50]}...")
        else:
            # Fallback: process directly in background
            asyncio.create_task(process_research_direct(task_id, request.query))
            print(f"🔄 Research task {task_id} processing directly: {request.query[:50]}...")
        
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
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = task_results[task_id]
    
    return TaskStatus(
        task_id=task_id,
        status=task_data["status"],
        query=task_data["query"],
        created_at=task_data["created_at"],
        completed_at=task_data.get("completed_at"),
        progress=get_task_progress(task_data["status"])
    )


@app.get("/research/{task_id}")
async def get_research_results(task_id: str):
    """
    Get the results of a completed research task
    
    Args:
        task_id: Unique task identifier
        
    Returns:
        Research results or current status
    """
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = task_results[task_id]
    
    if task_data["status"] == "completed":
        return {
            "task_id": task_id,
            "status": "completed",
            "query": task_data["query"],
            "result": task_data["result"],
            "created_at": task_data["created_at"],
            "completed_at": task_data["completed_at"],
            "files_generated": task_data.get("files_generated", [])
        }
    elif task_data["status"] == "failed":
        return {
            "task_id": task_id,
            "status": "failed",
            "query": task_data["query"],
            "error": task_data["error"],
            "created_at": task_data["created_at"],
            "failed_at": task_data.get("completed_at")
        }
    else:
        return {
            "task_id": task_id,
            "status": task_data["status"],
            "query": task_data["query"],
            "message": "Research in progress...",
            "progress": get_task_progress(task_data["status"])
        }


@app.get("/research")
async def list_research_tasks():
    """List all research tasks with their current status"""
    tasks = []
    for task_id, task_data in task_results.items():
        tasks.append({
            "task_id": task_id,
            "status": task_data["status"],
            "query": task_data["query"][:100] + "..." if len(task_data["query"]) > 100 else task_data["query"],
            "created_at": task_data["created_at"]
        })
    
    return {
        "total_tasks": len(tasks),
        "tasks": sorted(tasks, key=lambda x: x["created_at"], reverse=True)
    }


@app.delete("/research/{task_id}")
async def cancel_research_task(task_id: str):
    """Cancel a research task (if still queued)"""
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = task_results[task_id]
    
    if task_data["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed or failed task")
    
    if task_data["status"] == "queued":
        task_results[task_id]["status"] = "cancelled"
        task_results[task_id]["completed_at"] = datetime.now().isoformat()
        return {"message": "Task cancelled successfully"}
    else:
        raise HTTPException(status_code=400, detail="Cannot cancel task in progress")


async def process_research_direct(task_id: str, query: str):
    """
    Process research directly (fallback when RabbitMQ is not available)
    
    Args:
        task_id: Unique task identifier
        query: Research query
    """
    try:
        # Update status to processing
        task_results[task_id]["status"] = "processing"
        
        # Initialize research agent
        agent = LangChainResearchAgent()
        
        # Conduct research
        result = agent.research(query)
        
        # Get generated files
        files_generated = agent.list_generated_files()
        
        # Update task with results
        task_results[task_id].update({
            "status": "completed",
            "result": result,
            "completed_at": datetime.now().isoformat(),
            "files_generated": files_generated.split('\n') if files_generated else []
        })
        
        print(f"✅ Research task {task_id} completed successfully")
        
    except Exception as e:
        # Update task with error
        task_results[task_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })
        
        print(f"❌ Research task {task_id} failed: {str(e)}")


def get_task_progress(status: str) -> int:
    """Get progress percentage based on task status"""
    progress_map = {
        "queued": 0,
        "processing": 50,
        "completed": 100,
        "failed": 100,
        "cancelled": 100
    }
    return progress_map.get(status, 0)


# WebSocket endpoint for real-time updates (optional)
@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket, task_id: str):
    """WebSocket endpoint for real-time task updates"""
    await websocket.accept()
    
    try:
        while True:
            if task_id in task_results:
                task_data = task_results[task_id]
                await websocket.send_json({
                    "task_id": task_id,
                    "status": task_data["status"],
                    "progress": get_task_progress(task_data["status"]),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Close connection if task is completed
                if task_data["status"] in ["completed", "failed", "cancelled"]:
                    break
            
            await asyncio.sleep(2)  # Update every 2 seconds
            
    except Exception as e:
        print(f"WebSocket error for task {task_id}: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )