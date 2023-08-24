import json
import os
import random

import numpy as np
import tensorflow as tf
from flexpkit.basic_utils import current_strftime, current_timestamp, datetime_to_timestamp, timestamp_to_strftime

from flexpkit.exp_constants import (DATASET_CIFAR10, DATASET_MNIST, DATASET_SHAKESPEARE,
                                    EVENT_GLOBAL_WEIGHTS_UPLOADED, EVENT_LOCAL_WEIGHTS_UPLOADED,
                                    EVENT_TASK_PUBLISHED, FLSIM_VERION, MESSAGE_QUEUE_NAME_AGENT, 
                                    NO_BACKDOOR_PARAMS, NO_DISHONEST_PARAMS, NO_NOISE_PARAMS, 
                                    NO_POISON_PARAMS, RUNNER_TYPE_WORKER, STORAGE_FASTDFS, TABLE_DATASETS, 
                                    TABLE_DIAGNOSE_RUNNER_RUNTIME_ERRORS,
                                    TABLE_RUNNER_TASK_SETTINGS, TABLE_DIAGNOSE_WHOLE_TASKS_PROGRESS, 
                                    TABLE_DIAGNOSE_TASK_SCHEDULING_HISTORY, TABLE_RUNNERS,
                                    TASK_STATUS_STOPPED, WEIGHTS_TYPE_GLOBAL, RUNNER_MODE_BACKDOOR, 
                                    RUNNER_MODE_DISHONEST, RUNNER_MODE_NOISE,
                                    RUNNER_MODE_NORMAL, RUNNER_MODE_POISON)

from flexpkit.mysql_utils import (execute_update_sql, get_task_table, get_weights_table,
                                  insert_database, query_database, update_database)
from flexpkit.redis_utils import redis_cli
from flexpkit.weights_utils import upload_weights


def enable_reproducible_results(seed=None):
    """
    use fixed global random seeds to get reproducible results. 
    NEVER use tf.random.set_seed(None)

    :param seed: an integer value, if seed == None, use system seed.
    """
    if seed is None:
        return

    os.environ['PYTHONHASHSEED'] = str(seed)

    random.seed(seed)
    tf.random.set_seed(seed)
    np.random.seed(seed)

    os.environ['TF_DETERMINISTIC_OPS'] = '1'
    os.environ['TF_CUDNN_DETERMINISTIC'] = '1'

    # tf.config.threading.set_inter_op_parallelism_threads(1)
    # tf.config.threading.set_intra_op_parallelism_threads(1)


def generate_dataset_id(*args):
    """
    1. dataset source
    2. dataset sharding schema
    3. dataset shard id
    4. dataset type
    5. noisy ratio
    6. poison ratio

    """
    return '-'.join([str(x) for x in args])


def generate_runner_name(runner_type, rid):
    return 'flsim-{}-{}'.format(runner_type, str(rid).zfill(5))


def generate_poison_params_schema1(worker_num, poisoner_num, ratio=0.2):
    result = []

    result.extend([{'ratio': ratio} for i in range(poisoner_num)])
    result.extend([{'ratio': 0} for i in range(worker_num - poisoner_num)])

    return result


def generate_noise_params_schema1(worker_num, noiser_num, dataset_source, ratio=0.2):
    result = []
    if dataset_source in (DATASET_MNIST, DATASET_CIFAR10):
        result.extend([{'gaussian': {'ratio': ratio, 'mean': 0,
                      'stddev': 0.2}} for i in range(noiser_num)])
        result.extend([{'gaussian': {'ratio': 0, 'mean': 0, 'stddev': 0}}
                      for i in range(worker_num - noiser_num)])

    elif dataset_source == DATASET_SHAKESPEARE:
        result.extend([{'flip': {'ratio': ratio, 'flip_times': 1}}
                      for i in range(noiser_num)])
        result.extend([{'flip': {'ratio': 0, 'flip_times': 0}}
                      for i in range(worker_num - noiser_num)])
    else:
        result = NO_NOISE_PARAMS

    return result


def choose_workers(node_type_dict, use_random=True):
    params = {'conditions': {'_type': RUNNER_TYPE_WORKER}}
    runner_info_list = query_database(TABLE_RUNNERS, params)

    runner_type_map = dict()
    for ri in runner_info_list:
        node_type = ri['node_type']
        if node_type not in runner_type_map:
            runner_type_map[node_type] = []

        runner_type_map[node_type].append(ri['name'])

    worker_name_list = []
    for node_type, count in node_type_dict.items():
        if use_random:
            worker_names = random.sample(runner_type_map[node_type], count)
        else:
            worker_names = runner_type_map[node_type][:count]

        worker_name_list.extend(worker_names)

    return worker_name_list


