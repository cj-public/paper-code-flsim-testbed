import argparse

from flexpkit.exp_constants import *
from flexpkit.exp_settings import *


def coordinate(runner_names, message, run_type):
    # global weights uploaded也要处理，因为fedasync的机制比较特殊，不能简单的使用local weights upload event来驱动
    if message['event'] == EVENT_LOCAL_WEIGHTS_UPLOADED or message['event'] == EVENT_GLOBAL_WEIGHTS_UPLOADED:
        from fedasync.master import process_message

        # 每次只处理一个效率太低，且容易陷入死锁，即所有的weights都没有aggregate，即使task publish event能驱动某一个worker工作，但考虑只有一定概率会进行训练，导致整个训练过程停滞。
        for i in range(10):
            process_message(runner_names, message, run_type)

    # 如果不是task初始时的task publish event，说明是rescheduled的task，此时阻塞已经非常严重，需要及时清理
    if message['event'] == EVENT_TASK_PUBLISHED:
        from fedasync.master import process_message

        for i in range(VIRTUAL_NODE_NUM_EACH_TASK):
            process_message(runner_names, message, run_type)

    if message['event'] == EVENT_TASK_PUBLISHED or message['event'] == EVENT_GLOBAL_WEIGHTS_UPLOADED:
        from fedasync.worker import process_message
        process_message(runner_names, message, run_type)

