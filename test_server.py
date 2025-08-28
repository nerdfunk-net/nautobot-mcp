#!/usr/bin/env python3
"""
Testing utilities for the Nautobot MCP Server
"""
import json
import asyncio
import subprocess
import sys
from typing import Dict, Any, Optional

class MCPTester:
    """Test utility for MCP server interactions"""
    
    def __init__(self, server_script: str = "mcp_server.py"):
        self.server_script = server_script
    
    def create_jsonrpc_request(self, method: str, params: Optional[Dict[str, Any]] = None, request_id: int = 1) -> str:
        """Create a JSON-RPC 2.0 request"""
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }
        return json.dumps(request)
    
    def test_list_tools(self) -> bool:
        """Test the tools/list method"""
        print("Testing tools/list...")
        request = self.create_jsonrpc_request("tools/list")
        
        try:
            result = subprocess.run(
                [sys.executable, self.server_script],
                input=request,
                text=True,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout.strip())
                if "result" in response and "tools" in response["result"]:
                    tools = response["result"]["tools"]
                    print(f"✅ Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool['description']}")
                    return True
                else:
                    print(f"❌ Unexpected response format: {response}")
                    return False
            else:
                print(f"❌ Server error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            return False
    
    def test_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Test a specific tool call"""
        print(f"Testing tool call: {tool_name}")
        request = self.create_jsonrpc_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        try:
            result = subprocess.run(
                [sys.executable, self.server_script],
                input=request,
                text=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout.strip())
                if "result" in response:
                    print(f"✅ Tool call successful")
                    print(f"Response: {json.dumps(response['result'], indent=2)}")
                    return True
                else:
                    print(f"❌ Unexpected response: {response}")
                    return False
            else:
                print(f"❌ Tool call failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            return False
    
    def run_basic_tests(self) -> bool:
        """Run basic functionality tests"""
        print("🧪 Running Nautobot MCP Server Tests")
        print("=" * 50)
        
        all_passed = True
        
        # Test 1: List tools
        if not self.test_list_tools():
            all_passed = False
        
        print()
        
        # Test 2: Test device search by name (pattern matching)
        if not self.test_tool_call("devices_by_name", {
            "name_filter": ["switch"],
            "match_type": "pattern"
        }):
            all_passed = False
        
        print()
        
        # Test 3: Test device search by name (exact matching)
        if not self.test_tool_call("devices_by_name", {
            "name_filter": ["core-switch-01"],
            "match_type": "exact"
        }):
            all_passed = False
        
        print()
        
        # Test 4: Test get roles
        if not self.test_tool_call("get_roles", {}):
            all_passed = False
        
        print()
        
        # Test 5: Test get custom fields
        if not self.test_tool_call("get_custom_fields", {}):
            all_passed = False
        
        print("=" * 50)
        if all_passed:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
        
        return all_passed

def test_nautobot_connection():
    """Test direct connection to Nautobot"""
    print("Testing Nautobot connection...")
    try:
        from nautobot_client import NautobotClient
        client = NautobotClient()
        if client.test_connection():
            print("✅ Successfully connected to Nautobot")
            return True
        else:
            print("❌ Failed to connect to Nautobot")
            return False
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False

def interactive_test():
    """Interactive testing mode"""
    print("\n🔧 Interactive MCP Test Mode")
    print("Available tools:")
    tools = [
        "devices_by_name", "devices_by_location", "devices_by_role",
        "devices_by_tag", "devices_by_devicetype", "devices_by_manufacturer",
        "devices_by_platform", "get_roles", "get_tags", "get_custom_fields"
    ]
    
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool}")
    
    tester = MCPTester()
    
    while True:
        try:
            choice = input("\nEnter tool number (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                break
            
            tool_idx = int(choice) - 1
            if 0 <= tool_idx < len(tools):
                tool_name = tools[tool_idx]
                
                # Get arguments based on tool
                if tool_name in ["devices_by_name", "devices_by_location"]:
                    filter_values = input(f"Enter {tool_name.split('_by_')[1]} filter (comma-separated): ").split(',')
                    match_type = input("Match type (exact/pattern, default=pattern): ").strip() or "pattern"
                    args = {
                        f"{tool_name.split('_by_')[1]}_filter": [v.strip() for v in filter_values],
                        "match_type": match_type
                    }
                elif tool_name.startswith("devices_by_"):
                    filter_key = f"{tool_name.split('_by_')[1]}_filter"
                    filter_values = input(f"Enter {tool_name.split('_by_')[1]} filter (comma-separated): ").split(',')
                    args = {filter_key: [v.strip() for v in filter_values]}
                elif tool_name in ["get_roles", "get_tags"]:
                    filter_input = input("Enter content type filter (optional, comma-separated): ").strip()
                    if filter_input:
                        filter_key = "role_filter" if "role" in tool_name else "tags_filter"
                        args = {filter_key: [v.strip() for v in filter_input.split(',')]}
                    else:
                        args = {}
                else:
                    args = {}
                
                tester.test_tool_call(tool_name, args)
            else:
                print("Invalid choice")
                
        except (ValueError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "connection":
            test_nautobot_connection()
        elif sys.argv[1] == "interactive":
            interactive_test()
        elif sys.argv[1] == "all":
            test_nautobot_connection()
            print()
            MCPTester().run_basic_tests()
    else:
        print("Nautobot MCP Server Test Utility")
        print("Usage:")
        print("  python test_server.py connection    - Test Nautobot connection")
        print("  python test_server.py interactive   - Interactive tool testing")
        print("  python test_server.py all          - Run all tests")