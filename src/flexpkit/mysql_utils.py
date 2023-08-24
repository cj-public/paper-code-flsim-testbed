import json
import time
import datetime
import inspect

from mysql import connector

from flexpkit.basic_utils import TIMEZONE, current_timestamp, timestamp_to_strftime
from flexpkit.exp_constants import (CHARSET, FL_SYSTEM_BLOCKFL, FL_SYSTEM_DAGFL, FL_SYSTEM_FEDASYNC,
                                    FL_SYSTEM_FEDAVG, FL_SYSTEM_IRONFORGE,
                                    TABLE_BLOCKFL_TASK_POOL,
                                    TABLE_BLOCKFL_WEIGHTS_GLOBAL_EVALUATION,
                                    TABLE_BLOCKFL_WEIGHTS_POOL, TABLE_DAGFL_TASK_POOL,
                                    TABLE_DAGFL_WEIGHTS_GLOBAL_EVALUATION, 
                                    TABLE_DAGFL_WEIGHTS_LOCAL_EVALUATION,
                                    TABLE_DAGFL_WEIGHTS_POOL, TABLE_DIAGNOSE_WRONG_SQL,
                                    TABLE_FEDASYNC_TASK_POOL,
                                    TABLE_FEDASYNC_WEIGHTS_GLOBAL_EVALUATION,
                                    TABLE_FEDASYNC_WEIGHTS_POOL,
                                    TABLE_FEDAVG_TASK_POOL,
                                    TABLE_FEDAVG_WEIGHTS_GLOBAL_EVALUATION,
                                    TABLE_FEDAVG_WEIGHTS_POOL,
                                    TABLE_IRONFORGE_TASK_POOL,
                                    TABLE_IRONFORGE_WEIGHTS_GLOBAL_EVALUATION, 
                                    TABLE_IRONFORGE_WEIGHTS_LOCAL_EVALUATION,
                                    TABLE_IRONFORGE_WEIGHTS_POOL,
                                    TABLE_DIAGNOSE_SLOW_SQL_ANALYSIS)
from flexpkit.exp_settings import mysql_config
from flexpkit.basic_utils import format_call_stack
from flexpkit.redis_utils import redis_cli


class MySQLCli:
    mysql_conn = None

    host = None
    port = None

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def reconnect(self):
        self.mysql_conn = connector.connect(host=self.host, user='root', passwd='flsim', port=self.port,
                                            database='flsim', auth_plugin='caching_sha2_password', connection_timeout=240)

        # This is IMPORTANT, otherwise the connection will use the query cache
        self.mysql_conn.autocommit = True

    def cursor(self):
        if not self.mysql_conn:
            self.reconnect()

        for _ in range(5):
            try:
                cursor = self.mysql_conn.cursor()
                break
            except Exception as e:
                print(e)

                self.reconnect()
                time.sleep(1)

        return cursor

    def commit(self):
        if not self.mysql_conn:
            self.reconnect()

        self.mysql_conn.commit()


mysql_conn_prod = MySQLCli(mysql_config['host'], mysql_config['port'])


def escape_special_chars(content):
    if type(content) == bytes:
        content = content.decode(CHARSET)

    if type(content) == str: 
        content = content.replace('\"', '\\"').replace("\'", '\\"')
    
    return content


def recover_special_chars(content):
    if type(content) == bytes:
        content = content.decode(CHARSET)

    if type(content) == str:
        return content.replace("\'", '"')

    return content


def package_database_result(cols, vals):
    result = {c: recover_special_chars(v) for c, v in zip(cols, vals)}

    for k, v in result.items():
        if type(v) == datetime.datetime:
            result[k] = TIMEZONE.localize(v)

    return result


