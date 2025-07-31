#!/usr/bin/env python3
"""
Test runner for FinBot project.
Run this script to execute all tests.
"""

import unittest
import sys
import os

def setup_python_path():
    """Set up Python path to find the app modules."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(project_root, 'app')
    
    # Add app directory to Python path
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    
    # Also add project root for any other imports
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

def run_tests():
    """Run all tests in the project."""
    # Set up Python path
    setup_python_path()
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    # Check if tests directory exists
    if not os.path.exists(start_dir):
        print("❌ Tests directory not found!")
        return 1
    
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Check if any tests were found
    if not suite.countTestCases():
        print("❌ No tests found!")
        return 1
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    print("🧪 Running FinBot Tests...")
    print("=" * 50)
    
    exit_code = run_tests()
    
    print("=" * 50)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    sys.exit(exit_code) 