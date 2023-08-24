import json
import pandas as pd

from flexpkit.basic_utils import *
from flexpkit.exp_constants import *
from flexpkit.exp_settings import *
from flexpkit.exp_utils import *
from flexpkit.mysql_utils import *
from flexpkit.redis_utils import *

fl_system_list = (FL_SYSTEM_BLOCKFL, FL_SYSTEM_DAGFL, FL_SYSTEM_FEDASYNC, FL_SYSTEM_FEDAVG, FL_SYSTEM_IRONFORGE)


def query_all_tasks():
    df_task_list = []

    for fl_system in fl_system_list:
        task_table = get_task_table(fl_system)

        task_list = query_database(task_table, {})
        df_tasks = pd.DataFrame(task_list)
        df_tasks['fl_system'] = fl_system

        df_task_list.append(df_tasks)
    
    df_all_tasks = pd.concat(df_task_list).reset_index(drop=True)

    df_all_tasks['priority'] = 16
    df_all_tasks['max_concurrent'] = MAX_CONCURRENT_SCHEDULING_TASK_COUNT

    return df_all_tasks

    
def rectify_master_binding():
    params = {'conditions': {'_type': RUNNER_TYPE_MASTER}}
    master_info_list = query_database(TABLE_RUNNERS, params)

    for mi in master_info_list:
        # 如果未binding，不需调整
        if not mi['extra']:
            continue

        extra = json.loads(mi['extra'])

        task_table = get_task_table(extra['binded_fl_system'])
        params = {'conditions': {'id': extra['binded_task_id']}}
        task_info = query_database(task_table, params)
        if len(task_info) != 0 and task_info[0]['status'] == TASK_STATUS_RUNNING:
            continue

        print_log('rectify master {}'.format(mi['name']))

        # 没有对应的task，或者task为ready 或 terminated状态，但master仍被bind，需要重置
        params = {'updates': {'extra': ''}, 'conditions': {'name': mi['name']}}
        update_database(TABLE_RUNNERS, params)


def bind_task_master(fl_system, task_id):
    params = {'conditions': {'_type': RUNNER_TYPE_MASTER}}
    master_info_list = query_database(TABLE_RUNNERS, params)

    valid_master_info_list = [mi for mi in master_info_list if not mi['extra']]
    if len(valid_master_info_list) == 0:
        return False
    
    selected_master = valid_master_info_list[0]
    extra = {'binded_fl_system': fl_system, 'binded_task_id': task_id, 'binded_time': current_strftime()}
    extra = '''{}'''.format(extra)

    params = {'updates': {'extra': extra}, 'conditions': {'name': selected_master['name']}}
    update_database(TABLE_RUNNERS, params)

    return True


def unbind_task_master(fl_system, task_id):
    params = {'conditions': {'_type': RUNNER_TYPE_MASTER}}
    master_info_list = query_database(TABLE_RUNNERS, params)
    
    for mi in master_info_list:
        if not mi['extra']:
            continue 

        extra = json.loads(mi['extra'])
        if extra['binded_fl_system'] == fl_system and extra['binded_task_id'] == task_id:
            params = {'updates': {'extra': ''}, 'conditions': {'name': mi['name']}}
            update_database(TABLE_RUNNERS, params)

            return True

    return False


