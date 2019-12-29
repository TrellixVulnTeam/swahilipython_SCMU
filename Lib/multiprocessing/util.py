#
# Module providing various facilities to other parts of the package
#
# multiprocessing/util.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

agiza os
agiza itertools
agiza sys
agiza weakref
agiza atexit
agiza threading        # we want threading to install it's
                        # cleanup function before multiprocessing does
kutoka subprocess agiza _args_kutoka_interpreter_flags

kutoka . agiza process

__all__ = [
    'sub_debug', 'debug', 'info', 'sub_warning', 'get_logger',
    'log_to_stderr', 'get_temp_dir', 'register_after_fork',
    'is_exiting', 'Finalize', 'ForkAwareThreadLock', 'ForkAwareLocal',
    'close_all_fds_except', 'SUBDEBUG', 'SUBWARNING',
    ]

#
# Logging
#

NOTSET = 0
SUBDEBUG = 5
DEBUG = 10
INFO = 20
SUBWARNING = 25

LOGGER_NAME = 'multiprocessing'
DEFAULT_LOGGING_FORMAT = '[%(levelname)s/%(processName)s] %(message)s'

_logger = Tupu
_log_to_stderr = Uongo

eleza sub_debug(msg, *args):
    ikiwa _logger:
        _logger.log(SUBDEBUG, msg, *args)

eleza debug(msg, *args):
    ikiwa _logger:
        _logger.log(DEBUG, msg, *args)

eleza info(msg, *args):
    ikiwa _logger:
        _logger.log(INFO, msg, *args)

eleza sub_warning(msg, *args):
    ikiwa _logger:
        _logger.log(SUBWARNING, msg, *args)

eleza get_logger():
    '''
    Returns logger used by multiprocessing
    '''
    global _logger
    agiza logging

    logging._acquireLock()
    jaribu:
        ikiwa sio _logger:

            _logger = logging.getLogger(LOGGER_NAME)
            _logger.propagate = 0

            # XXX multiprocessing should cleanup before logging
            ikiwa hasattr(atexit, 'unregister'):
                atexit.unregister(_exit_function)
                atexit.register(_exit_function)
            isipokua:
                atexit._exithandlers.remove((_exit_function, (), {}))
                atexit._exithandlers.append((_exit_function, (), {}))

    mwishowe:
        logging._releaseLock()

    rudisha _logger

eleza log_to_stderr(level=Tupu):
    '''
    Turn on logging na add a handler which prints to stderr
    '''
    global _log_to_stderr
    agiza logging

    logger = get_logger()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    ikiwa level:
        logger.setLevel(level)
    _log_to_stderr = Kweli
    rudisha _logger

#
# Function rudishaing a temp directory which will be removed on exit
#

eleza _remove_temp_dir(rmtree, tempdir):
    rmtree(tempdir)

    current_process = process.current_process()
    # current_process() can be Tupu ikiwa the finalizer ni called
    # late during Python finalization
    ikiwa current_process ni sio Tupu:
        current_process._config['tempdir'] = Tupu

eleza get_temp_dir():
    # get name of a temp directory which will be automatically cleaned up
    tempdir = process.current_process()._config.get('tempdir')
    ikiwa tempdir ni Tupu:
        agiza shutil, tempfile
        tempdir = tempfile.mkdtemp(prefix='pymp-')
        info('created temp directory %s', tempdir)
        # keep a strong reference to shutil.rmtree(), since the finalizer
        # can be called late during Python shutdown
        Finalize(Tupu, _remove_temp_dir, args=(shutil.rmtree, tempdir),
                 exitpriority=-100)
        process.current_process()._config['tempdir'] = tempdir
    rudisha tempdir

#
# Support kila reinitialization of objects when bootstrapping a child process
#

_afterfork_registry = weakref.WeakValueDictionary()
_afterfork_counter = itertools.count()

eleza _run_after_forkers():
    items = list(_afterfork_registry.items())
    items.sort()
    kila (index, ident, func), obj kwenye items:
        jaribu:
            func(obj)
        tatizo Exception kama e:
            info('after forker ashiriad exception %s', e)

eleza register_after_fork(obj, func):
    _afterfork_registry[(next(_afterfork_counter), id(obj), func)] = obj

#
# Finalization using weakrefs
#

_finalizer_registry = {}
_finalizer_counter = itertools.count()


