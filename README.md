# Nautobot MCP Server

A Model Context Protocol (MCP) server that provides Claude with powerful tools to interact with Nautobot using natural language queries and dynamic GraphQL filtering.

## Features

- **🤖 Natural Language Queries** - Use plain English to query your network infrastructure
- **⚡ Dynamic Filtering** - Filter by any property with automatic field mapping and validation
- **🔍 Advanced Search** - Supports lookup expressions (contains, starts with, regex, etc.)
- **🛡️ Smart Validation** - Automatic field name mapping with helpful error suggestions
- **📊 Multiple Resource Types** - Devices, locations, IP addresses, prefixes, device types, and more
- **🎯 Custom Field Support** - Query custom fields with proper type handling
- **📝 MCP Prompts** - Pre-configured prompt templates for common queries
- **🔧 Modular Architecture** - Easy to extend with new resource types
- **📋 Comprehensive Logging** - Detailed query execution and error information

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

### 🚀 Dynamic Query Tools
These tools support natural language prompts and advanced filtering:

| Tool | Description | Example Prompts |
|------|-------------|-----------------|
| **`query_devices_dynamic`** | Query devices with dynamic filtering | `"show device router1"`, `"devices with name contains core"`, `"devices in location datacenter1"` |
| **`query_locations_dynamic`** | Query locations with dynamic filtering | `"show location datacenter1"`, `"locations with status active"`, `"sites in region west"` |
| **`query_ipam_dynamic`** | Query IP addresses with dynamic filtering | `"show ip address 192.168.1.1"`, `"ip addresses with dns_name contains server"`, `"addresses with cf_environment production"` |
| **`query_prefixes_dynamic`** | Query network prefixes with dynamic filtering | `"show prefix 10.0.0.0/8"`, `"prefixes within 172.16.0.0/12"`, `"prefixes with length 24"` |
| **`query_device_types_dynamic`** | Query device types with dynamic filtering | `"show all device types"`, `"device types with vendor cisco"`, `"models contains c9300"` |

### 📊 Metadata Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| **`get_roles`** | Get available device roles | `role_filter` (optional) |
| **`get_tags`** | Get available tags | `tags_filter` (optional) |
| **`get_custom_fields`** | Get custom field definitions | None |

### 🎯 Legacy Query Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `get_ip_addresses` | Get IP address information (filtered) | `address_filter`, `fields` |

### ✨ Key Features of Dynamic Tools:
- **🗣️ Natural Language**: Use plain English descriptions
- **🔄 Field Mapping**: Common aliases automatically mapped (e.g., `hostname` → `name`, `site` → `location`)
- **🔍 Lookup Expressions**: Advanced search with `__ic` (contains), `__isw` (starts with), `__re` (regex), etc.
- **🛠️ Custom Fields**: Support for `cf_fieldname` custom field queries
- **✅ Validation**: Helpful error messages with field suggestions

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

## 🎯 Prompt Examples

Once configured, you can use natural language to query your Nautobot instance with these example prompts:

### 🖥️ Device Queries
```
"Show device router1"
"Find all devices with name containing 'core'"
"Show devices in location datacenter1" 
"List devices with role firewall"
"Show devices with hostname starts with 'sw-'"
"Find devices where vendor is cisco"
"Show all properties of device spine01"
"Devices with status active in location lab"
"Show devices with custom field cf_environment equal to production"
```

### 📍 Location Queries
```
"Show location datacenter1"
"Find locations with status active"
"Show all sites in region west-coast"
"List locations with name contains 'branch'"
"Show sites with address containing 'New York'"
"Find locations where tenant is customer1"
```

### 🌐 IP Address & Network Queries
```
"Show ip address 192.168.1.1"
"Find IP addresses with dns_name contains 'server'"
"Show addresses with status reserved"
"List IP addresses with custom field cf_vrf production"
"Find addresses assigned to device router1"
"Show prefix 10.0.0.0/8"
"List prefixes within 172.16.0.0/12"
"Find prefixes with length 24"
"Show prefixes in location datacenter1"
```

### 🔧 Device Type & Hardware Queries  
```
"Show all device types"
"Find device types with vendor cisco"
"Show models containing 'c9300'"
"List device types with manufacturer juniper"
"Show all catalyst models"
```

