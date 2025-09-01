#!/usr/bin/env python3
"""
Nautobot MCP Server with modular query system

This version uses a modular query registry system that makes it easy to add new queries
without modifying the core server code.
"""

import asyncio
import json
import logging
from typing import List

from mcp.server import Server
from mcp.types import Tool, TextContent, Prompt, PromptArgument

from nautobot_client import NautobotClient
from queries import get_all_queries, get_query

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize server and client
app = Server("nautobot-mcp")

try:
    client = NautobotClient()
    logger.info("Nautobot client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Nautobot client: {str(e)}")
    client = None

@app.list_tools()
async def list_tools() -> List[Tool]:
    """Dynamically generate MCP tools from query registry"""
    tools = []
    
    try:
        queries = get_all_queries()
        logger.info(f"Found {len(queries)} registered queries")
        
        for query in queries.values():
            # Convert query schema to MCP Tool schema
            tool = Tool(
                name=query.tool_name,
                description=query.description,
                inputSchema={
                    "type": query.schema.type,
                    "properties": query.schema.properties,
                    "required": query.schema.required
                }
            )
            tools.append(tool)
            logger.debug(f"Registered tool: {query.tool_name}")
        
        return tools
        
    except Exception as e:
        logger.error(f"Failed to list tools: {str(e)}")
        return []

@app.list_resources()
async def list_resources() -> list:
    """List available resources (none for this server)"""
    return []

@app.list_prompts()
async def list_prompts() -> list:
    """List available prompt templates"""
    return [
        Prompt(
            name="show-device-details",
            description="Show all properties of a specific device",
            arguments=[
                PromptArgument(
                    name="device_name",
                    description="Name of the device to query",
                    required=True
                )
            ]
        ),
        Prompt(
            name="show-devices-in-location",
            description="Show the name and IP address of all devices in a specific location",
            arguments=[
                PromptArgument(
                    name="location_name",
                    description="Name of the location to query",
                    required=True
                )
            ]
        ),
        Prompt(
            name="find-ip-address",
            description="Find where a specific IP address is used",
            arguments=[
                PromptArgument(
                    name="ip_address",
                    description="IP address to search for",
                    required=True
                )
            ]
        ),
        Prompt(
            name="list-prefixes-within",
            description="List prefixes that are included within a specific CIDR block",
            arguments=[
                PromptArgument(
                    name="prefix_cidr",
                    description="CIDR block to search within and included (e.g., 10.0.0.0/8)",
                    required=True
                )
            ]
        )
    ]

@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> str:
    """Generate prompt content based on template and arguments"""
    if name == "show-device-details":
        device_name = arguments.get("device_name", "{device_name}")
        return f"show all properties of device {device_name}"
    elif name == "show-devices-in-location":
        location_name = arguments.get("location_name", "{location_name}")
        return f"show the name and the IP address of all devices in location {location_name}"
    elif name == "find-ip-address":
        ip_address = arguments.get("ip_address", "{ip_address}")
        return f"Where do I find the address {ip_address}?"
    elif name == "list-prefixes-within":
        prefix_cidr = arguments.get("prefix_cidr", "{prefix_cidr}")
        return f"List the prefixes that are includes in {prefix_cidr}"
    
    raise ValueError(f"Unknown prompt: {name}")

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Execute MCP tool calls using the query registry"""
    if not client:
        error_msg = "Nautobot client not initialized. Check connection settings."
        logger.error(error_msg)
        return [TextContent(type="text", text=f"Error: {error_msg}")]
    
    try:
        logger.info(f"Executing tool: {name} with arguments: {arguments}")
        
        # Get query from registry
        query = get_query(name)
        
        # Validate arguments
        query.validate_arguments(arguments)
        
        # Execute query
        result = query.execute(client, arguments)
        
        # Handle GraphQL errors
        if hasattr(result, 'get') and result.get("errors"):
            error_msg = f"GraphQL errors: {result['errors']}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]
        
        # Return successful result with special handling for customized queries
        if name == "get_device_details":
            # For customized device queries, return a concise summary
            if "devices" in result:
                devices = result["devices"]
                if devices:
                    summary_lines = [f"Found {len(devices)} device(s):"]
                    for device in devices:
                        device_info = [device.get("hostname", device.get("name", "Unknown"))]
                        if "status" in device:
                            device_info.append(f"Status: {device['status']['name']}")
                        if "role" in device:
                            device_info.append(f"Role: {device['role']['name']}")
                        if "interfaces" in device:
                            device_info.append(f"Interfaces: {len(device['interfaces'])}")
                        summary_lines.append(" - " + " | ".join(device_info))
                    
                    return [TextContent(type="text", text="\n".join(summary_lines))]
                else:
                    return [TextContent(type="text", text="No devices found matching the criteria.")]
            elif "error" in result:
                return [TextContent(type="text", text=f"Error: {result['error']}")]
        
        elif name == "get_ip_addresses":
            # For customized IP address queries, return a concise summary
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
                            interfaces_info = [f"{iface['name']} ({iface['device']['name']})" for iface in ip_addr["interfaces"]]
                            ip_info.append(f"Interfaces: {', '.join(interfaces_info)}")
                        if "primary_ip4_for" in ip_addr and ip_addr["primary_ip4_for"]:
                            devices_info = [device.get("hostname", device.get("name", "Unknown")) for device in ip_addr["primary_ip4_for"]]
                            ip_info.append(f"Primary IP for: {', '.join(devices_info)}")
                        summary_lines.append(" - " + " | ".join(ip_info))
                    
                    return [TextContent(type="text", text="\n".join(summary_lines))]
                else:
                    return [TextContent(type="text", text="No IP addresses found matching the criteria.")]
            elif "error" in result:
                return [TextContent(type="text", text=f"Error: {result['error']}")]
        
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

async def main():
    """Main entry point for the MCP server"""
    logger.info("Starting Nautobot MCP server (v2 - modular)...")
    
    # Display registered queries
    try:
        queries = get_all_queries()
        logger.info(f"Loaded {len(queries)} queries:")
        for tool_name in queries.keys():
            logger.info(f"  - {tool_name}")
    except Exception as e:
        logger.error(f"Failed to load queries: {str(e)}")
    
    # Test connection if client is available
    if client and not client.test_connection():
        logger.warning("Failed to connect to Nautobot, but continuing to serve...")
    
    # Start MCP server
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, 
            write_stream, 
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())