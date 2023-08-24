import json

from flexpkit.basic_utils import *
from flexpkit.exp_constants import *
from flexpkit.exp_settings import *
from flexpkit.exp_utils import *
from flexpkit.fastdfs_utils import *
from flexpkit.mysql_utils import *
from flexpkit.weights_utils import *


class Master:

    name = None
    task_id = None

    status = RUNNER_STATUS_SLEEP

    def __init__(self, master_name, message, run_type):
        if 'master' not in master_name:
            return

        self.name = master_name
        self.task_id = message['task_id']

        self.run_type = run_type

        params = {'conditions': {'name': master_name}, 'limit': 1}
        minfo = query_database(TABLE_RUNNERS, params)[0]

        bandwidth_limit = json.loads(minfo['node_settings'])['bandwidth']
        fastdfs_cli.set_runner_info(FL_SYSTEM_FEDAVG, self.name)
        fastdfs_cli.set_bandwidth_limit(bandwidth_limit)

        if not minfo['extra']:
            return

        extra = json.loads(minfo['extra'])
        if extra['binded_fl_system'] != message['fl_system'] or extra['binded_task_id'] != self.task_id:
            return

        params = {'conditions': {'task_id': self.task_id, 'fl_system': FL_SYSTEM_FEDAVG, 'runner_name': self.name}, 'limit': 1}
        rtset_info = query_database(TABLE_RUNNER_TASK_SETTINGS, params)[0]

        self.runtime_params = json.loads(rtset_info['runtime_params'])

        self.weights_cache_enabled = self.runtime_params['weights_cache_enabled']
        self.framework_params = self.runtime_params['framework_params']

        params = {'conditions': {'id': self.task_id}, 'limit': 1}
        task_info_list = query_database(TABLE_FEDAVG_TASK_POOL, params)
        if len(task_info_list) == 0:
            return

        task_info = task_info_list[0]
        self.task_status = task_info['status']
        if self.task_status != TASK_STATUS_RUNNING or task_info['required_flsim_version'] != FLSIM_VERION:
            return

        self.status = RUNNER_STATUS_IDLE

    def run(self):

        print_log('{} run aggregation task'.format(self.name))

        exec_hist = dict()
        exec_hist['runner_name'] = self.name
        exec_hist['fl_system'] = FL_SYSTEM_FEDAVG
        exec_hist['task_id'] = self.task_id
        exec_hist['start_time'] = current_strftime()
        exec_hist['status'] = 'aborted'

        least_weights_count = self.framework_params['least_size']
        most_weights_count = self.framework_params['most_size']

        # 取TASk_HPYSICAL_NODE_NUM的话，对fedavg是一种优化
        # params = {'conditions': {'task_id': self.task_id, '_type': WEIGHTS_TYPE_LOCAL, 'is_aggregated': 0}, 'limit': PHYSICAL_NODE_NUM_EACH_TASK}

        params = {'conditions': {'task_id': self.task_id, '_type': WEIGHTS_TYPE_LOCAL, 'is_aggregated': 0}, 'order': {'key': 'create_time', 'value': 'desc'}, 'limit': 60}
        weights_info_list = query_database(TABLE_FEDAVG_WEIGHTS_POOL, params)

        # 需要区分轮次，因此需要根据最新的global weights的id，来选择local weights

        params = {'conditions': {'task_id': self.task_id, '_type': WEIGHTS_TYPE_GLOBAL}, 'order': {'key': 'create_time', 'value': 'desc'}, 'limit': 1}
        latest_global_weights_info = query_database(TABLE_FEDAVG_WEIGHTS_POOL, params)[0]

        # 所有包含本轮global weights id的local weights
        # NOTE 必须取消这个限制，否则效率极低
        # weights_info_list = [wi for wi in weights_info_list if latest_global_weights_info['id'] in wi['source_weights_ids']]
        if len(weights_info_list) == 0:
            exec_hist['message'] = 'weights_info_list is empty'
            add_runner_executation_history(exec_hist)

            return

        contributors = [wi['contributor'] for wi in weights_info_list]
        latest_weights_create_time = datetime_to_timestamp(weights_info_list[0]['create_time'])

        # 至少超过x个weights，或者最新的weights与1分钟内之前创建
        if len(set(contributors)) < least_weights_count and current_timestamp() - latest_weights_create_time < 60 * 1:
            exec_hist['message'] = 'contributor num: {}, less than {}'.format(len(set(contributors)), least_weights_count)
            add_runner_executation_history(exec_hist)

            return None

        selected_weights_info_list = weights_info_list[:most_weights_count]

        used_time = dict()

        start_time = current_timestamp()
        weights_list = batch_download_weights(selected_weights_info_list, self.weights_cache_enabled)
        used_time['weights_prepare'] = current_timestamp() - start_time

        start_time = current_timestamp()

        aggr_weights = aggregate_weights(weights_list)

        used_time['weights_aggregate'] = current_timestamp() - start_time

        source_weights_ids = list(weights_list.keys())

        weights_id, weights_hash, pickled_weights = pickle_model_weights(aggr_weights)
        weights_config = {'weights_id': weights_id, 'weights_hash': weights_hash, 'pickled_weights': pickled_weights, 'source_weights_ids': source_weights_ids,
                          'contributor': self.name, 'contributor_mode': '', 'task_id': self.task_id, 'performance': {'loss': 0, 'accuracy': 0}, 
                          'used_time': used_time, 'extra': '', '_type': WEIGHTS_TYPE_GLOBAL, 'is_aggregated': 0, 'is_trained': 0}
        
        contribute_weights(FL_SYSTEM_FEDAVG, weights_config, True)

        update_weights_aggregated(TABLE_FEDAVG_WEIGHTS_POOL, source_weights_ids)

        exec_hist['complete_time'] = current_strftime()
        exec_hist['status'] = 'done'
        exec_hist['message'] = 'weights {} is uploaded'.format(weights_id)

        add_runner_executation_history(exec_hist)


def process_message(master_name, message, run_type):
    master = Master(master_name, message, run_type)
    if master.status == RUNNER_STATUS_SLEEP:
        return

    update_runner_active_info(master_name)

    master.run()
    del master