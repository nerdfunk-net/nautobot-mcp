"""
Prompt parser for status queries
"""

import re
from typing import Dict, Any, List

def parse_status_prompt(prompt: str) -> Dict[str, Any]:
    """
    Parse natural language prompts for status queries
    
    Args:
        prompt: Natural language query like "show all statuses", "statuses with name active"
    
    Returns:
        Dictionary containing parsed parameters for the status query
    """
    prompt_lower = prompt.lower().strip()
    
    # Default return structure
    result = {}
    
    # Handle "show all statuses" case
    if ("show all statuses" in prompt_lower or 
        "list all statuses" in prompt_lower or 
        "get all statuses" in prompt_lower or
        prompt_lower in ["statuses", "all statuses"]):
        result["show_all"] = True
        return result
    
    # Parse field-specific queries
    patterns = [
        # "statuses with name X" or "status name X"  
        (r'status(?:es)?\s+(?:with\s+)?name\s+(["\']?)([^"\']+)\1', 'name'),
        # "statuses with description X"
        (r'status(?:es)?\s+(?:with\s+)?description\s+(["\']?)([^"\']+)\1', 'description'),
        # "show status X" - treat as name
        (r'show\s+status\s+(["\']?)([^"\']+)\1', 'name'),
    ]
    
    for pattern, field_name in patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            value = match.group(2).strip()
            result["variable_name"] = field_name
            result["variable_value"] = [value]
            break
    
    # If no specific pattern matched, return empty to let manual input handle it
    if not result:
        return {}
    
    # Set default output fields based on common usage
    result.update({
        "get_name": True,
        "get_description": False,
        "get_content_types": True,
        "get_id": False
    })
    
    return result