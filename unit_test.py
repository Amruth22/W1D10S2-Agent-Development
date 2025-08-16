"""
Unit tests for LangChain AI Research Agent
Tests core components using existing code
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Import existing code components
import config
from agents.research_agent import LangChainResearchAgent, GeminiLLM
from memory.conversation_memory import ResearchAgentMemory


class TestConfiguration(unittest.TestCase):
    """Test Case 1: Configuration Test"""
    
    def test_api_key_exists(self):
        """Test that Gemini API key is present in config"""
        self.assertTrue(hasattr(config, 'GEMINI_API_KEY'), "GEMINI_API_KEY not found in config")
        self.assertIsNotNone(config.GEMINI_API_KEY, "GEMINI_API_KEY is None")
        self.assertNotEqual(config.GEMINI_API_KEY, "", "GEMINI_API_KEY is empty")
        self.assertNotEqual(config.GEMINI_API_KEY, "your-gemini-api-key-here", "GEMINI_API_KEY is placeholder value")
    
    def test_required_config_variables(self):
        """Test that all required configuration variables are present"""
        required_vars = [
            'GEMINI_API_KEY', 'GEMINI_MODEL', 'MAX_ITERATIONS', 
            'VERBOSE', 'REPORTS_DIR', 'DATA_DIR'
        ]
        
        for var in required_vars:
            with self.subTest(var=var):
                self.assertTrue(hasattr(config, var), f"{var} not found in config")
                self.assertIsNotNone(getattr(config, var), f"{var} is None")
    
    def test_config_values_valid(self):
        """Test that configuration values are valid"""
        self.assertEqual(config.GEMINI_MODEL, "gemini-2.5-flash", "Invalid Gemini model")
        self.assertIsInstance(config.MAX_ITERATIONS, int, "MAX_ITERATIONS should be integer")
        self.assertGreater(config.MAX_ITERATIONS, 0, "MAX_ITERATIONS should be positive")
        self.assertIsInstance(config.VERBOSE, bool, "VERBOSE should be boolean")


class TestGeminiLLMIntegration(unittest.TestCase):
    """Test Case 2: Gemini LLM Integration Test"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.llm = GeminiLLM()
    
    def test_gemini_llm_initialization(self):
        """Test GeminiLLM wrapper initializes correctly"""
        self.assertIsNotNone(self.llm, "GeminiLLM failed to initialize")
        self.assertEqual(self.llm._llm_type, "gemini-2.5-flash", "Incorrect LLM type")
        self.assertTrue(hasattr(self.llm, 'client'), "GeminiLLM missing client attribute")
        self.assertTrue(hasattr(self.llm, 'model'), "GeminiLLM missing model attribute")
    
    @patch('agents.research_agent.genai.Client')
    def test_gemini_api_connection(self, mock_client):
        """Test Gemini API connection (mocked)"""
        # Mock the streaming response
        mock_chunk = MagicMock()
        mock_chunk.text = "Test response"
        
        mock_stream = [mock_chunk]
        mock_client.return_value.models.generate_content_stream.return_value = mock_stream
        
        # Create new LLM instance with mocked client
        llm = GeminiLLM()
        response = llm._call("Test prompt")
        
        self.assertIsInstance(response, str, "Response should be string")
        self.assertIn("Test response", response, "Expected content not in response")
    
    def test_gemini_error_handling(self):
        """Test Gemini LLM error handling"""
        with patch.object(self.llm, 'client') as mock_client:
            mock_client.models.generate_content_stream.side_effect = Exception("API Error")
            
            response = self.llm._call("Test prompt")
            
            self.assertIn("Error calling Gemini", response, "Error not properly handled")


