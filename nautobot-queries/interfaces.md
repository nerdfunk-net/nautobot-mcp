# Interfaces
## prompts
  - show all interfaces
## query
    query(
        $get_id: Boolean = false,
        $get_name: Boolean = true,
        $get_enabled: Boolean = false,
        $get_label: Boolean = false,
        $get_type: Boolean = false,
        $get_status: Boolean = false,
        $get_role: Boolean = false,
        $get_description: Boolean = false,
        $get_device: Boolean = false,
        $get_tags: Boolean = false,
        $get_interface_redundancy_groups: Boolean = false,
        $variable_value: [String],
    ) {
    interfaces (enter_variable_name_here: $variable_value) {
        id @include(if: $get_id)
        name @include(if: $get_name)
        description @include(if: $get_description)
        enabled @include(if: $get_enabled)
        label @include(if: $get_label)
        status @include(if: $get_status) {
        id @include(if: $get_id)
            name
        }
        role @include(if: $get_role) {
            id @include(if: $get_id)
            name
        }
        tags @include(if: $get_tags) {
            id @include(if: $get_id)
            name
        }
        type @include(if: $get_type)
        interface_redundancy_groups @include(if: $get_interface_redundancy_groups) {
            id
            name
        }
        device @include(if: $get_device) {
            id @include(if: $get_id)
            name
        }
    }
    }