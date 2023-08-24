sudo rm -rf /tmp/storage
docker ps --filter name="flsim-worker-" -aq | xargs docker rm -f
docker ps --filter name="flsim-master-" -aq | xargs docker rm -f
docker ps --filter name="flsim-miner-" -aq | xargs docker rm -f
docker ps --filter name="flsim-evaluator-" -aq | xargs docker rm -f