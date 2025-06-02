# FastMCP Calculator Agent - Usage Guide

## Quick Start

### 1. Verify Setup

First, make sure everything is installed correctly:

```bash
uv run python test_setup.py
```

You should see all green checkmarks indicating the setup is working.

### 2. Try the Demo

Test the application functionality with the demo:

```bash
uv run python demo.py
```

Demo features:

- Shows how the agent interface works
- Demonstrates streaming responses
- Real calculator tool usage via FastMCP
- Uses your configured LLM provider

### 3. Setup Your LLM Provider

#### Create Environment File

1. Create a `.env` file from the example:

```bash
cp env.example .env
```

2. Configure for your chosen LLM provider:

**OpenAI Example:**

```env
LLM_API_KEY=sk-your-openai-api-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

**Qwen Example:**

```env
LLM_API_KEY=sk-your-qwen-api-key-here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo
```

#### Run the Agent

```bash
# Basic usage
uv run calculator-agent

# With thinking mode (shows LLM reasoning)
uv run calculator-agent --show-thinking

# Without streaming (for debugging)
uv run calculator-agent --no-stream

# Verbose logging
uv run calculator-agent --verbose --show-thinking
```

## Supported LLM Providers

This agent works with any OpenAI-compatible API:

- **OpenAI**: GPT-4, GPT-3.5-turbo, etc.
- **Qwen**: qwen-turbo, qwen-plus, etc.
- **Claude**: claude-3-sonnet, claude-3-haiku, etc.
- **Groq**: llama-3.1-70b-versatile, mixtral-8x7b, etc.
- **Anthropic**: Any Claude model via compatible proxy
- **Local models**: via OpenAI-compatible servers (Ollama, vLLM, etc.)

## Example Conversations

### Basic Math

```
You: What is 15 × 23 + 7?

🤖 Assistant: I'll help you calculate 15 × 23 + 7. Let me break this down:

First, I'll multiply 15 by 23:
[Using multiply tool: 15 × 23 = 345]

Then I'll add 7:
[Using add tool: 345 + 7 = 352]

Therefore, 15 × 23 + 7 = 352
```

### Complex Calculations

```
You: What's the square root of 144 plus 5 to the power of 3?

🤖 Assistant: I'll calculate √144 + 5³ step by step:

First, the square root of 144:
[Using sqrt tool: √144 = 12]

Next, 5 to the power of 3:
[Using power tool: 5³ = 125]

Finally, adding them together:
[Using add tool: 12 + 125 = 137]

So √144 + 5³ = 137
```

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--show-thinking` | Display model's reasoning process | `calculator-agent --show-thinking` |
| `--no-stream` | Disable streaming output | `calculator-agent --no-stream` |
| `--verbose`, `-v` | Enable detailed logging | `calculator-agent -v` |
| `--version` | Show version information | `calculator-agent --version` |
| `--help` | Show help message | `calculator-agent --help` |

## Available Calculator Tools

The agent has access to these mathematical operations:

- **add(a, b)** - Addition
- **subtract(a, b)** - Subtraction  
- **multiply(a, b)** - Multiplication
- **divide(a, b)** - Division (handles divide by zero)
- **power(a, b)** - Exponentiation (a^b)
- **sqrt(a)** - Square root (handles negative numbers)

## Troubleshooting

### Common Issues

1. **"Missing required environment variable: LLM_API_KEY"**
   - Make sure you've created a `.env` file with your API key
   - Check that the API key is valid for your provider

2. **Connection timeout or HTTP errors**
   - Verify your internet connection
   - Check if your LLM service is accessible
   - Verify the base URL is correct for your provider
   - Try again in a few moments

3. **Import errors**
   - Run `uv sync` to reinstall dependencies
   - Make sure you're using Python 3.10+

### Debug Mode

For detailed debugging information:

```bash
calculator-agent --verbose --show-thinking
```

This will show:

- HTTP request/response details
- Tool execution logs
- Model thinking process
- Error stack traces

### Testing

Use the demo mode to test functionality:

```bash
# Interactive demo with your LLM
uv run python demo.py

# Setup verification
uv run python test_setup.py
```

## Architecture Overview

```
User Input → Calculator Agent → LLM Provider → Tool Calls → Calculator Tools → Results → User
              ↑                                              ↓
         FastMCP Client ←─────── FastMCP Server ←─────────────┘
```

1. **User asks a math question**
2. **Agent sends to LLM** with available tools
3. **LLM decides which tools to use** and calls them
4. **FastMCP server executes** calculator functions
5. **Results flow back** through the chain
6. **Agent displays** the final answer with streaming

## Next Steps

- Extend with more mathematical functions (trigonometry, logarithms)
- Add support for additional specialized LLM providers
- Implement conversation memory and context
- Add visualization for complex calculations
- Create web interface using FastAPI integration
