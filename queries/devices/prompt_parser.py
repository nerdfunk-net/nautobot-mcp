"""
Prompt parser for dynamic device queries
"""

import re
from typing import Dict, Any, Optional, List, Tuple

class DevicePromptParser:
    """Parser for converting natural language prompts into device query parameters"""
    
    # Supported lookup expressions for string fields
    LOOKUP_EXPRESSIONS = {
        'not_equal': '__n',
        'contains': '__ic', 
        'not_contains': '__nic',
        'starts_with': '__isw',
        'not_starts_with': '__nisw', 
        'ends_with': '__iew',
        'not_ends_with': '__niew',
        'exact_case_insensitive': '__ie',
        'not_exact_case_insensitive': '__nie',
        'regex': '__re',
        'not_regex': '__nre',
        'regex_case_insensitive': '__ire',
        'not_regex_case_insensitive': '__nire',
        'is_null': '__isnull'
    }
    
    # Mapping of natural language terms to lookup expressions
    LOOKUP_TERMS = {
        'not equal': '__n',
        'not equals': '__n',
        '!=': '__n',
        'contains': '__ic',
        'includes': '__ic',
        'not contains': '__nic',
        'not includes': '__nic',
        'starts with': '__isw',
        'begins with': '__isw',
        'not starts with': '__nisw', 
        'not begins with': '__nisw',
        'ends with': '__iew',
        'not ends with': '__niew',
        'exact': '__ie',
        'exactly': '__ie',
        'not exact': '__nie',
        'not exactly': '__nie',
        'regex': '__re',
        'regexp': '__re',
        'regular expression': '__re',
        'not regex': '__nre',
        'not regexp': '__nre',
        'case insensitive regex': '__ire',
        'not case insensitive regex': '__nire',
        'is null': '__isnull',
        'is empty': '__isnull'
    }
    
    # Mapping of common prompt terms to GraphQL field names
    FIELD_MAPPINGS = {
        'name': 'name',
        'device': 'name',
        'hostname': 'name',
        'location': 'location',
        'site': 'location', 
        'role': 'role',
        'device_role': 'role',
        'platform': 'platform',
        'manufacturer': 'device_type__manufacturer',
        'device_type': 'device_type',
        'model': 'device_type',
        'tag': 'tags',
        'tags': 'tags',
        'tenant': 'tenant',
        'status': 'status',
        'rack': 'rack',
        'serial': 'serial',
        'asset_tag': 'asset_tag'
    }
    
    # Interface-specific field mappings
    INTERFACE_MAPPINGS = {
        'interface': 'name',
        'interface_name': 'name',
        'interface_type': 'type',
        'port': 'name'
    }
    
    # Boolean fields to enable based on query content
    FIELD_ENABLERS = {
        'name': ['get_name'],
        'hostname': ['get_name'],
        'location': ['get_location'],
        'role': ['get_role'],
        'platform': ['get_platform'],
        'device_type': ['get_device_type'],
        'tags': ['get_tags'],
        'tenant': ['get_tenant'],
        'status': ['get_status'],
        'rack': ['get_rack'],
        'serial': ['get_serial'],
        'asset_tag': ['get_asset_tag'],
        'ip': ['get_primary_ip4'],
        'ip address': ['get_primary_ip4'],
        'ip_address': ['get_primary_ip4'],
        'primary ip': ['get_primary_ip4'],
        'interface': ['get_interfaces']
    }
    
    def _parse_lookup_expression(self, field_term: str, operator_term: str) -> Tuple[str, str]:
        """Parse field and operator terms into GraphQL field name with lookup expression"""
        base_field = self.FIELD_MAPPINGS.get(field_term, field_term)
        lookup_suffix = self.LOOKUP_TERMS.get(operator_term, '')
        return base_field + lookup_suffix, operator_term
    
    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Parse a natural language prompt into query parameters
        
        Examples:
        - "show device router1" -> {'variable_name': 'name', 'variable_value': ['router1']}
        - "show all devices in location datacenter1" -> {'variable_name': 'location', 'variable_value': ['datacenter1']}
        - "devices with role firewall" -> {'variable_name': 'role', 'variable_value': ['firewall']}
        - "devices with name contains router" -> {'variable_name': 'name__ic', 'variable_value': ['router']}
        - "devices with name not equal router1" -> {'variable_name': 'name__n', 'variable_value': ['router1']}
        - "devices with hostname starts with core" -> {'variable_name': 'name__isw', 'variable_value': ['core']}
        - "show the name and the IP address of all devices in location lab" -> {'variable_name': 'location', 'variable_value': ['lab'], 'get_name': True, 'get_primary_ip4': True}
        """
        prompt_lower = prompt.lower().strip()
        
        # Initialize result
        result = {}
        
        # Parse main device filter
        variable_name, variable_value = self._extract_main_filter(prompt_lower)
        if variable_name and variable_value:
            if variable_name == 'show_all':
                result['show_all'] = True
            else:
                result['variable_name'] = variable_name
                result['variable_value'] = variable_value
            
        # Parse interface filter if present
        interface_var, interface_val = self._extract_interface_filter(prompt_lower)
        if interface_var and interface_val:
            result['interface_variable'] = interface_var
            result['interface_value'] = interface_val
            
        # Enable relevant boolean fields
        enabled_fields = self._determine_enabled_fields(prompt_lower, result)
        result.update(enabled_fields)
        
        return result
    
    def _extract_main_filter(self, prompt: str) -> Tuple[Optional[str], Optional[List[str]]]:
        """Extract the main device filter from prompt"""
        
        # Check for "show all" patterns first
        if ("show all devices" in prompt or 
            "list all devices" in prompt or 
            "get all devices" in prompt or
            prompt in ["all devices", "devices"]):
            return 'show_all', ['true']  # Special marker for show all
        
        # Pattern: "show device <name>" or "show all properties of device <name>"
        device_name_match = re.search(r'(?:show|get|find)(?:\s+all\s+properties\s+of)?\s+device\s+(\w+)', prompt)
        if device_name_match:
            return 'name', [device_name_match.group(1)]
        
        # Pattern: "devices with <field> <lookup_operator> <value>" - Enhanced for lookup expressions
        # Match patterns like "devices with name contains router", "devices with hostname not equal test"
        field_lookup_match = re.search(r'devices?\s+(?:with|having)\s+(\w+)\s+((?:not\s+)?(?:equal|contains|includes|starts\s+with|begins\s+with|ends\s+with|exact|regex|regexp|regular\s+expression|case\s+insensitive\s+regex)(?:\s+to)?)\s+(.+)', prompt)
        if field_lookup_match:
            field_term = field_lookup_match.group(1)
            operator_term = field_lookup_match.group(2).strip()
            value = field_lookup_match.group(3).strip()
            
            if field_term in self.FIELD_MAPPINGS:
                field_with_lookup, _ = self._parse_lookup_expression(field_term, operator_term)
                return field_with_lookup, [value]
        
        # Pattern: "devices with <field> <value>" or "devices in <field> <value>" - Original exact match
        field_match = re.search(r'devices?\s+(?:with|in|at|by)\s+(\w+)\s+(\w+)', prompt)
        if field_match:
            field_term = field_match.group(1)
            value = field_match.group(2)
            
            if field_term in self.FIELD_MAPPINGS:
                return self.FIELD_MAPPINGS[field_term], [value]
        
        # Pattern: "show all devices in location <name>"
        location_match = re.search(r'(?:in|at)\s+location\s+(\w+)', prompt)
        if location_match:
            return 'location', [location_match.group(1)]
            
        # Pattern: "devices with role <role>"
        role_match = re.search(r'(?:with|having)\s+role\s+(\w+)', prompt)
        if role_match:
            return 'role', [role_match.group(1)]
            
        # Pattern: "show <field> <value>"
        show_match = re.search(r'show\s+(\w+)\s+(\w+)', prompt)
        if show_match:
            field_term = show_match.group(1)
            value = show_match.group(2)
            
            if field_term in self.FIELD_MAPPINGS:
                return self.FIELD_MAPPINGS[field_term], [value]
        
        return None, None
    
    def _extract_interface_filter(self, prompt: str) -> Tuple[Optional[str], Optional[List[str]]]:
        """Extract interface filter from prompt"""
        
        # Pattern: "with interface <name>"
        interface_match = re.search(r'(?:with|having)\s+interface\s+(\w+)', prompt)
        if interface_match:
            return 'name', [interface_match.group(1)]
            
        # Pattern: "interface <name>"
        interface_direct = re.search(r'interface\s+(\w+)', prompt)
        if interface_direct:
            return 'name', [interface_direct.group(1)]
        
        return None, None
    
    def _determine_enabled_fields(self, prompt: str, parsed_result: Dict[str, Any]) -> Dict[str, bool]:
        """Determine which boolean fields should be enabled based on prompt content"""
        enabled = {}
        
        # Always enable hostname by default
        
        # Enable fields based on variable name
        if 'variable_name' in parsed_result:
            var_name = parsed_result['variable_name']
            for key, enablers in self.FIELD_ENABLERS.items():
                if key in var_name or var_name in key:
                    for enabler in enablers:
                        enabled[enabler] = True
        
        # Enable fields based on prompt keywords
        for keyword, enablers in self.FIELD_ENABLERS.items():
            if keyword in prompt:
                for enabler in enablers:
                    enabled[enabler] = True
        
        # Special cases
        if 'all properties' in prompt or 'show all' in prompt:
            # Enable most fields for comprehensive queries
            comprehensive_fields = [
                'get_name', 'get_location', 'get_role',
                'get_device_type', 'get_platform', 'get_status', 'get_tags'
            ]
            for field in comprehensive_fields:
                enabled[field] = True
        
        if 'interface' in prompt:
            enabled['get_interfaces'] = True
        
        return enabled

def parse_device_prompt(prompt: str) -> Dict[str, Any]:
    """Convenience function to parse a device prompt"""
    parser = DevicePromptParser()
    return parser.parse_prompt(prompt)