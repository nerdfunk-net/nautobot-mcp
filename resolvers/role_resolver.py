"""
Role resolver for converting role names to IDs
"""

from typing import Optional, Tuple
from .base_resolver import BaseResolver


class RoleResolver(BaseResolver):
    """Resolver for role names to IDs using REST API"""

    def get_cache_type(self) -> str:
        return "role"

    async def _resolve_from_source(
        self, name: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Resolve role name to ID using REST API"""
        try:
            # Use REST API to get roles
            roles_response = self.client.rest_get(f"/api/extras/roles/?name={name}")
            roles = roles_response.get("results", [])

            if roles:
                role_id = roles[0]["id"]
                return role_id, None

            return self._handle_not_found(name)

        except Exception as e:
            return self._handle_api_error(name, e)
