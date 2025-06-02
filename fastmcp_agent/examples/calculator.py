"""
Calculator Agent - Example Implementation of FastMCP Framework.

This module demonstrates how to create a specialized agent using the FastMCP framework.
The calculator agent showcases mathematical computation capabilities through MCP tools.
"""

import asyncio
import sys
from typing import Any

from ..agent import FastMCPAgent
from ..mcp_server import mcp_server


class CalculatorAgent(FastMCPAgent):
    """
    Calculator agent specialized for mathematical computations.
    
    This agent demonstrates how to extend the FastMCPAgent base class to create
    domain-specific agents. It provides natural language interface for mathematical
    calculations using FastMCP tools.
    
    Features:
    - Basic arithmetic operations (add, subtract, multiply, divide)
    - Advanced operations (power, square root)
    - Step-by-step problem solving
    - Natural language interaction
    """
    
    def __init__(self, show_thinking: bool = False, enable_streaming: bool = True):
        """
        Initialize the calculator agent.
        
        Args:
            show_thinking: Whether to display model thinking process
            enable_streaming: Whether to enable streaming responses
        """
        super().__init__(
            show_thinking=show_thinking,
            enable_streaming=enable_streaming,
            agent_name="Calculator Agent"
        )

    def get_system_prompt(self) -> str:
        """
        Get the calculator-specific system prompt.
        
        Returns:
            System prompt optimized for mathematical calculations
        """
        return """
You are a helpful calculator assistant with access to calculator tools for mathematical operations.

When a user asks a mathematical question:
1. Break down complex calculations into simpler steps
2. Use the available calculator tools to perform calculations
3. Explain your reasoning process clearly
4. Provide the final answer

Available tools:
- add(a, b): Add two numbers
- subtract(a, b): Subtract b from a
- multiply(a, b): Multiply two numbers
- divide(a, b): Divide a by b
- power(a, b): Raise a to the power of b
- sqrt(a): Calculate square root of a

Always use tools for calculations rather than doing math manually.
Show your work step by step so users can understand the solution process.
"""

    def get_mcp_server(self) -> Any:
        """
        Get the calculator MCP server instance.
        
        Returns:
            The calculator MCP server with mathematical tools
        """
        return mcp_server

    def get_welcome_message(self) -> str:
        """
        Get the welcome message for the calculator agent.
        
        Returns:
            Welcome message explaining calculator capabilities
        """
        return """🧮 Welcome to FastMCP Calculator Agent!

I can help you with mathematical calculations using FastMCP tools:
• Addition, Subtraction, Multiplication, Division
• Power operations and Square roots

Supports any OpenAI-compatible LLM provider (OpenAI, Qwen, Claude, Groq, etc.)
Ask me any math question, and I'll solve it step by step using the MCP server!
Type 'quit' or 'exit' to end the session."""


async def main():
    """
    Main function to run the calculator agent directly.
    
    This allows the calculator agent to be run as a standalone application.
    """
    try:
        # Create and initialize the calculator agent
        agent = CalculatorAgent(show_thinking=False, enable_streaming=True)
        
        # Initialize agent components
        await agent.initialize()
        
        # Run interactive session
        await agent.run_interactive_session()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'agent' in locals():
            await agent.cleanup()


def main_sync():
    """
    Synchronous main function for command line entry point.
    """
    asyncio.run(main())


if __name__ == "__main__":
    main_sync() 