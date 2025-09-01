"""
Dynamic location query module that supports variable replacement
"""

import logging
from typing import Dict, Any
from ..base import BaseQuery, QueryType, MatchType, ToolSchema
from .prompt_parser import parse_location_prompt

# Set up logger
logger = logging.getLogger(__name__)

class DynamicLocationQuery(BaseQuery):
    """Dynamic location query that replaces placeholders based on user input"""
    
    def __init__(self):
        # Mapping of common incorrect/alternate field names to correct GraphQL field names
        self.field_mappings = {
            # Common aliases for location name
            'location': 'name',
            'location_name': 'name',
            'site': 'name',
            'site_name': 'name',
            
            # Common aliases for parent
            'parent_location': 'parent',
            'parent_site': 'parent',
            'region': 'parent',
            'area': 'parent',
            
            # Common aliases for status
            'state': 'status',
            'condition': 'status',
            
            # Common aliases for tags
            'tag': 'tags',
            'label': 'tags',
            'labels': 'tags',
            
            # Common aliases for tenant
            'customer': 'tenant',
            'organization': 'tenant',
            'org': 'tenant',
            
            # Common aliases for address
            'address': 'physical_address',
            'street_address': 'physical_address',
            'postal_address': 'physical_address',
            
            # Common aliases for coordinates
            'lat': 'latitude',
            'long': 'longitude',
            'lng': 'longitude',
            'coordinates': 'latitude',
            
            # Common aliases for racks
            'rack': 'racks',
            'cabinet': 'racks',
            'cabinets': 'racks',
            
            # Common aliases for VLANs
            'vlan': 'vlans',
            'network': 'vlans',
            'networks': 'vlans',
            
            # Common aliases for prefixes
            'prefix': 'prefixes',
            'subnet': 'prefixes',
            'subnets': 'prefixes',
            'ip_range': 'prefixes',
            
            # Common aliases for contact
            'contact_person': 'contact',
            'admin': 'contact',
            'administrator': 'contact'
        }
        
        # Valid GraphQL fields that can be used in locations query
        self.valid_fields = {
            'name', 'parent', 'status', 'tags', 'tenant', 'physical_address',
            'latitude', 'longitude', 'racks', 'vlans', 'prefixes', 'contact',
            'rack_groups', 'created', 'custom_field_data'
        }
        
        self.base_query = """
    query Locations(
        $get_id: Boolean = false,
        $get_name: Boolean = true,
        $get_parent: Boolean = false,
        $get_tags: Boolean = false,
        $get_racks: Boolean = false,
        $get_rack_groups: Boolean = false,
        $get_contact: Boolean = false,
        $get_vlans: Boolean = false,
        $get_status: Boolean = false,
        $get_tenant: Boolean = false,
        $get_prefix: Boolean = false,
        $get_latitude: Boolean = false,
        $get_created: Boolean = false,
        $get_custom_field_data: Boolean = false,
        $get_physical_address: Boolean = false,
        $get_shipping_address: Boolean = false,
        $variable_value: [String],
        ) 
    {
      locations (enter_variable_name_here: $variable_value) 
      {
        id @include(if: $get_id)
        name @include(if: $get_name)
        associated_contacts {
          id @include(if: $get_id)
          contact @include(if: $get_contact)  {
            id @include(if: $get_id)
          }
        }
        parent @include(if: $get_parent) {
          name
        }
        tags @include(if: $get_tags) {
          id
        }
        racks @include(if: $get_racks) {
          id @include(if: $get_id)
          name
        }
        rack_groups @include(if: $get_rack_groups) {
          id  @include(if: $get_id)
          name
          parent {
            id
          }
        }
        vlans @include(if: $get_vlans) {
          id @include(if: $get_id)
          name
          vid
          vlan_group {
            id @include(if: $get_id)
          }
        }
        status @include(if: $get_status) {
          id @include(if: $get_id)
          name
        }
        tenant @include(if: $get_tenant) {
          id @include(if: $get_id)
          name
        }
        prefix_assignments @include(if: $get_prefix)  {
          id @include(if: $get_id)
          prefix {
            id
          }
        }
        latitude @include(if: $get_latitude)
        created @include(if: $get_created)
        _custom_field_data @include(if: $get_custom_field_data)
        physical_address @include(if: $get_physical_address)
        shipping_address @include(if: $get_shipping_address)
      }
    }"""
        super().__init__()
    
    def get_tool_name(self) -> str:
        return "query_locations_dynamic"
    
    def get_description(self) -> str:
        return "Query locations with dynamic filtering by any property (name, parent, tenant, status, etc.). Automatically maps common field aliases (site→name, region→parent, address→physical_address, etc.)"
    
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
                    "description": "Natural language query (e.g., 'show location datacenter1', 'locations with status active')"
                },
                "variable_name": {
                    "type": "string", 
                    "description": "Manual: The location property to filter by (e.g., 'name', 'parent', 'tenant', 'status', 'cf_fieldname' for custom fields). Common aliases are automatically mapped: 'site' → 'name', 'region' → 'parent', 'address' → 'physical_address', etc."
                },
                "variable_value": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Manual: The value(s) to filter by"
                },
                "get_id": {"type": "boolean", "default": False},
                "get_name": {"type": "boolean", "default": True},
                "get_parent": {"type": "boolean", "default": False},
                "get_tags": {"type": "boolean", "default": False},
                "get_racks": {"type": "boolean", "default": False},
                "get_rack_groups": {"type": "boolean", "default": False},
                "get_contact": {"type": "boolean", "default": False},
                "get_vlans": {"type": "boolean", "default": False},
                "get_status": {"type": "boolean", "default": False},
                "get_tenant": {"type": "boolean", "default": False},
                "get_prefix": {"type": "boolean", "default": False},
                "get_latitude": {"type": "boolean", "default": False},
                "get_created": {"type": "boolean", "default": False},
                "get_custom_field_data": {"type": "boolean", "default": False},
                "get_physical_address": {"type": "boolean", "default": False},
                "get_shipping_address": {"type": "boolean", "default": False}
            },
            required=[]
        )
    
    def _is_custom_field(self, field_name: str) -> bool:
        """Check if the field name is a custom field (starts with cf_)"""
        return field_name.startswith("cf_")
    
    def _map_field_name(self, field_name: str) -> str:
        """Map an alternate/incorrect field name to the correct GraphQL field name"""
        return self.field_mappings.get(field_name.lower(), field_name)
    
    def _is_valid_field(self, field_name: str) -> bool:
        """Check if a field name is valid for location queries"""
        return field_name in self.valid_fields or self._is_custom_field(field_name)
    
    def _suggest_field_name(self, invalid_field: str) -> str:
        """Suggest the correct field name for an invalid field"""
        invalid_lower = invalid_field.lower()
        
        # Check if it's a known mapping
        if invalid_lower in self.field_mappings:
            return self.field_mappings[invalid_lower]
        
        # Use fuzzy matching to suggest similar field names
        import difflib
        
        # Find closest matches
        matches = difflib.get_close_matches(invalid_lower, [f.lower() for f in self.valid_fields], n=3, cutoff=0.4)
        
        if matches:
            return matches[0]
        
        return "name"  # Default fallback for locations
    
    def _remove_filtering(self, query: str) -> str:
        """Remove the filtering clause from the query to fetch all records"""
        # Replace the filtered query with an unfiltered one
        query = query.replace("locations (enter_variable_name_here: $variable_value)", "locations")
        # Remove the variable declaration
        query = query.replace("$variable_value: [String],", "")
        return query
    
    def _execute_graphql(self, client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL query with dynamic variable replacement"""
        
        # Check if we have a prompt to parse
        if "prompt" in arguments:
            parsed = parse_location_prompt(arguments["prompt"])
            # Merge parsed parameters with existing arguments
            for key, value in parsed.items():
                if key not in arguments or arguments[key] is None:
                    arguments[key] = value
        
        # Check if this is a "show all" query
        if arguments.get("show_all"):
            query = self._remove_filtering(self.base_query)
            # Remove variable_value from arguments since it's not needed
            filtered_args = {k: v for k, v in arguments.items() 
                           if k not in ["variable_value", "variable_name", "show_all"]}
        else:
            # Get the variable name and value (either from prompt parsing or manual input)
            variable_name = arguments.get("variable_name")
            variable_value = arguments.get("variable_value")
            
            if not variable_name or not variable_value:
                raise ValueError("Either 'prompt' or both 'variable_name' and 'variable_value' must be provided")
            
            # Map field name if it's an alternate/incorrect name
            original_field_name = variable_name
            mapped_field_name = self._map_field_name(variable_name)
            
            # Validate field name and provide suggestions if invalid
            if not self._is_valid_field(mapped_field_name):
                suggested_field = self._suggest_field_name(original_field_name)
                available_fields = sorted(self.valid_fields)
                raise ValueError(
                    f"Invalid field name: '{original_field_name}'. "
                    f"Did you mean '{suggested_field}'? "
                    f"Available fields: {', '.join(available_fields)}. "
                    f"For custom fields, use 'cf_fieldname' format."
                )
            
            # Log field mapping if it occurred
            if mapped_field_name != original_field_name:
                logger.info(f"Mapped field '{original_field_name}' to '{mapped_field_name}'")
            
            # Use the mapped field name
            variable_name = mapped_field_name
            
            # Start with the base query and replace the placeholder
            query = self.base_query
            query = query.replace("enter_variable_name_here", variable_name)
            filtered_args = arguments
        
        # Log the complete query for debugging
        logger.info("=" * 80)
        logger.info("EXECUTING GRAPHQL QUERY:")
        logger.info("=" * 80)
        logger.info(query)
        logger.info("=" * 80)
        logger.info("WITH ARGUMENTS:")
        logger.info(filtered_args)
        logger.info("=" * 80)
        
        return client.graphql_query(query, filtered_args)