# Tags
## prompts
  - show all tags
## query
    query(
        $get_id: Boolean = false,
        $get_name: Boolean = true,
        $get_description: Boolean = false,
        $get_content_types: Boolean = false,
        $variable_value: [String],
    ) {
    tags (enter_variable_name_here: $variable_value) {
        id @include(if: $get_id)
        name @include(if: $get_name)
        description @include(if: $get_description)
        content_types @include(if: $get_content_types) {
            id @include(if: $get_id)
            model
        }
    }
    }
