#!/bin/bash
# MCP Server wrapper script for Claude Desktop

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Set up environment
export PATH="$HOME/.pyenv/shims:$PATH"

# Load .env file if it exists
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Run the MCP server
exec python mcp_server.py