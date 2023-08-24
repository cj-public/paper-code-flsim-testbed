current_time=$(date "+%Y.%m.%d-%H.%M.%S")
mysqldump --column-statistics=0  -uroot -pflsim -hmysql.flsim.iovi.com -P3307 flsim > ./backup/flsim-$current_time.prod.sql
mysqldump --column-statistics=0  -uroot -pflsim -hmysql.flsim.iovi.com -P3308 flsim > ./backup/flsim-$current_time.back.sql