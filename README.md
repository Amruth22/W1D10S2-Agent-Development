# 🔍 LangChain AI Research Agent

A **professional-grade AI research assistant** built with the **LangChain framework** and **Gemini 2.5 Flash**, demonstrating enterprise-level agent development practices and design patterns.

**Perfect for learning professional agent framework implementation!** 🎓

## 🎯 Key Features

✅ **Multi-Tool Agent**: Web search + Calculator + Report generation  
✅ **Real Tool Execution**: Actually creates files and performs calculations  
✅ **LangChain ReAct Pattern**: Professional agent orchestration  
✅ **Interactive Interface**: Command-line application with rich features  
✅ **Memory Management**: Context-aware conversation handling  

## 🛠️ Available Tools

Your agent has **3 intelligent tools** that work together:

### 🔍 **Web Search Tool**
- Real-time Google search via Gemini 2.5 Flash
- Current information retrieval and research
- **Example**: `"Search for the latest AI developments"`

### 🧮 **Calculator Tool** 
- Mathematical calculations and financial analysis
- Compound growth, percentages, statistical analysis
- **Example**: `"Calculate 15% compound growth over 10 years"`

### 📄 **File Operations Tool**
- Creates professional research reports in Markdown
- Saves to `reports/` directory with timestamps
- **Example**: `"Create a report on quantum computing trends"`

## 🚀 Quick Start

### 1. **Installation**
```bash
cd langchain-research-agent
pip install -r requirements.txt
```

### 2. **Configuration**
Add your API keys to the `.env` file:
```bash
GEMINI_API_KEY=your-gemini-api-key-here
TAVILY_API_KEY=your-tavily-api-key-here
```

### 3. **Test the Setup**
```bash
python3 unit_test.py
```

### 4. **Run the Agent**
```bash
python main.py
```

## 💡 Example Usage

### **Single Tool Examples**
```
Research Query: What is the current price of Bitcoin?
Research Query: Calculate 25% of 1000
Research Query: Create a report on AI trends
```

### **Multi-Tool Examples** (Agent uses multiple tools automatically)
```
Research Query: Search for Tesla stock price and calculate 30% increase
Research Query: Research EV market size, calculate 20% growth projections, and create a report
Research Query: Find current inflation rate and calculate impact on $50,000 savings
```

### **Interactive Commands**
```
tools    - List available tools
files    - Show generated reports  
history  - View conversation history
stats    - Show memory statistics
clear    - Clear conversation memory
quit     - Exit application
```

## 📁 Project Structure

```
langchain-research-agent/
├── main.py                     # Interactive application (Run this!)
├── config.py                   # Configuration settings
├── requirements.txt            # Dependencies
├── agents/
│   └── research_agent.py       # Core LangChain agent with embedded tools
├── memory/
│   └── conversation_memory.py  # Memory management
├── data/                       # Data storage (empty, ready for use)
└── reports/                    # Generated research reports
    ├── AI_Research_Fix_Test_20250816_200702.md
    ├── Electric_Vehicle_Market_Report_20250816_201552.md
    └── Impact_of_AI_on_Healthcare_Industry_20250816_200935.md
```

## 🎯 Professional Research Examples

### **Market Research**
- `"Research the global AI market size and create a comprehensive analysis report"`
- `"Analyze cryptocurrency adoption trends and calculate growth projections"`
- `"Study renewable energy market growth and project 5-year expansion"`

### **Financial Analysis**
- `"Calculate compound annual growth rate for an investment from $1000 to $2500 over 5 years"`
- `"Find current S&P 500 value and calculate what 12% annual returns would yield"`
- `"Research inflation data and calculate purchasing power impact"`

### **Technical Research**
- `"Research quantum computing developments and create a technical summary"`
- `"Analyze cybersecurity threats in 2025 and generate a report"`
- `"Study electric vehicle battery technology and calculate cost improvements"`

## 🔧 Technical Implementation

### **Environment Configuration**
```python
# Automatic .env loading in config.py
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
```

### **LangChain Agent Architecture**
```python
# Professional ReAct agent with embedded tools
agent_executor = initialize_agent(
    tools=[WebSearchTool(), CalculatorTool(), FileOperationsTool()],
    llm=GeminiLLM(),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=10,
    handle_parsing_errors=True
)
```

### **Smart Testing Architecture**
```python
# Quota-aware testing
if "429 RESOURCE_EXHAUSTED" in response:
    self.skipTest("API quota exceeded - expected behavior")
else:
    # Test real functionality
    self.assertGreater(len(response), 0)
```

### **Gemini 2.5 Flash Integration**
```python
class GeminiLLM(CoreLLM):
    """Custom LangChain wrapper for Gemini 2.5 Flash"""
    
    def _call(self, prompt: str) -> str:
        # Enhanced prompting to prevent tool hallucination
        # Native Google Search integration
        # Streaming response handling
```

### **Embedded Tools Design**
- **No external dependencies**: Tools are embedded in the agent
- **Proper error handling**: Robust exception management
- **Debugging output**: Clear tool execution logging
- **File verification**: Actual file creation with size checking

## 🎓 Learning Value

This implementation demonstrates:

