"""
Devices by tag query module
"""

from ..base import SimpleGraphQLQuery

class DevicesByTagQuery(SimpleGraphQLQuery):
    def __init__(self):
        query = """
            query devices_by_tag($tag_filter: [String]) {
                devices(tags: $tag_filter) {
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
            tool_name="devices_by_tag",
            description="Find devices by tag",
            query=query,
            required_params=["tag_filter"]
        )