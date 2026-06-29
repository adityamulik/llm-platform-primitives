.PHONY: install run run-all kill-all dev test clean clean-pycache help ollama-setup ollama-serve ollama-agent mcp-team-a mcp-team-b mcp-team-c mcp-servers gateway main

# Ports (override on the command line, e.g. `make run-all MAIN_PORT=8080`)
# Defaults match the "Services & ports" table in the README.
# NOTE: avoid 7000 — macOS AirPlay Receiver (Control Center) binds it and
# returns 403 to everything else.
GATEWAY_PORT ?= 7010
MAIN_PORT ?= 7020
MCP_A_PORT ?= 8001
MCP_B_PORT ?= 8002
MCP_C_PORT ?= 8003

help:
	@echo "Available targets:"
	@echo "  make install       Install dependencies"
	@echo "  make run           Run ADK only on http://localhost:3000"
	@echo "  make run-all       Run gateway + main API + all 3 MCP servers in the background (recommended)"
	@echo "  make kill-all      Stop everything started by run-all"
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
	@echo "  make gateway       Start the auth gateway (token issuer) on :$(GATEWAY_PORT)"
	@echo "  make main          Start the main API on :$(MAIN_PORT)"

install:
	uv sync

clean-pycache:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

run: clean-pycache
	uv run adk web

run-all: clean-pycache
	@mkdir -p logs
	@echo "Starting MCP servers (Team A :$(MCP_A_PORT), Team B :$(MCP_B_PORT), Team C :$(MCP_C_PORT))..."
	@MCP_PORT=$(MCP_A_PORT) uv run python mcp_server/server_team_a.py > logs/mcp_team_a.out 2>&1 & echo $$! > /tmp/team_a.pid
	@MCP_PORT=$(MCP_B_PORT) uv run python mcp_server/server_team_b.py > logs/mcp_team_b.out 2>&1 & echo $$! > /tmp/team_b.pid
	@MCP_PORT=$(MCP_C_PORT) uv run python mcp_server/server_team_c.py > logs/mcp_team_c.out 2>&1 & echo $$! > /tmp/team_c.pid
	@echo "✓ MCP servers started in background"
	@echo "  Team A logs: tail -f logs/mcp_team_a.log"
	@echo "  Team B logs: tail -f logs/mcp_team_b.log"
	@echo "  Team C logs: tail -f logs/mcp_team_c.log"
	@echo "Starting auth gateway on http://localhost:$(GATEWAY_PORT)..."
	@AUTH_PORT=$(GATEWAY_PORT) uv run python gateway/gateway_server.py > logs/gateway.out 2>&1 & echo $$! > /tmp/gateway.pid
	@echo "✓ Gateway started in background (logs: tail -f logs/gateway.log)"
	@sleep 2
	@echo "Starting main API on http://localhost:$(MAIN_PORT)..."
	@GATEWAY_URL=http://localhost:$(GATEWAY_PORT) uv run uvicorn main:app --host 127.0.0.1 --port $(MAIN_PORT) > logs/demo.out 2>&1 & echo $$! > /tmp/main.pid
	@echo "✓ Main API started in background (logs: tail -f logs/demo.log)"
	@echo ""
	@echo "All services are running in the background."
	@echo "  Stop everything with: make kill-all"

kill-all:
	@echo "Stopping all services..."
	@for port in $(GATEWAY_PORT) $(MAIN_PORT) $(MCP_A_PORT) $(MCP_B_PORT) $(MCP_C_PORT); do \
		pids=$$(lsof -ti tcp:$$port 2>/dev/null); \
		if [ -n "$$pids" ]; then \
			echo "  Killing port $$port (PID $$pids)"; \
			kill $$pids 2>/dev/null || true; \
		fi; \
	done
	@rm -f /tmp/team_a.pid /tmp/team_b.pid /tmp/team_c.pid /tmp/gateway.pid /tmp/main.pid
	@echo "✓ All services stopped"

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
	MCP_PORT=$(MCP_A_PORT) uv run python mcp_server/server_team_a.py

mcp-team-b:
	MCP_PORT=$(MCP_B_PORT) uv run python mcp_server/server_team_b.py

mcp-team-c:
	MCP_PORT=$(MCP_C_PORT) uv run python mcp_server/server_team_c.py

gateway:
	AUTH_PORT=$(GATEWAY_PORT) uv run python gateway/gateway_server.py

main:
	GATEWAY_URL=http://localhost:$(GATEWAY_PORT) uv run uvicorn main:app --host 127.0.0.1 --port $(MAIN_PORT)

mcp-servers:
	@echo "Starting all team MCP servers in the background..."
	MCP_PORT=$(MCP_A_PORT) uv run python mcp_server/server_team_a.py & \
	MCP_PORT=$(MCP_B_PORT) uv run python mcp_server/server_team_b.py & \
	MCP_PORT=$(MCP_C_PORT) uv run python mcp_server/server_team_c.py & \
	wait