def schedule_task(fl_system, task_id):
    task_table = get_task_table(fl_system)

    if fl_system in (FL_SYSTEM_FEDASYNC, FL_SYSTEM_FEDAVG):
        is_binded = bind_task_master(fl_system, task_id)
        if not is_binded:
            return False

    print_log('schedule task {}: {}'.format(task_table, task_id))

    params = {'conditions': {'task_id': task_id}, 'limit': -1}
    rtset_info_list = query_database(TABLE_RUNNER_TASK_SETTINGS, params)
    rtset_info_list = [ri for ri in rtset_info_list if 'worker' in ri['runner_name']]

    worker_names = [ts['runner_name'] for ts in rtset_info_list]

    sql = 'update {} set binded_task_id="{}" where name in ({})'
    if MAX_CONCURRENT_SCHEDULING_TASK_COUNT > 1:
        sql = sql.format(TABLE_RUNNERS, FLAG_ALL_TASKS_ALLOWED, ','.join(['"{}"'.format(wn) for wn in worker_names]))
    else:
        sql = sql.format(TABLE_RUNNERS, task_id, ','.join(['"{}"'.format(wn) for wn in worker_names]))

    execute_update_sql(sql)

    params = {'updates': {'status': TASK_STATUS_RUNNING, 'scheduled_time': current_strftime()}, 'conditions': {'id': task_id}}
    update_database(task_table, params)

    # broadcast the event

    event = {'event': EVENT_TASK_PUBLISHED, 'fl_system': fl_system, 'task_id': task_id}
    redis_cli.broadcast(MESSAGE_QUEUE_NAME_AGENT, 'coordinator', event)

    add_task_scheduling_history(fl_system, task_id, 'schedule')

    return True


def reset_task(fl_system, task_id):
    task_table = get_task_table(fl_system)
    print_log('reset task {}: {}'.format(task_table, task_id))

    params = {'updates': {'status': TASK_STATUS_READY}, 'conditions': {'id': task_id}}
    update_database(task_table, params)

    if fl_system in (FL_SYSTEM_FEDASYNC, FL_SYSTEM_FEDAVG):
        unbind_task_master(fl_system, task_id)

    add_task_scheduling_history(fl_system, task_id, 'reset')


def terminate_task(fl_system, task_id):
    task_table = get_task_table(fl_system)
    print_log('terminate task {}: {}'.format(task_table, task_id))

    params = {'updates': {'status': TASK_STATUS_DONE}, 'conditions': {'id': task_id}}
    update_database(task_table, params)

    event = {'event': EVENT_TASK_DONE, 'fl_system': fl_system, 'task_id': task_id}
    redis_cli.broadcast(MESSAGE_QUEUE_NAME_AGENT, 'coordinator', event)

    if fl_system in (FL_SYSTEM_FEDASYNC, FL_SYSTEM_FEDAVG):
        unbind_task_master(fl_system, task_id)

    add_task_scheduling_history(fl_system, task_id, 'terminate')


