"""
Devices by manufacturer query module
"""

from ..base import SimpleGraphQLQuery

class DevicesByManufacturerQuery(SimpleGraphQLQuery):
    def __init__(self):
        query = """
            query devices_by_manufacturer($manufacturer_filter: [String]) {
                devices(manufacturer: $manufacturer_filter) {
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
            tool_name="devices_by_manufacturer",
            description="Find devices by manufacturer",
            query=query,
            required_params=["manufacturer_filter"]
        )