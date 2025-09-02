"""
Device onboarding handler
"""

from typing import List
import logging
from mcp.types import TextContent
from resolvers import (
    LocationResolver, 
    NamespaceResolver, 
    RoleResolver, 
    StatusResolver, 
    PlatformResolver, 
    SecretsGroupResolver
)

logger = logging.getLogger(__name__)


class OnboardHandler:
    """Handler for device onboarding operations"""
    
    def __init__(self, cache, client):
        self.cache = cache
        self.client = client
        
        # Initialize resolvers
        self.location_resolver = LocationResolver(cache, client)
        self.namespace_resolver = NamespaceResolver(cache, client)
        self.role_resolver = RoleResolver(cache, client)
        self.status_resolver = StatusResolver(cache, client)
        self.platform_resolver = PlatformResolver(cache, client)
        self.secrets_group_resolver = SecretsGroupResolver(cache, client)
    
    async def handle(self, arguments: dict) -> List[TextContent]:
        """Handle device onboarding to Nautobot with name-to-ID resolution"""
        # Validate mandatory fields
        ip_address = arguments.get("ip_address")
        location_name = arguments.get("location")
        secret_groups_name = arguments.get("secret_groups")

        if not ip_address:
            return [TextContent(type="text", text="Error: ip_address is required for device onboarding")]
        
        if not location_name:
            return [TextContent(type="text", text="Error: location is required for device onboarding")]
            
        if not secret_groups_name:
            return [TextContent(type="text", text="Error: secret_groups is required for device authentication")]

        # Get parameter names for resolution
        role_name = arguments.get("role", "network")
        namespace_name = arguments.get("namespace", "Global")
        status_name = arguments.get("status", "Active")
        platform_name = arguments.get("platform", "")

        try:
            logger.info(f"Starting onboarding process for device {ip_address}")
            logger.info("Resolving names to IDs...")

            # Resolve all names to IDs using resolvers
            resolution_tasks = [
                ("location", self.location_resolver.resolve(location_name)),
                ("secrets_group", self.secrets_group_resolver.resolve(secret_groups_name)),
                ("role", self.role_resolver.resolve(role_name)),
                ("namespace", self.namespace_resolver.resolve(namespace_name)),
                ("status", self.status_resolver.resolve(status_name)),
                ("platform", self.platform_resolver.resolve(platform_name)),
            ]

            # Collect resolution results
            resolved_ids = {}
            errors = []
            
            for param_name, task in resolution_tasks:
                param_id, error = await task
                if error:
                    errors.append(f"  ❌ {param_name}: {error}")
                else:
                    resolved_ids[param_name] = param_id
                    logger.info(f"✅ Resolved {param_name} to ID: {param_id}")

            # If any resolution failed, return error
            if errors:
                error_msg = f"❌ Failed to resolve the following parameters to IDs:\n\n"
                error_msg += "\n".join(errors)
                error_msg += "\n\n**Troubleshooting:**\n"
                error_msg += "- Use `query_locations_dynamic` to see available locations\n"
                error_msg += "- Use `query_namespaces_dynamic` to see available namespaces\n"
                error_msg += "- Use `query_rest_api_fallback` with 'roles' to see available roles\n"
                error_msg += "- Use `query_rest_api_fallback` with 'statuses' to see available statuses\n"
                error_msg += "- Check that secret groups exist in your Nautobot instance\n"
                return [TextContent(type="text", text=error_msg)]

            # All IDs resolved successfully, prepare device data
            device_data = {
                "location": resolved_ids["location"],
                "ip_addresses": ip_address,
                "secrets_group": resolved_ids["secrets_group"],
                "device_role": resolved_ids["role"],
                "namespace": resolved_ids["namespace"],
                "device_status": resolved_ids["status"],
                "interface_status": resolved_ids["status"],  # Use same status for all
                "ip_address_status": resolved_ids["status"],
                "platform": resolved_ids["platform"],
                "port": arguments.get("port", 22),
                "timeout": arguments.get("timeout", 30),
                "update_devices_without_primary_ip": arguments.get("update_devices_without_primary_ip", False)
            }

            logger.info(f"Resolved device data with IDs: {device_data}")
            
            # Call Nautobot onboarding API with resolved IDs
            response = self.client.rest_post(
                "/api/extras/jobs/Sync%20Devices%20From%20Network/run/",
                {"data": device_data}
            )

            if response.get("job_id"):
                success_msg = f"✅ Device {ip_address} successfully queued for onboarding\n\n"
                success_msg += f"**Job ID**: {response['job_id']}\n\n"
                success_msg += f"**Device Details** (names → IDs resolved):\n"
                success_msg += f"  - IP Address: {ip_address}\n"
                success_msg += f"  - Location: {location_name} → {resolved_ids['location']}\n"
                
                # Handle platform display
                if resolved_ids['platform'] is None:
                    success_msg += f"  - Platform: {platform_name} → autodetect (None)\n"
                else:
                    success_msg += f"  - Platform: {platform_name} → {resolved_ids['platform']}\n"
                    
                success_msg += f"  - Role: {role_name} → {resolved_ids['role']}\n"
                success_msg += f"  - Status: {status_name} → {resolved_ids['status']}\n"
                success_msg += f"  - Namespace: {namespace_name} → {resolved_ids['namespace']}\n"
                success_msg += f"  - Secret Groups: {secret_groups_name} → {resolved_ids['secrets_group']}\n"
                success_msg += f"  - Port: {device_data['port']}\n"
                success_msg += f"  - Timeout: {device_data['timeout']}s\n\n"
                success_msg += "The device onboarding job is now running in the background. "
                success_msg += "You can monitor the job progress in Nautobot's Jobs interface."
                
                return [TextContent(type="text", text=success_msg)]
            else:
                error_msg = f"❌ Device onboarding failed: No job ID returned from Nautobot\n"
                error_msg += f"Response: {response}"
                return [TextContent(type="text", text=error_msg)]

        except Exception as e:
            error_msg = f"❌ Device onboarding failed: {str(e)}\n\n"
            error_msg += "This could be due to:\n"
            error_msg += "1. Network connectivity issues\n"
            error_msg += "2. Authentication problems\n"
            error_msg += "3. API endpoint not available\n"
            error_msg += "4. Invalid resolved ID values\n\n"
            error_msg += f"**Debug Information**:\n"
            error_msg += f"- IP Address: {ip_address}\n"
            error_msg += f"- Location: {location_name}\n"
            error_msg += f"- Secret Groups: {secret_groups_name}\n"
            
            return [TextContent(type="text", text=error_msg)]