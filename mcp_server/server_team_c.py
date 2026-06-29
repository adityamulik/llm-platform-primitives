# Team C MCP Server - Developer Team
# Tools: File operations, code management, user/permission management
from fastmcp import FastMCP
from authz_middleware import AuthzMiddleware

from server_common import serve

mcp = FastMCP("Team C - Developer Server")
mcp.add_middleware(AuthzMiddleware())  # RBAC enforcement on every tool call

@mcp.tool()
def read_file(path: str) -> dict:
    """Read a file (developer role)"""
    return {
        "status": "success",
        "path": path,
        "content": f"Mock file content from {path}",
        "size": 1024,
        "team": "C"
    }

@mcp.tool()
def query_database(query: str, database: str = "default") -> dict:
    """Execute a database query (developer role)"""
    if "DELETE" in query.upper():
        affected = 10234 if "users" in query.lower() else 5
        return {
            "status": "executed",
            "affected_rows": affected,
            "query": query,
            "database": database,
            "team": "C"
        }
    return {
        "status": "executed",
        "result": "Mock query results from Team C",
        "rows": 42,
        "query": query,
        "database": database,
        "team": "C"
    }

if __name__ == "__main__":
    serve(mcp, service="mcp_team_c", label="Team C (Developer)", default_port=8003)
