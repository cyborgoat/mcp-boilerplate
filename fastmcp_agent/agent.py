"""
Generic Base Agent for FastMCP Framework.

This module provides a flexible base agent class that can be extended to create
specialized agents for different domains and use cases.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from fastmcp import Client
from .llm_client import create_llm_client, LLMClient

logger = logging.getLogger(__name__)
console = Console()


class FastMCPAgent(ABC):
    """
    Abstract base class for FastMCP agents.
    
    This class provides the core functionality for building intelligent agents
    that integrate with FastMCP servers and LLM providers. Subclasses should
    implement the abstract methods to define domain-specific behavior.
    
    Features:
    - MCP server integration
    - LLM communication with tool calling
    - Conversation management
    - Rich console interface
    - Configurable system prompts
    
    Attributes:
        show_thinking (bool): Whether to display model thinking
        enable_streaming (bool): Whether to enable streaming responses
        llm_client (LLMClient): The LLM client for natural language processing
        mcp_client (Client): The FastMCP client for tool execution
        conversation_history (List[Dict]): Chat history for context
        agent_name (str): Display name for the agent
    """
    
    def __init__(
        self, 
        show_thinking: bool = False, 
        enable_streaming: bool = True,
        agent_name: str = "FastMCP Agent"
    ):
        """
        Initialize the base agent.
        
        Args:
            show_thinking: Whether to display model thinking process
            enable_streaming: Whether to enable streaming responses
            agent_name: Display name for the agent
        """
        self.show_thinking = show_thinking
        self.enable_streaming = enable_streaming
        self.agent_name = agent_name
        self.llm_client: Optional[LLMClient] = None
        self.mcp_client: Optional[Client] = None
        self.conversation_history: List[Dict[str, str]] = []

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        
        Subclasses must implement this method to define their domain-specific
        system prompt that guides the LLM's behavior.
        
        Returns:
            System prompt string
        """
        pass

    @abstractmethod
    def get_mcp_server(self) -> Any:
        """
        Get the MCP server instance for this agent.
        
        Subclasses must implement this method to provide their specific
        MCP server that contains the tools for their domain.
        
        Returns:
            MCP server instance
        """
        pass

    @abstractmethod
    def get_welcome_message(self) -> str:
        """
        Get the welcome message displayed to users.
        
        Subclasses should implement this method to provide a domain-specific
        welcome message that explains the agent's capabilities.
        
        Returns:
            Welcome message string
        """
        pass

    async def initialize(self) -> None:
        """
        Initialize the agent components.
        
        This method:
        1. Creates the LLM client with domain-specific configuration
        2. Connects to the MCP server
        3. Registers available tools with the LLM
        4. Sets up tool execution
        
        Raises:
            Exception: If initialization fails
        """
        try:
            logger.info(f"🚀 Initializing {self.agent_name}...")
            
            # Initialize MCP client with domain-specific server
            logger.debug("🔌 Setting up MCP server connection...")
            mcp_server = self.get_mcp_server()
            self.mcp_client = Client(mcp_server)
            
            # Initialize LLM client with domain-specific system prompt
            logger.debug("🧠 Creating LLM client...")
            self.llm_client = create_llm_client(
                show_thinking=self.show_thinking,
                system_prompt=self.get_system_prompt()
            )
            
            # Connect to MCP server and get available tools
            logger.debug("🔧 Connecting to MCP server and retrieving tools...")
            async with self.mcp_client:
                mcp_tools = await self.mcp_client.list_tools()
                logger.info(f"📋 Retrieved {len(mcp_tools)} tools from MCP server: {[tool.name for tool in mcp_tools]}")
                
                # Convert MCP tools to OpenAI format for LLM
                logger.debug("🔄 Converting MCP tools to OpenAI format...")
                openai_tools = self._convert_mcp_tools_to_openai_format(mcp_tools)
                
                # Register tools with LLM client
                logger.info(f"🔗 Registering {len(openai_tools)} tools with LLM client...")
                self.llm_client.register_tools(openai_tools)
                
                # Set the tool executor to use MCP client
                logger.debug("⚙️  Setting up tool executor...")
                self.llm_client.set_tool_executor(self.execute_tool_via_mcp)
            
            logger.info(f"✅ {self.agent_name} initialized successfully")
            logger.info(f"🤖 LLM: {self.llm_client.model} at {self.llm_client.base_url}")
            logger.info(f"🔧 Tools available: {len(openai_tools)}")
            logger.info(f"🧠 Thinking mode: {'enabled' if self.show_thinking else 'disabled'}")
            logger.info(f"📡 Streaming: {'enabled' if self.enable_streaming else 'disabled'}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            logger.debug(f"❌ Full initialization error: {e}", exc_info=True)
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
            logger.info(f"🔄 Processing user input: '{user_input}'")
            
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
            
            # Log the start of LLM interaction
            logger.info(f"🤖 Sending request to LLM ({self.llm_client.model}) with {len(self.llm_client.tools) if hasattr(self.llm_client, 'tools') else 0} available tools")
            
            # Generate response
            response_content = ""
            tool_calls_made = False
            
            console.print(f"\n🤖 {self.agent_name}:", style="bold green")
            
            # Track if any tools were called during this interaction
            original_tool_executor = self.llm_client.tool_executor
            
            async def logging_tool_executor(tool_name: str, parameters: dict) -> Any:
                """Wrapper to log tool executions."""
                nonlocal tool_calls_made
                tool_calls_made = True
                logger.info(f"🔧 LLM requested tool execution: {tool_name}")
                logger.debug(f"🔧 Tool parameters: {parameters}")
                result = await original_tool_executor(tool_name, parameters)
                logger.info(f"✅ Tool {tool_name} completed, result returned to LLM")
                return result
            
            # Temporarily replace the tool executor with our logging version
            self.llm_client.tool_executor = logging_tool_executor
                
            try:
                async for chunk in self.llm_client.create_completion(
                    self.conversation_history,
                    stream=self.enable_streaming
                ):
                    console.print(chunk, end="", style="green")
                    response_content += chunk
            finally:
                # Restore original tool executor
                self.llm_client.tool_executor = original_tool_executor
                
            console.print("\n")
            
            # Log the interaction summary
            if tool_calls_made:
                logger.info(f"📋 Interaction completed: LLM used tools to generate response")
            else:
                logger.info(f"💬 Interaction completed: LLM provided direct response (no tools used)")
            
            logger.debug(f"📝 Response length: {len(response_content)} characters")
            
            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": response_content})
            
        except Exception as e:
            logger.error(f"❌ Error processing user input: {e}")
            logger.debug(f"❌ Full error details: {e}", exc_info=True)
            console.print(f"❌ Error: {str(e)}", style="bold red")

    async def run_interactive_session(self) -> None:
        """
        Run an interactive chat session.
        
        This method provides a user-friendly interface for interacting with
        the agent using natural language input.
        """
        console.print(Panel(
            self.get_welcome_message(),
            title=self.agent_name,
            border_style="bright_blue",
            expand=False
        ))
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]Your question[/bold cyan]")
                
                if user_input.lower() in ["quit", "exit", "bye"]:
                    console.print(f"\n👋 Goodbye! Thanks for using {self.agent_name}!", style="bold green")
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
        """
        Clean up resources and close connections.
        
        This method should be called when the agent is no longer needed
        to ensure proper cleanup of resources.
        """
        if self.llm_client:
            await self.llm_client.close()
        if self.mcp_client:
            await self.mcp_client.close()
        logger.info("Agent cleanup completed") 