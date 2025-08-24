# 🧪 Testing Guide for LangChain AI Research Agent

This project includes **two different types of tests** to ensure comprehensive coverage of both component functionality and real-world integration.

## 📋 Test Types Overview

### 🧠 **Smart Unit Tests** (`unit_test.py`) - **RECOMMENDED**
- **Purpose**: Intelligent testing that adapts to API availability
- **API Calls**: Real when available, graceful handling when not
- **Speed**: Fast for non-API components, adaptive for API tests
- **Use Case**: Primary testing, development, CI/CD, production validation

### 🎭 **Legacy Mocked Tests** (`legacy_mocked_test.py`)
- **Purpose**: Reference implementation with heavy mocking
- **API Calls**: All mocked/simulated
- **Speed**: Fast (no network calls)
- **Use Case**: Reference only - not recommended for actual testing

### 🌐 **Full Integration Tests** (`integration_test.py`)
- **Purpose**: Comprehensive real API testing (when quota available)
- **API Calls**: Real API calls to Gemini and other services
- **Speed**: Slower (network dependent)
- **Use Case**: Full validation when API quota is available

## 🚀 Running Tests

### Smart Unit Tests (Recommended)
```bash
python3 unit_test.py
```
**Output Example:**
```
SMART API INTEGRATION TESTS
============================================================
Gemini API Key Available: ✅
API Status: ⚠️  Quota Exceeded
============================================================

✅ Calculator tool working correctly
✅ File operations working correctly  
✅ Memory management working correctly
⏭️  API-dependent tests skipped (quota exceeded)

GUIDANCE:
• API quota exceeded - this is normal for free tier
• Non-API components are working correctly
• Wait 24 hours or get new API key for full testing
```

### Legacy Mocked Tests (Reference Only)
```bash
python3 legacy_mocked_test.py
```

### Full Integration Tests (When API Available)
```bash
python3 integration_test.py
```
**Output Example:**
```
REAL API INTEGRATION TESTS
============================================================
Gemini API Key Available: ✅
Tavily API Key Available: ✅
============================================================

🧪 Testing REAL Gemini API call...
🔍 Testing REAL web search tool...
🤖 Testing REAL agent research...
🧮 Testing REAL calculator tool...
📄 Testing REAL file operations tool...
🔄 Testing REAL multi-tool workflow...
🧠 Testing REAL memory operations...
```

## 📊 What Each Test Suite Covers

### 🧠 **Smart Unit Tests** (`unit_test.py`) - **RECOMMENDED**

| Test Category | What's Tested | Real or Adaptive |
|---------------|---------------|------------------|
| **API Status Check** | Real API availability and quota status | ✅ **Real** |
| **Calculator Tool** | Mathematical calculations | ✅ **Real** |
| **File Operations** | File creation, content verification | ✅ **Real** |
| **Memory Management** | Conversation history, context tracking | ✅ **Real** |
| **Agent Structure** | Component initialization, tool loading | ✅ **Real** |
| **API-Dependent Features** | LLM calls, web search (when available) | 🔄 **Adaptive** |

**Advantages:**
- ✅ Tests real functionality where possible
- ✅ Gracefully handles API limitations
- ✅ Provides clear status reporting
- ✅ Gives actionable guidance
- ✅ Suitable for all environments

### 🎭 **Legacy Mocked Tests** (`legacy_mocked_test.py`)

| Test Category | What's Tested | Real or Mocked |
|---------------|---------------|----------------|
| **Configuration** | API key loading, config validation | ✅ **Real** |
| **LLM Integration** | GeminiLLM wrapper structure | ❌ **Mocked** |
| **Agent Initialization** | Component loading, directory creation | ❌ **Mocked** |
| **Tool Execution** | Calculator (real), File ops (real), Web search (mocked) | ⚠️ **Mixed** |

**Limitations:**
- ❌ No real API calls
- ❌ No actual web searches
- ❌ No real LLM responses
- ❌ No end-to-end workflows
- ❌ False confidence from mocked responses

### 🌐 **Integration Tests** (`integration_test.py`)

| Test Category | What's Tested | Real or Mocked |
|---------------|---------------|----------------|
| **Gemini API** | Real API calls, response validation | ✅ **Real** |
| **Web Search** | Real Google searches via Gemini | ✅ **Real** |
| **Agent Research** | Complete research workflows | ✅ **Real** |
| **Calculator Tool** | Mathematical calculations | ✅ **Real** |
| **File Operations** | File creation, content verification | ✅ **Real** |
| **Multi-tool Workflows** | Complex queries using multiple tools | ✅ **Real** |
| **Memory Management** | Conversation history, context tracking | ✅ **Real** |

**Requirements:**
- ✅ Valid Gemini API key in `.env`
- ✅ Internet connection
- ✅ File system write permissions

## 🔧 Test Configuration

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys in .env file
GEMINI_API_KEY=your-actual-api-key
TAVILY_API_KEY=your-tavily-key
```

### Running Specific Test Categories

#### Mocked Tests Only
```bash
# Run all mocked tests
python3 unit_test.py

