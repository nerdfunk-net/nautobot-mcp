# Locations
 - show all locations
 - show location {location_name}
## prompts

## query

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
    }