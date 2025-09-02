"""
REST API fallback handler for resources not covered by GraphQL queries
"""

from typing import List
import logging
from mcp.types import TextContent

logger = logging.getLogger(__name__)


class RestFallbackHandler:
    """Handler for REST API fallback queries"""

    def __init__(self, client):
        self.client = client

    async def handle(self, arguments: dict) -> List[TextContent]:
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
            result = self.client.rest_get(f"/{endpoint}")

            if result:
                # Format the response nicely
                if "results" in result:
                    # Paginated response
                    items = result["results"]
                    total_count = result.get("count", len(items))

                    response = f"Found {total_count} items from REST API endpoint `{endpoint}`:\n\n"

                    # Show first few items with key details
                    for i, item in enumerate(items[:10]):  # Limit to first 10
                        response += f"**{i + 1}. "

                        # Try to find a good display name
                        display_name = (
                            item.get("name")
                            or item.get("display")
                            or item.get("slug")
                            or f"Item {item.get('id', i + 1)}"
                        )
                        response += f"{display_name}**\n"

                        # Add key details
                        key_fields = [
                            "description",
                            "status",
                            "type",
                            "location",
                            "role",
                        ]
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
            error_response = (
                f"Error querying REST API endpoint `{endpoint}`: {str(e)}\n\n"
            )
            error_response += "This could mean:\n"
            error_response += "1. The endpoint doesn't exist\n"
            error_response += "2. You don't have permission to access it\n"
            error_response += "3. The Nautobot instance is not responding\n\n"
            error_response += "Try checking the API documentation at /api/docs/"

            return [TextContent(type="text", text=error_response)]
