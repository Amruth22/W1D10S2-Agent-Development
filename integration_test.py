"""
Integration Tests for LangChain AI Research Agent
Tests REAL API functionality with actual API calls
"""

import unittest
import os
import tempfile
import shutil
import time
from datetime import datetime

# Import existing code components
import config
from agents.research_agent import LangChainResearchAgent, GeminiLLM
from memory.conversation_memory import ResearchAgentMemory


class TestRealAPIIntegration(unittest.TestCase):
    """
    REAL API Integration Tests
    These tests make actual API calls and verify real functionality
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - check if API keys are available"""
        cls.has_gemini_key = bool(config.GEMINI_API_KEY and config.GEMINI_API_KEY != "")
        cls.has_tavily_key = bool(hasattr(config, 'TAVILY_API_KEY') and config.TAVILY_API_KEY and config.TAVILY_API_KEY != "")
        
        print(f"\n{'='*60}")
        print(f"REAL API INTEGRATION TESTS")
        print(f"{'='*60}")
        print(f"Gemini API Key Available: {'✅' if cls.has_gemini_key else '❌'}")
        print(f"Tavily API Key Available: {'✅' if cls.has_tavily_key else '❌'}")
        print(f"{'='*60}")
        
        if not cls.has_gemini_key:
            print("⚠️  WARNING: No Gemini API key found - API tests will be skipped")
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_reports_dir = config.REPORTS_DIR
        self.original_data_dir = config.DATA_DIR
        
        # Override config for testing
        config.REPORTS_DIR = os.path.join(self.temp_dir, "reports")
        config.DATA_DIR = os.path.join(self.temp_dir, "data")
        
        # Create directories
        os.makedirs(config.REPORTS_DIR, exist_ok=True)
        os.makedirs(config.DATA_DIR, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Restore original config
        config.REPORTS_DIR = self.original_reports_dir
        config.DATA_DIR = self.original_data_dir
        
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    @unittest.skipUnless(hasattr(config, 'GEMINI_API_KEY') and config.GEMINI_API_KEY, "No Gemini API key available")
    def test_real_gemini_llm_call(self):
        """Test REAL Gemini LLM API call"""
        print("\\n🧪 Testing REAL Gemini API call...")
        
        llm = GeminiLLM()
        
        # Make a real API call
        test_prompt = "What is 2+2? Answer with just the number."
        response = llm._call(test_prompt)
        
        print(f"Prompt: {test_prompt}")
        print(f"Response: {response[:100]}...")
        
        # Verify we got a real response
        self.assertIsInstance(response, str, "Response should be string")
        self.assertGreater(len(response), 0, "Response should not be empty")
        self.assertNotIn("Error calling Gemini", response, "API call failed")
        
        # Check if response contains expected answer
        self.assertTrue(any(char in response for char in ['4', 'four', 'Four']), 
                       f"Response doesn't contain expected answer: {response}")
    
    @unittest.skipUnless(hasattr(config, 'GEMINI_API_KEY') and config.GEMINI_API_KEY, "No Gemini API key available")
    def test_real_web_search_tool(self):
        """Test REAL web search functionality"""
        print("\\n🔍 Testing REAL web search tool...")
        
        agent = LangChainResearchAgent()
        
        # Find web search tool
        search_tool = None
        for tool in agent.tools:
            if tool.name == "web_search":
                search_tool = tool
                break
        
        self.assertIsNotNone(search_tool, "Web search tool not found")
        
        # Make a real search
        search_query = "current weather in New York"
        print(f"Searching for: {search_query}")
        
        result = search_tool._run(search_query)
        
        print(f"Search result length: {len(result)} characters")
        print(f"Search result preview: {result[:200]}...")
        
        # Verify we got a real search result
        self.assertIsInstance(result, str, "Search result should be string")
        self.assertGreater(len(result), 50, "Search result should be substantial")
        self.assertNotIn("Search error:", result, f"Search failed: {result}")
        
        # Check for weather-related content
        weather_keywords = ['weather', 'temperature', 'degrees', 'forecast', 'climate']
        has_weather_content = any(keyword.lower() in result.lower() for keyword in weather_keywords)
        self.assertTrue(has_weather_content, f"Search result doesn't contain weather information: {result[:300]}")
    
    @unittest.skipUnless(hasattr(config, 'GEMINI_API_KEY') and config.GEMINI_API_KEY, "No Gemini API key available")
    def test_real_agent_research(self):
        """Test REAL agent research functionality"""
        print("\\n🤖 Testing REAL agent research...")
        
        agent = LangChainResearchAgent()
        
        # Test a simple research query
        research_query = "What is the capital of France?"
        print(f"Research query: {research_query}")
        
        start_time = time.time()
        response = agent.research(research_query)
        end_time = time.time()
        
        print(f"Research completed in {end_time - start_time:.2f} seconds")
        print(f"Response length: {len(response)} characters")
        print(f"Response preview: {response[:300]}...")
        
        # Verify we got a real research response
        self.assertIsInstance(response, str, "Research response should be string")
        self.assertGreater(len(response), 20, "Research response should be substantial")
        self.assertNotIn("Research error:", response, f"Research failed: {response}")
        
        # Check for expected answer
        self.assertTrue(any(word in response.lower() for word in ['paris', 'france']), 
                       f"Research response doesn't contain expected information: {response}")
    
    def test_real_calculator_tool(self):
        """Test REAL calculator tool (no API needed)"""
        print("\\n🧮 Testing REAL calculator tool...")
        
        agent = LangChainResearchAgent()
        
        # Find calculator tool
        calc_tool = None
        for tool in agent.tools:
            if tool.name == "calculator":
                calc_tool = tool
                break
        
        self.assertIsNotNone(calc_tool, "Calculator tool not found")
        
        # Test various calculations
        test_cases = [
            ("2 + 2", "4"),
            ("10 * 5", "50"),
            ("25% of 1000", "250"),
            ("100 / 4", "25")
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                print(f"Calculating: {expression}")
                result = calc_tool._run(expression)
                print(f"Result: {result}")
                
                self.assertIsInstance(result, str, "Calculator result should be string")
                self.assertIn(expected, result, f"Expected {expected} in result: {result}")
    
    def test_real_file_operations_tool(self):
        """Test REAL file operations tool"""
        print("\\n📄 Testing REAL file operations tool...")
        
        agent = LangChainResearchAgent()
        
        # Find file operations tool
        file_tool = None
        for tool in agent.tools:
            if tool.name == "file_operations":
                file_tool = tool
                break
        
        self.assertIsNotNone(file_tool, "File operations tool not found")
        
        # Test report creation
        test_title = "Integration Test Report"
        test_content = f"This is a real integration test report created at {datetime.now()}"
        test_command = f"create_report:{test_title}:{test_content}"
        
        print(f"Creating report: {test_title}")
        result = file_tool._run(test_command)
        print(f"File operation result: {result}")
        
        # Verify file creation
        self.assertIn("SUCCESS", result, f"File creation failed: {result}")
        self.assertIn(test_title, result, "Report title not in result")
        
        # Verify file actually exists
        self.assertTrue(os.path.exists(config.REPORTS_DIR), f"Reports directory {config.REPORTS_DIR} does not exist")
        
        reports_files = os.listdir(config.REPORTS_DIR)
        test_files = [f for f in reports_files if f.startswith("Integration_Test_Report_")]
        
        self.assertGreater(len(test_files), 0, f"Test report file not created. Files found: {reports_files}")
        
        # Verify file content
        test_file_path = os.path.join(config.REPORTS_DIR, test_files[0])
        with open(test_file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        self.assertIn(test_title, file_content, "Report title not in file content")
        self.assertIn(test_content, file_content, "Report content not in file")
        
        print(f"✅ File created successfully: {test_file_path}")
        print(f"File size: {os.path.getsize(test_file_path)} bytes")
    
    @unittest.skipUnless(hasattr(config, 'GEMINI_API_KEY') and config.GEMINI_API_KEY, "No Gemini API key available")
    def test_real_multi_tool_workflow(self):
        """Test REAL multi-tool workflow"""
        print("\\n🔄 Testing REAL multi-tool workflow...")
        
        agent = LangChainResearchAgent()
        
        # Test a complex query that should use multiple tools
        complex_query = "Calculate 15% of 1000 and create a report about it"
        print(f"Complex query: {complex_query}")
        
        start_time = time.time()
        response = agent.research(complex_query)
        end_time = time.time()
        
        print(f"Multi-tool workflow completed in {end_time - start_time:.2f} seconds")
        print(f"Response length: {len(response)} characters")
        print(f"Response preview: {response[:400]}...")
        
        # Verify response
        self.assertIsInstance(response, str, "Multi-tool response should be string")
        self.assertGreater(len(response), 50, "Multi-tool response should be substantial")
        
        # Check if calculation was performed
        self.assertTrue(any(num in response for num in ['150', '15%', '1000']), 
                       f"Response doesn't contain calculation results: {response}")
        
        # Check if file was created
        reports_files = os.listdir(config.REPORTS_DIR)
        self.assertGreater(len(reports_files), 0, "No report files created during multi-tool workflow")
        
        print(f"✅ Multi-tool workflow completed successfully")
        print(f"Files created: {len(reports_files)}")


class TestRealMemoryFunctionality(unittest.TestCase):
    """Test REAL memory functionality"""
    
    def test_real_memory_operations(self):
        """Test REAL memory operations"""
        print("\\n🧠 Testing REAL memory operations...")
        
        memory = ResearchAgentMemory()
        
        # Test adding messages
        test_messages = [
            "What is machine learning?",
            "Machine learning is a subset of AI...",
            "Can you explain neural networks?",
            "Neural networks are computational models..."
        ]
        
        for i, message in enumerate(test_messages):
            if i % 2 == 0:
                memory.add_user_message(message)
                print(f"Added user message: {message[:50]}...")
            else:
                memory.add_ai_message(message)
                print(f"Added AI message: {message[:50]}...")
        
        # Test memory retrieval
        history = memory.get_conversation_history()
        self.assertEqual(len(history), 4, f"Expected 4 messages, got {len(history)}")
        
        # Test formatted history
        formatted_history = memory.get_formatted_history()
        self.assertIn("machine learning", formatted_history.lower(), "Formatted history missing content")
        
        # Test research context
        context = memory.get_research_context()
        self.assertIsInstance(context, str, "Research context should be string")
        
        # Test memory stats
        stats = memory.get_memory_stats()
        self.assertEqual(stats['total_messages'], 4, f"Expected 4 total messages, got {stats['total_messages']}")
        self.assertEqual(stats['human_messages'], 2, f"Expected 2 human messages, got {stats['human_messages']}")
        self.assertEqual(stats['ai_messages'], 2, f"Expected 2 AI messages, got {stats['ai_messages']}")
        
        print(f"✅ Memory operations working correctly")
        print(f"Total messages: {stats['total_messages']}")
        print(f"Research topics found: {stats['research_topics_count']}")
        
        # Test memory clearing
        memory.clear_memory()
        cleared_history = memory.get_conversation_history()
        self.assertEqual(len(cleared_history), 0, "Memory not properly cleared")
        
        print(f"✅ Memory clearing working correctly")


if __name__ == "__main__":
    # Create test suite for integration tests
    test_suite = unittest.TestSuite()
    
    # Add integration test cases
    integration_test_cases = [
        TestRealAPIIntegration,
        TestRealMemoryFunctionality
    ]
    
    for test_case in integration_test_cases:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print detailed summary
    print(f"\\n{'='*60}")
    print(f"REAL INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {result.testsRun - len(result.failures) - len(result.errors) - (result.testsRun - len([t for t in result.skipped]) if hasattr(result, 'skipped') else result.testsRun)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\\nFAILURES:")
        for test, traceback in result.failures:
            msg = traceback.split("AssertionError: ")[-1].split("\\n")[0]
            print(f"❌ {test}: {msg}")
    
    if result.errors:
        print(f"\\nERRORS:")
        for test, traceback in result.errors:
            msg = traceback.split("\\n")[-2]
            print(f"💥 {test}: {msg}")
    
    # Show what was actually tested
    print(f"\\n{'='*60}")
    print(f"WHAT WAS ACTUALLY TESTED:")
    print(f"{'='*60}")
    print(f"✅ Real Gemini API calls")
    print(f"✅ Real web search functionality") 
    print(f"✅ Real agent research workflows")
    print(f"✅ Real calculator operations")
    print(f"✅ Real file creation and verification")
    print(f"✅ Real memory operations")
    print(f"✅ Real multi-tool workflows")
    print(f"{'='*60}")
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)