"""
FastAPI + RabbitMQ Configuration
Environment-based configuration for the research agent API
"""

import os
from typing import Optional
from pydantic import BaseSettings


class APISettings(BaseSettings):
    """API configuration settings"""
    
    # FastAPI settings
    app_name: str = "LangChain Research Agent API"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # CORS settings
    cors_origins: list = ["*"]
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    # API limits
    max_query_length: int = 1000
    max_concurrent_tasks: int = 10
    task_timeout_seconds: int = 300  # 5 minutes
    
    # RabbitMQ settings
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_username: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "/"
    rabbitmq_connection_timeout: int = 30
    rabbitmq_heartbeat: int = 600
    
    # Queue names
    research_queue: str = "research_tasks"
    results_queue: str = "research_results"
    exchange_name: str = "research_exchange"
    
    # Redis settings (for task result storage)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Research agent settings
    default_max_iterations: int = 10
    default_priority: str = "normal"
    enable_file_generation: bool = True
    enable_source_citations: bool = True
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security settings
    api_key_header: str = "X-API-Key"
    require_api_key: bool = False
    allowed_api_keys: list = []
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class DevelopmentSettings(APISettings):
    """Development environment settings"""
    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"


class ProductionSettings(APISettings):
    """Production environment settings"""
    debug: bool = False
    reload: bool = False
    log_level: str = "WARNING"
    require_api_key: bool = True
    cors_origins: list = []  # Restrict CORS in production


class TestingSettings(APISettings):
    """Testing environment settings"""
    debug: bool = True
    rabbitmq_host: str = "localhost"
    redis_host: str = "localhost"
    max_concurrent_tasks: int = 5
    task_timeout_seconds: int = 60


def get_settings() -> APISettings:
    """
    Get configuration settings based on environment
    
    Returns:
        APISettings instance based on ENVIRONMENT variable
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()


# Environment variables documentation
ENV_VARS_DOCS = """
Environment Variables for FastAPI Research Agent API:

# FastAPI Settings
APP_NAME=LangChain Research Agent API
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8000
RELOAD=false

# RabbitMQ Settings
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
RABBITMQ_CONNECTION_TIMEOUT=30
RABBITMQ_HEARTBEAT=600

# Queue Configuration
RESEARCH_QUEUE=research_tasks
RESULTS_QUEUE=research_results
EXCHANGE_NAME=research_exchange

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Research Agent Settings
DEFAULT_MAX_ITERATIONS=10
DEFAULT_PRIORITY=normal
ENABLE_FILE_GENERATION=true
ENABLE_SOURCE_CITATIONS=true

# API Limits
MAX_QUERY_LENGTH=1000
MAX_CONCURRENT_TASKS=10
TASK_TIMEOUT_SECONDS=300

# Security Settings
REQUIRE_API_KEY=false
API_KEY_HEADER=X-API-Key
ALLOWED_API_KEYS=key1,key2,key3

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Environment
ENVIRONMENT=development  # development, production, testing
"""


def print_env_docs():
    """Print environment variables documentation"""
    print(ENV_VARS_DOCS)


if __name__ == "__main__":
    print_env_docs()
    print("\nCurrent Settings:")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Debug: {settings.debug}")
    print(f"Host: {settings.host}:{settings.port}")
    print(f"RabbitMQ: {settings.rabbitmq_host}:{settings.rabbitmq_port}")
    print(f"Redis: {settings.redis_host}:{settings.redis_port}")