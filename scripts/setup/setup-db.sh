host="mysql.flsim.iovi.com"

user="root"
password="flsim"
dbname="flsim"

port=3307
mysql -h$host -P$port -u$user -p$password -e "drop database $dbname"
mysql -h$host -P$port -u$user -p$password -e "source resources/flsim.sql"

port=3308
mysql -h$host -P$port -u$user -p$password -e "drop database $dbname"
mysql -h$host -P$port -u$user -p$password -e "source resources/flsim.sql"

rm -rf /tmp/localfs
rm -rf /tmp/localfs-tmp

mkdir  /tmp/localfs
mkdir /tmp/localfs-tmp

redis-cli -h $host -p 6380 -n 0 flushdb