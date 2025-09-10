#!/usr/bin/env python3
"""
Simple test script to verify ChromaDB integration works correctly.
"""

import os
import sys
import json

def test_chromadb_manager():
    """Test the ChromaDB manager functionality."""
    print("Testing ChromaDB Manager...")
    
    try:
        from src.chromadb_manager import ChromaDBManager
        
        # Create manager
        manager = ChromaDBManager("test_collection")
        
        # Test data
        test_cases = [
            {
                "title": "User Login Test",
                "type": "functional",
                "priority": "P1 - Critical",
                "steps": [
                    {"step_text": "Navigate to login page", "step_expected": "Login page loads"},
                    {"step_text": "Enter valid credentials", "step_expected": "User is logged in"}
                ],
                "_file_name": "tc_001.json"
            },
            {
                "title": "API Authentication Test",
                "type": "api",
                "priority": "P2 - High",
                "steps": [
                    {"step_text": "Send request without token", "step_expected": "401 Unauthorized"},
                    {"step_text": "Send request with valid token", "step_expected": "200 OK"}
                ],
                "_file_name": "tc_002.json"
            }
        ]
        
        # Test adding test cases
        success = manager.add_test_cases(test_cases)
        assert success, "Failed to add test cases"
        print("✓ Successfully added test cases to ChromaDB")
        
        # Test searching
        results = manager.search_similar("user authentication login", 2)
        assert len(results) > 0, "No search results found"
        print(f"✓ Found {len(results)} similar test cases")
        
        # Test collection stats
        stats = manager.get_collection_stats()
        assert stats['total_test_cases'] > 0, "No test cases in collection"
        print(f"✓ Collection has {stats['total_test_cases']} test cases")
        
        # Test updating a test case
        updated_case = test_cases[0].copy()
        updated_case["title"] = "Updated User Login Test"
        success = manager.update_test_case("tc_001.json", updated_case)
        assert success, "Failed to update test case"
        print("✓ Successfully updated test case")
        
        # Test deleting a test case
        success = manager.delete_test_case("tc_002.json")
        assert success, "Failed to delete test case"
        print("✓ Successfully deleted test case")
        
        # Clean up
        manager.reset_collection()
        print("✓ Successfully reset collection")
        
        return True
        
    except Exception as e:
        print(f"✗ ChromaDB Manager test failed: {e}")
        return False

def test_ai_copilot_chromadb():
    """Test AI copilot with ChromaDB (without scikit-learn)."""
    print("\nTesting AI Copilot with ChromaDB...")
    
    try:
        # Set dummy API key for testing
        os.environ['OPENAI_API_KEY'] = 'test-key'
        
        # Import without scikit-learn dependencies
        from src.chromadb_manager import ChromaDBManager
        
        # Test ChromaDB manager directly
        manager = ChromaDBManager("test_copilot_collection")
        
        # Test data
        test_cases = [
            {
                "title": "User Login Test",
                "type": "functional",
                "priority": "P1 - Critical",
                "steps": [
                    {"step_text": "Navigate to login page", "step_expected": "Login page loads"},
                    {"step_text": "Enter valid credentials", "step_expected": "User is logged in"}
                ],
                "_file_name": "tc_001.json"
            }
        ]
        
        # Test adding test cases
        success = manager.add_test_cases(test_cases)
        assert success, "Failed to add test cases"
        print("✓ Successfully added test cases to ChromaDB")
        
        # Test searching
        results = manager.search_similar("user login authentication", 1)
        assert len(results) > 0, "No search results found"
        print(f"✓ Found {len(results)} similar test cases")
        
        # Test stats
        stats = manager.get_collection_stats()
        assert stats['total_test_cases'] > 0, "No test cases in collection"
        print(f"✓ Collection stats: {stats}")
        
        # Clean up
        manager.reset_collection()
        print("✓ Successfully reset collection")
        
        return True
        
    except Exception as e:
        print(f"✗ AI Copilot ChromaDB test failed: {e}")
        return False

def main():
    """Run ChromaDB tests."""
    print("Running ChromaDB Integration Tests")
    print("=" * 50)
    
    tests = [
        test_chromadb_manager,
        test_ai_copilot_chromadb
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"✗ {test.__name__} failed with error: {e}")
            print()
    
    print("=" * 50)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All ChromaDB tests passed! The integration is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
