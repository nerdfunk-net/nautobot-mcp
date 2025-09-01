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
        
        # Add a help tool for query discovery
        help_tool = Tool(
            name="help_find_query",
            description="Help find the right query tool based on what you want to search for. Use this when you're not sure which specific query tool to use.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_intent": {
                        "type": "string",
                        "description": "Describe what you want to find (e.g., 'find devices', 'get network interfaces', 'show IP addresses', 'list manufacturers')"
                    }
                },
                "required": ["search_intent"]
            }
        )
        tools.append(help_tool)
        
        # Add REST API fallback tool
        rest_fallback_tool = Tool(
            name="query_rest_api_fallback",
            description="Fallback mechanism using Nautobot REST API for resources not covered by existing queries. Use this when no specific query tool exists for what you need.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_description": {
                        "type": "string",
                        "description": "Describe what you want to find (e.g., 'circuit types', 'cable connections', 'power panels')"
                    },
                    "resource_hint": {
                        "type": "string",
                        "description": "Optional: Specific API endpoint if you know it (e.g., 'circuits/circuit-types', 'dcim/cables')"
                    }
                },
                "required": ["search_description"]
            }
        )
        tools.append(rest_fallback_tool)
        
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
        ),
        Prompt(
            name="show-enabled-interfaces",
            description="Show all interfaces that are enabled in Nautobot",
            arguments=[]
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
    elif name == "show-enabled-interfaces":
        return "Show all interfaces that are enabled in nautobot."
    
    raise ValueError(f"Unknown prompt: {name}")

async def handle_help_query(arguments: dict) -> List[TextContent]:
    """Help find the right query tool based on search intent"""
    search_intent = arguments.get("search_intent", "").lower()
    
    # Map search intents to query tools
    query_mappings = {
        # Device-related
        ("device", "devices", "router", "switch", "server", "host", "hostname"): {
            "tool": "query_devices_dynamic",
            "description": "Use this to find devices, routers, switches, servers, or hosts",
            "examples": ["show device router1", "devices in location datacenter1", "devices with role firewall"]
        },
        
        # Interface-related  
        ("interface", "interfaces", "port", "ports", "ethernet"): {
            "tool": "query_interfaces_dynamic", 
            "description": "Use this to find network interfaces, ports, or ethernet connections",
            "examples": ["show all interfaces", "interfaces on device router1", "enabled interfaces"]
        },
        
        # IP/Network-related
        ("ip", "address", "addresses", "network", "subnet", "prefix"): {
            "tool": "query_ipam_dynamic",
            "description": "Use this to find IP addresses, networks, or subnets", 
            "examples": ["show ip address 192.168.1.1", "ip addresses with dns_name server", "addresses in prefix 10.0.0.0/8"]
        },
        
        # Prefix-specific
        ("prefix", "prefixes", "cidr", "range"): {
            "tool": "query_prefixes_dynamic",
            "description": "Use this to find network prefixes or CIDR blocks",
            "examples": ["show prefix 10.0.0.0/8", "prefixes within 172.16.0.0/12", "prefixes with length 24"]
        },
        
        # Location-related
        ("location", "locations", "site", "sites", "datacenter", "facility"): {
            "tool": "query_locations_dynamic",
            "description": "Use this to find locations, sites, or datacenters", 
            "examples": ["show location datacenter1", "locations with status active", "sites in region west"]
        },
        
        # Device types
        ("device type", "device types", "model", "models", "hardware"): {
            "tool": "query_device_types_dynamic",
            "description": "Use this to find device types, models, or hardware information",
            "examples": ["show all device types", "device types with model c9300", "models from manufacturer cisco"]
        },
        
        # Manufacturers
        ("manufacturer", "manufacturers", "vendor", "vendors", "make", "brand"): {
            "tool": "query_manufacturers_dynamic", 
            "description": "Use this to find manufacturers, vendors, or brands",
            "examples": ["show all manufacturers", "manufacturers with name cisco", "vendors contains hp"]
        },
        
        # Tags
        ("tag", "tags", "label", "labels"): {
            "tool": "query_tags_dynamic",
            "description": "Use this to find tags or labels",
            "examples": ["show all tags", "tags with name production", "tags with description server"]
        }
    }
    
    # Find matching tools
    matches = []
    for keywords, tool_info in query_mappings.items():
        if any(keyword in search_intent for keyword in keywords):
            matches.append(tool_info)
    
    if not matches:
        # No specific matches, show all available tools
        response = "I couldn't find a specific match for your search. Here are all available query tools:\n\n"
        
        queries = get_all_queries()
        for tool_name, query in queries.items():
            response += f"**{tool_name}**\n"
            response += f"  {query.description}\n\n"
        
        response += "You can also describe what you're looking for more specifically, like:\n"
        response += "- 'find devices' → query_devices_dynamic\n" 
        response += "- 'show interfaces' → query_interfaces_dynamic\n"
        response += "- 'get IP addresses' → query_ipam_dynamic\n"
        
    else:
        # Show matching tools
        response = f"Based on your search for '{arguments['search_intent']}', here are the recommended tools:\n\n"
        
        for i, tool_info in enumerate(matches, 1):
            response += f"**{i}. {tool_info['tool']}**\n"
            response += f"   {tool_info['description']}\n"
            response += f"   Examples:\n"
            for example in tool_info['examples']:
                response += f"   - \"{example}\"\n"
            response += "\n"
        
        if len(matches) == 1:
            response += f"💡 **Recommended**: Use `{matches[0]['tool']}` for your query."
        else:
            response += f"💡 **Most likely**: Use `{matches[0]['tool']}` if unsure."
    
    return [TextContent(type="text", text=response)]

async def handle_rest_fallback(arguments: dict) -> List[TextContent]:
    """Handle REST API fallback queries for resources not covered by GraphQL queries"""
    search_description = arguments.get("search_description", "").lower()
    resource_hint = arguments.get("resource_hint")
    
    # Common API endpoint mappings based on search terms
    api_mappings = {
        # Circuits
        ("circuit", "circuits"): "circuits/circuits/",
        ("circuit type", "circuit types"): "circuits/circuit-types/", 
        ("provider", "providers"): "circuits/providers/",
        
        # DCIM (Data Center Infrastructure Management)
        ("cable", "cables"): "dcim/cables/",
        ("console", "console port", "console connection"): "dcim/console-ports/",
        ("power port", "power connection"): "dcim/power-ports/",
        ("power panel", "power panels"): "dcim/power-panels/",
        ("power feed", "power feeds"): "dcim/power-feeds/",
        ("rack", "racks"): "dcim/racks/",
        ("site", "sites"): "dcim/sites/",
        ("region", "regions"): "dcim/regions/",
        
        # IPAM (covered by GraphQL but examples)
        ("vlan", "vlans"): "ipam/vlans/",
        ("vrf", "vrfs"): "ipam/vrfs/",
        ("aggregate", "aggregates"): "ipam/aggregates/",
        
        # Tenancy
        ("tenant", "tenants"): "tenancy/tenants/",
        ("tenant group", "tenant groups"): "tenancy/tenant-groups/",
        
        # Users
        ("user", "users"): "users/users/",
        ("group", "groups"): "users/groups/",
        
        # Virtualization  
        ("virtual machine", "vm", "vms"): "virtualization/virtual-machines/",
        ("cluster", "clusters"): "virtualization/clusters/",
        
        # Extras
        ("webhook", "webhooks"): "extras/webhooks/",
        ("custom field", "custom fields"): "extras/custom-fields/",
        ("export template", "export templates"): "extras/export-templates/",
        ("config context", "config contexts"): "extras/config-contexts/",
    }
    
    # Try to find API endpoint
    endpoint = None
    
    # First check if resource_hint is provided
    if resource_hint:
        endpoint = resource_hint.strip("/")
        if not endpoint.startswith("api/"):
            endpoint = f"api/{endpoint}/"
        else:
            endpoint = f"{endpoint}/"
    else:
        # Search for matching endpoint based on description
        for keywords, api_endpoint in api_mappings.items():
            if any(keyword in search_description for keyword in keywords):
                endpoint = f"api/{api_endpoint}"
                break
    
    if not endpoint:
        # If no specific endpoint found, try to suggest alternatives
        response = f"I couldn't find a specific API endpoint for '{search_description}'.\n\n"
        response += "Available REST API categories include:\n"
        response += "- **Circuits**: circuit-types, circuits, providers\n"
        response += "- **DCIM**: cables, racks, power-panels, console-ports\n" 
        response += "- **IPAM**: vlans, vrfs, aggregates\n"
        response += "- **Tenancy**: tenants, tenant-groups\n"
        response += "- **Virtualization**: virtual-machines, clusters\n"
        response += "- **Users**: users, groups\n"
        response += "- **Extras**: webhooks, custom-fields, config-contexts\n\n"
        response += "You can:\n"
        response += "1. Be more specific about what you're looking for\n"
        response += "2. Provide a `resource_hint` like 'circuits/circuit-types'\n"
        response += "3. Check the Nautobot API docs at /api/docs/\n"
        
        return [TextContent(type="text", text=response)]
    
    # Execute the REST API call
    try:
        logger.info(f"Executing REST API fallback: {endpoint}")
        result = client.rest_get(f"/{endpoint}")
        
        if result:
            # Format the response nicely
            if "results" in result:
                # Paginated response
                items = result["results"]
                total_count = result.get("count", len(items))
                
                response = f"Found {total_count} items from REST API endpoint `{endpoint}`:\n\n"
                
                # Show first few items with key details
                for i, item in enumerate(items[:10]):  # Limit to first 10
                    response += f"**{i+1}. "
                    
                    # Try to find a good display name
                    display_name = item.get("name") or item.get("display") or item.get("slug") or f"Item {item.get('id', i+1)}"
                    response += f"{display_name}**\n"
                    
                    # Add key details
                    key_fields = ["description", "status", "type", "location", "role"]
                    details = []
                    for field in key_fields:
                        if field in item and item[field]:
                            value = item[field]
                            if isinstance(value, dict) and "name" in value:
                                value = value["name"]
                            details.append(f"{field}: {value}")
                    
                    if details:
                        response += f"   {' | '.join(details)}\n"
                    response += "\n"
                
                if len(items) > 10:
                    response += f"... and {len(items) - 10} more items.\n\n"
                
                response += f"**API Endpoint**: `{endpoint}`\n"
                response += f"**Total Count**: {total_count}\n"
                
            else:
                # Direct result
                response = f"Result from REST API endpoint `{endpoint}`:\n\n"
                response += f"```json\n{result}\n```"
        else:
            response = f"No data returned from API endpoint `{endpoint}`"
            
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        error_response = f"Error querying REST API endpoint `{endpoint}`: {str(e)}\n\n"
        error_response += "This could mean:\n"
        error_response += "1. The endpoint doesn't exist\n"
        error_response += "2. You don't have permission to access it\n"
        error_response += "3. The Nautobot instance is not responding\n\n"
        error_response += "Try checking the API documentation at /api/docs/"
        
        return [TextContent(type="text", text=error_response)]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Execute MCP tool calls using the query registry"""
    if not client:
        error_msg = "Nautobot client not initialized. Check connection settings."
        logger.error(error_msg)
        return [TextContent(type="text", text=f"Error: {error_msg}")]
    
    try:
        logger.info(f"Executing tool: {name} with arguments: {arguments}")
        
        # Handle the help tool
        if name == "help_find_query":
            return await handle_help_query(arguments)
        
        # Handle the REST API fallback tool
        if name == "query_rest_api_fallback":
            return await handle_rest_fallback(arguments)
        
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