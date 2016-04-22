#!/usr/bin/python3

import os
import sys
from flask import Flask  
from modules.phue import Bridge

# Default response
close_response = "<html><head><script>window.close();</script></head>Done!</html>"

# Get the configuration
from modules import configuration

# Intialize the bridge
bridge = Bridge(configuration['bridge']['ip'])
bridge.connect()

app = Flask(__name__)  

@app.route("/funkytown")  
def funkytown():
    bridge.set_light("Bedroom", {"on": True, "effect":"colorloop", "bri":254})
    return close_response

@app.route("/toggleall")
def toggleall():
    lights_on = not bridge.get_group("Living Room", "on")
    command =  {'transitiontime' : 0, 'on' : lights_on, 'bri' : 254, "ct":480}
    bridge.set_group("Kitchen", command)
    bridge.set_group("Living Room", command)
    return close_response

@app.route("/bedroom")
def bedroom():
    lights_on = not bridge.get_light("Bedroom", "on")
    bridge.set_light("Bedroom", {"on": lights_on, "bri": 254, "ct":480})
    return close_response

@app.route("/photo/<path:to_show>")
def show_photo(to_show):
    os.system("killall -9 c.py")
    pid = os.fork()
    if pid == 0:
        print("Child execing")
        script_location = os.path.dirname(os.path.realpath(__file__))
        os.chdir(script_location)
        photo_script = os.path.join(script_location, 'photo.sh')
        os.execl(photo_script, photo_script, "/photo/" + to_show)
        sys.exit(0)
    return "Running!"

if __name__ == "__main__":
    app.run('0.0.0.0', port=8080)
