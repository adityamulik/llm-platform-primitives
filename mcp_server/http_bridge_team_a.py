#!/usr/bin/env python3
"""HTTP Bridge for Team A (Analytics) MCP Server"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys, os

from server_team_a import generate_report

app = Flask(__name__)
CORS(app)

TOOLS = {
    'generate_report': generate_report
}

@app.route('/health', methods=['GET'], strict_slashes=False)
def health():
    return jsonify({
        "status": "ok",
        "service": "Team A - Analytics HTTP Bridge",
        "team": "A",
        "tools": list(TOOLS.keys())
    })

@app.route('/tools/<tool>', methods=['POST'], strict_slashes=False)
def execute_tool(tool):
    try:
        data = request.get_json() or {}
        arguments = data.get('arguments', {})
        
        if tool not in TOOLS:
            return jsonify({
                "error": f"Tool '{tool}' not found in Team A",
                "available_tools": list(TOOLS.keys()),
                "team": "A"
            }), 404
        
        print(f"🔧 Team A: Executing tool '{tool}' with args: {arguments}")
        result = TOOLS[tool](**arguments)
        return jsonify(result)
        
    except TypeError as e:
        error_msg = str(e)
        return jsonify({
            "error": f"Invalid arguments for tool '{tool}'",
            "details": error_msg,
            "hint": f"Check required parameters for {tool}",
            "available_tools": list(TOOLS.keys()),
            "team": "A"
        }), 400
    except Exception as e:
        print(f"❌ Team A Error: {str(e)}", file=sys.stderr)
        return jsonify({"error": str(e), "team": "A"}), 500

@app.route('/api/tools/<tool>', methods=['POST'], strict_slashes=False)
def api_execute_tool(tool):
    try:
        data = request.get_json() or {}
        arguments = data.get('params', {}).get('arguments', data.get('arguments', {}))
        request_id = data.get('id', 1)
        
        if tool not in TOOLS:
            return jsonify({
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Tool '{tool}' not found in Team A"},
                "id": request_id
            }), 404
        
        print(f"🔧 Team A API: Executing tool '{tool}'")
        result = TOOLS[tool](**arguments)
        
        return jsonify({
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        })
        
    except Exception as e:
        print(f"❌ Team A API Error: {str(e)}", file=sys.stderr)
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
            "team": "A",
            "tools": [{"name": name, "description": func.__doc__} for name, func in TOOLS.items()],
            "count": len(TOOLS)
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('MCP_PORT', 8001))
    host = os.getenv('MCP_HOST', '0.0.0.0')
    print(f"🚀 Team A (Analytics) HTTP Bridge starting on {host}:{port}")
    print(f"📋 Tools: {', '.join(TOOLS.keys())}")
    app.run(host=host, port=port, debug=False)
