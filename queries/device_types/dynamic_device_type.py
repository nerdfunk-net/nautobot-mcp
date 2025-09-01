"""
Dynamic device type query module that supports variable replacement
"""

import logging
from typing import Dict, Any
from ..base import BaseQuery, QueryType, MatchType, ToolSchema
from .prompt_parser import parse_device_type_prompt

# Set up logger
logger = logging.getLogger(__name__)


class DynamicDeviceTypeQuery(BaseQuery):
    """Dynamic device type query that replaces placeholders based on user input"""

    def __init__(self):
        # Mapping of common incorrect/alternate field names to correct GraphQL field names
        self.field_mappings = {
            # Common aliases for model
            "device_model": "model",
            "name": "model",
            "device_name": "model",
            "type": "model",
            "device_type": "model",
            # Common aliases for manufacturer
            "vendor": "manufacturer",
            "make": "manufacturer",
            "brand": "manufacturer",
            "mfg": "manufacturer",
            "mfr": "manufacturer",
            "oem": "manufacturer",
            "company": "manufacturer",
        }

        # Valid GraphQL fields that can be used in device_types query
        self.valid_fields = {"model", "manufacturer"}

        self.base_query = """
    query DeviceTypes(
        $get_id: Boolean = false,
        $get_model: Boolean = true,
        $get_manufacturer: Boolean = false,
        $get_devices: Boolean = false,
        $variable_value: [String],
    ) {
    device_types (enter_variable_name_here: $variable_value) {
        id @include(if: $get_id)
        model @include(if: $get_model)
        manufacturer @include(if: $get_manufacturer) {
            id @include(if: $get_id)
            name
        }
        devices @include(if: $get_devices) {
            id @include(if: $get_id)
            name
        }
    }
    }"""
        super().__init__()

    def get_tool_name(self) -> str:
        return "query_device_types_dynamic"

    def get_description(self) -> str:
        return "Query device types with dynamic filtering by any property (model, manufacturer, etc.). Automatically maps common field aliases (name→model, vendor→manufacturer, etc.)"

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
                    "description": "Natural language query (e.g., 'show all device types', 'device types with model contains cisco')",
                },
                "variable_name": {
                    "type": "string",
                    "description": "Manual: The device type property to filter by (e.g., 'model', 'manufacturer', 'cf_fieldname' for custom fields). Common aliases are automatically mapped: 'name' → 'model', 'vendor' → 'manufacturer', etc.",
                },
                "variable_value": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Manual: The value(s) to filter by. For custom fields (cf_*), only the first value is used as a single string.",
                },
                "get_id": {"type": "boolean", "default": False},
                "get_model": {"type": "boolean", "default": True},
                "get_manufacturer": {"type": "boolean", "default": False},
                "get_devices": {"type": "boolean", "default": False},
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
        """Check if a field name is valid for device type queries"""
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

        return "model"  # Default fallback for device types

    def _modify_query_for_custom_field(self, query: str, variable_name: str) -> str:
        """Modify query for custom fields - use String instead of [String]"""
        if self._is_custom_field(variable_name):
            # Replace [String] with String for custom fields
            query = query.replace(
                "$variable_value: [String],", "$variable_value: String,"
            )
        return query

    def _remove_filtering(self, query: str) -> str:
        """Remove the filtering clause from the query to fetch all records"""
        # Replace the filtered query with an unfiltered one
        query = query.replace(
            "device_types (enter_variable_name_here: $variable_value)", "device_types"
        )
        # Remove the variable declaration
        query = query.replace("$variable_value: [String],", "")
        return query

    def _execute_graphql(self, client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL query with dynamic variable replacement"""

        # Check if we have a prompt to parse
        if "prompt" in arguments:
            parsed = parse_device_type_prompt(arguments["prompt"])
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

            # Start with the base query
            query = self.base_query

            # Replace the main variable placeholder
            query = query.replace("enter_variable_name_here", variable_name)

            # Handle custom fields - modify query to use String instead of [String]
            query = self._modify_query_for_custom_field(query, variable_name)

            # For custom fields, ensure variable_value is a single string, not an array
            if self._is_custom_field(variable_name) and isinstance(
                variable_value, list
            ):
                if len(variable_value) > 0:
                    # Take the first value for custom fields
                    arguments = arguments.copy()
                    arguments["variable_value"] = variable_value[0]

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
