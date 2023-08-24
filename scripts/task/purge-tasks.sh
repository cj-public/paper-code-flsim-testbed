host="mysql.flsim.iovi.com"

user="root"
password="flsim"
dbname="flsim"

port=3307
mysql -h$host -P$port -u$user -p$password -e "delete from flsim.y_runner_task_settings"

mysql -h$host -P$port -u$user -p$password -e "delete from flsim.blockfl_task_pool"
mysql -h$host -P$port -u$user -p$password -e "delete from flsim.blockfl_weights_pool"
mysql -h$host -P$port -u$user -p$password -e "delete from flsim.blockfl_weights_global_evaluation"

mysql -h$host -P$port -u$user -p$password -e "delete from flsim.dagfl_task_pool"
mysql -h$host -P$port -u$user -p$password -e "delete from flsim.dagfl_weights_pool"
mysql -h$host -P$port -u$user -p$password -e "delete from flsim.dagfl_weights_local_evaluation"
mysql -h$host -P$port -u$user -p$password -e "delete from flsim.dagfl_weights_global_evaluation"

mysql -h$host -P$port -u$user -p$password -e "delete from flsim.fedasync_task_pool"
mysql -h$host -P$port -u$user -p$password -e "delete from flsim.fedasync_weights_pool"
mysql -h$host -P$port -u$user -p$password -e "delete from flsim.fedasync_weights_global_evaluation"

mysql -h$host -P$port -u$user -p$password -e "delete from flsim.fedavg_task_pool"
mysql -h$host -P$port -u$user -p$password -e "delete from flsim.fedavg_weights_pool"
mysql -h$host -P$port -u$user -p$password -e "delete from flsim.fedavg_weights_global_evaluation"

mysql -h$host -P$port -u$user -p$password -e "delete from flsim.ironforge_task_pool"
mysql -h$host -P$port -u$user -p$password -e "delete from flsim.ironforge_weights_pool"
mysql -h$host -P$port -u$user -p$password -e "delete from flsim.ironforge_weights_local_evaluation"
mysql -h$host -P$port -u$user -p$password -e "delete from flsim.ironforge_weights_global_evaluation"

redis-cli -h $host -p 6380 -n 0 flushdb

port=3308
mysql -h$host -P$port -u$user -p$password -e "drop database $dbname"
mysql -h$host -P$port -u$user -p$password -e "source resources/flsim.sql"
