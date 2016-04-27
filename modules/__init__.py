# Get the configuration

import os
import json

spath =  os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "settings.json")
configuration = json.loads(open(spath, "r").read())
