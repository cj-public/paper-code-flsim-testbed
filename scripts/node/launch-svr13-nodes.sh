docker login docker.flsim.iovi.com:5000
docker pull docker.flsim.iovi.com:5000/flsim-env:0.2.2
docker pull docker.flsim.iovi.com:5000/flsim-node:0.2.8
docker run --network host --name flsim-master-06100 -d -v /tmp/paper-code-flsim-testbed:/var/app -e TZ=Asia/Shanghai --env NODE_TYPE="node-type-061" --env RUNNER_NAME="flsim-master-06100" --cpus="4" --memory="10G" docker.flsim.iovi.com:5000/flsim-node:0.2.8
docker run --network host --name flsim-master-06101 -d -v /tmp/paper-code-flsim-testbed:/var/app -e TZ=Asia/Shanghai --env NODE_TYPE="node-type-061" --env RUNNER_NAME="flsim-master-06101" --cpus="4" --memory="10G" docker.flsim.iovi.com:5000/flsim-node:0.2.8
docker run --network host --name flsim-miner-06100 -d -v /tmp/paper-code-flsim-testbed:/var/app -e TZ=Asia/Shanghai --env NODE_TYPE="node-type-061" --env RUNNER_NAME="flsim-miner-06100" --cpus="4" --memory="10G" docker.flsim.iovi.com:5000/flsim-node:0.2.8
docker run --network host --name flsim-miner-06101 -d -v /tmp/paper-code-flsim-testbed:/var/app -e TZ=Asia/Shanghai --env NODE_TYPE="node-type-061" --env RUNNER_NAME="flsim-miner-06101" --cpus="4" --memory="10G" docker.flsim.iovi.com:5000/flsim-node:0.2.8
docker run --network host --name flsim-miner-06102 -d -v /tmp/paper-code-flsim-testbed:/var/app -e TZ=Asia/Shanghai --env NODE_TYPE="node-type-061" --env RUNNER_NAME="flsim-miner-06102" --cpus="4" --memory="10G" docker.flsim.iovi.com:5000/flsim-node:0.2.8
docker run --network host --name flsim-miner-06103 -d -v /tmp/paper-code-flsim-testbed:/var/app -e TZ=Asia/Shanghai --env NODE_TYPE="node-type-061" --env RUNNER_NAME="flsim-miner-06103" --cpus="4" --memory="10G" docker.flsim.iovi.com:5000/flsim-node:0.2.8
docker run --network host --name flsim-miner-06104 -d -v /tmp/paper-code-flsim-testbed:/var/app -e TZ=Asia/Shanghai --env NODE_TYPE="node-type-061" --env RUNNER_NAME="flsim-miner-06104" --cpus="4" --memory="10G" docker.flsim.iovi.com:5000/flsim-node:0.2.8