import gc
import os

from flexpkit.basic_utils import (current_strftime, get_parent_dir,
                                  make_dir_recursively, remake_dir
                                  )
from flexpkit.exp_constants import (LOCAL_PERSISTENT_STORAGE_PATH,
                                    LOCAL_VOLATILE_STORAGE_PATH,
                                    STORAGE_FASTDFS)
from flexpkit.exp_settings import underlying_storage_system
from flexpkit.fastdfs_utils import fastdfs_cli

uploaded_file_cache = {}


def clean_storage_cache(clear_pers=False, clear_vol=True):
    if clear_pers:
        remake_dir(LOCAL_PERSISTENT_STORAGE_PATH)
    
    if clear_vol:
        remake_dir(LOCAL_VOLATILE_STORAGE_PATH)


def generate_local_storage_temp_path(key, suffix):
    return '{}/{}_{}'.format(LOCAL_VOLATILE_STORAGE_PATH, key, suffix)
    # return '{}/{}'.format(LOCAL_VOLATILE_STORAGE_PATH, key)


def generate_local_persistent_storage_path(key, suffix):
    return '{}/{}_{}'.format(LOCAL_PERSISTENT_STORAGE_PATH, key, suffix)
    # return '{}/{}'.format(LOCAL_PERSISTENT_STORAGE_PATH, key)


def upload_to_storage(key, content):
    print('{} uploading {}'.format(current_strftime(), key))

    content_sha1 = key.split('_')[0]
    if content_sha1 in uploaded_file_cache:
        return uploaded_file_cache[content_sha1]

    access_path = ''
    if underlying_storage_system == STORAGE_FASTDFS:
        access_path = fastdfs_cli.upload_bytes_with_bandwidth_limit(key, content)

    uploaded_file_cache[content_sha1] = access_path

    del content
    gc.collect()

    return access_path


def download_from_storage(storage_system, access_path, fp_out, enable_cache=True):
    print('{} downloading {}'.format(current_strftime(), fp_out))

    if enable_cache and os.path.exists(fp_out):
        return

    par_dir = get_parent_dir(fp_out)
    if not os.path.exists(par_dir):
        make_dir_recursively(par_dir)

    # 重复3次，以免网络抖动造成异常
    if storage_system == STORAGE_FASTDFS:
        fastdfs_cli.download_with_bandwidth_limit(access_path, fp_out)