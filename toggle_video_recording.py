#!/usr/bin/env python3

import requests
import optparse
from modules import configuration

# On or off
optparser = optparse.OptionParser(description="Toggles motion between always recording and not.")
optparser.add_option("--off", action="store_false", dest="record", default=True,
                     help="Turn off recording rather than turn it on.")
optparser.add_option("--host", action="store", dest="host", default=configuration["motion"]["host"], type="string",
                     help="The Motion host. (IP or hostname).")
optparser.add_option("--port", action="store", dest="port", default=configuration["motion"]["port"], type="int",
                     help="The port of the command interface.")
optparser.add_option("--user", action="store", dest="user", default=configuration["motion"]["user"], type="string",
                     help="The user to authenticate with Motion web interface.")
optparser.add_option("--password", action="store", dest="password", default=configuration["motion"]["password"], type="string",
                     help="The password to authenticate with Motion web interface")

(options, cmd_input) = optparser.parse_args()

state = "on"
if not options.record:
    state = "off"

# Enable video recording
r = requests.get("http://%s:%s/0/config/set?ffmpeg_output_movies=%s" % (options.host, options.port, state), auth=(options.user, options.password))
# Fake constant motion
r = requests.get("http://%s:%s/0/config/set?emulate_motion=%s" % (options.host, options.port, state), auth=(options.user, options.password))