def get_task_table(fl_system):
    if fl_system == FL_SYSTEM_BLOCKFL:
        return TABLE_BLOCKFL_TASK_POOL

    if fl_system == FL_SYSTEM_DAGFL:
        return TABLE_DAGFL_TASK_POOL

    if fl_system == FL_SYSTEM_FEDASYNC:
        return TABLE_FEDASYNC_TASK_POOL

    if fl_system == FL_SYSTEM_FEDAVG:
        return TABLE_FEDAVG_TASK_POOL

    if fl_system == FL_SYSTEM_IRONFORGE:
        return TABLE_IRONFORGE_TASK_POOL

    return None


def get_weights_table(fl_system):
    if fl_system == FL_SYSTEM_BLOCKFL:
        return TABLE_BLOCKFL_WEIGHTS_POOL

    if fl_system == FL_SYSTEM_DAGFL:
        return TABLE_DAGFL_WEIGHTS_POOL

    if fl_system == FL_SYSTEM_FEDASYNC:
        return TABLE_FEDASYNC_WEIGHTS_POOL

    if fl_system == FL_SYSTEM_FEDAVG:
        return TABLE_FEDAVG_WEIGHTS_POOL

    if fl_system == FL_SYSTEM_IRONFORGE:
        return TABLE_IRONFORGE_WEIGHTS_POOL

    return None


def get_weights_local_evaluation_table(fl_system):
    if fl_system == FL_SYSTEM_DAGFL:
        return TABLE_DAGFL_WEIGHTS_LOCAL_EVALUATION

    if fl_system == FL_SYSTEM_IRONFORGE:
        return TABLE_IRONFORGE_WEIGHTS_LOCAL_EVALUATION

    return None


def get_weights_global_evaluation_table(fl_system):
    if fl_system == FL_SYSTEM_BLOCKFL:
        return TABLE_BLOCKFL_WEIGHTS_GLOBAL_EVALUATION

    if fl_system == FL_SYSTEM_DAGFL:
        return TABLE_DAGFL_WEIGHTS_GLOBAL_EVALUATION

    if fl_system == FL_SYSTEM_FEDASYNC:
        return TABLE_FEDASYNC_WEIGHTS_GLOBAL_EVALUATION

    if fl_system == FL_SYSTEM_FEDAVG:
        return TABLE_FEDAVG_WEIGHTS_GLOBAL_EVALUATION

    if fl_system == FL_SYSTEM_IRONFORGE:
        return TABLE_IRONFORGE_WEIGHTS_GLOBAL_EVALUATION

    return None


def add_sql_record(start_time, complete_time, sql_content, db_conn=None):
    if complete_time - start_time < 0.5:
        return

    if db_conn is None:
        db_conn = mysql_conn_prod

    exec_stack_str = format_call_stack(inspect.stack())
    exec_stack_str = escape_special_chars(exec_stack_str)

    sql_content = escape_special_chars(sql_content)

    # record = {'exec_stack': exec_stack_str, 'sql_content': sql_content, 'used_time': complete_time - start_time, 'start_time': timestamp_to_strftime(start_time), 'complete_time': timestamp_to_strftime(complete_time)}
    # insert_database(TABLE_DIAGNOSE_SLOW_SQL_ANALYSIS, record, ignore_sql_analysis=True, db_conn=db_conn)

    sql = "insert into {}(exec_stack, sql_content, used_time, start_time, complete_time) values ('{}', '{}', {}, '{}', '{}')"
    sql = sql.format(TABLE_DIAGNOSE_SLOW_SQL_ANALYSIS, exec_stack_str, sql_content, complete_time - start_time, timestamp_to_strftime(start_time), timestamp_to_strftime(complete_time))

    # ignore_sql_analysis MUST BE True, otherwise Infinite loop
    execute_update_sql(sql, db_conn=db_conn, ignore_sql_analysis=True)


def execute_query_sql(sql, ignore_sql_analysis=False, db_conn=None):

    if db_conn is None:
        db_conn = mysql_conn_prod
    
    start_time = current_timestamp()

    try:
        cursor = db_conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
    except Exception as e:
        record = {'sql_content': sql}
        if not redis_cli.check_cache_exists('sql_content'):
            redis_cli.set_cached_value('sql_content', sql + str(e))

        # insert_database(TABLE_DIAGNOSE_WRONG_SQL, record, ignore_sql_analysis=True)

        raise e

    complete_time = current_timestamp()

    if not ignore_sql_analysis:
        add_sql_record(start_time, complete_time, sql)

    return result


