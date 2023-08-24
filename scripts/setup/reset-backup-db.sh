host="mysql.flsim.iovi.com"

user="root"
port=3308
password="flsim"
dbname="flsim"
mysql -h$host -P$port -u$user -p$password -e "drop database $dbname"
mysql -h$host -P$port -u$user -p$password -e "source resources/flsim.sql"