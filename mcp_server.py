#!/usr/bin/env python3
"""
Nautobot MCP Server with modular query system

This version uses a modular architecture with separate modules for:
- Cache management (cache/)
- ID resolvers (resolvers/)
- Request handlers (handlers/)
- Tool registry (tools/)
"""

import asyncio
import json
import logging
from typing import List

from mcp.server import Server
from mcp.types import TextContent

from nautobot_client import NautobotClient
from queries import get_query
from cache import IDCache
from handlers import HelpHandler, RestFallbackHandler, OnboardHandler
from tools import ToolRegistry

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize server and components
app = Server("nautobot-mcp")
id_cache = IDCache()

try:
    client = NautobotClient()
    logger.info("Nautobot client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Nautobot client: {str(e)}")
    client = None

# Initialize handlers
help_handler = HelpHandler()
rest_fallback_handler = RestFallbackHandler(client) if client else None
onboard_handler = OnboardHandler(id_cache, client) if client else None


@app.list_tools()
async def list_tools():
    """List all available MCP tools"""
    return ToolRegistry.get_all_tools()


@app.list_resources()
async def list_resources() -> list:
    """List available resources (none for this server)"""
    return []


@app.list_prompts()
async def list_prompts():
    """List available prompt templates"""
    return ToolRegistry.get_all_prompts()


@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> str:
    """Generate prompt content based on template and arguments"""
    return ToolRegistry.generate_prompt_content(name, arguments)


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Execute MCP tool calls using handlers and query registry"""
    if not client:
        error_msg = "Nautobot client not initialized. Check connection settings."
        logger.error(error_msg)
        return [TextContent(type="text", text=f"Error: {error_msg}")]

    try:
        logger.info(f"Executing tool: {name} with arguments: {arguments}")

        # Handle special tools with dedicated handlers
        if name == "help_find_query":
            return await help_handler.handle(arguments)

        if name == "query_rest_api_fallback" and rest_fallback_handler:
            return await rest_fallback_handler.handle(arguments)
            
        if name == "onboard_device" and onboard_handler:
            return await onboard_handler.handle(arguments)

        # Handle standard query tools
        query = get_query(name)

        # Validate arguments
        query.validate_arguments(arguments)

        # Execute query
        result = query.execute(client, arguments)

        # Handle GraphQL errors
        if hasattr(result, "get") and result.get("errors"):
            error_msg = f"GraphQL errors: {result['errors']}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

        # Return successful result with special handling for customized queries
        if name == "get_device_details":
            return _format_device_details_response(result)
        elif name == "get_ip_addresses":
            return _format_ip_addresses_response(result)

        # Standard handling for other queries
        if query.query_type.value == "graphql" and "data" in result:
            response_data = result["data"]
        else:
            response_data = result

        return [TextContent(type="text", text=json.dumps(response_data, indent=2))]

    except ValueError as e:
        # Query not found or validation error
        error_msg = str(e)
        logger.error(error_msg)
        return [TextContent(type="text", text=f"Error: {error_msg}")]

    except Exception as e:
        # General execution error
        error_msg = f"Tool execution failed: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=f"Error: {error_msg}")]


def _format_device_details_response(result) -> List[TextContent]:
    """Format device details query response"""
    if "devices" in result:
        devices = result["devices"]
        if devices:
            summary_lines = [f"Found {len(devices)} device(s):"]
            for device in devices:
                device_info = [
                    device.get("hostname", device.get("name", "Unknown"))
                ]
                if "status" in device:
                    device_info.append(f"Status: {device['status']['name']}")
                if "role" in device:
                    device_info.append(f"Role: {device['role']['name']}")
                if "interfaces" in device:
                    device_info.append(
                        f"Interfaces: {len(device['interfaces'])}"
                    )
                summary_lines.append(" - " + " | ".join(device_info))

            return [TextContent(type="text", text="\n".join(summary_lines))]
        else:
            return [
                TextContent(
                    type="text", text="No devices found matching the criteria."
                )
            ]
    elif "error" in result:
        return [TextContent(type="text", text=f"Error: {result['error']}")]


def _format_ip_addresses_response(result) -> List[TextContent]:
    """Format IP addresses query response"""
    if "ip_addresses" in result:
        ip_addresses = result["ip_addresses"]
        if ip_addresses:
            summary_lines = [f"Found {len(ip_addresses)} IP address(es):"]
            for ip_addr in ip_addresses:
                ip_info = [ip_addr.get("address", "Unknown")]
                if "dns_name" in ip_addr and ip_addr["dns_name"]:
                    ip_info.append(f"DNS: {ip_addr['dns_name']}")
                if "type" in ip_addr and ip_addr["type"]:
                    ip_info.append(f"Type: {ip_addr['type']}")
                if "status" in ip_addr:
                    ip_info.append(f"Status: {ip_addr['status']['name']}")
                if "interfaces" in ip_addr and ip_addr["interfaces"]:
                    interfaces_info = [
                        f"{iface['name']} ({iface['device']['name']})"
                        for iface in ip_addr["interfaces"]
                    ]
                    ip_info.append(f"Interfaces: {', '.join(interfaces_info)}")
                if "primary_ip4_for" in ip_addr and ip_addr["primary_ip4_for"]:
                    devices_info = [
                        device.get("hostname", device.get("name", "Unknown"))
                        for device in ip_addr["primary_ip4_for"]
                    ]
                    ip_info.append(f"Primary IP for: {', '.join(devices_info)}")
                summary_lines.append(" - " + " | ".join(ip_info))

            return [TextContent(type="text", text="\n".join(summary_lines))]
        else:
            return [
                TextContent(
                    type="text",
                    text="No IP addresses found matching the criteria.",
                )
            ]
    elif "error" in result:
        return [TextContent(type="text", text=f"Error: {result['error']}")]


async def main():
    """Main entry point for the MCP server"""
    logger.info("Starting Nautobot MCP server (refactored modular version)...")

    # Display cache statistics
    logger.info(f"ID cache initialized with TTL: {id_cache.ttl}s")

    # Display registered tools
    try:
        tools = ToolRegistry.get_all_tools()
        logger.info(f"Loaded {len(tools)} tools total")
    except Exception as e:
        logger.error(f"Failed to load tools: {str(e)}")

    # Test connection if client is available
    if client and not client.test_connection():
        logger.warning("Failed to connect to Nautobot, but continuing to serve...")

    # Start MCP server
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())