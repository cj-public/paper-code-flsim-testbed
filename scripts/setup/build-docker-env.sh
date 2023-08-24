docker_repo_url='docker.flsim.iovi.com:5000'
image_name='flsim-env:0.2.2'

docker rmi -f $docker_repo_url/$image_name

cp ./resources/Dockerfile.env ./Dockerfile
docker build -t $image_name ./

docker tag $image_name $docker_repo_url/$image_name
docker rmi -f $image_name

docker login $docker_repo_url
docker push $docker_repo_url/$image_name

rm Dockerfile