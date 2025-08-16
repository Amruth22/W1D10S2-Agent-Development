#!/usr/bin/env python3
"""
FastAPI Research Agent Startup Script
Launches the FastAPI application with RabbitMQ integration
"""

import asyncio
import uvicorn
import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from api.config import settings
from api.message_queue import run_consumer


def run_api_server():
    """Run the FastAPI server"""
    print("Starting FastAPI Research Agent API Server...")
    print(f"Server will run at: http://{settings.host}:{settings.port}")
    print(f"API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"RabbitMQ: {settings.rabbitmq_host}:{settings.rabbitmq_port}")
    print()
    
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        access_log=True,
        workers=1 if settings.reload else 4
    )


def run_consumer_only():
    """Run only the RabbitMQ consumer"""
    print("Starting RabbitMQ Research Task Consumer...")
    print(f"Connecting to: {settings.rabbitmq_host}:{settings.rabbitmq_port}")
    print("Press Ctrl+C to stop")
    print()
    
    asyncio.run(run_consumer())


def show_help():
    """Show help information"""
    help_text = """
LangChain Research Agent API - Startup Options

Usage: python run_api.py [command]

Commands:
  server    - Run FastAPI server (default)
  consumer  - Run RabbitMQ consumer only
  help      - Show this help message

Examples:
  python run_api.py           # Run API server
  python run_api.py server    # Run API server
  python run_api.py consumer  # Run consumer only
  python run_api.py help      # Show help

Environment Variables:
  ENVIRONMENT=development     # development, production, testing
  HOST=0.0.0.0               # API server host
  PORT=8000                  # API server port
  RABBITMQ_HOST=localhost    # RabbitMQ host
  RABBITMQ_PORT=5672         # RabbitMQ port
  DEBUG=true                 # Enable debug mode

Configuration:
  Current environment: {env}
  API server: {host}:{port}
  RabbitMQ: {rabbitmq_host}:{rabbitmq_port}
  Debug mode: {debug}

Documentation:
  API Docs: http://{host}:{port}/docs
  ReDoc: http://{host}:{port}/redoc
  Health Check: http://{host}:{port}/health
""".format(
        env=os.getenv('ENVIRONMENT', 'development'),
        host=settings.host,
        port=settings.port,
        rabbitmq_host=settings.rabbitmq_host,
        rabbitmq_port=settings.rabbitmq_port,
        debug=settings.debug
    )
    
    print(help_text)


def main():
    """Main entry point"""
    # Get command line argument
    command = sys.argv[1] if len(sys.argv) > 1 else "server"
    
    if command == "server":
        run_api_server()
    elif command == "consumer":
        run_consumer_only()
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}")
        print("Use 'python run_api.py help' for available commands")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)