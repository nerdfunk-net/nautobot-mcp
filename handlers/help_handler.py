"""
Help handler for query discovery
"""

from typing import List
from mcp.types import TextContent
from queries import get_all_queries


class HelpHandler:
    """Handler for the help_find_query tool"""
    
    @staticmethod
    async def handle(arguments: dict) -> List[TextContent]:
        """Help find the right query tool based on search intent"""
        search_intent = arguments.get("search_intent", "").lower()

        # Map search intents to query tools
        query_mappings = {
            # Device-related
            ("device", "devices", "router", "switch", "server", "host", "hostname"): {
                "tool": "query_devices_dynamic",
                "description": "Use this to find devices, routers, switches, servers, or hosts",
                "examples": [
                    "show device router1",
                    "devices in location datacenter1",
                    "devices with role firewall",
                ],
            },
            # Interface-related
            ("interface", "interfaces", "port", "ports", "ethernet"): {
                "tool": "query_interfaces_dynamic",
                "description": "Use this to find network interfaces, ports, or ethernet connections",
                "examples": [
                    "show all interfaces",
                    "interfaces on device router1",
                    "enabled interfaces",
                ],
            },
            # IP/Network-related
            ("ip", "address", "addresses", "network", "subnet", "prefix"): {
                "tool": "query_ipam_dynamic",
                "description": "Use this to find IP addresses, networks, or subnets",
                "examples": [
                    "show ip address 192.168.1.1",
                    "ip addresses with dns_name server",
                    "addresses in prefix 10.0.0.0/8",
                ],
            },
            # Prefix-specific
            ("prefix", "prefixes", "cidr", "range"): {
                "tool": "query_prefixes_dynamic",
                "description": "Use this to find network prefixes or CIDR blocks",
                "examples": [
                    "show prefix 10.0.0.0/8",
                    "prefixes within 172.16.0.0/12",
                    "prefixes with length 24",
                ],
            },
            # Location-related
            ("location", "locations", "site", "sites", "datacenter", "facility"): {
                "tool": "query_locations_dynamic",
                "description": "Use this to find locations, sites, or datacenters",
                "examples": [
                    "show location datacenter1",
                    "locations with status active",
                    "sites in region west",
                ],
            },
            # Device types
            ("device type", "device types", "model", "models", "hardware"): {
                "tool": "query_device_types_dynamic",
                "description": "Use this to find device types, models, or hardware information",
                "examples": [
                    "show all device types",
                    "device types with model c9300",
                    "models from manufacturer cisco",
                ],
            },
            # Manufacturers
            ("manufacturer", "manufacturers", "vendor", "vendors", "make", "brand"): {
                "tool": "query_manufacturers_dynamic",
                "description": "Use this to find manufacturers, vendors, or brands",
                "examples": [
                    "show all manufacturers",
                    "manufacturers with name cisco",
                    "vendors contains hp",
                ],
            },
            # Tags
            ("tag", "tags", "label", "labels"): {
                "tool": "query_tags_dynamic",
                "description": "Use this to find tags or labels",
                "examples": [
                    "show all tags",
                    "tags with name production",
                    "tags with description server",
                ],
            },
            # Namespaces
            ("namespace", "namespaces", "tenant", "tenants"): {
                "tool": "query_namespaces_dynamic",
                "description": "Use this to find namespaces or tenants",
                "examples": [
                    "show namespace Global",
                    "namespaces with description production",
                    "show all namespaces",
                ],
            },
            # Secrets groups
            ("secret", "secrets", "secret group", "secrets group", "auth group", "credential"): {
                "tool": "query_secrets_groups_dynamic",
                "description": "Use this to find secrets groups, authentication groups, or credential groups",
                "examples": [
                    "show secrets group production",
                    "secret group with name test",
                    "show all secrets groups",
                ],
            },
            # Onboarding
            ("onboard", "onboarding", "add device", "new device", "create device"): {
                "tool": "onboard_device",
                "description": "Use this to onboard a new network device to Nautobot",
                "examples": [
                    "onboard device 192.168.1.1 in location datacenter1",
                    "add new device with IP 10.0.0.1",
                    "create device at location site1",
                ],
            },
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

            response += (
                "You can also describe what you're looking for more specifically, like:\n"
            )
            response += "- 'find devices' → query_devices_dynamic\n"
            response += "- 'show interfaces' → query_interfaces_dynamic\n"
            response += "- 'get IP addresses' → query_ipam_dynamic\n"

        else:
            # Show matching tools
            response = f"Based on your search for '{arguments['search_intent']}', here are the recommended tools:\n\n"

            for i, tool_info in enumerate(matches, 1):
                response += f"**{i}. {tool_info['tool']}**\n"
                response += f"   {tool_info['description']}\n"
                response += "   Examples:\n"
                for example in tool_info["examples"]:
                    response += f'   - "{example}"\n'
                response += "\n"

            if len(matches) == 1:
                response += (
                    f"💡 **Recommended**: Use `{matches[0]['tool']}` for your query."
                )
            else:
                response += f"💡 **Most likely**: Use `{matches[0]['tool']}` if unsure."

        return [TextContent(type="text", text=response)]