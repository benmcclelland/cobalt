"""Hardware abstraction layer for the system on which process groups are run.

Classes:
OrcmBaseSystem -- base system component
"""

import time
import sys
import Cobalt
import pwd
import grp
import ConfigParser
import os
import ctypes
import Cobalt.Util
from ctypes import *
from Cobalt.Exceptions import  JobValidationError, NotSupportedError, ComponentLookupError
from Cobalt.DataTypes.ProcessGroup import ProcessGroupDict
from Cobalt.Data import DataDict
from Cobalt.Proxy import ComponentProxy
from Cobalt.Components.base import Component, exposed, automatic
from Cobalt.Util import config_true_values

STRING = c_char_p
int8_t = c_int8
orcm_node_state_t = int8_t

class liborcm_node_t (Structure):
    _fields_ = [
        ('name', STRING),
        ('state', orcm_node_state_t),
    ]

__all__ = [
    "OrcmBaseSystem", "orcm_node_state_t", "liborcm_node_t", "int8_t",
]

ORCM_NODE_STATE_UNDEF   = 0
ORCM_NODE_STATE_UNKNOWN = 1
ORCM_NODE_STATE_UP      = 2
ORCM_NODE_STATE_DOWN    = 3
ORCM_NODE_STATE_SESTERM = 4

if "posix" in os.name:
    orcm = CDLL("liborcmapi.so", mode=ctypes.RTLD_GLOBAL)
else:
    orcm = CDLL("liborcmapi.so")

P_node_t = POINTER(liborcm_node_t)
PP_node_t = POINTER(P_node_t)
orcm.orcmapi_init.argtypes = []
orcm.orcmapi_init.restype = c_int
orcm.orcmapi_finalize.argtypes = []
orcm.orcmapi_finalize.restype = c_int
orcm.orcmapi_get_nodes.argtypes = [POINTER(PP_node_t), POINTER(c_int)]
orcm.orcmapi_get_nodes.restype = c_int

__config = ConfigParser.ConfigParser()
__config.read(Cobalt.CONFIG_FILES)

if not __config.has_section('orcm_system'):
    print '''"ERROR: orcm_system" section missing from cobalt config file'''
    sys.exit(1)

def get_orcm_system_config(option, default):
    try:
        value = __config.get('orcm_system', option)
    except ConfigParser.NoOptionError:
        value = default
    return value

class OrcmNode(object):

    def __init__(self, name):

        self.name = name
        self.running = False
        self.down = False
        self.queues = None
        self.allocated = False
        self.cleaning = False
        self.cleaning_process = None
        self.assigned_jobid = None
        self.alloc_timeout = None
        self.alloc_start = None
        self.assigned_user = None

    def allocate(self, jobid, user, time=None):

        self.alloc_timeout = 300
        if time == None:
            self.alloc_start = time.time()
        else:
            self.alloc_start = time
        self.allocated = True
        self.assigned_user = user
        self.assigned_jobid = jobid

    def start_running(self):
        self.running = True

    def stop_running(self):

        self.running = False
        self.cleaning = True
        #invoke cleanup

    def deallocate(self):

        self.assigned_user = None
        self.assigned_jobid = None
        self.alloc_timeout = None
        self.alloc_start = None
        self.allocated = False

    def mark_up(self):
        self.down = False

    def mark_down (self):
        self.down = True



class OrcmNodeDict(DataDict):
    '''default container for OrcmNode information

       keyed by node name
    '''
    item_cls = OrcmNode
    key = "name"

