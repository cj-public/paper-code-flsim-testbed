FLSIM_VERION = 'v1.4.3'

RUN_TYPE_DEBUG = 'debug'
RUN_TYPE_PROD = 'prod'

MODEL_SIMPLE_CNN = 'simple-cnn'
MODEL_SIMPLE_CNN_1 = 'simple-cnn-1'
MODEL_SIMPLE_CNN_2 = 'simple-cnn-2'
MODEL_SIMPLE_CNN_3 = 'simple-cnn-3'
MODEL_SIMPLE_CNN_4 = 'simple-cnn-4'
MODEL_SIMPLE_CNN_5 = 'simple-cnn-5'
MODEL_SIMPLE_CNN_6 = 'simple-cnn-6'
MODEL_SIMPLE_CNN_7 = 'simple-cnn-7'

MODEL_SIMPLE_LSTM = 'simple-lstm'
MODEL_SIMPLE_LSTM_1 = 'simple-lstm-1'

MODEL_DIR = './output/models/'
SIMPLE_CNN_MODEL_FOR_MNIST_WEIGHTS_FILE_PATH = '{}/simple-cnn-model-for-mnist-init-weights.pkl'.format(MODEL_DIR)
SIMPLE_LSTM_MODEL_FOR_SHAKESPEARE_WEIGHTS_FILE_PATH = '{}/simple-lstm-model-for-shakespeare-init-weights.pkl'.format(MODEL_DIR)
SIMPLE_CNN_MODEL_FOR_CIFAR10_WEIGHTS_FILE_PATH = '{}/simple-cnn-model-for-cifar10-init-weights.pkl'.format(MODEL_DIR)

DATASET_CIFAR10 = 'cifar10'
DATASET_MNIST = 'mnist'
DATASET_SHAKESPEARE = 'shakespeare'

TABLE_BLOCKFL_TASK_POOL = 'blockfl_task_pool'
TABLE_BLOCKFL_WEIGHTS_POOL = 'blockfl_weights_pool'
TABLE_BLOCKFL_WEIGHTS_GLOBAL_EVALUATION = 'blockfl_weights_global_evaluation'

TABLE_DAGFL_TASK_POOL = 'dagfl_task_pool'
TABLE_DAGFL_WEIGHTS_POOL = 'dagfl_weights_pool'
TABLE_DAGFL_WEIGHTS_LOCAL_EVALUATION = 'dagfl_weights_local_evaluation'
TABLE_DAGFL_WEIGHTS_GLOBAL_EVALUATION = 'dagfl_weights_global_evaluation'

TABLE_FEDASYNC_TASK_POOL = 'fedasync_task_pool'
TABLE_FEDASYNC_WEIGHTS_POOL = 'fedasync_weights_pool'
TABLE_FEDASYNC_WEIGHTS_GLOBAL_EVALUATION = 'fedasync_weights_global_evaluation'

TABLE_FEDAVG_TASK_POOL = 'fedavg_task_pool'
TABLE_FEDAVG_WEIGHTS_POOL = 'fedavg_weights_pool'
TABLE_FEDAVG_WEIGHTS_GLOBAL_EVALUATION = 'fedavg_weights_global_evaluation'

TABLE_IRONFORGE_TASK_POOL = 'ironforge_task_pool'
TABLE_IRONFORGE_WEIGHTS_POOL = 'ironforge_weights_pool'
TABLE_IRONFORGE_WEIGHTS_LOCAL_EVALUATION = 'ironforge_weights_local_evaluation'
TABLE_IRONFORGE_WEIGHTS_GLOBAL_EVALUATION = 'ironforge_weights_global_evaluation'

TABLE_DATASETS = 'y_datasets'
TABLE_RUNNERS = 'y_runners'
TABLE_RUNNER_TASK_SETTINGS = 'y_runner_task_settings'

TABLE_DIAGNOSE_RUNNER_EXECUTATION_HISTORY = 'z_diagnose_runner_executation_history'
TABLE_DIAGNOSE_RUNNER_RUNTIME_ERRORS = 'z_diagnose_runner_runtime_errors'
TABLE_DIAGNOSE_SLOW_DFS_ANALYSIS = 'z_diagnose_slow_dfs_analysis'
TABLE_DIAGNOSE_SLOW_SQL_ANALYSIS = 'z_diagnose_slow_sql_analysis'
TABLE_DIAGNOSE_TASK_SCHEDULING_HISTORY = 'z_diagnose_task_scheduling_history'
TABLE_DIAGNOSE_WHOLE_TASKS_PROGRESS = 'z_diagnose_whole_tasks_progress'
TABLE_DIAGNOSE_WRONG_SQL = 'z_diagnose_wrong_sql'

MESSAGE_QUEUE_NAME_AGENT = 'message_queue.agent'

