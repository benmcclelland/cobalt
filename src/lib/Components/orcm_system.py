"""Hardware abstraction layer for the system on which process groups are run.

Classes:
ProcessGroup -- a group of processes started with mpirun
OrcmSystem -- ORCM system component
"""

import logging
import sys
import os
import ConfigParser
import Cobalt
import Cobalt.Data
import Cobalt.Util
from Cobalt.Components.base import exposed, automatic, query, locking
from Cobalt.Exceptions import ProcessGroupCreationError, ComponentLookupError
from Cobalt.Components.orcm_base_system import OrcmBaseSystem
from Cobalt.DataTypes.ProcessGroup import ProcessGroup
from Cobalt.Proxy import ComponentProxy
from Cobalt.Util import config_true_values


__all__ = [
    "OrcmProcessGroup",
    "OrcmSystem"
]

logger = logging.getLogger(__name__)

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


class OrcmProcessGroup(ProcessGroup):

    def __init__(self, spec):
        spec['forker'] = "user_script_forker"
        ProcessGroup.__init__(self, spec)
        self.nodefile = ""
        self.label = "%s/%s/%s" %(self.jobid, self.user, self.id)
        self.start()


    def prefork (self):
        ret = {}
        ret = ProcessGroup.prefork(self)

        sim_mode  = get_orcm_system_config("simulation_mode", 'false').lower() in config_true_values
        if not sim_mode:
            nodefile_dir = get_orcm_system_config("nodefile_dir", "/var/tmp")
            self.nodefile = os.path.join(nodefile_dir, "cobalt.%s" % self.jobid)
        else:
            self.nodefile = "fake"

        try:
            #This is the head node, return this to the user.
            rank0 = self.location[0].split(":")[0]
        except IndexError:
            raise ProcessGroupCreationError("no location")

        split_args = self.args
        cmd_args = ['--nf', str(self.nodefile),
                    '--jobid', str(self.jobid),
                    '--cwd', str(self.cwd),]

        qsub_env_list = ["%s=%s" % (key, val) for key, val in self.env.iteritems()]
        for env in qsub_env_list:
            cmd_args.extend(['--env', env])
        cmd_args.append(self.executable)

        cmd_exe = None
        if sim_mode:
            logger.debug("We are setting up with simulation mode.")
            cmd_exe = get_cluster_system_config("simulation_executable", None)
            if None == cmd_exe:
                logger.critical("Job: %s/%s: Executable for simulator not specified! This job will not run!")
                raise RuntimeError("Unspecified simulation_executable in cobalt config")
        else:
            cmd_exe = get_orcm_system_config('launcher','/usr/bin/cobalt-launcher.py')

        #run the user script off the login node, and on the compute node
        if (get_orcm_system_config("run_remote", 'true').lower() in config_true_values and not sim_mode):
            cmd = ("/usr/bin/ssh", rank0, cmd_exe, ) + tuple(cmd_args) + tuple(split_args)
        else:
            cmd = (cmd_exe,) + tuple(cmd_args) + tuple(split_args)

        ret["cmd" ] = cmd
        ret["args"] = cmd[1:]
        ret["executable"] = cmd[0]
        self.executable = ret["executable"]
        self.cmd = ret["cmd"]
        self.args = list(ret["args"])

        return ret

class OrcmSystem (OrcmBaseSystem):


    """ORCM system component.

    Methods:
    add_process_groups -- add (start) an mpirun process on the system (exposed, ~query)
    get_process_groups -- retrieve mpirun processes (exposed, query)
    wait_process_groups -- get process groups that have exited, and remove them from the system (exposed, query)
    signal_process_groups -- send a signal to the head process of the specified process groups (exposed, query)
    update_partition_state -- update partition state from the bridge API (runs as a thread)
    """

    name = "system"
    implementation = "orcm_system"

    logger = logger


    def __init__ (self, *args, **kwargs):
        OrcmBaseSystem.__init__(self, *args, **kwargs)
        self.process_groups.item_cls = OrcmProcessGroup

    def __del__ (self):
        OrcmBaseSystem.__del__(self)

    def __getstate__(self):
        state = {}
        state.update(OrcmBaseSystem.__getstate__(self))
        # state.update({
        #         "orcm_system_version": 1 })
        return state

    def __setstate__(self, state):
        OrcmBaseSystem.__setstate__(self, state)
        self.process_groups.item_cls = OrcmProcessGroup
    

    def add_process_groups (self, specs):
        """Create a process group.

        Arguments:
        spec -- dictionary hash specifying a process group to start
        """

        self.logger.info("add_process_groups(%r)", specs)
        process_groups = self.process_groups.q_add(specs)
        for pgroup in process_groups:
            self.logger.info("Job %s/%s: process group %s created to track script", pgroup.user, pgroup.jobid, pgroup.id)
        #System has started the job.  We need remove them from the temp, alloc array
        #in orcm_base_system.
        self.apg_started = True
        for pgroup in process_groups:
            for location in pgroup.location:
                try:
                    del self.alloc_only_nodes[location]
                except KeyError:
                    logger.critical("%s already removed from alloc_only_nodes list", location)
        return process_groups
    add_process_groups = exposed(query(add_process_groups))

    def get_process_groups (self, specs):
        self._get_exit_status()
        return self.process_groups.q_get(specs)
    get_process_groups = exposed(query(get_process_groups))

    def _get_exit_status (self):
        children = {}
        cleanup = {}
    _get_exit_status = automatic(_get_exit_status,
            float(get_orcm_system_config('get_exit_status_interval', 10)))

    def wait_process_groups (self, specs):
        process_groups = self.process_groups.q_get(specs)
        return process_groups
    wait_process_groups = locking(exposed(query(wait_process_groups)))

    def signal_process_groups (self, specs, signame="SIGINT"):
        my_process_groups = self.process_groups.q_get(specs)
        return my_process_groups
    signal_process_groups = exposed(query(signal_process_groups))

    def del_process_groups(self, jobid):
        '''delete a process group and don't track it anymore.

           jobid -- jobid associated with the process group we are removing

        '''
        del_items = self.process_groups.q_del([{'jobid':jobid}])
        if del_items == []:
            self.logger.warning("Job %s: Process group not found for this jobid.", jobid)
        else:
            self.logger.info("Job %s: Process group deleted.", jobid)
            return