class OrcmBaseSystem (Component):
    """base system class.

    Methods:
    add_partitions -- tell the system to manage partitions (exposed, query)
    get_partitions -- retrieve partitions in the simulator (exposed, query)
    del_partitions -- tell the system not to manage partitions (exposed, query)
    set_partitions -- change random attributes of partitions (exposed, query)
    update_relatives -- should be called when partitions are added and removed from the managed list
    """

    def __init__ (self, *args, **kwargs):
        orcm.orcmapi_init()
        Component.__init__(self, *args, **kwargs)
        self.process_groups = ProcessGroupDict()
        self.all_nodes = set()
        self.running_nodes = set()
        self.down_nodes = set()
        self.queue_assignments = {}
        self.node_order = {}

        self.configure()
        
        self.queue_assignments["default"] = set(self.all_nodes)
        self.alloc_only_nodes = {} # nodename:starttime
        self.cleaning_processes = []
        #keep track of which jobs still have hosts being cleaned
        self.cleaning_host_count = {} # jobid:count
        self.locations_by_jobid = {} #jobid:[locations]
        self.jobid_to_user = {} #jobid:username

        self.alloc_timeout = int(get_orcm_system_config("allocation_timeout", 300))

        self.logger.info("allocation timeout set to %d seconds." % self.alloc_timeout)

    def __del__(self):
        orcm.orcmapi_finalize()
    
    def __getstate__(self):
        state = {}
        state.update(Component.__getstate__(self))
        state.update({
                "orcm_base_version": 1,
                "queue_assignments": self.queue_assignments,
                "down_nodes": self.down_nodes })
        return state

    def __setstate__(self, state):
        Component.__setstate__(self, state)
        self.all_nodes = set()
        self.node_order = {}
        self.configure()
        self.queue_assignments = state.get('queue_assignments', {})
        nonexistent_queues = []
        #make sure we can't try and schedule nodes that don't exist
        if self.queue_assignments == {}:
            self.queue_assignments["default"] = set(self.all_nodes)
        else:
            #remove nodes that have disappeared
            for queue, nodes in self.queue_assignments.iteritems():
                corrected_nodes = self.all_nodes & set(nodes)
                if corrected_nodes == set():
                    nonexistent_queues.append(queue)
                self.queue_assignments[queue] = corrected_nodes
            for queue in nonexistent_queues:
                del self.queue_assignments[queue]
        self.down_nodes = self.all_nodes & set(state.get('down_nodes', set()))
        self.process_groups = ProcessGroupDict()
        self.running_nodes = set()
        self.alloc_only_nodes = {} # nodename:starttime
        if not state.has_key("cleaning_processes"):
            self.cleaning_processes = []
        self.cleaning_host_count = {} # jobid:count
        self.locations_by_jobid = {} #jobid:[locations]
        self.jobid_to_user = {} #jobid:username

        self.alloc_timeout = int(get_orcm_system_config("allocation_timeout", 300))
        self.logger.info("allocation timeout set to %d seconds." % self.alloc_timeout)

    def save_me(self):
        '''Automatically write statefiles.'''
        Component.save(self)
    save_me = automatic(save_me)


    def validate_job(self, spec):
        """validate a job for submission

        Arguments:
        spec -- job specification dictionary
        """
        # spec has {nodes, walltime*, procs, mode, kernel}

        max_nodes = len(self.all_nodes)
        sys_type = 'orcm'
        job_types = ['co','vn','smp','dual','script']
        spec['mode'] = 'script'
        try:
            spec['nodecount'] = int(spec['nodecount'])
        except:
            raise JobValidationError("Non-integer node count")
        if not 0 < spec['nodecount'] <= max_nodes:
            raise JobValidationError("Node count out of realistic range")
        if float(spec['time']) < 5 and float(spec['time']) > 0:
            raise JobValidationError("Walltime less than minimum")
        if spec['mode'] not in job_types:
            raise JobValidationError("%s is an invalid mode" % spec['mode'])
        if not spec['proccount']:
            spec['proccount'] = spec['nodecount']
        else:
            try:
                spec['proccount'] = int(spec['proccount'])
            except:
                JobValidationError("non-integer proccount")
            if spec['proccount'] < 1:
                raise JobValidationError("negative proccount")
            if spec['proccount'] > spec['nodecount']:
                if spec['mode'] not in ['vn', 'dual']:
                    raise JobValidationError("proccount too large")
        # need to handle kernel
        return spec
    validate_job = exposed(validate_job)


    def fail_partitions(self, specs):
        self.logger.error("Fail_partitions not used on orcm systems.")
        return ""
    fail_partitions = exposed(fail_partitions)

    def unfail_partitions(self, specs):
        self.logger.error("unfail_partitions not used on orcm systems.")
        return ""
    unfail_partitions = exposed(unfail_partitions)

    def _find_job_location(self, args):
        '''Get a list of nodes capable of running a job.

        '''
        nodes = args['nodes']
        jobid = args['jobid']

        available_nodes = self._get_available_nodes(args)

        if nodes <= len(available_nodes):
            return {jobid: [available_nodes.pop() for i in range(nodes)]}
        else:
            return None

    def _get_available_nodes(self, args):
        '''Get all nodes required for a job, ignoring forbidden ones (i.e. reserved nodes).

        '''
        queue = args['queue']
        forbidden = args.get("forbidden", [])
        required = args.get("required", [])

        if required:
            available_nodes = set(required)
        else:
            available_nodes = self.queue_assignments[queue].difference(forbidden)

        available_nodes = available_nodes.difference(self.running_nodes)
        available_nodes = available_nodes.difference(self.down_nodes)

        return available_nodes

    def _backfill_cmp(self, left, right):
        return cmp(left[1], right[1])

    # the argument "required" is used to pass in the set of locations allowed by a reservation;
    def find_job_location(self, arg_list, end_times):
        '''Find the best location for a job and start the job allocation process

        '''
        best_location_dict = {}
        winner = arg_list[0]

        jobid = None
        user = None

        # first time through, try for starting jobs based on utility scores
        for args in arg_list:
            location_data = self._find_job_location(args)
            if location_data:
                best_location_dict.update(location_data)
                jobid = int(args['jobid'])
                user = args['user']
                break

        # the next time through, try to backfill, but only if we couldn't find anything to start
        if not best_location_dict:
            job_end_times = {}
            total = 0
            for item in sorted(end_times, cmp=self._backfill_cmp):
                total += len(item[0])
                job_end_times[total] = item[1]

            needed = winner['nodes'] - len(self._get_available_nodes(winner))
            now = time.time()
            backfill_cutoff = 0
            for num in sorted(job_end_times):
                if needed <= num:
                    backfill_cutoff = job_end_times[num] - now

            for args in arg_list:
                if 60*float(args['walltime']) > backfill_cutoff:
                    continue

                location_data = self._find_job_location(args)
                if location_data:
                    best_location_dict.update(location_data)
                    self.logger.info("backfilling job %s" % args['jobid'])
                    jobid = int(args['jobid'])
                    user = args['user']
                    break

        # reserve the stuff in the best_partition_dict, as those partitions are allegedly going to
        # be running jobs very soon
        for jobid_str, location_list in best_location_dict.iteritems():
            self.running_nodes.update(location_list)
            self.logger.info("Job %s: Allocating nodes: %s" % (int(jobid_str), location_list))
            #just in case we're not going to be running a job soon, and have to
            #return this to the pool:
            self.jobid_to_user[jobid] = user
            alloc_time = time.time()
            for location in location_list:
                self.alloc_only_nodes[location] = alloc_time
            self.locations_by_jobid[jobid] = location_list


        return best_location_dict
    find_job_location = exposed(find_job_location)

    def check_alloc_only_nodes(self):
        '''Check to see if nodes that we have allocated but not run yet should be freed.

        '''
        jobids = []
        check_time = time.time()
        dead_locations = []
        for location, start_time in self.alloc_only_nodes.iteritems():
            if int(check_time) - int(start_time) > self.alloc_timeout:
                self.logger.warning("Location: %s: released.  Time between allocation and run exceeded.", location)
                dead_locations.append(location)

        if dead_locations == []:
                    #well we don't have anything dying this time.
            return

        for jobid, locations in self.locations_by_jobid.iteritems():
            clear_from_dead_locations = False
            for location in locations:
                if location in dead_locations:
                    clear_from_dead_locations = True
                    if jobid not in jobids:
                        jobids.append(jobid)
            #bagging the jobid will cause all locs assoc with job to be
            #cleaned so clear them out to make this faster
            if clear_from_dead_locations:
                for location in locations:
                    if location in dead_locations:
                        dead_locations.remove(location)
            if dead_locations == []:
                #well we don't have anything dying this time.
                break
        self.invoke_node_cleanup(jobids)
        return


    check_alloc_only_nodes = automatic(check_alloc_only_nodes, get_orcm_system_config("automatic_method_interval", 10.0))

    def invoke_node_cleanup(self, jobids):
        '''Invoke cleanup for nodes that have exceeded their allocated time

        '''
        found_locations = set()
        for jobid in jobids:
            user = self.jobid_to_user[jobid]
            locations = self.locations_by_jobid[jobid]
            locations_to_clean = set()
            for location in locations:
                if location not in found_locations:
                    try:
                        del self.alloc_only_nodes[location]
                    except KeyError:
                        self.logger.warning('WANING: Location: %s Jobid: %s; Location already removed from alloc_only_nodes',
                            location, jobid)
                    else:
                        locations_to_clean.add(location)
                        found_locations.add(location)

