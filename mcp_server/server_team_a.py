# Team A MCP Server - Analytics Team
# Tools: Database queries, reporting, audit logs
from fastmcp import FastMCP
from datetime import datetime
from authz_middleware import AuthzMiddleware

from server_common import serve

mcp = FastMCP("Team A - Analytics Server")
mcp.add_middleware(AuthzMiddleware())  # RBAC enforcement on every tool call

@mcp.tool()
def generate_report(report_type: str, format: str = "json") -> dict:
    """Generate an analytics report (analyst role)"""
    return {
        "status": "generated",
        "report_type": report_type,
        "format": format,
        "timestamp": datetime.now().isoformat(),
        "data": {"summary": "Mock analytics report from Team A"},
        "team": "A"
    }

if __name__ == "__main__":
    serve(mcp, service="mcp_team_a", label="Team A (Analytics)", default_port=8001)