def execute_update_sql(sql, ignore_sql_analysis=False, db_conn=None):

    if db_conn is None:
        db_conn = mysql_conn_prod
    
    start_time = current_timestamp()

    try:
        db_conn.cursor().execute(sql)
        db_conn.commit()
    except Exception as e:
        record = {'sql_content': sql}
        if not redis_cli.check_cache_exists('sql_content'):
            redis_cli.set_cached_value('sql_content', sql + str(e))

        # 容易导致无限循环
        # insert_database(TABLE_DIAGNOSE_WRONG_SQL, record, ignore_sql_analysis=True)
        raise e

    complete_time = current_timestamp()

    if not ignore_sql_analysis:
        add_sql_record(start_time, complete_time, sql)


def get_table_column_names(table_name, db_conn=None):

    if db_conn is None:
        db_conn = mysql_conn_prod

    sql = "SHOW columns FROM {}".format(table_name)
    result = execute_query_sql(sql, ignore_sql_analysis=True, db_conn=db_conn)

    return [col[0] for col in result]


def query_database(table_name, params, ignore_sql_analysis=False, db_conn=None):

    if db_conn is None:
        db_conn = mysql_conn_prod

    if 'columns' not in params:
        params['columns'] = get_table_column_names(table_name, db_conn)

    sql = 'select {} from {} '.format(','.join(params['columns']), table_name)
    if 'conditions' in params:
        sql += ' where '
        sql += ' and '.join(['{}="{}"'.format(c, v)
                            for c, v in params['conditions'].items()])

    if 'order' in params:
        sql += ' order by {} {}'.format(params['order']
                                        ['key'], params['order']['value'])

    if 'limit' in params and params['limit'] > 0:
        sql += ' limit {}'.format(params['limit'])

    result = execute_query_sql(sql, ignore_sql_analysis=ignore_sql_analysis, db_conn=db_conn)

    if len(result) == 0:
        return []

    return [package_database_result(params['columns'], r) for r in result]


def insert_database(table_name, params, ignore_exist=False, insert_many=False, ignore_sql_analysis=False, db_conn=None):

    if db_conn is None:
        db_conn = mysql_conn_prod

    if not insert_many:
        params = [params, ]

    cols = ', '.join(params[0].keys())
    vals = ', '.join(['%s' for _ in range(len(params[0]))])

    if not ignore_exist:
        sql = 'insert into {}({}) values {}'
    else:
        sql = 'insert ignore into {}({}) values {}'

    data_list = []
    for param in params:
        data = ['"{}"'.format(escape_special_chars(v)) for v in param.values()]
        data_str = ', '.join(data)
        data_str = '({})'.format(data_str)

        data_list.append(data_str)

    vals = ', '.join(data_list)

    # NOTE executemany并不能显著提高插入速度
    # 最终参考了这个答案：https://stackoverflow.com/questions/11053324/oursql-extremely-slow-in-inserting-data
    # mysql_conn_prod.cursor().executemany(sql, data_list)

    sql = sql.format(table_name, cols, vals)

    execute_update_sql(sql, ignore_sql_analysis=ignore_sql_analysis, db_conn=db_conn)


def update_database(table_name, params, ignore_sql_analysis=False, db_conn=None):

    if db_conn is None:
        db_conn = mysql_conn_prod

    sql = 'update {} set '.format(table_name)
    sql += ' , '.join(['{}="{}"'.format(c, escape_special_chars(v)) for c, v in params['updates'].items()])

    if 'conditions' in params:
        sql += ' where '
        sql += ' and '.join(['{}="{}"'.format(c, escape_special_chars(v)) for c, v in params['conditions'].items()])

    execute_update_sql(sql, ignore_sql_analysis=ignore_sql_analysis, db_conn=db_conn)
