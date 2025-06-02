"""
Generic LLM client supporting any OpenAI-compatible API provider with FastMCP integration.
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
    Generic LLM client supporting any OpenAI-compatible API with streaming and MCP tool integration.
    Supports providers like OpenAI, Qwen, Claude, Groq, and others.
    """

    def __init__(
        self, api_key: str, base_url: str, model: str, show_thinking: bool = False
    ):
        """
        Initialize the LLM client.

        Args:
            api_key: API key for the LLM provider
            base_url: Base URL for the API (e.g., https://api.openai.com/v1)
            model: Model name to use (e.g., gpt-4o-mini, qwen-turbo)
            show_thinking: Whether to display thinking content
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

        # System prompt for calculator agent
        self.system_prompt = """
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
"""

    def register_tools(self, tools: List[Dict[str, Any]]) -> None:
        """
        Register MCP tools for use with the LLM.

        Args:
            tools: List of tool definitions from MCP server
        """
        self.tools = tools
        logger.info(
            f"Registered {len(tools)} tools: {[tool['function']['name'] for tool in tools]}"
        )

    def set_tool_executor(self, executor: Callable) -> None:
        """
        Set the tool executor function.

        Args:
            executor: Function that can execute tools by name and parameters
        """
        self.tool_executor = executor

    async def create_completion_with_tools(
        self, messages: List[Dict[str, str]], stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Create a completion with full tool calling support.

        Args:
            messages: List of messages in OpenAI format
            stream: Whether to stream the response

        Yields:
            Streaming response chunks
        """
        # Add system message if not present
        working_messages = messages.copy()
        if not working_messages or working_messages[0].get("role") != "system":
            working_messages.insert(
                0, {"role": "system", "content": self.system_prompt}
            )

        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            try:
                # Use OpenAI client to create completion
                if self.tools:
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=working_messages,
                        tools=self.tools,
                        tool_choice="auto",
                        temperature=0.1,
                        max_tokens=2000,
                    )
                else:
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=working_messages,
                        temperature=0.1,
                        max_tokens=2000,
                    )

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

                        logger.info(
                            f"Executing tool: {tool_name} with args: {tool_args}"
                        )

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
                            tool_result = (
                                f"Error: No tool executor available for {tool_name}"
                            )

                        # Add tool result to messages
                        working_messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_id,
                                "content": tool_result,
                            }
                        )

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
                                await asyncio.sleep(
                                    0.05
                                )  # Small delay for streaming effect
                        else:
                            yield content
                    return

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                yield f"Error: {str(e)}"
                return

        yield "Error: Maximum tool calling iterations reached"

    async def create_completion(
        self, messages: List[Dict[str, str]], stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Create a completion using the LLM with tool calling support.

        Args:
            messages: List of messages in OpenAI format
            stream: Whether to stream the response

        Yields:
            Streaming response chunks
        """
        async for chunk in self.create_completion_with_tools(messages, stream):
            yield chunk

    async def close(self) -> None:
        """Close the HTTP client."""
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
        Display the main response content.

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

    Returns:
        Dictionary containing configuration values

    Raises:
        ValueError: If required environment variables are missing
    """
    # Load from .env file if it exists
    load_dotenv()

    config = {}

    # Required configuration with defaults
    config["llm_api_key"] = os.getenv("LLM_API_KEY")
    if not config["llm_api_key"]:
        raise ValueError("Missing required environment variable: LLM_API_KEY")
    
    config["llm_base_url"] = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    config["llm_model"] = os.getenv("LLM_MODEL", "gpt-4o-mini")

    return config
