# Secret Groups
## prompts
  - show all secret groups
## query
    query(
        $get_id: Boolean = false,
        $get_description: Boolean = false,
        $get_secrets: Boolean = false,
        $variable_value: [String],
    ) {
    secrets_groups (enter_variable_name_here: $variable_value)
    {
        id @include(if: $get_id)
        name
        description @include(if: $get_description)
        secrets @include(if: $get_secrets) {
            id @include(if: $get_id)
            name
            description
        }
    }
    }