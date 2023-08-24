PYTHONPATH='./src' python agent.py --node_type node-type-000 --name flsim-worker-00028_flsim-worker-00011_flsim-worker-00026 --mode debug
PYTHONPATH='./src' python agent.py --node_type node-type-000 --name flsim-miner-06000
PYTHONPATH='./src' python scheduler.py 
PYTHONPATH='./src' python evaluator.py --name evaluator-00005 --devid 5

PYTHONPATH='./src' mprof run agent.py --node_type node-type-000 --name flsim-worker-00011_flsim-worker-00021_flsim-worker-00031 --mode debug
mprof plot mprofiler_xxx.dat

nodemon --exec "PYTHONPATH='./src' python -v" agent.py --node_type node-type-000 --names flsim_worker-00028_flsim_worker-00011_flsim_worker-00026

sudo docker rmi -f $(sudo docker images | grep 'flsim-node')
sudo docker rmi -f $(sudo docker images | grep 'flsim-env')

SELECT UNIX_TIMESTAMP(create_time) from blockfl_task_pool LIMIT 0,100

SELECT * FROM task_scheduling_history where event='schedule' ORDER BY task_id, occur_time desc LIMIT 0,100

mysql -uroot -p -P3307 -hgpu3.zjsec.cn
CREATE DATABASE `flsim`;
use flsim;
source backup/flsim-2023.05.04-10.48.00.prod.sql;

mysql -uroot -p -P3308 -hgpu3.zjsec.cn
CREATE DATABASE `flsim`;
use flsim;
source backup/flsim-2023.05.04-10.48.00.back.sql