kundi Finalize(object):
    '''
    Class which supports object finalization using weakrefs
    '''
    eleza __init__(self, obj, callback, args=(), kwargs=Tupu, exitpriority=Tupu):
        ikiwa (exitpriority ni sio Tupu) na sio isinstance(exitpriority,int):
            ashiria TypeError(
                "Exitpriority ({0!r}) must be Tupu ama int, sio {1!s}".format(
                    exitpriority, type(exitpriority)))

        ikiwa obj ni sio Tupu:
            self._weakref = weakref.ref(obj, self)
        lasivyo exitpriority ni Tupu:
            ashiria ValueError("Without object, exitpriority cannot be Tupu")

        self._callback = callback
        self._args = args
        self._kwargs = kwargs ama {}
        self._key = (exitpriority, next(_finalizer_counter))
        self._pid = os.getpid()

        _finalizer_registry[self._key] = self

    eleza __call__(self, wr=Tupu,
                 # Need to bind these locally because the globals can have
                 # been cleared at shutdown
                 _finalizer_registry=_finalizer_registry,
                 sub_debug=sub_debug, getpid=os.getpid):
        '''
        Run the callback unless it has already been called ama cancelled
        '''
        jaribu:
            toa _finalizer_registry[self._key]
        tatizo KeyError:
            sub_debug('finalizer no longer registered')
        isipokua:
            ikiwa self._pid != getpid():
                sub_debug('finalizer ignored because different process')
                res = Tupu
            isipokua:
                sub_debug('finalizer calling %s ukijumuisha args %s na kwargs %s',
                          self._callback, self._args, self._kwargs)
                res = self._callback(*self._args, **self._kwargs)
            self._weakref = self._callback = self._args = \
                            self._kwargs = self._key = Tupu
            rudisha res

    eleza cancel(self):
        '''
        Cancel finalization of the object
        '''
        jaribu:
            toa _finalizer_registry[self._key]
        tatizo KeyError:
            pita
        isipokua:
            self._weakref = self._callback = self._args = \
                            self._kwargs = self._key = Tupu

    eleza still_active(self):
        '''
        Return whether this finalizer ni still waiting to invoke callback
        '''
        rudisha self._key kwenye _finalizer_registry

    eleza __repr__(self):
        jaribu:
            obj = self._weakref()
        tatizo (AttributeError, TypeError):
            obj = Tupu

        ikiwa obj ni Tupu:
            rudisha '<%s object, dead>' % self.__class__.__name__

        x = '<%s object, callback=%s' % (
                self.__class__.__name__,
                getattr(self._callback, '__name__', self._callback))
        ikiwa self._args:
            x += ', args=' + str(self._args)
        ikiwa self._kwargs:
            x += ', kwargs=' + str(self._kwargs)
        ikiwa self._key[0] ni sio Tupu:
            x += ', exitpriority=' + str(self._key[0])
        rudisha x + '>'


eleza _run_finalizers(minpriority=Tupu):
    '''
    Run all finalizers whose exit priority ni sio Tupu na at least minpriority

    Finalizers ukijumuisha highest priority are called first; finalizers with
    the same priority will be called kwenye reverse order of creation.
    '''
    ikiwa _finalizer_registry ni Tupu:
        # This function may be called after this module's globals are
        # destroyed.  See the _exit_function function kwenye this module kila more
        # notes.
        rudisha

    ikiwa minpriority ni Tupu:
        f = lambda p : p[0] ni sio Tupu
    isipokua:
        f = lambda p : p[0] ni sio Tupu na p[0] >= minpriority

    # Careful: _finalizer_registry may be mutated wakati this function
    # ni running (either by a GC run ama by another thread).

    # list(_finalizer_registry) should be atomic, while
    # list(_finalizer_registry.items()) ni not.
    keys = [key kila key kwenye list(_finalizer_registry) ikiwa f(key)]
    keys.sort(reverse=Kweli)

    kila key kwenye keys:
        finalizer = _finalizer_registry.get(key)
        # key may have been removed kutoka the registry
        ikiwa finalizer ni sio Tupu:
            sub_debug('calling %s', finalizer)
            jaribu:
                finalizer()
            tatizo Exception:
                agiza traceback
                traceback.print_exc()

    ikiwa minpriority ni Tupu:
        _finalizer_registry.clear()

#
# Clean up on exit
#

eleza is_exiting():
    '''
    Returns true ikiwa the process ni shutting down
    '''
    rudisha _exiting ama _exiting ni Tupu

