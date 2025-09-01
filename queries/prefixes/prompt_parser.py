"""
Prompt parser for dynamic prefix queries
"""

import re
from typing import Dict, Any, Optional, List, Tuple

class PrefixPromptParser:
    """Parser for converting natural language prompts into prefix query parameters"""
    
    # Mapping of common prompt terms to GraphQL field names
    FIELD_MAPPINGS = {
        'prefix': 'prefix',
        'network': 'prefix',
        'subnet': 'prefix',
        'prefix_length': 'prefix_length',
        'within': 'within',
        'within_include': 'within_include',
        'description': 'description',
        'location': 'location',
        'site': 'location', 
        'status': 'status',
        'namespace': 'namespace',
        'tag': 'tags',
        'tags': 'tags',
        'vlan': 'vlan',
        'vrf': 'vrf_assignments__vrf'
    }
    
    # Boolean fields to enable based on query content
    FIELD_ENABLERS = {
        'prefix': ['get_prefix_length', 'get_ip_version'],
        'network': ['get_prefix_length', 'get_ip_version'],
        'subnet': ['get_prefix_length', 'get_ip_version'],
        'prefix_length': ['get_prefix_length'],
        'within': ['get_parent'],
        'within_include': ['get_parent'],
        'description': ['get_description'],
        'location': ['get_location'],
        'status': ['get_status'],
        'namespace': ['get_namespace'],
        'tags': ['get_tags'],
        'vlan': ['get_vlan'],
        'vrf': ['get_vrf_assignments'],
        'parent': ['get_parent'],
        'broadcast': ['get_broadcast']
    }
    
    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Parse a natural language prompt into query parameters
        
        Examples:
        - "show all prefixes" -> {'show_all': True}
        - "show prefix 192.168.1.0/24" -> {'variable_name': 'prefix', 'variable_value': ['192.168.1.0/24']}
        - "prefixes with prefix_length 24" -> {'variable_name': 'prefix_length', 'variable_value': ['24']}
        - "prefixes within 10.0.0.0/8" -> {'variable_name': 'within', 'variable_value': ['10.0.0.0/8']}
        - "prefixes within_include 172.16.0.0/12" -> {'variable_name': 'within_include', 'variable_value': ['172.16.0.0/12']}
        - "prefixes in location datacenter1" -> {'variable_name': 'location', 'variable_value': ['datacenter1']}
        - "prefixes with status active" -> {'variable_name': 'status', 'variable_value': ['active']}
        """
        prompt_lower = prompt.lower().strip()
        
        # Initialize result
        result = {}
        
        # Parse main prefix filter
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
        """Extract the main prefix filter from prompt"""
        
        # Check for "show all" patterns first
        if ("show all prefixes" in prompt or 
            "list all prefixes" in prompt or 
            "get all prefixes" in prompt or
            prompt in ["all prefixes", "prefixes"]):
            return 'show_all', ['true']  # Special marker for show all
        
        # Pattern: "show prefix <cidr>" - matches CIDR notation like 192.168.1.0/24
        prefix_cidr_match = re.search(r'(?:show|get|find)\s+prefix\s+(\d+\.\d+\.\d+\.\d+/\d+)', prompt)
        if prefix_cidr_match:
            return 'prefix', [prefix_cidr_match.group(1)]
        
        # Pattern: "show prefix <network>" - matches any prefix value
        prefix_match = re.search(r'(?:show|get|find)\s+prefix\s+(\S+)', prompt)
        if prefix_match:
            return 'prefix', [prefix_match.group(1)]
        
        # Pattern: "prefixes with prefix_length <length>"
        prefix_length_match = re.search(r'(?:with|having)\s+prefix_length\s+(\d+)', prompt)
        if prefix_length_match:
            return 'prefix_length', [prefix_length_match.group(1)]
        
        # Pattern: "prefixes within <network>"
        within_match = re.search(r'(?:prefixes?\s+)?within\s+(\d+\.\d+\.\d+\.\d+/\d+)', prompt)
        if within_match:
            return 'within', [within_match.group(1)]
        
        # Pattern: "prefixes within_include <network>"
        within_include_match = re.search(r'(?:prefixes?\s+)?within_include\s+(\d+\.\d+\.\d+\.\d+/\d+)', prompt)
        if within_include_match:
            return 'within_include', [within_include_match.group(1)]
        
        # Pattern: "prefixes with <field> <value>" or "prefixes in <field> <value>"
        field_match = re.search(r'prefixes?\s+(?:with|in|at|by)\s+(\w+)\s+(\w+)', prompt)
        if field_match:
            field_term = field_match.group(1)
            value = field_match.group(2)
            
            if field_term in self.FIELD_MAPPINGS:
                return self.FIELD_MAPPINGS[field_term], [value]
        
        # Pattern: "prefixes in location <name>"
        location_match = re.search(r'(?:in|at)\s+location\s+(\w+)', prompt)
        if location_match:
            return 'location', [location_match.group(1)]
            
        # Pattern: "prefixes with status <status>"
        status_match = re.search(r'(?:with|having)\s+status\s+(\w+)', prompt)
        if status_match:
            return 'status', [status_match.group(1)]
            
        # Pattern: "show <field> <value>"
        show_match = re.search(r'show\s+(\w+)\s+(\w+)', prompt)
        if show_match:
            field_term = show_match.group(1)
            value = show_match.group(2)
            
            if field_term in self.FIELD_MAPPINGS:
                return self.FIELD_MAPPINGS[field_term], [value]
        
        return None, None
    
    def _determine_enabled_fields(self, prompt: str, parsed_result: Dict[str, Any]) -> Dict[str, bool]:
        """Determine which boolean fields should be enabled based on prompt content"""
        enabled = {}
        
        # Default fields - always show basic prefix information
        enabled['get_prefix_length'] = True
        enabled['get_ip_version'] = True
        
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
        if 'all' in prompt and ('show all' in prompt or 'list all' in prompt):
            # Enable most fields for comprehensive queries
            comprehensive_fields = [
                'get_description', 'get_status', 'get_namespace', 
                'get_tags', 'get_vlan', 'get_location', 'get_parent'
            ]
            for field in comprehensive_fields:
                enabled[field] = True
        
        return enabled

def parse_prefix_prompt(prompt: str) -> Dict[str, Any]:
    """Convenience function to parse a prefix prompt"""
    parser = PrefixPromptParser()
    return parser.parse_prompt(prompt)