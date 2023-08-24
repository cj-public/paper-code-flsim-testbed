host="mysql.flsim.iovi.com"

user="root"
port=3307
password="flsim"
dbname="flsim"

if [[ $1 == 1 ]]
then
    mysql -h$host -P$port -u$user -p$password -e "update flsim.blockfl_task_pool set status='stopped'"
    mysql -h$host -P$port -u$user -p$password -e "delete from flsim.blockfl_weights_pool where contributor!='publisher'"
    mysql -h$host -P$port -u$user -p$password -e "delete from flsim.blockfl_weights_global_evaluation"
fi

if [[ $2 == 2 ]]
then 
    mysql -h$host -P$port -u$user -p$password -e "update flsim.dagfl_task_pool set status='stopped'"
    mysql -h$host -P$port -u$user -p$password -e "delete from flsim.dagfl_weights_pool where contributor!='publisher'"
    mysql -h$host -P$port -u$user -p$password -e "delete from flsim.dagfl_weights_local_evaluation"
    mysql -h$host -P$port -u$user -p$password -e "delete from flsim.dagfl_weights_global_evaluation"
fi

if [[ $3 == 3 ]]
then
    mysql -h$host -P$port -u$user -p$password -e "update flsim.fedasync_task_pool set status='stopped'"
    mysql -h$host -P$port -u$user -p$password -e "delete from flsim.fedasync_weights_pool where contributor!='publisher'"
    mysql -h$host -P$port -u$user -p$password -e "delete from flsim.fedasync_weights_global_evaluation"
fi

if [[ $4 == 4 ]]
then
    mysql -h$host -P$port -u$user -p$password -e "update flsim.fedavg_task_pool set status='stopped'"
    mysql -h$host -P$port -u$user -p$password -e "delete from flsim.fedavg_weights_pool where contributor!='publisher'"
    mysql -h$host -P$port -u$user -p$password -e "delete from flsim.fedavg_weights_global_evaluation"
fi

if [[ $5 == 5 ]]
then 
    mysql -h$host -P$port -u$user -p$password -e "update flsim.ironforge_task_pool set status='stopped'"
    mysql -h$host -P$port -u$user -p$password -e "delete from flsim.ironforge_weights_pool where contributor!='publisher'"
    mysql -h$host -P$port -u$user -p$password -e "delete from flsim.ironforge_weights_local_evaluation"
    mysql -h$host -P$port -u$user -p$password -e "delete from flsim.ironforge_weights_global_evaluation"
fi

rm -rf /tmp/localfs
rm -rf /tmp/localfs-tmp

mkdir  /tmp/localfs
mkdir /tmp/localfs-tmp

redis-cli -h $host -p 6380 -n 0 flushdb
