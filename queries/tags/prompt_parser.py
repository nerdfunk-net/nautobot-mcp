"""
Prompt parser for dynamic tag queries
"""

import re
from typing import Dict, Any, Optional, List, Tuple

class TagPromptParser:
    """Parser for converting natural language prompts into tag query parameters"""
    
    # Mapping of common prompt terms to GraphQL field names
    FIELD_MAPPINGS = {
        'name': 'name',
        'tag': 'name',
        'tag_name': 'name',
        'title': 'name',
        'description': 'description',
        'desc': 'description',
        'summary': 'description'
    }
    
    # Boolean fields to enable based on query content
    FIELD_ENABLERS = {
        'name': ['get_name'],
        'tag': ['get_name'],
        'tag_name': ['get_name'],
        'title': ['get_name'],
        'description': ['get_description'],
        'desc': ['get_description'],
        'summary': ['get_description'],
        'content_types': ['get_content_types'],
        'models': ['get_content_types']
    }
    
    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Parse a natural language prompt into query parameters
        
        Examples:
        - "show all tags" -> {'show_all': True}
        - "tags with name production" -> {'variable_name': 'name', 'variable_value': ['production']}
        - "tags with description contains server" -> {'variable_name': 'description', 'variable_value': ['server']}
        """
        prompt_lower = prompt.lower().strip()
        
        # Initialize result
        result = {}
        
        # Parse main tag filter
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
        """Extract the main tag filter from prompt"""
        
        # Check for "show all" patterns first
        if (any(pattern in prompt for pattern in [
            "show all tags", "list all tags", "get all tags", 
            "all tags", "show tags"]) or prompt == "tags"):
            return 'show_all', ['true']  # Special marker for show all
        
        # Pattern: "tags with <field> <operator> <value>" - Enhanced for lookup expressions
        field_lookup_match = re.search(r'tags?\\s+(?:with|having)\\s+(\\w+)\\s+((?:not\\s+)?(?:equal|contains|includes|starts\\s+with|begins\\s+with|ends\\s+with|exact|regex|regexp|regular\\s+expression)(?:\\s+to)?)\\s+(.+)', prompt)
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
        
        # Pattern: "tags with <field> <value>" or "tags by <field> <value>"
        field_match = re.search(r'tags?\\s+(?:with|by|having)\\s+(\\w+)\\s+(\\w+)', prompt)
        if field_match:
            field_term = field_match.group(1)
            value = field_match.group(2)
            
            # Handle custom fields directly (cf_fieldname)
            if field_term.startswith('cf_'):
                return field_term, [value]
            
            if field_term in self.FIELD_MAPPINGS:
                return self.FIELD_MAPPINGS[field_term], [value]
        
        # Pattern: "show tag <value>" or "show <field> <value>"
        show_match = re.search(r'show\\s+(?:tag\\s+)?(\\w+)\\s*(?:\\s+(\\w+))?', prompt)
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
                # Single term - assume it's a tag name
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
            
        if 'content_types' in prompt or 'models' in prompt:
            enabled['get_content_types'] = True
        
        # Special cases for comprehensive queries
        if 'all' in prompt and ('properties' in prompt or 'details' in prompt):
            enabled['get_name'] = True
            enabled['get_description'] = True
            enabled['get_content_types'] = True
        
        return enabled

def parse_tag_prompt(prompt: str) -> Dict[str, Any]:
    """Convenience function to parse a tag prompt"""
    parser = TagPromptParser()
    return parser.parse_prompt(prompt)