def batch_create_master_task_settings(task_settings):
    task_id = task_settings['task_id']
    fl_system = task_settings['fl_system']

    master_name_list = task_settings['master_name_list']
    master_num = len(master_name_list)

    framework_params_list = task_settings['framework_master_params_list']

    rtset_info_list = []
    for idx in range(master_num):
        master_name = master_name_list[idx]

        runtime_params = {}
        runtime_params['weights_cache_enabled'] = task_settings['weights_cache_enabled']
        runtime_params['framework_params'] = framework_params_list[idx]
        runtime_params = '''{}'''.format(runtime_params)

        rtset_info = {'runner_name': master_name, 'task_id': task_id, 'fl_system': fl_system,
                      'runner_mode': '', 'dataset_id': '', 'runtime_params': runtime_params, 'extra': ''}
        rtset_info_list.append(rtset_info)

    insert_database(TABLE_RUNNER_TASK_SETTINGS,
                          rtset_info_list, ignore_exist=True, insert_many=True)


def batch_create_miner_task_settings(task_settings):
    task_id = task_settings['task_id']
    fl_system = task_settings['fl_system']

    miner_name_list = task_settings['miner_name_list']
    miner_num = len(miner_name_list)

    framework_params_list = task_settings['framework_miner_params_list']

    rtset_info_list = []
    for idx in range(miner_num):
        miner_name = miner_name_list[idx]

        runtime_params = {}
        runtime_params['weights_cache_enabled'] = task_settings['weights_cache_enabled']
        runtime_params['framework_params'] = framework_params_list[idx]
        runtime_params = '''{}'''.format(runtime_params)

        rtset_info = {'runner_name': miner_name, 'task_id': task_id, 'fl_system': fl_system,
                      'runner_mode': '', 'dataset_id': '', 'runtime_params': runtime_params, 'extra': ''}
        rtset_info_list.append(rtset_info)

    insert_database(TABLE_RUNNER_TASK_SETTINGS,
                          rtset_info_list, ignore_exist=True, insert_many=True)


def batch_create_worker_task_settings(task_settings):
    task_id = task_settings['task_id']
    fl_system = task_settings['fl_system']

    worker_mode_list = task_settings['worker_mode_list']
    worker_num = len(worker_mode_list)

    worker_name_list = task_settings['worker_name_list']

    dataset_source = task_settings['dataset_source']
    dataset_sharding_schema = task_settings['dataset_sharding_schema']

    params = {'conditions': {'source': dataset_source,
                             'sharding_schema': dataset_sharding_schema, '_usage': 'trainset'}}
    dataset_shard_info_list = query_database(TABLE_DATASETS, params)

    dataset_shard_ids = [dsi['id'] for dsi in dataset_shard_info_list]
    selected_dataset_shard_ids = random.sample(dataset_shard_ids, worker_num)

    backdoor_config_list = task_settings['backdoor_config_list']
    noise_config_list = task_settings['noise_config_list']
    poison_config_list = task_settings['poison_config_list']
    model_params_list = task_settings['model_params_list']
    framework_params_list = task_settings['framework_worker_params_list']

    rtset_info_list = []
    for idx in range(worker_num):
        worker_name = worker_name_list[idx]
        worker_mode = worker_mode_list[idx]
        dataset_id = selected_dataset_shard_ids[idx]

        runtime_params = {}
        runtime_params['weights_cache_enabled'] = task_settings['weights_cache_enabled']
        runtime_params['attack_params'] = {'poison': poison_config_list[idx],
                                           'noise': noise_config_list[idx], 'backdoor': backdoor_config_list[idx]}
        runtime_params['model_params'] = model_params_list[idx]
        runtime_params['model_params'].update(
            {'model_name': task_settings['model_name']})
        runtime_params['framework_params'] = framework_params_list[idx]
        runtime_params = '''{}'''.format(runtime_params)

        rtset_info = {'runner_name': worker_name, 'task_id': task_id, 'fl_system': fl_system,
                      'runner_mode': worker_mode, 'dataset_id': dataset_id, 'runtime_params': runtime_params, 'extra': ''}
        rtset_info_list.append(rtset_info)

    insert_database(TABLE_RUNNER_TASK_SETTINGS,
                          rtset_info_list, ignore_exist=True, insert_many=True)


