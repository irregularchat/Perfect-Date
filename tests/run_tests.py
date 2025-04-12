import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == '__main__':
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir='tests', pattern='test_*.py')
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    results = test_runner.run(test_suite)
    
    # Exit with non-zero code if there are failures or errors
    if results.failures or results.errors:
        sys.exit(1)
    else:
        print("All tests passed!")
        sys.exit(0) 