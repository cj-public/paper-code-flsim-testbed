import json
import pandas as pd
import time
import traceback

from flexpkit.scheduler_util import *


def set_task_scheduling_params(df_all_tasks):
    
    for idx, task_info in df_all_tasks.iterrows():
        if task_info['id'].startswith('exp-5.'):
            df_all_tasks.loc[idx, 'priority'] = 21
            df_all_tasks.loc[idx, 'max_concurrent'] = 2

        if task_info['id'].startswith('exp-2.'):
            df_all_tasks.loc[idx, 'priority'] = 20
            df_all_tasks.loc[idx, 'max_concurrent'] = 1

        if task_info['id'].startswith('exp-6.'):
            df_all_tasks.loc[idx, 'priority'] = 10
            df_all_tasks.loc[idx, 'max_concurrent'] = 0

        if task_info['id'].startswith('exp-6.1'):
            df_all_tasks.loc[idx, 'priority'] = 12
            df_all_tasks.loc[idx, 'max_concurrent'] = 1

    return df_all_tasks


def main():
    while True:
        try:
            rectify_master_binding()

            df_all_tasks = query_all_tasks()
            
            set_task_scheduling_params(df_all_tasks)

            register_task_progress(df_all_tasks)

            schedule_tasks(df_all_tasks)

            time.sleep(5)
        except Exception as e:
            traceback.print_exc()

            time.sleep(10)


if __name__ == '__main__':
    """
     PYTHONPATH='./src' python scheduler.py 
    """
    main()