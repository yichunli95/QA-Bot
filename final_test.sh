SHARE=$(pwd)
IMAGE=$1
NAME=$(sudo docker run -d -v ${SHARE}:/host/Users -it ${IMAGE} /bin/bash)
echo '****************'
sudo docker exec -it $NAME ./ask /host/Users/Development_data/set5/a10.txt 10
echo '****************'
sudo docker exec -it $NAME ./answer /host/Users/Development_data/set5/a10.txt /host/Users/s5a10Q.txt
echo '****************'
sudo docker stop $NAME >/dev/null
