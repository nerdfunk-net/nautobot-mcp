"""
Dynamic prefix query module that supports variable replacement
"""

import logging
from typing import Dict, Any
from ..base import BaseQuery, QueryType, MatchType, ToolSchema
from .prompt_parser import parse_prefix_prompt

# Set up logger
logger = logging.getLogger(__name__)


class DynamicPrefixQuery(BaseQuery):
    """Dynamic prefix query that replaces placeholders based on user input"""

    def __init__(self):
        self.base_query = """
    query Prefixes(
    $get_id: Boolean = false,
    $get_prefix_length: Boolean = true,
    $get_ip_version: Boolean = true,
    $get_broadcast: Boolean = true,
    $get_description: Boolean = true,
    $get_parent: Boolean = true,
    $get_status: Boolean = true,
    $get_namespace: Boolean = true,
    $get_tags: Boolean = true,
    $get_vlan: Boolean = true,
    $get_location: Boolean = true,
    $get_vrf_assignments: Boolean = true,
    $get_custom_field_data: Boolean = true,
    $variable_value: [String],
    ) {
    prefixes (enter_variable_name_here: $variable_value) {
        id @include(if: $get_id)
        prefix
        ip_version @include(if: $get_ip_version)
        prefix_length @include(if: $get_prefix_length)
        broadcast @include(if: $get_broadcast)
        description @include(if: $get_description)
        _custom_field_data @include(if: $get_custom_field_data)
        status @include(if: $get_status) {
        id @include(if: $get_id)
        name
        }
        namespace @include(if: $get_namespace) {
        id @include(if: $get_id)
        name
        }
        tags @include(if: $get_tags) {
        id @include(if: $get_id)
        name
        }
        vlan @include(if: $get_vlan) {
        id @include(if: $get_id)
        vid
        vlan_group {
            id
        }
        name
        }
        parent @include(if: $get_parent) {
        id @include(if: $get_id)
        prefix
        prefix_length
        parent {
            id
        }
        }
        location @include(if: $get_location) {
        id @include(if: $get_id)
        name
        }
        vrf_assignments @include(if: $get_vrf_assignments) {
        id @include(if: $get_id)
        vrf {
            id
        }
        }
    }
    }"""
        super().__init__()

    def get_tool_name(self) -> str:
        return "query_prefixes_dynamic"

    def get_description(self) -> str:
        return "Query prefixes with dynamic filtering by any property (prefix, description, location, etc.)"

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
                    "description": "Natural language query (e.g., 'show all prefixes', 'show prefix 192.168.1.0/24')",
                },
                "variable_name": {
                    "type": "string",
                    "description": "Manual: The prefix property to filter by (e.g., 'prefix', 'description', 'location')",
                },
                "variable_value": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Manual: The value(s) to filter by",
                },
                "get_id": {"type": "boolean", "default": False},
                "get_prefix_length": {"type": "boolean", "default": True},
                "get_ip_version": {"type": "boolean", "default": True},
                "get_broadcast": {"type": "boolean", "default": True},
                "get_description": {"type": "boolean", "default": True},
                "get_parent": {"type": "boolean", "default": True},
                "get_status": {"type": "boolean", "default": True},
                "get_namespace": {"type": "boolean", "default": True},
                "get_tags": {"type": "boolean", "default": True},
                "get_vlan": {"type": "boolean", "default": True},
                "get_location": {"type": "boolean", "default": True},
                "get_vrf_assignments": {"type": "boolean", "default": True},
                "get_custom_field_data": {"type": "boolean", "default": True},
            },
            required=[],
        )

    def _remove_filtering(self, query: str) -> str:
        """Remove the filtering clause from the query to fetch all records"""
        # Replace the filtered query with an unfiltered one
        query = query.replace(
            "prefixes (enter_variable_name_here: $variable_value)", "prefixes"
        )
        # Remove the variable declaration
        query = query.replace("$variable_value: [String],", "")
        return query

    def _execute_graphql(self, client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL query with dynamic variable replacement"""

        # Check if we have a prompt to parse
        if "prompt" in arguments:
            parsed = parse_prefix_prompt(arguments["prompt"])
            # Merge parsed parameters with existing arguments
            for key, value in parsed.items():
                if key not in arguments or arguments[key] is None:
                    arguments[key] = value

        # Check if this is a "show all" query
        if arguments.get("show_all"):
            query = self._remove_filtering(self.base_query)
            # Remove unnecessary arguments
            filtered_args = {
                k: v
                for k, v in arguments.items()
                if k not in ["variable_value", "variable_name", "show_all"]
            }
        else:
            # Get the variable name and value (either from prompt parsing or manual input)
            variable_name = arguments.get("variable_name")
            variable_value = arguments.get("variable_value")

            if not variable_name or not variable_value:
                raise ValueError(
                    "Either 'prompt' or both 'variable_name' and 'variable_value' must be provided"
                )

            # Start with the base query
            query = self.base_query

            # Replace the main variable placeholder
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
