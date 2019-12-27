agiza os
agiza sys
agiza threading

kutoka . agiza process
kutoka . agiza reduction

__all__ = ()

#
# Exceptions
#

kundi ProcessError(Exception):
    pass

kundi BufferTooShort(ProcessError):
    pass

kundi TimeoutError(ProcessError):
    pass

kundi AuthenticationError(ProcessError):
    pass

#
# Base type for contexts. Bound methods of an instance of this type are included in __all__ of __init__.py
#

kundi BaseContext(object):

    ProcessError = ProcessError
    BufferTooShort = BufferTooShort
    TimeoutError = TimeoutError
    AuthenticationError = AuthenticationError

    current_process = staticmethod(process.current_process)
    parent_process = staticmethod(process.parent_process)
    active_children = staticmethod(process.active_children)

    eleza cpu_count(self):
        '''Returns the number of CPUs in the system'''
        num = os.cpu_count()
        ikiwa num is None:
            raise NotImplementedError('cannot determine number of cpus')
        else:
            rudisha num

    eleza Manager(self):
        '''Returns a manager associated with a running server process

        The managers methods such as `Lock()`, `Condition()` and `Queue()`
        can be used to create shared objects.
        '''
        kutoka .managers agiza SyncManager
        m = SyncManager(ctx=self.get_context())
        m.start()
        rudisha m

    eleza Pipe(self, duplex=True):
        '''Returns two connection object connected by a pipe'''
        kutoka .connection agiza Pipe
        rudisha Pipe(duplex)

    eleza Lock(self):
        '''Returns a non-recursive lock object'''
        kutoka .synchronize agiza Lock
        rudisha Lock(ctx=self.get_context())

    eleza RLock(self):
        '''Returns a recursive lock object'''
        kutoka .synchronize agiza RLock
        rudisha RLock(ctx=self.get_context())

    eleza Condition(self, lock=None):
        '''Returns a condition object'''
        kutoka .synchronize agiza Condition
        rudisha Condition(lock, ctx=self.get_context())

    eleza Semaphore(self, value=1):
        '''Returns a semaphore object'''
        kutoka .synchronize agiza Semaphore
        rudisha Semaphore(value, ctx=self.get_context())

    eleza BoundedSemaphore(self, value=1):
        '''Returns a bounded semaphore object'''
        kutoka .synchronize agiza BoundedSemaphore
        rudisha BoundedSemaphore(value, ctx=self.get_context())

    eleza Event(self):
        '''Returns an event object'''
        kutoka .synchronize agiza Event
        rudisha Event(ctx=self.get_context())

    eleza Barrier(self, parties, action=None, timeout=None):
        '''Returns a barrier object'''
        kutoka .synchronize agiza Barrier
        rudisha Barrier(parties, action, timeout, ctx=self.get_context())

    eleza Queue(self, maxsize=0):
        '''Returns a queue object'''
        kutoka .queues agiza Queue
        rudisha Queue(maxsize, ctx=self.get_context())

    eleza JoinableQueue(self, maxsize=0):
        '''Returns a queue object'''
        kutoka .queues agiza JoinableQueue
        rudisha JoinableQueue(maxsize, ctx=self.get_context())

    eleza SimpleQueue(self):
        '''Returns a queue object'''
        kutoka .queues agiza SimpleQueue
        rudisha SimpleQueue(ctx=self.get_context())

    eleza Pool(self, processes=None, initializer=None, initargs=(),
             maxtasksperchild=None):
        '''Returns a process pool object'''
        kutoka .pool agiza Pool
        rudisha Pool(processes, initializer, initargs, maxtasksperchild,
                    context=self.get_context())

    eleza RawValue(self, typecode_or_type, *args):
        '''Returns a shared object'''
        kutoka .sharedctypes agiza RawValue
        rudisha RawValue(typecode_or_type, *args)

    eleza RawArray(self, typecode_or_type, size_or_initializer):
        '''Returns a shared array'''
        kutoka .sharedctypes agiza RawArray
        rudisha RawArray(typecode_or_type, size_or_initializer)

    eleza Value(self, typecode_or_type, *args, lock=True):
        '''Returns a synchronized shared object'''
        kutoka .sharedctypes agiza Value
        rudisha Value(typecode_or_type, *args, lock=lock,
                     ctx=self.get_context())

    eleza Array(self, typecode_or_type, size_or_initializer, *, lock=True):
        '''Returns a synchronized shared array'''
        kutoka .sharedctypes agiza Array
        rudisha Array(typecode_or_type, size_or_initializer, lock=lock,
                     ctx=self.get_context())

    eleza freeze_support(self):
        '''Check whether this is a fake forked process in a frozen executable.
        If so then run code specified by commandline and exit.
        '''
        ikiwa sys.platform == 'win32' and getattr(sys, 'frozen', False):
            kutoka .spawn agiza freeze_support
            freeze_support()

    eleza get_logger(self):
        '''Return package logger -- ikiwa it does not already exist then
        it is created.
        '''
        kutoka .util agiza get_logger
        rudisha get_logger()

    eleza log_to_stderr(self, level=None):
        '''Turn on logging and add a handler which prints to stderr'''
        kutoka .util agiza log_to_stderr
        rudisha log_to_stderr(level)

    eleza allow_connection_pickling(self):
        '''Install support for sending connections and sockets
        between processes
        '''
        # This is undocumented.  In previous versions of multiprocessing
        # its only effect was to make socket objects inheritable on Windows.
        kutoka . agiza connection

    eleza set_executable(self, executable):
        '''Sets the path to a python.exe or pythonw.exe binary used to run
        child processes instead of sys.executable when using the 'spawn'
        start method.  Useful for people embedding Python.
        '''
        kutoka .spawn agiza set_executable
        set_executable(executable)

    eleza set_forkserver_preload(self, module_names):
        '''Set list of module names to try to load in forkserver process.
        This is really just a hint.
        '''
        kutoka .forkserver agiza set_forkserver_preload
        set_forkserver_preload(module_names)

    eleza get_context(self, method=None):
        ikiwa method is None:
            rudisha self
        try:
            ctx = _concrete_contexts[method]
        except KeyError:
            raise ValueError('cannot find context for %r' % method) kutoka None
        ctx._check_available()
        rudisha ctx

    eleza get_start_method(self, allow_none=False):
        rudisha self._name

    eleza set_start_method(self, method, force=False):
        raise ValueError('cannot set start method of concrete context')

    @property
    eleza reducer(self):
        '''Controls how objects will be reduced to a form that can be
        shared with other processes.'''
        rudisha globals().get('reduction')

    @reducer.setter
    eleza reducer(self, reduction):
        globals()['reduction'] = reduction

    eleza _check_available(self):
        pass

