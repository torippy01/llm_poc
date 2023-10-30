pid=`lsof -i:3999 | awk '{print $2}' | tr -d "PID"`
kill -9 $pid
