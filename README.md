# Nautobot MCP Server

A Model Context Protocol (MCP) server that provides Claude with tools to interact with Nautobot via GraphQL and REST APIs.

## Features

- **10 MCP Tools** for device queries and metadata retrieval
- **Modular Architecture** - easy to add new queries without code changes
- **Combined matching** - exact and pattern matching for name/location queries
- **Comprehensive logging** - errors logged and returned to user
- **Testing utilities** - connection testing and interactive tool testing
- **GraphQL & REST** - supports both Nautobot API types

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configuration
```bash
cp .env.example .env
# Edit .env with your Nautobot credentials
```

### 3. Test Connection
```bash
python test_server.py connection
```

### 4. Run Server
```bash
python mcp_server.py
```

### 5. Test with MCP Inspector (Recommended)
```bash
npm install -g @modelcontextprotocol/inspector
npx @modelcontextprotocol/inspector python mcp_server.py
```

### 6. Configure Claude Desktop to Use This Server
Add the following configuration to your Claude Desktop config file:

**macOS/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nautobot-mcp": {
      "command": "python",
      "args": ["/path/to/your/nautobot-mcp/mcp_server.py"],
      "env": {
        "NAUTOBOT_URL": "http://your-nautobot-instance.com",
        "NAUTOBOT_TOKEN": "your-api-token"
      }
    }
  }
}
```

**Important Notes:**
- Replace `/path/to/your/nautobot-mcp/` with the actual absolute path to your project directory
- Replace `http://your-nautobot-instance.com` with your actual Nautobot URL
- Replace `your-api-token` with your actual Nautobot API token
- Restart Claude Desktop after making configuration changes
- Ensure Python dependencies are installed in your system Python or the Python environment Claude Desktop can access

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `devices_by_name` | Find devices by name | `name_filter`, `match_type` (exact/pattern) |
| `devices_by_location` | Find devices by location | `location_filter`, `match_type` (exact/pattern) |
| `devices_by_role` | Find devices by role | `role_filter` |
| `devices_by_tag` | Find devices by tag | `tag_filter` |
| `devices_by_devicetype` | Find devices by device type | `devicetype_filter` |
| `devices_by_manufacturer` | Find devices by manufacturer | `manufacturer_filter` |
| `devices_by_platform` | Find devices by platform | `platform_filter` |
| `get_roles` | Get available device roles | `role_filter` (optional) |
| `get_tags` | Get available tags | `tags_filter` (optional) |
| `get_custom_fields` | Get custom field definitions | None |

## Testing

### Run All Tests
```bash
python test_server.py all
```

### Interactive Testing
```bash
python test_server.py interactive
```

### Manual JSON-RPC Testing
```bash
# List tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python mcp_server.py

# Call a tool
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"devices_by_name","arguments":{"name_filter":["switch"],"match_type":"pattern"}}}' | python mcp_server.py
```

## Configuration

### Environment Variables
- `NAUTOBOT_URL` - Nautobot instance URL (default: http://127.0.0.1:8080)
- `NAUTOBOT_TOKEN` - API authentication token (default: 0123456789abcdef0123456789abcdef01234567)

### Example Tool Call
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "devices_by_name",
    "arguments": {
      "name_filter": ["switch"],
      "match_type": "pattern"
    }
  }
}
```

## Architecture

- **nautobot_client.py** - API client with GraphQL/REST methods and logging
- **mcp_server.py** - MCP server with tool definitions and query execution
- **test_server.py** - Testing utilities for validation and debugging

## Error Handling

- All errors are logged to console and returned in MCP responses
- Connection failures are handled gracefully
- GraphQL errors are parsed and returned with context
- Network timeouts are configured (30s default)

## Using with Claude Desktop

Once configured, you can use natural language to query your Nautobot instance:

**Example prompts:**
- "Show me all devices with 'switch' in the name"
- "Find devices in the datacenter location"
- "List all devices with the 'production' tag"
- "What device roles are available?"
- "Show me all Cisco devices"

**Available tools will appear in Claude Desktop with descriptions:**
- 🔧 devices_by_name - Find devices by name
- 📍 devices_by_location - Find devices by location
- 🏷️ devices_by_tag - Find devices by tag
- And 7 more device query tools...

## Troubleshooting

### Common Issues

**1. "Server not found" in Claude Desktop**
- Verify the absolute path to `mcp_server.py` is correct
- Ensure Python is accessible from Claude Desktop's environment
- Check that all dependencies are installed: `pip install -r requirements.txt`

**2. "Connection failed" errors**
- Verify `NAUTOBOT_URL` and `NAUTOBOT_TOKEN` are correct
- Test connection manually: `python test_server.py connection`
- Check Nautobot instance is accessible from your machine

**3. "GraphQL errors" in responses**
- Verify your API token has appropriate permissions in Nautobot
- Check Nautobot logs for authentication/authorization issues
- Ensure GraphQL endpoint is enabled: `{nautobot_url}/graphql/`

**4. Tools not appearing in Claude Desktop**
- Restart Claude Desktop after configuration changes
- Check Claude Desktop logs for MCP connection errors
- Verify JSON syntax in `claude_desktop_config.json`

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export PYTHONPATH="$PYTHONPATH:$(pwd)"
NAUTOBOT_DEBUG=1 python mcp_server.py
```

## Development

The server uses a **modular query system** that makes adding new queries simple. See `DEVELOPMENT.md` for detailed information.

### Quick: Add a New Query
```bash
# Interactive generator
python add_query.py interactive

# Test your new query
python test_queries.py all
```

### Testing Framework
```bash
# Test all components
python test_queries.py all

# Interactive testing
python test_queries.py interactive

# Test individual components  
python test_queries.py registration
python test_queries.py schemas
python test_queries.py live
```

### Project Structure
```
queries/
├── base.py              # Base query classes
├── devices/             # Device query modules  
│   ├── by_name.py
│   ├── by_location.py
│   └── ...
└── metadata/            # Metadata query modules
    ├── roles.py
    ├── tags.py
    └── ...
```

### Adding New Queries (Manual)
1. **Create query module** in `queries/devices/` or `queries/metadata/`
2. **Inherit from base class** (`SimpleGraphQLQuery`, `CombinedMatchQuery`, or `BaseQuery`)
3. **Update imports** in `queries/__init__.py`
4. **Test** with `python test_queries.py interactive`

Example:
```python
# queries/devices/by_status.py
from ..base import SimpleGraphQLQuery

class DevicesByStatusQuery(SimpleGraphQLQuery):
    def __init__(self):
        super().__init__(
            tool_name="devices_by_status",
            description="Find devices by status",
            query="query devices_by_status($status_filter: [String]) {...}",
            required_params=["status_filter"]
        )
```

### Architecture
- **Modular**: Each query is a separate module
- **Type-safe**: Base classes with validation  
- **Testable**: Comprehensive testing framework
- **Extensible**: Easy to add new query types

### Logging
- Set `logging.basicConfig(level=logging.DEBUG)` for verbose output
- Logs include query execution, errors, and connection status