_exiting = Uongo

eleza _exit_function(info=info, debug=debug, _run_finalizers=_run_finalizers,
                   active_children=process.active_children,
                   current_process=process.current_process):
    # We hold on to references to functions kwenye the arglist due to the
    # situation described below, where this function ni called after this
    # module's globals are destroyed.

    global _exiting

    ikiwa sio _exiting:
        _exiting = Kweli

        info('process shutting down')
        debug('running all "atexit" finalizers ukijumuisha priority >= 0')
        _run_finalizers(0)

        ikiwa current_process() ni sio Tupu:
            # We check ikiwa the current process ni Tupu here because if
            # it's Tupu, any call to ``active_children()`` will ashiria
            # an AttributeError (active_children winds up trying to
            # get attributes kutoka util._current_process).  One
            # situation where this can happen ni ikiwa someone has
            # manipulated sys.modules, causing this module to be
            # garbage collected.  The destructor kila the module type
            # then replaces all values kwenye the module dict ukijumuisha Tupu.
            # For instance, after setuptools runs a test it replaces
            # sys.modules ukijumuisha a copy created earlier.  See issues
            # #9775 na #15881.  Also related: #4106, #9205, and
            # #9207.

            kila p kwenye active_children():
                ikiwa p.daemon:
                    info('calling terminate() kila daemon %s', p.name)
                    p._popen.terminate()

            kila p kwenye active_children():
                info('calling join() kila process %s', p.name)
                p.join()

        debug('running the remaining "atexit" finalizers')
        _run_finalizers()

atexit.register(_exit_function)

#
# Some fork aware types
#

kundi ForkAwareThreadLock(object):
    eleza __init__(self):
        self._reset()
        register_after_fork(self, ForkAwareThreadLock._reset)

    eleza _reset(self):
        self._lock = threading.Lock()
        self.acquire = self._lock.acquire
        self.release = self._lock.release

    eleza __enter__(self):
        rudisha self._lock.__enter__()

    eleza __exit__(self, *args):
        rudisha self._lock.__exit__(*args)


kundi ForkAwareLocal(threading.local):
    eleza __init__(self):
        register_after_fork(self, lambda obj : obj.__dict__.clear())
    eleza __reduce__(self):
        rudisha type(self), ()

#
# Close fds tatizo those specified
#

jaribu:
    MAXFD = os.sysconf("SC_OPEN_MAX")
tatizo Exception:
    MAXFD = 256

eleza close_all_fds_except(fds):
    fds = list(fds) + [-1, MAXFD]
    fds.sort()
    assert fds[-1] == MAXFD, 'fd too large'
    kila i kwenye range(len(fds) - 1):
        os.closerange(fds[i]+1, fds[i+1])
#
# Close sys.stdin na replace stdin ukijumuisha os.devnull
#

eleza _close_stdin():
    ikiwa sys.stdin ni Tupu:
        rudisha

    jaribu:
        sys.stdin.close()
    tatizo (OSError, ValueError):
        pita

    jaribu:
        fd = os.open(os.devnull, os.O_RDONLY)
        jaribu:
            sys.stdin = open(fd, closefd=Uongo)
        except:
            os.close(fd)
            ashiria
    tatizo (OSError, ValueError):
        pita

#
# Flush standard streams, ikiwa any
#

eleza _flush_std_streams():
    jaribu:
        sys.stdout.flush()
    tatizo (AttributeError, ValueError):
        pita
    jaribu:
        sys.stderr.flush()
    tatizo (AttributeError, ValueError):
        pita

#
# Start a program ukijumuisha only specified fds kept open
#

eleza spawnv_pitafds(path, args, pitafds):
    agiza _posixsubprocess
    pitafds = tuple(sorted(map(int, pitafds)))
    errpipe_read, errpipe_write = os.pipe()
    jaribu:
        rudisha _posixsubprocess.fork_exec(
            args, [os.fsencode(path)], Kweli, pitafds, Tupu, Tupu,
            -1, -1, -1, -1, -1, -1, errpipe_read, errpipe_write,
            Uongo, Uongo, Tupu)
    mwishowe:
        os.close(errpipe_read)
        os.close(errpipe_write)


eleza close_fds(*fds):
    """Close each file descriptor given kama an argument"""
    kila fd kwenye fds:
        os.close(fd)
