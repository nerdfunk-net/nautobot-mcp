"""
Base classes for Nautobot MCP query definitions
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union
from dataclasses import dataclass
from enum import Enum


class QueryType(Enum):
    GRAPHQL = "graphql"
    REST = "rest"


class MatchType(Enum):
    EXACT = "exact"
    PATTERN = "pattern"
    COMBINED = "combined"


@dataclass
class QueryVariant:
    """Represents a single query variant (e.g., exact vs pattern matching)"""

    name: str
    query: str
    description: str
    variables: List[str]


@dataclass
class ToolSchema:
    """MCP tool input schema definition"""

    type: str = "object"
    properties: Dict[str, Any] = None
    required: List[str] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.required is None:
            self.required = []


class BaseQuery(ABC):
    """Base class for all Nautobot queries"""

    def __init__(self):
        self.tool_name = self.get_tool_name()
        self.description = self.get_description()
        self.query_type = self.get_query_type()
        self.match_type = self.get_match_type()
        self.queries = self.get_queries()
        self.schema = self.get_input_schema()

    @abstractmethod
    def get_tool_name(self) -> str:
        """Return the MCP tool name"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Return the tool description"""
        pass

    @abstractmethod
    def get_query_type(self) -> QueryType:
        """Return the query type (GraphQL or REST)"""
        pass

    @abstractmethod
    def get_match_type(self) -> MatchType:
        """Return the matching strategy"""
        pass

    @abstractmethod
    def get_queries(self) -> Union[str, Dict[str, QueryVariant]]:
        """Return the query string(s)"""
        pass

    @abstractmethod
    def get_input_schema(self) -> ToolSchema:
        """Return the MCP tool input schema"""
        pass

    def execute(self, client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the query with the given arguments"""
        if self.query_type == QueryType.GRAPHQL:
            return self._execute_graphql(client, arguments)
        elif self.query_type == QueryType.REST:
            return self._execute_rest(client, arguments)
        else:
            raise ValueError(f"Unsupported query type: {self.query_type}")

    def _execute_graphql(self, client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL query"""
        if self.match_type == MatchType.COMBINED:
            # Handle combined exact/pattern matching
            match_type = arguments.get("match_type", "pattern")
            query_variant = self.queries.get(match_type)
            if not query_variant:
                raise ValueError(f"Unknown match type: {match_type}")
            query = query_variant.query
        else:
            query = (
                self.queries
                if isinstance(self.queries, str)
                else self.queries["default"].query
            )

        return client.graphql_query(query, arguments)

    def _execute_rest(self, client, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute REST query"""
        endpoint = (
            self.queries
            if isinstance(self.queries, str)
            else self.queries["default"].query
        )
        return client.rest_get(endpoint)

    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate query arguments against schema"""
        required_fields = self.schema.required
        for field in required_fields:
            if field not in arguments:
                raise ValueError(f"Missing required field: {field}")
        return True


class SimpleGraphQLQuery(BaseQuery):
    """Simplified base class for basic GraphQL queries"""

    def __init__(
        self,
        tool_name: str,
        description: str,
        query: str,
        required_params: List[str] = None,
        optional_params: Dict[str, Any] = None,
    ):
        self._tool_name = tool_name
        self._description = description
        self._query = query
        self._required_params = required_params or []
        self._optional_params = optional_params or {}
        super().__init__()

    def get_tool_name(self) -> str:
        return self._tool_name

    def get_description(self) -> str:
        return self._description

    def get_query_type(self) -> QueryType:
        return QueryType.GRAPHQL

    def get_match_type(self) -> MatchType:
        return MatchType.EXACT

    def get_queries(self) -> str:
        return self._query

    def get_input_schema(self) -> ToolSchema:
        properties = {}

        # Add required parameters
        for param in self._required_params:
            if param.endswith("_filter"):
                properties[param] = {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": f"{param.replace('_filter', '').replace('_', ' ').title()} to filter by",
                }
            else:
                properties[param] = {"type": "string"}

        # Add optional parameters
        properties.update(self._optional_params)

        return ToolSchema(
            type="object", properties=properties, required=self._required_params
        )


class CombinedMatchQuery(BaseQuery):
    """Base class for queries with exact/pattern matching variants"""

    def __init__(
        self,
        tool_name: str,
        description: str,
        exact_query: str,
        pattern_query: str,
        filter_param: str,
    ):
        self._tool_name = tool_name
        self._description = description
        self._exact_query = exact_query
        self._pattern_query = pattern_query
        self._filter_param = filter_param
        super().__init__()

    def get_tool_name(self) -> str:
        return self._tool_name

    def get_description(self) -> str:
        return self._description

    def get_query_type(self) -> QueryType:
        return QueryType.GRAPHQL

    def get_match_type(self) -> MatchType:
        return MatchType.COMBINED

    def get_queries(self) -> Dict[str, QueryVariant]:
        return {
            "exact": QueryVariant(
                name="exact",
                query=self._exact_query,
                description="Exact match",
                variables=[self._filter_param],
            ),
            "pattern": QueryVariant(
                name="pattern",
                query=self._pattern_query,
                description="Pattern match",
                variables=[self._filter_param],
            ),
        }

    def get_input_schema(self) -> ToolSchema:
        return ToolSchema(
            type="object",
            properties={
                self._filter_param: {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": f"{self._filter_param.replace('_filter', '').replace('_', ' ').title()} to search for",
                },
                "match_type": {
                    "type": "string",
                    "enum": ["exact", "pattern"],
                    "default": "pattern",
                    "description": "Type of matching: exact for exact match, pattern for regex-like matching",
                },
            },
            required=[self._filter_param],
        )
