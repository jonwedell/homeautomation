#!/usr/bin/env python2

import os
import sys
import time
import socket
try:
    import magic
except ImportError:
    print "Please run 'sudo pip install python-magic'."
    sys.exit(1)
import SimpleHTTPServer
import SocketServer
from modules import pythonzenity

try:
    import pychromecast as chromecast
except ImportError:
    print "Please run 'sudo pip install pychromecast."
    sys.exit(2)

selection = pythonzenity.FileSelection(multiple=True)
print selection

#chromecast.get_chromecasts_as_dict().keys()

print "Connecting to Chromecast..."

my_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
cast = chromecast.get_chromecast(friendly_name="Living Room")
cast.wait()
mc = cast.media_controller

def serve_file(the_file, port=8000):
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


port = 8000
for vid in selection:
    
    mime = magic.from_file(vid, mime=True)
    the_location = "http://" + my_ip + ":" + str(port) + "/" + os.path.basename(vid)
    server_pid = serve_file(vid, port)
    print the_location, mime
    mc.play_media(the_location, mime)
    os.wait()
    port += 1
