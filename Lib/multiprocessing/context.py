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
    pita

kundi BufferTooShort(ProcessError):
    pita

kundi TimeoutError(ProcessError):
    pita

kundi AuthenticationError(ProcessError):
    pita

#
# Base type kila contexts. Bound methods of an instance of this type are included kwenye __all__ of __init__.py
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
        '''Returns the number of CPUs kwenye the system'''
        num = os.cpu_count()
        ikiwa num ni Tupu:
            ashiria NotImplementedError('cannot determine number of cpus')
        isipokua:
            rudisha num

    eleza Manager(self):
        '''Returns a manager associated ukijumuisha a running server process

        The managers methods such kama `Lock()`, `Condition()` na `Queue()`
        can be used to create shared objects.
        '''
        kutoka .managers agiza SyncManager
        m = SyncManager(ctx=self.get_context())
        m.start()
        rudisha m

    eleza Pipe(self, duplex=Kweli):
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

    eleza Condition(self, lock=Tupu):
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

    eleza Barrier(self, parties, action=Tupu, timeout=Tupu):
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

    eleza Pool(self, processes=Tupu, initializer=Tupu, initargs=(),
             maxtasksperchild=Tupu):
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

    eleza Value(self, typecode_or_type, *args, lock=Kweli):
        '''Returns a synchronized shared object'''
        kutoka .sharedctypes agiza Value
        rudisha Value(typecode_or_type, *args, lock=lock,
                     ctx=self.get_context())

    eleza Array(self, typecode_or_type, size_or_initializer, *, lock=Kweli):
        '''Returns a synchronized shared array'''
        kutoka .sharedctypes agiza Array
        rudisha Array(typecode_or_type, size_or_initializer, lock=lock,
                     ctx=self.get_context())

    eleza freeze_support(self):
        '''Check whether this ni a fake forked process kwenye a frozen executable.
        If so then run code specified by commandline na exit.
        '''
        ikiwa sys.platform == 'win32' na getattr(sys, 'frozen', Uongo):
            kutoka .spawn agiza freeze_support
            freeze_support()

    eleza get_logger(self):
        '''Return package logger -- ikiwa it does sio already exist then
        it ni created.
        '''
        kutoka .util agiza get_logger
        rudisha get_logger()

    eleza log_to_stderr(self, level=Tupu):
        '''Turn on logging na add a handler which prints to stderr'''
        kutoka .util agiza log_to_stderr
        rudisha log_to_stderr(level)

    eleza allow_connection_pickling(self):
        '''Install support kila sending connections na sockets
        between processes
        '''
        # This ni undocumented.  In previous versions of multiprocessing
        # its only effect was to make socket objects inheritable on Windows.
        kutoka . agiza connection

    eleza set_executable(self, executable):
        '''Sets the path to a python.exe ama pythonw.exe binary used to run
        child processes instead of sys.executable when using the 'spawn'
        start method.  Useful kila people embedding Python.
        '''
        kutoka .spawn agiza set_executable
        set_executable(executable)

    eleza set_forkserver_preload(self, module_names):
        '''Set list of module names to try to load kwenye forkserver process.
        This ni really just a hint.
        '''
        kutoka .forkserver agiza set_forkserver_preload
        set_forkserver_preload(module_names)

    eleza get_context(self, method=Tupu):
        ikiwa method ni Tupu:
            rudisha self
        jaribu:
            ctx = _concrete_contexts[method]
        tatizo KeyError:
            ashiria ValueError('cannot find context kila %r' % method) kutoka Tupu
        ctx._check_available()
        rudisha ctx

    eleza get_start_method(self, allow_none=Uongo):
        rudisha self._name

    eleza set_start_method(self, method, force=Uongo):
        ashiria ValueError('cannot set start method of concrete context')

    @property
    eleza reducer(self):
        '''Controls how objects will be reduced to a form that can be
        shared ukijumuisha other processes.'''
        rudisha globals().get('reduction')

    @reducer.setter
    eleza reducer(self, reduction):
        globals()['reduction'] = reduction

    eleza _check_available(self):
        pita

#
# Type of default context -- underlying context can be set at most once
#

kundi Process(process.BaseProcess):
    _start_method = Tupu
    @staticmethod
    eleza _Popen(process_obj):
        rudisha _default_context.get_context().Process._Popen(process_obj)

kundi DefaultContext(BaseContext):
    Process = Process

    eleza __init__(self, context):
        self._default_context = context
        self._actual_context = Tupu

    eleza get_context(self, method=Tupu):
        ikiwa method ni Tupu:
            ikiwa self._actual_context ni Tupu:
                self._actual_context = self._default_context
            rudisha self._actual_context
        isipokua:
            rudisha super().get_context(method)

    eleza set_start_method(self, method, force=Uongo):
        ikiwa self._actual_context ni sio Tupu na sio force:
            ashiria RuntimeError('context has already been set')
        ikiwa method ni Tupu na force:
            self._actual_context = Tupu
            rudisha
        self._actual_context = self.get_context(method)

    eleza get_start_method(self, allow_none=Uongo):
        ikiwa self._actual_context ni Tupu:
            ikiwa allow_none:
                rudisha Tupu
            self._actual_context = self._default_context
        rudisha self._actual_context._name

    eleza get_all_start_methods(self):
        ikiwa sys.platform == 'win32':
            rudisha ['spawn']
        isipokua:
            ikiwa reduction.HAVE_SEND_HANDLE:
                rudisha ['fork', 'spawn', 'forkserver']
            isipokua:
                rudisha ['fork', 'spawn']

#
# Context types kila fixed start method
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
            ikiwa sio reduction.HAVE_SEND_HANDLE:
                ashiria ValueError('forkserver start method sio available')

    _concrete_contexts = {
        'fork': ForkContext(),
        'spawn': SpawnContext(),
        'forkserver': ForkServerContext(),
    }
    ikiwa sys.platform == 'darwin':
        # bpo-33725: running arbitrary code after fork() ni no longer reliable
        # on macOS since macOS 10.14 (Mojave). Use spawn by default instead.
        _default_context = DefaultContext(_concrete_contexts['spawn'])
    isipokua:
        _default_context = DefaultContext(_concrete_contexts['fork'])

isipokua:

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
# Check that the current thread ni spawning a child process
#

_tls = threading.local()

eleza get_spawning_popen():
    rudisha getattr(_tls, 'spawning_popen', Tupu)

eleza set_spawning_popen(popen):
    _tls.spawning_popen = popen

eleza assert_spawning(obj):
    ikiwa get_spawning_popen() ni Tupu:
        ashiria RuntimeError(
            '%s objects should only be shared between processes'
            ' through inheritance' % type(obj).__name__
            )
