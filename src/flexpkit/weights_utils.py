import os
import pickle
import random
import uuid
import numpy as np

from flexpkit.basic_utils import (generate_bytes_sha1, get_parent_dir)
from flexpkit.storage_utils import (clean_storage_cache, download_from_storage,
                                    generate_local_storage_temp_path,
                                    upload_to_storage)


def pickle_model_weights(weights):
    pickled_weights = pickle.dumps(weights)
    weights_hash = generate_bytes_sha1(pickled_weights)

    id_suffix = str(uuid.uuid4())[:8]
    weights_id = '{}_{}'.format(weights_hash, id_suffix)

    return weights_id, weights_hash, pickled_weights


def unpickle_model_weights(pickled_weights):
    return pickle.loads(pickled_weights)


def upload_weights(weights_id, pickled_weights):
    return upload_to_storage(weights_id, pickled_weights)


def download_weights(weights_info, cache_enabled):
    # 不要加以下代码
    # network_delay = random.randint(0, MAX_NETWORK_DELAY)
    # time.sleep(network_delay)

    weights_id, storage_system, access_path = weights_info['id'], weights_info['storage_system'], weights_info['access_path']

    fp_out = generate_local_storage_temp_path(weights_id, weights_info['contributor'])

    download_from_storage(storage_system, access_path, fp_out, cache_enabled)

    # 事实上如果下载文件为None，则抛出异常，因此以下代码不会执行
    if not os.path.exists(fp_out):
        return None

    unpickled_weights = pickle.load(open(fp_out, 'rb'))

    par_dir = get_parent_dir(fp_out)
    fns = os.listdir(par_dir)
    if len(fns) > 3000:
        clean_storage_cache()

    return unpickled_weights


def batch_download_weights(weights_info_list, weights_cache_enabled):
    print('retrieve remote weights')

    # 避免多个worker同时下载同一个weights
    random.shuffle(weights_info_list)

    # download weights from storage system
    unpickled_weights_map = dict()
    for wi in weights_info_list:
        weights_id = wi['id']
        weights = download_weights(wi, weights_cache_enabled)
        if weights is None:
            continue

        unpickled_weights_map[weights_id] = weights

    return unpickled_weights_map


def scale_weights(weights, scalar):
    """
    function for scaling a models weights
    """
    weight_final = []
    steps = len(weights)
    for i in range(steps):
        weight_final.append(scalar * weights[i])

    return weight_final


def sum_weights(scaled_weight_list):
    """
    Return the sum of the listed scaled weights. The is equivalent to scaled avg of the weights
    """
   
    return np.sum(scaled_weight_list, axis=0, dtype=object)


def aggregate_weights(weights_map, weighting_factors=None):
    """
    aggregate weights with specified manner
    """

    if len(weights_map) == 0:
        return None

    if not weighting_factors:
        weighting_factors = dict()
        for key in weights_map:
            weighting_factors[key] = 1.0 / len(weights_map)

    scaled_weights_list = [scale_weights(weights_map[key], weighting_factors[key]) for key in weights_map]

    return sum_weights(scaled_weights_list)

