"""
Dynamic device query module that supports variable replacement
"""

import re
import logging
from typing import Dict, Any, Optional
from ..base import BaseQuery, QueryType, MatchType, ToolSchema
from .prompt_parser import parse_device_prompt

# Set up logger
logger = logging.getLogger(__name__)

class DynamicDeviceQuery(BaseQuery):
    """Dynamic device query that replaces placeholders based on user input"""
    
    def __init__(self):
        self.base_query = """
  query Devices(
      $get_asset_tag: Boolean = false,
      $get_custom_field_data: Boolean = false,
      $get__custom_field_data: Boolean = false,
      $get_config_context: Boolean = false,
      $get_device_bays: Boolean = false,
      $get_device_type: Boolean = false,
      $get_face: Boolean = false,
      $get_hostname: Boolean = true, 
      $get_id: Boolean = false,
      $get_device_id: Boolean = false, 
      $get_interfaces: Boolean = false,
      $get_local_config_context_data: Boolean = false,
      $get_location: Boolean = false,
      $get_location_parent: Boolean = false,
      $get_name: Boolean = false,
      $get_parent_bay: Boolean = false,
      $get_primary_ip4: Boolean = false, 
      $get_platform: Boolean = false, 
      $get_position: Boolean = false,
      $get_rack: Boolean = false,
      $get_role: Boolean = false, 
      $get_serial: Boolean = false,
      $get_status: Boolean = false,
      $get_tags: Boolean = false, 
      $get_tenant: Boolean = false,
      $get_vrfs: Boolean = false,
      $variable_value: [String],
      $interface_var_value: [String]
    ) 
    {
      devices(enter_variable_name_here: $variable_value) 
      {
        id @include(if: $get_id)
        device_id: id @include(if: $get_device_id)
        name @include(if: $get_name)
        hostname: name @include(if: $get_hostname)
        asset_tag @include(if: $get_asset_tag)
        config_context @include(if: $get_config_context)
        _custom_field_data @include(if: $get__custom_field_data)
        custom_field_data : _custom_field_data @include(if: $get_custom_field_data)
        position @include(if: $get_position)
        face @include(if: $get_face)
        serial @include(if: $get_serial)
        local_config_context_data @include(if: $get_local_config_context_data)
        primary_ip4 @include(if: $get_primary_ip4) 
        {
          id @include(if: $get_id)
          description
          ip_version
          address
          host
          mask_length
          dns_name
          parent {
            id @include(if: $get_id)
            prefix
          }
          status {
            id @include(if: $get_id)
            name
          }
          interfaces {
            id @include(if: $get_id)
            name
          }
        }
        role @include(if: $get_role) {
          id @include(if: $get_id)
          name
        }
        device_type @include(if: $get_device_type) 
        {
          id @include(if: $get_id)
          model
          manufacturer 
          {
            id @include(if: $get_id)
            name
          }
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
        rack @include(if: $get_rack) 
        {
          id @include(if: $get_id)
          name
          rack_group
          {
            id @include(if: $get_id)
            name
          }
        }
        location @include(if: $get_location) 
        {
          id @include(if: $get_id)
          name
          description
          location_type
          {
            id @include(if: $get_id)
            name
          }
          parent @include(if: $get_location_parent)
          {
            id @include(if: $get_id)
            name
            description
            location_type
            {
              id @include(if: $get_id)
              name
            }
          }
        }
        status @include(if: $get_status) 
        {
          id @include(if: $get_id)
          name
        }
        vrfs @include(if: $get_vrfs) 
        {
          id @include(if: $get_id)
          name
          namespace 
          {
            id @include(if: $get_id)
            name
          }
          rd
          description
        }
        interfaces (enter_interface_var_here: $interface_var_value) @include(if: $get_interfaces)
        {
          id @include(if: $get_id)
          name
          description
          enabled
          mac_address
          type
          mode
          mtu
          parent_interface
          {
            id @include(if: $get_id)
            name
          }
          bridged_interfaces 
          {
            id @include(if: $get_id)
            name
          }
          status {
            id @include(if: $get_id)
            name
          }
          lag {
            id @include(if: $get_id)
            name
            enabled
          }
          member_interfaces {
            id @include(if: $get_id)
            name
          }
          vrf 
          {
            id @include(if: $get_id)
            name
            namespace 
            {
              id @include(if: $get_id)
              name
            }
          }
          ip_addresses {
            address
            status {
              id @include(if: $get_id)
              name
            }
            role 
            {
              id @include(if: $get_id)
              name
            }
            tags {
              id @include(if: $get_id)
              name
            }
            parent {
              id @include(if: $get_id)
              network
              prefix
              prefix_length
              namespace {
                id @include(if: $get_id)
                name
              }
            }
          }
          connected_circuit_termination 
          {
            circuit 
            {
              cid
              commit_rate
              provider 
              {
                id @include(if: $get_id)
                name
              }
            }
          }
          tagged_vlans 
          {
            id @include(if: $get_id)
            name
            vid
          }
          untagged_vlan 
          {
            id @include(if: $get_id)
            name
            vid
          }
          cable 
          {
            id @include(if: $get_id)
            termination_a_type
            status 
            {
              id @include(if: $get_id)
              name
            }
            color
          }
          tags 
          {
            id @include(if: $get_id)
            name
            content_types 
            {
              id @include(if: $get_id)
              app_label
              model
            }
          }
        }
        parent_bay @include(if: $get_parent_bay)
        {
          id @include(if: $get_id)
          name
        }
        device_bays @include(if: $get_device_bays)
        {
          id @include(if: $get_id)
          name
        }
      }
    }"""
        super().__init__()
    
    def get_tool_name(self) -> str:
        return "query_devices_dynamic"
    
    def get_description(self) -> str:
        return "Query devices with dynamic filtering by any property (name, location, role, etc.) with support for lookup expressions (__ic, __isw, __iew, __n, etc.)"
    
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
                    "description": "Natural language query (e.g., 'show device router1', 'devices with name contains router', 'devices with hostname starts with core')"
                },
                "variable_name": {
                    "type": "string", 
                    "description": "Manual: The device property to filter by with optional lookup expressions (e.g., 'name', 'name__ic', 'name__isw', 'location', 'role'). Supports: __n (not equal), __ic (contains), __nic (not contains), __isw (starts with), __nisw (not starts with), __iew (ends with), __niew (not ends with), __ie (exact case-insensitive), __nie (not exact case-insensitive), __re (regex), __nre (not regex), __ire (case-insensitive regex), __nire (not case-insensitive regex), __isnull (is null)"
                },
                "variable_value": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Manual: The value(s) to filter by"
                },
                "interface_variable": {
                    "type": "string",
                    "description": "Optional interface property to filter by (e.g., 'name', 'type')"
                },
                "interface_value": {
                    "type": "array", 
                    "items": {"type": "string"},
                    "description": "Optional interface value(s) to filter by"
                },
                "get_asset_tag": {"type": "boolean", "default": False},
                "get_custom_field_data": {"type": "boolean", "default": False},
                "get__custom_field_data": {"type": "boolean", "default": False},
                "get_config_context": {"type": "boolean", "default": False},
                "get_device_bays": {"type": "boolean", "default": False},
                "get_device_type": {"type": "boolean", "default": False},
                "get_face": {"type": "boolean", "default": False},
                "get_hostname": {"type": "boolean", "default": True},
                "get_id": {"type": "boolean", "default": False},
                "get_device_id": {"type": "boolean", "default": False},
                "get_interfaces": {"type": "boolean", "default": False},
                "get_local_config_context_data": {"type": "boolean", "default": False},
                "get_location": {"type": "boolean", "default": False},
                "get_location_parent": {"type": "boolean", "default": False},
                "get_name": {"type": "boolean", "default": False},
                "get_parent_bay": {"type": "boolean", "default": False},
                "get_primary_ip4": {"type": "boolean", "default": False},
                "get_platform": {"type": "boolean", "default": False},
                "get_position": {"type": "boolean", "default": False},
                "get_rack": {"type": "boolean", "default": False},
                "get_role": {"type": "boolean", "default": False},
                "get_serial": {"type": "boolean", "default": False},
                "get_status": {"type": "boolean", "default": False},
                "get_tags": {"type": "boolean", "default": False},
                "get_tenant": {"type": "boolean", "default": False},
                "get_vrfs": {"type": "boolean", "default": False}
            },
            required=[]
        )
    
    def _remove_interface_section(self, query: str) -> str:
        """Remove the entire interfaces section from the query"""
        # More precise pattern to match the complete interfaces block
        # This handles the nested structure properly
        lines = query.split('\n')
        result_lines = []
        skip_interface_section = False
        brace_count = 0
        interface_start_found = False
        
        for line in lines:
            # Check if this line contains the interface placeholder
            if 'interfaces (enter_interface_var_here:' in line:
                interface_start_found = True
                skip_interface_section = True
                brace_count = 0
                continue
            
            if skip_interface_section:
                # Count braces to know when the interface section ends
                brace_count += line.count('{') - line.count('}')
                
                # If we've closed all braces, we're done with the interface section
                if brace_count <= 0:
                    skip_interface_section = False
                    interface_start_found = False
                continue
            
            # Remove the interface variable declaration and get_interfaces boolean
            if '$interface_var_value: [String]' in line:
                continue
            if '$get_interfaces: Boolean = false,' in line:
                continue
                
            result_lines.append(line)
        
        # Fix trailing comma after variable_value when interface variable is removed
        result_query = '\n'.join(result_lines)
        result_query = result_query.replace('$variable_value: [String],\n    )', '$variable_value: [String]\n    )')
        return result_query
    
    def _remove_filtering(self, query: str) -> str:
        """Remove the filtering clause from the query to fetch all records"""
        # Replace the filtered query with an unfiltered one
        query = query.replace("devices(enter_variable_name_here: $variable_value)", "devices")
        # Remove the variable declaration
        query = query.replace("$variable_value: [String],", "")
        return query
    
    def _execute_graphql(self, client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL query with dynamic variable replacement"""
        
        # Check if we have a prompt to parse
        if "prompt" in arguments:
            parsed = parse_device_prompt(arguments["prompt"])
            # Merge parsed parameters with existing arguments
            for key, value in parsed.items():
                if key not in arguments or arguments[key] is None:
                    arguments[key] = value
        
        # Check if this is a "show all" query
        if arguments.get("show_all"):
            query = self._remove_filtering(self.base_query)
            # Remove interface section since we're showing all devices
            query = self._remove_interface_section(query)
            # Remove unnecessary arguments
            filtered_args = {k: v for k, v in arguments.items() 
                           if k not in ["variable_value", "variable_name", "show_all", "interface_variable", "interface_value", "get_interfaces"]}
        else:
            # Get the variable name and value (either from prompt parsing or manual input)
            variable_name = arguments.get("variable_name")
            variable_value = arguments.get("variable_value")
            
            if not variable_name or not variable_value:
                raise ValueError("Either 'prompt' or both 'variable_name' and 'variable_value' must be provided")
            
            # Get interface parameters
            interface_variable = arguments.get("interface_variable")
            interface_value = arguments.get("interface_value")
            
            # Start with the base query
            query = self.base_query
            
            # Replace the main variable placeholder
            query = query.replace("enter_variable_name_here", variable_name)
            
            # Handle interface parameters
            if interface_variable and interface_value:
                # Replace interface placeholder
                query = query.replace("enter_interface_var_here", interface_variable)
            else:
                # Remove the entire interface section if not needed
                query = self._remove_interface_section(query)
                # Remove get_interfaces from arguments when not using interfaces
                if 'get_interfaces' in arguments:
                    arguments = arguments.copy()
                    del arguments['get_interfaces']
            
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