#!/usr/bin/env python3

import requests
import argparse
from modules import configuration

# On or off
argparser = argparse.ArgumentParser(description="Toggles motion between always recording and not.")
argparser.add_argument("--off", action="store_false", dest="record", default=True,
                     help="Turn off recording rather than turn it on.")
argparser.add_argument("--host", dest="host", default=configuration["motion"]["host"], type=str,
                     help="The Motion host. (IP or hostname).")
argparser.add_argument("--port", dest="port", default=configuration["motion"]["port"], type=int,
                     help="The port of the command interface.")
argparser.add_argument("--camera", dest="camera", default=[0], type=int, nargs='+',
                     help="The camera number to toggle. Default of 0 means all.")
argparser.add_argument("--user", dest="user", default=configuration["motion"]["user"], type=str,
                     help="The user to authenticate with Motion web interface.")
argparser.add_argument("--password", dest="password", default=configuration["motion"]["password"], type=str,
                     help="The password to authenticate with Motion web interface")

args = argparser.parse_args()

state = "on"
if not args.record:
    state = "off"

for camera in args.camera:
    # Enable video recording
    r = requests.get("http://%s:%s/%s/config/set?ffmpeg_output_movies=%s" % (args.host, args.port, camera, state), auth=(args.user, args.password))
    # Fake constant motion
    r = requests.get("http://%s:%s/%sconfig/set?emulate_motion=%s" % (args.host, args.port, camera, state), auth=(args.user, args.password))