def _publish_task(fl_system, task_config, broadcast_it=False):
    """
    save task to database
    """

    task_table = get_task_table(fl_system)

    task_config['required_flsim_version'] = FLSIM_VERION
    insert_database(task_table, task_config, ignore_exist=False)

    if broadcast_it:
        # notify agents to handle task
        event = {'event': EVENT_TASK_PUBLISHED,
                 'fl_system': fl_system, 'task_id': task_config['id']}
        redis_cli.broadcast(MESSAGE_QUEUE_NAME_AGENT, task_config['publisher_name'], event)


def contribute_weights(fl_system, weights_config, broadcast_it=True):
    """
    upload weights to network
    """

    weights_table = get_weights_table(fl_system)

    start_time = current_timestamp()
    access_path = upload_weights(
        weights_config['weights_id'], weights_config['pickled_weights'])
    if not access_path:
        return

    weights_config['used_time']['weights_upload'] = current_timestamp() - start_time

    source_weights_ids = '''{}'''.format(weights_config['source_weights_ids'])
    performance = '''{}'''.format(weights_config['performance']) # NOTE: Object of type float32 is not JSON serializable
    used_time = '''{}'''.format(weights_config['used_time'])
    extra = '''{}'''.format(weights_config['extra'])

    weights_info = {'id': weights_config['weights_id'], 'hash': weights_config['weights_hash'], 'task_id': weights_config['task_id'], '_type': weights_config['_type'],
                    'is_aggregated': weights_config['is_aggregated'], 'is_trained': weights_config['is_trained'],
                    'source_weights_ids': source_weights_ids, 'contributor': weights_config['contributor'], 'contributor_mode': weights_config['contributor_mode'],
                    'performance': performance, 'storage_system': STORAGE_FASTDFS,
                    'access_path': access_path, 'used_time': used_time, 'extra': extra}

    insert_database(weights_table, weights_info, ignore_exist=True)

    if broadcast_it:
        # broadcast 'local weights uploaded' event
        event = EVENT_LOCAL_WEIGHTS_UPLOADED
        if weights_config['_type'] == WEIGHTS_TYPE_GLOBAL:
            event = EVENT_GLOBAL_WEIGHTS_UPLOADED

        event = {'event': event, 'fl_system': fl_system, 'access_path': access_path,
                 'task_id': weights_config['task_id'], 'weights_id': weights_config['weights_id']}
        redis_cli.broadcast(MESSAGE_QUEUE_NAME_AGENT, weights_config['contributor'], event)


def publish_task(task_settings):
    # task_settings['task_id'] = int(task_settings['task_tag'].replace('exp-', '').replace('.', ''))

    fl_system = task_settings['fl_system']

    weights_id, weights_hash, pickled_weights = task_settings['weights_info']

    # 初始weights都相同，为避免主键冲突，加入task_id
    weights_id = '{}_{}'.format(weights_id, task_settings['task_id'])

    source_weights_ids = '''{}'''.format([])

    publisher_name = 'publisher'

    used_time = {'weights_prepare': 0, 'model_train': 0}
    weights_config = {'weights_id': weights_id, 'weights_hash': weights_hash, 'pickled_weights': pickled_weights, 'source_weights_ids': source_weights_ids,
                      'contributor': publisher_name, 'contributor_mode': RUNNER_MODE_NORMAL, 'task_id': task_settings['task_id'], 'performance': {'loss': 0, 'accuracy': 0},
                      'used_time': used_time, 'extra': '', '_type': WEIGHTS_TYPE_GLOBAL, 'is_aggregated': 0, 'is_trained': 0}

    # 不要broadcast，统一由coordinator管理任务状态
    contribute_weights(fl_system, weights_config, False)

    # upload task and then broadcast the event
    evalset_id = generate_dataset_id(
        task_settings['dataset_source'], '', '', 'evalset', 0, 0)
    if 'extra' not in task_settings:
        task_settings['extra'] = {}

    task_extra = '''{}'''.format(task_settings['extra'])

    task_config = {'id': task_settings['task_id'], 'publisher_name': publisher_name,
                   'model_name': task_settings['model_name'], 'dataset_source': task_settings['dataset_source'],
                   'dataset_sharding_schema': task_settings['dataset_sharding_schema'], 'evalset_id': evalset_id,
                   'init_weights_id': weights_id, 'status': TASK_STATUS_STOPPED, 'max_iteration': task_settings['max_iteration'], 'extra': task_extra}

    _publish_task(fl_system, task_config, False)


