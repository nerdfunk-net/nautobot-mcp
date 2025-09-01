"""
Filtered IP addresses query with dynamic field filtering
Supports prompts like: "show status of 192.168.10.1/32 having tags tag-1"
"""

from typing import Dict, Any
from ..base import BaseQuery, QueryType, MatchType, ToolSchema


class IPAddressesFilteredQuery(BaseQuery):
    def __init__(self):
        # Mapping from user-friendly names to GraphQL variables
        self.field_mapping = {
            "id": "get_id",
            "address": "get_address",
            "config_context": "get_config_context",
            "custom_field_data": "get_custom_field_data",
            "_custom_field_data": "get__custom_field_data",
            "description": "get_description",
            "device_type": "get_device_type",
            "dns_name": "get_dns_name",
            "host": "get_host",
            "hostname": "get_hostname",
            "interfaces": "get_interfaces",
            "interface_assignments": "get_interface_assignments",
            "ip_version": "get_ip_version",
            "location": "get_location",
            "mask_length": "get_mask_length",
            "name": "get_name",
            "parent": "get_parent",
            "platform": "get_platform",
            "primary_ip4_for": "get_primary_ip4_for",
            "primary_ip4": "get_primary_ip4",
            "role": "get_role",
            "serial": "get_serial",
            "status": "get_status",
            "tags": "get_tags",
            "tenant": "get_tenant",
            "type": "get_type",
        }

        # Supported filter fields
        self.supported_filter_fields = {
            "tags": "tags",  # user_name -> graphql_field_name
            "role": "role",  # IP address role filtering
        }

        # Default fields that are always included
        self.default_fields = ["get_address"]

        super().__init__()

    def get_tool_name(self) -> str:
        return "get_ip_addresses_filtered"

    def get_description(self) -> str:
        return "FILTER IP addresses by tags/roles. Use ONLY when query contains: 'having tags', 'having role', 'with tags', 'with role', 'tagged with', or 'filtered by'. NEVER use get_ip_addresses for filtering."

    def get_query_type(self) -> QueryType:
        return QueryType.GRAPHQL

    def get_match_type(self) -> MatchType:
        return MatchType.EXACT

    def get_queries(self) -> str:
        # Return the template query - will be modified dynamically
        return """
            query IPaddresses_fully_customizable(
                $get_address: Boolean = true,
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
                $get_status: Boolean = false,
                $get_tags: Boolean = false,
                $get_tenant: Boolean = false,
                $get_type: Boolean = false,
                $address_filter: [String],
                $variable_value: [String]
            ) 
            {
                ip_addresses(address: $address_filter, enter_variable_name_here: $variable_value)
                {
                    id @include(if: $get_id)
                    address @include(if: $get_address)
                    description @include(if: $get_description)
                    dns_name @include(if: $get_dns_name)
                    type @include(if: $get_type)
                    status @include(if: $get_status) {
                        id @include(if: $get_id)
                        name
                    }
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

    def get_input_schema(self) -> ToolSchema:
        available_fields = ", ".join(sorted(self.field_mapping.keys()))
        available_filter_fields = ", ".join(sorted(self.supported_filter_fields.keys()))

        return ToolSchema(
            type="object",
            properties={
                "address_filter": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of IP addresses to filter by (e.g., ['192.168.10.1/32']). Leave empty to search all IPs.",
                },
                "fields": {
                    "type": "string",
                    "description": f"Comma-separated list of fields to retrieve. Available: {available_fields}",
                },
                "filter_field": {
                    "type": "string",
                    "description": f"Field to filter by. Currently supported: {available_filter_fields}",
                },
                "filter_value": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Values to filter by (e.g., ['tag-1', 'production'])",
                },
            },
            required=["fields", "filter_field", "filter_value"],
        )

    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate arguments and field names"""
        super().validate_arguments(arguments)

        # Validate required fields
        for field in ["fields", "filter_field", "filter_value"]:
            if field not in arguments:
                raise ValueError(f"Missing required field: {field}")

        # Parse and validate field names
        field_names = [f.strip().lower() for f in arguments["fields"].split(",")]
        invalid_fields = [f for f in field_names if f not in self.field_mapping]

        if invalid_fields:
            available = ", ".join(sorted(self.field_mapping.keys()))
            raise ValueError(
                f"Invalid field names: {invalid_fields}. Available fields: {available}"
            )

        # Validate filter field
        filter_field = arguments["filter_field"].strip().lower()
        if filter_field not in self.supported_filter_fields:
            available = ", ".join(sorted(self.supported_filter_fields.keys()))
            raise ValueError(
                f"Invalid filter field: {filter_field}. Currently supported: {available}"
            )

        return True

    def execute(self, client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the filtered query with dynamic GraphQL modification"""
        self.validate_arguments(arguments)

        # Parse arguments
        requested_fields = [f.strip().lower() for f in arguments["fields"].split(",")]
        filter_field = arguments["filter_field"].strip().lower()
        filter_value = arguments["filter_value"]
        address_filter = arguments.get("address_filter", [])

        # Build GraphQL variables
        graphql_variables = {
            "address_filter": address_filter if address_filter else None,
            "variable_value": filter_value,
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

        # Get the template query
        query_template = self.get_queries()

        # DYNAMIC MODIFICATION: Replace the placeholder with actual field name
        graphql_field_name = self.supported_filter_fields[filter_field]
        modified_query = query_template.replace(
            "enter_variable_name_here", graphql_field_name
        )

        # Execute query with logging
        import logging
        import json

        logger = logging.getLogger(__name__)

        logger.info(
            f"Executing filtered IP addresses query: filter={filter_field}={filter_value}, fields={requested_fields}, addresses={address_filter}"
        )
        logger.debug(f"Modified GraphQL query uses filter: {graphql_field_name}")

        try:
            result = client.graphql_query(modified_query, graphql_variables)

            # Check for GraphQL errors first
            if result.get("errors"):
                return {"error": "GraphQL query failed", "details": result["errors"]}

            # Check response size and provide helpful error if too large
            response_json = json.dumps(result)
            response_size = len(response_json)
            logger.info(f"Response size: {response_size} bytes")

            if response_size > 50000:  # 50KB limit
                ip_count = len(result.get("data", {}).get("ip_addresses", []))
                return {
                    "error": f"Response too large ({response_size} bytes, {ip_count} IP addresses). Try requesting fewer fields.",
                    "suggested_fields": ["address", "status"],
                    "requested_fields": requested_fields,
                }

            # Log successful execution
            ip_count = len(result.get("data", {}).get("ip_addresses", []))
            logger.info(
                f"Successfully returned {ip_count} IP addresses with {len(requested_fields)} fields"
            )

            # Return just the IP addresses data, not the full GraphQL wrapper
            ip_addresses_data = result.get("data", {}).get("ip_addresses", [])

            # Format for better Claude Desktop consumption
            if ip_addresses_data:
                formatted_result = []
                for ip_address in ip_addresses_data:
                    formatted_result.append(ip_address)

                return {
                    "ip_addresses_found": len(formatted_result),
                    "requested_fields": requested_fields,
                    "filter_applied": f"{filter_field} = {filter_value}",
                    "ip_addresses": formatted_result,
                }
            else:
                return {
                    "ip_addresses_found": 0,
                    "requested_fields": requested_fields,
                    "filter_applied": f"{filter_field} = {filter_value}",
                    "message": "No IP addresses found matching the criteria",
                    "searched_addresses": address_filter
                    if address_filter
                    else "all IPs",
                }

        except Exception as e:
            logger.error(f"Filtered IP addresses query execution failed: {str(e)}")
            return {
                "error": f"Query execution failed: {str(e)}",
                "requested_fields": requested_fields,
                "filter_applied": f"{filter_field} = {filter_value}",
                "address_filter": address_filter,
            }
