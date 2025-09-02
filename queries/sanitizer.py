"""
Central input sanitization module for Nautobot MCP queries
"""

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


class QuerySanitizer:
    """Central sanitization utility for query inputs"""
    
    def __init__(self):
        # Define patterns that are considered unsafe
        self.unsafe_patterns = [
            # SQL injection patterns
            (r'\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b', re.IGNORECASE),
            # Script injection patterns  
            (r'<script[^>]*>.*?</script>', 0),
            (r'javascript:', 0),
            (r'vbscript:', 0),
            # Command injection patterns
            (r'[;&|`$()]', 0),
            # Path traversal patterns
            (r'\.\./|\.\.\\', 0),
            # GraphQL injection patterns
            (r'\b(mutation|subscription|fragment)\b', re.IGNORECASE),
            # Null bytes and control characters
            (r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', 0),
        ]
        
        # Compile patterns for performance
        self.compiled_patterns = [re.compile(pattern, flags) for pattern, flags in self.unsafe_patterns]
        
        # Valid lookup expressions for GraphQL
        self.valid_lookups = {
            '__n', '__ic', '__nic', '__isw', '__nisw', '__iew', '__niew',
            '__ie', '__nie', '__re', '__nre', '__ire', '__nire', '__isnull'
        }

    def sanitize_input(self, query_name: str, variable_value: Any) -> bool:
        """
        Central sanitization function for query inputs
        
        Args:
            query_name: Name of the calling query (e.g., 'device', 'interface', 'location')
            variable_value: The input value to sanitize
            
        Returns:
            bool: True if input is valid, False if input is invalid/malicious
        """
        try:
            # Handle None values
            if variable_value is None:
                return True
                
            # Convert to string for pattern matching
            if isinstance(variable_value, list):
                values_to_check = [str(v) for v in variable_value if v is not None]
            else:
                values_to_check = [str(variable_value)]
            
            # Check each value against unsafe patterns
            for value in values_to_check:
                if not self._is_safe_value(value):
                    logger.warning(f"Unsafe input detected in query '{query_name}': {value[:50]}...")
                    return False
                    
                # Additional validation based on query type
                if not self._validate_by_query_type(query_name, value):
                    logger.warning(f"Invalid input for query type '{query_name}': {value[:50]}...")
                    return False
                    
            logger.debug(f"Input validated successfully for query '{query_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error during sanitization for query '{query_name}': {e}")
            return False

    def _is_safe_value(self, value: str) -> bool:
        """Check if a value matches any unsafe patterns"""
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                return False
        return True

    def _validate_by_query_type(self, query_name: str, value: str) -> bool:
        """Additional validation based on the specific query type"""
        
        # Length validation - prevent extremely long inputs
        if len(value) > 1000:
            return False
            
        # For field names containing lookup expressions, validate the lookup
        if '__' in value:
            parts = value.split('__')
            if len(parts) > 1:
                lookup = '__' + parts[-1]
                if lookup not in self.valid_lookups:
                    logger.warning(f"Invalid lookup expression: {lookup}")
                    return False
        
        # Query-specific validations
        if query_name in ['device', 'devices']:
            return self._validate_device_input(value)
        elif query_name in ['interface', 'interfaces']:
            return self._validate_interface_input(value)
        elif query_name in ['location', 'locations']:
            return self._validate_location_input(value)
        elif query_name in ['ipam', 'ip', 'prefix', 'prefixes']:
            return self._validate_ipam_input(value)
        elif query_name in ['role', 'roles']:
            return self._validate_role_input(value)
        elif query_name in ['status', 'statuses']:
            return self._validate_status_input(value)
        elif query_name in ['tag', 'tags']:
            return self._validate_tag_input(value)
        elif query_name in ['manufacturer', 'manufacturers']:
            return self._validate_manufacturer_input(value)
        elif query_name in ['device_type', 'device_types']:
            return self._validate_device_type_input(value)
            
        return True  # Default to allow if no specific validation

    def _validate_device_input(self, value: str) -> bool:
        """Validate device-specific inputs"""
        # Device names should be reasonable length and contain valid characters
        if re.match(r'^[a-zA-Z0-9._-]+(__[a-z]+)?$', value.split('__')[0]):
            return True
        return False

    def _validate_interface_input(self, value: str) -> bool:
        """Validate interface-specific inputs"""
        # Interface names can contain forward slashes, colons, etc.
        base_value = value.split('__')[0]
        if re.match(r'^[a-zA-Z0-9._/-]+$', base_value):
            return True
        return False

    def _validate_location_input(self, value: str) -> bool:
        """Validate location-specific inputs"""
        base_value = value.split('__')[0]
        if re.match(r'^[a-zA-Z0-9._\s-]+$', base_value):
            return True
        return False

    def _validate_ipam_input(self, value: str) -> bool:
        """Validate IP/prefix-specific inputs"""
        base_value = value.split('__')[0]
        # Allow IP addresses, CIDR notation, and field names
        if re.match(r'^[a-zA-Z0-9._:/]+$', base_value):
            return True
        return False

    def _validate_role_input(self, value: str) -> bool:
        """Validate role-specific inputs"""
        base_value = value.split('__')[0]
        if re.match(r'^[a-zA-Z0-9._\s-]+$', base_value):
            return True
        return False

    def _validate_status_input(self, value: str) -> bool:
        """Validate status-specific inputs"""
        base_value = value.split('__')[0]
        if re.match(r'^[a-zA-Z0-9._\s-]+$', base_value):
            return True
        return False

    def _validate_tag_input(self, value: str) -> bool:
        """Validate tag-specific inputs"""
        base_value = value.split('__')[0]
        if re.match(r'^[a-zA-Z0-9._\s-]+$', base_value):
            return True
        return False

    def _validate_manufacturer_input(self, value: str) -> bool:
        """Validate manufacturer-specific inputs"""
        base_value = value.split('__')[0]
        if re.match(r'^[a-zA-Z0-9._\s-]+$', base_value):
            return True
        return False

    def _validate_device_type_input(self, value: str) -> bool:
        """Validate device type-specific inputs"""
        base_value = value.split('__')[0]
        if re.match(r'^[a-zA-Z0-9._\s-]+$', base_value):
            return True
        return False


# Global sanitizer instance
sanitizer = QuerySanitizer()


def sanitize_query_input(query_name: str, variable_value: Any) -> bool:
    """
    Convenience function for sanitizing query inputs
    
    Args:
        query_name: Name of the calling query (e.g., 'device', 'interface', 'location')
        variable_value: The input value to sanitize
        
    Returns:
        bool: True if input is valid, False if input is invalid/malicious
    """
    return sanitizer.sanitize_input(query_name, variable_value)