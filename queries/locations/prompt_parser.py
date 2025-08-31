"""
Location prompt parser
"""

import re
from typing import Dict, Any, List, Optional

def parse_location_prompt(prompt: str) -> Dict[str, Any]:
    """Parse natural language location queries into structured parameters"""
    
    # Define field mappings from natural language to variables
    field_mappings = {
        'location': 'name',
        'name': 'name', 
        'id': 'id',
        'parent': 'parent',
        'status': 'status',
        'tenant': 'tenant',
        'tag': 'tags',
        'tags': 'tags'
    }
    
    # Set default return values
    result = {
        'variable_name': None,
        'variable_value': None,
        'get_name': True,
        'get_id': False,
        'get_parent': False,
        'get_tags': False,
        'get_racks': False,
        'get_rack_groups': False,
        'get_contact': False,
        'get_vlans': False,
        'get_status': False,
        'get_tenant': False,
        'get_prefix': False,
        'get_latitude': False,
        'get_created': False,
        'get_custom_field_data': False,
        'get_physical_address': False,
        'get_shipping_address': False
    }
    
    prompt = prompt.lower().strip()
    
    # Check for "show all" patterns first
    if ("show all locations" in prompt or 
        "list all locations" in prompt or 
        "get all locations" in prompt or
        prompt in ["all locations", "locations"]):
        result['show_all'] = True
        return result
    
    # Parse simple queries like "show location datacenter1"
    match = re.search(r'location\s+([a-zA-Z0-9-_.]+)', prompt)
    if match:
        location_name = match.group(1)
        result['variable_name'] = 'name'
        result['variable_value'] = [location_name]
        return result
    
    # Parse "locations with status active" or similar
    match = re.search(r'locations?\s+(?:with|having|where)\s+(\w+)\s+([a-zA-Z0-9-_.]+)', prompt)
    if match:
        field = match.group(1)
        value = match.group(2)
        
        # Map the field to the correct variable name
        if field in field_mappings:
            result['variable_name'] = field_mappings[field]
            result['variable_value'] = [value]
            
            # Set appropriate get_* flags based on the field
            if field in ['status']:
                result['get_status'] = True
            elif field in ['tenant']:
                result['get_tenant'] = True
            elif field in ['parent']:
                result['get_parent'] = True
            elif field in ['tag', 'tags']:
                result['get_tags'] = True
        
        return result
    
    # Parse "locations in tenant companyA" or similar
    match = re.search(r'locations?\s+in\s+(\w+)\s+([a-zA-Z0-9-_.]+)', prompt)
    if match:
        field = match.group(1)
        value = match.group(2)
        
        if field in field_mappings:
            result['variable_name'] = field_mappings[field]
            result['variable_value'] = [value]
            
            # Set appropriate flags
            if field in ['tenant']:
                result['get_tenant'] = True
            elif field in ['parent']:
                result['get_parent'] = True
        
        return result
    
    # If no specific pattern matches, try to extract location names
    # Look for patterns like "show datacenter1" or just "datacenter1"
    words = prompt.split()
    for word in words:
        # Skip common query words
        if word not in ['show', 'get', 'list', 'find', 'location', 'locations', 'all']:
            # Assume it's a location name
            result['variable_name'] = 'name'
            result['variable_value'] = [word]
            return result
    
    # Default case - return all locations
    result['variable_name'] = 'name'
    result['variable_value'] = []  # Empty value returns all
    
    return result