"""
Tool registry for MCP server tools
"""

from typing import List
import logging
from mcp.types import Tool, Prompt, PromptArgument
from queries import get_all_queries

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for MCP tools and prompts"""
    
    @staticmethod 
    def get_all_tools() -> List[Tool]:
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
                            "description": "Describe what you want to find (e.g., 'find devices', 'get network interfaces', 'show IP addresses', 'list manufacturers')",
                        }
                    },
                    "required": ["search_intent"],
                },
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
                            "description": "Describe what you want to find (e.g., 'circuit types', 'cable connections', 'power panels')",
                        },
                        "resource_hint": {
                            "type": "string",
                            "description": "Optional: Specific API endpoint if you know it (e.g., 'circuits/circuit-types', 'dcim/cables')",
                        },
                    },
                    "required": ["search_description"],
                },
            )
            tools.append(rest_fallback_tool)

            # Add device onboarding tool
            onboard_tool = Tool(
                name="onboard_device",
                description="Onboard a new network device to Nautobot. Requires mandatory fields: ip_address, location, and secret_groups. Optional fields have defaults. Platform autodetection is used if platform is not specified or not found.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ip_address": {
                            "type": "string",
                            "description": "IP address of the device to onboard (required)",
                        },
                        "location": {
                            "type": "string",
                            "description": "Location name where the device is located (required)",
                        },
                        "secret_groups": {
                            "type": "string",
                            "description": "Secret groups for device authentication (required)",
                        },
                        "role": {
                            "type": "string",
                            "description": "Device role (optional, defaults to 'network')",
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Namespace for the device (optional, defaults to 'Global')",
                        },
                        "status": {
                            "type": "string",
                            "description": "Device status (optional, defaults to 'Active')",
                        },
                        "platform": {
                            "type": "string",
                            "description": "Platform type (optional, defaults to autodetection if not specified or not found)",
                        },
                        "port": {
                            "type": "integer",
                            "description": "SSH port for device connection (optional, defaults to 22)",
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Connection timeout in seconds (optional, defaults to 30)",
                        },
                        "update_devices_without_primary_ip": {
                            "type": "boolean",
                            "description": "Update devices without primary IP (optional, defaults to false)",
                        },
                    },
                    "required": ["ip_address", "location", "secret_groups"],
                },
            )
            tools.append(onboard_tool)

            # Add query tools from registry
            for query in queries.values():
                # Convert query schema to MCP Tool schema
                tool = Tool(
                    name=query.tool_name,
                    description=query.description,
                    inputSchema={
                        "type": query.schema.type,
                        "properties": query.schema.properties,
                        "required": query.schema.required,
                    },
                )
                tools.append(tool)
                logger.debug(f"Registered tool: {query.tool_name}")

            return tools

        except Exception as e:
            logger.error(f"Failed to list tools: {str(e)}")
            return []
    
    @staticmethod
    def get_all_prompts() -> List[Prompt]:
        """List available prompt templates"""
        return [
            Prompt(
                name="show-device-details",
                description="Show all properties of a specific device",
                arguments=[
                    PromptArgument(
                        name="device_name",
                        description="Name of the device to query",
                        required=True,
                    )
                ],
            ),
            Prompt(
                name="show-devices-in-location",
                description="Show the name and IP address of all devices in a specific location",
                arguments=[
                    PromptArgument(
                        name="location_name",
                        description="Name of the location to query",
                        required=True,
                    )
                ],
            ),
            Prompt(
                name="find-ip-address",
                description="Find where a specific IP address is used",
                arguments=[
                    PromptArgument(
                        name="ip_address",
                        description="IP address to search for",
                        required=True,
                    )
                ],
            ),
            Prompt(
                name="list-prefixes-within",
                description="List prefixes that are included within a specific CIDR block",
                arguments=[
                    PromptArgument(
                        name="prefix_cidr",
                        description="CIDR block to search within and included (e.g., 10.0.0.0/8)",
                        required=True,
                    )
                ],
            ),
            Prompt(
                name="show-enabled-interfaces",
                description="Show all interfaces that are enabled in Nautobot",
                arguments=[],
            ),
        ]
    
    @staticmethod
    def generate_prompt_content(name: str, arguments: dict) -> str:
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