#            self.clean_nodes(list(locations_to_clean), user, jobid)


    def _walltimecmp(self, dict1, dict2):
        return -cmp(float(dict1['walltime']), float(dict2['walltime']))


    def find_queue_equivalence_classes(self, reservation_dict, active_queue_names, passthrough_partitions=[]):
        '''Take a dictionary of reservation information and a list of active
            queues return a list of dictionaries containing queues, partition
            associations and reservation data.
            
            Input:
            reservation_dict: A dict of reservations and associated partitions
            active_queue_names: A list of queues that you can schedule jobs from
            passthrough_partitions: not used in this implementation
            
            Output:
            A dictionary of queues and associated reservations that have resources
            in common with each other
            
        '''
        
        equiv = []
        for q in self.queue_assignments:
            # skip queues that aren't "running"
            if not q in active_queue_names:
                continue

            found_a_match = False
            for e in equiv:
                if e['data'].intersection(self.queue_assignments[q]):
                    e['queues'].add(q)
                    e['data'].update(self.queue_assignments[q])
                    found_a_match = True
                    break
            if not found_a_match:
                equiv.append( { 'queues': set([q]), 'data': set(self.queue_assignments[q]), 'reservations': set() } )


        real_equiv = []
        for eq_class in equiv:
            found_a_match = False
            for e in real_equiv:
                if e['queues'].intersection(eq_class['queues']):
                    e['queues'].update(eq_class['queues'])
                    e['data'].update(eq_class['data'])
                    found_a_match = True
                    break
            if not found_a_match:
                real_equiv.append(eq_class)

        equiv = real_equiv

        for eq_class in equiv:
            for res_name in reservation_dict:
                skip = True
                for host_name in reservation_dict[res_name].split(":"):
                    if host_name in eq_class['data']:
                        eq_class['reservations'].add(res_name)

            for key in eq_class:
                eq_class[key] = list(eq_class[key])
            del eq_class['data']

        return equiv
    find_queue_equivalence_classes = exposed(find_queue_equivalence_classes)

    def reserve_resources_until(self, location, time, jobid):
        '''hold onto resources until a timeout has passed, and then clear the
        nodes for another job.

        '''

        #WARNING: THIS IS VERY DIFFERENT FROM BLUE GENES!
        #THIS WILL FORCIBLY CLEAR THE NODE!

        if time is None:
            for host in location:
                self.running_nodes.discard(host)
                self.logger.info("hasty job kill: freeing %s" % host)
        else:
            self.logger.error("failed to reserve location '%r' until '%s'" % (location, time))
            return True #So we can progress.
    reserve_resources_until = exposed(reserve_resources_until)


    def nodes_up(self, node_list, user_name=None):
        changed = []
        for n in node_list:
            if n in self.down_nodes:
                self.down_nodes.remove(n)
                changed.append(n)
            if n in self.running_nodes:
                self.running_nodes.remove(n)
                changed.append(n)
        if changed:
            self.logger.info("%s marking nodes up: %s", user_name, ", ".join(changed))
        return changed
    nodes_up = exposed(nodes_up)


    def nodes_down(self, node_list, user_name=None):
        changed = []
        for n in node_list:
            if n in self.all_nodes:
                self.down_nodes.add(n)
                changed.append(n)
        if changed:
            self.logger.info("%s marking nodes down: %s", user_name, ", ".join(changed))
        return changed
    nodes_down = exposed(nodes_down)

    def get_node_status(self):
        def my_cmp(left, right):
            return cmp(left[2], right[2])

        self.configure()
        status_list = []
        for n in self.all_nodes:
            if n in self.running_nodes:
                status = "allocated"
            elif n in self.down_nodes:
                status = "down"
            else:
                status = "idle"

            status_list.append( (n, status, self.node_order[n]) )
        status_list.sort(my_cmp)
        return status_list
    get_node_status = exposed(get_node_status)

    def get_queue_assignments(self):
        ret = {}
        for q in self.queue_assignments:
            ret[q] = list(self.queue_assignments[q])
        return ret
    get_queue_assignments = exposed(get_queue_assignments)

    def set_queue_assignments(self, queue_names, node_list, user_name=None):
        checked_nodes = set()
        for n in node_list:
            if n in self.all_nodes:
                checked_nodes.add(n)

        queue_list = queue_names.split(":")
        for q in queue_list:
            if q not in self.queue_assignments:
                self.queue_assignments[q] = set()

        for q in self.queue_assignments.keys():
            if q not in queue_list:
                self.queue_assignments[q].difference_update(checked_nodes)
                if len(self.queue_assignments[q])==0:
                    del self.queue_assignments[q]
            else:
                self.queue_assignments[q].update(checked_nodes)
        self.logger.info("%s assigning queues %s to nodes %s", user_name, queue_names, " ".join(checked_nodes))
        return list(checked_nodes)
    set_queue_assignments = exposed(set_queue_assignments)

    def verify_locations(self, location_list):
        """Providing a system agnostic interface for making sure a 'location string' is valid"""
        ret = []
        for l in location_list:
            if l in self.all_nodes:
                ret.append(l)
        return ret
    verify_locations = exposed(verify_locations)

    def configure(self):
        '''Add nodes from ORCM to Cobalt's configuration of tracked nodes.
        '''
        nodelist = PP_node_t()
        node_count = c_int(0)
        counter = 0
        orcm.orcmapi_get_nodes(byref(nodelist), byref(node_count))
        self.down_nodes.clear()
        for i in range(node_count.value):
            name = nodelist[i].contents.name
            state = nodelist[i].contents.state
            self.all_nodes.add(name)
            self.node_order[name] = counter
            if (state == ORCM_NODE_STATE_UNKNOWN) or (state == ORCM_NODE_STATE_DOWN):
                self.down_nodes.add(name)
            counter += 1

    # this gets called by bgsched in order to figure out if there are partition overlaps;
    # it was written to provide the data that bgsched asks for and raises an exception
    # if you try to ask for more
    def get_partitions (self, specs):
        '''Fetch node information and their respective states.

        '''
        partitions = []
        for spec in specs:
            item = {}
            for node in self.all_nodes:
                if "name" in spec:
                    if spec["name"] == '*':
                        item.update( {"name": node} )
                    elif spec["name"] == node:
                        item.update( {"name": node} )

            if "name" in spec:
                spec.pop("name")
            if "children" in spec:
                item.update( {"children": []} )
                spec.pop("children")
            if "parents" in spec:
                item.update( {"parents": []} )
                spec.pop("parents")
            if spec:
                raise NotSupportedError("orcm clusters lack information on: %s" % ", ".join(spec.keys()))
            if item:
                partitions.append(item)

        return partitions
    get_partitions = exposed(get_partitions)


    def launch_script(self, config_option, host, jobid, user, group_name):
        '''Start our script processes used for node prep and cleanup.

        '''
        #TODO: ORCM_launch


    def del_process_groups(self, jobid):
        '''Set actions to take when deleting process groups.  This must be
        overridden in the implementation.

        '''
        raise NotImplementedError("Must be overridden in child class")
