#!/usr/bin/python2.6
# $Id$

import sys

from Cobalt.Components.orcm_system import OrcmSystem
from Cobalt.Components.base import run_component

if __name__ == "__main__":
#    myorcm = OrcmSystem()
    try:
#        run_component(OrcmSystem, register=True, state_name="orcm_system")
        run_component(OrcmSystem, register=True)
    except KeyboardInterrupt:
        sys.exit(1)
