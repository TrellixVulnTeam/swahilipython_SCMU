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

try:
    ORIGINAL_DIR = os.path.abspath(os.getcwd())
except OSError:
    ORIGINAL_DIR = None

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
    # check for processes which have finished
    for p in list(_children):
        ikiwa p._popen.poll() is not None:
            _children.discard(p)

#
# The `Process` class
#

kundi BaseProcess(object):
    '''
    Process objects represent activity that is run in a separate process

    The kundi is analogous to `threading.Thread`
    '''
    eleza _Popen(self):
        raise NotImplementedError

    eleza __init__(self, group=None, target=None, name=None, args=(), kwargs={},
                 *, daemon=None):
        assert group is None, 'group argument must be None for now'
        count = next(_process_counter)
        self._identity = _current_process._identity + (count,)
        self._config = _current_process._config.copy()
        self._parent_pid = os.getpid()
        self._parent_name = _current_process.name
        self._popen = None
        self._closed = False
        self._target = target
        self._args = tuple(args)
        self._kwargs = dict(kwargs)
        self._name = name or type(self).__name__ + '-' + \
                     ':'.join(str(i) for i in self._identity)
        ikiwa daemon is not None:
            self.daemon = daemon
        _dangling.add(self)

    eleza _check_closed(self):
        ikiwa self._closed:
            raise ValueError("process object is closed")

    eleza run(self):
        '''
        Method to be run in sub-process; can be overridden in sub-class
        '''
        ikiwa self._target:
            self._target(*self._args, **self._kwargs)

    eleza start(self):
        '''
        Start child process
        '''
        self._check_closed()
        assert self._popen is None, 'cannot start a process twice'
        assert self._parent_pid == os.getpid(), \
               'can only start a process object created by current process'
        assert not _current_process._config.get('daemon'), \
               'daemonic processes are not allowed to have children'
        _cleanup()
        self._popen = self._Popen(self)
        self._sentinel = self._popen.sentinel
        # Avoid a refcycle ikiwa the target function holds an indirect
        # reference to the process object (see bpo-30775)
        del self._target, self._args, self._kwargs
        _children.add(self)

    eleza terminate(self):
        '''
        Terminate process; sends SIGTERM signal or uses TerminateProcess()
        '''
        self._check_closed()
        self._popen.terminate()

    eleza kill(self):
        '''
        Terminate process; sends SIGKILL signal or uses TerminateProcess()
        '''
        self._check_closed()
        self._popen.kill()

    eleza join(self, timeout=None):
        '''
        Wait until child process terminates
        '''
        self._check_closed()
        assert self._parent_pid == os.getpid(), 'can only join a child process'
        assert self._popen is not None, 'can only join a started process'
        res = self._popen.wait(timeout)
        ikiwa res is not None:
            _children.discard(self)

    eleza is_alive(self):
        '''
        Return whether process is alive
        '''
        self._check_closed()
        ikiwa self is _current_process:
            rudisha True
        assert self._parent_pid == os.getpid(), 'can only test a child process'

        ikiwa self._popen is None:
            rudisha False

        returncode = self._popen.poll()
        ikiwa returncode is None:
            rudisha True
        else:
            _children.discard(self)
            rudisha False

    eleza close(self):
        '''
        Close the Process object.

        This method releases resources held by the Process object.  It is
        an error to call this method ikiwa the child process is still running.
        '''
        ikiwa self._popen is not None:
            ikiwa self._popen.poll() is None:
                raise ValueError("Cannot close a process while it is still running. "
                                 "You should first call join() or terminate().")
            self._popen.close()
            self._popen = None
            del self._sentinel
            _children.discard(self)
        self._closed = True

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
        Return whether process is a daemon
        '''
        rudisha self._config.get('daemon', False)

    @daemon.setter
    eleza daemon(self, daemonic):
        '''
        Set whether process is a daemon
        '''
        assert self._popen is None, 'process has already started'
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
        Return exit code of process or `None` ikiwa it has yet to stop
        '''
        self._check_closed()
        ikiwa self._popen is None:
            rudisha self._popen
        rudisha self._popen.poll()

    @property
    eleza ident(self):
        '''
        Return identifier (PID) of process or `None` ikiwa it has yet to start
        '''
        self._check_closed()
        ikiwa self is _current_process:
            rudisha os.getpid()
        else:
            rudisha self._popen and self._popen.pid

    pid = ident

    @property
    eleza sentinel(self):
        '''
        Return a file descriptor (Unix) or handle (Windows) suitable for
        waiting for process termination.
        '''
        self._check_closed()
        try:
            rudisha self._sentinel
        except AttributeError:
            raise ValueError("process not started") kutoka None

    eleza __repr__(self):
        exitcode = None
        ikiwa self is _current_process:
            status = 'started'
        elikiwa self._closed:
            status = 'closed'
        elikiwa self._parent_pid != os.getpid():
            status = 'unknown'
        elikiwa self._popen is None:
            status = 'initial'
        else:
            exitcode = self._popen.poll()
            ikiwa exitcode is not None:
                status = 'stopped'
            else:
                status = 'started'

        info = [type(self).__name__, 'name=%r' % self._name]
        ikiwa self._popen is not None:
            info.append('pid=%s' % self._popen.pid)
        info.append('parent=%s' % self._parent_pid)
        info.append(status)
        ikiwa exitcode is not None:
            exitcode = _exitcode_to_name.get(exitcode, exitcode)
            info.append('exitcode=%s' % exitcode)
        ikiwa self.daemon:
            info.append('daemon')
        rudisha '<%s>' % ' '.join(info)

    ##

    eleza _bootstrap(self, parent_sentinel=None):
        kutoka . agiza util, context
        global _current_process, _parent_process, _process_counter, _children

        try:
            ikiwa self._start_method is not None:
                context._force_start_method(self._start_method)
            _process_counter = itertools.count(1)
            _children = set()
            util._close_stdin()
            old_process = _current_process
            _current_process = self
            _parent_process = _ParentProcess(
                self._parent_name, self._parent_pid, parent_sentinel)
            try:
                util._finalizer_registry.clear()
                util._run_after_forkers()
            finally:
                # delay finalization of the old process object until after
                # _run_after_forkers() is executed
                del old_process
            util.info('child process calling self.run()')
            try:
                self.run()
                exitcode = 0
            finally:
                util._exit_function()
        except SystemExit as e:
            ikiwa not e.args:
                exitcode = 1
            elikiwa isinstance(e.args[0], int):
                exitcode = e.args[0]
            else:
                sys.stderr.write(str(e.args[0]) + '\n')
                exitcode = 1
        except:
            exitcode = 1
            agiza traceback
            sys.stderr.write('Process %s:\n' % self.name)
            traceback.print_exc()
        finally:
            threading._shutdown()
            util.info('process exiting with exitcode %d' % exitcode)
            util._flush_std_streams()

        rudisha exitcode

