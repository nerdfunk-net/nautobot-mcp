#!/usr/bin/env python3
"""
Mock MCP Server for testing Claude Desktop hanging issues
Returns static data without touching Nautobot
"""

import asyncio
import json
import logging
from typing import List

from mcp.server import Server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Server("nautobot-mock")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List mock tools"""
    return [
        Tool(
            name="mock_hello",
            description="Simple hello world test",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="mock_device",
            description="Mock device info",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Device name"}
                },
                "required": ["name"]
            }
        )
    ]

@app.list_resources()
async def list_resources() -> list:
    return []

@app.list_prompts()
async def list_prompts() -> list:
    return []

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Execute mock tool calls"""
    logger.info(f"Mock tool called: {name} with {arguments}")
    
    if name == "mock_hello":
        return [TextContent(type="text", text="OK")]
    
    elif name == "mock_device":
        device_name = arguments.get("name", "unknown")
        return [TextContent(
            type="text", 
            text=f"Mock device: {device_name} | Status: Active | Type: Virtual"
        )]
    
    else:
        return [TextContent(type="text", text=f"Unknown mock tool: {name}")]

async def main():
    """Main entry point"""
    logger.info("Starting mock MCP server...")
    
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, 
            write_stream, 
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())