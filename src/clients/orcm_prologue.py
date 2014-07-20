#! /usr/bin/env python

import sys
import os
import ConfigParser
import Cobalt
import subprocess
import logging
import time
import signal
import Cobalt.Util
from ctypes import *

if "posix" in os.name:
    orcm = CDLL("liborcmapi.so", mode=ctypes.RTLD_GLOBAL)
else:
    orcm = CDLL("liborcmapi.so")

orcm.orcmapi_launch_session.argtypes = [c_int, c_int, c_char_p, c_char_p]
orcm.orcmapi_launch_session.argtypes.restype = c_int

logging.basicConfig(level=logging.INFO, format="%(message)s")

config = ConfigParser.ConfigParser()
config.read(Cobalt.CONFIG_FILES)

if not config.has_section('orcm_system'):
    print '''"ERROR: orcm_system" section missing from cobalt config file'''
    sys.exit(1)

def get_orcm_system_config(option, default):
    try:
        value = config.get('orcm_system', option)
    except ConfigParser.NoOptionError:
        value = default
    return value

sim_mode  = get_orcm_system_config("simulation_mode", 'false').lower() in Cobalt.Util.config_true_values

args = {}
for s in sys.argv[1:]:
    key, value = s.split("=")
    args[key] = value

if not sim_mode:
    nodefile_dir = get_cluster_system_config("nodefile_dir", "/var/tmp")
    nodefile = os.path.join(nodefile_dir, "cobalt.%s" % args['jobid'])
else:
    nodefile = "fake"

user = args["user"]
location = args["location"].split(":")
jobid = args["jobid"]
nodes = args["nodes"]

fd = open(nodefile, "w")
for host in location:
    fd.write(host + "\n")
fd.close()

nodelist = ",".join(location)

if sim_mode:
    sys.exit(0)

sys.exit(orcm.orcmapi_launch_session(jobid, nodes, nodelist, user))
