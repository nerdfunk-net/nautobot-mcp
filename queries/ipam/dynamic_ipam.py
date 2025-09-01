"""
Dynamic IPAM query module that supports variable replacement
"""

import logging
from typing import Dict, Any
from ..base import BaseQuery, QueryType, MatchType, ToolSchema
from .prompt_parser import parse_ipam_prompt

# Set up logger
logger = logging.getLogger(__name__)

class DynamicIPAMQuery(BaseQuery):
    """Dynamic IPAM query that replaces placeholders based on user input"""
    
    def __init__(self):
        self.base_query = """
    query IPaddresses (
      $get_address: Boolean = false,
      $get_config_context: Boolean = false, 
      $get_custom_field_data: Boolean = false,
      $get__custom_field_data: Boolean = false,
      $get_description: Boolean = false,
      $get_device_type: Boolean = false, 
      $get_dns_name: Boolean = false,
      $get_host: Boolean = false,
      $get_hostname: Boolean = false, 
      $get_id: Boolean = false, 
      $get_interfaces: Boolean = false,
      $get_interface_assignments: Boolean = false,
      $get_ip_version: Boolean = false,
      $get_location: Boolean = false,
      $get_mask_length: Boolean = false,
      $get_name: Boolean = false, 
      $get_parent: Boolean = false,
      $get_platform: Boolean = false, 
      $get_primary_ip4_for: Boolean = false,
      $get_primary_ip4: Boolean = false,
      $get_role: Boolean = false, 
      $get_serial: Boolean = false,
      $get_status:  Boolean = false,
      $get_tags: Boolean = false,
      $get_tenant: Boolean = false,
      $get_type: Boolean = false,
      $variable_value: [String],
    ) 
    {
      ip_addresses(enter_variable_name_here: $variable_value)
      {
        id @include(if: $get_id)
        address @include(if: $get_address)
        description @include(if: $get_description)
        dns_name @include(if: $get_dns_name)
        type @include(if: $get_type)
        tags @include(if: $get_tags) 
        {
          id @include(if: $get_id)
          name
        }
        parent @include(if: $get_parent) 
        {
          id @include(if: $get_id)
          network
          prefix
          prefix_length
          namespace {
            id @include(if: $get_id)
            name
          }
          _custom_field_data @include(if: $get__custom_field_data)
          custom_field_data : _custom_field_data @include(if: $get_custom_field_data)
        }
        # show ALL interfaces the IP address is assigned on
        interfaces @include(if: $get_interfaces) 
        {
          id @include(if: $get_id)
          name
          device {
            id @include(if: $get_id)
            name
          }
          description
          enabled
          mac_address
          type
          mode
          ip_addresses {
            address
            role {
              id @include(if: $get_id)
              name
            }
            tags {
              name
              content_types {
                id @include(if: $get_id)
                app_label
                model
              }
            }
          }
        }

        # interface assignments
        interface_assignments @include(if: $get_interface_assignments) 
        {
          id @include(if: $get_id)
          is_standby
          is_default
          is_destination
          interface {
            id @include(if: $get_id)
            name
            description
            type
            status {
              id @include(if: $get_id)
              name
            }
            device {
              id @include(if: $get_id)
              name
            }
            child_interfaces {
              id @include(if: $get_id)
              name
            }
          }
        }

        # now ALL data for the primary IP device
        primary_ip4_for @include(if: $get_primary_ip4_for) {
          id @include(if: $get_id)
          name @include(if: $get_name)
          hostname: name @include(if: $get_hostname)
          role @include(if: $get_role) 
          {
            id @include(if: $get_id)
            name
          }
          device_type @include(if: $get_device_type) 
          {
            id @include(if: $get_id)
            model
          }
          platform @include(if: $get_platform) 
          {
            id @include(if: $get_id)
            name
            manufacturer {
              id @include(if: $get_id)
              name
            }
          }
          tags @include(if: $get_tags) 
          {
            id @include(if: $get_id)
            name
            content_types {
              id @include(if: $get_id)
              app_label
              model
            }
          }
          tenant @include(if: $get_tenant) 
          {
            id @include(if: $get_id)
            name
            tenant_group {
              name
            }
          }
          serial @include(if: $get_serial)
          status @include(if: $get_status)
          {
            id @include(if: $get_id)
            name
          }
          config_context @include(if: $get_config_context)
          _custom_field_data @include(if: $get__custom_field_data)
          custom_field_data : _custom_field_data @include(if: $get_custom_field_data)
          primary_ip4 @include(if: $get_primary_ip4) 
          {
            id @include(if: $get_id)
            description @include(if: $get_description)
            ip_version @include(if: $get_ip_version)
            address @include(if: $get_address)
            host @include(if: $get_host)
            mask_length @include(if: $get_mask_length)
            dns_name @include(if: $get_dns_name)
            parent @include(if: $get_parent)
            {
              id @include(if: $get_id)
              prefix
            }
            status @include(if: $get_status) 
            {
              id @include(if: $get_id)
              name
            }
            interfaces @include(if: $get_interfaces) 
            {
              id @include(if: $get_id)
              name
              description
              enabled
              mac_address
              type
              mode
            }
          }
          interfaces @include(if: $get_interfaces)
          {
            id @include(if: $get_id)
            name
            device {
              name
            }
            description
            enabled
            mac_address
            type
            mode
            ip_addresses 
            {
              address
              role {
                id @include(if: $get_id)
                name
              }
              tags 
              {
                id @include(if: $get_id)
                name
                content_types {
                  id
                  app_label
                  model
                }
              }
            }
            connected_circuit_termination 
            {
              circuit {
                cid
                commit_rate
                provider {
                  name
                }
              }
            }
            tagged_vlans 
            {
              name
              vid
            }
            untagged_vlan 
            {
              name
              vid
            }
            cable 
            {
              termination_a_type
              status 
              {
                name
              }
              color
            }
            tags 
            {
              name
              content_types 
              {
                id
                app_label
                model
              }
            }
            lag {
              name
              enabled
            }
            member_interfaces {
              name
            }
          }
          location @include(if: $get_location) {
            name
          }
        }
      }
    }"""
        super().__init__()
    
    def get_tool_name(self) -> str:
        return "query_ipam_dynamic"
    
    def get_description(self) -> str:
        return "Query IP addresses with dynamic filtering by any property (address, dns_name, type, status, etc.)"
    
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
                    "description": "Natural language query (e.g., 'show ip address 192.168.1.1', 'ip addresses with dns_name contains server')"
                },
                "variable_name": {
                    "type": "string", 
                    "description": "Manual: The IP address property to filter by (e.g., 'address', 'dns_name', 'type', 'status', 'cf_fieldname' for custom fields)"
                },
                "variable_value": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Manual: The value(s) to filter by. For custom fields (cf_*), only the first value is used as a single string."
                },
                "get_address": {"type": "boolean", "default": True},
                "get_config_context": {"type": "boolean", "default": False},
                "get_custom_field_data": {"type": "boolean", "default": False},
                "get__custom_field_data": {"type": "boolean", "default": False},
                "get_description": {"type": "boolean", "default": False},
                "get_device_type": {"type": "boolean", "default": False},
                "get_dns_name": {"type": "boolean", "default": False},
                "get_host": {"type": "boolean", "default": False},
                "get_hostname": {"type": "boolean", "default": False},
                "get_id": {"type": "boolean", "default": False},
                "get_interfaces": {"type": "boolean", "default": False},
                "get_interface_assignments": {"type": "boolean", "default": False},
                "get_ip_version": {"type": "boolean", "default": False},
                "get_location": {"type": "boolean", "default": False},
                "get_mask_length": {"type": "boolean", "default": False},
                "get_name": {"type": "boolean", "default": False},
                "get_parent": {"type": "boolean", "default": False},
                "get_platform": {"type": "boolean", "default": False},
                "get_primary_ip4_for": {"type": "boolean", "default": False},
                "get_primary_ip4": {"type": "boolean", "default": False},
                "get_role": {"type": "boolean", "default": False},
                "get_serial": {"type": "boolean", "default": False},
                "get_status": {"type": "boolean", "default": False},
                "get_tags": {"type": "boolean", "default": False},
                "get_tenant": {"type": "boolean", "default": False},
                "get_type": {"type": "boolean", "default": False}
            },
            required=[]
        )
    
    def _is_custom_field(self, field_name: str) -> bool:
        """Check if the field name is a custom field (starts with cf_)"""
        return field_name.startswith("cf_")
    
    def _modify_query_for_custom_field(self, query: str, variable_name: str) -> str:
        """Modify query for custom fields - use String instead of [String]"""
        if self._is_custom_field(variable_name):
            # Replace [String] with String for custom fields
            query = query.replace("$variable_value: [String],", "$variable_value: String,")
        return query
    
    def _remove_filtering(self, query: str) -> str:
        """Remove the filtering clause from the query to fetch all records"""
        # Replace the filtered query with an unfiltered one
        query = query.replace("ip_addresses(enter_variable_name_here: $variable_value)", "ip_addresses")
        # Remove the variable declaration
        query = query.replace("$variable_value: [String],", "")
        return query
    
    def _execute_graphql(self, client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL query with dynamic variable replacement"""
        
        # Check if we have a prompt to parse
        if "prompt" in arguments:
            parsed = parse_ipam_prompt(arguments["prompt"])
            # Merge parsed parameters with existing arguments
            for key, value in parsed.items():
                if key not in arguments or arguments[key] is None:
                    arguments[key] = value
        
        # Check if this is a "show all" query
        if arguments.get("show_all"):
            query = self._remove_filtering(self.base_query)
            # Remove unnecessary arguments
            filtered_args = {k: v for k, v in arguments.items() 
                           if k not in ["variable_value", "variable_name", "show_all"]}
        else:
            # Get the variable name and value (either from prompt parsing or manual input)
            variable_name = arguments.get("variable_name")
            variable_value = arguments.get("variable_value")
            
            if not variable_name or not variable_value:
                raise ValueError("Either 'prompt' or both 'variable_name' and 'variable_value' must be provided")
            
            # Start with the base query
            query = self.base_query
            
            # Replace the main variable placeholder
            query = query.replace("enter_variable_name_here", variable_name)
            
            # Handle custom fields - modify query to use String instead of [String]
            query = self._modify_query_for_custom_field(query, variable_name)
            
            # For custom fields, ensure variable_value is a single string, not an array
            if self._is_custom_field(variable_name) and isinstance(variable_value, list):
                if len(variable_value) > 0:
                    # Take the first value for custom fields
                    arguments = arguments.copy()
                    arguments['variable_value'] = variable_value[0]
            
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