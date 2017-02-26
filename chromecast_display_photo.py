#!/usr/bin/env python2

from __future__ import print_function

import os
import sys
import time
import random
import socket
import SimpleHTTPServer
import SocketServer
from optparse import OptionParser

# Modules that are not guaranteed to be installed
try:
    import magic
except ImportError:
    print("Please run 'sudo pip install python-magic'.")
    sys.exit(1)

# Should exist as submodules here
import pychromecast as chromecast


# Specify some basic information about our command
parser = OptionParser(usage="usage: %prog", version="%prog 1",
                      description="Show photos on the photo display.")
parser.add_option("--time", action="store", dest="time", default=20,
                  type="int", help="The time to show each photo.")
parser.add_option("--order", action="store_true", dest="order",
                  default=False, help="Show the photos in order.")
parser.add_option("--chromecast", action="store", dest="chromecast", default="Living Room",
                  type="str", help="Which chromecast to show the photo on.")
parser.add_option("--port-range", action="store", dest="ports", default=(8000,9000),
                  type="int", nargs=2, help="Local ports to serve files from.")
parser.add_option("--verbose", action="store_true", default=False, 
                  dest="verbose", help="Be verbose.")

# Options, parse 'em
(options, selection) = parser.parse_args()

# They didn't specify a path on the command line, so import python-zenitys
if len(selection) == 0:
	from modules import pythonzenity
	selection = pythonzenity.FileSelection(directory=True, multiple=True)

if options.verbose:
	print("Loading list of files to show...")

# Enumerate the files
to_show = []
for adir in selection:
	for root, dirs, files in os.walk(adir):
		for _file in files:
			to_show.append(os.path.join(root, _file))
			#if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".JPEG") or file.endswith(".jpeg"):
			#	to_show.append("http://192.168.1.200/BDsYNs2A8egT1xNGyc4M6QixRbshxdVh/" + )
			#   to_show.append(root.split("photo/")[1] + _file)

if options.verbose:
	print("Connecting to Chromecast...")
my_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
cast = chromecast.get_chromecast(friendly_name=options.chromecast)
try:
	cast.wait()
	mc = cast.media_controller
except:
	valid = chromecast.get_chromecasts_as_dict().keys()
	print("The chromecast you specified wasn't located. Please chose "
	      "from the following Cast devices: '%s'" % "','".join(valid))
	sys.exit(2)

def serve_file(the_file, port):
    os.chdir(os.path.dirname(the_file))

    # Start the webserver
    child_pid = os.fork()

    if child_pid == 0:
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", port), Handler)
        httpd.timeout = 15
        httpd.handle_request()
        httpd.server_close()
        sys.exit(0)
    else:
        return child_pid

# Sort the files if in ordered mode
if options.order:
	curpos = 0
	to_show.sort()
	
# Get the first port
if not options.ports[0] < options.ports[1]:
	raise ValueError("You must specify at least 2 ports to use.")
port = options.ports[0]

# Go through the videos and show them
while True:
	
	if options.order:
		photo = to_show[curpos]
		curpos += 1
		if curpos >= len(to_show):
			curpos = 0
	else:
		photo = random.choice(to_show)
	    
	mime = magic.from_file(photo, mime=True)
	the_location = "http://%s:%s/%s" % (my_ip, port, os.path.basename(photo))
	try:
		server_pid = serve_file(photo, port)
	except socket.error:
		port += 1
		server_pid = serve_file(photo, port)
	print("Showing file (type: %s): %s" % (mime, the_location))
	mc.play_media(the_location, mime)
	# Wait the specified amount of time
	time.sleep(options.time)
	# By now the server should be done...
	os.wait()
	
	port += 1
	if port > options.ports[1]:
		port = options.ports[0]
