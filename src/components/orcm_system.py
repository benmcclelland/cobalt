#!/usr/bin/env python
# $Id$

import sys

from Cobalt.Components.orcm_system import OrcmSystem
from Cobalt.Components.base import run_component

if __name__ == "__main__":
    try:
        run_component(OrcmSystem, register=True)
    except KeyboardInterrupt:
        sys.exit(1)
