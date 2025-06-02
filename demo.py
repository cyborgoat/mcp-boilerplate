#!/usr/bin/env python3
"""
Demo script for the FastMCP Agent Framework.

This script demonstrates how to use the framework to build intelligent agents
that integrate FastMCP servers with LLM providers. The calculator agent serves
as a practical example of the framework's capabilities.

Features demonstrated:
- FastMCP server integration
- Tool calling with LLM providers
- Multi-step problem solving
- OpenAI-compatible API support
"""

import asyncio
import sys
from fastmcp_agent.examples.calculator import CalculatorAgent

async def demo():
    """
    Run a demonstration of the FastMCP Agent Framework using the calculator agent.
    
    This demo shows how agents can:
    1. Connect to MCP servers
    2. Integrate with LLM providers
    3. Execute tools through natural language
    4. Handle complex multi-step problems
    """
    print("🚀 FastMCP Agent Framework Demo")
    print("=" * 50)
    print("Demonstrating intelligent agent capabilities!")
    print("Using Calculator Agent as an example\n")
    
    # Create and initialize the calculator agent
    agent = CalculatorAgent(show_thinking=False, enable_streaming=False)
    
    try:
        print("📡 Initializing agent and connecting to MCP server...")
        await agent.initialize()
        print("✅ Agent initialized successfully!")
        
        # Test questions demonstrating different capabilities
        test_questions = [
            "What is 9 + 1053?",                    # Basic arithmetic
            "Calculate 15 * 23 + 7",                # Multi-step calculation
            "What's the square root of 144?",       # Special functions
            "Compute 2^8",                          # Power operations
        ]
        
        print(f"\n🤖 Testing {len(test_questions)} mathematical problems...\n")
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n[Test {i}] Question: {question}")
            print("-" * 40)
            
            # Add to conversation history and process
            agent.conversation_history.append({"role": "user", "content": question})
            
            # Get response from LLM via MCP tools
            response_chunks = []
            async for chunk in agent.llm_client.create_completion(
                agent.conversation_history,
                stream=False
            ):
                response_chunks.append(chunk)
            
            response = "".join(response_chunks)
            agent.conversation_history.append({"role": "assistant", "content": response})
            
            print(f"🤖 Response: {response}")
            
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("\nWhat was demonstrated:")
        print("• FastMCP server integration")
        print("• LLM tool calling capabilities")
        print("• Multi-step problem solving")
        print("• OpenAI-compatible API support")
        print("• Natural language to tool execution")
        print("\nThe framework is ready for building custom agents!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("\nTroubleshooting tips:")
        print("• Check your .env file configuration")
        print("• Verify your LLM API key and access")
        print("• Ensure all dependencies are installed")
        return 1
    finally:
        await agent.cleanup()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(demo()))
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user.")
        sys.exit(0) 