"""
Base resolver abstract class for ID resolution
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class BaseResolver(ABC):
    """Abstract base class for all ID resolvers"""

    def __init__(self, cache, client):
        self.cache = cache
        self.client = client
        self.cache_type = self.get_cache_type()

    @abstractmethod
    def get_cache_type(self) -> str:
        """Return the cache type identifier for this resolver"""
        pass

    @abstractmethod
    async def _resolve_from_source(
        self, name: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Resolve name to ID from the data source (GraphQL/REST API)

        Returns:
            Tuple[Optional[str], Optional[str]]: (id, error_message)
        """
        pass

    async def resolve(self, name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Resolve name to ID using cache first, then source

        Returns:
            Tuple[Optional[str], Optional[str]]: (id, error_message)
        """
        # Check cache first
        cached_id = self.cache.get(self.cache_type, name)
        if cached_id:
            logger.debug(f"Cache hit for {self.cache_type}:{name} -> {cached_id}")
            return cached_id, None

        # Cache miss, resolve from source
        logger.debug(f"Cache miss for {self.cache_type}:{name}, resolving from source")
        entity_id, error = await self._resolve_from_source(name)

        if entity_id and not error:
            # Cache successful resolution
            self.cache.set(self.cache_type, name, entity_id)
            logger.debug(f"Cached {self.cache_type}:{name} -> {entity_id}")

        return entity_id, error

    def _handle_api_error(self, name: str, exception: Exception) -> Tuple[None, str]:
        """Helper method to handle API errors consistently"""
        error_msg = f"Error resolving {self.cache_type} '{name}': {str(exception)}"
        logger.error(error_msg)
        return None, error_msg

    def _handle_not_found(self, name: str) -> Tuple[None, str]:
        """Helper method to handle not found cases consistently"""
        error_msg = f"{self.cache_type.title()} '{name}' not found"
        logger.warning(error_msg)
        return None, error_msg
