"""
Prompt parser for dynamic interface queries
"""

import re
from typing import Dict, Any, Optional, List, Tuple

class InterfacePromptParser:
    """Parser for converting natural language prompts into interface query parameters"""
    
    # Mapping of common prompt terms to GraphQL field names
    FIELD_MAPPINGS = {
        'name': 'name',
        'interface': 'name',
        'interface_name': 'name',
        'port': 'name',
        'port_name': 'name',
        'description': 'description',
        'desc': 'description',
        'summary': 'description',
        'enabled': 'enabled',
        'active': 'enabled',
        'status': 'status',
        'state': 'status',
        'role': 'role',
        'type': 'type',
        'interface_type': 'type',
        'port_type': 'type',
        'label': 'label',
        'device': 'device',
        'device_name': 'device',
        'host': 'device',
        'hostname': 'device',
        'tags': 'tags',
        'tag': 'tags'
    }
    
    # Boolean fields to enable based on query content
    FIELD_ENABLERS = {
        'name': ['get_name'],
        'interface': ['get_name'],
        'interface_name': ['get_name'],
        'port': ['get_name'],
        'port_name': ['get_name'],
        'description': ['get_description'],
        'desc': ['get_description'],
        'summary': ['get_description'],
        'enabled': ['get_enabled'],
        'active': ['get_enabled'],
        'status': ['get_status'],
        'state': ['get_status'],
        'role': ['get_role'],
        'type': ['get_type'],
        'interface_type': ['get_type'],
        'port_type': ['get_type'],
        'label': ['get_label'],
        'device': ['get_device'],
        'device_name': ['get_device'],
        'host': ['get_device'],
        'hostname': ['get_device'],
        'tags': ['get_tags'],
        'tag': ['get_tags'],
        'redundancy': ['get_interface_redundancy_groups'],
        'redundancy_groups': ['get_interface_redundancy_groups']
    }
    
    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Parse a natural language prompt into query parameters
        
        Examples:
        - "show all interfaces" -> {'show_all': True}
        - "interfaces with name eth0" -> {'variable_name': 'name', 'variable_value': ['eth0']}
        - "interfaces on device router1" -> {'variable_name': 'device', 'variable_value': ['router1']}
        - "active interfaces" -> {'variable_name': 'enabled', 'variable_value': ['true']}
        """
        prompt_lower = prompt.lower().strip()
        
        # Initialize result
        result = {}
        
        # Parse main interface filter
        variable_name, variable_value = self._extract_main_filter(prompt_lower)
        if variable_name and variable_value:
            if variable_name == 'show_all':
                result['show_all'] = True
            else:
                result['variable_name'] = variable_name
                result['variable_value'] = variable_value
            
        # Enable relevant boolean fields
        enabled_fields = self._determine_enabled_fields(prompt_lower, result)
        result.update(enabled_fields)
        
        return result
    
    def _extract_main_filter(self, prompt: str) -> Tuple[Optional[str], Optional[List[str]]]:
        """Extract the main interface filter from prompt"""
        
        # Check for "show all" patterns first
        if (any(pattern in prompt for pattern in [
            "show all interfaces", "list all interfaces", "get all interfaces", 
            "all interfaces", "show interfaces"]) or prompt == "interfaces"):
            return 'show_all', ['true']  # Special marker for show all
        
        # Special patterns for enabled/active interfaces
        if any(pattern in prompt for pattern in ["active interfaces", "enabled interfaces"]):
            return 'enabled', ['true']
        
        if any(pattern in prompt for pattern in ["disabled interfaces", "inactive interfaces"]):
            return 'enabled', ['false']
        
        # Pattern: "interfaces on <device>" or "interfaces for <device>"
        device_match = re.search(r'interfaces\\s+(?:on|for|of)\\s+(\\w+)', prompt)
        if device_match:
            device_name = device_match.group(1)
            return 'device', [device_name]
        
        # Pattern: "interfaces with <field> <operator> <value>" - Enhanced for lookup expressions
        field_lookup_match = re.search(r'interfaces?\\s+(?:with|having)\\s+(\\w+)\\s+((?:not\\s+)?(?:equal|contains|includes|starts\\s+with|begins\\s+with|ends\\s+with|exact|regex|regexp|regular\\s+expression)(?:\\s+to)?)\\s+(.+)', prompt)
        if field_lookup_match:
            field_term = field_lookup_match.group(1)
            operator_term = field_lookup_match.group(2).strip()
            value = field_lookup_match.group(3).strip()
            
            # Handle custom fields directly (cf_fieldname)
            if field_term.startswith('cf_'):
                return field_term, [value]
                
            if field_term in self.FIELD_MAPPINGS:
                # For now, we'll use basic field mapping - can be enhanced later for lookup expressions
                return self.FIELD_MAPPINGS[field_term], [value]
        
        # Pattern: "interfaces with <field> <value>" or "interfaces by <field> <value>"
        field_match = re.search(r'interfaces?\\s+(?:with|by|having)\\s+(\\w+)\\s+(\\w+)', prompt)
        if field_match:
            field_term = field_match.group(1)
            value = field_match.group(2)
            
            # Handle custom fields directly (cf_fieldname)
            if field_term.startswith('cf_'):
                return field_term, [value]
            
            if field_term in self.FIELD_MAPPINGS:
                return self.FIELD_MAPPINGS[field_term], [value]
        
        # Pattern: "show interface <value>" or "show <field> <value>"
        show_match = re.search(r'show\\s+(?:interface\\s+|port\\s+)?(\\w+)\\s*(?:\\s+(\\w+))?', prompt)
        if show_match:
            first_term = show_match.group(1)
            second_term = show_match.group(2)
            
            # If we have two terms, first is field, second is value
            if second_term:
                field_term = first_term
                value = second_term
                
                # Handle custom fields directly (cf_fieldname)
                if field_term.startswith('cf_'):
                    return field_term, [value]
                    
                if field_term in self.FIELD_MAPPINGS:
                    return self.FIELD_MAPPINGS[field_term], [value]
            else:
                # Single term - assume it's an interface name
                return 'name', [first_term]
        
        return None, None
    
    def _determine_enabled_fields(self, prompt: str, parsed_result: Dict[str, Any]) -> Dict[str, bool]:
        """Determine which boolean fields should be enabled based on prompt content"""
        enabled = {}
        
        # Default fields - always show basic interface info
        enabled['get_name'] = True
        enabled['get_device'] = True
        enabled['get_status'] = True
        
        # Enable fields based on variable name
        if 'variable_name' in parsed_result:
            var_name = parsed_result['variable_name']
            
            # Handle custom fields - enable custom field data retrieval
            if var_name.startswith('cf_'):
                enabled['get_custom_field_data'] = True
                enabled['get__custom_field_data'] = True
            
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
        if any(word in prompt for word in ['description', 'desc']):
            enabled['get_description'] = True
            
        if any(word in prompt for word in ['enabled', 'active', 'disabled', 'inactive']):
            enabled['get_enabled'] = True
            
        if any(word in prompt for word in ['type', 'interface_type', 'port_type']):
            enabled['get_type'] = True
            
        if any(word in prompt for word in ['role']):
            enabled['get_role'] = True
            
        if any(word in prompt for word in ['label']):
            enabled['get_label'] = True
            
        if any(word in prompt for word in ['tags', 'tag']):
            enabled['get_tags'] = True
            
        if any(word in prompt for word in ['redundancy', 'redundancy_groups']):
            enabled['get_interface_redundancy_groups'] = True
        
        # Special cases for comprehensive queries
        if 'all' in prompt and ('properties' in prompt or 'details' in prompt):
            enabled.update({
                'get_name': True,
                'get_description': True,
                'get_enabled': True,
                'get_label': True,
                'get_type': True,
                'get_status': True,
                'get_role': True,
                'get_device': True,
                'get_tags': True,
                'get_interface_redundancy_groups': True
            })
        
        return enabled

def parse_interface_prompt(prompt: str) -> Dict[str, Any]:
    """Convenience function to parse an interface prompt"""
    parser = InterfacePromptParser()
    return parser.parse_prompt(prompt)