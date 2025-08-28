# Roles

## prompts
- show all roles of content type "ipam.addresses"
## query

    query Roles(
        $get_id: Boolean = false,
        $get_name: Boolean = false,
        $get_model: Boolean = false,
        $field_value: [String]
    ) {
    roles(enter_name_of_field_here: field_value) {
        id @include(if: $get_id)
        name @include(if: $get_name)
        content_types {
            id
            app_label
            model @include(if: $get_model)
        }
      }
    }
