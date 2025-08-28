"""
Devices by name query module
"""

from ..base import CombinedMatchQuery

class DevicesByNameQuery(CombinedMatchQuery):
    def __init__(self):
        exact_query = """
            query devices_by_name_exact($name_filter: [String]) {
                devices(name: $name_filter) {
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
        
        pattern_query = """
            query devices_by_name_pattern($name_filter: [String]) {
                devices(name__ire: $name_filter) {
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
            tool_name="devices_by_name",
            description="Find devices by name (supports exact match and pattern matching)",
            exact_query=exact_query,
            pattern_query=pattern_query,
            filter_param="name_filter"
        )