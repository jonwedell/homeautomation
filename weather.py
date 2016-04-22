#!/usr/bin/python

import os
import sys
import json
import time
import urllib2
import datetime
from modules.phue import Bridge
import xml.etree.ElementTree as ET

# Fetch the configuration
from modules import configuration
bridge_ip = configuration['bridge']['ip']
configuration = configuration['weather']

# Configuration
red = [0.674,0.322]
blue = [.1691, .0441]
weather_xml = "http://w1.weather.gov/xml/current_obs/%(citycode)s.xml" % configuration
weather_json = "http://api.openweathermap.org/data/2.5/forecast/city?id=%(cityid)s&APPID=%(key)s" % configuration

# Get rid of the unicode in the bulbs
configuration['bulbs'] = [x.encode() for x in configuration['bulbs']]

# Set up connection to Hue
my_bridge = Bridge(bridge_ip)
my_bridge.connect()

try:
    if len(sys.argv) > 1:
        temp_f = float(sys.argv[1])

    elif configuration['simple']:

        # Fetch the weather as XML
        weather = ET.fromstring(urllib2.urlopen(weather_xml).read())

        # Get the temperature
        temp_f = float(weather.findall('temp_f')[0].text)

    else:
        # Fetch the weather as JSON
        weather_data = urllib2.urlopen(weather_json).read()
        weather = json.loads(weather_data)

        # Calculate the average temperature over the next 12 hours
        avg_list = []
        for prediction in weather['list']:
            if prediction['dt'] < time.time() + 12*60*60:
                avg_list.append(prediction['main']['temp'])

        temp_f = sum(avg_list)/len(avg_list) * 9/5 - 459.67
        open(os.path.join(configuration['records_dir'], str(time.time())), "w").write(str(temp_f))

    # Calculate what color the bulb should be
    relative_temp = (float(temp_f) - configuration['cold']) / (configuration['hot'] - configuration['cold'])
    if relative_temp > 1:
        relative_temp = 1
    if relative_temp < 0:
        relative_temp = 0
    color = [relative_temp*(red[0]-blue[0]) + blue[0], relative_temp*(red[1]-blue[1]) + blue[1]]

# Set light to white if no access to weather
except Exception as e:
    print str(e)
    if datetime.datetime.today().weekday() < 5:
        command =  {'transitiontime' : 0, 'on' : True, 'bri' : 254, 'ct': 153}
        my_bridge.set_light(configuration['bulbs'], command)
    sys.exit(0)

# Set lights to color calculated from weather - if it isn't a weekend
if datetime.datetime.today().weekday() < 5:
    command =  {'transitiontime' : 0, 'on' : True, 'bri' : 254, 'xy': color}
    my_bridge.set_light(configuration['bulbs'], command)

