"""
Get tags query module
"""

from ..base import SimpleGraphQLQuery


class GetTagsQuery(SimpleGraphQLQuery):
    def __init__(self):
        query = """
            query tags($tags_filter: [String]) {
                tags(content_types: $tags_filter) {
                    name
                }
            }"""

        super().__init__(
            tool_name="get_tags",
            description="Get available tags",
            query=query,
            required_params=[],
            optional_params={
                "tags_filter": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional filter for specific tag content types",
                }
            },
        )
