"""
Dynamic secrets groups query module that supports variable replacement
"""

import logging
from typing import Dict, Any
from ..base import BaseQuery, QueryType, MatchType, ToolSchema
from .prompt_parser import parse_secrets_group_prompt
from ..sanitizer import sanitize_query_input

# Set up logger
logger = logging.getLogger(__name__)


class DynamicSecretsGroupQuery(BaseQuery):
    """Dynamic secrets groups query that replaces placeholders based on user input"""

    def __init__(self):
        # Mapping of common incorrect/alternate field names to correct GraphQL field names
        self.field_mappings = {
            # Common aliases for secrets group name
            "secrets_group": "name",
            "group": "name",
            "group_name": "name",
            "secret_group": "name",
            "auth_group": "name",
            "credential_group": "name",
            # Common aliases for description
            "desc": "description",
            "summary": "description",
            "note": "description",
            "comment": "description",
            # Common aliases for secrets
            "secret": "secrets",
            "credential": "secrets",
            "credentials": "secrets",
            "auth": "secrets",
        }

        # Valid GraphQL fields that can be used in secrets groups query
        self.valid_fields = {
            "name",
            "description",
            "secrets",
            "created",
            "custom_field_data",
        }

        self.base_query = """
    query SecretsGroups(
        $get_id: Boolean = false,
        $get_description: Boolean = false,
        $get_secrets: Boolean = false,
        $variable_value: [String],
        ) 
    {
      secrets_groups (enter_variable_name_here: $variable_value)
      {
        id @include(if: $get_id)
        name
        description @include(if: $get_description)
        secrets @include(if: $get_secrets) {
            id @include(if: $get_id)
            name
            description
        }
      }
    }"""
        super().__init__()

    def get_tool_name(self) -> str:
        return "query_secrets_groups_dynamic"

    def get_description(self) -> str:
        return "Query secrets groups with dynamic filtering by any property (name, description, secrets). Automatically maps common field aliases (group→name, desc→description, credential→secrets, etc.)"

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
                    "description": "Natural language query (e.g., 'show secrets group production', 'groups with description test', 'show all secrets groups')",
                },
                "variable_name": {
                    "type": "string",
                    "description": "Manual: The secrets group property to filter by (e.g., 'name', 'description', 'secrets', 'cf_fieldname' for custom fields). Common aliases are automatically mapped: 'group' → 'name', 'desc' → 'description', 'credential' → 'secrets', etc.",
                },
                "variable_value": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Manual: The value(s) to filter by",
                },
                "get_id": {"type": "boolean", "default": False},
                "get_description": {"type": "boolean", "default": False},
                "get_secrets": {"type": "boolean", "default": False},
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
        """Check if a field name is valid for secrets groups queries"""
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

        return "name"  # Default fallback for secrets groups

    def _remove_filtering(self, query: str) -> str:
        """Remove the filtering clause from the query to fetch all records"""
        # Replace the filtered query with an unfiltered one
        query = query.replace(
            "secrets_groups (enter_variable_name_here: $variable_value)", "secrets_groups"
        )
        # Remove the variable declaration
        query = query.replace("$variable_value: [String],", "")
        return query

    def _execute_graphql(self, client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL query with dynamic variable replacement"""

        # Check if we have a prompt to parse
        if "prompt" in arguments:
            parsed = parse_secrets_group_prompt(arguments["prompt"])
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
            if not sanitize_query_input("secrets_group", variable_value):
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