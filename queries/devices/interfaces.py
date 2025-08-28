"""
Device interfaces query module
"""

from ..base import SimpleGraphQLQuery

class DeviceInterfacesQuery(SimpleGraphQLQuery):
    def __init__(self):
        query = """
            query device_interfaces($device_filter: [String]) {
                devices(name: $device_filter) {
                    name
                    interfaces {
                        name
                        type
                        enabled
                        ip_addresses {
                            address
                        }
                        status {
                            name
                        }
                    }
                }
            }"""
        
        super().__init__(
            tool_name="get_device_interfaces",
            description="Get interfaces for specific devices",
            query=query,
            required_params=["device_filter"]
        )