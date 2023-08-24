import argparse
import json
import gc
import random
import time
import traceback
from flexpkit.basic_utils import print_log, strftime_to_timestamp
from flexpkit.exp_utils import *
from flexpkit.exp_constants import *
from flexpkit.exp_settings import *
from flexpkit.mysql_utils import *
from flexpkit.redis_utils import *
from flexpkit.storage_utils import *

from threading import Thread, Event
from memory_profiler import profile


def run_loop(runner_names, run_type):
    print('{} is booting'.format(runner_names))

    ps = redis_cli.get_connection().pubsub()
    ps.subscribe([MESSAGE_QUEUE_NAME_AGENT, ])

    for message in ps.listen():

        print_log('AGENT: {}'.format(message))

        if message['type'] != 'message':
            continue

        message = json.loads(message['data'])

        # 设置消息的超时机制
        if 'timestamp' in message and current_timestamp() - strftime_to_timestamp(message['timestamp']) > 10:
            print_log('AGENT: message timeout, stop processing')
            return

        if message['fl_system'] == FL_SYSTEM_BLOCKFL:
            from blockfl.coordinator import coordinate
        elif message['fl_system'] == FL_SYSTEM_DAGFL:
            from dagfl.coordinator import coordinate
        elif message['fl_system'] == FL_SYSTEM_FEDASYNC:
            from fedasync.coordinator import coordinate
        elif message['fl_system'] == FL_SYSTEM_FEDAVG:
            from fedavg.coordinator import coordinate
        elif message['fl_system'] == FL_SYSTEM_IRONFORGE:
            from ironforge.coordinator import coordinate
        else:
            assert False

        # 再加个exception处理
        try:
            coordinate(runner_names, message, run_type)

        except Exception as e:
            err_msg = traceback.format_exc()
            print(err_msg)

            upload_runtime_errors(runner_names, message['fl_system'], message, str(err_msg))

            raise Exception('error handled')

        finally:
            gc.collect()


# @profile
def wait_for_tasks(node_type, runner_names, run_type=RUN_TYPE_DEBUG):

    clean_storage_cache(True, True)

    node_settings = node_type_config_list[node_type]
    memG = node_settings['memory']
    # resource.setrlimit(resource.RLIMIT_AS, (memG * 1e9, memG * 1e9))

    while True:
        try:
            run_loop(runner_names, run_type)

        except Exception as e:
            if 'error handled' not in str(e):
                err_msg = traceback.format_exc()
                print(err_msg)

                upload_runtime_errors(runner_names, 'anywhere', 'outer loop', str(err_msg))

            time.sleep(10)

        finally:
            gc.collect()


if __name__ == '__main__':
    """
    PYTHONPATH='./src' python agent.py --node_type node-type-000 --name flsim-worker-00028_flsim-worker-00011_flsim-worker-00026 --mode debug
    """
    parser = argparse.ArgumentParser(description='Runner information')
    parser.add_argument('--node_type', dest='node_type', type=str,
                        default="", help='node_type')
    parser.add_argument('--name', dest='name', type=str,
                        default="", help='Runner name(s)')
    parser.add_argument('--mode', dest='mode', type=str,
                        default="", help='Run mode(debug or production)')

    args = parser.parse_args()

    assert args.node_type
    assert args.name
    assert args.mode

    wait_for_tasks(args.node_type, args.name, args.mode)
