#!/bin/sh

#curl -s --digest -u $1:$2 -X GET "http://192.168.1.210/mjpeg/snap.cgi" > /tmp/kitchen.jpg &
#curl -s --digest -u $1:$2 -X GET "http://192.168.1.211/mjpeg/snap.cgi" > /tmp/living_room.jpg &
#curl -s --digest -u $1:$2 -X GET "http://192.168.1.212/mjpeg/snap.cgi" > /tmp/hall.jpg &
/zdrive/home/hass/homeautomation/motion-jpg-fetch 127.0.0.1 8081 > /tmp/porch.jpg &
/zdrive/home/hass/homeautomation/motion-jpg-fetch 127.0.0.1 8082 > /tmp/street.jpg &
/zdrive/home/hass/homeautomation/motion-jpg-fetch 127.0.0.1 8083 > /tmp/driveway.jpg &
/zdrive/home/hass/homeautomation/motion-jpg-fetch 127.0.0.1 8084 > /tmp/backyard.jpg &

/zdrive/home/hass/homeautomation/motion-jpg-fetch 127.0.0.1 8085 > /tmp/kitchen.jpg &
/zdrive/home/hass/homeautomation/motion-jpg-fetch 127.0.0.1 8086 > /tmp/living_room.jpg &
/zdrive/home/hass/homeautomation/motion-jpg-fetch 127.0.0.1 8087 > /tmp/hall.jpg &
/zdrive/home/hass/homeautomation/motion-jpg-fetch 127.0.0.1 8088 > /tmp/office.jpg &
