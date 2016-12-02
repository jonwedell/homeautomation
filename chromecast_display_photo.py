#!/usr/bin/env python2

import os
import sys
import time
import random
from optparse import OptionParser
from modules import pythonzenity

try:
    import pychromecast as chromecast
except ImportError:
    print "Please run 'sudo pip install pychromecast."
    sys.exit(2)


# Todo: Show based on mime type
# Todo: implement local sever

# Specify some basic information about our command
parser = OptionParser(usage="usage: %prog",version="%prog 1",description="Show photos on the photo display.")
parser.add_option("--time", action="store", dest="time", default=20, type="int", help="The time to show each photo.")
parser.add_option("--order", action="store_true", dest="order", default=False, help="Show the photos in order.")
parser.add_option("--chromecast", action="store", dest="chromecast", default="Living Room", type="str", help="Which chromecast to show the photo on.")

# Options, parse 'em
(options, selection) = parser.parse_args()

if len(selection) == 0:
	selection = pythonzenity.FileSelection(directory=True, multiple=True)

to_show = []

print "Loading list of files to show..."

# Get the 
for adir in selection:
	for root, dirs, files in os.walk(adir):
		for file in files:
			if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".JPEG") or file.endswith(".jpeg"):
				to_show.append("http://192.168.1.200/BDsYNs2A8egT1xNGyc4M6QixRbshxdVh/" + root.split("photo/")[1] + "/" + file)

print "Connecting to Chromecast..."

cast = chromecast.get_chromecast(friendly_name=options.chromecast)
cast.wait()
mc = cast.media_controller

if options.order:
	curpos = 0
	to_show.sort()

while True:
	if options.order:
		photo = to_show[curpos]
		curpos += 1
		if curpos >= len(to_show):
			curpos = 0
	else:
		photo = random.choice(to_show)
	print "Showing: " + photo
	mc.play_media(photo, "image/jpeg")
	time.sleep(options.time)
