#!/usr/bin/env python3
"""HTTP Bridge for Team C (Developer) MCP Server"""
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sys, os
from pathlib import Path

# Make the repo-root `mcp_auth` package importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server_team_c import read_file, query_database
from gateway.authz import require_tool_access

app = Flask(__name__)
CORS(app)

TOOLS = {
    'read_file': read_file,
    'query_database': query_database
}

@app.route('/health', methods=['GET'], strict_slashes=False)
def health():
    return jsonify({
        "status": "ok",
        "service": "Team C - Developer HTTP Bridge",
        "team": "C",
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
                "error": f"Tool '{tool}' not found in Team C",
                "available_tools": list(TOOLS.keys()),
                "team": "C"
            }), 404
        
        caller = g.claims.get("sub")
        role = g.claims.get("role")
        print(f"🔧 Team C: {caller} ({role}) executing tool '{tool}' with args: {arguments}")
        result = TOOLS[tool](**arguments)
        return jsonify(result)
        
    except TypeError as e:
        error_msg = str(e)
        return jsonify({
            "error": f"Invalid arguments for tool '{tool}'",
            "details": error_msg,
            "hint": f"Check required parameters for {tool}",
            "available_tools": list(TOOLS.keys()),
            "team": "C"
        }), 400
    except Exception as e:
        print(f"❌ Team C Error: {str(e)}", file=sys.stderr)
        return jsonify({"error": str(e), "team": "C"}), 500

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
                "error": {"code": -32601, "message": f"Tool '{tool}' not found in Team C"},
                "id": request_id
            }), 404
        
        print(f"🔧 Team C API: Executing tool '{tool}'")
        result = TOOLS[tool](**arguments)
        
        return jsonify({
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        })
        
    except Exception as e:
        print(f"❌ Team C API Error: {str(e)}", file=sys.stderr)
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
            "team": "C",
            "tools": [{"name": name, "description": func.__doc__} for name, func in TOOLS.items()],
            "count": len(TOOLS)
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('MCP_PORT', 8003))
    host = os.getenv('MCP_HOST', '0.0.0.0')
    print(f"🚀 Team C (Developer) HTTP Bridge starting on {host}:{port}")
    print(f"📋 Tools: {', '.join(TOOLS.keys())}")
    app.run(host=host, port=port, debug=False)
