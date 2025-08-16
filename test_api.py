#!/usr/bin/env python3
"""
FastAPI Research Agent Test Script
Tests the API endpoints and functionality
"""

import requests
import time
import json
import sys
from typing import Dict, Any


class APITester:
    """Test the FastAPI Research Agent API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def test_health_check(self) -> bool:
        """Test the health check endpoint"""
        print("Testing health check...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            
            health_data = response.json()
            print(f"Health check passed: {health_data['status']}")
            print(f"   RabbitMQ connected: {health_data['rabbitmq_connected']}")
            print(f"   Agent available: {health_data['agent_available']}")
            return True
            
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def test_api_info(self) -> bool:
        """Test the root API info endpoint"""
        print("\nTesting API info...")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            response.raise_for_status()
            
            info_data = response.json()
            print(f"API Info: {info_data['message']}")
            print(f"   Version: {info_data['version']}")
            print(f"   Framework: {info_data['framework']}")
            return True
            
        except Exception as e:
            print(f"API info failed: {e}")
            return False
    
    def test_research_submission(self, query: str = "What is artificial intelligence?") -> str:
        """Test research request submission"""
        print(f"\nTesting research submission...")
        print(f"   Query: {query}")
        
        try:
            payload = {
                "query": query,
                "priority": "normal",
                "max_iterations": 5,
                "include_sources": True,
                "create_report": False
            }
            
            response = self.session.post(
                f"{self.base_url}/research",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            task_data = response.json()
            task_id = task_data["task_id"]
            
            print(f"Research submitted successfully")
            print(f"   Task ID: {task_id}")
            print(f"   Status: {task_data['status']}")
            print(f"   Estimated time: {task_data.get('estimated_time', 'Unknown')}")
            
            return task_id
            
        except Exception as e:
            print(f"Research submission failed: {e}")
            return ""
    
    def test_task_status(self, task_id: str) -> Dict[str, Any]:
        """Test task status checking"""
        print(f"\nTesting task status...")
        
        try:
            response = self.session.get(f"{self.base_url}/research/{task_id}/status")
            response.raise_for_status()
            
            status_data = response.json()
            print(f"Task status retrieved")
            print(f"   Task ID: {status_data['task_id']}")
            print(f"   Status: {status_data['status']}")
            print(f"   Progress: {status_data['progress']}%")
            print(f"   Created: {status_data['created_at']}")
            
            return status_data
            
        except Exception as e:
            print(f"Task status check failed: {e}")
            return {}
    
    def test_task_results(self, task_id: str) -> Dict[str, Any]:
        """Test task results retrieval"""
        print(f"\nTesting task results...")
        
        try:
            response = self.session.get(f"{self.base_url}/research/{task_id}")
            response.raise_for_status()
            
            results_data = response.json()
            print(f"Task results retrieved")
            print(f"   Status: {results_data['status']}")
            
            if results_data['status'] == 'completed':
                result_preview = results_data['result'][:100] + "..." if len(results_data['result']) > 100 else results_data['result']
                print(f"   Result preview: {result_preview}")
                print(f"   Files generated: {len(results_data.get('files_generated', []))}")
            elif results_data['status'] == 'failed':
                print(f"   Error: {results_data.get('error', 'Unknown error')}")
            
            return results_data
            
        except Exception as e:
            print(f"Task results retrieval failed: {e}")
            return {}
    
    def test_task_list(self) -> bool:
        """Test task listing"""
        print(f"\nTesting task list...")
        
        try:
            response = self.session.get(f"{self.base_url}/research")
            response.raise_for_status()
            
            list_data = response.json()
            print(f"Task list retrieved")
            print(f"   Total tasks: {list_data['total_tasks']}")
            
            if list_data['tasks']:
                print("   Recent tasks:")
                for task in list_data['tasks'][:3]:  # Show first 3
                    print(f"     - {task['task_id'][:8]}... ({task['status']})")
            
            return True
            
        except Exception as e:
            print(f"Task list retrieval failed: {e}")
            return False
    
    def wait_for_completion(self, task_id: str, max_wait: int = 120) -> Dict[str, Any]:
        """Wait for task completion with polling"""
        print(f"\nWaiting for task completion (max {max_wait}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_data = self.test_task_status(task_id)
            
            if not status_data:
                break
            
            status = status_data.get('status', '')
            
            if status in ['completed', 'failed', 'cancelled']:
                print(f"Task finished with status: {status}")
                return self.test_task_results(task_id)
            
            print(f"   Still processing... ({status}, {status_data.get('progress', 0)}%)")
            time.sleep(10)  # Wait 10 seconds between checks
        
        print(f"Timeout reached after {max_wait}s")
        return {}
    
    def run_full_test(self, query: str = "Explain quantum computing in simple terms") -> bool:
        """Run a complete API test"""
        print("Starting Full API Test")
        print("=" * 50)
        
        # Test 1: Health check
        if not self.test_health_check():
            return False
        
        # Test 2: API info
        if not self.test_api_info():
            return False
        
        # Test 3: Submit research
        task_id = self.test_research_submission(query)
        if not task_id:
            return False
        
        # Test 4: Check initial status
        if not self.test_task_status(task_id):
            return False
        
        # Test 5: Wait for completion
        final_results = self.wait_for_completion(task_id, max_wait=180)
        
        # Test 6: List tasks
        self.test_task_list()
        
        # Summary
        print("\n" + "=" * 50)
        if final_results and final_results.get('status') == 'completed':
            print("Full API test completed successfully!")
            print(f"   Research query: {query}")
            print(f"   Task ID: {task_id}")
            print(f"   Final status: {final_results['status']}")
            return True
        else:
            print("API test completed with issues")
            return False


def main():
    """Main test function"""
    # Get API URL from command line or use default
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    # Get test query from command line or use default
    test_query = sys.argv[2] if len(sys.argv) > 2 else "What are the latest trends in artificial intelligence?"
    
    print(f"FastAPI Research Agent Test")
    print(f"API URL: {api_url}")
    print(f"Test Query: {test_query}")
    print()
    
    # Create tester instance
    tester = APITester(api_url)
    
    try:
        # Run full test
        success = tester.run_full_test(test_query)
        
        if success:
            print("\nAll tests passed! API is working correctly.")
            sys.exit(0)
        else:
            print("\nSome tests failed. Check the API and try again.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()