def make_abnormal_settings(task_settings, abnormal_type, worker_num, abnormal_worker_num, abnormal_params):
    worker_ids = [i for i in range(worker_num)]
    abnormal_worker_ids = random.sample(worker_ids, abnormal_worker_num)

    if abnormal_type == RUNNER_MODE_NORMAL:
        task_settings['worker_mode_list'] = [
            RUNNER_MODE_NORMAL for _ in range(worker_num)]
        task_settings['backdoor_config_list'] = [
            NO_BACKDOOR_PARAMS for _ in range(worker_num)]
        task_settings['dishonest_config_list'] = [
            NO_DISHONEST_PARAMS for _ in range(worker_num)]
        task_settings['noise_config_list'] = [
            NO_NOISE_PARAMS for _ in range(worker_num)]
        task_settings['poison_config_list'] = [
            NO_POISON_PARAMS for _ in range(worker_num)]

        return

    task_settings['worker_mode_list'] = []

    if abnormal_type == RUNNER_MODE_BACKDOOR:
        task_settings['backdoor_config_list'] = []
        task_settings['dishonest_config_list'] = [
            NO_DISHONEST_PARAMS for _ in range(worker_num)]
        task_settings['noise_config_list'] = [
            NO_NOISE_PARAMS for _ in range(worker_num)]
        task_settings['poison_config_list'] = [
            NO_POISON_PARAMS for _ in range(worker_num)]

    if abnormal_type == RUNNER_MODE_DISHONEST:
        task_settings['backdoor_config_list'] = [
            NO_BACKDOOR_PARAMS for _ in range(worker_num)]
        task_settings['dishonest_config_list'] = []
        task_settings['noise_config_list'] = [
            NO_NOISE_PARAMS for _ in range(worker_num)]
        task_settings['poison_config_list'] = [
            NO_POISON_PARAMS for _ in range(worker_num)]

    if abnormal_type == RUNNER_MODE_NOISE:
        task_settings['backdoor_config_list'] = [
            NO_BACKDOOR_PARAMS for _ in range(worker_num)]
        task_settings['dishonest_config_list'] = [
            NO_DISHONEST_PARAMS for _ in range(worker_num)]
        task_settings['noise_config_list'] = []
        task_settings['poison_config_list'] = [
            NO_POISON_PARAMS for _ in range(worker_num)]

    if abnormal_type == RUNNER_MODE_POISON:
        task_settings['backdoor_config_list'] = [
            NO_BACKDOOR_PARAMS for _ in range(worker_num)]
        task_settings['dishonest_config_list'] = [
            NO_DISHONEST_PARAMS for _ in range(worker_num)]
        task_settings['noise_config_list'] = [
            NO_NOISE_PARAMS for _ in range(worker_num)]
        task_settings['poison_config_list'] = []

    for wi in worker_ids:
        if abnormal_type == RUNNER_MODE_BACKDOOR:
            if wi not in abnormal_worker_ids:
                task_settings['worker_mode_list'].append(RUNNER_MODE_NORMAL)
                task_settings['backdoor_config_list'].append(
                    NO_BACKDOOR_PARAMS)
            else:
                task_settings['worker_mode_list'].append(RUNNER_MODE_BACKDOOR)
                task_settings['backdoor_config_list'].append(abnormal_params)

        if abnormal_type == RUNNER_MODE_DISHONEST:
            if wi not in abnormal_worker_ids:
                task_settings['worker_mode_list'].append(RUNNER_MODE_NORMAL)
                task_settings['dishonest_config_list'].append(
                    NO_DISHONEST_PARAMS)
            else:
                task_settings['worker_mode_list'].append(RUNNER_MODE_DISHONEST)
                task_settings['dishonest_config_list'].append(abnormal_params)

        if abnormal_type == RUNNER_MODE_NOISE:
            if wi not in abnormal_worker_ids:
                task_settings['worker_mode_list'].append(RUNNER_MODE_NORMAL)
                task_settings['noise_config_list'].append(NO_NOISE_PARAMS)
            else:
                task_settings['worker_mode_list'].append(RUNNER_MODE_NOISE)
                task_settings['noise_config_list'].append(abnormal_params)

        if abnormal_type == RUNNER_MODE_POISON:
            if wi not in abnormal_worker_ids:
                task_settings['worker_mode_list'].append(RUNNER_MODE_NORMAL)
                task_settings['poison_config_list'].append(NO_POISON_PARAMS)
            else:
                task_settings['worker_mode_list'].append(RUNNER_MODE_POISON)
                task_settings['poison_config_list'].append(abnormal_params)


