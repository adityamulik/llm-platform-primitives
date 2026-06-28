.PHONY: install run run-all dev test clean clean-pycache help ollama-setup ollama-serve ollama-agent mcp-team-a mcp-team-b mcp-team-c mcp-servers auth-server

help:
	@echo "Available targets:"
	@echo "  make install       Install dependencies"
	@echo "  make run           Run ADK only on http://localhost:3000"
	@echo "  make run-all       Run ADK + all 3 MCP servers (recommended)"
	@echo "  make dev           Install dependencies and run"
	@echo "  make test          Run tests"
	@echo "  make clean         Clean up temporary files"
	@echo "  make clean-pycache Remove __pycache__ directories"
	@echo ""
	@echo "Ollama targets:"
	@echo "  make ollama-setup  Pull and setup Llama 3.1 model"
	@echo "  make ollama-serve  Start Ollama server"
	@echo "  make ollama-agent  Run the agent (requires Ollama running)"
	@echo ""
	@echo "MCP server targets (run each in its own terminal):"
	@echo "  make mcp-team-a    Start Team A (Analytics) on :8001"
	@echo "  make mcp-team-b    Start Team B (DevOps) on :8002"
	@echo "  make mcp-team-c    Start Team C (Developer) on :8003"
	@echo "  make mcp-servers   Start all three team servers in the background"
	@echo ""
	@echo "Auth/AuthZ:"
	@echo "  make auth-server   Start the login/token (auth) server on :8000"

install:
	uv sync

clean-pycache:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

run: clean-pycache
	uv run adk web

run-all: clean-pycache
	@echo "Starting MCP servers..."
	uv run python mcp_server/server_team_a.py > /tmp/team_a.log 2>&1 &
	uv run python mcp_server/server_team_b.py > /tmp/team_b.log 2>&1 &
	uv run python mcp_server/server_team_c.py > /tmp/team_c.log 2>&1 &
	@echo "✓ MCP servers started in background"
	@echo "  Team A logs: tail -f /tmp/team_a.log"
	@echo "  Team B logs: tail -f /tmp/team_b.log"
	@echo "  Team C logs: tail -f /tmp/team_c.log"
	@sleep 2
	@echo ""
	@echo "Starting ADK on http://localhost:3000..."
	uv run adk web

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

mcp-team-a:
	uv run python mcp_server/server_team_a.py

mcp-team-b:
	uv run python mcp_server/server_team_b.py

mcp-team-c:
	uv run python mcp_server/server_team_c.py

auth-server:
	uv run python mcp_auth/auth_server.py

mcp-servers:
	@echo "Starting all team MCP servers in the background..."
	uv run python mcp_server/server_team_a.py & \
	uv run python mcp_server/server_team_b.py & \
	uv run python mcp_server/server_team_c.py & \
	wait
