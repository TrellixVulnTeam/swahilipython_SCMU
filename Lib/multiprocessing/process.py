#
# Module providing the `Process` kundi which emulates `threading.Thread`
#
# multiprocessing/process.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = ['BaseProcess', 'current_process', 'active_children',
           'parent_process']

#
# Imports
#

agiza os
agiza sys
agiza signal
agiza itertools
agiza threading
kutoka _weakrefset agiza WeakSet

#
#
#

jaribu:
    ORIGINAL_DIR = os.path.abspath(os.getcwd())
tatizo OSError:
    ORIGINAL_DIR = Tupu

#
# Public functions
#

eleza current_process():
    '''
    Return process object representing the current process
    '''
    rudisha _current_process

eleza active_children():
    '''
    Return list of process objects corresponding to live child processes
    '''
    _cleanup()
    rudisha list(_children)


eleza parent_process():
    '''
    Return process object representing the parent process
    '''
    rudisha _parent_process

#
#
#

eleza _cleanup():
    # check kila processes which have finished
    kila p kwenye list(_children):
        ikiwa p._popen.poll() ni sio Tupu:
            _children.discard(p)

#
# The `Process` class
#

kundi BaseProcess(object):
    '''
    Process objects represent activity that ni run kwenye a separate process

    The kundi ni analogous to `threading.Thread`
    '''
    eleza _Popen(self):
        ashiria NotImplementedError

    eleza __init__(self, group=Tupu, target=Tupu, name=Tupu, args=(), kwargs={},
                 *, daemon=Tupu):
        assert group ni Tupu, 'group argument must be Tupu kila now'
        count = next(_process_counter)
        self._identity = _current_process._identity + (count,)
        self._config = _current_process._config.copy()
        self._parent_pid = os.getpid()
        self._parent_name = _current_process.name
        self._popen = Tupu
        self._closed = Uongo
        self._target = target
        self._args = tuple(args)
        self._kwargs = dict(kwargs)
        self._name = name ama type(self).__name__ + '-' + \
                     ':'.join(str(i) kila i kwenye self._identity)
        ikiwa daemon ni sio Tupu:
            self.daemon = daemon
        _dangling.add(self)

    eleza _check_closed(self):
        ikiwa self._closed:
            ashiria ValueError("process object ni closed")

    eleza run(self):
        '''
        Method to be run kwenye sub-process; can be overridden kwenye sub-class
        '''
        ikiwa self._target:
            self._target(*self._args, **self._kwargs)

    eleza start(self):
        '''
        Start child process
        '''
        self._check_closed()
        assert self._popen ni Tupu, 'cannot start a process twice'
        assert self._parent_pid == os.getpid(), \
               'can only start a process object created by current process'
        assert sio _current_process._config.get('daemon'), \
               'daemonic processes are sio allowed to have children'
        _cleanup()
        self._popen = self._Popen(self)
        self._sentinel = self._popen.sentinel
        # Avoid a refcycle ikiwa the target function holds an indirect
        # reference to the process object (see bpo-30775)
        toa self._target, self._args, self._kwargs
        _children.add(self)

    eleza terminate(self):
        '''
        Terminate process; sends SIGTERM signal ama uses TerminateProcess()
        '''
        self._check_closed()
        self._popen.terminate()

    eleza kill(self):
        '''
        Terminate process; sends SIGKILL signal ama uses TerminateProcess()
        '''
        self._check_closed()
        self._popen.kill()

    eleza join(self, timeout=Tupu):
        '''
        Wait until child process terminates
        '''
        self._check_closed()
        assert self._parent_pid == os.getpid(), 'can only join a child process'
        assert self._popen ni sio Tupu, 'can only join a started process'
        res = self._popen.wait(timeout)
        ikiwa res ni sio Tupu:
            _children.discard(self)

    eleza is_alive(self):
        '''
        Return whether process ni alive
        '''
        self._check_closed()
        ikiwa self ni _current_process:
            rudisha Kweli
        assert self._parent_pid == os.getpid(), 'can only test a child process'

        ikiwa self._popen ni Tupu:
            rudisha Uongo

        returncode = self._popen.poll()
        ikiwa returncode ni Tupu:
            rudisha Kweli
        isipokua:
            _children.discard(self)
            rudisha Uongo

    eleza close(self):
        '''
        Close the Process object.

        This method releases resources held by the Process object.  It is
        an error to call this method ikiwa the child process ni still running.
        '''
        ikiwa self._popen ni sio Tupu:
            ikiwa self._popen.poll() ni Tupu:
                ashiria ValueError("Cannot close a process wakati it ni still running. "
                                 "You should first call join() ama terminate().")
            self._popen.close()
            self._popen = Tupu
            toa self._sentinel
            _children.discard(self)
        self._closed = Kweli

    @property
    eleza name(self):
        rudisha self._name

    @name.setter
    eleza name(self, name):
        assert isinstance(name, str), 'name must be a string'
        self._name = name

    @property
    eleza daemon(self):
        '''
        Return whether process ni a daemon
        '''
        rudisha self._config.get('daemon', Uongo)

    @daemon.setter
    eleza daemon(self, daemonic):
        '''
        Set whether process ni a daemon
        '''
        assert self._popen ni Tupu, 'process has already started'
        self._config['daemon'] = daemonic

    @property
    eleza authkey(self):
        rudisha self._config['authkey']

    @authkey.setter
    eleza authkey(self, authkey):
        '''
        Set authorization key of process
        '''
        self._config['authkey'] = AuthenticationString(authkey)

    @property
    eleza exitcode(self):
        '''
        Return exit code of process ama `Tupu` ikiwa it has yet to stop
        '''
        self._check_closed()
        ikiwa self._popen ni Tupu:
            rudisha self._popen
        rudisha self._popen.poll()

    @property
    eleza ident(self):
        '''
        Return identifier (PID) of process ama `Tupu` ikiwa it has yet to start
        '''
        self._check_closed()
        ikiwa self ni _current_process:
            rudisha os.getpid()
        isipokua:
            rudisha self._popen na self._popen.pid

    pid = ident

    @property
    eleza sentinel(self):
        '''
        Return a file descriptor (Unix) ama handle (Windows) suitable for
        waiting kila process termination.
        '''
        self._check_closed()
        jaribu:
            rudisha self._sentinel
        tatizo AttributeError:
            ashiria ValueError("process sio started") kutoka Tupu

    eleza __repr__(self):
        exitcode = Tupu
        ikiwa self ni _current_process:
            status = 'started'
        lasivyo self._closed:
            status = 'closed'
        lasivyo self._parent_pid != os.getpid():
            status = 'unknown'
        lasivyo self._popen ni Tupu:
            status = 'initial'
        isipokua:
            exitcode = self._popen.poll()
            ikiwa exitcode ni sio Tupu:
                status = 'stopped'
            isipokua:
                status = 'started'

        info = [type(self).__name__, 'name=%r' % self._name]
        ikiwa self._popen ni sio Tupu:
            info.append('pid=%s' % self._popen.pid)
        info.append('parent=%s' % self._parent_pid)
        info.append(status)
        ikiwa exitcode ni sio Tupu:
            exitcode = _exitcode_to_name.get(exitcode, exitcode)
            info.append('exitcode=%s' % exitcode)
        ikiwa self.daemon:
            info.append('daemon')
        rudisha '<%s>' % ' '.join(info)

    ##

    eleza _bootstrap(self, parent_sentinel=Tupu):
        kutoka . agiza util, context
        global _current_process, _parent_process, _process_counter, _children

        jaribu:
            ikiwa self._start_method ni sio Tupu:
                context._force_start_method(self._start_method)
            _process_counter = itertools.count(1)
            _children = set()
            util._close_stdin()
            old_process = _current_process
            _current_process = self
            _parent_process = _ParentProcess(
                self._parent_name, self._parent_pid, parent_sentinel)
            jaribu:
                util._finalizer_registry.clear()
                util._run_after_forkers()
            mwishowe:
                # delay finalization of the old process object until after
                # _run_after_forkers() ni executed
                toa old_process
            util.info('child process calling self.run()')
            jaribu:
                self.run()
                exitcode = 0
            mwishowe:
                util._exit_function()
        tatizo SystemExit kama e:
            ikiwa sio e.args:
                exitcode = 1
            lasivyo isinstance(e.args[0], int):
                exitcode = e.args[0]
            isipokua:
                sys.stderr.write(str(e.args[0]) + '\n')
                exitcode = 1
        tatizo:
            exitcode = 1
            agiza traceback
            sys.stderr.write('Process %s:\n' % self.name)
            traceback.print_exc()
        mwishowe:
            threading._shutdown()
            util.info('process exiting ukijumuisha exitcode %d' % exitcode)
            util._flush_std_streams()

        rudisha exitcode

