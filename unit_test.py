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
        with patch('agents.research_agent.genai.Client'):
            self.llm = GeminiLLM()
    
    def test_gemini_llm_initialization(self):
        """Test GeminiLLM wrapper initializes correctly"""
        self.assertIsNotNone(self.llm, "GeminiLLM failed to initialize")
        self.assertEqual(self.llm._llm_type, "gemini-2.5-flash", "Incorrect LLM type")
        self.assertTrue(hasattr(self.llm, 'client'), "GeminiLLM missing client attribute")
        self.assertTrue(hasattr(self.llm, 'model'), "GeminiLLM missing model attribute")
    
    @patch('agents.research_agent.genai.Client')
    def test_gemini_api_connection(self, mock_client):
        """Test Gemini API connection (MOCKED - NOT REAL API CALL)"""
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
        # Test error handling by patching the genai.Client class directly
        with patch('agents.research_agent.genai.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client.models.generate_content_stream.side_effect = Exception("API Error")
            mock_client_class.return_value = mock_client
            
            # Create new LLM instance with mocked client
            llm = GeminiLLM()
            response = llm._call("Test prompt")
            
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
        # Agent should create directories based on current config values
        agent = LangChainResearchAgent()
        
        # Check that directories exist at the configured paths
        self.assertTrue(os.path.exists(config.REPORTS_DIR), f"Reports directory not created at {config.REPORTS_DIR}")
        self.assertTrue(os.path.exists(config.DATA_DIR), f"Data directory not created at {config.DATA_DIR}")
        
        # Verify directories are actually the temp directories we set up
        self.assertIn(self.temp_dir, config.REPORTS_DIR, "Reports directory not using temp path")
        self.assertIn(self.temp_dir, config.DATA_DIR, "Data directory not using temp path")


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
        
        # Verify file actually exists in the configured directory
        self.assertTrue(os.path.exists(config.REPORTS_DIR), f"Reports directory {config.REPORTS_DIR} does not exist")
        
        reports_files = os.listdir(config.REPORTS_DIR)
        test_files = [f for f in reports_files if f.startswith("Unit_Test_Report_")]
        
        self.assertGreater(len(test_files), 0, f"Test report file not created in {config.REPORTS_DIR}. Files found: {reports_files}. Tool result: {result}")
    
    @patch('google.genai.Client')
    def test_web_search_tool_structure(self, mock_client):
        """Test web search tool structure (MOCKED - NO REAL SEARCH PERFORMED)"""
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





if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_cases = [
        TestConfiguration,
        TestGeminiLLMIntegration, 
        TestAgentInitialization,
        TestToolExecution
    ]
    
    for test_case in test_cases:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"MOCKED UNIT TEST SUMMARY")
    print(f"⚠️  WARNING: These tests use mocks - NOT real APIs")
    print(f"For real API testing run: python3 integration_test.py")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            # print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\n')[0]}")
            # print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
            msg = traceback.split("AssertionError: ")[-1].split("\n")[0]
            print(f"- {test}: {msg}")


    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            msg = traceback.split("\n")[-2]
            print(f"- {test}: {msg}")

    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
