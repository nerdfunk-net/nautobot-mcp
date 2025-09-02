"""
Secrets group resolver for converting secrets group names to IDs
"""

from typing import Optional, Tuple
from .base_resolver import BaseResolver
from queries import get_query


class SecretsGroupResolver(BaseResolver):
    """Resolver for secrets group names to IDs using existing secrets groups query"""

    def get_cache_type(self) -> str:
        return "secrets_group"

    async def _resolve_from_source(
        self, name: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Resolve secrets group name to ID using existing secrets groups query"""
        try:
            # Use existing secrets groups query
            secrets_group_query = get_query("query_secrets_groups_dynamic")
            result = secrets_group_query.execute(
                self.client,
                {"variable_name": "name", "variable_value": [name], "get_id": True},
            )

            if result.get("data", {}).get("secrets_groups"):
                secrets_groups = result["data"]["secrets_groups"]
                if secrets_groups:
                    group_id = secrets_groups[0]["id"]
                    return group_id, None

            return self._handle_not_found(name)

        except Exception as e:
            return self._handle_api_error(name, e)
