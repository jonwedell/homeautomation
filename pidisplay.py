#!/usr/bin/env python2

import requests
from modules import pythonzenity
selection = pythonzenity.FileSelection(directory=True, multiple=False)
selection = selection.replace("/zdrive", "").replace('/NAS', '').replace('/remotePhoto', '/photo')
print "getting " + "http://raspberry:8080" + selection
requests.get("http://raspberry:8080" + selection)
