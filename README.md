# FastMCP Calculator Agent

A simple end-to-end agent application built with Python that integrates [FastMCP](https://gofastmcp.com/getting-started/welcome) to perform calculator tasks using any OpenAI-compatible LLM provider.

## Features

- 🧮 **Calculator Tools**: Basic arithmetic operations (add, subtract, multiply, divide, power, sqrt)
- 🤖 **Multi-LLM Support**: Works with any OpenAI-compatible API (OpenAI, Qwen, Claude, Groq, etc.)
- 🌊 **Streaming Output**: Real-time streaming responses from the LLM
- 🧠 **Thinking Mode**: Optional display of the model's reasoning process
- ⚡ **FastMCP**: High-performance MCP server and client implementation
- 📦 **UV Package Manager**: Modern Python package management

## Prerequisites

- Python 3.10+
- UV package manager
- API key for your chosen LLM provider

## Supported LLM Providers

This agent works with any OpenAI-compatible API, including:

- **OpenAI**: GPT-4, GPT-3.5-turbo, etc.
- **Qwen**: qwen-turbo, qwen-plus, etc.
- **Claude**: claude-3-sonnet, claude-3-haiku, etc.
- **Groq**: llama-3.1-70b-versatile, mixtral-8x7b, etc.
- **Anthropic**: Any Claude model via compatible proxy
- **Local models**: via OpenAI-compatible servers (Ollama, vLLM, etc.)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp-boilerplate
```

2. Install dependencies using UV:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your LLM provider credentials
```

## Configuration

Create a `.env` file with your LLM provider credentials:

### OpenAI Example
```env
LLM_API_KEY=sk-your_openai_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

### Qwen Example
```env
LLM_API_KEY=your_qwen_api_key_here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo
```

### Groq Example
```env
LLM_API_KEY=your_groq_api_key_here
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-70b-versatile
```

## Usage

### Run the Calculator Agent

```bash
# Using UV
uv run calculator-agent

# Or activate virtual environment and run directly
uv shell
python -m calculator_agent.main
```

### Command Line Options

```bash
calculator-agent --help
```

Options:
- `--show-thinking`: Enable display of model's thinking process
- `--no-stream`: Disable streaming output
- `--verbose`: Enable verbose logging

### Example Usage

```bash
# Basic usage
calculator-agent

# With thinking mode enabled
calculator-agent --show-thinking

# With verbose output
calculator-agent --verbose --show-thinking
```

## How It Works

1. **FastMCP Server**: Provides calculator tools (add, subtract, multiply, divide, power, sqrt)
2. **Agent Client**: Connects to the MCP server and your chosen LLM
3. **Interactive Loop**: Users can ask mathematical questions
4. **Tool Execution**: The LLM uses calculator tools to solve problems
5. **Streaming Response**: Results are streamed back to the user

## Example Conversation

```
User: What is 15 * 23 + 7?

🤖 Assistant: I'll help you calculate 15 * 23 + 7. Let me break this down step by step:

First, I'll multiply 15 by 23:
[Tool: multiply(15, 23) = 345]

Now I'll add 7 to that result:
[Tool: add(345, 7) = 352]

Therefore, 15 * 23 + 7 = 352
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │   LLM Provider  │
│  User Interface │◄──►│ Calculator Agent│◄──►│ (OpenAI-compat  │
│   (Rich CLI)    │    │  (Orchestrator) │    │    API)         │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │                 │
                       │  FastMCP Server │
                       │ (Calculator     │
                       │     Tools)      │
                       │                 │
                       └─────────────────┘
```

### Components

- **FastMCP Server** (`mcp_server.py`): Provides calculator tools using FastMCP framework
- **LLM Client** (`llm_client.py`): Handles communication with any OpenAI-compatible LLM API
- **Agent Orchestrator** (`agent.py`): Coordinates between MCP server and LLM
- **CLI Interface** (`main.py`): Command-line interface with Rich formatting

## Available Calculator Tools

| Tool | Description | Parameters | Example |
|------|-------------|------------|---------|
| `add` | Add two numbers | `a`, `b` | `add(5, 3) → 8` |
| `subtract` | Subtract second from first | `a`, `b` | `subtract(10, 4) → 6` |
| `multiply` | Multiply two numbers | `a`, `b` | `multiply(6, 7) → 42` |
| `divide` | Divide first by second | `a`, `b` | `divide(15, 3) → 5` |
| `power` | Raise first to power of second | `a`, `b` | `power(2, 8) → 256` |
| `sqrt` | Calculate square root | `a` | `sqrt(16) → 4` |

## Development

### Install Development Dependencies

```bash
uv sync --extra dev
```

### Run Tests

```bash
uv run python test_setup.py
```

### Quick Demo

```bash
uv run python demo.py
```

### Project Structure

```
calculator_agent/
├── __init__.py          # Package initialization
├── main.py              # CLI entry point
├── agent.py             # Main agent orchestrator
├── mcp_server.py        # FastMCP server with tools
├── llm_client.py        # Generic LLM client
└── tests/               # Test suite
    ├── __init__.py
    ├── test_agent.py
    ├── test_mcp_server.py
    └── test_llm_client.py
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'fastmcp'**
   - Make sure dependencies are installed: `uv sync`

2. **Authentication Error with LLM**
   - Check your API key in `.env` file
   - Verify API key has proper permissions

3. **Connection Timeout**
   - Check internet connection
   - Verify LLM service is accessible

### Debug Mode

Run with verbose logging to see detailed information:

```bash
calculator-agent --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `uv run pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

- [FastMCP Documentation](https://gofastmcp.com/getting-started/welcome)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [UV Package Manager](https://github.com/astral-sh/uv)