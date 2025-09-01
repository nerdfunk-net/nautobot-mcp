"""
Dynamic interface query for Nautobot
"""

from typing import Dict, Any, List, Optional
from difflib import get_close_matches
from ..base import BaseQuery, QueryType, MatchType, ToolSchema
from .prompt_parser import parse_interface_prompt

class DynamicInterfaceQuery(BaseQuery):
    """Dynamic query for interfaces with field mapping and validation"""
    
    def __init__(self):
        self.field_mappings = {
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
        
        self.valid_fields = {
            'name', 'description', 'enabled', 'label', 'type', 'status',
            'role', 'device', 'tags', 'interface_redundancy_groups',
            'id', 'url', 'display'
        }
        
        # Fields that require Boolean type instead of [String]
        self.boolean_fields = {'enabled'}
        
        self.base_query = """
        query Interfaces(
            $get_id: Boolean = false,
            $get_name: Boolean = true,
            $get_enabled: Boolean = false,
            $get_label: Boolean = false,
            $get_type: Boolean = false,
            $get_status: Boolean = false,
            $get_role: Boolean = false,
            $get_description: Boolean = false,
            $get_device: Boolean = false,
            $get_tags: Boolean = false,
            $get_interface_redundancy_groups: Boolean = false,
            $variable_value: [String]
        ) {
            interfaces (enter_variable_name_here: $variable_value) {
                id @include(if: $get_id)
                name @include(if: $get_name)
                description @include(if: $get_description)
                enabled @include(if: $get_enabled)
                label @include(if: $get_label)
                status @include(if: $get_status) {
                    id @include(if: $get_id)
                    name
                }
                role @include(if: $get_role) {
                    id @include(if: $get_id)
                    name
                }
                tags @include(if: $get_tags) {
                    id @include(if: $get_id)
                    name
                }
                type @include(if: $get_type)
                interface_redundancy_groups @include(if: $get_interface_redundancy_groups) {
                    id
                    name
                }
                device @include(if: $get_device) {
                    id @include(if: $get_id)
                    name
                }
            }
        }
        """
        super().__init__()
    
    def get_tool_name(self) -> str:
        return "query_interfaces_dynamic"
    
    def get_description(self) -> str:
        return "Query interfaces with dynamic filtering and field mapping. Supports natural language prompts and custom field queries."
    
    def get_query_type(self) -> QueryType:
        return QueryType.GRAPHQL
    
    def get_match_type(self) -> MatchType:
        return MatchType.EXACT
    
    def get_queries(self) -> str:
        return self.base_query
    
    def get_input_schema(self) -> ToolSchema:
        return ToolSchema(
            type="object",
            properties={
                "prompt": {
                    "type": "string",
                    "description": "Natural language prompt describing what interfaces to find (e.g., 'show all interfaces', 'interfaces with name eth0', 'interfaces on device router1')"
                },
                "variable_name": {
                    "type": "string", 
                    "description": "The field name to filter by (e.g., 'name', 'device', 'status'). Will be mapped from common aliases."
                },
                "variable_value": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The values to filter for"
                },
                "get_id": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include ID field in response"
                },
                "get_name": {
                    "type": "boolean", 
                    "default": True,
                    "description": "Include name field in response"
                },
                "get_enabled": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include enabled field in response"
                },
                "get_label": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include label field in response"
                },
                "get_type": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include type field in response"
                },
                "get_status": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include status field in response"
                },
                "get_role": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include role field in response"
                },
                "get_description": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include description field in response"
                },
                "get_device": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include device field in response"
                },
                "get_tags": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include tags field in response"
                },
                "get_interface_redundancy_groups": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include interface_redundancy_groups field in response"
                }
            },
            required=[]
        )
    
    def _validate_field_name(self, field_name: str) -> tuple[str, Optional[str]]:
        """Validate and map field name with helpful error message if invalid"""
        
        # Handle custom fields directly (cf_fieldname)
        if field_name.startswith('cf_'):
            return field_name, None
            
        # Map field name if it's an alias
        mapped_field = self.field_mappings.get(field_name.lower(), field_name.lower())
        
        # Check if mapped field is valid
        if mapped_field in self.valid_fields:
            if field_name.lower() != mapped_field:
                print(f"INFO: Mapped field '{field_name}' to '{mapped_field}'")
            return mapped_field, None
        
        # Field not found - provide helpful error with suggestions
        available_fields_str = ', '.join(sorted(self.valid_fields))
        close_matches = get_close_matches(field_name.lower(), list(self.valid_fields) + list(self.field_mappings.keys()), n=1, cutoff=0.6)
        
        error_msg = f"Invalid field name: '{field_name}'. "
        if close_matches:
            error_msg += f"Did you mean '{close_matches[0]}'? "
        error_msg += f"Available fields: {available_fields_str}. For custom fields, use 'cf_fieldname' format."
        
        return field_name, error_msg
    
    def execute(self, nautobot_client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the interfaces query with dynamic parameters"""
        try:
            # Parse prompt if provided
            if 'prompt' in arguments:
                prompt_result = parse_interface_prompt(arguments['prompt'])
                # Update arguments with prompt results, but don't override explicit parameters
                for key, value in prompt_result.items():
                    if key not in arguments:
                        arguments[key] = value
            
            # Extract parameters with defaults
            variable_name = arguments.get('variable_name')
            variable_value = arguments.get('variable_value', [])
            show_all = arguments.get('show_all', False)
            
            # Boolean field parameters
            get_id = arguments.get('get_id', False)
            get_name = arguments.get('get_name', True)
            get_enabled = arguments.get('get_enabled', True)
            get_label = arguments.get('get_label', True)
            get_type = arguments.get('get_type', True)
            get_status = arguments.get('get_status', True)
            get_role = arguments.get('get_role', True)
            get_description = arguments.get('get_description', True)
            get_device = arguments.get('get_device', True)
            get_tags = arguments.get('get_tags', True)
            get_interface_redundancy_groups = arguments.get('get_interface_redundancy_groups', True)
            
            # Build the GraphQL query
            query = self.base_query
            variables = {
                "get_id": get_id,
                "get_name": get_name,
                "get_enabled": get_enabled,
                "get_label": get_label,
                "get_type": get_type,
                "get_status": get_status,
                "get_role": get_role,
                "get_description": get_description,
                "get_device": get_device,
                "get_tags": get_tags,
                "get_interface_redundancy_groups": get_interface_redundancy_groups
            }
            
            # Handle show_all case (no filtering)
            if show_all or not variable_name:
                # Remove the filter by replacing with empty parentheses
                query = query.replace('interfaces (enter_variable_name_here: $variable_value)', 'interfaces')
                # Remove variable_value from variables since we're not using it
            else:
                # Validate field name
                validated_field, error_msg = self._validate_field_name(variable_name)
                if error_msg:
                    return {"error": error_msg}
                
                # Handle custom fields (cf_*) - they use String instead of [String]
                if validated_field.startswith('cf_'):
                    # Modify query to use String instead of [String] for custom fields
                    query = query.replace('$variable_value: [String]', '$variable_value: String')
                    # Use single value instead of array
                    variables["variable_value"] = variable_value[0] if variable_value else ""
                # Handle boolean fields - they use Boolean instead of [String]
                elif validated_field in self.boolean_fields:
                    # Modify query to use Boolean instead of [String] for boolean fields
                    query = query.replace('$variable_value: [String]', '$variable_value: Boolean')
                    # Convert value to boolean
                    if variable_value:
                        # Handle different input types
                        first_value = variable_value[0] if isinstance(variable_value, list) else variable_value
                        
                        if isinstance(first_value, bool):
                            # Already a boolean
                            variables["variable_value"] = first_value
                        elif isinstance(first_value, str):
                            # Convert string to boolean
                            bool_value = first_value.lower() in ('true', '1', 'yes', 'on', 'enabled', 'active')
                            variables["variable_value"] = bool_value
                        else:
                            # Fallback: try to convert to boolean
                            variables["variable_value"] = bool(first_value)
                    else:
                        variables["variable_value"] = True  # Default to true if no value specified
                else:
                    variables["variable_value"] = variable_value
                
                # Replace placeholder with actual field name
                query = query.replace('enter_variable_name_here', validated_field)
            
            print(f"DEBUG: Executing interfaces query with field: {variable_name}, values: {variable_value}")
            print(f"DEBUG: Query variables: {variables}")
            
            # Execute query
            result = nautobot_client.graphql_query(query, variables)
            
            if result and 'data' in result and 'interfaces' in result['data']:
                interfaces = result['data']['interfaces']
                return {
                    "interfaces": interfaces,
                    "total_count": len(interfaces),
                    "query_info": {
                        "field_name": variable_name,
                        "field_values": variable_value,
                        "show_all": show_all
                    }
                }
            else:
                return {"error": f"Query failed: {result}"}
                
        except Exception as e:
            return {"error": f"Query execution failed: {str(e)}"}