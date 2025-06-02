"""
Main entry point for the FastMCP Calculator Agent.
"""

import asyncio
import argparse
import logging
import sys
from typing import Optional
import os
from dotenv import load_dotenv

from .agent import CalculatorAgent

# Load environment variables from .env file
load_dotenv()

# Get log level from environment, default to INFO  
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_level_value = getattr(logging, log_level, logging.INFO)

# Configure global logging (applies to all modules including external libraries)
logging.basicConfig(
    level=log_level_value,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True  # Force reconfiguration even if basicConfig was called before
)

# Also set the root logger level to ensure external libraries respect it
root_logger = logging.getLogger()
root_logger.setLevel(log_level_value)

# Suppress specific noisy loggers if log level is WARNING or higher
if log_level_value >= logging.WARNING:
    logging.getLogger('httpx').setLevel(logging.ERROR)
    logging.getLogger('mcp').setLevel(logging.ERROR)
    logging.getLogger('mcp.server').setLevel(logging.ERROR)
    logging.getLogger('mcp.server.lowlevel.server').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="FastMCP Calculator Agent supporting any OpenAI-compatible LLM provider",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  calculator-agent                    # Run with default settings
  calculator-agent --show-thinking    # Enable thinking display
  calculator-agent --no-stream        # Disable streaming
  calculator-agent --verbose          # Enable verbose logging

Supported LLM Providers:
  - OpenAI (GPT-4, GPT-3.5, etc.)
  - Qwen (qwen-turbo, qwen-plus, etc.)
  - Claude (claude-3-sonnet, etc.)
  - Groq (llama-3.1-70b-versatile, etc.)
  - Any OpenAI-compatible API
        """
    )
    
    parser.add_argument(
        "--show-thinking",
        action="store_true",
        help="Display the model's thinking process (default: False)"
    )
    
    parser.add_argument(
        "--no-stream",
        action="store_true", 
        help="Disable streaming output (default: streaming enabled)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging (default: False)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="FastMCP Calculator Agent 0.1.0"
    )
    
    return parser.parse_args()


async def main_async() -> int:
    """
    Main async function for the calculator agent.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    args = parse_arguments()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Initialize agent
    agent: Optional[CalculatorAgent] = None
    
    try:
        # Create agent instance
        agent = CalculatorAgent(
            show_thinking=args.show_thinking,
            enable_streaming=not args.no_stream
        )
        
        # Initialize agent components
        logger.info("Initializing Calculator Agent...")
        await agent.initialize()
        
        # Run interactive session
        await agent.run_interactive_session()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        if args.verbose:
            logger.exception("Detailed error information:")
        return 1
        
    finally:
        # Cleanup
        if agent:
            logger.info("Cleaning up...")
            await agent.cleanup()


def main() -> None:
    """
    Main entry point for the application.
    """
    try:
        # Check Python version
        if sys.version_info < (3, 10):
            print("Error: Python 3.10 or higher is required", file=sys.stderr)
            sys.exit(1)
            
        # Run the async main function
        exit_code = asyncio.run(main_async())
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user", file=sys.stderr)
        sys.exit(0)
        
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 