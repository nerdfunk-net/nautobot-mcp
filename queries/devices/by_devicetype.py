"""
Devices by device type query module
"""

from ..base import SimpleGraphQLQuery

class DevicesByDeviceTypeQuery(SimpleGraphQLQuery):
    def __init__(self):
        query = """
            query devices_by_devicetype($devicetype_filter: [String]) {
                devices(device_type: $devicetype_filter) {
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
            tool_name="devices_by_devicetype",
            description="Find devices by device type",
            query=query,
            required_params=["devicetype_filter"]
        )