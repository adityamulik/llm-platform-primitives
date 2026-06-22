.PHONY: install run dev test clean clean-pycache help ollama-setup ollama-serve ollama-agent

help:
	@echo "Available targets:"
	@echo "  make install       Install dependencies"
	@echo "  make run           Run web interface on http://localhost:3000"
	@echo "  make dev           Install dependencies and run"
	@echo "  make test          Run tests"
	@echo "  make clean         Clean up temporary files"
	@echo "  make clean-pycache Remove __pycache__ directories"
	@echo ""
	@echo "Ollama targets:"
	@echo "  make ollama-setup  Pull and setup Llama 3.1 model"
	@echo "  make ollama-serve  Start Ollama server"
	@echo "  make ollama-agent  Run the agent (requires Ollama running)"

install:
	uv sync

clean-pycache:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

run: clean-pycache
	uv run adk web

run-mcp: 
	uv run python mcp_server/analytics_mcp.py

dev: install run

test:
	uv run pytest tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .venv -exec rm -rf {} +
	rm -rf dist/ build/ *.egg-info/

ollama-setup:
	@echo "Setting up Ollama with Llama 3.1 model..."
	ollama pull llama3.1
	@echo "✓ Ollama setup complete. Run 'make ollama-serve' to start the server."

ollama-serve:
	@echo "Starting Ollama server on http://localhost:11434..."
	ollama serve

ollama-agent:
	@echo "Running agent with Ollama (ensure 'make ollama-serve' is running in another terminal)"
	uv run adk run app
