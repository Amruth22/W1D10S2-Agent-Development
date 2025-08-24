# Configuration for LangChain Research Agent

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

# Tavily API Configuration
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Agent Configuration
MAX_ITERATIONS = 10
VERBOSE = True

# Memory Configuration
CONVERSATION_MEMORY_KEY = "chat_history"
MAX_TOKEN_LIMIT = 2000

# Output directories
REPORTS_DIR = "reports"
DATA_DIR = "data"
