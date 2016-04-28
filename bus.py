#!/usr/bin/python

import time
import json
import urllib2
import datetime

now = datetime.datetime.now().time()

# http://webwatch.cityofmadison.com/webwatch/MobileAda.aspx?r=38&d=43&s=883

from modules import configuration

# Searching for the afternoon bus
if now.hour > 12:

    # Load the module we need to show the messages
    from pythonzenity import Warning as zWarning, Message as zMessage

    # Get the next arrivals
    buses = json.loads(urllib2.urlopen("http://api.smsmybus.com/v1/getarrivals?key=%s&stopID=0573&routeID=38" % configuration['smsmybus']['key']).read())

    # Go through the next buses on our route to arrive
    for bus in buses['stop']['route']:

        # Find the first bus going where we want
        if bus['destination'] == 'Buckeye:Jn Nolen:Oakrdg':

            # Check if the bus is on time
            if bus['arrivalTime'] == "3:09 pm":
                zMessage(text="Bus on time.", timeout=30000, width=1000, height=800)
            else:
                hour, minute = bus['arrivalTime'][0:bus['arrivalTime'].index(" ")].split(":")
                hour = int(hour) - 3
                minute = int(minute) - 9

                if hour != 0:
                    zWarning(text="The bus is more than an hour late, or something is wrong with the code.", timeout=120000, width=1000, height=800)
                else:
                    if minute < 1:
                        zWarning(text="The bus home is early? Bus will arrive " + str(-minute) + " minute early.", timeout=120000, width=1000, height=800)
                    elif minute == 1:
                        zWarning(text="The bus home will be later than normal. Arrival delayed by 1 minute.", timeout=120000, width=1000, height=800)
                    else:
                        zWarning(text="The bus home will be later than normal. Arrival delayed by " + str(minute) + " minutes.", timeout=120000, width=1000, height=800)

            # Don't alert about any bus but the first to arrive
            break

# Searching for the morning bus
else:
    # Load the phue code
    from modules.phue import Bridge

    # Get the next arrivals
    buses = json.loads(urllib2.urlopen("http://api.smsmybus.com/v1/getarrivals?key=%s&stopID=7215&routeID=38" % configuration['smsmybus']['key']).read())

    # Go the next bus to arrive
    minutes = int(buses['stop']['route'][0]['minutes'])

    # Connect to the bridge
    a = Bridge(configuration['bridge']['ip'])
    a.connect()

    # Wait until the right time to flash
    if minutes > 6:
		print "Waiting " + str(minutes-6) + " minutes before flash."
		time.sleep((int(minutes) - 6) * 60)

    # Turn the lights on
    command = {'transitiontime':0, 'on': True, 'bri':254}
    a.set_group(2, command)

    # Make them long flash
    a.set_group(2, 'alert', 'lselect')
    time.sleep(30)

    # Turn them off after a minute
    command = {'alert': 'none'}
    a.set_group(2, command)


