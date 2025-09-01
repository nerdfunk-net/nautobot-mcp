"""
Dynamic manufacturer query for Nautobot
"""

from typing import Dict, Any, List, Optional
from difflib import get_close_matches
from ..base import BaseQuery, QueryType, MatchType, ToolSchema
from .prompt_parser import parse_manufacturer_prompt

class DynamicManufacturerQuery(BaseQuery):
    """Dynamic query for manufacturers with field mapping and validation"""
    
    def __init__(self):
        self.field_mappings = {
            'vendor': 'name',
            'make': 'name',
            'brand': 'name',
            'company': 'name',
            'mfg': 'name',
            'mfr': 'name',
            'oem': 'name',
            'manufacturer': 'name',
            'manufacturer_name': 'name',
            'description': 'description',
            'desc': 'description',
            'summary': 'description'
        }
        
        self.valid_fields = {
            'name', 'description', 'device_types',
            'id', 'url', 'display'
        }
        
        self.base_query = """
        query Manufacturers(
            $get_id: Boolean = false,
            $get_name: Boolean = true,
            $get_description: Boolean = false,
            $get_device_types: Boolean = false,
            $variable_value: [String]
        ) {
            manufacturers (enter_variable_name_here: $variable_value) {
                id @include(if: $get_id)
                name @include(if: $get_name)
                description @include(if: $get_description)
                device_types @include(if: $get_device_types) {
                    id @include(if: $get_id)
                    model
                }
            }
        }
        """
        super().__init__()
    
    def get_tool_name(self) -> str:
        return "query_manufacturers_dynamic"
    
    def get_description(self) -> str:
        return "Query manufacturers with dynamic filtering and field mapping. Supports natural language prompts and custom field queries."
    
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
                    "description": "Natural language prompt describing what manufacturers to find (e.g., 'show all manufacturers', 'manufacturers with name cisco', 'vendors contains hp')"
                },
                "variable_name": {
                    "type": "string", 
                    "description": "The field name to filter by (e.g., 'name', 'description'). Will be mapped from common aliases."
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
                "get_description": {
                    "type": "boolean",
                    "default": False, 
                    "description": "Include description field in response"
                },
                "get_device_types": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include device_types field in response"
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
        """Execute the manufacturers query with dynamic parameters"""
        try:
            # Parse prompt if provided
            if 'prompt' in arguments:
                prompt_result = parse_manufacturer_prompt(arguments['prompt'])
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
            get_description = arguments.get('get_description', False)
            get_device_types = arguments.get('get_device_types', False)
            
            # Build the GraphQL query
            query = self.base_query
            variables = {
                "get_id": get_id,
                "get_name": get_name,
                "get_description": get_description,
                "get_device_types": get_device_types
            }
            
            # Handle show_all case (no filtering)
            if show_all or not variable_name:
                # Remove the filter by replacing with empty parentheses
                query = query.replace('manufacturers (enter_variable_name_here: $variable_value)', 'manufacturers')
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
                else:
                    variables["variable_value"] = variable_value
                
                # Replace placeholder with actual field name
                query = query.replace('enter_variable_name_here', validated_field)
            
            print(f"DEBUG: Executing manufacturers query with field: {variable_name}, values: {variable_value}")
            print(f"DEBUG: Query variables: {variables}")
            
            # Execute query
            result = nautobot_client.graphql_query(query, variables)
            
            if result and 'data' in result and 'manufacturers' in result['data']:
                manufacturers = result['data']['manufacturers']
                return {
                    "manufacturers": manufacturers,
                    "total_count": len(manufacturers),
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