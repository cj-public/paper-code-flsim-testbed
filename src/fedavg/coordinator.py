from flexpkit.exp_constants import *


def coordinate(runner_names, message, run_type):
    if message['event'] == EVENT_LOCAL_WEIGHTS_UPLOADED:
        from fedavg.master import process_message
    elif message['event'] == EVENT_TASK_PUBLISHED or message['event'] == EVENT_GLOBAL_WEIGHTS_UPLOADED:
        from fedavg.worker import process_message
    else:
        # discard other events
        return

    process_message(runner_names, message, run_type)