#
# We subkundi bytes to avoid accidental transmission of auth keys over network
#

kundi AuthenticationString(bytes):
    eleza __reduce__(self):
        kutoka .context agiza get_spawning_popen
        ikiwa get_spawning_popen() ni Tupu:
            ashiria TypeError(
                'Pickling an AuthenticationString object ni '
                'disallowed kila security reasons'
                )
        rudisha AuthenticationString, (bytes(self),)


#
# Create object representing the parent process
#

kundi _ParentProcess(BaseProcess):

    eleza __init__(self, name, pid, sentinel):
        self._identity = ()
        self._name = name
        self._pid = pid
        self._parent_pid = Tupu
        self._popen = Tupu
        self._closed = Uongo
        self._sentinel = sentinel
        self._config = {}

    eleza is_alive(self):
        kutoka multiprocessing.connection agiza wait
        rudisha sio wait([self._sentinel], timeout=0)

    @property
    eleza ident(self):
        rudisha self._pid

    eleza join(self, timeout=Tupu):
        '''
        Wait until parent process terminates
        '''
        kutoka multiprocessing.connection agiza wait
        wait([self._sentinel], timeout=timeout)

    pid = ident

#
# Create object representing the main process
#

kundi _MainProcess(BaseProcess):

    eleza __init__(self):
        self._identity = ()
        self._name = 'MainProcess'
        self._parent_pid = Tupu
        self._popen = Tupu
        self._closed = Uongo
        self._config = {'authkey': AuthenticationString(os.urandom(32)),
                        'semprefix': '/mp'}
        # Note that some versions of FreeBSD only allow named
        # semaphores to have names of up to 14 characters.  Therefore
        # we choose a short prefix.
        #
        # On MacOSX kwenye a sandbox it may be necessary to use a
        # different prefix -- see #19478.
        #
        # Everything kwenye self._config will be inherited by descendant
        # processes.

    eleza close(self):
        pita


_parent_process = Tupu
_current_process = _MainProcess()
_process_counter = itertools.count(1)
_children = set()
toa _MainProcess

#
# Give names to some rudisha codes
#

_exitcode_to_name = {}

kila name, signum kwenye list(signal.__dict__.items()):
    ikiwa name[:3]=='SIG' na '_' haiko kwenye name:
        _exitcode_to_name[-signum] = f'-{name}'

# For debug na leak testing
_dangling = WeakSet()
