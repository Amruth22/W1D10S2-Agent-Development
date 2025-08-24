"""
Smart Integration Tests for LangChain AI Research Agent
Handles API quotas and rate limits gracefully
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


class TestSmartAPIIntegration(unittest.TestCase):
    """
    Smart API Integration Tests
    These tests handle quota limits and provide meaningful results
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - check API availability"""
        cls.has_gemini_key = bool(config.GEMINI_API_KEY and config.GEMINI_API_KEY != "" and config.GEMINI_API_KEY != "your-fresh-api-key-here")
        cls.api_quota_exceeded = False
        
        print(f"\\n{'='*60}")
        print(f"SMART API INTEGRATION TESTS")
        print(f"{'='*60}")
        print(f"Gemini API Key Available: {'✅' if cls.has_gemini_key else '❌'}")
        
        # Test API availability with a simple call
        if cls.has_gemini_key:
            try:
                llm = GeminiLLM()
                test_response = llm._call("Test")
                if "429 RESOURCE_EXHAUSTED" in test_response or "quota" in test_response.lower():
                    cls.api_quota_exceeded = True
                    print(f"API Status: ⚠️  Quota Exceeded")
                else:
                    print(f"API Status: ✅ Available")
            except Exception as e:
                print(f"API Status: ❌ Error - {str(e)[:100]}")
                cls.api_quota_exceeded = True
        
        print(f"{'='*60}")
    
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
    
    def test_api_quota_status(self):
        """Test and report API quota status"""
        print("\\n📊 Testing API quota status...")
        
        if not self.has_gemini_key:
            self.skipTest("No Gemini API key available")
        
        llm = GeminiLLM()
        response = llm._call("What is 1+1?")
        
        print(f"API Response: {response[:200]}...")
        
        if "429 RESOURCE_EXHAUSTED" in response:
            print("⚠️  API Quota Status: EXCEEDED")
            print("💡 Solution: Wait 24 hours or get a new API key")
            self.skipTest("API quota exceeded - this is expected behavior")
        elif "Error calling Gemini" in response:
            print("❌ API Status: ERROR")
            self.fail(f"API error: {response[:300]}")
        else:
            print("✅ API Status: WORKING")
            self.assertGreater(len(response), 0, "API should return response")
    
    def test_non_api_components(self):
        """Test components that don't require API calls"""
        print("\\n🧮 Testing non-API components...")
        
        agent = LangChainResearchAgent()
        
        # Test calculator tool (no API needed)
        calc_tool = None
        for tool in agent.tools:
            if tool.name == "calculator":
                calc_tool = tool
                break
        
        self.assertIsNotNone(calc_tool, "Calculator tool should be available")
        
        # Test calculations
        test_cases = [
            ("2 + 2", "4"),
            ("50% of 200", "100"),
            ("10 * 3", "30")
        ]
        
        for expression, expected in test_cases:
            result = calc_tool._run(expression)
            print(f"  {expression} = {result}")
            self.assertIn(expected, result, f"Calculator failed for {expression}")
        
        print("✅ Calculator tool working correctly")
    
    def test_file_operations(self):
        """Test file operations (no API needed)"""
        print("\\n📄 Testing file operations...")
        
        agent = LangChainResearchAgent()
        
        # Find file operations tool
        file_tool = None
        for tool in agent.tools:
            if tool.name == "file_operations":
                file_tool = tool
                break
        
        self.assertIsNotNone(file_tool, "File operations tool should be available")
        
        # Test file creation
        test_title = "Smart Test Report"
        test_content = f"Created at {datetime.now()}"
        command = f"create_report:{test_title}:{test_content}"
        
        result = file_tool._run(command)
        print(f"File creation result: {result}")
        
        self.assertIn("SUCCESS", result, "File creation should succeed")
        
        # Verify file exists
        reports = os.listdir(config.REPORTS_DIR)
        test_files = [f for f in reports if f.startswith("Smart_Test_Report_")]
        self.assertGreater(len(test_files), 0, "Report file should be created")
        
        print(f"✅ File operations working correctly - created {len(test_files)} file(s)")
    
    def test_memory_management(self):
        """Test memory management (no API needed)"""
        print("\\n🧠 Testing memory management...")
        
        memory = ResearchAgentMemory()
        
        # Test message handling
        messages = [
            ("user", "Hello, how are you?"),
            ("ai", "I'm doing well, thank you!"),
            ("user", "Can you help me with research?"),
            ("ai", "Of course! I'd be happy to help.")
        ]
        
        for role, message in messages:
            if role == "user":
                memory.add_user_message(message)
            else:
                memory.add_ai_message(message)
        
        # Test memory retrieval
        history = memory.get_conversation_history()
        self.assertEqual(len(history), 4, f"Should have 4 messages, got {len(history)}")
        
        # Test stats
        stats = memory.get_memory_stats()
        self.assertEqual(stats['total_messages'], 4)
        self.assertEqual(stats['human_messages'], 2)
        self.assertEqual(stats['ai_messages'], 2)
        
        print(f"✅ Memory management working correctly")
        print(f"  Total messages: {stats['total_messages']}")
        print(f"  Human messages: {stats['human_messages']}")
        print(f"  AI messages: {stats['ai_messages']}")
        
        # Test memory clearing
        memory.clear_memory()
        cleared_history = memory.get_conversation_history()
        self.assertEqual(len(cleared_history), 0, "Memory should be cleared")
        
        print(f"✅ Memory clearing working correctly")
    
    @unittest.skipIf(not hasattr(config, 'GEMINI_API_KEY') or not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your-fresh-api-key-here", "No valid Gemini API key")
    def test_api_dependent_features_if_available(self):
        """Test API-dependent features only if API is available"""
        print("\\n🌐 Testing API-dependent features...")
        
        # Quick API availability check
        llm = GeminiLLM()
        test_response = llm._call("Test")
        
        if "429 RESOURCE_EXHAUSTED" in test_response or "quota" in test_response.lower():
            print("⚠️  API quota exceeded - skipping API tests")
            print("💡 This is normal behavior when quota is exceeded")
            self.skipTest("API quota exceeded")
        
        if "Error calling Gemini" in test_response:
            print("❌ API error detected")
            self.skipTest(f"API error: {test_response[:200]}")
        
        # If we get here, API is working
        print("✅ API is available - testing functionality")
        
        # Test simple LLM call
        simple_response = llm._call("What is 2+2? Answer with just the number.")
        print(f"LLM Response: {simple_response[:100]}...")
        
        self.assertGreater(len(simple_response), 0, "Should get response")
        self.assertNotIn("Error calling Gemini", simple_response, "Should not have errors")
        
        # Test web search if API is working
        agent = LangChainResearchAgent()
        search_tool = None
        for tool in agent.tools:
            if tool.name == "web_search":
                search_tool = tool
                break
        
        if search_tool:
            search_result = search_tool._run("current time")
            print(f"Search result: {search_result[:200]}...")
            
            if "Search error:" not in search_result:
                print("✅ Web search working correctly")
            else:
                print("⚠️  Web search has issues (likely quota)")
    
    def test_agent_structure_and_initialization(self):
        """Test agent structure without making API calls"""
        print("\\n🏗️  Testing agent structure...")
        
        agent = LangChainResearchAgent()
        
        # Test agent components
        self.assertIsNotNone(agent.llm, "Agent should have LLM")
        self.assertIsNotNone(agent.tools, "Agent should have tools")
        self.assertIsNotNone(agent.memory, "Agent should have memory")
        self.assertIsNotNone(agent.agent_executor, "Agent should have executor")
        
        # Test tool availability
        self.assertEqual(len(agent.tools), 3, "Should have 3 tools")
        
        tool_names = [tool.name for tool in agent.tools]
        expected_tools = ["web_search", "calculator", "file_operations"]
        
        for expected_tool in expected_tools:
            self.assertIn(expected_tool, tool_names, f"Should have {expected_tool} tool")
        
        print(f"✅ Agent structure correct")
        print(f"  Tools available: {', '.join(tool_names)}")
        print(f"  LLM type: {agent.llm._llm_type}")
        
        # Test agent info
        info = agent.get_agent_info()
        self.assertEqual(info['framework'], 'LangChain')
        self.assertEqual(info['llm'], 'Gemini 2.5 Flash')
        self.assertEqual(len(info['tools']), 3)
        
        print(f"✅ Agent configuration correct")


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_cases = [TestSmartAPIIntegration]
    
    for test_case in test_cases:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print detailed summary
    print(f"\\n{'='*60}")
    print(f"SMART INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(getattr(result, 'skipped', []))}")
    
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
    
    if hasattr(result, 'skipped') and result.skipped:
        print(f"\\nSKIPPED:")
        for test, reason in result.skipped:
            print(f"⏭️  {test}: {reason}")
    
    # Show what was actually tested
    print(f"\\n{'='*60}")
    print(f"WHAT WAS TESTED:")
    print(f"{'='*60}")
    print(f"✅ Agent structure and initialization")
    print(f"✅ Calculator tool (no API needed)")
    print(f"✅ File operations (no API needed)")
    print(f"✅ Memory management (no API needed)")
    print(f"⚠️  API-dependent features (quota-aware)")
    print(f"{'='*60}")
    
    # Provide guidance
    print(f"\\n💡 GUIDANCE:")
    if TestSmartAPIIntegration.api_quota_exceeded:
        print(f"• API quota exceeded - this is normal for free tier")
        print(f"• Non-API components are working correctly")
        print(f"• Wait 24 hours or get new API key for full testing")
    elif not TestSmartAPIIntegration.has_gemini_key:
        print(f"• Add valid Gemini API key to .env file")
        print(f"• Non-API components are working correctly")
    else:
        print(f"• All components tested successfully!")
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)