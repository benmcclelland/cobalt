import testutils

# ---------------------------------------------------------------------------------
def test_qstat_version_option():
    """
    qstat test run: version_option

        Command Output:
        version: "qstat.py " + $Revision: 406 $ + , Cobalt  + $Version$
        
        Command Error/Debug:
        
    """

    args      = """--version"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_help_option():
    """
    qstat test run: help_option

        Command Output:
        Usage: qstat.py [options] <jobids1> ... <jobidsN>
        
        Options:
          --version             show program's version number and exit
          -h, --help            show this help message and exit
          -d, --debug           turn non communication debugging
          -f, --full            show more verbose information
          -l, --long            show job info in vertical format
          -Q                    show queues and properties
          --reverse             show output in reverse
          --header=HEADER       specify custom header
          --sort=SORT           sort output by specified attribute
          -u USER, --user=USER  Specify username
        
        Command Error/Debug:
        
    """

    args      = """-h"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_debug_only():
    """
    qstat test run: debug_only

        Command Output:
        JobID  User         WallTime  Nodes  State   Location  
        =======================================================
        5      georgerojas  02:45:00  30     queued  None      
        6      georgerojas  02:30:00  30     queued  None      
        7      georgerojas  02:30:00  30     queued  None      
        
        Command Error/Debug:
        qstat.py -d
        
        component: "queue-manager.get_queues", defer: True
          get_queues(
             [{'state': '*', 'name': '*'}],
             )
        
        
        component: "queue-manager.get_jobs", defer: False
          get_jobs(
             [{'timeremaining': '*', 'kernel': '*', 'errorpath': '*', 'kerneloptions': '*', 'args': '*', 'geometry': '*', 'maxtasktime': '*', 'admin_hold': '*', 'outputpath': '*', 'tag': 'job', 'notify': '*', 'user': '*', 'path': '*', 'outputdir': '*', 'procs': '*', 'walltime': '*', 'short_state': '*', 'index': '*', 'preemptable': '*', 'score': '*', 'envs': '*', 'project': '*', 'user_hold': '*', 'user_list': '*', 'queuedtime': '*', 'jobid': '*', 'queue': '*', 'submittime': '*', 'state': '*', 'dependencies': '*', 'command': '*', 'location': '*', 'starttime': '*', 'nodes': '*', 'runtime': '*', 'attrs': '*', 'dep_frac': '*', 'mode': '*'}],
             )
        
        
        
        
    """

    args      = """-d"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_full_option_10():
    """
    qstat test run: full_option_10

        Command Output:
        JobID  JobName  User         Score    WallTime  QueuedTime  RunTime  Nodes  State   Location  Mode  Procs  Queue    StartTime  
        ===============================================================================================================================
        6      -        georgerojas    0.9    02:30:00  00:01:38    N/A      30     queued  None      smp   30     default  N/A        
        7      -        georgerojas    0.9    02:30:00  00:01:38    N/A      30     queued  None      smp   30     default  N/A        
        5      -        georgerojas    1.0    02:45:00  00:01:42    N/A      30     queued  None      smp   30     default  N/A        
        
        Command Error/Debug:
        
    """

    args      = """-f"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_long_option_1():
    """
    qstat test run: long_option_1

        Command Output:
        JobID: 5
            User     : georgerojas
            WallTime : 02:45:00
            Nodes    : 30
            State    : queued
            Location : None
        
        JobID: 6
            User     : georgerojas
            WallTime : 02:30:00
            Nodes    : 30
            State    : queued
            Location : None
        
        JobID: 7
            User     : georgerojas
            WallTime : 02:30:00
            Nodes    : 30
            State    : queued
            Location : None
        
        
        Command Error/Debug:
        
    """

    args      = """-l"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_queue_option_3():
    """
    qstat test run: queue_option_3

        Command Output:
        Name     Users  MinTime  MaxTime  MaxRunning  MaxQueued  MaxUserNodes  MaxNodeHours  TotalNodes  State    
        ==========================================================================================================
        default  None   None     None     None        None       None          None          None        running  
        q_4      None   None     None     None        None       None          None          None        running  
        q_1      None   None     None     None        None       None          None          None        running  
        q_2      None   None     None     None        None       None          None          None        running  
        q_3      None   None     None     None        None       None          None          None        running  
        
        Command Error/Debug:
        
    """

    args      = """-f --sort users -Q"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_queue_option_4():
    """
    qstat test run: queue_option_4

        Command Output:
        Name     Users  MinTime  MaxTime  MaxRunning  MaxQueued  MaxUserNodes  MaxNodeHours  TotalNodes  State    
        ==========================================================================================================
        default  None   None     None     None        None       None          None          None        running  
        q_1      None   None     None     None        None       None          None          None        running  
        q_2      None   None     None     None        None       None          None          None        running  
        q_3      None   None     None     None        None       None          None          None        running  
        q_4      None   None     None     None        None       None          None          None        running  
        
        Command Error/Debug:
        
    """

    args      = """-Q"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_queue_option_5():
    """
    qstat test run: queue_option_5

        Command Output:
        Name     Users  MinTime  MaxTime  MaxRunning  MaxQueued  MaxUserNodes  MaxNodeHours  TotalNodes  State    
        ==========================================================================================================
        q_4      None   None     None     None        None       None          None          None        running  
        q_3      None   None     None     None        None       None          None          None        running  
        q_2      None   None     None     None        None       None          None          None        running  
        q_1      None   None     None     None        None       None          None          None        running  
        default  None   None     None     None        None       None          None          None        running  
        
        Command Error/Debug:
        
    """

    args      = """-Q --reverse"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_queue_option_6():
    """
    qstat test run: queue_option_6

        Command Output:
        Name     Users  MinTime  MaxTime  MaxRunning  MaxQueued  MaxUserNodes  MaxNodeHours  TotalNodes  State    
        ==========================================================================================================
        default  None   None     None     None        None       None          None          None        running  
        q_4      None   None     None     None        None       None          None          None        running  
        q_1      None   None     None     None        None       None          None          None        running  
        q_2      None   None     None     None        None       None          None          None        running  
        q_3      None   None     None     None        None       None          None          None        running  
        
        Command Error/Debug:
        
    """

    args      = """-Q --sort users"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_queue_option_7():
    """
    qstat test run: queue_option_7

        Command Output:
        Name     Users  MinTime  MaxTime  MaxRunning  MaxQueued  MaxUserNodes  MaxNodeHours  TotalNodes  State    
        ==========================================================================================================
        q_3      None   None     None     None        None       None          None          None        running  
        q_2      None   None     None     None        None       None          None          None        running  
        q_1      None   None     None     None        None       None          None          None        running  
        q_4      None   None     None     None        None       None          None          None        running  
        default  None   None     None     None        None       None          None          None        running  
        
        Command Error/Debug:
        
    """

    args      = """-Q --sort users --reverse"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_queue_option_8():
    """
    qstat test run: queue_option_8

        Command Output:
        Name: default
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_1
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_2
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_3
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_4
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        
        Command Error/Debug:
        
    """

    args      = """-Q -l"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_queue_option_9():
    """
    qstat test run: queue_option_9

        Command Output:
        Name: q_4
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_3
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_2
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_1
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: default
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        
        Command Error/Debug:
        
    """

    args      = """-Q --reverse -l"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_queue_option_10():
    """
    qstat test run: queue_option_10

        Command Output:
        Name: default
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_4
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_1
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_2
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_3
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        
        Command Error/Debug:
        
    """

    args      = """-Q --sort users -l"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_queue_option_11():
    """
    qstat test run: queue_option_11

        Command Output:
        Name: q_3
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_2
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_1
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: q_4
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        Name: default
            Users        : None
            MinTime      : None
            MaxTime      : None
            MaxRunning   : None
            MaxQueued    : None
            MaxUserNodes : None
            MaxNodeHours : None
            TotalNodes   : None
            State        : running
        
        
        Command Error/Debug:
        
    """

    args      = """-Q --sort users --reverse -l"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_queue_option_12():
    """
    qstat test run: queue_option_12

        Command Output:
        Name     Users  MinTime  MaxTime  MaxRunning  MaxQueued  MaxUserNodes  MaxNodeHours  TotalNodes  State    
        ==========================================================================================================
        default  None   None     None     None        None       None          None          None        running  
        q_1      None   None     None     None        None       None          None          None        running  
        q_2      None   None     None     None        None       None          None          None        running  
        q_3      None   None     None     None        None       None          None          None        running  
        q_4      None   None     None     None        None       None          None          None        running  
        
        Command Error/Debug:
        
    """

    args      = """-Q --header Jobid:State:RunTime"""
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg

# ---------------------------------------------------------------------------------
def test_qstat_no_arguments_or_options():
    """
    qstat test run: no_arguments_or_options

        Command Output:
        JobID  User         WallTime  Nodes  State   Location  
        =======================================================
        5      georgerojas  02:45:00  30     queued  None      
        6      georgerojas  02:30:00  30     queued  None      
        7      georgerojas  02:30:00  30     queued  None      
        
        Command Error/Debug:
        
    """

    args      = ''
    exp_rs    = 0

    results = testutils.run_cmd('qstat.py',args,None) 
    rs      = results[0]
    cmd_out = results[1]
    cmd_err = results[3]

    # Test Pass Criterias
    no_rs_err     = (rs == exp_rs)
    no_fatal_exc  = (cmd_out.find("FATAL EXCEPTION") == -1)

    result = no_rs_err and no_fatal_exc

    errmsg  = "\n\nFailed Data:\n\n" \
        "Return Status %s, Expected Return Status %s\n\n" \
        "Command Output:\n%s\n\n" \
        "Command Error:\n%s\n\n" \
        "Arguments: %s" % (str(rs), str(exp_rs), str(cmd_out), str(cmd_err), args)

    assert result, errmsg