def update_weights_aggregated(weights_table, weights_id_list):
    sql = 'update {} set is_aggregated=1 where id in ({})'
    sql = sql.format(weights_table, ','.join(
        ['"{}"'.format(wi) for wi in weights_id_list]))

    execute_update_sql(sql)


def query_runner_node_type(runner_name):
    rinfo = query_database(
        TABLE_RUNNERS, {'conditions': {'name': runner_name}})[0]

    return rinfo['node_type']


def query_runner_node_settings(runner_name):
    rinfo = query_database(
        TABLE_RUNNERS, {'conditions': {'name': runner_name}})[0]

    return json.loads(rinfo['node_settings'])


def upload_runtime_errors(runner_name, fl_system, src_info, err_msg):

    # src_info可能是str，也可能是json
    task_info = '''{}'''.format(src_info)

    msg_params = {'runner_name': runner_name,
                  'fl_system': fl_system, 'task_info': task_info, 'message': err_msg}
    insert_database(TABLE_DIAGNOSE_RUNNER_RUNTIME_ERRORS, msg_params)


def add_task_scheduling_history(fl_system, task_id, event):

    hist = dict()

    hist['fl_system'] = fl_system
    hist['task_id'] = task_id
    hist['event'] = event

    insert_database(TABLE_DIAGNOSE_TASK_SCHEDULING_HISTORY, hist)


def register_task_progress(df_tasks):

    for idx, task in df_tasks.iterrows():
        record = dict()

        params = {'conditions': {'fl_system': task['fl_system'], 'task_id': task['id']}, 'limit': 1}
        prog_info = query_database(TABLE_DIAGNOSE_WHOLE_TASKS_PROGRESS, params)

        if len(prog_info) > 0:
            params = {'conditions': {'fl_system': task['fl_system'], 'task_id': task['id']}, 'updates': {'task_status': task['status']}}
            update_database(TABLE_DIAGNOSE_WHOLE_TASKS_PROGRESS, params)

        else:
            record['fl_system'] = task['fl_system']
            record['task_id'] = task['id']
            record['completed_iteration'] = 0
            record['max_iteration'] = task['max_iteration']
            record['task_status'] = task['status']
            record['schedule_priority'] = task['priority']
            record['schedule_max_concurrent'] = task['max_concurrent']

            insert_database(TABLE_DIAGNOSE_WHOLE_TASKS_PROGRESS, record, ignore_exist=True)


def update_task_progress(fl_system, task_id, task_status, trained_weights_list):
    completed_iteration = len(trained_weights_list)

    if completed_iteration < 2:
        params = {'updates': {'completed_iteration': completed_iteration, 'update_time': current_strftime(), 'task_status': task_status}, 
              'conditions': {'fl_system': fl_system, 'task_id': task_id}}

    else:
        weights_created_time_list = [datetime_to_timestamp(record['create_time']) for record in trained_weights_list]
        task_start_time = timestamp_to_strftime(min(weights_created_time_list))
        latest_update_time = timestamp_to_strftime(max(weights_created_time_list))

        params = {'updates': {'completed_iteration': completed_iteration, 'task_start_time': task_start_time, 
                              'latest_update_time': latest_update_time, 'update_time': current_strftime(), 'task_status': task_status}, 
                              'conditions': {'fl_system': fl_system, 'task_id': task_id}}

    update_database(TABLE_DIAGNOSE_WHOLE_TASKS_PROGRESS, params)


def update_runner_active_info(runner_name):
    key = '{}_activation'.format(runner_name)
    val = json.dumps({'activate_time': current_strftime(), 'flsim_version': FLSIM_VERION})

    redis_cli.set_cached_value(key, val)


def add_runner_executation_history(hist):
    if 'complete_time' not in hist:
        hist['complete_time'] = current_strftime()

    key = '{}_exec_hist'.format(hist['runner_name'])
    val = json.dumps({'fl_system': hist['fl_system'], 'task_id': hist['task_id'], 
                      'start_time': hist['start_time'], 'complete_time': hist['complete_time'], 'status': hist['status']})

    redis_cli.set_cached_value(key, val)

    # insert_database(TABLE_DIAGNOSE_RUNNER_EXECUTATION_HISTORY, hist)
