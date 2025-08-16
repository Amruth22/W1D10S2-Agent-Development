# LangChain AI Research Agent - Project Structure

## Overview
Professional LangChain-based AI Research Agent with Gemini 2.5 Flash integration.

## Project Structure

```
langchain-research-agent/
├── main.py                     # Main interactive application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── PROJECT_STRUCTURE.md        # This file
├── agents/
│   ├── __init__.py
│   └── research_agent.py       # Core LangChain agent implementation
├── memory/
│   ├── __init__.py
│   └── conversation_memory.py  # Memory management
├── data/                       # Data storage directory
└── reports/                    # Generated research reports
    ├── AI_Research_Fix_Test_20250816_200240.md
    ├── AI_Research_Fix_Test_20250816_200702.md
    └── Impact_of_AI_on_Healthcare_Industry_20250816_200935.md
```

## Key Files

- **main.py**: Interactive command-line interface for the research agent
- **agents/research_agent.py**: Core LangChain agent with embedded tools (web search, calculator, file operations)
- **config.py**: API keys and configuration
- **memory/conversation_memory.py**: Conversation buffer memory management

## Usage

```bash
python main.py
```

## Features

- ✅ Real-time web search and information retrieval
- ✅ Mathematical calculations and data analysis  
- ✅ Professional research report generation
- ✅ Conversation context and research continuity
- ✅ File management and data persistence

## Tools

The agent includes three embedded tools:
1. **Web Search** - Uses Gemini's native Google Search capability
2. **Calculator** - Performs mathematical calculations
3. **File Operations** - Creates and manages research reports

## Agent Framework

- **Framework**: LangChain with ReAct pattern
- **LLM**: Gemini 2.5 Flash  
- **Agent Type**: Zero-shot React Description
- **Memory**: Conversation Buffer Window