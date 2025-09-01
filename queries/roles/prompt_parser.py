"""
Prompt parser for role queries
"""

import re
from typing import Dict, Any


def parse_role_prompt(prompt: str) -> Dict[str, Any]:
    """
    Parse natural language prompts for role queries

    Args:
        prompt: Natural language query like "show all roles", "roles with name firewall"

    Returns:
        Dictionary containing parsed parameters for the role query
    """
    prompt_lower = prompt.lower().strip()

    # Default return structure
    result = {}

    # Handle "show all roles" case
    if (
        "show all roles" in prompt_lower
        or "list all roles" in prompt_lower
        or "get all roles" in prompt_lower
        or prompt_lower in ["roles", "all roles"]
    ):
        result["show_all"] = True
        return result

    # Parse field-specific queries
    patterns = [
        # "roles with name X" or "role name X"
        (r'roles?\s+(?:with\s+)?name\s+(["\']?)([^"\']+)\1', "name"),
        # "roles with description X"
        (r'roles?\s+(?:with\s+)?description\s+(["\']?)([^"\']+)\1', "description"),
        # "roles for content type X" or "roles of content type X"
        (
            r'roles?\s+(?:for|of)\s+content\s+type\s+(["\']?)([^"\']+)\1',
            "content_types",
        ),
        # "show role X" - treat as name
        (r'show\s+role\s+(["\']?)([^"\']+)\1', "name"),
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
    result.update(
        {
            "get_name": True,
            "get_description": False,
            "get_content_types": True,
            "get_id": False,
        }
    )

    return result
