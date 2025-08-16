"""
RabbitMQ Message Queue Implementation
Handles asynchronous research task processing
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import aio_pika
from aio_pika import Message, connect_robust, ExchangeType
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.research_agent import LangChainResearchAgent


class RabbitMQConfig:
    """RabbitMQ configuration"""
    
    def __init__(self):
        self.host = os.getenv("RABBITMQ_HOST", "localhost")
        self.port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.username = os.getenv("RABBITMQ_USERNAME", "guest")
        self.password = os.getenv("RABBITMQ_PASSWORD", "guest")
        self.virtual_host = os.getenv("RABBITMQ_VHOST", "/")
        
        # Queue configuration
        self.research_queue = "research_tasks"
        self.results_queue = "research_results"
        self.exchange_name = "research_exchange"
        
        # Connection settings
        self.connection_timeout = 30
        self.heartbeat = 600
        
    @property
    def connection_url(self) -> str:
        """Get RabbitMQ connection URL"""
        return f"amqp://{self.username}:{self.password}@{self.host}:{self.port}{self.virtual_host}"


class ResearchTaskPublisher:
    """
    RabbitMQ publisher for research tasks
    Sends research requests to the queue for processing
    """
    
    def __init__(self, config: Optional[RabbitMQConfig] = None):
        self.config = config or RabbitMQConfig()
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.exchange = None
        
    async def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            print(f"Connecting to RabbitMQ at {self.config.host}:{self.config.port}...")
            
            self.connection = await connect_robust(
                self.config.connection_url,
                timeout=self.config.connection_timeout,
                heartbeat=self.config.heartbeat
            )
            
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)
            
            # Declare exchange
            self.exchange = await self.channel.declare_exchange(
                self.config.exchange_name,
                ExchangeType.DIRECT,
                durable=True
            )
            
            # Declare research queue
            await self.channel.declare_queue(
                self.config.research_queue,
                durable=True
            )
            
            print("RabbitMQ publisher connected successfully!")
            
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def publish_research_task(self, task_data: Dict[str, Any]):
        """
        Publish a research task to the queue
        
        Args:
            task_data: Task information including query, task_id, etc.
        """
        if not self.connection or self.connection.is_closed:
            await self.connect()
        
        try:
            message_body = json.dumps(task_data, default=str)
            
            message = Message(
                message_body.encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                headers={
                    "task_id": task_data["task_id"],
                    "priority": task_data.get("priority", "normal"),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            await self.exchange.publish(
                message,
                routing_key=self.config.research_queue
            )
            
            print(f"Published research task: {task_data['task_id']}")
            
        except Exception as e:
            print(f"Failed to publish task: {e}")
            raise
    
    async def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            print("RabbitMQ publisher connection closed")


class ResearchTaskConsumer:
    """
    RabbitMQ consumer for research tasks
    Processes research requests from the queue
    """
    
    def __init__(self, config: Optional[RabbitMQConfig] = None, result_callback=None):
        self.config = config or RabbitMQConfig()
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.queue: Optional[AbstractQueue] = None
        self.result_callback = result_callback  # Callback to store results
        self.agent: Optional[LangChainResearchAgent] = None
        
    async def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            print(f"Connecting consumer to RabbitMQ at {self.config.host}:{self.config.port}...")
            
            self.connection = await connect_robust(
                self.config.connection_url,
                timeout=self.config.connection_timeout,
                heartbeat=self.config.heartbeat
            )
            
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)
            
            # Declare exchange
            exchange = await self.channel.declare_exchange(
                self.config.exchange_name,
                ExchangeType.DIRECT,
                durable=True
            )
            
            # Declare and bind queue
            self.queue = await self.channel.declare_queue(
                self.config.research_queue,
                durable=True
            )
            
            await self.queue.bind(exchange, routing_key=self.config.research_queue)
            
            # Initialize research agent
            self.agent = LangChainResearchAgent()
            
            print("RabbitMQ consumer connected successfully!")
            
        except Exception as e:
            print(f"Failed to connect consumer to RabbitMQ: {e}")
            raise
    
    async def start_consuming(self):
        """Start consuming research tasks from the queue"""
        if not self.queue:
            await self.connect()
        
        print("Starting to consume research tasks...")
        
        async def process_message(message: aio_pika.IncomingMessage):
            async with message.process():
                await self.process_research_task(message)
        
        await self.queue.consume(process_message)
        
        print("Consumer is running. Waiting for research tasks...")
        
        # Keep the consumer running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            print("Consumer stopped by user")
    
    async def process_research_task(self, message: aio_pika.IncomingMessage):
        """
        Process a research task from the queue
        
        Args:
            message: RabbitMQ message containing task data
        """
        try:
            # Parse task data
            task_data = json.loads(message.body.decode())
            task_id = task_data["task_id"]
            query = task_data["query"]
            
            print(f"Processing research task {task_id}: {query[:50]}...")
            
            # Update task status to processing
            if self.result_callback:
                await self.result_callback(task_id, {
                    "status": "processing",
                    "message": "Research in progress..."
                })
            
            # Conduct research using LangChain agent
            result = self.agent.research(query)
            
            # Get generated files
            files_generated = self.agent.list_generated_files()
            
            # Prepare result data
            result_data = {
                "status": "completed",
                "result": result,
                "completed_at": datetime.now().isoformat(),
                "files_generated": files_generated.split('\n') if files_generated else []
            }
            
            # Store result via callback
            if self.result_callback:
                await self.result_callback(task_id, result_data)
            
            print(f"Research task {task_id} completed successfully")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Research task failed: {error_msg}")
            
            # Store error result
            if self.result_callback:
                await self.result_callback(task_data.get("task_id", "unknown"), {
                    "status": "failed",
                    "error": error_msg,
                    "completed_at": datetime.now().isoformat()
                })
    
    async def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            print("RabbitMQ consumer connection closed")


class ResearchTaskManager:
    """
    High-level manager for research task processing
    Combines publisher and consumer functionality
    """
    
    def __init__(self, config: Optional[RabbitMQConfig] = None):
        self.config = config or RabbitMQConfig()
        self.publisher = ResearchTaskPublisher(self.config)
        self.consumer = None
        self.task_results: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self):
        """Initialize the task manager"""
        await self.publisher.connect()
        
        # Create consumer with result callback
        self.consumer = ResearchTaskConsumer(
            self.config,
            result_callback=self.update_task_result
        )
        await self.consumer.connect()
    
    async def submit_task(self, task_data: Dict[str, Any]) -> str:
        """
        Submit a research task
        
        Args:
            task_data: Task information
            
        Returns:
            Task ID
        """
        task_id = task_data["task_id"]
        
        # Initialize task status
        self.task_results[task_id] = {
            "status": "queued",
            "query": task_data["query"],
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        
        # Publish to queue
        await self.publisher.publish_research_task(task_data)
        
        return task_id
    
    async def update_task_result(self, task_id: str, result_data: Dict[str, Any]):
        """
        Update task result (callback for consumer)
        
        Args:
            task_id: Task identifier
            result_data: Result information
        """
        if task_id in self.task_results:
            self.task_results[task_id].update(result_data)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and results"""
        return self.task_results.get(task_id)
    
    async def start_consumer(self):
        """Start the consumer in background"""
        if self.consumer:
            asyncio.create_task(self.consumer.start_consuming())
    
    async def close(self):
        """Close all connections"""
        await self.publisher.close()
        if self.consumer:
            await self.consumer.close()


# Standalone consumer script
async def run_consumer():
    """Run standalone consumer for processing research tasks"""
    print("Starting RabbitMQ Research Task Consumer...")
    
    # In-memory storage for demo (in production, use Redis/Database)
    task_results = {}
    
    async def store_result(task_id: str, result_data: Dict[str, Any]):
        """Store task result"""
        task_results[task_id] = result_data
        print(f"Stored result for task {task_id}: {result_data['status']}")
    
    consumer = ResearchTaskConsumer(result_callback=store_result)
    
    try:
        await consumer.start_consuming()
    except KeyboardInterrupt:
        print("Consumer stopped")
    finally:
        await consumer.close()


if __name__ == "__main__":
    # Run standalone consumer
    asyncio.run(run_consumer())