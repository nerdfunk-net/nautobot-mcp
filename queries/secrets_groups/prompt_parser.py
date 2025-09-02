"""
Prompt parser for secrets groups queries
"""

import re
from typing import Dict, Any, List, Optional


def parse_secrets_group_prompt(prompt: str) -> Dict[str, Any]:
    """Parse natural language prompts for secrets groups queries"""
    result = {}
    prompt_lower = prompt.lower().strip()

    # Check for "show all" patterns
    if any(pattern in prompt_lower for pattern in ["show all", "list all", "get all", "find all"]):
        result["show_all"] = True
        return result

    # Extract secrets group name patterns
    name_patterns = [
        r"secrets?\s+group\s+([\"']?)([^\"'\s]+)\1",
        r"group\s+([\"']?)([^\"'\s]+)\1",
        r"named?\s+([\"']?)([^\"'\s]+)\1",
        r"with\s+name\s+([\"']?)([^\"'\s]+)\1",
        r"called\s+([\"']?)([^\"'\s]+)\1",
    ]

    for pattern in name_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            result["variable_name"] = "name"
            result["variable_value"] = [match.group(2)]
            return result

    # Extract description patterns
    description_patterns = [
        r"with\s+description\s+([\"']?)([^\"'\s]+)\1",
        r"description\s+contains\s+([\"']?)([^\"'\s]+)\1",
        r"description\s+([\"']?)([^\"'\s]+)\1",
    ]

    for pattern in description_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            result["variable_name"] = "description"
            result["variable_value"] = [match.group(2)]
            return result

    # Extract secrets patterns
    secrets_patterns = [
        r"with\s+secret\s+([\"']?)([^\"'\s]+)\1",
        r"containing\s+secret\s+([\"']?)([^\"'\s]+)\1",
        r"secret\s+([\"']?)([^\"'\s]+)\1",
    ]

    for pattern in secrets_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            result["variable_name"] = "secrets"
            result["variable_value"] = [match.group(2)]
            return result

    # If no specific pattern is found, try to extract a generic term and assume it's a name
    words = prompt_lower.split()
    if len(words) >= 2:
        # Look for potential secrets group names (avoid common words)
        common_words = {"show", "get", "find", "list", "secret", "secrets", "group", "groups", "the", "all"}
        potential_names = [word for word in words if word not in common_words and len(word) > 2]
        
        if potential_names:
            result["variable_name"] = "name"
            result["variable_value"] = potential_names[:1]  # Take the first potential name
            return result

    # Default fallback - show all secrets groups
    result["show_all"] = True
    return result