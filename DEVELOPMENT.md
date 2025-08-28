# Adding New Queries

## Quick Start

### Interactive Generator
```bash
python add_query.py interactive
```

### Manual Implementation

1. **Create query file** in `queries/devices/` or `queries/metadata/`:
```python
# queries/devices/by_status.py
from ..base import SimpleGraphQLQuery

class DevicesByStatusQuery(SimpleGraphQLQuery):
    def __init__(self):
        super().__init__(
            tool_name="devices_by_status",
            description="Find devices by status", 
            query="""
                query devices_by_status($status_filter: [String]) {
                    devices(status: $status_filter) {
                        id name
                        status { name }
                    }
                }""",
            required_params=["status_filter"]
        )
```

2. **Add import** to `queries/devices/__init__.py`:
```python
from .by_status import DevicesByStatusQuery

__all__ = [
    # ... existing imports
    'DevicesByStatusQuery'
]
```

3. **Register** in `queries/__init__.py`:
```python
from .devices import (
    # ... existing imports
    DevicesByStatusQuery
)

# Add to query_classes list:
query_classes = [
    # ... existing classes
    DevicesByStatusQuery,
]
```

4. **Test**:
```bash
python test_queries.py registration
```

## Query Types

### Simple GraphQL
```python
class MyQuery(SimpleGraphQLQuery):
    def __init__(self):
        super().__init__(
            tool_name="my_tool",
            description="Tool description",
            query="query my_query($param: [String]) { ... }",
            required_params=["param"],
            optional_params={"opt": {"type": "string"}}
        )
```

### Combined Match (exact/pattern)
```python 
class MyQuery(CombinedMatchQuery):
    def __init__(self):
        super().__init__(
            tool_name="my_tool",
            description="Tool description",
            exact_query="query { items(name: $filter) { ... } }",
            pattern_query="query { items(name__ire: $filter) { ... } }",
            filter_param="filter"
        )
```

### REST API
```python
class MyQuery(BaseQuery):
    def get_tool_name(self) -> str:
        return "my_rest_tool"
    
    def get_query_type(self) -> QueryType:
        return QueryType.REST
    
    def get_queries(self) -> str:
        return "/api/endpoint/"
```

## Testing
```bash
python test_queries.py all                # Full test suite
python test_queries.py interactive        # Test individual queries
python test_queries.py registration       # Test registration only
```

## File Structure
```
queries/
├── base.py                    # Base classes
├── devices/by_<criteria>.py   # Device queries  
└── metadata/<resource>.py     # Metadata queries
```

## Rules
- **tool_name**: Unique identifier Claude calls
- **description**: What Claude sees in tool list
- **required_params**: Must end with `_filter` for arrays
- **GraphQL variables**: Match parameter names exactly
- **Test**: Always test new queries before deployment