### 📊 Metadata Queries
```
"What device roles are available?"
"Show all tags in the system"
"List custom fields for devices"
"Show available statuses"
```

### 🔍 Advanced Search Examples
```
"Show devices with name not equal to 'test'"
"Find devices where location ends with '-dc'"  
"List IP addresses with dns_name starts with 'web-'"
"Show prefixes with description contains 'mgmt'"
"Find device types where model regex matches 'c[0-9]+'"
```

### 💡 MCP Prompt Templates
The server also provides pre-configured prompt templates accessible through Claude:
- **Device Details**: "Show all properties of device {device_name}"
- **Location Devices**: "Show the name and IP address of all devices in location {location_name}"
- **IP Lookup**: "Where do I find the address {ip_address}?"
- **Prefix Search**: "List the prefixes that are included in {prefix_cidr}"

## 🛠️ Parameter Mapping & Validation

The dynamic query system includes intelligent parameter mapping and validation to make queries more intuitive and error-resistant.

### 🔄 Automatic Field Mapping

Common field aliases are automatically mapped to their correct GraphQL field names:

| Resource | Alias → Correct Field | Example |
|----------|----------------------|---------|
| **Devices** | `hostname` → `name` | `"devices with hostname router1"` |
| | `site` → `location` | `"devices in site datacenter1"` |
| | `vendor` → `device_type__manufacturer` | `"devices with vendor cisco"` |
| | `ip` → `primary_ip4` | `"devices with ip 192.168.1.1"` |
| **Locations** | `site` → `name` | `"show site headquarters"` |
| | `region` → `parent` | `"locations in region west"` |
| | `address` → `physical_address` | `"sites with address contains NYC"` |
| **IP Addresses** | `hostname` → `dns_name` | `"ips with hostname web-server"` |
| | `ip` → `address` | `"show ip 10.0.0.1"` |
| **Device Types** | `vendor` → `manufacturer` | `"device types with vendor juniper"` |
| | `name` → `model` | `"show device type c9300"` |

### ✅ Smart Validation

When an invalid field name is provided, the system offers helpful suggestions:

**Example Error Response:**
```
Invalid field name: 'invalid_field'. 
Did you mean 'name'? 
Available fields: name, location, role, status, device_type, platform, tags, tenant, rack, serial, asset_tag, primary_ip4, interfaces. 
For custom fields, use 'cf_fieldname' format.
```

**Fuzzy Matching**: The system uses intelligent fuzzy matching to suggest the most likely intended field:
- `"loction"` → suggests `"location"`
- `"manufacurer"` → suggests `"manufacturer"`  
- `"addres"` → suggests `"address"`

### 🎯 Custom Field Support

Custom fields are automatically detected and handled with proper typing:

**Standard Fields** (Arrays):
```graphql
$variable_value: [String]
```

**Custom Fields** (Single Values):
```graphql  
$variable_value: String
```

**Usage Examples**:
```
"devices with cf_environment production"
"ip addresses with cf_vrf management"  
"locations with cf_criticality high"
```

### 🔍 Validation Features

1. **Field Existence**: Validates field names against available GraphQL fields
2. **Type Safety**: Ensures proper parameter types (String vs Array)
3. **Helpful Messages**: Provides specific suggestions and available options
4. **Logging**: Logs field mappings for transparency and debugging

**Example Field Mapping Log**:
```
INFO: Mapped field 'hostname' to 'name'
INFO: Mapped field 'site' to 'location'  
INFO: Mapped field 'vendor' to 'device_type__manufacturer'
```

### 💡 Best Practices

1. **Use Natural Terms**: The system understands common network terminology
2. **Custom Fields**: Always prefix with `cf_` (e.g., `cf_environment`) 
3. **Case Insensitive**: Field mapping is case-insensitive
4. **Check Logs**: Review logs to understand field mappings
5. **Error Messages**: Read validation errors for specific guidance

This intelligent mapping system makes the MCP server much more intuitive to use while maintaining the precision of GraphQL queries underneath.

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

## 🏗️ Architecture

### Modern Dynamic Query System
The server uses a **dynamic query registry** that supports natural language processing and advanced filtering:

