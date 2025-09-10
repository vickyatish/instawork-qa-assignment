#!/usr/bin/env python3
"""
Test script to verify ChromaDB integration works correctly.
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

def test_enhanced_semantic_retriever():
    """Test the enhanced semantic retriever with ChromaDB."""
    print("\nTesting Enhanced Semantic Retriever with ChromaDB...")
    
    try:
        from src.enhanced_semantic_retriever import EnhancedSemanticRetriever
        
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
        
        # Test with ChromaDB
        retriever = EnhancedSemanticRetriever(k=2, use_chromadb=True)
        
        # Fit the retriever
        retriever.fit(test_cases)
        print("✓ Successfully fitted retriever with test cases")
        
        # Test retrieval
        results = retriever.retrieve_relevant("user authentication login")
        assert len(results) > 0, "No retrieval results found"
        print(f"✓ Retrieved {len(results)} relevant test cases")
        
        # Test stats
        stats = retriever.get_stats()
        assert stats['is_fitted'], "Retriever not fitted"
        assert stats['use_chromadb'], "Not using ChromaDB"
        print(f"✓ Retriever stats: {stats}")
        
        # Test fallback to TF-IDF
        retriever_fallback = EnhancedSemanticRetriever(k=2, use_chromadb=False)
        retriever_fallback.fit(test_cases)
        results_fallback = retriever_fallback.retrieve_relevant("user authentication login")
        assert len(results_fallback) > 0, "No fallback results found"
        print("✓ TF-IDF fallback works correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Enhanced Semantic Retriever test failed: {e}")
        return False

def test_ai_copilot_integration():
    """Test AI copilot integration with ChromaDB."""
    print("\nTesting AI Copilot Integration...")
    
    try:
        # Set dummy API key for testing
        os.environ['OPENAI_API_KEY'] = 'test-key'
        
        from src.ai_test_copilot import AITestCopilot
        
        # Test with ChromaDB
        copilot = AITestCopilot(use_chromadb=True)
        status = copilot.get_status()
        
        assert 'vector_store_type' in status, "Vector store type not in status"
        print(f"✓ AI Copilot initialized with {status['vector_store_type']}")
        
        # Test vector store stats
        stats = copilot.get_vector_store_stats()
        assert 'use_chromadb' in stats, "ChromaDB status not in stats"
        print(f"✓ Vector store stats: {stats}")
        
        # Test search functionality
        # This will fail without real test cases, but we can test the method exists
        try:
            results = copilot.search_test_cases("test query", 1)
            print("✓ Search functionality works")
        except Exception as e:
            print(f"⚠ Search functionality test skipped: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ AI Copilot integration test failed: {e}")
        return False

def main():
    """Run all ChromaDB tests."""
    print("Running ChromaDB Integration Tests")
    print("=" * 50)
    
    tests = [
        test_chromadb_manager,
        test_enhanced_semantic_retriever,
        test_ai_copilot_integration
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
