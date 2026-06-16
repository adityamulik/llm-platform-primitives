# LLM Platform Primitives

A learning repository exploring platform engineering patterns for LLM applications.

## Focus Areas

- **Intent Validation** - Validate user intents before processing
- **LLM Observability** - Monitor and trace LLM operations
- **Prompt Versioning** - Manage prompt versions and variants
- **Auth & AuthZ** - Authentication and authorization patterns

## Getting Started

Install dependencies and run the web interface:
```bash
make dev
```

The agent will be available at `http://localhost:8000` (or the port shown in the terminal).

See `make help` for all available commands.

## Agent Prototyping

We use [Google Agent Development Kit (python-adk)](https://adk.dev/get-started/python/) for rapid agent prototyping and testing.

## Local Model Execution with Ollama

This project uses [Ollama](https://ollama.ai/) to run local LLM models locally with the `llama3.1` model.

Quick start:
```bash
make ollama-setup   # One-time setup to pull the model
make ollama-serve   # Start Ollama server (terminal 1)
make ollama-agent   # Run the agent (terminal 2)
```

See `make help` for more Ollama-related commands.

## License

MIT