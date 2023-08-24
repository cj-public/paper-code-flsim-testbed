sudo apt install -y gnupg2 pass
sudo apt install -y nodejs npm mysql-client graphviz
sudo apt-get install -y texlive-latex-extra texlive-fonts-recommended dvipng cm-super
sudo apt-get install -y libcurl4-openssl-dev
sudo apt-get install -y libffi-dev curl

npm install --global redis-cli

docker_repo_url='docker.flsim.iovi.com:5000'
docker login $docker_repo_url
docker pull $docker_repo_url/flsim-env:0.2.2
docker pull $docker_repo_url/flsim-node:0.2.8

mkdir  /tmp/localfs
mkdir /tmp/localfs-tmp