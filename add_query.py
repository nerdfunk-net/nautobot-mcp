#!/usr/bin/env python3
"""
Query Generator Utility

This utility helps you quickly add new queries to the Nautobot MCP Server.
Run this script to interactively create new query modules.
"""

import os
import sys
from typing import List

def create_simple_query(tool_name: str, description: str, query: str, 
                       required_params: List[str], category: str = "devices"):
    """Create a simple GraphQL query module"""
    
    # Determine file path
    if category == "metadata":
        file_path = f"queries/metadata/{tool_name.replace('get_', '')}.py"
        class_name = f"{tool_name.replace('_', ' ').title().replace(' ', '')}Query"
    else:
        file_path = f"queries/devices/{tool_name.replace('devices_by_', 'by_')}.py"  
        class_name = f"{tool_name.replace('_', ' ').title().replace(' ', '')}Query"
    
    # Generate module content
    content = f'''"""
{description} query module
"""

from ..base import SimpleGraphQLQuery

class {class_name}(SimpleGraphQLQuery):
    def __init__(self):
        query = """{query}"""
        
        super().__init__(
            tool_name="{tool_name}",
            description="{description}",
            query=query,
            required_params={required_params}
        )
'''
    
    # Write file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Created {file_path}")
    print(f"📝 Class name: {class_name}")
    
    # Update __init__.py
    update_init_file(category, class_name, tool_name)

def create_combined_query(tool_name: str, description: str, 
                         exact_query: str, pattern_query: str, 
                         filter_param: str, category: str = "devices"):
    """Create a combined exact/pattern query module"""
    
    file_path = f"queries/devices/{tool_name.replace('devices_by_', 'by_')}.py"
    class_name = f"{tool_name.replace('_', ' ').title().replace(' ', '')}Query"
    
    content = f'''"""
{description} query module
"""

from ..base import CombinedMatchQuery

class {class_name}(CombinedMatchQuery):
    def __init__(self):
        exact_query = """{exact_query}"""
        
        pattern_query = """{pattern_query}"""
        
        super().__init__(
            tool_name="{tool_name}",
            description="{description}",
            exact_query=exact_query,
            pattern_query=pattern_query,
            filter_param="{filter_param}"
        )
'''
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Created {file_path}")
    update_init_file(category, class_name, tool_name)

def update_init_file(category: str, class_name: str, tool_name: str):
    """Update the __init__.py file to include the new query"""
    init_path = f"queries/{category}/__init__.py"
    
    if not os.path.exists(init_path):
        print(f"⚠️  {init_path} not found, skipping __init__.py update")
        return
    
    # Read current content
    with open(init_path, 'r') as f:
        content = f.read()
    
    # Add import
    import_line = f"from .{tool_name.replace('devices_by_', '').replace('get_', '')} import {class_name}"
    if import_line not in content:
        # Find the import section and add new import
        lines = content.split('\n')
        import_section_end = -1
        for i, line in enumerate(lines):
            if line.startswith('from .') and ' import ' in line:
                import_section_end = i
        
        if import_section_end >= 0:
            lines.insert(import_section_end + 1, import_line)
        else:
            lines.insert(-1, import_line)
        
        # Add to __all__
        if "__all__" in content:
            all_section = None
            for i, line in enumerate(lines):
                if "__all__" in line:
                    all_section = i
                    break
            
            if all_section:
                # Find the end of __all__
                for i in range(all_section, len(lines)):
                    if ']' in lines[i]:
                        lines[i] = lines[i].replace(']', f",\n    '{class_name}'\n]")
                        break
        
        # Write back
        with open(init_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Updated {init_path}")

def interactive_query_creator():
    """Interactive query creation wizard"""
    print("🚀 Nautobot MCP Query Generator")
    print("=" * 50)
    
    # Get basic info
    tool_name = input("Tool name (e.g., 'devices_by_status'): ").strip()
    if not tool_name:
        print("❌ Tool name is required")
        return
    
    description = input("Description: ").strip()
    if not description:
        description = f"Find items by {tool_name.split('_by_')[-1] if '_by_' in tool_name else 'criteria'}"
    
    # Choose query type
    print("\nQuery type:")
    print("1. Simple GraphQL query")
    print("2. Combined exact/pattern matching query") 
    print("3. REST API query")
    
    query_type = input("Choose (1-3): ").strip()
    
    if query_type == "1":
        create_simple_interactive()
    elif query_type == "2":
        create_combined_interactive()
    elif query_type == "3":
        create_rest_interactive()
    else:
        print("❌ Invalid choice")

def create_simple_interactive():
    """Create simple query interactively"""
    print("\n📝 Simple GraphQL Query")
    
    tool_name = input("Tool name: ").strip()
    description = input("Description: ").strip()
    
    print("\nEnter GraphQL query (end with empty line):")
    query_lines = []
    while True:
        line = input()
        if not line:
            break
        query_lines.append(line)
    
    query = '\n'.join(query_lines)
    
    required_params = input("Required parameters (comma-separated): ").strip().split(',')
    required_params = [p.strip() for p in required_params if p.strip()]
    
    create_simple_query(tool_name, description, query, required_params)
    print("\n🎉 Query created successfully!")
    print(f"Next steps:")
    print(f"1. Update queries/__init__.py to register {tool_name}")
    print(f"2. Test with: python -c \"from queries import get_query; print(get_query('{tool_name}'))\"")

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_query_creator()
    else:
        print("Usage:")
        print("  python add_query.py interactive  - Interactive query creation")
        print()
        print("Example of adding a query programmatically:")
        print("  create_simple_query(")
        print("      tool_name='devices_by_status',")
        print("      description='Find devices by status',") 
        print("      query='query {...}',")
        print("      required_params=['status_filter']")
        print("  )")

if __name__ == "__main__":
    main()