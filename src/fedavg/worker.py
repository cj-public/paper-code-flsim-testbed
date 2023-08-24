import json
import random

from flexpkit.dataset_utils import *
from flexpkit.exp_constants import *
from flexpkit.exp_settings import *
from flexpkit.exp_utils import *
from flexpkit.fastdfs_utils import *
from flexpkit.model_utils import *
from flexpkit.mysql_utils import *
from flexpkit.weights_utils import *


class Worker:
    name = None
    status = RUNNER_STATUS_SLEEP

    global_weights_id = None

    mode = RUNNER_MODE_NORMAL
    dataset_shard_id = None

    task_id = None
    task_status = TASK_STATUS_RUNNING

    model_name = None
    model_params = None
    model_obj = None

    dataset_id = None
    dataset_obj = None

    def __init__(self, worker_name, message, run_type, sibling_worker_num):
        if 'worker' not in worker_name:
            return

        self.name = worker_name
        self.run_type = run_type
        self.sibling_worker_num = sibling_worker_num

        msg_task_id = message['task_id']

        params = {'conditions': {'name': worker_name}, 'limit': 1}
        wkinfo = query_database(TABLE_RUNNERS, params)[0]

        bandwidth_limit = json.loads(wkinfo['node_settings'])['bandwidth']
        fastdfs_cli.set_runner_info(FL_SYSTEM_FEDAVG, self.name)
        fastdfs_cli.set_bandwidth_limit(bandwidth_limit)

        task_id = wkinfo['binded_task_id']

        # task not scheduled to this worker
        if not task_id:
            print_log('task id is None, not {}\'s task'.format(self.name))
            return

        if task_id == FLAG_ALL_TASKS_ALLOWED:
            self.task_id = msg_task_id
        elif task_id == msg_task_id:
            self.task_id = task_id
        else:
            # not my task, ignore it
            self.status = RUNNER_STATUS_SLEEP
            return

        params = {'conditions': {'id': self.task_id}, 'limit': 1}
        task_info_list = query_database(TABLE_FEDAVG_TASK_POOL, params)

        # 任务完成，被转移到backup数据库
        if len(task_info_list) == 0:
            return

        task_info = task_info_list[0]

        self.task_status = task_info['status']
        if self.task_status != TASK_STATUS_RUNNING:
            print_log('{} task not running'.format(self.name))
            return

        if task_info['required_flsim_version'] != FLSIM_VERION:
            print_log('{} version error'.format(self.name))
            return

        params = {'conditions': {'task_id': self.task_id, 'fl_system': FL_SYSTEM_FEDAVG, 'runner_name': self.name}, 'limit': 1}
        rtset_info_list = query_database(TABLE_RUNNER_TASK_SETTINGS, params)
        if len(rtset_info_list) == 0:
            return

        rtset_info = rtset_info_list[0]

        self.runner_mode, self.dataset_id = rtset_info['runner_mode'], rtset_info['dataset_id']

        self.runtime_params = json.loads(rtset_info['runtime_params'])
        self.framework_params = self.runtime_params['framework_params']
        self.weights_cache_enabled = self.runtime_params['weights_cache_enabled']
        self.attack_params = self.runtime_params['attack_params']
        self.model_params = self.runtime_params['model_params']
        self.model_name = self.model_params['model_name']

        # reject training with a certain probability
        if self.run_type == RUN_TYPE_PROD and random.random() > self.framework_params['accept_prob'] * self.sibling_worker_num:
            print_log('{} random quit'.format(self.name))
            return

        params = {'conditions': {'id': self.dataset_id}, 'limit': 1}
        dtinfo = query_database(TABLE_DATASETS, params)[0]

        self.dataset_obj = load_dataset_with_dataset_info(dtinfo, worker_name)

        self.model_obj = create_model_with_params(self.model_params)

        if self.runner_mode == RUNNER_MODE_BACKDOOR:
            self.dataset_obj = add_backdoor_to_dataset(dtinfo['source'], self.dataset_obj, self.attack_params['backdoor'])
        elif self.runner_mode == RUNNER_MODE_NOISE:
            self.dataset_obj = add_noise_to_dataset(dtinfo['source'], self.dataset_obj, self.attack_params['noise'])
        elif self.runner_mode == RUNNER_MODE_POISON:
            self.dataset_obj = add_poison_to_dataset(dtinfo['source'], self.dataset_obj, self.attack_params['poison'])

        self.status = RUNNER_STATUS_IDLE

    def prepare_base_weights(self):

        params = {'conditions': {'task_id': self.task_id, '_type': WEIGHTS_TYPE_GLOBAL}, 'order': {'key': 'create_time', 'value': 'desc'}, 'limit': 1}
        latest_global_weights_info = query_database(TABLE_FEDAVG_WEIGHTS_POOL, params)[0]

        return download_weights(latest_global_weights_info, self.weights_cache_enabled), [latest_global_weights_info['id'], ]

    def run(self):

        print_log('{} run training task'.format(self.name))

        exec_hist = dict()
        exec_hist['runner_name'] = self.name
        exec_hist['fl_system'] = FL_SYSTEM_FEDAVG
        exec_hist['task_id'] = self.task_id
        exec_hist['start_time'] = current_strftime()
        exec_hist['status'] = 'aborted'

        used_time = dict()

        start_time = current_timestamp()

        base_weights, source_weights_ids = self.prepare_base_weights()

        if base_weights is None:
            exec_hist['message'] = 'base weights is None'
            add_runner_executation_history(exec_hist)

            return
        
        used_time['weights_prepare'] = current_timestamp() - start_time

        start_time = current_timestamp()

        # train local model based on aggregated model
        # 传入worker mode，如果dishonest，则不训练
        if self.runner_mode == RUNNER_MODE_DISHONEST:
            self.model_params['epochs'] = 0

        performance = train_model(self.model_obj, base_weights, self.model_params, self.dataset_obj)

        used_time['model_train'] = current_timestamp() - start_time

        weights_id, weights_hash, pickled_weights = pickle_model_weights(self.model_obj.get_weights())
        weights_config = {'weights_id': weights_id, 'weights_hash': weights_hash, 'pickled_weights': pickled_weights, 'source_weights_ids': source_weights_ids,
                          'contributor': self.name, 'contributor_mode': self.runner_mode, 'task_id': self.task_id, 'performance': performance, 'used_time': used_time,
                          'extra': '', '_type': WEIGHTS_TYPE_LOCAL, 'is_aggregated': 0, 'is_trained': 1}
        
        contribute_weights(FL_SYSTEM_FEDAVG, weights_config, True)

        exec_hist['complete_time'] = current_strftime()
        exec_hist['status'] = 'done'
        exec_hist['message'] = 'weights {} is uploaded'.format(weights_id)

        add_runner_executation_history(exec_hist)


last_accept_time = dict()


def process_message(worker_names, message, run_type):
    global last_accept_time

    virtual_worker_names = worker_names.split('_')

    # selected_worker_name = random.choice(virtual_worker_names)

    worker = None

    random.shuffle(virtual_worker_names)
    for selected_worker_name in virtual_worker_names[:1]:

        if worker is not None:
            del worker.model_obj
            del worker.dataset_obj
            del worker
            worker = None

        update_runner_active_info(selected_worker_name)

        if message['event'] == EVENT_TASK_DONE:
            continue

        ftu_id = '{}-{}-{}'.format(message['fl_system'], message['task_id'], selected_worker_name)
        # if current_timestamp() - last_accept_time.get(ftu_id, 0) < 12:
            # continue

        worker = Worker(selected_worker_name, message, run_type, len(virtual_worker_names))
        if worker.status == RUNNER_STATUS_SLEEP:
            continue

        if message['sender'] == worker.name:
            continue

        if message['event'] == EVENT_TASK_PUBLISHED or message['event'] == EVENT_GLOBAL_WEIGHTS_UPLOADED:
            last_accept_time[ftu_id] = current_timestamp()
            worker.run()
            continue
