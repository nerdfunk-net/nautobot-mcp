"""
Devices by platform query module
"""

from ..base import SimpleGraphQLQuery

class DevicesByPlatformQuery(SimpleGraphQLQuery):
    def __init__(self):
        query = """
            query devices_by_platform($platform_filter: [String]) {
                devices(platform: $platform_filter) {
                    id
                    name
                    primary_ip4 {
                        address
                    }
                    status {
                        name
                    }
                    device_type {
                        model
                    }
                }
            }"""
        
        super().__init__(
            tool_name="devices_by_platform",
            description="Find devices by platform",
            query=query,
            required_params=["platform_filter"]
        )