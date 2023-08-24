import json
import random

from flexpkit.dataset_utils import *
from flexpkit.exp_constants import *
from flexpkit.exp_settings import *
from flexpkit.exp_utils import *
from flexpkit.fastdfs_utils import *
from flexpkit.model_utils import *
from flexpkit.mysql_utils import *
from flexpkit.redis_utils import *
from flexpkit.weights_utils import *
from ironforge.local_utils import *

use_evaluated_weights = True
include_my_weights = False


class Worker:
    name = None
    status = RUNNER_STATUS_SLEEP

    mode = RUNNER_MODE_NORMAL
    dataset_shard_id = None

    task_id = None
    task_status = TASK_STATUS_RUNNING
    framework_settings = {}

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

        params = {'conditions': {'name': worker_name}, 'limit': 1}
        wkinfo = query_database(TABLE_RUNNERS, params)[0]

        self.node_type = wkinfo['node_type']

        bandwidth_limit = json.loads(wkinfo['node_settings'])['bandwidth']
        fastdfs_cli.set_runner_info(FL_SYSTEM_IRONFORGE, self.name)
        fastdfs_cli.set_bandwidth_limit(bandwidth_limit)

        task_id = wkinfo['binded_task_id']

        # task not scheduled to this worker
        if not task_id:
            print_log('task id is None, not {}\'s task'.format(self.name))
            return

        msg_task_id = message['task_id']

        if task_id == FLAG_ALL_TASKS_ALLOWED:
            self.task_id = msg_task_id
        elif task_id == msg_task_id:
            self.task_id = task_id
        else:
            # not my task, ignore it
            self.status = RUNNER_STATUS_SLEEP
            return

        params = {'conditions': {'id': self.task_id}, 'limit': 1}
        task_info_list = query_database(TABLE_IRONFORGE_TASK_POOL, params)
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

        params = {'conditions': {'task_id': self.task_id, 'fl_system': FL_SYSTEM_IRONFORGE, 'runner_name': self.name}, 'limit': 1}
        rtset_info_list = query_database(TABLE_RUNNER_TASK_SETTINGS, params)
        if len(rtset_info_list) == 0:
            print_log('{} not task associated runner'.format(self.name))
            return

        rtset_info = rtset_info_list[0]

        self.runner_mode, self.dataset_id = rtset_info['runner_mode'], rtset_info['dataset_id']

        params = {'conditions': {'id': self.dataset_id}, 'limit': 1}
        dtinfo = query_database(TABLE_DATASETS, params)[0]

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

        print_log('{} prepare base weights'.format(self.name))

        used_time = dict()
        start_time = current_timestamp()

        # 不推荐aggregated=0，因为无法确保真实性
        # params = {'conditions': {'task_id': self.task_id, 'is_aggregated': 0}, 'limit': 10}

        params = {'conditions': {'task_id': self.task_id}, 'order': {'key': 'create_time', 'value': 'desc'}, 'limit': self.framework_params['sample_size']}
        candidate_weights_info_list = query_database(TABLE_IRONFORGE_WEIGHTS_POOL, params)

        # 只选择local weights进行aggregate
        # 不能直接在query中设定_type为local，因为publisher发布的weights是global的
        candidate_weights_info_list = [cwi for cwi in candidate_weights_info_list if cwi['_type'] == WEIGHTS_TYPE_LOCAL or cwi['contributor'] == 'publisher']

        candidate_size = len(candidate_weights_info_list)

        # PoL可以排除dishonest worker uploaded weights
        candidate_weights_info_list = [cw for cw in candidate_weights_info_list if cw['pol'] == POL_VERIFIED]
        candidate_weights_info_list = [cw for cw in candidate_weights_info_list if not check_weights_aggregated(cw['id'], self.dataset_id)]

        if len(candidate_weights_info_list) == 0:
            return None, None, None

        # 由于每个worker查询到的weights都是类似的，如果选取固定的几个weights（如top n），则其余weights将被忽略
        candidate_size = self.framework_params['candidate_size']
        if len(candidate_weights_info_list) > candidate_size:
            candidate_weights_info_list = random.sample(candidate_weights_info_list, candidate_size)

        if self.runner_mode == RUNNER_MODE_DISHONEST:
            dishonest_weights_info = random.choice(candidate_weights_info_list)
            dishonest_weights = download_weights(dishonest_weights_info, self.weights_cache_enabled)

            return dishonest_weights, [dishonest_weights_info['id'], ], [dishonest_weights_info['id'], ]

        aggregation_size = self.framework_params['aggregation_size']
        if candidate_size < aggregation_size:
            aggregation_size = candidate_size

        if use_evaluated_weights:
            evaluate_new_weights(candidate_weights_info_list, self.model_obj, self.dataset_obj, self.task_id, self.dataset_id, self.name, self.weights_cache_enabled)
            preferred_weights_info_list = select_preferred_weights_info_list_from_evaluation_history(self.task_id, self.dataset_id, top_n=aggregation_size)
        else:
            preferred_weights_info_list = random.sample(candidate_weights_info_list, aggregation_size)

        if not preferred_weights_info_list or len(preferred_weights_info_list) == 0:
            return None, None, None

        # if include_my_weights:
            # my_weights_info_list = [cw for cw in candidate_weights_info_list if cw['contributor'] == self.name]
            # preferred_weights_info_list.extend(my_weights_info_list)

        # remove duplicate weights
        preferred_weights_info_map = {wi['id']: wi for wi in preferred_weights_info_list}
        preferred_weights_info_list = list(preferred_weights_info_map.values())

        good_weights_map = batch_download_weights(preferred_weights_info_list, self.weights_cache_enabled)
        # if len(good_weights_map) > 12:
            # good_weights_keys = random.sample(good_weights_map.keys(), 12)
            # good_weights_map = {k: v for k, v in good_weights_map.items() if k in good_weights_keys}

        aggr_weights = aggregate_weights(good_weights_map)

        selected_weights_ids = list(good_weights_map.keys())

        # 偷个懒，复用update_weights_aggregated这个函数；错了，这样将导致其他worker无法使用该weights，因为cache的primary key是weights+dataset
        # update_weights_aggregated(TABLE_IRONFORGE_WEIGHTS_LOCAL_EVALUATION, selected_weights_ids)
        for wi in selected_weights_ids:
            update_weights_local_evaluation_aggregated(wi, self.dataset_id)
        
        update_weights_aggregated(TABLE_IRONFORGE_WEIGHTS_POOL, selected_weights_ids)

        weights_id, weights_hash, pickled_weights = pickle_model_weights(aggr_weights)
        used_time['weights_prepare'] = current_timestamp() - start_time
        used_time['model_train'] = 0
        weights_config = {'weights_id': weights_id, 'weights_hash': weights_hash, 'pickled_weights': pickled_weights, 'source_weights_ids': selected_weights_ids,
                          'contributor': self.name, 'contributor_mode': self.runner_mode, 'task_id': self.task_id, 'performance': {'loss': 0, 'accuracy': 0}, 'used_time': used_time, 
                          '_type': WEIGHTS_TYPE_GLOBAL, 'is_aggregated': 0, 'is_trained': 0, 'extra': ''}

        contribute_weights(FL_SYSTEM_IRONFORGE, weights_config, True)

        for _, gw in good_weights_map.items():
            del gw

        # return aggr_weights, selected_weights_ids
        return aggr_weights, [weights_id, ], selected_weights_ids

    def run(self):

        print_log('{} run training task'.format(self.name))

        exec_hist = dict()
        exec_hist['runner_name'] = self.name
        exec_hist['fl_system'] = FL_SYSTEM_IRONFORGE
        exec_hist['task_id'] = self.task_id
        exec_hist['start_time'] = current_strftime()
        exec_hist['status'] = 'aborted'

        used_time = dict()

        start_time = current_timestamp()

        base_weights, source_weights_ids, selected_weights_id = self.prepare_base_weights()

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
                          '_type': WEIGHTS_TYPE_LOCAL, 'is_aggregated': 0, 'is_trained': 1, 'extra': {'true_source': selected_weights_id}}
        
        contribute_weights(FL_SYSTEM_IRONFORGE, weights_config, True)

        exec_hist['complete_time'] = current_strftime()
        exec_hist['status'] = 'done'
        exec_hist['message'] = 'weights {} is uploaded'.format(weights_id)

        add_runner_executation_history(exec_hist)

    def raise_challenge(self, message):
        key = 'challenge_{}'.format(message['weights_id'])
        if not redis_cli.set_lock(key, current_timestamp()):
            print('weights have been challenged')
            return

        event = {'event': 'challenge raised', 'task_id': self.task_id, 'weights_id': message['weights_id'],
                 'contributor': message['sender'], 'fl_system': FL_SYSTEM_IRONFORGE}
        redis_cli.broadcast(MESSAGE_QUEUE_NAME_AGENT, self.name, event)


