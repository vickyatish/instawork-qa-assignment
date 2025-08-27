#!/usr/bin/env python3
"""
Test runner for the AI Test Case Copilot

This script runs the unit tests and provides a summary of results.
"""

import subprocess
import sys
import os

def run_tests():
    """Run the test suite and report results."""
    print("🧪 Running AI Test Case Copilot Test Suite")
    print("=" * 50)
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"], check=True)
        print("✅ pytest installed successfully!")
    
    # Run the tests
    print("\n🚀 Starting test execution...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Print test output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  Test warnings/errors:")
            print(result.stderr)
        
        # Report results
        if result.returncode == 0:
            print("\n✅ All tests passed successfully!")
            return True
        else:
            print(f"\n❌ Some tests failed (exit code: {result.returncode})")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running tests: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main entry point."""
    print("AI Test Case Copilot - Test Runner")
    print("=" * 40)
    
    success = run_tests()
    
    if success:
        print("\n🎉 Test suite completed successfully!")
        print("The AI Test Case Copilot is ready for use.")
    else:
        print("\n💥 Test suite failed!")
        print("Please check the errors above and fix any issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()
