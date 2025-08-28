"""
Devices by role query module
"""

from ..base import SimpleGraphQLQuery

class DevicesByRoleQuery(SimpleGraphQLQuery):
    def __init__(self):
        query = """
            query devices_by_role($role_filter: [String]) {
                devices(role: $role_filter) {
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
            tool_name="devices_by_role",
            description="Find devices by role",
            query=query,
            required_params=["role_filter"]
        )