last_accept_time = dict()


def process_message(worker_names, message, run_type):
    global last_accept_time

    virtual_worker_names = worker_names.split('_')

    # selected_worker_name = random.choice(virtual_worker_names)

    worker = None
    random.shuffle(virtual_worker_names)
    for selected_worker_name in virtual_worker_names[:1]:

        # 设置消息的超时机制
        # if 'timestamp' in message and current_timestamp() - strftime_to_timestamp(message['timestamp']) > 10:
            # print_log('{} message timeout, stop processing'.format(selected_worker_name))
            # return

        if worker is not None:
            del worker.model_obj
            del worker.dataset_obj
            del worker
            worker = None

        update_runner_active_info(selected_worker_name)

        if message['event'] == EVENT_TASK_DONE:
            continue

        ftu_id = '{}-{}-{}'.format(message['fl_system'], message['task_id'], selected_worker_name)
        if current_timestamp() - last_accept_time.get(ftu_id, 0) < 10:
            continue

        worker = Worker(selected_worker_name, message, run_type, len(virtual_worker_names))
        if worker.status == RUNNER_STATUS_SLEEP:
            continue

        if message['event'] == EVENT_TASK_PUBLISHED and message['sender'] != worker.name:
            worker.run()
            last_accept_time[ftu_id] = current_timestamp()

            continue

        if message['event'] == EVENT_GLOBAL_WEIGHTS_UPLOADED and message['sender'] != worker.name:

            # 已一定概率执行，否则资源占用率过高
            # 但概率不能低于0.1，否则*acceptance prob，要少于1，导致任务无法被驱动
            if random.random() >= 0.25 * RUNNER_NUM_EACH_NODE:
                continue

            worker.raise_challenge(message)

            worker.run()
            last_accept_time[ftu_id] = current_timestamp()

            continue