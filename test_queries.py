#!/usr/bin/env python3
"""
Query Testing Framework for Nautobot MCP Server

This framework provides comprehensive testing for individual queries and the overall system.
"""

import json
import sys
import traceback
from typing import Dict, Any, List, Optional

from nautobot_client import NautobotClient
from queries import get_all_queries, get_query, query_registry

class QueryTester:
    """Test framework for individual queries and the query system"""
    
    def __init__(self):
        try:
            self.client = NautobotClient()
            self.connection_ok = self.client.test_connection()
        except Exception as e:
            print(f"⚠️  Failed to initialize client: {str(e)}")
            self.client = None
            self.connection_ok = False
    
    def test_query_registration(self) -> bool:
        """Test that all queries are properly registered"""
        print("🔍 Testing query registration...")
        
        try:
            queries = get_all_queries()
            print(f"✅ Found {len(queries)} registered queries")
            
            # Test each query is properly initialized
            failed_queries = []
            for tool_name, query in queries.items():
                try:
                    # Test basic properties
                    assert query.tool_name == tool_name
                    assert query.description
                    assert query.query_type
                    assert query.schema
                    
                    # Test schema structure
                    assert query.schema.type == "object"
                    assert isinstance(query.schema.properties, dict)
                    assert isinstance(query.schema.required, list)
                    
                    print(f"  ✅ {tool_name}: OK")
                    
                except Exception as e:
                    print(f"  ❌ {tool_name}: {str(e)}")
                    failed_queries.append(tool_name)
            
            if failed_queries:
                print(f"❌ {len(failed_queries)} queries failed registration test")
                return False
            else:
                print("✅ All queries passed registration test")
                return True
                
        except Exception as e:
            print(f"❌ Query registration test failed: {str(e)}")
            return False
    
    def test_query_schemas(self) -> bool:
        """Test query schema validation"""
        print("\n🔍 Testing query schemas...")
        
        if not self.client:
            print("⚠️  Skipping schema tests - no client available")
            return True
        
        queries = get_all_queries()
        failed_schemas = []
        
        for tool_name, query in queries.items():
            try:
                # Test with empty arguments (should fail for required fields)
                if query.schema.required:
                    try:
                        query.validate_arguments({})
                        print(f"  ❌ {tool_name}: Should fail with empty args but didn't")
                        failed_schemas.append(tool_name)
                        continue
                    except ValueError:
                        pass  # Expected
                
                # Test with valid arguments
                test_args = {}
                for req_field in query.schema.required:
                    if req_field.endswith("_filter"):
                        test_args[req_field] = ["test"]
                    elif req_field == "fields" and tool_name == "get_device_details":
                        test_args[req_field] = "status,role"  # Valid device fields
                    elif req_field == "fields" and tool_name == "get_ip_addresses":
                        test_args[req_field] = "status,dns_name"  # Valid IP address fields
                    else:
                        test_args[req_field] = "test"
                
                # Add optional match_type if present
                if "match_type" in query.schema.properties:
                    test_args["match_type"] = "pattern"
                
                query.validate_arguments(test_args)
                print(f"  ✅ {tool_name}: Schema validation OK")
                
            except Exception as e:
                print(f"  ❌ {tool_name}: Schema error - {str(e)}")
                failed_schemas.append(tool_name)
        
        if failed_schemas:
            print(f"❌ {len(failed_schemas)} queries failed schema test")
            return False
        else:
            print("✅ All query schemas are valid")
            return True
    
    def test_live_queries(self, sample_only: bool = True) -> bool:
        """Test queries against live Nautobot instance"""
        print("\n🔍 Testing live query execution...")
        
        if not self.connection_ok:
            print("⚠️  Skipping live tests - no Nautobot connection")
            return True
        
        queries = get_all_queries()
        
        # Test a sample of queries to avoid overwhelming the server
        if sample_only:
            test_queries = {
                "get_roles": {},
                "get_tags": {},
                "devices_by_name": {"name_filter": ["nonexistent"], "match_type": "pattern"}
            }
        else:
            # Test all queries with safe parameters
            test_queries = {}
            for tool_name, query in queries.items():
                args = {}
                for req_field in query.schema.required:
                    if req_field.endswith("_filter"):
                        args[req_field] = ["test"]
                    else:
                        args[req_field] = "test"
                
                if "match_type" in query.schema.properties:
                    args["match_type"] = "pattern"
                
                test_queries[tool_name] = args
        
        failed_queries = []
        
        for tool_name, test_args in test_queries.items():
            try:
                query = get_query(tool_name)
                result = query.execute(self.client, test_args)
                
                # Check result structure
                if query.query_type.value == "graphql":
                    if "errors" in result:
                        print(f"  ⚠️  {tool_name}: GraphQL errors - {result['errors']}")
                    elif "data" in result:
                        print(f"  ✅ {tool_name}: Executed successfully")
                    else:
                        print(f"  ❌ {tool_name}: Unexpected GraphQL response format")
                        failed_queries.append(tool_name)
                else:
                    # REST query
                    if isinstance(result, dict) or isinstance(result, list):
                        print(f"  ✅ {tool_name}: Executed successfully") 
                    else:
                        print(f"  ❌ {tool_name}: Unexpected REST response format")
                        failed_queries.append(tool_name)
                
            except Exception as e:
                print(f"  ❌ {tool_name}: Execution failed - {str(e)}")
                failed_queries.append(tool_name)
        
        if failed_queries:
            print(f"❌ {len(failed_queries)} queries failed live execution test")
            return False
        else:
            print("✅ All tested queries executed successfully")
            return True
    
    def test_query_categories(self) -> bool:
        """Test query categorization system"""
        print("\n🔍 Testing query categorization...")
        
        try:
            categories = query_registry.list_queries_by_category()
            
            print(f"Found categories: {list(categories.keys())}")
            for category, tools in categories.items():
                print(f"  {category}: {len(tools)} tools")
                for tool in tools[:3]:  # Show first 3
                    print(f"    - {tool}")
                if len(tools) > 3:
                    print(f"    ... and {len(tools) - 3} more")
            
            print("✅ Query categorization working")
            return True
            
        except Exception as e:
            print(f"❌ Categorization test failed: {str(e)}")
            return False
    
    def interactive_query_test(self):
        """Interactive testing mode for individual queries"""
        print("\n🔧 Interactive Query Testing")
        
        if not self.connection_ok:
            print("⚠️  No Nautobot connection - testing will be limited")
        
        queries = get_all_queries()
        tool_names = list(queries.keys())
        
        print("\nAvailable queries:")
        for i, tool_name in enumerate(tool_names, 1):
            query = queries[tool_name]
            print(f"{i:2d}. {tool_name} - {query.description}")
        
        while True:
            try:
                choice = input(f"\nSelect query (1-{len(tool_names)}, or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    break
                
                idx = int(choice) - 1
                if 0 <= idx < len(tool_names):
                    tool_name = tool_names[idx]
                    query = queries[tool_name]
                    
                    print(f"\n📋 Testing: {tool_name}")
                    print(f"Description: {query.description}")
                    print(f"Required params: {query.schema.required}")
                    
                    # Build arguments
                    args = {}
                    for param in query.schema.required:
                        value = input(f"Enter {param}: ").strip()
                        if param.endswith("_filter"):
                            args[param] = [v.strip() for v in value.split(',')]
                        else:
                            args[param] = value
                    
                    # Optional parameters
                    if "match_type" in query.schema.properties:
                        match_type = input("Match type (exact/pattern, default=pattern): ").strip() or "pattern"
                        args["match_type"] = match_type
                    
                    # Execute query
                    if self.connection_ok:
                        try:
                            result = query.execute(self.client, args)
                            print(f"\n✅ Result:\n{json.dumps(result, indent=2)}")
                        except Exception as e:
                            print(f"\n❌ Execution failed: {str(e)}")
                    else:
                        print("\n⚠️  Cannot execute - no Nautobot connection")
                        try:
                            query.validate_arguments(args)
                            print("✅ Arguments are valid")
                        except Exception as e:
                            print(f"❌ Argument validation failed: {str(e)}")
                
                else:
                    print("Invalid choice")
                    
            except (ValueError, KeyboardInterrupt):
                break
    
    def run_all_tests(self) -> bool:
        """Run all test suites"""
        print("🧪 Nautobot MCP Query Test Suite")
        print("=" * 60)
        
        tests = [
            ("Query Registration", self.test_query_registration),
            ("Schema Validation", self.test_query_schemas),
            ("Live Query Execution", lambda: self.test_live_queries(sample_only=True)),
            ("Query Categorization", self.test_query_categories)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} crashed: {str(e)}")
                traceback.print_exc()
                results.append((test_name, False))
        
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        
        all_passed = True
        for test_name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name}: {status}")
            if not passed:
                all_passed = False
        
        print("=" * 60)
        if all_passed:
            print("🎉 All tests passed!")
        else:
            print("❌ Some tests failed.")
        
        return all_passed

def main():
    """Main entry point"""
    tester = QueryTester()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "all":
            tester.run_all_tests()
        elif command == "interactive":
            tester.interactive_query_test()
        elif command == "registration":
            tester.test_query_registration()
        elif command == "schemas":
            tester.test_query_schemas()
        elif command == "live":
            tester.test_live_queries(sample_only=False)
        elif command == "categories":
            tester.test_query_categories()
        else:
            print(f"Unknown command: {command}")
    else:
        print("Query Testing Framework")
        print("Commands:")
        print("  all           - Run all tests")
        print("  interactive   - Interactive query testing")
        print("  registration  - Test query registration")
        print("  schemas       - Test schema validation")
        print("  live          - Test live query execution")
        print("  categories    - Test query categorization")

if __name__ == "__main__":
    main()