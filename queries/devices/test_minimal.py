"""
Minimal test query to debug Claude Desktop hanging
"""

from ..base import SimpleGraphQLQuery

class TestMinimalQuery(SimpleGraphQLQuery):
    def __init__(self):
        # Extremely simple query
        query = """
            query test_minimal {
                devices {
                    name
                }
            }"""
        
        super().__init__(
            tool_name="test_minimal",
            description="Minimal test query - just device names",
            query=query,
            required_params=[]
        )