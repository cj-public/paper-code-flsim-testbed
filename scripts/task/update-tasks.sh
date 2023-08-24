host="mysql.flsim.iovi.com"

user="root"
port=3307
password="flsim"
dbname="flsim"

max_iter=3000

if [[ $1 == 1 ]]
then
    mysql -h$host -P$port -u$user -p$password -e "update flsim.blockfl_task_pool set status='ready', max_iteration=$max_iter"
fi

if [[ $2 == 2 ]]
then
    mysql -h$host -P$port -u$user -p$password -e "update flsim.dagfl_task_pool set status='ready', max_iteration=$max_iter"
fi

if [[ $3 == 3 ]]
then
    mysql -h$host -P$port -u$user -p$password -e "update flsim.fedasync_task_pool set status='ready', max_iteration=$max_iter"
fi

if [[ $4 == 4 ]]
then
    mysql -h$host -P$port -u$user -p$password -e "update flsim.fedavg_task_pool set status='ready', max_iteration=$max_iter"
fi

if [[ $5 == 5 ]]
then
    mysql -h$host -P$port -u$user -p$password -e "update flsim.ironforge_task_pool set status='ready', max_iteration=$max_iter"
fi