# Run specific test class
python3 -m unittest unit_test.TestConfiguration -v
```

#### Integration Tests Only
```bash
# Run all integration tests
python3 integration_test.py

# Run specific integration test
python3 -m unittest integration_test.TestRealAPIIntegration.test_real_gemini_llm_call -v
```

## 🎯 When to Use Each Test Type

### Use **Smart Unit Tests** (`unit_test.py`) When:
- ✅ **Primary testing** - recommended for all scenarios
- ✅ Developing new features
- ✅ Running CI/CD pipelines
- ✅ Testing component structure
- ✅ API keys may or may not be available
- ✅ Need intelligent, adaptive testing
- ✅ Want clear guidance on issues

### Use **Legacy Mocked Tests** (`legacy_mocked_test.py`) When:
- ⚠️ **Reference only** - not recommended for actual testing
- 📚 Studying mocking patterns
- 🔍 Understanding component structure

### Use **Full Integration Tests** (`integration_test.py`) When:
- ✅ API quota is definitely available
- ✅ Comprehensive end-to-end validation needed
- ✅ Debugging specific API integration issues
- ✅ Before major deployments (when quota allows)

## 🚨 Common Issues and Solutions

### Mocked Tests Failing
```bash
# Usually indicates structural issues
AssertionError: GEMINI_API_KEY is empty
```
**Solution**: Check `.env` file and config loading

### Integration Tests Failing
```bash
# API-related failures
Error calling Gemini: 403 Forbidden
```
**Solutions:**
1. Verify API key is valid
2. Check API quotas/limits
3. Ensure internet connectivity
4. Verify API key permissions

### Skipped Integration Tests
```bash
# Tests skipped due to missing API keys
test_real_gemini_llm_call ... skipped 'No Gemini API key available'
```
**Solution**: Add valid API keys to `.env` file

## 📈 Test Coverage Analysis

### Current Coverage:

| Component | Mocked Tests | Integration Tests | Coverage Level |
|-----------|-------------|------------------|----------------|
| **Configuration** | ✅ Complete | ✅ Complete | 🟢 **Excellent** |
| **LLM Integration** | ⚠️ Structure only | ✅ Real API calls | 🟡 **Good** |
| **Web Search** | ❌ Structure only | ✅ Real searches | 🟡 **Good** |
| **Calculator** | ✅ Complete | ✅ Complete | 🟢 **Excellent** |
| **File Operations** | ✅ Complete | ✅ Complete | 🟢 **Excellent** |
| **Memory Management** | ❌ Not tested | ✅ Complete | 🟡 **Good** |
| **Agent Workflows** | ❌ Not tested | ✅ Complete | 🟡 **Good** |

## 🎓 Best Practices

### For Development:
1. **Use smart unit tests** (`python3 unit_test.py`) as your primary testing
2. **Check test output** for guidance on API issues
3. **Run tests frequently** - they adapt to your environment
4. **Use full integration tests** only when API quota available
5. **Ignore legacy mocked tests** - they provide false confidence

### For CI/CD:
1. **Always run mocked tests** (fast, no API keys needed)
2. **Run integration tests** in staging environment
3. **Use test API keys** for integration tests
4. **Monitor API usage** during testing

### For Debugging:
1. **Use mocked tests** to isolate component issues
2. **Use integration tests** to debug real-world problems
3. **Check both test outputs** for comprehensive understanding
4. **Verify API responses** in integration tests

## 📚 Example Test Outputs

### Successful Mocked Test Run:
```
test_api_key_exists ... ok
test_gemini_llm_initialization ... ok
test_agent_tools_loaded ... ok
test_calculator_tool ... ok
test_file_operations_tool ... ok

MOCKED UNIT TEST SUMMARY
⚠️  WARNING: These tests use mocks - NOT real APIs
Tests run: 12, Failures: 0, Errors: 0, Success rate: 100.0%
```

### Successful Integration Test Run:
```
🧪 Testing REAL Gemini API call...
Prompt: What is 2+2? Answer with just the number.
Response: 4

🔍 Testing REAL web search tool...
Searching for: current weather in New York
Search result length: 1247 characters

🤖 Testing REAL agent research...
Research query: What is the capital of France?
Research completed in 3.45 seconds
Response preview: The capital of France is Paris...

REAL INTEGRATION TEST SUMMARY
Tests run: 8, Failures: 0, Errors: 0, Success rate: 100.0%
```

---

## 🎯 Summary

- **`unit_test.py`**: Smart, adaptive, real testing where possible - **USE THIS**
- **`legacy_mocked_test.py`**: Mocked, reference only - **AVOID**
- **`integration_test.py`**: Full real API testing - **USE WHEN QUOTA AVAILABLE**
- **Smart tests are recommended** for all scenarios
- **Legacy mocked tests** provide false confidence
- **Full integration tests** for comprehensive validation when possible

**Remember**: Smart tests give you real confidence by testing actual functionality while gracefully handling limitations!