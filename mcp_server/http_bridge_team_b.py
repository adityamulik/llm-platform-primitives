#!/usr/bin/env python3
"""HTTP Bridge for Team B (DevOps) MCP Server"""
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sys, os
from pathlib import Path

# Make the repo-root `mcp_auth` package importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server_team_b import (
    deploy_application, restart_service, update_configuration
)
from gateway.authz import require_tool_access

app = Flask(__name__)
CORS(app)

TOOLS = {
    'deploy_application': deploy_application,
    'restart_service': restart_service,
    'update_configuration': update_configuration
}

@app.route('/health', methods=['GET'], strict_slashes=False)
def health():
    return jsonify({
        "status": "ok",
        "service": "Team B - DevOps HTTP Bridge",
        "team": "B",
        "tools": list(TOOLS.keys())
    })

@app.route('/tools/<tool>', methods=['POST'], strict_slashes=False)
@require_tool_access
def execute_tool(tool):
    try:
        data = request.get_json() or {}
        arguments = data.get('arguments', {})
        
        if tool not in TOOLS:
            return jsonify({
                "error": f"Tool '{tool}' not found in Team B",
                "available_tools": list(TOOLS.keys()),
                "team": "B"
            }), 404
        
        caller = g.claims.get("sub")
        role = g.claims.get("role")
        print(f"🔧 Team B: {caller} ({role}) executing tool '{tool}' with args: {arguments}")
        result = TOOLS[tool](**arguments)
        return jsonify(result)
        
    except TypeError as e:
        error_msg = str(e)
        return jsonify({
            "error": f"Invalid arguments for tool '{tool}'",
            "details": error_msg,
            "hint": f"Check required parameters for {tool}",
            "available_tools": list(TOOLS.keys()),
            "team": "B"
        }), 400
    except Exception as e:
        print(f"❌ Team B Error: {str(e)}", file=sys.stderr)
        return jsonify({"error": str(e), "team": "B"}), 500

@app.route('/api/tools/<tool>', methods=['POST'], strict_slashes=False)
@require_tool_access
def api_execute_tool(tool):
    try:
        data = request.get_json() or {}
        arguments = data.get('params', {}).get('arguments', data.get('arguments', {}))
        request_id = data.get('id', 1)
        
        if tool not in TOOLS:
            return jsonify({
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Tool '{tool}' not found in Team B"},
                "id": request_id
            }), 404
        
        print(f"🔧 Team B API: Executing tool '{tool}'")
        result = TOOLS[tool](**arguments)
        
        return jsonify({
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        })
        
    except Exception as e:
        print(f"❌ Team B API Error: {str(e)}", file=sys.stderr)
        return jsonify({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": data.get('id', 1)
        }), 500

@app.route('/api/tools', methods=['GET'], strict_slashes=False)
def list_tools():
    return jsonify({
        "jsonrpc": "2.0",
        "result": {
            "team": "B",
            "tools": [{"name": name, "description": func.__doc__} for name, func in TOOLS.items()],
            "count": len(TOOLS)
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('MCP_PORT', 8002))
    host = os.getenv('MCP_HOST', '0.0.0.0')
    print(f"🚀 Team B (DevOps) HTTP Bridge starting on {host}:{port}")
    print(f"📋 Tools: {', '.join(TOOLS.keys())}")
    app.run(host=host, port=port, debug=False)
