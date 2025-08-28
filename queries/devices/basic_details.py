"""
Basic device details query - simplified version for better Claude Desktop compatibility
"""

from ..base import SimpleGraphQLQuery

class DeviceBasicDetailsQuery(SimpleGraphQLQuery):
    def __init__(self):
        query = """
            query device_basic_details($name_filter: [String]) {
                devices(name: $name_filter) {
                    name
                    status { name }
                    role { name }
                    device_type { 
                        model 
                        manufacturer { name }
                    }
                    location { name }
                    primary_ip4 { address }
                    platform { name }
                }
            }"""
        
        super().__init__(
            tool_name="get_device_summary",
            description="Get basic device information (name, status, role, type, location, IP)",
            query=query,
            required_params=["name_filter"]
        )