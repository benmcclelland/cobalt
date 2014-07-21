#! /usr/bin/env python
import sys
import Cobalt
import logging
import time
import signal
import Cobalt.Util
from Cobalt import client_utils
from Cobalt.client_utils import cb_debug

SYSMGR = client_utils.SYSMGR
args = {}
for s in sys.argv[1:]:
    key, value = s.split("=")
    args[key] = value

user = args["user"]
location = args["location"].split(":")
jobid = int(args["jobid"])
nodes = int(args["nodes"])
nodelist = ",".join(location)

client_utils.component_call(SYSMGR, False, 'launch_session', (jobid, nodes, nodelist, user))

sys.exit(0)