```
queries/
├── base.py                    # Base query classes and schemas
├── devices/                   # Device queries
│   ├── dynamic_device.py      # Dynamic device query with field mapping
│   └── prompt_parser.py       # Natural language prompt parser
├── locations/                 # Location queries  
│   ├── dynamic_location.py    # Dynamic location query
│   └── prompt_parser.py       # Location prompt parser
├── ipam/                      # IP Address Management
│   ├── dynamic_ipam.py        # Dynamic IP address query
│   ├── filtered.py            # Legacy filtered query
│   └── prompt_parser.py       # IPAM prompt parser
├── prefixes/                  # Network prefixes
│   ├── dynamic_prefix.py      # Dynamic prefix query
│   └── prompt_parser.py       # Prefix prompt parser
├── device_types/              # Device types
│   ├── dynamic_device_type.py # Dynamic device type query
│   └── prompt_parser.py       # Device type prompt parser
├── statuses/                  # Status queries
├── roles/                     # Role queries
└── metadata/                  # System metadata
    ├── roles.py               # Device roles
    ├── tags.py                # Tags
    └── custom_fields.py       # Custom field definitions
```

### 🧩 Core Components

**1. Dynamic Query Classes**
- **Field Mapping**: Automatic translation of common aliases (`hostname` → `name`, `site` → `location`)
- **Validation**: Smart field validation with helpful suggestions
- **Custom Fields**: Proper handling of `cf_*` fields with String vs Array types
- **Lookup Expressions**: Support for advanced search operators

**2. Prompt Parsers**
- **Natural Language**: Convert English descriptions to structured queries
- **Pattern Recognition**: Regex-based parsing for various query patterns
- **Field Enablers**: Automatically enable relevant response fields based on context

**3. Query Registry**
- **Auto-Discovery**: Automatically registers all query classes
- **Type Safety**: Validates query schemas and parameters
- **Tool Generation**: Dynamically generates MCP tool definitions

### 🔧 Adding New Resource Types

1. **Create Directory Structure**:
```bash
mkdir queries/your_resource
touch queries/your_resource/__init__.py
```

2. **Create Dynamic Query**:
```python
# queries/your_resource/dynamic_your_resource.py
from ..base import BaseQuery, QueryType, MatchType, ToolSchema

class DynamicYourResourceQuery(BaseQuery):
    def __init__(self):
        self.field_mappings = {
            'alias1': 'real_field1',
            'alias2': 'real_field2'
        }
        self.valid_fields = {'field1', 'field2', 'field3'}
        self.base_query = """
        query YourResources($variable_value: [String]) {
            your_resources(enter_variable_name_here: $variable_value) {
                field1
                field2
            }
        }"""
        super().__init__()
```

3. **Create Prompt Parser**:
```python  
# queries/your_resource/prompt_parser.py
from typing import Dict, Any

def parse_your_resource_prompt(prompt: str) -> Dict[str, Any]:
    # Implement parsing logic
    return {"variable_name": "field1", "variable_value": ["value"]}
```

4. **Register in Main Registry**:
```python
# queries/__init__.py
from .your_resource import DynamicYourResourceQuery

# Add to query_classes list in _initialize_queries()
```

### 🧪 Development & Testing

```bash
# Test connection
python test_server.py connection

# Test all tools interactively
python test_server.py interactive

# Run server for testing
python mcp_server.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python mcp_server.py
```

### 📝 Advanced Features

**Field Mapping Examples**:
```python
'hostname' → 'name'                    # Simple alias
'site' → 'location'                    # Common terminology
'vendor' → 'device_type__manufacturer' # Nested field access
'ip' → 'primary_ip4'                   # Field relationship
```

**Lookup Expression Support**:
```python
'name__ic'    # Contains (case-insensitive)
'name__isw'   # Starts with (case-insensitive)  
'name__iew'   # Ends with (case-insensitive)
'name__re'    # Regular expression
'name__n'     # Not equal
'name__isnull' # Is null
```

**Custom Field Handling**:
```python
# Standard fields use [String] type
"$variable_value: [String]"

# Custom fields (cf_*) use String type  
"$variable_value: String"
```
