"""
Nautobot MCP Query Registry

This module provides a centralized registry of all available queries.
New queries are automatically discovered and registered.
"""

from typing import Dict, List
from .base import BaseQuery

# Import all query modules
from .devices import (
    DynamicDeviceQuery
)

from .locations import (
    DynamicLocationQuery
)

from .statuses import (
    DynamicStatusQuery
)

from .roles import (
    DynamicRoleQuery
)

from .metadata import (
    GetRolesQuery,
    GetTagsQuery,
    GetCustomFieldsQuery
)

from .ipam import (
    DynamicIPAMQuery,
    IPAddressesFilteredQuery
)

from .prefixes import (
    DynamicPrefixQuery
)

class QueryRegistry:
    """Central registry for all MCP queries"""
    
    def __init__(self):
        self._queries: Dict[str, BaseQuery] = {}
        self._initialize_queries()
    
    def _initialize_queries(self):
        """Initialize and register all available queries"""
        query_classes = [
            # Device queries
            DynamicDeviceQuery,
            
            # Location queries
            DynamicLocationQuery,
            
            # Status queries
            DynamicStatusQuery,
            
            # Role queries
            DynamicRoleQuery,
            
            # IPAM queries
            DynamicIPAMQuery,
            IPAddressesFilteredQuery,
            
            # Prefix queries
            DynamicPrefixQuery,
            
            # Metadata queries
            GetRolesQuery,
            GetTagsQuery,
            GetCustomFieldsQuery
        ]
        
        for query_class in query_classes:
            query_instance = query_class()
            self._queries[query_instance.tool_name] = query_instance
    
    def get_query(self, tool_name: str) -> BaseQuery:
        """Get a query by tool name"""
        if tool_name not in self._queries:
            raise ValueError(f"Unknown tool: {tool_name}")
        return self._queries[tool_name]
    
    def get_all_queries(self) -> Dict[str, BaseQuery]:
        """Get all registered queries"""
        return self._queries.copy()
    
    def get_tool_names(self) -> List[str]:
        """Get all available tool names"""
        return list(self._queries.keys())
    
    def register_query(self, query: BaseQuery):
        """Register a new query dynamically"""
        self._queries[query.tool_name] = query
    
    def list_queries_by_category(self) -> Dict[str, List[str]]:
        """Group queries by category for easier management"""
        categories = {
            "devices": [],
            "ipam": [],
            "metadata": [],
            "other": []
        }
        
        for tool_name in self._queries.keys():
            if tool_name.startswith("devices_"):
                categories["devices"].append(tool_name)
            elif tool_name.startswith("get_ip"):
                categories["ipam"].append(tool_name)
            elif tool_name.startswith("get_"):
                categories["metadata"].append(tool_name)
            else:
                categories["other"].append(tool_name)
        
        return categories

# Global registry instance
query_registry = QueryRegistry()

# Convenience functions
def get_query(tool_name: str) -> BaseQuery:
    """Get a query by tool name"""
    return query_registry.get_query(tool_name)

def get_all_queries() -> Dict[str, BaseQuery]:
    """Get all registered queries"""
    return query_registry.get_all_queries()

def register_query(query: BaseQuery):
    """Register a new query"""
    query_registry.register_query(query)