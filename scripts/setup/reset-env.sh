if [[ $1 = 'soft' ]]
then
    bash scripts/setup/deploy-flsim-code.sh
    bash scripts/task/purge-tasks.sh

elif [[ $1 = 'hard' ]]
then
    bash scripts/runner/destroy-remote-runners.sh
    bash scripts/setup/build-docker-node.sh
    bash scripts/setup/deploy-flsim-code.sh
    bash scripts/runner/destroy-remote-runners.sh
    bash scripts/runner/launch-remote-runners.sh
fi