### **LangChain Best Practices**
- ✅ Proper tool schema definition
- ✅ Agent executor configuration  
- ✅ Memory management patterns
- ✅ Error handling strategies

### **Problem Solving**
- ✅ **Fixed tool hallucination**: Agent now actually executes tools instead of faking responses
- ✅ **Proper LLM prompting**: Enhanced system instructions prevent fake observations
- ✅ **Tool debugging**: Clear execution logging to verify real tool usage
- ✅ **Windows compatibility**: Removed Unicode characters that cause terminal issues

### **Professional Development**
- ✅ Modular agent design
- ✅ Configuration management
- ✅ Interactive user interfaces
- ✅ File organization and cleanup

## 🔍 Agent Capabilities

### **Intelligent Tool Selection**
The agent automatically chooses the right tools for each task:
- **Research questions** → Web Search Tool
- **Math problems** → Calculator Tool  
- **Report requests** → File Operations Tool
- **Complex queries** → Multiple tools in sequence

### **Multi-Step Workflows**
Example workflow for: *"Research Bitcoin price, calculate 50% increase, and create analysis report"*

1. **Web Search**: Finds current Bitcoin price ($117,703)
2. **Calculator**: Computes 50% increase ($176,554.50)  
3. **File Operations**: Creates comprehensive analysis report
4. **Memory**: Maintains context throughout the process

### **Context Awareness**
- Remembers previous research within session
- Builds upon earlier findings
- Maintains conversation flow
- Provides relevant follow-up suggestions

## 📊 Example Tool Usage

```bash
# Calculator Tool in Action
Research Query: Calculate compound growth of $1000 at 15% for 5 years

Action: calculator
Action Input: 1000 * (1.15)^5
Observation: Result: 2011.3571875
Final Answer: $1000 growing at 15% annually for 5 years becomes $2,011.36

# Web Search + Calculator Combination  
Research Query: Find current gold price and calculate 20% increase

Action: web_search
Action Input: current gold price
Observation: Current gold price is approximately $2,025 per ounce...

Action: calculator  
Action Input: 2025 * 1.20
Observation: Result: 2430.0
Final Answer: Current gold price is $2,025/oz. A 20% increase would be $2,430/oz.
```

## 🚀 Advanced Usage

### **Programmatic Access**
```python
from agents.research_agent import LangChainResearchAgent

# Initialize agent
agent = LangChainResearchAgent()

# Get agent information
info = agent.get_agent_info()
print(f"Framework: {info['framework']}")  # LangChain
print(f"LLM: {info['llm']}")             # Gemini 2.5 Flash
print(f"Tools: {info['tools']}")         # [web_search, calculator, file_operations]

# Conduct research
result = agent.research("Analyze renewable energy market trends")
print(result)

# Check generated files
files = agent.list_generated_files()
print(files)
```

### **Session Management**
```python
# Memory statistics
stats = agent.get_memory_stats()
print(f"Messages: {stats['total_messages']}")
print(f"Tokens: {stats['total_tokens']}")

# Clear memory for new session
agent.clear_memory()

# Get conversation history
history = agent.get_conversation_history()
```

## 🆘 Troubleshooting

### **Common Issues**

#### **API Quota Exceeded (429 Error)**
```
429 RESOURCE_EXHAUSTED: You exceeded your current quota
```
**Solutions:**
- Wait 24 hours for quota reset
- Get a new Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- Run `python3 unit_test.py` - it handles quota limits gracefully

#### **API Key Issues**
```
Gemini API Key Available: ❌
```
**Solutions:**
- Add valid API key to `.env` file
- Ensure `.env` file is in project root
- Check API key permissions

#### **Tool Not Executing**
**Verification:** Look for debug output:
```
[FILE TOOL] Executing: create_report:Title:Content
[FILE TOOL] Creating report 'Title'
[FILE TOOL] SUCCESS: Report 'Title' created at reports\Title_20250816_201552.md
```

#### **Testing Issues**
- **Mocked tests passing but real functionality broken**: Use `python3 unit_test.py` (smart tests)
- **All tests failing**: Check API key and internet connection
- **Some tests skipped**: Normal behavior when API quota exceeded

## 🧪 Testing

### **Smart Unit Tests**
```bash
python3 unit_test.py
```
Runs intelligent tests that:
- ✅ Test non-API components (calculator, file ops, memory)
- ⚠️  Gracefully handle API quota limits
- 📊 Provide clear status reporting
- 💡 Give helpful guidance for issues

### **Legacy Mocked Tests** (Reference Only)
```bash
python3 legacy_mocked_test.py
```
Old mocked tests kept for reference - not recommended for actual testing.

### **Full Integration Tests** (When API Available)
```bash
python3 integration_test.py
```
Comprehensive tests that make real API calls - use when quota available.

## 📄 Dependencies

```txt
google-genai
langchain
langchain-community  
langchain-core
langchain-google-genai
python-dotenv
```

## 📚 Learn More

- [LangChain Documentation](https://python.langchain.com/)
- [Gemini API Documentation](https://ai.google.dev/)
- [ReAct Pattern Paper](https://arxiv.org/abs/2210.03629)

---

**Professional AI Research Agent with LangChain! 🚀**

*Demonstrates real tool execution, multi-step workflows, and professional agent development patterns*