"""
LangChain-based AI Research Agent
Demonstrates proper agent framework usage with ReAct pattern
"""

from langchain.agents import AgentType, initialize_agent, AgentExecutor
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM as CoreLLM
from langchain.tools import BaseTool
from google import genai
from google.genai import types
from typing import Optional, List, Any, Dict
import json
import os
from datetime import datetime

# Import working tools instead
# from tools.web_search_tool import GeminiWebSearchTool
# from tools.calculator_tool import CalculatorTool
# from tools.file_operations_tool import FileOperationsTool
from memory.conversation_memory import ResearchAgentMemory
from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_ITERATIONS, VERBOSE, REPORTS_DIR, DATA_DIR


class GeminiLLM(CoreLLM):
    """
    Custom LangChain LLM wrapper for Gemini 2.5 Flash
    Integrates Gemini with LangChain's agent framework
    """
    
    def __init__(self):
        super().__init__()
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'client', genai.Client(api_key=GEMINI_API_KEY))
        object.__setattr__(self, 'model', GEMINI_MODEL)
    
    @property
    def _llm_type(self) -> str:
        return "gemini-2.5-flash"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call Gemini API and return response"""
        try:
            # Add system instruction to prevent hallucination  
            system_instruction = """You are an AI research agent that uses tools. CRITICAL RULES:
1. When you need to use a tool, output ONLY the Action and Action Input
2. Do NOT generate fake observations or responses  
3. Stop immediately after outputting Action Input
4. Wait for the actual tool result before continuing

Format your response exactly like this:
Thought: [your reasoning]
Action: [tool_name]  
Action Input: [input_for_tool]

Then STOP. Do not continue writing."""

            if "Action:" in prompt:
                # If this is a tool execution prompt, add strict instruction
                enhanced_prompt = system_instruction + "\n\n" + prompt
            else:
                enhanced_prompt = prompt
                
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=enhanced_prompt)],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            )
            
            response_text = ""
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                if chunk.text:
                    response_text += chunk.text
            
            return response_text
            
        except Exception as e:
            return f"Error calling Gemini: {str(e)}"


class LangChainResearchAgent:
    """
    Advanced AI Research Agent using LangChain framework
    
    Features:
    - LangChain ReAct agent with proper tool integration
    - Gemini 2.5 Flash as the reasoning engine
    - Structured memory management
    - Professional tool ecosystem
    - Comprehensive research capabilities
    """
    
    def __init__(self):
        """Initialize the LangChain research agent"""
        # Initialize LLM
        self.llm = GeminiLLM()
        
        # Initialize working tools
        self.tools = self._create_working_tools()
        
        # Initialize enhanced memory
        self.memory = ResearchAgentMemory()
        
        # Create directories
        self._ensure_directories()
        
        # Initialize LangChain ReAct agent (without memory for now)
        # Use standard agent with enhanced prompting to prevent hallucination
        self.agent_executor = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=VERBOSE,
            max_iterations=MAX_ITERATIONS,
            handle_parsing_errors=True
        )
    
    def _ensure_directories(self):
        """Create necessary directories"""
        # Import config values at runtime to get current values
        from config import REPORTS_DIR as current_reports_dir, DATA_DIR as current_data_dir
        for directory in [current_reports_dir, current_data_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def _create_working_tools(self):
        """Create working tool implementations"""
        class WorkingWebSearchTool(BaseTool):
            name: str = "web_search"
            description: str = "Search the internet for current information. Input: search query"
            
            def __init__(self):
                super().__init__()
                object.__setattr__(self, 'client', genai.Client(api_key=GEMINI_API_KEY))
            
            def _run(self, query: str) -> str:
                try:
                    contents = [types.Content(role="user", parts=[types.Part.from_text(text=f"Search for: {query}")])]
                    tools = [types.Tool(googleSearch=types.GoogleSearch())]
                    config = types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                        tools=tools,
                    )
                    
                    response_text = ""
                    for chunk in self.client.models.generate_content_stream(
                        model=GEMINI_MODEL, contents=contents, config=config
                    ):
                        if chunk.text:
                            response_text += chunk.text
                    return response_text
                except Exception as e:
                    return f"Search error: {str(e)}"
        
        class WorkingCalculatorTool(BaseTool):
            name: str = "calculator"
            description: str = "Perform mathematical calculations. Input: mathematical expression"
            
            def _run(self, expression: str) -> str:
                try:
                    # Handle common calculations
                    if "%" in expression and "of" in expression:
                        parts = expression.replace("%", "").split("of")
                        if len(parts) == 2:
                            percentage = float(parts[0].strip())
                            value = float(parts[1].strip())
                            result = (percentage / 100) * value
                            return f"{percentage}% of {value} = {result}"
                    
                    # Simple math evaluation (safe)
                    import re
                    safe_expr = re.sub(r'[a-zA-Z\s]', '', expression)
                    safe_expr = safe_expr.replace('^', '**')
                    
                    if safe_expr.strip():
                        result = eval(safe_expr, {"__builtins__": {}}, {})
                        return f"Result: {result}"
                    
                    return f"Cannot calculate: {expression}"
                except Exception as e:
                    return f"Calculation error: {str(e)}"
        
        class WorkingFileOperationsTool(BaseTool):
            name: str = "file_operations"
            description: str = "Create research reports. Input format: 'create_report:title:content'"
            
            def _run(self, command: str) -> str:
                print(f"[FILE TOOL] Executing: {command}")
                try:
                    if command.startswith("create_report:"):
                        parts = command.split(":", 2)
                        if len(parts) >= 3:
                            title = parts[1]
                            content = parts[2]
                            
                            print(f"[FILE TOOL] Creating report '{title}'")
                            
                            # Create reports directory using current config
                            from config import REPORTS_DIR as current_reports_dir
                            os.makedirs(current_reports_dir, exist_ok=True)
                            
                            # Generate filename
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{title.replace(' ', '_')}_{timestamp}.md"
                            filepath = os.path.join(current_reports_dir, filename)
                            
                            # Create report
                            report_content = f"""# {title}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Research Findings

