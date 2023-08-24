from flexpkit.basic_utils import load_json
from flexpkit.exp_constants import (NODE_TYPE_000, NODE_TYPE_011, NODE_TYPE_012, 
                                    NODE_TYPE_013, NODE_TYPE_021,
                                    NODE_TYPE_022, NODE_TYPE_023,
                                    NODE_TYPE_031, NODE_TYPE_032, NODE_TYPE_033,
                                    NODE_TYPE_061,
                                    STORAGE_FASTDFS)

config = load_json('./config/flsim.conf')

# which environment to conduct the experiments
mysql_config = config['mysql']
redis_config = config['redis']

fastdfs_node_urls = config['fastdfs']

underlying_storage_system = STORAGE_FASTDFS

"""
node_type_config_list = {
    # 单位分别为: core, GB, GB, MB/s
    NODE_TYPE_000: {'cpu': 2, 'memory': 4, 'bandwidth': 16},

    NODE_TYPE_000: {'cpu': 2, 'memory': 4, 'bandwidth': 16},
    NODE_TYPE_011: {'cpu': 4, 'memory': 4, 'bandwidth': 16},
    NODE_TYPE_012: {'cpu': 6, 'memory': 4, 'bandwidth': 16},
    NODE_TYPE_013: {'cpu': 8, 'memory': 4,  'bandwidth': 16},

    NODE_TYPE_000: {'cpu': 2, 'memory': 4, 'bandwidth': 16},
    NODE_TYPE_021: {'cpu': 2, 'memory': 6, 'bandwidth': 16},
    NODE_TYPE_022: {'cpu': 2, 'memory': 8, 'bandwidth': 16},
    NODE_TYPE_023: {'cpu': 2, 'memory': 10, 'bandwidth': 16},

    NODE_TYPE_000: {'cpu': 2, 'memory': 4, 'bandwidth': 2},
    NODE_TYPE_031: {'cpu': 2, 'memory': 4, 'bandwidth': 4},
    NODE_TYPE_032: {'cpu': 2, 'memory': 4, 'bandwidth': 8},
    NODE_TYPE_033: {'cpu': 2, 'memory': 4, 'bandwidth': 12},

    NODE_TYPE_061: {'cpu': 4, 'memory': 8, 'bandwidth': 1000},
}
"""

node_type_config_list = {
    # 单位分别为: core, GB, GB, MB/s
    NODE_TYPE_000: {'cpu': 2, 'memory': 6, 'bandwidth': 16},

    NODE_TYPE_011: {'cpu': 4, 'memory': 6, 'bandwidth': 16},
    NODE_TYPE_012: {'cpu': 6, 'memory': 6, 'bandwidth': 16},
    NODE_TYPE_013: {'cpu': 8, 'memory': 6,  'bandwidth': 16},

    NODE_TYPE_021: {'cpu': 2, 'memory': 8, 'bandwidth': 16},
    NODE_TYPE_022: {'cpu': 2, 'memory': 10, 'bandwidth': 16},
    NODE_TYPE_023: {'cpu': 2, 'memory': 12, 'bandwidth': 16},

    NODE_TYPE_031: {'cpu': 2, 'memory': 6, 'bandwidth': 4},
    NODE_TYPE_032: {'cpu': 2, 'memory': 6, 'bandwidth': 8},
    NODE_TYPE_033: {'cpu': 2, 'memory': 6, 'bandwidth': 12},

    NODE_TYPE_061: {'cpu': 4, 'memory': 10, 'bandwidth': 1000},
}

"""
task是按照顺序调度的，因此某一时刻，只有一个task在运行，PHYSICAL_NODE_NUM_EACH_TASK指每个task能使用的物理节点个数
虽然创建的docker容器个数会多倍于PHYSICAL_NODE_NUM_EACH_TASK，但同一时间运行的node数量<=HYSICAL_NODE_NUM
"""

# 这个不允许改，否则会出现竞争关系，同一个node一个时间段内只能服务一个task

TASK_WORKER_NUM = 100 
TASK_AVG_WORKER_NUM = int(TASK_WORKER_NUM / 5)

VIRTUAL_NODE_NUM_EACH_TASK = TASK_WORKER_NUM
RUNNER_NUM_EACH_NODE = 1
PHYSICAL_NODE_NUM_EACH_TASK = VIRTUAL_NODE_NUM_EACH_TASK / RUNNER_NUM_EACH_NODE

MAX_NETWORK_DELAY = 0.001

# 在blockfl中，miner与worker是绑定的，一个block至少3个transaction，即5个miner至少有一个有3个candidate transaction，所以至少2*5+1个worker同时运行
# WORKER_IDLE_PROBABILITY_BLOCKFL = 0.10 * RUNNER_NUM_EACH_NODE
# WORKER_IDLE_PROBABILITY_DAGFL = 0.10 * RUNNER_NUM_EACH_NODE
# WORKER_IDLE_PROBABILITY_FEDASYNC = 0.10 * RUNNER_NUM_EACH_NODE
# WORKER_IDLE_PROBABILITY_FEDAVG = 0.10 * RUNNER_NUM_EACH_NODE
# WORKER_IDLE_PROBABILITY_IRONFORGE = 0.10 * RUNNER_NUM_EACH_NODE
# ABANDON_UPLOADING_PROBABILITY = 0

MAX_CONCURRENT_SCHEDULING_TASK_COUNT = 2

MINER_NUM = 5

DATASET_SHARD_NUM = TASK_WORKER_NUM
DATASET_AVG_SHARD_NUM = int(DATASET_SHARD_NUM / 5)

STORAGE_LOAD_BALANCE_ENABLED = False

LEARNING_RATE_FOR_CIFAR10 = 0.005
LEARNING_RATE_FOR_MNIST = 0.002
LEARNING_RATE_FOR_SHAKESPEARE = 0.001

EMBEDDING_VECTOR_SIZE_FOR_SHAKESPEARE = 16

TASK_REWARDS = 1000
REWARD_ACCURACY_THRESHOLD_FOR_CIFAR10 = -1 # 0.600
REWARD_ACCURACY_THRESHOLD_FOR_MNIST = -1 # 0.960
REWARD_ACCURACY_THRESHOLD_FOR_SHAKESPEARE = -1 # 0.1

MAX_ITERATION_FOR_CIFAR10_TASK = 4000
MAX_ITERATION_FOR_MNIST_TASK = 3000
MAX_ITERATION_FOR_SHAKESPEARE_TASK = 3000

DATASET_CACHE_ENABLED = True