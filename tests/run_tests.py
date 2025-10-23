import unittest
import os, sys

if __name__ == '__main__':
    
    # Get the directory of the run_tests.py file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root directory
    project_root = os.path.join(current_dir, '..')
    # Add the project root to the system path
    sys.path.insert(0, project_root)
    
    # 1. Create a TestLoader
    loader = unittest.TestLoader()
    
    # 2. Discover tests starting from the current directory ('.')
    #    This finds all files matching 'test_*.py'
    suite = loader.discover('.')
    
    # 3. Create a TestRunner
    runner = unittest.TextTestRunner(verbosity=2)
    
    # 4. Run the discovered suite
    runner.run(suite)