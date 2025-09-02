"""
Status resolver for converting status names to IDs
"""

from typing import Optional, Tuple
from .base_resolver import BaseResolver


class StatusResolver(BaseResolver):
    """Resolver for status names to IDs using REST API"""
    
    def get_cache_type(self) -> str:
        return "status"
    
    async def _resolve_from_source(self, name: str) -> Tuple[Optional[str], Optional[str]]:
        """Resolve status name to ID using REST API"""
        try:
            # Use REST API to get statuses
            statuses_response = self.client.rest_get(f"/api/extras/statuses/?name={name}")
            statuses = statuses_response.get("results", [])
            
            if statuses:
                status_id = statuses[0]["id"]
                return status_id, None
                
            return self._handle_not_found(name)
            
        except Exception as e:
            return self._handle_api_error(name, e)