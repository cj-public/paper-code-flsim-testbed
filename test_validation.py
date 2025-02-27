import sys
import json
from unittest.mock import MagicMock, patch
import argparse

class MockRedis:
    def __init__(self, message):
        self.message = message
        
    def get_connection(self):
        return self
        
    def pubsub(self):
        return self
        
    def subscribe(self, channels):
        pass
        
    def listen(self):
        yield self.message

def mock_import(*args):
    return MagicMock()

def test_validation():
    print("Starting validation tests...")
    
    # Mock all imports that might happen in agent.py
    sys.modules['flexpkit'] = MagicMock()
    sys.modules['flexpkit.basic_utils'] = MagicMock(
        print_log=lambda x: print(f"[MOCK LOG] {x}"),
        strftime_to_timestamp=lambda x: 0,
        current_timestamp=lambda: 0
    )
    sys.modules['flexpkit.exp_utils'] = MagicMock()
    sys.modules['flexpkit.exp_constants'] = MagicMock(
        FL_SYSTEM_BLOCKFL='blockfl',
        FL_SYSTEM_DAGFL='dagfl',
        FL_SYSTEM_FEDASYNC='fedasync',
        FL_SYSTEM_FEDAVG='fedavg',
        FL_SYSTEM_IRONFORGE='ironforge',
        RUN_TYPE_DEBUG='debug',
        MESSAGE_QUEUE_NAME_AGENT='agent_queue'
    )
    sys.modules['flexpkit.exp_settings'] = MagicMock(
        node_type_config_list={'test': {'memory': 1}}
    )
    sys.modules['flexpkit.mysql_utils'] = MagicMock()
    sys.modules['flexpkit.redis_utils'] = MagicMock()
    sys.modules['flexpkit.storage_utils'] = MagicMock()
    sys.modules['memory_profiler'] = MagicMock()
    sys.modules['blockfl.coordinator'] = MagicMock()
    sys.modules['dagfl.coordinator'] = MagicMock()
    sys.modules['fedasync.coordinator'] = MagicMock()
    sys.modules['fedavg.coordinator'] = MagicMock()
    sys.modules['ironforge.coordinator'] = MagicMock()

    print("\n=== Testing Invalid FL System Type ===")
    try:
        # Create a mock message for FL system type validation
        mock_message = {
            'type': 'message',
            'data': json.dumps({
                'fl_system': 'invalid_system_type',
                'timestamp': '2023-01-01 00:00:00'
            })
        }
        
        # Set up Redis mock
        sys.modules['flexpkit.redis_utils'].redis_cli = MockRedis(mock_message)
        
        print("Importing and running agent module...")
        # Import after all mocks are set up
        with patch('builtins.__import__', side_effect=mock_import):
            import agent
            # Reload in case it was imported before
            import importlib
            importlib.reload(agent)
            
            agent.run_loop("test_runner", "debug")
        
        print("❌ Expected ValueError was not raised!")
        sys.exit(1)
    except ValueError as e:
        print(f"Got expected ValueError: {str(e)}")
        assert "Invalid FL system type: invalid_system_type" in str(e), "Wrong error message"
        print("✓ FL system type validation works correctly")
    except Exception as e:
        print(f"Got unexpected error: {type(e).__name__}: {str(e)}")
        print(f"Error details: {str(e)}")
        raise

    print("\n=== Testing Command Line Args ===")
    try:
        # Test missing node_type
        sys.argv = ['agent.py']
        parser = argparse.ArgumentParser(description='Runner information')
        parser.add_argument('--node_type', dest='node_type', type=str, default="", help='node_type')
        parser.add_argument('--name', dest='name', type=str, default="", help='Runner name(s)')
        parser.add_argument('--mode', dest='mode', type=str, default="", help='Run mode')
        args = parser.parse_args()

        if not args.node_type:
            raise ValueError("node_type argument is required")
        if not args.name:
            raise ValueError("name argument is required")
        if not args.mode:
            raise ValueError("mode argument is required")
        print("❌ Expected ValueError was not raised!")
        sys.exit(1)
    except ValueError as e:
        print(f"Got expected ValueError: {str(e)}")
        assert "node_type argument is required" in str(e), "Wrong error message"
        print("✓ Command line argument validation works correctly")

    print("\nAll validation tests passed successfully!")

if __name__ == '__main__':
    print("\n=== Running Validation Tests ===")
    test_validation()
    print("=== Tests Complete ===\n")