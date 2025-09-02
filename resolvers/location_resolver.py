"""
Location resolver for converting location names to IDs
"""

from typing import Optional, Tuple
from .base_resolver import BaseResolver
from queries import get_query


class LocationResolver(BaseResolver):
    """Resolver for location names to IDs using existing location query"""

    def get_cache_type(self) -> str:
        return "location"

    async def _resolve_from_source(
        self, name: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Resolve location name to ID using existing location query"""
        try:
            # Use existing location query
            location_query = get_query("query_locations_dynamic")
            result = location_query.execute(
                self.client,
                {"variable_name": "name", "variable_value": [name], "get_id": True},
            )

            if result.get("data", {}).get("locations"):
                locations = result["data"]["locations"]
                if locations:
                    location_id = locations[0]["id"]
                    return location_id, None

            return self._handle_not_found(name)

        except Exception as e:
            return self._handle_api_error(name, e)
