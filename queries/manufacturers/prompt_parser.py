"""
Prompt parser for dynamic manufacturer queries
"""

import re
from typing import Dict, Any, Optional, List, Tuple

class ManufacturerPromptParser:
    """Parser for converting natural language prompts into manufacturer query parameters"""
    
    # Mapping of common prompt terms to GraphQL field names
    FIELD_MAPPINGS = {
        'name': 'name',
        'manufacturer': 'name',
        'manufacturer_name': 'name',
        'vendor': 'name',
        'make': 'name',
        'brand': 'name',
        'company': 'name',
        'mfg': 'name',
        'mfr': 'name',
        'oem': 'name',
        'description': 'description',
        'desc': 'description',
        'summary': 'description'
    }
    
    # Boolean fields to enable based on query content
    FIELD_ENABLERS = {
        'name': ['get_name'],
        'manufacturer': ['get_name'],
        'manufacturer_name': ['get_name'],
        'vendor': ['get_name'],
        'make': ['get_name'],
        'brand': ['get_name'],
        'company': ['get_name'],
        'mfg': ['get_name'],
        'mfr': ['get_name'],
        'oem': ['get_name'],
        'description': ['get_description'],
        'desc': ['get_description'],
        'summary': ['get_description'],
        'device_types': ['get_device_types'],
        'devices': ['get_device_types'],
        'models': ['get_device_types']
    }
    
    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Parse a natural language prompt into query parameters
        
        Examples:
        - "show all manufacturers" -> {'show_all': True}
        - "manufacturers with name cisco" -> {'variable_name': 'name', 'variable_value': ['cisco']}
        - "vendors with description contains network" -> {'variable_name': 'description', 'variable_value': ['network']}
        """
        prompt_lower = prompt.lower().strip()
        
        # Initialize result
        result = {}
        
        # Parse main manufacturer filter
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
        """Extract the main manufacturer filter from prompt"""
        
        # Check for "show all" patterns first
        if (any(pattern in prompt for pattern in [
            "show all manufacturers", "list all manufacturers", "get all manufacturers", 
            "all manufacturers", "show manufacturers"]) or prompt == "manufacturers"):
            return 'show_all', ['true']  # Special marker for show all
        
        # Pattern: "manufacturers with <field> <operator> <value>" - Enhanced for lookup expressions
        field_lookup_match = re.search(r'(?:manufacturers?|vendors?)\\s+(?:with|having)\\s+(\\w+)\\s+((?:not\\s+)?(?:equal|contains|includes|starts\\s+with|begins\\s+with|ends\\s+with|exact|regex|regexp|regular\\s+expression)(?:\\s+to)?)\\s+(.+)', prompt)
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
        
        # Pattern: "manufacturers with <field> <value>" or "manufacturers by <field> <value>"
        field_match = re.search(r'(?:manufacturers?|vendors?)\\s+(?:with|by|having)\\s+(\\w+)\\s+(\\w+)', prompt)
        if field_match:
            field_term = field_match.group(1)
            value = field_match.group(2)
            
            # Handle custom fields directly (cf_fieldname)
            if field_term.startswith('cf_'):
                return field_term, [value]
            
            if field_term in self.FIELD_MAPPINGS:
                return self.FIELD_MAPPINGS[field_term], [value]
        
        # Pattern: "show manufacturer <value>" or "show <field> <value>"
        show_match = re.search(r'show\\s+(?:manufacturer\\s+|vendor\\s+)?(\\w+)\\s*(?:\\s+(\\w+))?', prompt)
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
                # Single term - assume it's a manufacturer name
                return 'name', [first_term]
        
        return None, None
    
    def _determine_enabled_fields(self, prompt: str, parsed_result: Dict[str, Any]) -> Dict[str, bool]:
        """Determine which boolean fields should be enabled based on prompt content"""
        enabled = {}
        
        # Default fields - always show name
        enabled['get_name'] = True
        
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
        if 'description' in prompt or 'desc' in prompt:
            enabled['get_description'] = True
            
        if any(word in prompt for word in ['device_types', 'devices', 'models']):
            enabled['get_device_types'] = True
        
        # Special cases for comprehensive queries
        if 'all' in prompt and ('properties' in prompt or 'details' in prompt):
            enabled['get_name'] = True
            enabled['get_description'] = True
            enabled['get_device_types'] = True
        
        return enabled

def parse_manufacturer_prompt(prompt: str) -> Dict[str, Any]:
    """Convenience function to parse a manufacturer prompt"""
    parser = ManufacturerPromptParser()
    return parser.parse_prompt(prompt)