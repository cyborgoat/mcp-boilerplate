"""
Generic LLM Client for FastMCP Agent Framework.

This module provides a flexible LLM client that works with any OpenAI-compatible API
and integrates seamlessly with FastMCP servers for tool-based interactions.

Features:
- Support for multiple LLM providers (OpenAI, Qwen, Claude, Groq, etc.)
- Tool calling integration with MCP servers
- Streaming and non-streaming responses
- Configurable system prompts
- Rich console output formatting
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, AsyncGenerator, Any, Callable
from openai import AsyncOpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
console = Console()


class LLMClient:
    """
    Generic LLM client supporting any OpenAI-compatible API with FastMCP integration.
    
    This client can be used with various LLM providers including OpenAI, Qwen, Claude,
    Groq, and any other service that implements the OpenAI chat completions API.
    
    Features:
    - Tool calling support for MCP server integration
    - Streaming and non-streaming responses
    - Configurable system prompts
    - Rich console formatting
    - Comprehensive error handling
    
    Attributes:
        api_key (str): API key for the LLM provider
        base_url (str): Base URL for the API endpoint
        model (str): Model name to use for completions
        show_thinking (bool): Whether to display thinking content
        tools (List[Dict]): Available tools for the LLM to call
        tool_executor (Callable): Function to execute tool calls
    """
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str, 
        model: str, 
        show_thinking: bool = False,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize the LLM client.
        
        Args:
            api_key: API key for the LLM provider
            base_url: Base URL for the API (e.g., https://api.openai.com/v1)
            model: Model name to use (e.g., gpt-4o-mini, qwen-turbo)
            show_thinking: Whether to display thinking content
            system_prompt: Custom system prompt (if None, uses default)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.show_thinking = show_thinking
        self.tools: List[Dict[str, Any]] = []
        self.tool_executor: Optional[Callable] = None
        
        # Initialize OpenAI client with custom base URL
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=60.0,
        )
        
        # Set system prompt (use provided or default)
        self.system_prompt = system_prompt or self._get_default_system_prompt()

    def _get_default_system_prompt(self) -> str:
        """
        Get the default system prompt for tool-enabled agents.
        
        Returns:
            Default system prompt string
        """
        return """
You are a helpful AI assistant with access to various tools to help users.

When a user asks a question:
1. Analyze the request to understand what they need
2. Use the available tools when appropriate to provide accurate information
3. Explain your reasoning process clearly
4. Provide comprehensive and helpful responses

