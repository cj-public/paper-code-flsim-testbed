import base64
import datetime
import gzip
import json
import hashlib
import math
import os
import pytz
import random
import subprocess


TIMEZONE = pytz.timezone('Asia/Shanghai')  


def get_file_size(fp):
    if not os.path.exists(fp):
        return 0

    st = os.stat(fp)
    return st.st_size


def sort_dict_by_value(x, reverse=True):
    return {k: v for k, v in sorted(x.items(), key=lambda item: item[1], reverse=reverse)}


def run_shell(cmd):
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True) as proc:
        try:
            stdout, stderr = proc.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
        
        if proc.returncode != 0:
            print('Command execution failed with error:', stderr)
        
        return stdout, stderr


def pandas_Timestamp_to_int(pd_ts):
    return datetime.datetime.timestamp(pd_ts)


def datetime_to_timestamp(dateobj):
    return datetime.datetime.timestamp(dateobj)


def timestamp_to_datetime(timestamp):
    dtime = datetime.datetime.fromtimestamp(timestamp)
    return dtime.astimezone(TIMEZONE)


def datetime_to_strftime(dateobj):
    return dateobj.strftime('%Y-%m-%d %H:%M:%S')


def timestamp_to_strftime(timestamp):
    return datetime_to_strftime(timestamp_to_datetime(timestamp))


def strftime_to_timestamp(strftime):
    datetime_obj = datetime.datetime.strptime(strftime, "%Y-%m-%d %H:%M:%S")
    datetime_obj = TIMEZONE.localize(datetime_obj)
    # datetime_obj = datetime_obj.astimezone(TIMEZONE) # 不要使用该语句，会认为当前时间的时区是UTC，转成BJ时间时+8h

    return datetime_to_timestamp(datetime_obj)


def current_timestamp():
    current_time = datetime.datetime.now(TIMEZONE)
    return current_time.timestamp()


def current_strftime():
    now = datetime.datetime.now(TIMEZONE)
    return now.strftime("%Y-%m-%d %H:%M:%S")


def split_elements(elements, n_splits):
    """
    如果elements个数不能被n_splits整除的话，最后几个splits可能为空
    """
    splits = []

    ele_size = len(elements)
    step_size = math.ceil(ele_size / n_splits)

    for i in range(n_splits):
        start = i * step_size
        end = (i + 1) * step_size

        splits.append(elements[start:end])

    return splits


def merge_lists(lists):
    if not lists or len(lists) == 0:
        return []

    result = []
    for l in lists:
        result.extend(l)

    return result


def compress_str(val):
    return gzip.compress(bytes(val, 'utf-8'))


def decompress_str(val):
    return gzip.decompress(val).decode('utf-8')


def encode_base64(val):
    # return str(base64.b64encode(val), 'utf-8')
    return base64.b64encode(val)


def decode_base64(val):
    return base64.b64decode(val)


def generate_str_sha1(val):
    return generate_bytes_sha1(val.encode('utf-8'))


def generate_bytes_sha1(val):
    return hashlib.sha1(val).hexdigest()


def read_file(fp, mode='r', encoding='utf-8', join_lines=False):
    if not os.path.exists(fp):
        return None

    if not fp.endswith('.gz'):
        if 'b' in mode:
            fh = open(fp, mode)
        else:
            fh = open(fp, mode, encoding=encoding)
    else:
        fh = gzip.open(fp, 'rt', encoding=encoding)

    lns = fh.readlines()
    fh.close()

    if join_lines:
        return ''.join([ln.decode('utf-8') for ln in lns])

    return lns


def get_parent_dir(file_path):
    if '/' not in file_path:
        return ''

    if file_path.endswith('/'):
        file_path = file_path[:-1]

    idx = file_path.strip().rindex('/')

    return file_path[:idx + 1]


def make_dir_recursively(path):
    run_shell('mkdir -p %s ' % path)


def remake_dir(path):
    if os.path.exists(path):
        run_shell('rm -rf {}'.format(path))

    make_dir_recursively(path)


def write_file(fp, data, mode='w', strip=True, new_line=True, make_dir=True):
    if type(data) != list:
        data = [data, ]

    dir_out = get_parent_dir(fp)
    if not os.path.exists(dir_out) and make_dir:
        make_dir_recursively(dir_out)

    lines = []
    for ln in data:
        if strip:
            ln = ln.strip()

        if new_line:
            ln = ln + '\n'

        lines.append(ln)

    if not fp.endswith('.gz'):
        fh = open(fp, mode)
    else:
        fh = gzip.open(fp, 'wt')

    fh.writelines(lines)
    fh.close()


def remove_file(path):
    if not os.path.exists(path):
        return False

    os.remove(path)

    return True


def random_select_with_weights(weighting_choices):
    total_size = sum(weighting_choices.values())
    new_weights = {
        k: int(100 * weighting_choices[k] / total_size) for k in weighting_choices}

    choices = []
    for choice in weighting_choices:
        weight = new_weights[choice]
        choices.extend([choice for i in range(weight)])

    return random.choice(choices)


def load_json(path, encoding='utf-8'):
    if path.endswith('.gz'):
        fh = gzip.open(path, 'rt', encoding=encoding)
    else:
        fh = open(path, 'r', encoding=encoding, errors='ignore')

    content = json.load(fh)
    fh.close()

    return content


def print_log(log_str):
    print('{} {}'.format(current_strftime(), log_str))


def format_call_stack(call_stack):
    stack_list = []
    for frame_info in call_stack:
        file_name = frame_info.filename
        if 'conda' in file_name:
            break

        line_no = frame_info.lineno
        func_name = frame_info.function

        exec_info = '{}({}, {})'.format(file_name, func_name, line_no)
        stack_list.append(exec_info)
    
    return '#'.join(stack_list)