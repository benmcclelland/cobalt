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

jobid = int(args["jobid"])

client_utils.component_call(SYSMGR, False, 'cancel_session', (jobid))

sys.exit(0)
