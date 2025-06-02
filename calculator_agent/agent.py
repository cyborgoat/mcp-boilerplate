"""
Main agent orchestrator that connects to MCP server via FastMCP client and communicates with LLM.
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

from fastmcp import Client
from .llm_client import LLMClient, load_config
from .mcp_server import mcp_server

logger = logging.getLogger(__name__)

console = Console()


class CalculatorAgent:
    """
    Main agent that orchestrates between MCP server (via FastMCP client) and LLM.
    Supports any OpenAI-compatible LLM provider (OpenAI, Qwen, Claude, Groq, etc.).
    """
    
    def __init__(self, show_thinking: bool = False, enable_streaming: bool = True):
        """
        Initialize the calculator agent.
        
        Args:
            show_thinking: Whether to display model thinking
            enable_streaming: Whether to enable streaming responses
        """
        self.show_thinking = show_thinking
        self.enable_streaming = enable_streaming
        self.llm_client: Optional[LLMClient] = None
        self.mcp_client: Optional[Client] = None
        self.conversation_history: List[Dict[str, str]] = []

    async def initialize(self) -> None:
        """Initialize the agent components."""
        try:
            # Load configuration
            config = load_config()
            
            # Initialize MCP client (connects to our MCP server)
            self.mcp_client = Client(mcp_server)
            
            # Initialize LLM client
            self.llm_client = LLMClient(
                api_key=config["llm_api_key"],
                base_url=config["llm_base_url"],
                model=config["llm_model"],
                show_thinking=self.show_thinking
            )
            
            # Connect to MCP server and get tools
            async with self.mcp_client:
                mcp_tools = await self.mcp_client.list_tools()
                logger.info(f"Retrieved {len(mcp_tools)} tools from MCP server: {[tool.name for tool in mcp_tools]}")
                
                # Convert MCP tools to OpenAI format for LLM
                openai_tools = self._convert_mcp_tools_to_openai_format(mcp_tools)
                
                # Register tools with LLM client
                self.llm_client.register_tools(openai_tools)
                
                # Set the tool executor to use MCP client
                self.llm_client.set_tool_executor(self.execute_tool_via_mcp)
            
            logger.info("Calculator agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise

    def _convert_mcp_tools_to_openai_format(self, mcp_tools) -> List[Dict[str, Any]]:
        """
        Convert MCP tools to OpenAI function calling format for LLM.
        
        Args:
            mcp_tools: List of MCP tools from the server
            
        Returns:
            List of tools in OpenAI format
        """
        openai_tools = []
        
        for tool in mcp_tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or f"Execute {tool.name} tool",
                    "parameters": tool.inputSchema or {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            openai_tools.append(openai_tool)
        
        return openai_tools

    async def execute_tool_via_mcp(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute a tool via the MCP client.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            
        Returns:
            Result of the tool execution
        """
        try:
            logger.info(f"🔧 Executing tool via MCP: {tool_name} with parameters: {parameters}")
            
            # Use MCP client to execute the tool
            async with self.mcp_client:
                result = await self.mcp_client.call_tool(tool_name, parameters)
                
                # Extract text content from the result
                if result and len(result) > 0:
                    # MCP returns a list of content objects
                    content = result[0]
                    if hasattr(content, 'text'):
                        tool_result = content.text
                    else:
                        tool_result = str(content)
                else:
                    tool_result = "No result returned"
                    
                logger.info(f"✅ Tool {tool_name} result: {tool_result}")
                return tool_result
                
        except Exception as e:
            error_msg = f"Error executing {tool_name}: {str(e)}"
            logger.error(f"❌ Tool execution error: {error_msg}")
            return error_msg

    async def process_user_input(self, user_input: str) -> None:
        """
        Process user input and generate response.
        
        Args:
            user_input: The user's question or request
        """
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Display user input
            user_panel = Panel(
                user_input,
                title="👤 You",
                border_style="cyan",
                expand=False
            )
            console.print(user_panel)
            
            # Generate response
            response_content = ""
            
            console.print("\n🤖 Assistant:", style="bold green")
                
            async for chunk in self.llm_client.create_completion(
                self.conversation_history,
                stream=self.enable_streaming
            ):
                console.print(chunk, end="", style="green")
                response_content += chunk
                
            console.print("\n")
            
            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": response_content})
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            console.print(f"❌ Error: {str(e)}", style="bold red")

    async def run_interactive_session(self) -> None:
        """Run an interactive chat session."""
        console.print(Panel(
            "🧮 Welcome to FastMCP Calculator Agent!\n\n"
            "I can help you with mathematical calculations using FastMCP tools:\n"
            "• Addition, Subtraction, Multiplication, Division\n"
            "• Power operations and Square roots\n\n"
            "Supports any OpenAI-compatible LLM provider (OpenAI, Qwen, Claude, Groq, etc.)\n"
            "Ask me any math question, and I'll solve it step by step using the MCP server!\n"
            "Type 'quit' or 'exit' to end the session.",
            title="Calculator Agent",
            border_style="bright_blue",
            expand=False
        ))
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]Your question[/bold cyan]")
                
                if user_input.lower() in ["quit", "exit", "bye"]:
                    console.print("\n👋 Goodbye! Thanks for using Calculator Agent!", style="bold green")
                    break
                
                if user_input.strip():
                    await self.process_user_input(user_input)
                    
            except KeyboardInterrupt:
                console.print("\n\n👋 Session ended by user. Goodbye!", style="bold yellow")
                break
            except Exception as e:
                logger.error(f"Session error: {e}")
                console.print(f"❌ Unexpected error: {str(e)}", style="bold red")

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.llm_client:
            await self.llm_client.close()
        if self.mcp_client:
            await self.mcp_client.close()
        logger.info("Agent cleanup completed") 