#
# Type of default context -- underlying context can be set at most once
#

kundi Process(process.BaseProcess):
    _start_method = None
    @staticmethod
    eleza _Popen(process_obj):
        rudisha _default_context.get_context().Process._Popen(process_obj)

kundi DefaultContext(BaseContext):
    Process = Process

    eleza __init__(self, context):
        self._default_context = context
        self._actual_context = None

    eleza get_context(self, method=None):
        ikiwa method is None:
            ikiwa self._actual_context is None:
                self._actual_context = self._default_context
            rudisha self._actual_context
        else:
            rudisha super().get_context(method)

    eleza set_start_method(self, method, force=False):
        ikiwa self._actual_context is not None and not force:
            raise RuntimeError('context has already been set')
        ikiwa method is None and force:
            self._actual_context = None
            return
        self._actual_context = self.get_context(method)

    eleza get_start_method(self, allow_none=False):
        ikiwa self._actual_context is None:
            ikiwa allow_none:
                rudisha None
            self._actual_context = self._default_context
        rudisha self._actual_context._name

    eleza get_all_start_methods(self):
        ikiwa sys.platform == 'win32':
            rudisha ['spawn']
        else:
            ikiwa reduction.HAVE_SEND_HANDLE:
                rudisha ['fork', 'spawn', 'forkserver']
            else:
                rudisha ['fork', 'spawn']

#
# Context types for fixed start method
#

ikiwa sys.platform != 'win32':

    kundi ForkProcess(process.BaseProcess):
        _start_method = 'fork'
        @staticmethod
        eleza _Popen(process_obj):
            kutoka .popen_fork agiza Popen
            rudisha Popen(process_obj)

    kundi SpawnProcess(process.BaseProcess):
        _start_method = 'spawn'
        @staticmethod
        eleza _Popen(process_obj):
            kutoka .popen_spawn_posix agiza Popen
            rudisha Popen(process_obj)

    kundi ForkServerProcess(process.BaseProcess):
        _start_method = 'forkserver'
        @staticmethod
        eleza _Popen(process_obj):
            kutoka .popen_forkserver agiza Popen
            rudisha Popen(process_obj)

    kundi ForkContext(BaseContext):
        _name = 'fork'
        Process = ForkProcess

    kundi SpawnContext(BaseContext):
        _name = 'spawn'
        Process = SpawnProcess

    kundi ForkServerContext(BaseContext):
        _name = 'forkserver'
        Process = ForkServerProcess
        eleza _check_available(self):
            ikiwa not reduction.HAVE_SEND_HANDLE:
                raise ValueError('forkserver start method not available')

    _concrete_contexts = {
        'fork': ForkContext(),
        'spawn': SpawnContext(),
        'forkserver': ForkServerContext(),
    }
    ikiwa sys.platform == 'darwin':
        # bpo-33725: running arbitrary code after fork() is no longer reliable
        # on macOS since macOS 10.14 (Mojave). Use spawn by default instead.
        _default_context = DefaultContext(_concrete_contexts['spawn'])
    else:
        _default_context = DefaultContext(_concrete_contexts['fork'])

else:

    kundi SpawnProcess(process.BaseProcess):
        _start_method = 'spawn'
        @staticmethod
        eleza _Popen(process_obj):
            kutoka .popen_spawn_win32 agiza Popen
            rudisha Popen(process_obj)

    kundi SpawnContext(BaseContext):
        _name = 'spawn'
        Process = SpawnProcess

    _concrete_contexts = {
        'spawn': SpawnContext(),
    }
    _default_context = DefaultContext(_concrete_contexts['spawn'])

#
# Force the start method
#

eleza _force_start_method(method):
    _default_context._actual_context = _concrete_contexts[method]

#
# Check that the current thread is spawning a child process
#

_tls = threading.local()

eleza get_spawning_popen():
    rudisha getattr(_tls, 'spawning_popen', None)

eleza set_spawning_popen(popen):
    _tls.spawning_popen = popen

eleza assert_spawning(obj):
    ikiwa get_spawning_popen() is None:
        raise RuntimeError(
            '%s objects should only be shared between processes'
            ' through inheritance' % type(obj).__name__
            )