EVENT_LOCAL_WEIGHTS_UPLOADED = 'local_weights_uploaded'
EVENT_GLOBAL_WEIGHTS_UPLOADED = 'global_weights_uploaded'
EVENT_TASK_DONE = 'task_done'
EVENT_TASK_PUBLISHED = 'task_published'
EVENT_RUNNER_SYNC = 'runner_sync'

STORAGE_FASTDFS = 'fastdfs'

CHARSET = 'utf-8'

# ready for tasks if status is idle
RUNNER_STATUS_IDLE = 'idle'

# discard any taks if status is sleep
RUNNER_STATUS_SLEEP = 'sleep'

RUNNER_MODE_NORMAL = 'normal'
RUNNER_MODE_BACKDOOR = 'backdoor'
RUNNER_MODE_DISHONEST = 'dishonest'
RUNNER_MODE_NOISE = 'noise'
RUNNER_MODE_POISON = 'poison'

TASK_STATUS_READY = 'ready'
TASK_STATUS_RUNNING = 'running'
TASK_STATUS_STOPPED = 'stopped'
TASK_STATUS_DONE = 'done'

FL_SYSTEM_BLOCKFL = 'blockfl'
FL_SYSTEM_DAGFL = 'dagfl'
FL_SYSTEM_FEDASYNC = 'fedasync'
FL_SYSTEM_FEDAVG = 'fedavg'
FL_SYSTEM_IRONFORGE = 'ironforge'

DATASET_SHARDING_SCHEMA001 = 'sharding-schema-001'
DATASET_SHARDING_SCHEMA002 = 'sharding-schema-002'
DATASET_SHARDING_SCHEMA003 = 'sharding-schema-003'

RUNNER_TYPE_PUBLISHER = 'publisher'
RUNNER_TYPE_WORKER = 'worker'
RUNNER_TYPE_MASTER = 'master'
RUNNER_TYPE_MINER = 'miner'
RUNNER_TYPE_EVALUATOR = 'evaluator'

NODE_TYPE_000 = 'node-type-000'

NODE_TYPE_011 = 'node-type-011'
NODE_TYPE_012 = 'node-type-012'
NODE_TYPE_013 = 'node-type-013'
NODE_TYPE_014 = 'node-type-014'

NODE_TYPE_021 = 'node-type-021'
NODE_TYPE_022 = 'node-type-022'
NODE_TYPE_023 = 'node-type-023'
NODE_TYPE_024 = 'node-type-024'

NODE_TYPE_031 = 'node-type-031'
NODE_TYPE_032 = 'node-type-032'
NODE_TYPE_033 = 'node-type-033'
NODE_TYPE_034 = 'node-type-034'

NODE_TYPE_061 = 'node-type-061'

NODE_TYPE_X_RUNNER_START_INDEX = {
    NODE_TYPE_000: 0,

    NODE_TYPE_011: 1100,
    NODE_TYPE_012: 1200,
    NODE_TYPE_013: 1300,
    NODE_TYPE_014: 1400,

    NODE_TYPE_021: 2100,
    NODE_TYPE_022: 2200,
    NODE_TYPE_023: 2300,
    NODE_TYPE_024: 2400,

    NODE_TYPE_031: 3100,
    NODE_TYPE_032: 3200,
    NODE_TYPE_033: 3300,
    NODE_TYPE_034: 3400,

    NODE_TYPE_061: 6100,
}

FLAG_ALL_TASKS_ALLOWED = 'all tasks allowed'

NO_BACKDOOR_PARAMS = {'ratio': 0}
NO_DISHONEST_PARAMS = {'ratio': 0}
NO_NOISE_PARAMS = {'gaussian': {'ratio': 0.0, 'mean': 0, 'stddev': 0}, 'flip': {'ratio': 0.0, 'flip_times': 0}}
NO_POISON_PARAMS = {'ratio': 0}

DEFAULT_BACKDOOR_PARAMS = {'ratio': 0.5}
DEFAULT_DISHONEST_PARAMS = {'ratio': 0.5}
DEFAULT_NOISE_PARAMS = {'gaussian': {'ratio': 1.0, 'mean': 0, 'stddev': 1.0}, 'flip': {'ratio': 1.0, 'flip_times': 3}}
DEFAULT_POISON_PARAMS = {'ratio': 0.5}

WEIGHTS_TYPE_LOCAL = 'local_weights'
WEIGHTS_TYPE_GLOBAL = 'global_weights'

TMP_STORAGE_VOLUME = '/tmp/storage/'
LOCAL_PERSISTENT_STORAGE_PATH = '/tmp/localfs-persistent'
LOCAL_VOLATILE_STORAGE_PATH = '/tmp/localfs-volatile'

POL_VERIFIED = 1
POL_PENDING = 0
POL_REJECTED = -1