#
# We subkundi bytes to avoid accidental transmission of auth keys over network
#

kundi AuthenticationString(bytes):
    eleza __reduce__(self):
        kutoka .context agiza get_spawning_popen
        ikiwa get_spawning_popen() is None:
            raise TypeError(
                'Pickling an AuthenticationString object is '
                'disallowed for security reasons'
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
        self._parent_pid = None
        self._popen = None
        self._closed = False
        self._sentinel = sentinel
        self._config = {}

    eleza is_alive(self):
        kutoka multiprocessing.connection agiza wait
        rudisha not wait([self._sentinel], timeout=0)

    @property
    eleza ident(self):
        rudisha self._pid

    eleza join(self, timeout=None):
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
        self._parent_pid = None
        self._popen = None
        self._closed = False
        self._config = {'authkey': AuthenticationString(os.urandom(32)),
                        'semprefix': '/mp'}
        # Note that some versions of FreeBSD only allow named
        # semaphores to have names of up to 14 characters.  Therefore
        # we choose a short prefix.
        #
        # On MacOSX in a sandbox it may be necessary to use a
        # different prefix -- see #19478.
        #
        # Everything in self._config will be inherited by descendant
        # processes.

    eleza close(self):
        pass


_parent_process = None
_current_process = _MainProcess()
_process_counter = itertools.count(1)
_children = set()
del _MainProcess

#
# Give names to some rudisha codes
#

_exitcode_to_name = {}

for name, signum in list(signal.__dict__.items()):
    ikiwa name[:3]=='SIG' and '_' not in name:
        _exitcode_to_name[-signum] = f'-{name}'

# For debug and leak testing
_dangling = WeakSet()
