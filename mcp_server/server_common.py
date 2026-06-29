"""Shared startup for the team MCP servers, which differ only by their tools."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def serve(mcp, *, service: str, label: str, default_port: int) -> None:
    """Configure file logging and run an MCP server over HTTP.

    Centralizes the identical boot block each team server used to repeat: the
    repo-root path fix (so ``python mcp_server/server_team_x.py`` can import the
    ``observability`` package), per-service logging, and the HTTP run. ``port``
    is overridable via the ``MCP_PORT`` env var.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from observability.logging import setup_logging

    log_file = setup_logging(service)
    port = int(os.getenv("MCP_PORT", default_port))
    print(f"📝 Logging to {log_file}")
    print(f"🚀 {label} MCP Server starting on http://0.0.0.0:{port}/mcp")
    mcp.run(transport="http", host="0.0.0.0", port=port)
