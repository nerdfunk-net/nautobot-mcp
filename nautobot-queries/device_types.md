# Device Types
## prompts
  - show all device types
## query
    query (
        $get_id: Boolean = false,
        $get_model: Boolean = true,
        $get_manufacturer: Boolean = false,
        $get_devices: Boolean = false,
        $variable_value: [String],
    ) {
    device_types (enter_variable_name_here: $variable_value) {
        id @include(if: $get_id)
        model @include(if: $get_model)
        manufacturer @include(if: $get_manufacturer) {
            id @include(if: $get_id)
                name
            }
        }
        devices @include(if: $get_devices) {
            id @include(if: $get_id)
            name
        }
    }