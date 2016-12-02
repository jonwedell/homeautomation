#!/usr/bin/env python2

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

def get_average_temperature(cur_temp):
    temps = []
    
    # Only get the last number of records as specified in the config
    records = sorted(os.listdir(configuration['records_dir']))[-configuration['days']:]
    
    # Go through the records and read the temps
    for record in records:
        if os.path.isfile(os.path.join(configuration['records_dir'], record)):
            with open(os.path.join(configuration['records_dir'], record), "r") as f:
                try:
                    temps.append(float(f.read()))
                except ValueError:
                    pass
                
    # Return the current temperature if there are no records
    try:
        return sum(temps) / float(len(temps))
    except ZeroDivisionError:
        return cur_temp

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
    temp_diff_from_avg = temp_f - get_average_temperature(temp_f)
    relative_temp = (float(temp_diff_from_avg) - configuration['cold']) / (configuration['hot'] - configuration['cold'])
    
    if relative_temp > 1:
        relative_temp = 1
    if relative_temp < 0:
        relative_temp = 0

    # Scale from .15 to .65
    x_color = relative_temp * .5 + .175
    # The following is a custom parabola to generate good colors
    y_color = -float(246)*x_color**2/91 + float(5183)*x_color/1820 - float(1901)/5200
#-(float(1130)*(x_color**2)/399) + (float(1551)*x_color/532) -(float(1703)/4560)

    # Graph the calculated color
    color = [x_color, y_color]
    print color

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


