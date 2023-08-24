import gc
import os
import json
import random
import time

import requests

from flexpkit.basic_utils import (current_timestamp, get_file_size, make_dir_recursively, 
                                  random_select_with_weights, remove_file,
                                  run_shell, timestamp_to_strftime)
from flexpkit.exp_constants import CHARSET, LOCAL_VOLATILE_STORAGE_PATH, TABLE_DIAGNOSE_SLOW_DFS_ANALYSIS
from flexpkit.exp_settings import (STORAGE_LOAD_BALANCE_ENABLED, fastdfs_node_urls)
from flexpkit.mysql_utils import insert_database


class FastDFSCli:
    fl_system = 'not assigned'
    runner_name = 'not assigned'

    bandwidth_limit = 10000  # 10MB/s

    node_urls = []

    node_weights = dict()

    def __init__(self, node_urls) -> None:
        self.node_urls = node_urls

        if STORAGE_LOAD_BALANCE_ENABLED:
            self.balance_load()

    def set_runner_info(self, fl_system, runner_name):
        self.fl_system = fl_system
        self.runner_name = runner_name

    def set_bandwidth_limit(self, limit):
        self.bandwidth_limit = limit

    def upload_bytes_with_bandwidth_limit(self, key, content, node_url=''):
        if not os.path.exists(LOCAL_VOLATILE_STORAGE_PATH):
            make_dir_recursively(LOCAL_VOLATILE_STORAGE_PATH)

        fp = '{}/{}'.format(LOCAL_VOLATILE_STORAGE_PATH, key)
        fh = open(fp, 'wb')
        fh.write(content)
        fh.close()

        result = self.upload_with_bandwidth_limit(fp, node_url)

        # 删除临时文件
        remove_file(fp)

        return result

    def upload_with_bandwidth_limit(self, file_path, node_url=''):
        if not node_url:
            if STORAGE_LOAD_BALANCE_ENABLED:
                node_url = random_select_with_weights(self.node_weights)
            else:
                node_url = random.choice(self.node_urls)

        cmd = 'curl -m 60 --limit-rate {}M -F "file=@{}" {}'
        cmd = cmd.format(self.bandwidth_limit, file_path, node_url)

        record = dict()
        record['fl_system'] = self.fl_system
        record['runner_name'] = self.runner_name
        record['_type'] = 'upload'
        record['node_url'] = node_url
        record['shell_cmd'] = cmd
        record['start_time'] = current_timestamp()

        result = run_shell(cmd)

        record['status'] = 'falied' if 'http://' not in result[0].decode(CHARSET) else 'success'
        record['std_resp'] = result[0]
        record['err_resp'] = result[1]
        record['complete_time'] = current_timestamp()

        add_dfs_record(record)

        if 'http://' not in result[0].decode(CHARSET):
            raise Exception('not valid access path {}, error message is {}'.format(result[0], result[1]))

        return result[0].decode(CHARSET)

    def download_with_bandwidth_limit(self, file_link, fp_out):
        # -m timeout 整个下载时间不超过timeout seconds，否则停止下载
        cmd = 'curl -m 120 --limit-rate {}M -o {} {}'
        cmd = cmd.format(self.bandwidth_limit, fp_out, file_link)

        record = dict()
        record['fl_system'] = self.fl_system
        record['runner_name'] = self.runner_name
        record['_type'] = 'download'
        record['node_url'] = file_link
        record['shell_cmd'] = cmd
        record['start_time'] = current_timestamp()

        result = run_shell(cmd)

        record['status'] = 'failed' if get_file_size(fp_out) == 0 else 'success'
        record['std_resp'] = result[0]
        record['err_resp'] = result[1]
        record['complete_time'] = current_timestamp()

        add_dfs_record(record)

        if get_file_size(fp_out) == 0:
            remove_file(fp_out)
            raise Exception('empty file downloaded {}, error message is {}'.format(file_link, result[1]))

    # 以下代码未被使用

    @staticmethod
    def _get_node_status(node_url):
        parts = node_url.split('/')
        node_status_url = '{}//{}/status'.format(parts[0], parts[2])
        resp = requests.get(node_status_url)

        return json.loads(resp.text)

    def balance_load(self):
        for node_url in self.node_urls:
            status = self._get_node_status(node_url)

            self.node_weights[node_url] = int(
                status['data']['Sys.DiskInfo']['free'] / 1024 / 1024)

            time.sleep(0.5)

    @staticmethod
    def _download(file_link, fp_out):
        cmd = 'wget "{}" -O {}'.format(file_link, fp_out)
        result = run_shell(cmd)

    def _upload(self, key, file_path):
        self._upload_bytes(key, open(file_path, 'rb'))

    def _upload_bytes(self, key, file_content, node_url=''):
        if not node_url:
            if STORAGE_LOAD_BALANCE_ENABLED:
                if random.random() < 0.1:
                    self.balance_load()

                node_url = random_select_with_weights(self.node_weights)
            else:
                node_url = random.choice(self.node_urls)

        files = {'file': file_content}
        options = {'filename': key, 'output': 'json', 'path': '', 'scene': ''}

        resp = requests.post(node_url, data=options, files=files)

        return json.loads(resp.text)


def add_dfs_record(record):
    # 如果时间少于4s，不做记录
    if record['complete_time'] - record['start_time'] < 4:
        return

    record['shell_cmd'] = record['shell_cmd']
    record['std_resp'] = record['std_resp'].decode(CHARSET)
    record['err_resp'] = record['err_resp'].decode(CHARSET)
    record['used_time'] = record['complete_time'] - record['start_time']
    record['start_time'] = timestamp_to_strftime(record['start_time'])
    record['complete_time'] = timestamp_to_strftime(record['complete_time'])

    insert_database(TABLE_DIAGNOSE_SLOW_DFS_ANALYSIS, record, ignore_sql_analysis=True)


fastdfs_cli = FastDFSCli(fastdfs_node_urls)
