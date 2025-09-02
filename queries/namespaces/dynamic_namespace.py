"""
Dynamic namespace query module that supports variable replacement
"""

import logging
from typing import Dict, Any
from ..base import BaseQuery, QueryType, MatchType, ToolSchema
from .prompt_parser import parse_namespace_prompt
from ..sanitizer import sanitize_query_input

# Set up logger
logger = logging.getLogger(__name__)


class DynamicNamespaceQuery(BaseQuery):
    """Dynamic namespace query that replaces placeholders based on user input"""

    def __init__(self):
        # Mapping of common incorrect/alternate field names to correct GraphQL field names
        self.field_mappings = {
            # Common aliases for namespace name
            "namespace": "name",
            "namespace_name": "name",
            "ns": "name",
            "space": "name",
            # Common aliases for description
            "desc": "description",
            "summary": "description",
            "note": "description",
            "comment": "description",
            # Common aliases for location
            "site": "location",
            "datacenter": "location",
            "facility": "location",
            # Common aliases for tags
            "tag": "tags",
            "label": "tags",
            "labels": "tags",
        }

        # Valid GraphQL fields that can be used in namespaces query
        self.valid_fields = {
            "name",
            "description", 
            "location",
            "tags",
            "created",
            "custom_field_data",
        }

        self.base_query = """
    query Namespaces(
        $get_id: Boolean = false,
        $get_description: Boolean = false,
        $get_location: Boolean = false,
        $get_tags: Boolean = false,
        $variable_value: [String],
        ) 
    {
      namespaces (enter_variable_name_here: $variable_value) 
      {
        id @include(if: $get_id)
        name
        description @include(if: $get_description)
        location @include(if: $get_location) {
            id @include(if: $get_id)
            name
        }
        tags @include(if: $get_tags) {
            id @include(if: $get_id)
            name
        }
      }
    }"""
        super().__init__()

    def get_tool_name(self) -> str:
        return "query_namespaces_dynamic"

    def get_description(self) -> str:
        return "Query namespaces with dynamic filtering by any property (name, description, location, tags). Automatically maps common field aliases (namespace→name, desc→description, site→location, etc.)"

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
                    "description": "Natural language query (e.g., 'show namespace Global', 'namespaces with description production', 'show all namespaces')",
                },
                "variable_name": {
                    "type": "string",
                    "description": "Manual: The namespace property to filter by (e.g., 'name', 'description', 'location', 'tags', 'cf_fieldname' for custom fields). Common aliases are automatically mapped: 'namespace' → 'name', 'desc' → 'description', 'site' → 'location', etc.",
                },
                "variable_value": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Manual: The value(s) to filter by",
                },
                "get_id": {"type": "boolean", "default": False},
                "get_description": {"type": "boolean", "default": False},
                "get_location": {"type": "boolean", "default": False},
                "get_tags": {"type": "boolean", "default": False},
            },
            required=[],
        )

    def _is_custom_field(self, field_name: str) -> bool:
        """Check if the field name is a custom field (starts with cf_)"""
        return field_name.startswith("cf_")

    def _map_field_name(self, field_name: str) -> str:
        """Map an alternate/incorrect field name to the correct GraphQL field name"""
        return self.field_mappings.get(field_name.lower(), field_name)

    def _is_valid_field(self, field_name: str) -> bool:
        """Check if a field name is valid for namespace queries"""
        return field_name in self.valid_fields or self._is_custom_field(field_name)

    def _suggest_field_name(self, invalid_field: str) -> str:
        """Suggest the correct field name for an invalid field"""
        invalid_lower = invalid_field.lower()

        # Check if it's a known mapping
        if invalid_lower in self.field_mappings:
            return self.field_mappings[invalid_lower]

        # Use fuzzy matching to suggest similar field names
        import difflib

        # Find closest matches
        matches = difflib.get_close_matches(
            invalid_lower, [f.lower() for f in self.valid_fields], n=3, cutoff=0.4
        )

        if matches:
            return matches[0]

        return "name"  # Default fallback for namespaces

    def _remove_filtering(self, query: str) -> str:
        """Remove the filtering clause from the query to fetch all records"""
        # Replace the filtered query with an unfiltered one
        query = query.replace(
            "namespaces (enter_variable_name_here: $variable_value)", "namespaces"
        )
        # Remove the variable declaration
        query = query.replace("$variable_value: [String],", "")
        return query

    def _execute_graphql(self, client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL query with dynamic variable replacement"""

        # Check if we have a prompt to parse
        if "prompt" in arguments:
            parsed = parse_namespace_prompt(arguments["prompt"])
            # Merge parsed parameters with existing arguments
            for key, value in parsed.items():
                if key not in arguments or arguments[key] is None:
                    arguments[key] = value

        # Check if this is a "show all" query
        if arguments.get("show_all"):
            query = self._remove_filtering(self.base_query)
            # Remove variable_value from arguments since it's not needed
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

            # Sanitize the input value
            if not sanitize_query_input("namespace", variable_value):
                raise ValueError(
                    f"Invalid or potentially malicious input detected: {variable_value}"
                )

            # Map field name if it's an alternate/incorrect name
            original_field_name = variable_name
            mapped_field_name = self._map_field_name(variable_name)

            # Validate field name and provide suggestions if invalid
            if not self._is_valid_field(mapped_field_name):
                suggested_field = self._suggest_field_name(original_field_name)
                available_fields = sorted(self.valid_fields)
                raise ValueError(
                    f"Invalid field name: '{original_field_name}'. "
                    f"Did you mean '{suggested_field}'? "
                    f"Available fields: {', '.join(available_fields)}. "
                    f"For custom fields, use 'cf_fieldname' format."
                )

            # Log field mapping if it occurred
            if mapped_field_name != original_field_name:
                logger.info(
                    f"Mapped field '{original_field_name}' to '{mapped_field_name}'"
                )

            # Use the mapped field name
            variable_name = mapped_field_name

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