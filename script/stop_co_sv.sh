pid=`lsof -i:3010 | awk '{print $2}' | tr -d "PID"`
kill -9 $pid
