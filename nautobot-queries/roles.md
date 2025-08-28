# Roles

## prompts
- show all roles
## query

    query Roles(
        $get_id: Boolean = false,
        $get_name: Boolean = false,
        $get_model: Boolean = false,
        $name_filter: [String]
    ) {
    roles(name: $name_filter) {
        id @include(if: $get_id)
        name @include(if: $get_name)
        content_types {
            id
            app_label
            model @include(if: $get_model)
        }
      }
    }