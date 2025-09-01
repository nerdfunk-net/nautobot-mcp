# Prefixes

## prompts
  - show all prefixes
  - show prefix {prefix}
## query
    query Prefixes(
    $get_id: Boolean = false,
    $get_prefix_length: Boolean = true,
    $get_ip_version: Boolean = true,
    $get_broadcast: Boolean = true,
    $get_description: Boolean = true,
    $get_parent: Boolean = true,
    $get_status: Boolean = true,
    $get_namespace: Boolean = true,
    $get_tags: Boolean = true,
    $get_vlan: Boolean = true,
    $get_location: Boolean = true,
    $get_vrf_assignments: Boolean = true,
    $get_custom_field_data: Boolean = true,
    $variable_value: [String],
    ) {
    prefixes (enter_variable_name_here: $variable_value) {
        id @include(if: $get_id)
        prefix
        ip_version @include(if: $get_ip_version)
        prefix_length @include(if: $get_prefix_length)
        broadcast @include(if: $get_broadcast)
        description @include(if: $get_description)
        _custom_field_data @include(if: $get_custom_field_data)
        status @include(if: $get_status) {
        id @include(if: $get_id)
        name
        }
        namespace @include(if: $get_namespace) {
        id @include(if: $get_id)
        name
        }
        tags @include(if: $get_tags) {
        id @include(if: $get_id)
        name
        }
        vlan @include(if: $get_vlan) {
        id @include(if: $get_id)
        vid
        vlan_group {
            id
        }
        name
        }
        parent @include(if: $get_parent) {
        id @include(if: $get_id)
        prefix
        prefix_length
        parent {
            id
        }
        }
        location @include(if: $get_location) {
        id @include(if: $get_id)
        name
        }
        vrf_assignments @include(if: $get_vrf_assignments) {
        id @include(if: $get_id)
        vrf {
            id
        }
        }
    }
    }