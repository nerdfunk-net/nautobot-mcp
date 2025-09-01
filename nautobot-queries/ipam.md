# IPAM

## prompts
- show {list_of_properties} of the ip address {address_filter}
## query
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
      $address_filter: [String],
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
    }


## prompts
- show {list_of_properties} of the ip address {address_filter} that have {field} = {field_value}
## query
    query IPaddresses_customized(
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
      $address_filter: [String]
      $field_value: [String]
    ) 
    {
      ip_addresses(address: $address_filter, enter_name_of_field_here: field_value)
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
    }