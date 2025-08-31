# Devices

## prompts
- show all devices in location {locatio_name}
- show device {device_name}
## query
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
    }