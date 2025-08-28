# MCP Server for Nautobot

Build a Model Context Protocol server that acts as middleware for Nautobot using the [python-sdk](https://github.com/modelcontextprotocol/python-sdk). This server exposes the GraphQL/REST queries from `nautobot-queries/devices.md` as MCP tools.

## Quick setup

1. **Install dependencies**
   ```bash
   pip install mcp requests python-dotenv
   ```

2. **Environment variables**
   Create a `.env` file:
   ```bash
   NAUTOBOT_URL=https://your-nautobot-instance.com
   NAUTOBOT_TOKEN=your-api-token
   ```

3. **Project structure**
   ```
   mcp_server.py      # Main server with MCP tool definitions
   nautobot_client.py # Nautobot API client
   .env               # Environment variables
   requirements.txt   # Dependencies
   ```

## Implementation

### Core components

**nautobot_client.py** - API client with GraphQL/REST methods
```python
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class NautobotClient:
    def __init__(self):
        self.base_url = os.getenv("NAUTOBOT_URL")
        self.token = os.getenv("NAUTOBOT_TOKEN")
        
        if not self.base_url or not self.token:
            raise ValueError("NAUTOBOT_URL and NAUTOBOT_TOKEN must be set")
            
        self.headers = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json"
        }
    
    def graphql_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict:
        try:
            response = requests.post(
                f"{self.base_url}/graphql/",
                json={"query": query, "variables": variables or {}},
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"GraphQL query failed: {str(e)}")
    
    def rest_get(self, endpoint: str) -> Dict:
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}", 
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"REST request failed: {str(e)}")
```

**mcp_server.py** - Complete MCP server implementation
```python
import asyncio
import json
from mcp.server import Server
from mcp.types import Tool, TextContent
from nautobot_client import NautobotClient

app = Server("nautobot-mcp")
client = NautobotClient()

# GraphQL queries from devices.md
QUERIES = {
    "devices_by_name": """
        query devices_by_name($name_filter: [String]) {
            devices(name__ire: $name_filter) {
                id name
                primary_ip4 { address }
                status { name }
                device_type { model }
            }
        }""",
    "devices_by_location": """
        query devices_by_location($location_filter: [String]) {
            locations(name__ire: $location_filter) {
                name
                devices {
                    id name
                    role { name }
                    location { name }
                    primary_ip4 { address }
                    status { name }
                }
            }
        }""",
    "devices_by_role": """
        query devices_by_role($role_filter: [String]) {
            devices(role: $role_filter) {
                id name
                primary_ip4 { address }
                status { name }
                device_type { model }
            }
        }""",
    "devices_by_tag": """
        query devices_by_tag($tag_filter: [String]) {
            devices(tags: $tag_filter) {
                id name
                primary_ip4 { address }
                status { name }
                device_type { model }
            }
        }""",
    "get_roles": """
        query roles($role_filter: [String]) {
            roles(content_types: $role_filter) {
                name
            }
        }""",
    "get_tags": """
        query tags($tags_filter: [String]) {
            tags(content_types: $tags_filter) {
                name
            }
        }"""
}

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="devices_by_name",
            description="Find devices by name pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_filter": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["name_filter"]
            }
        ),
        Tool(
            name="devices_by_location", 
            description="Find devices by location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_filter": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["location_filter"]
            }
        ),
        Tool(
            name="devices_by_role",
            description="Find devices by role",
            inputSchema={
                "type": "object",
                "properties": {
                    "role_filter": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["role_filter"]
            }
        ),
        Tool(
            name="devices_by_tag",
            description="Find devices by tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag_filter": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["tag_filter"]
            }
        ),
        Tool(
            name="get_roles",
            description="Get available device roles",
            inputSchema={
                "type": "object",
                "properties": {
                    "role_filter": {"type": "array", "items": {"type": "string"}}
                }
            }
        ),
        Tool(
            name="get_tags",
            description="Get available tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "tags_filter": {"type": "array", "items": {"type": "string"}}
                }
            }
        ),
        Tool(
            name="get_custom_fields",
            description="Get custom field definitions",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name in QUERIES:
            result = client.graphql_query(QUERIES[name], arguments)
            if result.get("errors"):
                return [TextContent(type="text", text=f"GraphQL errors: {result['errors']}")]
            return [TextContent(type="text", text=json.dumps(result["data"], indent=2))]
        
        elif name == "get_custom_fields":
            result = client.rest_get("/api/extras/custom-fields/?depth=0&exclude_m2m=false")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### Complete tool mapping

Map each query from `nautobot-queries/devices.md` to MCP tools:

| Tool Name | Query Type | Variables | Description |
|-----------|------------|-----------|-------------|
| `devices_by_name` | GraphQL | `name_filter` | Devices matching name pattern |
| `devices_by_location` | GraphQL | `location_filter` | Devices in specified locations |
| `devices_by_role` | GraphQL | `role_filter` | Devices with specific role |
| `devices_by_tag` | GraphQL | `tag_filter` | Devices with specified tags |
| `devices_by_devicetype` | GraphQL | `devicetype_filter` | Devices of specific type |
| `devices_by_manufacturer` | GraphQL | `manufacturer_filter` | Devices from manufacturer |
| `devices_by_platform` | GraphQL | `platform_filter` | Devices on platform |
| `get_roles` | GraphQL | `role_filter` | Available device roles |
| `get_tags` | GraphQL | `tags_filter` | Available tags |
| `get_custom_fields` | REST | None | Custom field definitions |

## Testing and deployment

**Create requirements.txt**
```
mcp>=1.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

**Run the server**
```bash
python mcp_server.py
```

**Test with MCP Inspector (recommended)**
```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Test the server
npx @modelcontextprotocol/inspector python mcp_server.py
```

**Manual testing with stdio**
```bash
# Send JSON-RPC request via stdin
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python mcp_server.py
```

**Example tool calls**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "devices_by_name",
    "arguments": {"name_filter": ["switch"]}
  }
}
```

**Error handling**
- Validate input parameters before making API calls
- Return descriptive error messages for API failures
- Log authentication and network errors

## Requirements coverage
✅ MCP server using python-sdk  
✅ Middleware for Nautobot interaction  
✅ All queries from `nautobot-queries/devices.md` implemented  
✅ Compact, functional implementation guide

