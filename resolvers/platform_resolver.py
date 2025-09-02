"""
Platform resolver for converting platform names to IDs
"""

from typing import Optional, Tuple
import logging
from .base_resolver import BaseResolver

logger = logging.getLogger(__name__)


class PlatformResolver(BaseResolver):
    """Resolver for platform names to IDs using REST API, or None for autodetection"""

    def get_cache_type(self) -> str:
        return "platform"

    async def _resolve_from_source(
        self, name: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Resolve platform name to ID using REST API, or return None for autodetection"""
        # If no platform specified, use None for autodetection
        if not name or name.lower() in ["auto", "autodetect", "detect", ""]:
            return None, None

        try:
            # Use REST API to get platforms
            platforms_response = self.client.rest_get(
                f"/api/dcim/platforms/?name={name}"
            )
            platforms = platforms_response.get("results", [])

            if platforms:
                platform_id = platforms[0]["id"]
                return platform_id, None

            # Platform not found, use None for autodetection
            logger.info(f"Platform '{name}' not found, using autodetection (None)")
            return None, None

        except Exception as e:
            # On error, fallback to autodetection
            logger.warning(
                f"Error resolving platform '{name}': {str(e)}, using autodetection (None)"
            )
            return None, None
