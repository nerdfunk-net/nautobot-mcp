"""
ID Resolution Cache System
"""

from typing import Dict, Any, Optional
from time import time
import logging

logger = logging.getLogger(__name__)


class IDCache:
    """Cache for resolved name-to-ID mappings with expiration"""
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minute TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
        logger.info(f"Initialized ID cache with TTL {ttl_seconds}s")
    
    def get(self, cache_type: str, name: str) -> Optional[str]:
        """Get cached ID for a name"""
        cache_key = f"{cache_type}:{name.lower()}"
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if time() - entry["timestamp"] < self.ttl:
                logger.debug(f"Cache hit: {cache_key} -> {entry['id']}")
                return entry["id"]
            else:
                # Expired, remove from cache
                logger.debug(f"Cache expired: {cache_key}")
                del self.cache[cache_key]
        return None
    
    def set(self, cache_type: str, name: str, entity_id: str):
        """Cache an ID for a name"""
        cache_key = f"{cache_type}:{name.lower()}"
        self.cache[cache_key] = {
            "id": entity_id,
            "timestamp": time()
        }
        logger.debug(f"Cached: {cache_key} -> {entity_id}")
    
    def clear(self):
        """Clear all cached entries"""
        cache_count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cleared {cache_count} cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time()
        active_entries = 0
        expired_entries = 0
        
        for entry in self.cache.values():
            if current_time - entry["timestamp"] < self.ttl:
                active_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self.cache),
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "ttl_seconds": self.ttl
        }