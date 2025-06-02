#!/usr/bin/env python3
"""
Demo script to show logging output for tool vs non-tool interactions.

This demonstrates the enhanced logging in the FastMCP Agent Framework.
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def demo_with_logging():
    """
    Demo showing different interaction types and their logging output.
    """
    print("🔍 FastMCP Agent Logging Demo")
    print("=" * 50)
    
    try:
        from fastmcp_agent.examples.calculator import CalculatorAgent
        
        # Create agent with DEBUG logging
        agent = CalculatorAgent(show_thinking=False, enable_streaming=False)
        
        print("📡 Initializing agent (watch for initialization logs)...")
        await agent.initialize()
        
        print("\n" + "=" * 50)
        print("🧪 Testing different interaction types:")
        print("=" * 50)
        
        # Test cases: tool-calling vs non-tool-calling
        test_cases = [
            {
                "question": "What is 15 + 25?",
                "expected": "tool_calling",
                "description": "Mathematical question - should trigger tool calling"
            },
            {
                "question": "Hello, how are you?",
                "expected": "direct_response", 
                "description": "General greeting - should get direct LLM response"
            },
            {
                "question": "Calculate the square root of 144",
                "expected": "tool_calling",
                "description": "Square root calculation - should trigger tool calling"
            },
            {
                "question": "What's the weather like?",
                "expected": "direct_response",
                "description": "Weather question - should get direct response (no weather tools)"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[Test {i}] {test_case['description']}")
            print(f"Question: '{test_case['question']}'")
            print(f"Expected: {test_case['expected']}")
            print("-" * 40)
            
            # Process the question and observe logging
            await agent.process_user_input(test_case['question'])
            
            print("\n⏳ (Check the logs above to see if tools were called or not)")
            
        print("\n" + "=" * 50)
        print("📋 Demo completed!")
        print("\nLogging patterns to observe:")
        print("🔧 Tool calling interactions show:")
        print("  • 'LLM requested tool execution: [tool_name]'")
        print("  • 'Tool [tool_name] completed, result returned to LLM'") 
        print("  • 'Interaction completed: LLM used tools to generate response'")
        print("\n💬 Direct response interactions show:")
        print("  • 'Interaction completed: LLM provided direct response (no tools used)'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you have a valid LLM_API_KEY in your .env file")
        print("2. Set LOG_LEVEL=DEBUG in your .env file")
        print("3. Run: uv sync")
        return 1
    finally:
        if 'agent' in locals():
            await agent.cleanup()
    
    return 0

def check_logging_config():
    """Check if logging is configured correctly."""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    print(f"Current LOG_LEVEL: {log_level}")
    
    if log_level != 'DEBUG':
        print(f"⚠️  Warning: LOG_LEVEL is set to {log_level}")
        print("For detailed tool calling logs, set LOG_LEVEL=DEBUG in your .env file")
        print("\nTo see the full logging output:")
        print("1. Edit your .env file")
        print("2. Change LOG_LEVEL=DEBUG")
        print("3. Re-run this demo")
        return False
    else:
        print("✅ DEBUG logging is enabled - you'll see detailed logs!")
        return True

def main():
    """Main function."""
    
    print("🚀 FastMCP Agent Logging Demo")
    print("This demo shows the difference between tool-calling and direct responses")
    print("=" * 70)
    
    # Check logging configuration
    if not check_logging_config():
        print("\n⚠️  Running demo anyway, but you may not see detailed logs")
        input("Press Enter to continue...")
    
    print("\n🔄 Starting agent interaction demo...")
    
    try:
        return asyncio.run(demo_with_logging())
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
        return 0
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 