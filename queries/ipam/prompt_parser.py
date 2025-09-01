"""
Prompt parser for dynamic IPAM queries
"""

import re
from typing import Dict, Any, Optional, List, Tuple


class IPAMPromptParser:
    """Parser for converting natural language prompts into IPAM query parameters"""

    # Mapping of common prompt terms to GraphQL field names
    FIELD_MAPPINGS = {
        "address": "address",
        "ip": "address",
        "ip_address": "address",
        "dns_name": "dns_name",
        "dns": "dns_name",
        "hostname": "dns_name",
        "description": "description",
        "type": "type",
        "status": "status",
        "host": "host",
        "mask_length": "mask_length",
        "mask": "mask_length",
        "ip_version": "ip_version",
        "version": "ip_version",
        "tag": "tags",
        "tags": "tags",
        "tenant": "tenant",
        "parent": "parent",
    }

    # Boolean fields to enable based on query content
    FIELD_ENABLERS = {
        "address": ["get_address"],
        "ip": ["get_address"],
        "ip_address": ["get_address"],
        "dns_name": ["get_dns_name"],
        "dns": ["get_dns_name"],
        "hostname": ["get_dns_name"],
        "description": ["get_description"],
        "type": ["get_type"],
        "status": ["get_status"],
        "host": ["get_host"],
        "mask_length": ["get_mask_length"],
        "mask": ["get_mask_length"],
        "ip_version": ["get_ip_version"],
        "version": ["get_ip_version"],
        "tags": ["get_tags"],
        "tenant": ["get_tenant"],
        "parent": ["get_parent"],
        "interface": ["get_interfaces"],
        "interfaces": ["get_interfaces"],
        "device": ["get_primary_ip4_for", "get_interfaces"],
        "location": ["get_location"],
    }

    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Parse a natural language prompt into query parameters

        Examples:
        - "show all ip addresses" -> {'show_all': True}
        - "show ip address 192.168.1.1" -> {'variable_name': 'address', 'variable_value': ['192.168.1.1']}
        - "ip addresses with dns_name contains server" -> {'variable_name': 'dns_name', 'variable_value': ['server']}
        - "ip addresses with type active" -> {'variable_name': 'type', 'variable_value': ['active']}
        - "ip addresses with cf_net production" -> {'variable_name': 'cf_net', 'variable_value': ['production']}
        """
        prompt_lower = prompt.lower().strip()

        # Initialize result
        result = {}

        # Parse main IP address filter
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
        """Extract the main IP address filter from prompt"""

        # Check for "show all" patterns first
        if (
            "show all ip addresses" in prompt
            or "list all ip addresses" in prompt
            or "get all ip addresses" in prompt
            or prompt in ["all ip addresses", "ip addresses"]
        ):
            return "show_all", ["true"]  # Special marker for show all

        # Pattern: "show ip address <address>" - matches IP addresses
        ip_match = re.search(
            r"(?:show|get|find)\s+(?:ip\s+address|address)\s+(\d+\.\d+\.\d+\.\d+)",
            prompt,
        )
        if ip_match:
            return "address", [ip_match.group(1)]

        # Pattern: "ip addresses with <field> <operator> <value>" - Enhanced for lookup expressions
        field_lookup_match = re.search(
            r"ip\s+addresses?\s+(?:with|having)\s+(\w+)\s+((?:not\s+)?(?:equal|contains|includes|starts\s+with|begins\s+with|ends\s+with|exact|regex|regexp|regular\s+expression)(?:\s+to)?)\s+(.+)",
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

        # Pattern: "ip addresses with <field> <value>" or "ip addresses by <field> <value>"
        field_match = re.search(
            r"ip\s+addresses?\s+(?:with|by|having)\s+(\w+)\s+(\w+)", prompt
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

        # Default fields - always show address
        enabled["get_address"] = True

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
        if "dns" in prompt or "hostname" in prompt:
            enabled["get_dns_name"] = True

        if "status" in prompt:
            enabled["get_status"] = True

        if "type" in prompt:
            enabled["get_type"] = True

        if "description" in prompt:
            enabled["get_description"] = True

        if "interface" in prompt:
            enabled["get_interfaces"] = True

        if "device" in prompt:
            enabled["get_primary_ip4_for"] = True
            enabled["get_interfaces"] = True

        if "parent" in prompt or "prefix" in prompt:
            enabled["get_parent"] = True

        if "tag" in prompt:
            enabled["get_tags"] = True

        # Special cases for comprehensive queries
        if "all" in prompt and ("properties" in prompt or "details" in prompt):
            comprehensive_fields = [
                "get_address",
                "get_dns_name",
                "get_type",
                "get_status",
                "get_description",
                "get_parent",
                "get_tags",
            ]
            for field in comprehensive_fields:
                enabled[field] = True

        return enabled


def parse_ipam_prompt(prompt: str) -> Dict[str, Any]:
    """Convenience function to parse an IPAM prompt"""
    parser = IPAMPromptParser()
    return parser.parse_prompt(prompt)
