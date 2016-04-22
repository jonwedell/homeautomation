#!/usr/bin/python

import sys
from modules.phue import Bridge

# Get the configuration
from modules import configuration

my_bridge = Bridge(configuration['bridge']['ip'])
my_bridge.connect()

the_lights = my_bridge.lights

for light in the_lights:
	print light.name + ": " + {True:"On", False:"Off"}[light.on] + " " + str(float(light.brightness)/254*100) + "% " #+ str(light.xy)
        if len(sys.argv) > 1:
            if sys.argv[1] == "on":
                light.on = True
            if sys.argv[1] == "off":
                light.on = False

print "Daylight: " + str(my_bridge.get_api()['sensors']['1']['state']['daylight'])
