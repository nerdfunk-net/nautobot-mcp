"""
Prompt parser for dynamic device type queries
"""

import re
from typing import Dict, Any, Optional, List, Tuple


class DeviceTypePromptParser:
    """Parser for converting natural language prompts into device type query parameters"""

    # Mapping of common prompt terms to GraphQL field names
    FIELD_MAPPINGS = {
        "model": "model",
        "name": "model",
        "device_model": "model",
        "device_name": "model",
        "type": "model",
        "device_type": "model",
        "manufacturer": "manufacturer",
        "vendor": "manufacturer",
        "make": "manufacturer",
        "brand": "manufacturer",
        "mfg": "manufacturer",
        "mfr": "manufacturer",
        "oem": "manufacturer",
        "company": "manufacturer",
    }

    # Boolean fields to enable based on query content
    FIELD_ENABLERS = {
        "model": ["get_model"],
        "name": ["get_model"],
        "device_model": ["get_model"],
        "device_name": ["get_model"],
        "type": ["get_model"],
        "device_type": ["get_model"],
        "manufacturer": ["get_manufacturer"],
        "vendor": ["get_manufacturer"],
        "make": ["get_manufacturer"],
        "brand": ["get_manufacturer"],
        "mfg": ["get_manufacturer"],
        "mfr": ["get_manufacturer"],
        "oem": ["get_manufacturer"],
        "company": ["get_manufacturer"],
    }

    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Parse a natural language prompt into query parameters

        Examples:
        - "show all device types" -> {'show_all': True}
        - "device types with model c9300" -> {'variable_name': 'model', 'variable_value': ['c9300']}
        - "device types with manufacturer cisco" -> {'variable_name': 'manufacturer', 'variable_value': ['cisco']}
        - "device types with vendor contains hp" -> {'variable_name': 'manufacturer', 'variable_value': ['hp']}
        """
        prompt_lower = prompt.lower().strip()

        # Initialize result
        result = {}

        # Parse main device type filter
        variable_name, variable_value = self._extract_main_filter(prompt_lower)
        if variable_name and variable_value:
            if variable_name == "show_all":
                result["show_all"] = True
            else:
                result["variable_name"] = variable_name
                result["variable_value"] = variable_value

        # Enable relevant boolean fields
        enabled_fields = self._determine_enabled_fields(prompt_lower, result)
        result.update(enabled_fields)

        return result

    def _extract_main_filter(
        self, prompt: str
    ) -> Tuple[Optional[str], Optional[List[str]]]:
        """Extract the main device type filter from prompt"""

        # Check for "show all" patterns first
        if (
            "show all device types" in prompt
            or "list all device types" in prompt
            or "get all device types" in prompt
            or prompt in ["all device types", "device types"]
        ):
            return "show_all", ["true"]  # Special marker for show all

        # Pattern: "device types with <field> <operator> <value>" - Enhanced for lookup expressions
        field_lookup_match = re.search(
            r"device\s+types?\s+(?:with|having)\s+(\w+)\s+((?:not\s+)?(?:equal|contains|includes|starts\s+with|begins\s+with|ends\s+with|exact|regex|regexp|regular\s+expression)(?:\s+to)?)\s+(.+)",
            prompt,
        )
        if field_lookup_match:
            field_term = field_lookup_match.group(1)
            field_lookup_match.group(2).strip()
            value = field_lookup_match.group(3).strip()

            # Handle custom fields directly (cf_fieldname)
            if field_term.startswith("cf_"):
                return field_term, [value]

            if field_term in self.FIELD_MAPPINGS:
                # For now, we'll use basic field mapping - can be enhanced later for lookup expressions
                return self.FIELD_MAPPINGS[field_term], [value]

        # Pattern: "device types with <field> <value>" or "device types by <field> <value>"
        field_match = re.search(
            r"device\s+types?\s+(?:with|by|having)\s+(\w+)\s+(\w+)", prompt
        )
        if field_match:
            field_term = field_match.group(1)
            value = field_match.group(2)

            # Handle custom fields directly (cf_fieldname)
            if field_term.startswith("cf_"):
                return field_term, [value]

            if field_term in self.FIELD_MAPPINGS:
                return self.FIELD_MAPPINGS[field_term], [value]

        # Pattern: "show <field> <value>"
        show_match = re.search(r"show\s+(\w+)\s+(.+)", prompt)
        if show_match:
            field_term = show_match.group(1)
            value = show_match.group(2).strip()

            # Handle custom fields directly (cf_fieldname)
            if field_term.startswith("cf_"):
                return field_term, [value]

            if field_term in self.FIELD_MAPPINGS:
                return self.FIELD_MAPPINGS[field_term], [value]

        return None, None

    def _determine_enabled_fields(
        self, prompt: str, parsed_result: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Determine which boolean fields should be enabled based on prompt content"""
        enabled = {}

        # Default fields - always show model and manufacturer
        enabled["get_model"] = True
        enabled["get_manufacturer"] = True

        # Enable fields based on variable name
        if "variable_name" in parsed_result:
            var_name = parsed_result["variable_name"]

            # Handle custom fields - enable custom field data retrieval
            if var_name.startswith("cf_"):
                enabled["get_custom_field_data"] = True
                enabled["get__custom_field_data"] = True

            for key, enablers in self.FIELD_ENABLERS.items():
                if key in var_name or var_name in key:
                    for enabler in enablers:
                        enabled[enabler] = True

        # Enable fields based on prompt keywords
        for keyword, enablers in self.FIELD_ENABLERS.items():
            if keyword in prompt:
                for enabler in enablers:
                    enabled[enabler] = True

        # Special cases based on prompt content
        if "model" in prompt or "name" in prompt:
            enabled["get_model"] = True

        if "manufacturer" in prompt or "vendor" in prompt or "make" in prompt:
            enabled["get_manufacturer"] = True

        # Special cases for comprehensive queries
        if "all" in prompt and ("properties" in prompt or "details" in prompt):
            enabled["get_model"] = True
            enabled["get_manufacturer"] = True

        return enabled


def parse_device_type_prompt(prompt: str) -> Dict[str, Any]:
    """Convenience function to parse a device type prompt"""
    parser = DeviceTypePromptParser()
    return parser.parse_prompt(prompt)
