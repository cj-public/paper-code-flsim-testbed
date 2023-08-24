if [[ $1 == 0 ]]
then
    # 存储路径在/home下

    sudo docker rm -f fastdfs
    sudo rm -rf /home/fastdfs
    sudo mkdir -p /home/fastdfs/
    sudo chmod -R 777 /home/fastdfs/
    sudo docker run --name fastdfs --cpus="6" --memory="16G" -d -v /home/fastdfs:/data -p 18081:8080 -e GO_FASTDFS_DIR=/data sjqzhang/go-fastdfs
    sleep 3
    sudo sed -i 's/"support_group_manage": true/"support_group_manage": false/' /home/fastdfs/conf/cfg.json
    sudo sed -i 's/127.0.0.1"/0.0.0.0"/' /home/fastdfs/conf/cfg.json
    sudo docker restart fastdfs

else
    # 存储路径在/data下
    sudo docker rm -f fastdfs
    sudo rm -rf /data/fastdfs
    sudo mkdir -p /data/fastdfs/
    sudo chmod -R 777 /data/fastdfs/
    sudo docker run --name fastdfs --cpus="6" --memory="16G" -d -v /data/fastdfs:/data -p 18081:8080 -e GO_FASTDFS_DIR=/data sjqzhang/go-fastdfs
    sleep 3
    sudo sed -i 's/"support_group_manage": true/"support_group_manage": false/' /data/fastdfs/conf/cfg.json
    sudo sed -i 's/127.0.0.1"/0.0.0.0"/' /data/fastdfs/conf/cfg.json
    sudo docker restart fastdfs

fi