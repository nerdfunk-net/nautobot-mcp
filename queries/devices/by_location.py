"""
Devices by location query module
"""

from ..base import CombinedMatchQuery

class DevicesByLocationQuery(CombinedMatchQuery):
    def __init__(self):
        exact_query = """
            query devices_by_location_exact($location_filter: [String]) {
                locations(name: $location_filter) {
                    name
                    devices {
                        id
                        name
                        role {
                            name
                        }
                        location {
                            name
                        }
                        primary_ip4 {
                            address
                        }
                        status {
                            name
                        }
                    }
                }
            }"""
        
        pattern_query = """
            query devices_by_location_pattern($location_filter: [String]) {
                locations(name__ire: $location_filter) {
                    name
                    devices {
                        id
                        name
                        role {
                            name
                        }
                        location {
                            name
                        }
                        primary_ip4 {
                            address
                        }
                        status {
                            name
                        }
                    }
                }
            }"""
        
        super().__init__(
            tool_name="devices_by_location",
            description="Find devices by location (supports exact match and pattern matching)",
            exact_query=exact_query,
            pattern_query=pattern_query,
            filter_param="location_filter"
        )