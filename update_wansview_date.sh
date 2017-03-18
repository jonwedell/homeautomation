#!/bin/bash

hosts=('192.168.1.210' '192.168.1.211' '192.168.1.212')
username=$1
pass=$2
now=`date +%Y-%m-%d\;%H:%M:%S`

for host in ${hosts[*]}; do
  echo "Updating time for: $host"
  url="http://${host}/hy-cgi/device.cgi?cmd=setsystime&stime=${now}&timezone=11"
#  echo "curl --digest -u $username:$pass -X GET $url"
  curl --digest -u $username:$pass -X GET $url
done