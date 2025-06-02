"""
MCP Server providing calculator tools using FastMCP.
"""

import asyncio
import json
import logging
import os
from typing import Union
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp_server = FastMCP("Calculator Server 🧮")


@mcp_server.tool()
def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The sum of a and b
    """
    result = a + b
    logger.info(f"Adding {a} + {b} = {result}")
    return result


@mcp_server.tool()
def subtract(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Subtract the second number from the first number.
    
    Args:
        a: Number to subtract from
        b: Number to subtract
        
    Returns:
        The difference of a and b
    """
    result = a - b
    logger.info(f"Subtracting {a} - {b} = {result}")
    return result


@mcp_server.tool()
def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Multiply two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The product of a and b
    """
    result = a * b
    logger.info(f"Multiplying {a} × {b} = {result}")
    return result


@mcp_server.tool()
def divide(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Divide the first number by the second number.
    
    Args:
        a: Dividend (number to be divided)
        b: Divisor (number to divide by)
        
    Returns:
        The quotient of a and b
        
    Raises:
        ValueError: If attempting to divide by zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    
    result = a / b
    logger.info(f"Dividing {a} ÷ {b} = {result}")
    return result


@mcp_server.tool()
def power(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Raise the first number to the power of the second number.
    
    Args:
        a: Base number
        b: Exponent
        
    Returns:
        a raised to the power of b
    """
    result = a ** b
    logger.info(f"Power {a} ^ {b} = {result}")
    return result


@mcp_server.tool()
def sqrt(a: Union[int, float]) -> float:
    """
    Calculate the square root of a number.
    
    Args:
        a: Number to calculate square root of
        
    Returns:
        The square root of a
        
    Raises:
        ValueError: If attempting to calculate square root of a negative number
    """
    if a < 0:
        raise ValueError("Cannot calculate square root of a negative number")
    
    import math
    result = math.sqrt(a)
    logger.info(f"Square root of {a} = {result}")
    return result


async def run_server():
    """Run the FastMCP calculator server."""
    try:
        logger.info("Starting Calculator MCP Server...")
        await mcp_server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_server()) 