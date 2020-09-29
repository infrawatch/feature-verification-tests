if grep -q ": 2" results.txt; then
    echo "ONE OR MORE CONTAINERS ARE NOT HEALTHY!!"
else
    echo "all dockers are healthy!!"
fi
