from flexpkit.basic_utils import *
from flexpkit.exp_constants import *
from flexpkit.mysql_utils import *
from flexpkit.redis_utils import *
from flexpkit.weights_utils import *


def evaluate_new_weights(candidate_weights_info_list, model, dataset, task_id, dataset_id, worker_name, weights_cache_enabled, evalset_size=200):
    print('{} evaluate new local weights'.format(current_strftime()))

    X, y = dataset
    X_eval = X[:evalset_size]
    y_eval = y[:evalset_size]

    new_weights_info_list = []
    for cwi in candidate_weights_info_list:
        key = generate_str_sha1('{}_{}'.format(cwi['id'], dataset_id))
        if check_evaluation_history_exist(key):
            continue

        new_weights_info_list.append(cwi)

    for wi in new_weights_info_list:
        used_time = dict()

        weights_id = wi['id']

        start_time = current_timestamp()
        new_weights = download_weights(wi, weights_cache_enabled)
        used_time['weights_download'] = current_timestamp() - start_time

        print('{} evaluate {}, {}'.format(current_strftime(), weights_id, dataset_id))

        key = '{}-{}'.format(weights_id, dataset_id)
        if not redis_cli.set_lock(key, current_timestamp(), 20):
            print('{} is locked'.format(weights_id))
            continue

        start_time = current_timestamp()

        model.set_weights(new_weights)
        loss, acc = model.evaluate(X_eval, y_eval, batch_size=256)

        used_time['model_evaluation'] = current_timestamp() - start_time

        used_time = '''{}'''.format(used_time)

        wtinfo = {'id': key, 'task_id': task_id, 'weights_id': weights_id, 'dataset_id': dataset_id, 'worker_name': worker_name, 'accuracy': acc, 'loss': loss, 'used_time': used_time, 'is_aggregated': 0}
        insert_database(TABLE_DAGFL_WEIGHTS_LOCAL_EVALUATION, wtinfo, ignore_exist=True)


def check_evaluation_history_exist(eva_id):
    params = {'conditions': {'id': eva_id}}
    result = query_database(TABLE_DAGFL_WEIGHTS_LOCAL_EVALUATION, params)

    return False if len(result) == 0 else True


def check_weights_aggregated(weights_id, dataset_id):
    params = {'conditions': {'weights_id': weights_id, 'dataset_id': dataset_id, 'is_aggregated': 1}}
    result = query_database(TABLE_DAGFL_WEIGHTS_LOCAL_EVALUATION, params)

    return False if len(result) == 0 else True


def select_preferred_weights_info_list_from_evaluation_history(task_id, dataset_id, top_n=5):
    # params = {'conditions': {'task_id': task_id, 'dataset_id': dataset_id, 'is_aggregated': 0}, 'order': {'key': 'loss', 'value': 'asc'}, 'limit': top_n}
    params = {'conditions': {'task_id': task_id, 'dataset_id': dataset_id, 'is_aggregated': 0}, 'order': {'key': 'accuracy', 'value': 'desc'}, 'limit': top_n}
    result = query_database(TABLE_DAGFL_WEIGHTS_LOCAL_EVALUATION, params)

    preferred_weights_id_list = [wi['weights_id'] for wi in result]
    print('selected preferred weights {}'.format(preferred_weights_id_list))

    preferred_weights_info_list = []
    for pwi in preferred_weights_id_list:
        params = {'conditions': {'id': pwi}}
        wtinfo_list = query_database(TABLE_DAGFL_WEIGHTS_POOL, params)

        if len(wtinfo_list) == 0:
            continue

        preferred_weights_info_list.append(wtinfo_list[0])

    return preferred_weights_info_list


def update_weights_local_evaluation_aggregated(weights_id, dataset_id):
    params = {'updates': {'is_aggregated': 1}, 'conditions': {'id': '{}-{}'.format(weights_id, dataset_id)}}
    update_database(TABLE_DAGFL_WEIGHTS_LOCAL_EVALUATION, params)