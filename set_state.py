#!/usr/bin/python

import sys
import requests

requests.post('http://localhost:8123/api/states/binary_sensor.%s' % sys.argv[1], json={"state": sys.argv[2]})
