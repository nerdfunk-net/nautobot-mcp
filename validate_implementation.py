#!/usr/bin/env python3
"""
Validate the MCP server implementation without requiring a live Nautobot instance
"""
import json
import sys
from nautobot_client import NautobotClient
from mcp_server import QUERIES, list_tools

def validate_client_structure():
    """Validate the NautobotClient structure"""
    print("🔍 Validating NautobotClient structure...")
    
    try:
        # Test client initialization (will fail connection but structure is valid)
        client = NautobotClient()
        print(f"✅ Client initialized with URL: {client.base_url}")
        print(f"✅ Token configured: {'Yes' if client.token else 'No'}")
        print(f"✅ Headers configured: {len(client.headers)} headers")
        
        # Test methods exist
        methods = ['graphql_query', 'rest_get', 'test_connection']
        for method in methods:
            if hasattr(client, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Client validation failed: {str(e)}")
        return False

def validate_queries():
    """Validate all GraphQL queries are properly structured"""
    print("\n🔍 Validating GraphQL queries...")
    
    expected_tools = [
        "devices_by_name", "devices_by_location", "devices_by_role",
        "devices_by_tag", "devices_by_devicetype", "devices_by_manufacturer", 
        "devices_by_platform", "get_roles", "get_tags"
    ]
    
    all_valid = True
    
    for tool in expected_tools:
        if tool in QUERIES:
            query_data = QUERIES[tool]
            
            # Handle combined queries (name/location)
            if isinstance(query_data, dict):
                if "exact" in query_data and "pattern" in query_data:
                    print(f"✅ {tool}: Combined exact/pattern queries found")
                    # Validate both queries contain GraphQL syntax
                    for variant in ["exact", "pattern"]:
                        if "query " in query_data[variant] and "{" in query_data[variant]:
                            print(f"  ✅ {variant} variant valid")
                        else:
                            print(f"  ❌ {variant} variant invalid")
                            all_valid = False
                else:
                    print(f"❌ {tool}: Invalid combined query structure")
                    all_valid = False
            else:
                # Single query validation
                if "query " in query_data and "{" in query_data:
                    print(f"✅ {tool}: Query structure valid")
                else:
                    print(f"❌ {tool}: Invalid query structure")
                    all_valid = False
        else:
            print(f"❌ {tool}: Query missing from QUERIES dict")
            all_valid = False
    
    return all_valid

async def validate_mcp_tools():
    """Validate MCP tool definitions"""
    print("\n🔍 Validating MCP tool definitions...")
    
    try:
        tools = await list_tools()
        print(f"✅ Found {len(tools)} MCP tools")
        
        expected_tools = [
            "devices_by_name", "devices_by_location", "devices_by_role",
            "devices_by_tag", "devices_by_devicetype", "devices_by_manufacturer",
            "devices_by_platform", "get_roles", "get_tags", "get_custom_fields"
        ]
        
        tool_names = [tool.name for tool in tools]
        
        all_valid = True
        for expected in expected_tools:
            if expected in tool_names:
                print(f"✅ Tool {expected} defined")
            else:
                print(f"❌ Tool {expected} missing")
                all_valid = False
        
        # Validate tool schemas
        for tool in tools:
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                print(f"✅ {tool.name}: Input schema defined")
            else:
                print(f"⚠️  {tool.name}: No input schema (might be optional)")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ MCP tool validation failed: {str(e)}")
        return False

def validate_project_structure():
    """Validate project file structure"""
    print("\n🔍 Validating project structure...")
    
    import os
    required_files = [
        "nautobot_client.py",
        "mcp_server.py", 
        "test_server.py",
        "requirements.txt",
        ".env.example",
        "README.md"
    ]
    
    all_valid = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_valid = False
    
    return all_valid

def main():
    """Run all validations"""
    print("🧪 Nautobot MCP Server Implementation Validation")
    print("=" * 60)
    
    validations = [
        ("Project Structure", validate_project_structure()),
        ("Client Structure", validate_client_structure()),
        ("GraphQL Queries", validate_queries()),
    ]
    
    # Run async validation
    import asyncio
    mcp_valid = asyncio.run(validate_mcp_tools())
    validations.append(("MCP Tools", mcp_valid))
    
    print("\n" + "=" * 60)
    print("📋 Validation Summary:")
    
    all_passed = True
    for name, result in validations:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 All validations passed! Implementation is ready.")
        print("\n📝 Next steps:")
        print("1. Set up .env file with real Nautobot credentials")
        print("2. Test with: python test_server.py connection")
        print("3. Run server with: python mcp_server.py")
    else:
        print("❌ Some validations failed. Please review the errors above.")
        
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())