Always use tools when they can help provide better, more accurate answers.
Be clear about what tools you're using and why.
"""

    def set_system_prompt(self, prompt: str) -> None:
        """
        Set a custom system prompt for the agent.
        
        Args:
            prompt: New system prompt to use
        """
        self.system_prompt = prompt
        logger.info("System prompt updated")

    def register_tools(self, tools: List[Dict[str, Any]]) -> None:
        """
        Register MCP tools for use with the LLM.
        
        Args:
            tools: List of tool definitions from MCP server in OpenAI format
        """
        self.tools = tools
        tool_names = [tool['function']['name'] for tool in tools]
        logger.info(f"Registered {len(tools)} tools: {tool_names}")

    def set_tool_executor(self, executor: Callable) -> None:
        """
        Set the tool executor function.
        
        Args:
            executor: Async function that can execute tools by name and parameters
                     Should have signature: async def executor(tool_name: str, parameters: Dict) -> Any
        """
        self.tool_executor = executor
        logger.debug("Tool executor configured")

    async def create_completion_with_tools(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = True,
        max_iterations: int = 5
    ) -> AsyncGenerator[str, None]:
        """
        Create a completion with full tool calling support.
        
        This method handles the complete tool calling loop:
        1. Send messages to LLM
        2. If LLM wants to call tools, execute them
        3. Send tool results back to LLM
        4. Return final response
        
        Args:
            messages: List of messages in OpenAI format
            stream: Whether to stream the response
            max_iterations: Maximum number of tool calling iterations to prevent loops
            
        Yields:
            Streaming response chunks
        """
        # Add system message if not present
        working_messages = messages.copy()
        if not working_messages or working_messages[0].get("role") != "system":
            working_messages.insert(
                0, {"role": "system", "content": self.system_prompt}
            )

        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            try:
                # Create completion request
                completion_kwargs = {
                    "model": self.model,
                    "messages": working_messages,
                    "temperature": 0.1,
                    "max_tokens": 2000,
                }
                
                # Add tools if available
                if self.tools:
                    completion_kwargs["tools"] = self.tools
                    completion_kwargs["tool_choice"] = "auto"
                
                # Use OpenAI client to create completion
                response = await self.client.chat.completions.create(**completion_kwargs)
                choice = response.choices[0]
                message = choice.message

                # Check if the model wants to call tools
                if message.tool_calls:
                    # Add the assistant's message with tool calls
                    working_messages.append(message.model_dump())

                    # Execute each tool call
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        tool_id = tool_call.id

                        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                        # Execute the tool
                        if self.tool_executor:
                            try:
                                result = await self.tool_executor(tool_name, tool_args)
                                tool_result = str(result)
                                logger.info(f"Tool {tool_name} result: {tool_result}")
                            except Exception as e:
                                tool_result = f"Error executing {tool_name}: {str(e)}"
                                logger.error(f"Tool execution error: {e}")
                        else:
                            tool_result = f"Error: No tool executor available for {tool_name}"

                        # Add tool result to messages
                        working_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": tool_result,
                        })

                    # Continue the loop to get the final response
                    continue
                else:
                    # No tool calls, return the content
                    content = message.content or ""
                    if content:
                        if stream:
                            # Simulate streaming for the final response
                            words = content.split()
                            for i, word in enumerate(words):
                                yield word + (" " if i < len(words) - 1 else "")
                                await asyncio.sleep(0.05)  # Small delay for streaming effect
                        else:
                            yield content
                    return

            except Exception as e:
                logger.error(f"Unexpected error in completion: {e}")
                yield f"Error: {str(e)}"
                return

        yield "Error: Maximum tool calling iterations reached"

    async def create_completion(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Create a completion using the LLM with tool calling support.
        
        This is the main method for generating responses. It automatically
        handles tool calling if tools are registered.
        
        Args:
            messages: List of messages in OpenAI format
            stream: Whether to stream the response
            
        Yields:
            Streaming response chunks
        """
        async for chunk in self.create_completion_with_tools(messages, stream):
            yield chunk

    async def close(self) -> None:
        """
        Close the LLM client and clean up resources.
        
        Note: AsyncOpenAI client doesn't require explicit closing,
        but this method is provided for consistency.
        """
        pass

    def display_thinking(self, content: str) -> None:
        """
        Display thinking content in a formatted panel.
        
        Args:
            content: The thinking content to display
        """
        if self.show_thinking and content.strip():
            thinking_panel = Panel(
                Markdown(content),
                title="🧠 Model Thinking",
                border_style="blue",
                expand=False,
            )
            console.print(thinking_panel)

    def display_response(self, content: str) -> None:
        """
        Display the main response content in a formatted panel.
        
        Args:
            content: The response content to display
        """
        response_panel = Panel(
            Markdown(content),
            title="🤖 Assistant Response",
            border_style="green",
            expand=False,
        )
        console.print(response_panel)


def load_config() -> Dict[str, str]:
    """
    Load configuration from environment variables.
    
    This function loads configuration from a .env file if present,
    then reads environment variables for LLM settings.
    
    Returns:
        Dictionary containing configuration values
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Load from .env file if it exists
    load_dotenv()

    config = {}

    # Required configuration
    config["llm_api_key"] = os.getenv("LLM_API_KEY")
    if not config["llm_api_key"]:
        raise ValueError(
            "Missing required environment variable: LLM_API_KEY\n"
            "Please set your API key in the .env file or environment variables."
        )
    
    # Optional configuration with sensible defaults
    config["llm_base_url"] = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    config["llm_model"] = os.getenv("LLM_MODEL", "gpt-4o-mini")

    return config


def create_llm_client(
    show_thinking: bool = False, 
    system_prompt: Optional[str] = None
) -> LLMClient:
    """
    Factory function to create an LLM client with configuration from environment.
    
    Args:
        show_thinking: Whether to enable thinking display
        system_prompt: Custom system prompt (if None, uses default)
        
    Returns:
        Configured LLMClient instance
        
    Raises:
        ValueError: If configuration is invalid
    """
    config = load_config()
    
    return LLMClient(
        api_key=config["llm_api_key"],
        base_url=config["llm_base_url"],
        model=config["llm_model"],
        show_thinking=show_thinking,
        system_prompt=system_prompt
    )
