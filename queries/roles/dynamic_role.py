"""
Dynamic role query module that supports variable replacement
"""

import logging
from typing import Dict, Any
from ..base import BaseQuery, QueryType, MatchType, ToolSchema
from .prompt_parser import parse_role_prompt

# Set up logger
logger = logging.getLogger(__name__)

class DynamicRoleQuery(BaseQuery):
    """Dynamic role query that replaces placeholders based on user input"""
    
    def __init__(self):
        self.base_query = """
    query Roles (
        $get_id: Boolean = false,
        $get_name: Boolean = true,
        $get_description: Boolean = false,
        $get_content_types: Boolean = true,
        $variable_value: [String],
    ){
    roles (enter_variable_name_here: $variable_value) {
        id @include(if: $get_id)
        name @include(if: $get_name)
        description @include(if: $get_description)
        content_types @include(if: $get_content_types)  {
        id
            model
        }
    }
    }"""
        super().__init__()
    
    def get_tool_name(self) -> str:
        return "query_roles_dynamic"
    
    def get_description(self) -> str:
        return "Query roles with dynamic filtering by any property (name, description, content_types, etc.)"
    
    def get_query_type(self) -> QueryType:
        return QueryType.GRAPHQL
    
    def get_match_type(self) -> MatchType:
        return MatchType.EXACT
    
    def get_queries(self) -> str:
        return self.base_query
    
    def get_input_schema(self) -> ToolSchema:
        return ToolSchema(
            type="object",
            properties={
                "prompt": {
                    "type": "string",
                    "description": "Natural language query (e.g., 'show all roles', 'roles with name firewall')"
                },
                "variable_name": {
                    "type": "string", 
                    "description": "Manual: The role property to filter by (e.g., 'name', 'description', 'content_types')"
                },
                "variable_value": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Manual: The value(s) to filter by"
                },
                "get_id": {"type": "boolean", "default": False},
                "get_name": {"type": "boolean", "default": True},
                "get_description": {"type": "boolean", "default": False},
                "get_content_types": {"type": "boolean", "default": True}
            },
            required=[]
        )
    
    def _remove_filtering(self, query: str) -> str:
        """Remove the filtering clause from the query to fetch all records"""
        # Replace the filtered query with an unfiltered one
        query = query.replace("roles (enter_variable_name_here: $variable_value)", "roles")
        # Remove the variable declaration
        query = query.replace("$variable_value: [String],", "")
        return query
    
    def _execute_graphql(self, client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL query with dynamic variable replacement"""
        
        # Check if we have a prompt to parse
        if "prompt" in arguments:
            parsed = parse_role_prompt(arguments["prompt"])
            # Merge parsed parameters with existing arguments
            for key, value in parsed.items():
                if key not in arguments or arguments[key] is None:
                    arguments[key] = value
        
        # Check if this is a "show all" query
        if arguments.get("show_all"):
            query = self._remove_filtering(self.base_query)
            # Remove variable_value from arguments since it's not needed
            filtered_args = {k: v for k, v in arguments.items() 
                           if k not in ["variable_value", "variable_name", "show_all"]}
        else:
            # Get the variable name and value (either from prompt parsing or manual input)
            variable_name = arguments.get("variable_name")
            variable_value = arguments.get("variable_value")
            
            if not variable_name or not variable_value:
                raise ValueError("Either 'prompt' or both 'variable_name' and 'variable_value' must be provided")
            
            # Start with the base query and replace the placeholder
            query = self.base_query
            query = query.replace("enter_variable_name_here", variable_name)
            filtered_args = arguments
        
        # Log the complete query for debugging
        logger.info("=" * 80)
        logger.info("EXECUTING GRAPHQL QUERY:")
        logger.info("=" * 80)
        logger.info(query)
        logger.info("=" * 80)
        logger.info("WITH ARGUMENTS:")
        logger.info(filtered_args)
        logger.info("=" * 80)
        
        return client.graphql_query(query, filtered_args)