class TestAgentInitialization(unittest.TestCase):
    """Test Case 3: Agent Initialization Test"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.original_reports_dir = config.REPORTS_DIR
        self.original_data_dir = config.DATA_DIR
        
        # Override config for testing
        config.REPORTS_DIR = os.path.join(self.temp_dir, "reports")
        config.DATA_DIR = os.path.join(self.temp_dir, "data")
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Restore original config
        config.REPORTS_DIR = self.original_reports_dir
        config.DATA_DIR = self.original_data_dir
        
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    @patch('google.genai.Client')
    def test_agent_initialization(self, mock_client):
        """Test LangChainResearchAgent creates successfully"""
        agent = LangChainResearchAgent()
        
        self.assertIsNotNone(agent, "Agent failed to initialize")
        self.assertIsNotNone(agent.llm, "Agent LLM not initialized")
        self.assertIsNotNone(agent.tools, "Agent tools not initialized")
        self.assertIsNotNone(agent.memory, "Agent memory not initialized")
        self.assertIsNotNone(agent.agent_executor, "Agent executor not initialized")
    
    @patch('google.genai.Client')
    def test_agent_tools_loaded(self, mock_client):
        """Test all 3 tools are loaded correctly"""
        agent = LangChainResearchAgent()
        
        self.assertEqual(len(agent.tools), 3, "Should have exactly 3 tools")
        
        tool_names = [tool.name for tool in agent.tools]
        expected_tools = ["web_search", "calculator", "file_operations"]
        
        for expected_tool in expected_tools:
            with self.subTest(tool=expected_tool):
                self.assertIn(expected_tool, tool_names, f"{expected_tool} tool not found")
    
    @patch('google.genai.Client')
    def test_directories_created(self, mock_client):
        """Test that required directories are created"""
        agent = LangChainResearchAgent()
        
        self.assertTrue(os.path.exists(config.REPORTS_DIR), "Reports directory not created")
        self.assertTrue(os.path.exists(config.DATA_DIR), "Data directory not created")


class TestToolExecution(unittest.TestCase):
    """Test Case 4: Tool Execution Test"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_reports_dir = config.REPORTS_DIR
        config.REPORTS_DIR = os.path.join(self.temp_dir, "reports")
        os.makedirs(config.REPORTS_DIR, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        config.REPORTS_DIR = self.original_reports_dir
        shutil.rmtree(self.temp_dir)
    
    @patch('google.genai.Client')
    def test_calculator_tool(self, mock_client):
        """Test calculator tool execution"""
        agent = LangChainResearchAgent()
        
        # Find calculator tool
        calc_tool = None
        for tool in agent.tools:
            if tool.name == "calculator":
                calc_tool = tool
                break
        
        self.assertIsNotNone(calc_tool, "Calculator tool not found")
        
        # Test simple calculation
        result = calc_tool._run("2 + 2")
        self.assertIn("Result: 4", result, "Calculator failed simple addition")
        
        # Test percentage calculation
        result = calc_tool._run("25% of 1000")
        self.assertIn("250", result, "Calculator failed percentage calculation")
    
    @patch('google.genai.Client')
    def test_file_operations_tool(self, mock_client):
        """Test file operations tool execution"""
        agent = LangChainResearchAgent()
        
        # Find file operations tool
        file_tool = None
        for tool in agent.tools:
            if tool.name == "file_operations":
                file_tool = tool
                break
        
        self.assertIsNotNone(file_tool, "File operations tool not found")
        
        # Test report creation
        test_command = "create_report:Unit Test Report:This is a test report created by unit tests"
        result = file_tool._run(test_command)
        
        self.assertIn("SUCCESS", result, "File creation failed")
        self.assertIn("Unit Test Report", result, "Report title not in result")
        
        # Verify file actually exists
        reports_files = os.listdir(config.REPORTS_DIR)
        test_files = [f for f in reports_files if f.startswith("Unit_Test_Report_")]
        self.assertGreater(len(test_files), 0, "Test report file not created")
    
    @patch('google.genai.Client')
    def test_web_search_tool_structure(self, mock_client):
        """Test web search tool structure (without actual API call)"""
        agent = LangChainResearchAgent()
        
        # Find web search tool
        search_tool = None
        for tool in agent.tools:
            if tool.name == "web_search":
                search_tool = tool
                break
        
        self.assertIsNotNone(search_tool, "Web search tool not found")
        self.assertEqual(search_tool.name, "web_search", "Incorrect tool name")
        self.assertIn("Search the internet", search_tool.description, "Invalid tool description")


class TestMemorySystem(unittest.TestCase):
    """Test Case 5: Memory System Test"""
    
    def test_memory_initialization(self):
        """Test ResearchAgentMemory initializes correctly"""
        memory = ResearchAgentMemory()
        
        self.assertIsNotNone(memory, "Memory failed to initialize")
        self.assertIsNotNone(memory.memory, "LangChain memory not initialized")
        self.assertIsNotNone(memory.session_summary, "Session summary not initialized")
    
    def test_memory_operations(self):
        """Test memory add and retrieve operations"""
        memory = ResearchAgentMemory()
        
        # Test adding messages
        memory.add_user_message("Test user message")
        memory.add_ai_message("Test AI response")
        
        # Test getting history
        history = memory.get_formatted_history()
        self.assertIsInstance(history, str, "History should be string")
        self.assertIn("Test user message", history, "User message not in history")
        self.assertIn("Test AI response", history, "AI message not in history")
    
    def test_memory_statistics(self):
        """Test memory statistics retrieval"""
        memory = ResearchAgentMemory()
        
        # Add some messages
        memory.add_user_message("Test message 1")
        memory.add_ai_message("Test response 1")
        memory.add_user_message("Test message 2")
        
        # Get statistics
        stats = memory.get_memory_stats()
        
        self.assertIsInstance(stats, dict, "Stats should be dictionary")
        self.assertIn("total_messages", stats, "total_messages not in stats")
        self.assertGreaterEqual(stats["total_messages"], 3, "Incorrect message count")
    
    def test_memory_clear(self):
        """Test memory clearing functionality"""
        memory = ResearchAgentMemory()
        
        # Add messages
        memory.add_user_message("Test message")
        memory.add_ai_message("Test response")
        
        # Clear memory
        memory.clear_memory()
        
        # Check memory is cleared
        stats = memory.get_memory_stats()
        self.assertEqual(stats["total_messages"], 0, "Memory not properly cleared")


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_cases = [
        TestConfiguration,
        TestGeminiLLMIntegration, 
        TestAgentInitialization,
        TestToolExecution,
        TestMemorySystem
    ]
    
    for test_case in test_cases:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"UNIT TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\n')[0]}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\n')[-2]}")
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
