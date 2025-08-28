"""
Get roles query module
"""

from ..base import SimpleGraphQLQuery

class GetRolesQuery(SimpleGraphQLQuery):
    def __init__(self):
        query = """
            query roles($role_filter: [String]) {
                roles(content_types: $role_filter) {
                    name
                }
            }"""
        
        super().__init__(
            tool_name="get_roles",
            description="Get available device roles",
            query=query,
            required_params=[],
            optional_params={
                "role_filter": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional filter for specific role content types"
                }
            }
        )