{content}

---
*Generated by LangChain Research Agent*
"""
                            
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(report_content)
                            
                            # Verify file was actually created
                            if os.path.exists(filepath):
                                result = f"SUCCESS: Report '{title}' created at {filepath}"
                                print(f"[FILE TOOL] {result}")
                                return result
                            else:
                                error = f"FAILED: Could not create report at {filepath}"
                                print(f"[FILE TOOL] {error}")
                                return error
                    
                    return "Use format: create_report:title:content"
                except Exception as e:
                    error_msg = f"File operation error: {str(e)}"
                    print(f"[FILE TOOL] ERROR: {error_msg}")
                    return error_msg
        
        return [
            WorkingWebSearchTool(),
            WorkingCalculatorTool(),
            WorkingFileOperationsTool()
        ]
    
    def _get_agent_prefix(self) -> str:
        """Get the agent system prompt prefix"""
        return """You are an intelligent AI Research Agent powered by LangChain framework. Your mission is to conduct thorough, accurate research on any topic and provide comprehensive insights.

CAPABILITIES:
- Web Search: Access current information from the internet
- Data Analysis: Perform mathematical calculations and statistical analysis  
- Report Generation: Create professional research reports
- Memory: Maintain conversation context and build upon previous research

RESEARCH METHODOLOGY:
1. UNDERSTAND the user's research request thoroughly
2. PLAN your research approach using multiple information sources
3. SEARCH for current, reliable information using web search
4. ANALYZE data and perform calculations when needed
5. SYNTHESIZE findings into coherent insights
6. GENERATE reports for comprehensive research

BEST PRACTICES:
- Always verify important facts with multiple searches
- Use specific, targeted search queries for better results
- Provide sources and citations when possible
- Break complex research into manageable steps
- Build upon previous conversation context
- Create reports for substantial research findings

Remember: You are using the LangChain framework to demonstrate professional agent development practices."""
    
    def _get_agent_suffix(self) -> str:
        """Get the agent prompt suffix"""
        return """
Research Context:
{research_context}

Current Request: {input}

Conversation History:
{chat_history}

Think step by step about how to best research this topic.

{agent_scratchpad}"""
    
    def research(self, query: str) -> str:
        """
        Main research method using LangChain agent
        
        Args:
            query: Research question or topic
            
        Returns:
            Comprehensive research response
        """
        try:
            # Add user message to memory
            self.memory.add_user_message(query)
            
            # Execute research using LangChain agent
            print(f"Starting LangChain research: {query}")
            
            # Use the invoke method that we know works
            response = self.agent_executor.invoke({"input": query})
            result = response.get("output", str(response))
            
            # Add response to memory
            self.memory.add_ai_message(result)
            
            return result
            
        except Exception as e:
            error_msg = f"Research error: {str(e)}"
            self.memory.add_ai_message(error_msg)
            return error_msg
    
    def get_conversation_history(self) -> str:
        """Get formatted conversation history"""
        return self.memory.get_formatted_history()
    
    def get_research_context(self) -> str:
        """Get current research context"""
        return self.memory.get_research_context()
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear_memory()
        print("Memory cleared!")
    
    def get_available_tools(self) -> Dict[str, str]:
        """Get list of available tools and their descriptions"""
        return {tool.name: tool.description for tool in self.tools}
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return self.memory.get_memory_stats()
    
    def list_generated_files(self) -> str:
        """List files generated during research"""
        files_info = []
        
        for directory in [REPORTS_DIR, DATA_DIR]:
            if os.path.exists(directory):
                files = os.listdir(directory)
                if files:
                    files_info.append(f"\n{directory.upper()} ({len(files)} files):")
                    for file in sorted(files)[-5:]:  # Show last 5 files
                        filepath = os.path.join(directory, file)
                        size = os.path.getsize(filepath)
                        modified = os.path.getmtime(filepath)
                        from datetime import datetime
                        mod_time = datetime.fromtimestamp(modified)
                        files_info.append(f"  {file} ({size} bytes, {mod_time.strftime('%Y-%m-%d %H:%M')})")
                else:
                    files_info.append(f"\n{directory.upper()}: empty")
        
        return "\n".join(files_info) if files_info else "No files generated yet"
    
    def update_session_summary(self, summary: str):
        """Update the session summary with key findings"""
        self.memory.update_session_summary(summary)
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent configuration"""
        return {
            "framework": "LangChain",
            "llm": "Gemini 2.5 Flash",
            "agent_type": "ZERO_SHOT_REACT_DESCRIPTION",
            "max_iterations": MAX_ITERATIONS,
            "tools_count": len(self.tools),
            "tools": [tool.name for tool in self.tools],
            "memory_type": "ConversationBufferWindowMemory",
            "verbose": VERBOSE
        }