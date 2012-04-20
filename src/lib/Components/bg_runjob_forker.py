import copy
import ConfigParser
import logging
import os
import sys
import subprocess
import re
import Cobalt.Components.pg_forker
PGChild = Cobalt.Components.pg_forker.PGChild
PGForker = Cobalt.Components.pg_forker.PGForker

import Cobalt.Util
convert_argv_to_quoted_command_string = Cobalt.Util.convert_argv_to_quoted_command_string


_logger = logging.getLogger(__name__.split('.')[-1])

rpn_re  = re.compile(r'c(?P<pos>[0-9]*)') 

class _Config (object):
    _bgpm_configfields = ['runjob',]

    _config = ConfigParser.ConfigParser()
    _config.read(Cobalt.CONFIG_FILES)
    if not _config._sections.has_key('bgpm'):
        print '''"bgpm" section missing from cobalt config file'''
        sys.exit(1)

    bgpm = _config._sections['bgpm']
    _mfields = ['bgpm::%s' % (field,) for field in _bgpm_configfields if not bgpm.has_key(field)]

    if _mfields:
        print "Missing option(s) in cobalt config file: %s" % (" ".join(_mfields))
        sys.exit(1)

class BGRunjobChild (PGChild):
    def __init__(self, id = None, **kwargs):
        PGChild.__init__(self, id=id, **kwargs)

        try:
            self.bg_partition = self.pg.location[0]
        except IndexError:
            _logger.error("%s: no partition was specified", self.label)
            raise

    def __getstate__(self):
        state = {}
        state.update(PGChild.__getstate__(self))
        return state

    def __setstate__(self, state):
        PGChild.__setstate__(self, state)

    def preexec_first(self):
        PGChild.preexec_first(self)

        # FIXME: we really shouldn't be copying all of root's environment, should we?
        self.env = copy.deepcopy(os.environ)

        # export subset of MPIRUN_* variables to mpirun's environment
        # we explicitly state the ones we want since some are "dangerous"
        exportenv = [ 'MPIRUN_CONNECTION', 'MPIRUN_KERNEL_OPTIONS',
                      'MPIRUN_MAPFILE', 'MPIRUN_START_GDBSERVER',
                      'MPIRUN_LABEL', 'MPIRUN_NW', 'MPIRUN_VERBOSE',
                      'MPIRUN_ENABLE_TTY_REPORTING', 'MPIRUN_STRACE']

        app_envs = []
        set_label = False
        set_verbose = None
        for key, value in self.pg.env.iteritems():
            if key in exportenv:
    	        if key == 'MPIRUN_LABEL':
    	            set_label = True
    	        elif key == 'MPIRUN_VERBOSE':
    	            set_verbose = int(value)
                    postfork_env[key] = value
            else:
                app_envs.append((key, value))

        #we want this set to at least 32 MB.  Don't reset if the user has set it.  
        if 'BG_SHAREDMEMSIZE' not in self.pg.env.keys():
            _logger.debug("adding BG_SHAREDMEMSIZE=32.")
            app_envs.append(('BG_SHAREDMEMSIZE','32'))
        
        self.args = [_Config.bgpm['runjob'],
               '--np', str(int(self.pg.size)), #* int(rpn_re.match(pg.mode).groups()[0])),
               #'--block', pg.partition, #corner and shape derived from this.
               '--ranks-per-node', rpn_re.match(self.pg.mode).groups()[0], 
                    #default 1.  valid values are 2^n for n <= 6.
               '--cwd', self.pg.cwd]
        if self.pg.subblock:
            self.args.extend(['--block',self.pg.subblock_parent,
                        '--corner', self.pg.corner,
                        '--shape', "x".join([str(ext) for ext in self.pg.extents])
                        ])
        else:
            self.args.extend(['--block', self.bg_partition]) 
        if len(app_envs) > 0:
            for e in app_envs:
                self.args.extend(['--envs', ("%s=%s" % e)])
        #if self.pg.kerneloptions: FIXME: No kernel support yet
        #    cmd.extend(['-kernel_options', self.pg.kerneloptions])
        #munging for the "MPIRUN_LABEL" and the "MPIRUN_VERBOSE" fake envs.
        if set_label:
            self.args.extend(['--label', 'long'])
        if set_verbose != None:
            self.args.extend(['--verbose', str(set_verbose)])
        else:
            self.args.extend(['--verbose', '4'])
        #last append the binary and it's args:
        self.args.extend([':',self.pg.executable])
        if self.pg.args:
            self.args.extend(self.pg.args)

    def preexec_last(self):
        PGChild.preexec_last(self)


class BGRunjobForker (PGForker):
    
    """Component for starting runjob jobs on the BlueGene/Q
    
    """
    
    name = __name__.split('.')[-1]
    implementation = name

    child_cls = BGRunjobChild

    logger = _logger

    def __init__ (self, *args, **kwargs):
        """Initialize a new BG mpirun forker.
        
        All arguments are passed to the base forker constructor.
        """
        PGForker.__init__(self, *args, **kwargs)

    def __getstate__(self):
        return PGForker.__getstate__(self)

    def __setstate__(self, state):
        PGForker.__setstate__(self, state)