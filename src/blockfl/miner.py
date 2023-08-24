import json
import random

from blockfl.local_utils import *
from flexpkit.basic_utils import *
from flexpkit.exp_constants import *
from flexpkit.exp_settings import *
from flexpkit.exp_utils import *
from flexpkit.mysql_utils import *
from flexpkit.fastdfs_utils import *
from flexpkit.redis_utils import *
from flexpkit.weights_utils import *


class Miner:

    name = None
    task_id = None

    binded_workers = None

    status = RUNNER_STATUS_SLEEP

    def __init__(self, miner_name, message, run_type):
        if 'miner' not in miner_name:
            return

        self.task_id = message['task_id']
        self.run_type = run_type

        self.name = miner_name

        params = {'conditions': {'name': miner_name}, 'limit': 1}
        minfo = query_database(TABLE_RUNNERS, params)[0]

        self.binded_workers = json.loads(minfo['extra'])['binded_workers']

        bandwidth_limit = json.loads(minfo['node_settings'])['bandwidth']
        fastdfs_cli.set_runner_info(FL_SYSTEM_BLOCKFL, self.name)
        fastdfs_cli.set_bandwidth_limit(bandwidth_limit)

        params = {'conditions': {'task_id': self.task_id, 'fl_system': FL_SYSTEM_BLOCKFL, 'runner_name': self.name}, 'limit': 1}
        rtset_info = query_database(TABLE_RUNNER_TASK_SETTINGS, params)[0]

        self.runtime_params = json.loads(rtset_info['runtime_params'])

        self.weights_cache_enabled = self.runtime_params['weights_cache_enabled']
        self.framework_params = self.runtime_params['framework_params']

        params = {'conditions': {'id': self.task_id}, 'limit': 1}
        task_info_list = query_database(TABLE_BLOCKFL_TASK_POOL, params)
        if len(task_info_list) == 0:
            return

        task_info = task_info_list[0]

        self.task_status = task_info['status']
        if self.task_status != TASK_STATUS_RUNNING or task_info['required_flsim_version'] != FLSIM_VERION:
            return

        self.status = RUNNER_STATUS_IDLE

    def run(self):

        print_log('{} run mining task'.format(self.name))

        exec_hist = dict()
        exec_hist['runner_name'] = self.name
        exec_hist['fl_system'] = FL_SYSTEM_BLOCKFL
        exec_hist['task_id'] = self.task_id
        exec_hist['start_time'] = current_strftime()
        exec_hist['status'] = 'aborted'

        # 按照blockfl的规则，先到先加入到缓存，所以应该是按照时间顺序排列
        # 应该是从监听开始算，所以不应该是asc排序
        params = {'conditions': {'task_id': self.task_id, '_type': WEIGHTS_TYPE_LOCAL, 'is_aggregated': 0}, 'order': {'key': 'create_time', 'value': 'desc'}, 'limit': 10}
        weights_info_list = query_database(TABLE_BLOCKFL_WEIGHTS_POOL, params)
        
        if len(weights_info_list) == 0:
            exec_hist['message'] = 'weights_info_list is empty'
            add_runner_executation_history(exec_hist)

            return

        candidate_weights_info_list = [wi for wi in weights_info_list if wi['contributor'] in self.binded_workers]
        if len(candidate_weights_info_list) == 0:
            exec_hist['message'] = 'candidate_weights_info_list is empty'
            add_runner_executation_history(exec_hist)

            return

        latest_weights_create_time = datetime_to_timestamp(candidate_weights_info_list[0]['create_time'])

        least_transactions = self.framework_params['least_size']
        most_transactions = self.framework_params['most_size']

        # 最新的weights在1分钟内之前创建，即很久没有新的weights生成
        if len(candidate_weights_info_list) < least_transactions and current_timestamp() - latest_weights_create_time < 60 * 1:
            exec_hist['message'] = 'long time no new local weights!'
            add_runner_executation_history(exec_hist)

            return None

        used_time = dict()

        start_time = current_timestamp()

        random.shuffle(candidate_weights_info_list)
        candidate_weights_id_list = [wi['id'] for wi in candidate_weights_info_list][:most_transactions]
        nonce, block_hash = mine_block(candidate_weights_id_list)
        if not nonce:
            exec_hist['message'] = 'block nonce not found'
            add_runner_executation_history(exec_hist)

            return

        params = {'conditions': {'task_id': self.task_id, '_type': WEIGHTS_TYPE_GLOBAL}, 'order': {'key': 'create_time', 'value': 'desc'}, 'limit': 1}
        global_weights_info_list = query_database(TABLE_BLOCKFL_WEIGHTS_POOL, params)

        if len(global_weights_info_list) < 1:
            exec_hist['message'] = 'block mined by others'
            add_runner_executation_history(exec_hist)

            return None

        latest_global_weights_info = global_weights_info_list[0]

        lock_key = 'block_{}'.format(latest_global_weights_info['id'])
        lock_value = '{}###{}'.format(self.name, current_timestamp())

        if not redis_cli.set_lock(lock_key, value=lock_value, lock_timeout=-1):
            lock_value = redis_cli.get_lock_value(lock_key)
            lock_owner, lock_time = lock_value.split('###')

            print('{} block seized by {}'.format(self.name, lock_owner))

            # latest global weights已经产生一段时间，说明已经很久没有生成block，但相关的锁已经存在
            if self.name == lock_owner:
                redis_cli.remove_lock(lock_key)

            elif current_timestamp() - datetime_to_timestamp(latest_global_weights_info['create_time']) > 60 * 1:

                # 相关的锁已经存在超过10秒，照理说，本轮block已经生成，即本轮global weights已经存在。
                # 所以，大概率这个lock有问题，需删除
                # 考虑到节点中带宽有限，weights下载速度方面会有一定影响，因此考虑至少等待20s
                if current_timestamp() - float(lock_time) > 20:
                    redis_cli.remove_lock(lock_key)
                    return
            else:
                return

        print('{} mined'.format(self.name))

        used_time['mine_block'] = current_timestamp() - start_time

        start_time = current_timestamp()
        candidate_weights_list = batch_download_weights(candidate_weights_info_list, self.weights_cache_enabled)
        used_time['weights_prepare'] = current_timestamp() - start_time

        start_time = current_timestamp()

        aggr_weights = aggregate_weights(candidate_weights_list)

        used_time['weights_aggregate'] = current_timestamp() - start_time

        weights_id, weights_hash, pickled_weights = pickle_model_weights(aggr_weights)
        weights_config = {'weights_id': weights_id, 'weights_hash': weights_hash, 'pickled_weights': pickled_weights, 'source_weights_ids': candidate_weights_id_list,
                          'contributor': self.name, 'contributor_mode': '', 'task_id': self.task_id, 'performance': {'loss': 0, 'accuracy': 0}, 
                          'used_time': used_time, 'extra': {'nonce': nonce, 'hash': block_hash}, '_type': WEIGHTS_TYPE_GLOBAL, 'is_aggregated': 0, 'is_trained': 0}
        
        contribute_weights(FL_SYSTEM_BLOCKFL, weights_config, True)

        update_weights_aggregated(TABLE_BLOCKFL_WEIGHTS_POOL, candidate_weights_id_list)

        print_log('block contributed by {}'.format(self.name))

        exec_hist['complete_time'] = current_strftime()
        exec_hist['status'] = 'done'
        exec_hist['message'] = 'weights {} is uploaded'.format(weights_id)

        add_runner_executation_history(exec_hist)


def process_message(miner_name, message, run_type):
    miner = Miner(miner_name, message, run_type)
    if miner.status == RUNNER_STATUS_SLEEP:
        return

    update_runner_active_info(miner_name)

    miner.run()

    del miner

