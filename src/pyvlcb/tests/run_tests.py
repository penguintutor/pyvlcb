#!/usr/bin/env python3


import unittest
import os, sys

if __name__ == '__main__':

    os.environ["QT_LOGGING_RULES"] = "*.debug=false"
    
    # Get the directory of the run_tests.py file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root directory
    project_root = os.path.join(current_dir, '../..')
    # Add the project root to the system path
    sys.path.insert(0, project_root)
    
    # Create a TestLoader
    loader = unittest.TestLoader()
    # Discover tests starting from the current directory ('.')
    # This finds all files matching 'test_*.py'
    suite = loader.discover('.')    
    # Create a TestRunner
    runner = unittest.TextTestRunner(verbosity=2)
    # Run the discovered suite
    runner.run(suite)
