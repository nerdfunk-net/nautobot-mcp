"""
Customized devices query with dynamic field selection
"""

from typing import Dict, Any, List
from ..base import BaseQuery, QueryType, MatchType, ToolSchema

class DevicesCustomizedQuery(BaseQuery):
    def __init__(self):
        # Mapping from user-friendly names to GraphQL variables
        self.field_mapping = {
            "id": "get_id",
            "device_id": "get_device_id", 
            "name": "get_name",
            "hostname": "get_hostname",
            "asset_tag": "get_asset_tag",
            "config_context": "get_config_context",
            "custom_field_data": "get_custom_field_data",
            "_custom_field_data": "get__custom_field_data",
            "device_bays": "get_device_bays",
            "device_type": "get_device_type",
            "face": "get_face",
            "interfaces": "get_interfaces",
            "local_config_context_data": "get_local_config_context_data",
            "location": "get_location",
            "location_parent": "get_location_parent",
            "parent_bay": "get_parent_bay",
            "primary_ip4": "get_primary_ip4",
            "primary_ip": "get_primary_ip4",  # alias
            "platform": "get_platform",
            "position": "get_position",
            "rack": "get_rack",
            "role": "get_role",
            "serial": "get_serial",
            "status": "get_status",
            "tags": "get_tags",
            "tenant": "get_tenant",
            "vrfs": "get_vrfs",
        }
        
        # Default fields that are always included
        self.default_fields = ["get_hostname"]
        
        super().__init__()
    
    def get_tool_name(self) -> str:
        return "get_device_details"
    
    def get_description(self) -> str:
        return "Get specific properties of devices (e.g., 'show status,interfaces of device-name')"
    
    def get_query_type(self) -> QueryType:
        return QueryType.GRAPHQL
    
    def get_match_type(self) -> MatchType:
        return MatchType.COMBINED
    
    def get_queries(self) -> str:
        return """
            query Devices_customized(
              $name_filter: [String],
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
              $get_vrfs: Boolean = false
            ) {
              devices(name: $name_filter) {
                id @include(if: $get_id)
                id @include(if: $get_device_id)
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
                primary_ip4 @include(if: $get_primary_ip4) {
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
                device_type @include(if: $get_device_type) {
                  id @include(if: $get_id)
                  model
                  manufacturer {
                    id @include(if: $get_id)
                    name
                  }
                }
                platform @include(if: $get_platform) {
                  id @include(if: $get_id)
                  name
                  manufacturer {
                    id @include(if: $get_id)
                    name
                  }
                }
                tags @include(if: $get_tags) {
                  id @include(if: $get_id)
                  name
                  content_types {
                    id @include(if: $get_id)
                    app_label
                    model
                  }
                }
                tenant @include(if: $get_tenant) {
                  id @include(if: $get_id)
                  name
                  tenant_group {
                    name
                  }
                }
                rack @include(if: $get_rack) {
                  id @include(if: $get_id)
                  name
                  rack_group {
                    id @include(if: $get_id)
                    name
                  }
                }
                location @include(if: $get_location) {
                  id @include(if: $get_id)
                  name
                  description
                  location_type {
                    id @include(if: $get_id)
                    name
                  }
                  parent @include(if: $get_location_parent) {
                    id @include(if: $get_id)
                    name
                    description
                    location_type {
                      id @include(if: $get_id)
                      name
                    }
                  }
                }
                status @include(if: $get_status) {
                  id @include(if: $get_id)
                  name
                }
                vrfs @include(if: $get_vrfs) {
                  id @include(if: $get_id)
                  name
                  namespace {
                    id @include(if: $get_id)
                    name
                  }
                  rd
                  description
                }
                interfaces @include(if: $get_interfaces) {
                  id @include(if: $get_id)
                  name
                  description
                  enabled
                  mac_address
                  type
                  mode
                  mtu
                  parent_interface {
                    id @include(if: $get_id)
                    name
                  }
                  bridged_interfaces {
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
                  vrf {
                    id @include(if: $get_id)
                    name
                    namespace {
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
                    role {
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
                  connected_circuit_termination {
                    circuit {
                      cid
                      commit_rate
                      provider {
                        id @include(if: $get_id)
                        name
                      }
                    }
                  }
                  tagged_vlans {
                    id @include(if: $get_id)
                    name
                    vid
                  }
                  untagged_vlan {
                    id @include(if: $get_id)
                    name
                    vid
                  }
                  cable {
                    id @include(if: $get_id)
                    termination_a_type
                    status {
                      id @include(if: $get_id)
                      name
                    }
                    color
                  }
                  tags {
                    id @include(if: $get_id)
                    name
                    content_types {
                      id @include(if: $get_id)
                      app_label
                      model
                    }
                  }
                }
                parent_bay @include(if: $get_parent_bay) {
                  id @include(if: $get_id)
                  name
                }
                device_bays @include(if: $get_device_bays) {
                  id @include(if: $get_id)
                  name
                }
              }
            }"""
    
    def get_input_schema(self) -> ToolSchema:
        available_fields = ", ".join(sorted(self.field_mapping.keys()))
        return ToolSchema(
            type="object",
            properties={
                "name_filter": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Device names to get details for"
                },
                "fields": {
                    "type": "string", 
                    "description": f"Comma-separated list of fields to retrieve. Available: {available_fields}"
                }
            },
            required=["name_filter", "fields"]
        )
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate arguments and field names"""
        super().validate_arguments(arguments)
        
        if "fields" not in arguments:
            raise ValueError("Missing required field: fields")
        
        # Parse and validate field names
        field_names = [f.strip().lower() for f in arguments["fields"].split(",")]
        invalid_fields = [f for f in field_names if f not in self.field_mapping]
        
        if invalid_fields:
            available = ", ".join(sorted(self.field_mapping.keys()))
            raise ValueError(f"Invalid field names: {invalid_fields}. Available fields: {available}")
        
        return True
    
    def execute(self, client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the customized query with dynamic field selection"""
        self.validate_arguments(arguments)
        
        # Parse requested fields
        requested_fields = [f.strip().lower() for f in arguments["fields"].split(",")]
        
        # Build GraphQL variables
        graphql_variables = {
            "name_filter": arguments["name_filter"]
        }
        
        # Set all field flags to false initially
        for graphql_var in self.field_mapping.values():
            graphql_variables[graphql_var] = False
        
        # Enable default fields
        for default_field in self.default_fields:
            graphql_variables[default_field] = True
        
        # Enable requested fields
        for field_name in requested_fields:
            graphql_var = self.field_mapping[field_name]
            graphql_variables[graphql_var] = True
        
        # Execute query with logging
        import logging
        import json
        logger = logging.getLogger(__name__)
        
        logger.info(f"Executing customized query for devices: {arguments['name_filter']}, fields: {requested_fields}")
        
        try:
            result = client.graphql_query(self.get_queries(), graphql_variables)
            
            # Check for GraphQL errors first
            if result.get("errors"):
                return {
                    "error": "GraphQL query failed",
                    "details": result["errors"]
                }
            
            # Check response size and provide helpful error if too large
            response_json = json.dumps(result)
            response_size = len(response_json)
            logger.info(f"Response size: {response_size} bytes")
            
            if response_size > 50000:  # 50KB limit
                device_count = len(result.get("data", {}).get("devices", []))
                return {
                    "error": f"Response too large ({response_size} bytes, {device_count} devices). Try requesting fewer fields or devices.",
                    "suggested_fields": ["status", "role", "device_type"],
                    "requested_fields": requested_fields
                }
            
            # Log successful execution
            device_count = len(result.get("data", {}).get("devices", []))
            logger.info(f"Successfully returned {device_count} devices with {len(requested_fields)} fields")
            
            # Return just the devices data, not the full GraphQL wrapper
            devices_data = result.get("data", {}).get("devices", [])
            
            # Format for better Claude Desktop consumption
            if devices_data:
                formatted_result = []
                for device in devices_data:
                    formatted_result.append(device)
                
                return {
                    "devices_found": len(formatted_result),
                    "requested_fields": requested_fields,
                    "devices": formatted_result
                }
            else:
                return {
                    "devices_found": 0,
                    "requested_fields": requested_fields,
                    "message": "No devices found matching the criteria",
                    "searched_devices": arguments['name_filter']
                }
            
        except Exception as e:
            logger.error(f"Customized query execution failed: {str(e)}")
            return {
                "error": f"Query execution failed: {str(e)}",
                "requested_fields": requested_fields,
                "device_filter": arguments['name_filter']
            }