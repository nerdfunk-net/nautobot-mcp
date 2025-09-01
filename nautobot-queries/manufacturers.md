# Manufacturers
## prompts
  - show all manufacturers
## query
    query(
        $get_id: Boolean = false,
        $get_name: Boolean = true,
        $get_description: Boolean = false,
        $get_device_types: Boolean = false,
        $variable_value: [String],
    ) {
    manufacturers (enter_variable_name_here: $variable_value) {
        id @include(if: $get_id)
        name @include(if: $get_name)
        description @include(if: $get_description)
        device_types @include(if: $get_device_types) {
            id @include(if: $get_id)
            model
        }
    }
    }