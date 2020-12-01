SHARE=$(pwd)
IMAGE=$1
NAME=$(sudo docker run -d -v ${SHARE}:/host/Users -it ${IMAGE} /bin/bash)
sudo docker exec -it $NAME ./ask /host/Users/Development_data/set1/a1.txt 5 | tee tests/ddset1a1.txt
echo '****************'
sudo docker exec -it $NAME ./answer /host/Users/Development_data/set1/a1.txt /host/Users/tests/ddset1a1.txt

# # Development_data
# for (( i = 1; i <= 5; i++ ))
# do
#     for (( j = 1; j <= 10; j++ ))
#     do
#         echo "Development_data/set${i}/a${j}.txt"
#         echo '****************'
#         start_time=$(date +%s)
#         sudo docker exec -it $NAME ./ask /host/Users/Development_data/set"$i"/a"$j".txt 5 | tee tests/ddset"$i"a"$j".txt
#         end_time=$(date +%s)
#         dur=$(expr $end_time - $start_time)
#         echo '---------'
#         echo "Execution time was ${dur}s."
#         echo '****************'
#         start_time=$(date +%s)
#         sudo docker exec -it $NAME ./answer /host/Users/Development_data/set"$i"/a"$j".txt /host/Users/tests/ddset"$i"a"$j".txt
#         end_time=$(date +%s)
#         dur=$(expr $end_time - $start_time)
#         echo '---------'
#         echo "Execution time was ${dur}s."
#         echo '****************'    
#     done
# done

# # data
# for (( i = 1; i <= 4; i++ ))
# do
#     for (( j = 1; j <= 10; j++ ))
#     do
#         echo "data/set${i}/a${j}.txt"
#         echo '****************'
#         start_time=$(date +%s)
#         sudo docker exec -it $NAME ./ask /host/Users/data/set"$i"/a"$j".txt 5 | tee tests/dset"$i"a"$j".txt
#         end_time=$(date +%s)
#         dur=$(expr $end_time - $start_time)
#         echo '---------'
#         echo "Execution time was ${dur}s."
#         echo '****************'
#         start_time=$(date +%s)
#         sudo docker exec -it $NAME ./answer /host/Users/data/set"$i"/a"$j".txt /host/Users/tests/dset"$i"a"$j".txt
#         end_time=$(date +%s)
#         dur=$(expr $end_time - $start_time)
#         echo '---------'
#         echo "Execution time was ${dur}s."
#         echo '****************'    
#     done
# done

# # noun_counting_data
# for (( j = 1; j <= 10; j++ ))
#     do
#         echo "noun_counting_data/a${j}.txt"
#         echo '****************'
#         start_time=$(date +%s)
#         sudo docker exec -it $NAME ./ask /host/Users/noun_counting_data/a"$j".txt 5 | tee tests/ncda"$j".txt
#         end_time=$(date +%s)
#         dur=$(expr $end_time - $start_time)
#         echo "execution time was ${dur} s."
#         echo '---------'
#         echo '****************'
#         start_time=$(date +%s)
#         sudo docker exec -it $NAME ./answer /host/Users/noun_counting_data/a"$j".txt /host/Users/tests/ncda"$j".txt
#         end_time=$(date +%s)
#         dur=$(expr $end_time - $start_time)
#         echo "execution time was ${dur} s."
#         echo '---------'
#         echo '****************'    
#     done
sudo docker stop $NAME >/dev/null