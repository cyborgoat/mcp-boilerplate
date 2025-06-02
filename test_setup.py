#!/usr/bin/env python3
"""
Simple test script to verify the FastMCP Calculator Agent setup.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import fastmcp
        print("✅ FastMCP imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import FastMCP: {e}")
        return False
    
    try:
        import httpx
        print("✅ HTTPX imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import HTTPX: {e}")
        return False
    
    try:
        from rich.console import Console
        from rich.panel import Panel
        print("✅ Rich imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Rich: {e}")
        return False
    
    try:
        import calculator_agent
        print("✅ Calculator Agent package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Calculator Agent: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of the calculator tools."""
    print("\nTesting calculator tools...")
    
    try:
        from calculator_agent.agent import CalculatorAgent
        
        # Create agent instance
        agent = CalculatorAgent(show_thinking=False, enable_streaming=False)
        
        # Initialize the agent (this connects to MCP server)
        import asyncio
        asyncio.run(agent.initialize())
        
        # Test calculator functions
        test_cases = [
            ("add", {"a": 5, "b": 3}, 8),
            ("subtract", {"a": 10, "b": 4}, 6),
            ("multiply", {"a": 6, "b": 7}, 42),
            ("divide", {"a": 15, "b": 3}, 5),
            ("power", {"a": 2, "b": 3}, 8),
            ("sqrt", {"a": 16}, 4),
        ]
        
        all_passed = True
        for tool_name, params, expected in test_cases:
            result = asyncio.run(agent.execute_tool_via_mcp(tool_name, params))
            # Try to convert result to number for comparison
            try:
                numeric_result = float(result)
                if abs(numeric_result - expected) < 0.0001:  # Allow for floating point precision
                    print(f"✅ {tool_name}{params} = {numeric_result}")
                else:
                    print(f"❌ {tool_name}{params} = {numeric_result}, expected {expected}")
                    all_passed = False
            except (ValueError, TypeError):
                # If result is not numeric, check if it contains the expected value
                if str(expected) in str(result):
                    print(f"✅ {tool_name}{params} = {result}")
                else:
                    print(f"❌ {tool_name}{params} = {result}, expected {expected}")
                    all_passed = False
        
        # Clean up
        asyncio.run(agent.cleanup())
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing calculator functionality: {e}")
        return False

def check_environment():
    """Check environment configuration."""
    print("\nChecking environment...")
    
    # Check Python version
    if sys.version_info >= (3, 10):
        print(f"✅ Python version: {sys.version}")
    else:
        print(f"❌ Python version {sys.version} is too old. Requires 3.10+")
        return False
    
    # Check for .env file
    if os.path.exists(".env"):
        print("✅ .env file found")
    else:
        print("⚠️  No .env file found (you'll need to create one with your Qwen API key)")
    
    return True

def main():
    """Run all tests."""
    print("FastMCP Calculator Agent - Setup Test")
    print("=" * 50)
    
    success = True
    
    success &= check_environment()
    success &= test_imports()
    success &= test_basic_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Your setup is working correctly.")
        print("\nNext steps:")
        print("1. Create a .env file with your LLM provider API key")
        print("2. Run: uv run calculator-agent")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 