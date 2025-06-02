#!/usr/bin/env python3
"""
Test script to demonstrate correct logging configuration for FastMCP Agent Framework.

This script shows how to properly configure the .env file for detailed logging.
"""

import os
import sys

def create_test_env_file():
    """Create a test .env file with correct logging configuration."""
    
    env_content = """# LLM API Configuration (OpenAI-compatible)
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# Example configurations for different providers:
# OpenAI: LLM_BASE_URL=https://api.openai.com/v1, LLM_MODEL=gpt-4o-mini
# Qwen: LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1, LLM_MODEL=qwen-turbo
# Claude: LLM_BASE_URL=https://api.anthropic.com/v1, LLM_MODEL=claude-3-sonnet
# Groq: LLM_BASE_URL=https://api.groq.com/openai/v1, LLM_MODEL=llama-3.1-70b-versatile

# Logging configuration (loaded via python-dotenv)
# LOG_LEVEL options: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Use DEBUG to see detailed tool calling logs (recommended for troubleshooting)
# Use INFO to see general interaction flow
# Use WARNING or ERROR to suppress most logs
LOG_LEVEL=DEBUG

# Optional: Additional debug flag (not used by the application)
DEBUG=false"""

    # Write to .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with correct logging configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def show_logging_explanation():
    """Show explanation of logging levels and what they display."""
    
    print("\n📋 Logging Configuration Explanation")
    print("=" * 50)
    
    print("\n🔧 Correct .env Configuration:")
    print("LOG_LEVEL=DEBUG    # Shows all logging details")
    print("LOG_LEVEL=INFO     # Shows general flow info")
    print("LOG_LEVEL=WARNING  # Shows only warnings/errors")
    print("LOG_LEVEL=ERROR    # Shows only errors")
    
    print("\n❌ Incorrect Configuration (what you had):")
    print("DEBUG=true         # This variable is not used by the agent")
    print("LOG_LEVEL=INFO     # This would suppress DEBUG level logs")
    
    print("\n📊 What Each Log Level Shows:")
    print("DEBUG level logs include:")
    print("  • 🔧 Tool parameters passed to functions")
    print("  • 🔄 MCP tool conversion details")
    print("  • ⚙️  Tool executor setup")
    print("  • 📝 Response length details")
    print("  • 🔌 MCP server connection details")
    
    print("\nINFO level logs include:")
    print("  • 🔄 Processing user input messages")
    print("  • 🤖 LLM interaction start notifications")
    print("  • 🔧 Tool execution requests and completions")
    print("  • 📋 Interaction summaries (tools used vs direct response)")
    print("  • ✅ Agent initialization status")
    
    print("\n🎯 For debugging tool calling behavior, use LOG_LEVEL=DEBUG")

def test_logging_import():
    """Test that the logging configuration works correctly."""
    
    try:
        # Test dotenv import
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check if LOG_LEVEL is set
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        print(f"✅ Current LOG_LEVEL: {log_level}")
        
        if log_level == 'DEBUG':
            print("✅ DEBUG logging is enabled - you will see detailed tool calling logs")
        elif log_level == 'INFO':
            print("⚠️  INFO logging is enabled - you will see general flow but not detailed tool logs")
        else:
            print(f"⚠️  {log_level} logging is enabled - you may not see tool calling details")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure to run: uv sync")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Main function to run the logging configuration test."""
    
    print("🔍 FastMCP Agent Logging Configuration Test")
    print("=" * 60)
    
    success = True
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("📁 No .env file found, creating one...")
        success &= create_test_env_file()
    else:
        print("📁 Found existing .env file")
    
    # Test configuration
    success &= test_logging_import()
    
    # Show explanation
    show_logging_explanation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Logging configuration test completed!")
        print("\nNext steps:")
        print("1. Update your .env file with a valid LLM_API_KEY")
        print("2. Set LOG_LEVEL=DEBUG in your .env file")
        print("3. Run: uv run fastmcp-agent")
        print("4. Ask a math question to see detailed tool calling logs")
        
        print("\n📋 Expected log output with LOG_LEVEL=DEBUG:")
        print("  🚀 Initializing Calculator Agent...")
        print("  🔧 Connecting to MCP server and retrieving tools...")
        print("  📋 Retrieved 6 tools from MCP server: ['add', 'subtract', ...]")
        print("  🔗 Registering 6 tools with LLM client...")
        print("  ✅ Calculator Agent initialized successfully")
        print("  🔄 Processing user input: 'What is 5 + 3?'")
        print("  🤖 Sending request to LLM with 6 available tools")
        print("  🔧 LLM requested tool execution: add")
        print("  🔧 Tool parameters: {'a': 5, 'b': 3}")
        print("  ✅ Tool add completed, result returned to LLM")
        print("  📋 Interaction completed: LLM used tools to generate response")
        
    else:
        print("❌ Some configuration issues found. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 