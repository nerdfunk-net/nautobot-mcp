"""
Get custom fields query module  
"""

from ..base import BaseQuery, QueryType, MatchType, ToolSchema

class GetCustomFieldsQuery(BaseQuery):
    def get_tool_name(self) -> str:
        return "get_custom_fields"
    
    def get_description(self) -> str:
        return "Get custom field definitions"
    
    def get_query_type(self) -> QueryType:
        return QueryType.REST
    
    def get_match_type(self) -> MatchType:
        return MatchType.EXACT
    
    def get_queries(self) -> str:
        return "/api/extras/custom-fields/?depth=0&exclude_m2m=false"
    
    def get_input_schema(self) -> ToolSchema:
        return ToolSchema(
            type="object",
            properties={},
            required=[]
        )