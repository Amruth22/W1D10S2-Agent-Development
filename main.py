"""
LangChain AI Research Agent - Main Application
Professional implementation using LangChain framework
"""

from agents.research_agent import LangChainResearchAgent
import sys
import json


def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print("LangChain AI Research Agent")
    print("Professional Agent Framework Implementation")
    print("=" * 70)
    print("Powered by:")
    print("• Gemini 2.5 Flash LLM")
    print("• LangChain Agent Framework")
    print("• Professional Tool Ecosystem")
    print("• Advanced Memory Management")
    print("• ReAct Pattern Implementation")
    print()
    print("Capabilities:")
    print("• Real-time web search and information retrieval")
    print("• Mathematical calculations and data analysis")
    print("• Professional research report generation")
    print("• Conversation context and research continuity")
    print("• File management and data persistence")
    print()
    print("Commands:")
    print("• Type your research question")
    print("• 'history' - View conversation history")
    print("• 'context' - Show current research context")
    print("• 'tools' - List available tools")
    print("• 'files' - List generated files")
    print("• 'stats' - Show memory statistics")
    print("• 'info' - Show agent configuration")
    print("• 'clear' - Clear conversation memory")
    print("• 'help' - Show example queries")
    print("• 'quit' or 'exit' - Exit the application")
    print("=" * 70)


def print_example_queries():
    """Print example research queries"""
    print("\nProfessional Research Examples:")
    print()
    print("Web Research:")
    print("  • 'Research the latest developments in quantum computing'")
    print("  • 'Analyze current trends in renewable energy adoption'")
    print("  • 'Study the impact of AI on healthcare industry'")
    print()
    print("Data Analysis:")
    print("  • 'Calculate compound annual growth rate of 15% over 10 years'")
    print("  • 'Find the average and percentage change from these values: 100, 120, 95, 130'")
    print("  • 'Analyze statistical significance of a 25% improvement'")
    print()
    print("Report Generation:")
    print("  • 'Create a comprehensive report on cybersecurity trends in 2024'")
    print("  • 'Research and analyze blockchain technology adoption'")
    print("  • 'Study climate change impacts and create a summary report'")
    print()
    print("Multi-step Research:")
    print("  • 'Research electric vehicle market, calculate growth rates, and create a report'")
    print("  • 'Analyze AI startup funding trends and compare with previous years'")
    print("  • 'Study remote work productivity data and provide statistical insights'")
    print()


def main():
    """Main application loop"""
    print_banner()
    print_example_queries()
    
    # Initialize the LangChain research agent
    try:
        print("Initializing LangChain Research Agent...")
        agent = LangChainResearchAgent()
        
        # Show agent info
        info = agent.get_agent_info()
        print(f"Agent ready! Framework: {info['framework']}, LLM: {info['llm']}")
        print(f"Tools available: {', '.join(info['tools'])}")
        print("\nReady for professional research! What would you like to investigate?\n")
        
    except Exception as e:
        print(f"Error initializing agent: {e}")
        print("Please check your configuration and dependencies.")
        return
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            user_input = input("Research Query: ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("\nThank you for using LangChain AI Research Agent!")
                break
            
            elif user_input.lower() == 'clear':
                agent.clear_memory()
                continue
            
            elif user_input.lower() == 'history':
                history = agent.get_conversation_history()
                print(f"\n{history}\n")
                continue
            
            elif user_input.lower() == 'context':
                context = agent.get_research_context()
                print(f"\nCurrent Research Context:\n{context}\n")
                continue
            
            elif user_input.lower() == 'tools':
                tools = agent.get_available_tools()
                print("\nAvailable Tools:")
                for name, description in tools.items():
                    print(f"• {name}: {description[:100]}...")
                print()
                continue
            
            elif user_input.lower() == 'files':
                files = agent.list_generated_files()
                print(f"\nGenerated Files:\n{files}\n")
                continue
            
            elif user_input.lower() == 'stats':
                stats = agent.get_memory_stats()
                print(f"\nMemory Statistics:")
                for key, value in stats.items():
                    print(f"• {key}: {value}")
                print()
                continue
            
            elif user_input.lower() == 'info':
                info = agent.get_agent_info()
                print(f"\nAgent Configuration:")
                print(json.dumps(info, indent=2))
                print()
                continue
            
            elif user_input.lower() == 'help':
                print_example_queries()
                continue
            
            # Conduct research using LangChain agent
            print(f"\nLangChain Agent researching: {user_input}")
            print("Processing with professional tools...\n")
            
            response = agent.research(user_input)
            
            print("Research Results:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            print()
            
        except KeyboardInterrupt:
            print("\n\nResearch session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError during research: {e}")
            print("Please try rephrasing your query or check your connection.\n")


def example_research_session():
    """
    Example of how to use the LangChain agent programmatically
    Demonstrates professional agent framework usage
    """
    print("\nRunning LangChain Example Research Session...\n")
    
    # Initialize agent
    agent = LangChainResearchAgent()
    
    # Show agent configuration
    info = agent.get_agent_info()
    print(f"Agent Info: {info['framework']} with {info['llm']}")
    print(f"Tools: {', '.join(info['tools'])}")
    print()
    
    # Example research queries demonstrating different capabilities
    queries = [
        "Research the latest trends in artificial intelligence for 2024",
        "Calculate the compound annual growth rate for an investment that grows from $1000 to $2500 over 8 years",
        "Create a comprehensive report on quantum computing developments"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"Example {i}: {query}")
        print("LangChain Agent processing...\n")
        
        response = agent.research(query)
        
        print(f"Response: {response[:300]}...\n")
        print("-" * 60)
    
    # Show session statistics
    stats = agent.get_memory_stats()
    print(f"\nSession Statistics:")
    for key, value in stats.items():
        print(f"• {key}: {value}")
    
    # Show generated files
    files = agent.list_generated_files()
    print(f"\nGenerated Files:\n{files}")
    
    print("\nLangChain example session completed!")
    print("This demonstrates professional agent framework implementation")


if __name__ == "__main__":
    # Check if running in example mode
    if len(sys.argv) > 1 and sys.argv[1] == "--example":
        example_research_session()
    else:
        main()