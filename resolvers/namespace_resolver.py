"""
Namespace resolver for converting namespace names to IDs
"""

from typing import Optional, Tuple
from .base_resolver import BaseResolver
from queries import get_query


class NamespaceResolver(BaseResolver):
    """Resolver for namespace names to IDs using existing namespace query"""

    def get_cache_type(self) -> str:
        return "namespace"

    async def _resolve_from_source(
        self, name: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Resolve namespace name to ID using existing namespace query"""
        try:
            # Use existing namespace query
            namespace_query = get_query("query_namespaces_dynamic")
            result = namespace_query.execute(
                self.client,
                {"variable_name": "name", "variable_value": [name], "get_id": True},
            )

            if result.get("data", {}).get("namespaces"):
                namespaces = result["data"]["namespaces"]
                if namespaces:
                    namespace_id = namespaces[0]["id"]
                    return namespace_id, None

            return self._handle_not_found(name)

        except Exception as e:
            return self._handle_api_error(name, e)
