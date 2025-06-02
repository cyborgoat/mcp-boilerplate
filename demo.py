#!/usr/bin/env python3
"""
Demo script to showcase the FastMCP Calculator Agent with LLM integration.
Supports any OpenAI-compatible LLM provider (OpenAI, Qwen, Claude, Groq, etc.).
"""

import asyncio
import sys
from calculator_agent.agent import CalculatorAgent

async def demo():
    """Run a demonstration of the calculator agent."""
    print("🧮 FastMCP Calculator Agent Demo")
    print("=" * 50)
    print("Supports any OpenAI-compatible LLM provider!")
    print("(OpenAI, Qwen, Claude, Groq, etc.)\n")
    
    # Create and initialize the agent
    agent = CalculatorAgent(show_thinking=False, enable_streaming=False)
    
    try:
        print("📡 Initializing agent and connecting to MCP server...")
        await agent.initialize()
        print("✅ Agent initialized successfully!")
        
        # Test questions
        test_questions = [
            "What is 9 + 1053?",
            "Calculate 15 * 23 + 7",
            "What's the square root of 144?",
            "Compute 2^8",
        ]
        
        print(f"\n🤖 Testing {len(test_questions)} calculations...\n")
        
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
        print("The agent successfully used FastMCP to connect to the MCP server")
        print("and execute calculator tools via your configured LLM provider!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
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