def schedule_tasks(df_all_tasks):
    print_log('schedule_tasks')

    if df_all_tasks.shape[0] == 0:
        return

    df_all_tasks = df_all_tasks[df_all_tasks['dataset_source'].isin([DATASET_MNIST, DATASET_CIFAR10])]
    df_done_tasks = df_all_tasks[df_all_tasks['status']==TASK_STATUS_DONE]

    suspend_scheduling = False

    # 还在备份数据，暂缓task scheduling
    if len(df_done_tasks) > 2:
        print_log('suspend scheduling for backup')
        suspend_scheduling = True

    df_runnable_tasks = df_all_tasks[df_all_tasks['status'].isin([TASK_STATUS_READY, TASK_STATUS_RUNNING])]
    if df_runnable_tasks.shape[0] == 0:
        return

    df_runnable_tasks = df_runnable_tasks.sort_values(['priority'], ascending=False)
    priority = df_runnable_tasks.iloc[0]['priority']
    max_concurrent = df_runnable_tasks.iloc[0]['max_concurrent']

    df_running_tasks = df_runnable_tasks[df_runnable_tasks['status']==TASK_STATUS_RUNNING]
    running_task_num = df_running_tasks.shape[0]

    # 如果不同priority的task在同时运行，reset所有task
    if len(df_running_tasks['priority'].unique()) > 1:
        max_concurrent = 0

    # 查询所有tasks，重置额外的task，并且退出调度
    has_reset = False
    for _, task_info in df_running_tasks.iloc[max_concurrent:].iterrows():
        has_reset = True
        reset_task(task_info['fl_system'], task_info['id'])

    if has_reset:
        return

    df_runnable_tasks = df_runnable_tasks.sample(frac=1)

    for _, task_info in df_runnable_tasks.iterrows():
    # for fl_system, task_info_list in df_runnable_tasks.groupby('fl_system'):
        # task_info = task_info_list.iloc[0]

        fl_system = task_info['fl_system']

        weights_table = get_weights_table(fl_system)

        params = {'columns': ['create_time', ], 'conditions': {'task_id': task_info['id'], 'is_trained': 1}}
        trained_weights_list = query_database(weights_table, params)

        # trained_weights_list = [w for w in weights_list if w['is_trained']==1]
        # aggregated_weights_list = [w for w in weights_list if w['is_aggregated']==1]

        # 更新task进度
        update_task_progress(fl_system, task_info['id'], task_info['status'], trained_weights_list)

        # 完成后设置状态为terminated
        # 或者 len(aggregated_weights_list) > task_map[task_id]['max_iteration']
        if len(trained_weights_list) > task_info['max_iteration'] and task_info['status'] not in [TASK_STATUS_STOPPED, TASK_STATUS_DONE]: 
            terminate_task(fl_system, task_info['id'])
            continue

            # 不需要减，因为存在以下情况：某个任务刚好schedule，另一个刚好terminated，那么running_task_count=0，这样显然不对
            # running_task_count -= 1 

        # 如果超时，则重置任务
        if task_info['status'] == TASK_STATUS_RUNNING:
            params = {'conditions': {'task_id': task_info['id']}, 'order': {'key': 'create_time', 'value': 'desc'}, 'limit': 1}
            weights_list = query_database(weights_table, params)

            cur_time = current_timestamp()
            last_update_time = datetime_to_timestamp(weights_list[0]['create_time'])

            # 只有running状态的task才有scheduled time
            task_scheduled_time = pandas_Timestamp_to_int(task_info['scheduled_time'])

            # 时区异常
            if cur_time < last_update_time:
                upload_runtime_errors('evaluator', task_info['id'], task_info['scheduled_time'].strftime('%Y-%m-%d %H:%M:%S'), 'invalid timezone')

            # 超过1分钟没有新weights出现，且距离上一次schedule超过1分钟，则reset
            if cur_time - last_update_time > 60 * 2 and cur_time - task_scheduled_time > 60 * 2: 
                reset_task(fl_system, task_info['id'])
                continue

        # 只选取priority相同的tasks进行调度
        if task_info['status'] == TASK_STATUS_READY and task_info['priority'] == priority and running_task_num < max_concurrent and not suspend_scheduling:
            is_scheduled = schedule_task(fl_system, task_info['id'])

            if is_scheduled:
                running_task_num += 1

            else:
                # 如果无法调度，可能是资源不够（master用尽），则继续下一个任务的调度
                continue


def update_runners_info():

    if random.randint(0, 10) >= 5:
        return

    print_log('update runners info')

    runner_list = query_database(TABLE_RUNNERS, params={})

    for runner in runner_list:
        
        runner_name = runner['name']

        params = {'conditions': {'name': runner_name}, 'updates': {}}

        key_act = '{}_activation'.format(runner_name)
        if redis_cli.check_cache_exists(key_act):
            val_act = json.loads(redis_cli.get_cached_value(key_act))
            params['updates'].update({'flsim_version': val_act['flsim_version'], 'activate_time': val_act['activate_time']})

        key_exe = '{}_exec_hist'.format(runner_name)
        if redis_cli.check_cache_exists(key_exe):
            val_exe = json.loads(redis_cli.get_cached_value(key_exe))
            params['updates'].update({'running_task_info': val_exe})

        if len(params['updates']) != 0:
            update_database(TABLE_RUNNERS, params)
        
        time.sleep(0.01)