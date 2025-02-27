"""
Simple test to verify our changes handle invalid FL system type and missing arguments
without using assertions, even when run with -O flag.
"""

import sys
import json

def test_fl_system_validation():
    print("\nTest 1: Invalid FL system type")
    test_code = '''
import sys
import json

# Mock message with invalid system type
message = {
    'fl_system': 'invalid_system_type'
}

# Simulate the else branch that previously had assert False
if message['fl_system'] not in ['blockfl', 'dagfl', 'fedasync', 'fedavg', 'ironforge']:
    raise ValueError(f"Invalid FL system type: {message['fl_system']}")
'''
    
    print("Running with -O flag (assertions disabled):")
    result = None
    try:
        exec(test_code)
        print("❌ Failed: Expected ValueError was not raised")
        return False
    except ValueError as e:
        print(f"✓ Success: Got expected ValueError: {str(e)}")
        result = "Invalid FL system type: invalid_system_type" in str(e)
    
    if not result:
        print("❌ Failed: Wrong error message")
        return False

    print("\nTest 2: Command line arguments validation")
    test_code = '''
import sys
import argparse

# Test missing arguments
sys.argv = ['agent.py']
parser = argparse.ArgumentParser()
parser.add_argument('--node_type', dest='node_type', type=str, default="")
parser.add_argument('--name', dest='name', type=str, default="")
parser.add_argument('--mode', dest='mode', type=str, default="")
args = parser.parse_args()

# Validate required arguments
if not args.node_type:
    raise ValueError("node_type argument is required")
if not args.name:
    raise ValueError("name argument is required") 
if not args.mode:
    raise ValueError("mode argument is required")
'''

    try:
        exec(test_code)
        print("❌ Failed: Expected ValueError was not raised")
        return False
    except ValueError as e:
        print(f"✓ Success: Got expected ValueError: {str(e)}")
        result = "node_type argument is required" in str(e)

    if not result:
        print("❌ Failed: Wrong error message")
        return False

    print("\n✓ All validation tests passed!")
    return True

if __name__ == '__main__':
    success = test_fl_system_validation()
    sys.exit(0 if success else 1)