# FastAPI + RabbitMQ Research Agent API

**Professional AI Research Assistant with Asynchronous Processing**

Transform your LangChain Research Agent into a **production-ready, scalable API service** with FastAPI and RabbitMQ integration.

## Architecture Overview

```
Client Request → FastAPI → RabbitMQ → LangChain Agent → Response
     ↓              ↓          ↓           ↓            ↓
   REST API    Queue Tasks  Process    Research     Store Results
```

### Key Components:
- **FastAPI**: High-performance REST API with automatic documentation
- **RabbitMQ**: Message queue for asynchronous task processing
- **LangChain Agent**: Your existing research agent (unchanged)
- **Redis**: Task result storage and caching
- **Docker**: Containerized deployment

## Features

### Production-Ready
- Asynchronous Processing - Non-blocking API responses
- Horizontal Scaling - Multiple consumer workers
- Message Persistence - Reliable task queuing
- Health Monitoring - Built-in health checks
- Auto Documentation - Interactive API docs
- Local Development - Easy setup

### Advanced Capabilities
- Task Status Tracking - Real-time progress updates
- Priority Queues - Urgent vs normal tasks
- WebSocket Support - Live status updates
- File Generation - Research reports with timestamps
- Error Handling - Robust failure management
- CORS Support - Cross-origin requests

## Quick Start

### 1. Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Install RabbitMQ (Ubuntu/Debian)
sudo apt-get install rabbitmq-server

# Or download from: https://www.rabbitmq.com/download.html
```

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

Required Settings:
```env
GEMINI_API_KEY=your-gemini-api-key-here
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
```

### 3. Start the API
```bash
# Method 1: Direct Python
python run_api.py server

# Method 2: Individual components
python run_api.py server    # Terminal 1: API Server
python run_api.py consumer  # Terminal 2: Task Consumer
```

### 4. Access the API
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## API Usage Examples

### Submit Research Request
```bash
curl -X POST "http://localhost:8000/research" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze the latest trends in quantum computing for 2024",
    "priority": "normal",
    "create_report": true,
    "include_sources": true
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
  "query": "Analyze the latest trends in quantum computing for 2024",
  "created_at": "2024-01-16T10:30:00",
  "progress": 50
}
```

### Get Research Results
```bash
curl "http://localhost:8000/research/123e4567-e89b-12d3-a456-426614174000"
```

Response:
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "query": "Analyze the latest trends in quantum computing for 2024",
  "result": "Quantum computing is experiencing rapid advancement in 2024...",
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
    "query": "Research the impact of AI on healthcare industry",
    "priority": "high",
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

## Advanced Configuration

### Environment Variables
```env
# Production Settings
ENVIRONMENT=production
DEBUG=false
REQUIRE_API_KEY=true
ALLOWED_API_KEYS=key1,key2,key3

# Scaling Settings
MAX_CONCURRENT_TASKS=50
TASK_TIMEOUT_SECONDS=600

# RabbitMQ Clustering
RABBITMQ_HOST=rabbitmq-cluster.example.com
RABBITMQ_USERNAME=research_user
RABBITMQ_PASSWORD=secure_password
```

### Production Setup
```bash
# Start multiple consumers for scaling
python run_api.py consumer  # Terminal 1
python run_api.py consumer  # Terminal 2
python run_api.py consumer  # Terminal 3
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
| `WS` | `/ws/{task_id}` | WebSocket status updates |

## Architecture Benefits

### Scalability
- **Horizontal Scaling**: Add more consumer workers
- **Load Distribution**: RabbitMQ distributes tasks evenly
- **Resource Isolation**: API and processing separated

### Reliability
- **Message Persistence**: Tasks survive system restarts
- **Error Recovery**: Failed tasks can be retried
- **Health Monitoring**: Built-in health checks

### Performance
- **Non-blocking**: API responds immediately
- **Concurrent Processing**: Multiple tasks simultaneously
- **Efficient Queuing**: RabbitMQ handles high throughput

### Maintainability
- **Modular Design**: Clear separation of concerns
- **Docker Support**: Easy deployment and scaling
- **Configuration Management**: Environment-based config

## Monitoring & Debugging

### RabbitMQ Management UI
- URL: http://localhost:15672
- Credentials: guest/guest (development)
- Features: Queue monitoring, message tracking, performance metrics

### Health Checks
```bash
# API Health
curl http://localhost:8000/health

# RabbitMQ Health
curl http://localhost:15672/api/healthchecks/node

# Process Status
ps aux | grep python
```

### Logs
```bash
# Check application logs in terminal output
```

## Troubleshooting

### Common Issues

1. RabbitMQ Connection Failed
```bash
# Check RabbitMQ status
sudo systemctl status rabbitmq-server

# Restart RabbitMQ
sudo systemctl restart rabbitmq-server

# Check RabbitMQ logs
sudo journalctl -u rabbitmq-server
```

2. Tasks Stuck in Queue
```bash
# Check consumer process
ps aux | grep "run_api.py consumer"

# Restart consumer
# Stop with Ctrl+C and restart: python run_api.py consumer

# Check queue status in RabbitMQ UI
```

3. API Not Responding
```bash
# Check API process
ps aux | grep "run_api.py server"

# Verify port binding
netstat -tlnp | grep 8000

# Test health endpoint
curl http://localhost:8000/health
```

## Security Considerations

### Production Security
```env
# Enable API key authentication
REQUIRE_API_KEY=true
ALLOWED_API_KEYS=your-secure-api-key

# Restrict CORS origins
CORS_ORIGINS=https://yourdomain.com

# Use secure RabbitMQ credentials
RABBITMQ_USERNAME=secure_user
RABBITMQ_PASSWORD=complex_password
```

### Network Security
- Use HTTPS in production
- Implement rate limiting
- Set up firewall rules
- Use VPN for internal services

## Performance Tuning

### Scaling Guidelines
- API Instances: 1-2 per CPU core
- Consumer Workers: 2-4 per CPU core
- RabbitMQ: Dedicated server for high load
- Storage: Use database for large datasets

### Optimization Tips
```python
# Increase worker processes
uvicorn.run("api.main:app", workers=4)

# Tune RabbitMQ prefetch
await channel.set_qos(prefetch_count=10)

# Use connection pooling
# Implement result caching
```

## Use Cases

### Perfect For:
- Research Platforms - Academic and commercial research
- Content Generation - Automated report creation
- Data Analysis - Large-scale information processing
- Microservices - Part of larger application ecosystem
- API Services - Expose research capabilities to other systems

### Example Applications:
- Market research automation
- Academic paper analysis
- Competitive intelligence
- Content creation pipelines
- Business intelligence systems

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Transform your research agent into a production-ready API service!

Built with FastAPI, RabbitMQ, and LangChain for maximum performance and scalability.