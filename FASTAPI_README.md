# FastAPI Background Tasks Implementation

Simple FastAPI integration for the LangChain Research Agent using built-in BackgroundTasks - no external dependencies required.

## Features

- **Non-blocking API**: Immediate response with task ID
- **Background Processing**: Research happens in background
- **Task Status Tracking**: Check progress and results
- **No External Dependencies**: Uses FastAPI's built-in BackgroundTasks
- **Simple Setup**: No Redis, RabbitMQ, or Docker needed

## Architecture

```
Client Request → FastAPI → BackgroundTask → LangChain Agent → Results
     ↓              ↓           ↓              ↓            ↓
   REST API    Immediate    Background     Research     In-Memory
              Response     Processing                   Storage
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the API
```bash
python fastapi_app.py
```

### 3. Access the API
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Usage

### Submit Research Request
```bash
curl -X POST "http://localhost:8000/research" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain quantum computing",
    "max_iterations": 10,
    "create_report": false
  }'
```

Response:
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued",
  "message": "Research request submitted successfully",
  "estimated_time": "30-120 seconds"
}
```

### Check Task Status
```bash
curl "http://localhost:8000/research/123e4567-e89b-12d3-a456-426614174000/status"
```

Response:
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "query": "Explain quantum computing",
  "created_at": "2024-01-16T10:30:00",
  "progress": 50
}
```

### Get Results
```bash
curl "http://localhost:8000/research/123e4567-e89b-12d3-a456-426614174000"
```

Response:
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "query": "Explain quantum computing",
  "result": "Quantum computing is a revolutionary technology...",
  "created_at": "2024-01-16T10:30:00",
  "completed_at": "2024-01-16T10:32:15",
  "files_generated": ["quantum_computing_report_20240116_103215.md"]
}
```

## Python Client Example

```python
import requests
import time

# Submit research request
response = requests.post("http://localhost:8000/research", json={
    "query": "What are the benefits of renewable energy?",
    "max_iterations": 10,
    "create_report": True
})

task_data = response.json()
task_id = task_data["task_id"]
print(f"Task submitted: {task_id}")

# Poll for results
while True:
    status_response = requests.get(f"http://localhost:8000/research/{task_id}/status")
    status = status_response.json()
    
    print(f"Status: {status['status']} ({status['progress']}%)")
    
    if status["status"] in ["completed", "failed"]:
        break
    
    time.sleep(5)

# Get final results
if status["status"] == "completed":
    results_response = requests.get(f"http://localhost:8000/research/{task_id}")
    results = results_response.json()
    print(f"Research completed: {results['result'][:100]}...")
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `POST` | `/research` | Submit research request |
| `GET` | `/research/{task_id}` | Get research results |
| `GET` | `/research/{task_id}/status` | Get task status |
| `GET` | `/research` | List all tasks |
| `DELETE` | `/research/{task_id}` | Cancel task |

## Testing

Run the test script:
```bash
# Start the API first
python fastapi_app.py

# In another terminal, run tests
python test_fastapi.py

# Test with custom query
python test_fastapi.py "http://localhost:8000" "Research climate change solutions"
```

## How It Works

1. **Client submits request** → FastAPI receives it
2. **FastAPI creates task ID** → Returns immediately to client
3. **BackgroundTask starts** → Runs research in background
4. **Research agent processes** → Uses existing LangChain agent
5. **Results stored in memory** → Client can check status/results

## Benefits vs External Message Queues

### Advantages
- **No external dependencies** - No Redis/RabbitMQ installation
- **Simple setup** - Just run one Python file
- **Built into FastAPI** - Uses framework's native capabilities
- **Good for development** - Easy testing and debugging

### Limitations
- **Single server only** - Can't distribute across machines
- **Memory storage** - Results lost on restart
- **Limited scaling** - Bound by single process resources

## Production Considerations

For production use, consider:
- **Persistent storage** - Database instead of in-memory
- **Process management** - Use Gunicorn/uWSGI
- **Load balancing** - Multiple API instances
- **Monitoring** - Health checks and logging

## Comparison with Message Queue Version

| Feature | BackgroundTasks | RabbitMQ/Redis |
|---------|----------------|----------------|
| Setup Complexity | Simple | Complex |
| External Dependencies | None | Required |
| Horizontal Scaling | Limited | Excellent |
| Persistence | Memory only | Persistent |
| Development | Easy | Moderate |
| Production | Basic | Enterprise |

## When to Use This

Perfect for:
- **Development and testing**
- **Small to medium workloads**
- **Single server deployments**
- **Quick prototypes**
- **When you can't install external services**

Consider message queues for:
- **High-volume production**
- **Multi-server deployments**
- **Critical task persistence**
- **Enterprise scaling needs**

---

**Simple, effective FastAPI integration without external dependencies!**