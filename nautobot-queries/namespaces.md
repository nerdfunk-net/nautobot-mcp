# namespaces
## prompts
  - show all namespaces 
## query
    query (
        $get_id: Boolean = false,
        $get_description: Boolean = false,
        $get_location: Boolean = false,
        $get_tags: Boolean = false,
        $variable_value: [String],
    ) {
    namespaces (enter_variable_name_here: $variable_value) 
    {
        id @include(if: $get_id)
        name
        description @include(if: $get_description)
        location @include(if: $get_location) {
            id @include(if: $get_id)
            name
        }
        tags @include(if: $get_tags) {
            id @include(if: $get_id)
            name
        }
    }
    }