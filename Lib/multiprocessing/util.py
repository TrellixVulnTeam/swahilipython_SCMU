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

_logger = None
_log_to_stderr = False

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
    try:
        ikiwa not _logger:

            _logger = logging.getLogger(LOGGER_NAME)
            _logger.propagate = 0

            # XXX multiprocessing should cleanup before logging
            ikiwa hasattr(atexit, 'unregister'):
                atexit.unregister(_exit_function)
                atexit.register(_exit_function)
            else:
                atexit._exithandlers.remove((_exit_function, (), {}))
                atexit._exithandlers.append((_exit_function, (), {}))

    finally:
        logging._releaseLock()

    rudisha _logger

eleza log_to_stderr(level=None):
    '''
    Turn on logging and add a handler which prints to stderr
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
    _log_to_stderr = True
    rudisha _logger

#
# Function returning a temp directory which will be removed on exit
#

eleza _remove_temp_dir(rmtree, tempdir):
    rmtree(tempdir)

    current_process = process.current_process()
    # current_process() can be None ikiwa the finalizer is called
    # late during Python finalization
    ikiwa current_process is not None:
        current_process._config['tempdir'] = None

eleza get_temp_dir():
    # get name of a temp directory which will be automatically cleaned up
    tempdir = process.current_process()._config.get('tempdir')
    ikiwa tempdir is None:
        agiza shutil, tempfile
        tempdir = tempfile.mkdtemp(prefix='pymp-')
        info('created temp directory %s', tempdir)
        # keep a strong reference to shutil.rmtree(), since the finalizer
        # can be called late during Python shutdown
        Finalize(None, _remove_temp_dir, args=(shutil.rmtree, tempdir),
                 exitpriority=-100)
        process.current_process()._config['tempdir'] = tempdir
    rudisha tempdir

#
# Support for reinitialization of objects when bootstrapping a child process
#

_afterfork_registry = weakref.WeakValueDictionary()
_afterfork_counter = itertools.count()

eleza _run_after_forkers():
    items = list(_afterfork_registry.items())
    items.sort()
    for (index, ident, func), obj in items:
        try:
            func(obj)
        except Exception as e:
            info('after forker raised exception %s', e)

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
    eleza __init__(self, obj, callback, args=(), kwargs=None, exitpriority=None):
        ikiwa (exitpriority is not None) and not isinstance(exitpriority,int):
            raise TypeError(
                "Exitpriority ({0!r}) must be None or int, not {1!s}".format(
                    exitpriority, type(exitpriority)))

        ikiwa obj is not None:
            self._weakref = weakref.ref(obj, self)
        elikiwa exitpriority is None:
            raise ValueError("Without object, exitpriority cannot be None")

        self._callback = callback
        self._args = args
        self._kwargs = kwargs or {}
        self._key = (exitpriority, next(_finalizer_counter))
        self._pid = os.getpid()

        _finalizer_registry[self._key] = self

    eleza __call__(self, wr=None,
                 # Need to bind these locally because the globals can have
                 # been cleared at shutdown
                 _finalizer_registry=_finalizer_registry,
                 sub_debug=sub_debug, getpid=os.getpid):
        '''
        Run the callback unless it has already been called or cancelled
        '''
        try:
            del _finalizer_registry[self._key]
        except KeyError:
            sub_debug('finalizer no longer registered')
        else:
            ikiwa self._pid != getpid():
                sub_debug('finalizer ignored because different process')
                res = None
            else:
                sub_debug('finalizer calling %s with args %s and kwargs %s',
                          self._callback, self._args, self._kwargs)
                res = self._callback(*self._args, **self._kwargs)
            self._weakref = self._callback = self._args = \
                            self._kwargs = self._key = None
            rudisha res

    eleza cancel(self):
        '''
        Cancel finalization of the object
        '''
        try:
            del _finalizer_registry[self._key]
        except KeyError:
            pass
        else:
            self._weakref = self._callback = self._args = \
                            self._kwargs = self._key = None

    eleza still_active(self):
        '''
        Return whether this finalizer is still waiting to invoke callback
        '''
        rudisha self._key in _finalizer_registry

    eleza __repr__(self):
        try:
            obj = self._weakref()
        except (AttributeError, TypeError):
            obj = None

        ikiwa obj is None:
            rudisha '<%s object, dead>' % self.__class__.__name__

        x = '<%s object, callback=%s' % (
                self.__class__.__name__,
                getattr(self._callback, '__name__', self._callback))
        ikiwa self._args:
            x += ', args=' + str(self._args)
        ikiwa self._kwargs:
            x += ', kwargs=' + str(self._kwargs)
        ikiwa self._key[0] is not None:
            x += ', exitpriority=' + str(self._key[0])
        rudisha x + '>'


eleza _run_finalizers(minpriority=None):
    '''
    Run all finalizers whose exit priority is not None and at least minpriority

    Finalizers with highest priority are called first; finalizers with
    the same priority will be called in reverse order of creation.
    '''
    ikiwa _finalizer_registry is None:
        # This function may be called after this module's globals are
        # destroyed.  See the _exit_function function in this module for more
        # notes.
        return

    ikiwa minpriority is None:
        f = lambda p : p[0] is not None
    else:
        f = lambda p : p[0] is not None and p[0] >= minpriority

    # Careful: _finalizer_registry may be mutated while this function
    # is running (either by a GC run or by another thread).

    # list(_finalizer_registry) should be atomic, while
    # list(_finalizer_registry.items()) is not.
    keys = [key for key in list(_finalizer_registry) ikiwa f(key)]
    keys.sort(reverse=True)

    for key in keys:
        finalizer = _finalizer_registry.get(key)
        # key may have been removed kutoka the registry
        ikiwa finalizer is not None:
            sub_debug('calling %s', finalizer)
            try:
                finalizer()
            except Exception:
                agiza traceback
                traceback.print_exc()

    ikiwa minpriority is None:
        _finalizer_registry.clear()

#
# Clean up on exit
#

eleza is_exiting():
    '''
    Returns true ikiwa the process is shutting down
    '''
    rudisha _exiting or _exiting is None

_exiting = False

eleza _exit_function(info=info, debug=debug, _run_finalizers=_run_finalizers,
                   active_children=process.active_children,
                   current_process=process.current_process):
    # We hold on to references to functions in the arglist due to the
    # situation described below, where this function is called after this
    # module's globals are destroyed.

    global _exiting

    ikiwa not _exiting:
        _exiting = True

        info('process shutting down')
        debug('running all "atexit" finalizers with priority >= 0')
        _run_finalizers(0)

        ikiwa current_process() is not None:
            # We check ikiwa the current process is None here because if
            # it's None, any call to ``active_children()`` will raise
            # an AttributeError (active_children winds up trying to
            # get attributes kutoka util._current_process).  One
            # situation where this can happen is ikiwa someone has
            # manipulated sys.modules, causing this module to be
            # garbage collected.  The destructor for the module type
            # then replaces all values in the module dict with None.
            # For instance, after setuptools runs a test it replaces
            # sys.modules with a copy created earlier.  See issues
            # #9775 and #15881.  Also related: #4106, #9205, and
            # #9207.

            for p in active_children():
                ikiwa p.daemon:
                    info('calling terminate() for daemon %s', p.name)
                    p._popen.terminate()

            for p in active_children():
                info('calling join() for process %s', p.name)
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
# Close fds except those specified
#

try:
    MAXFD = os.sysconf("SC_OPEN_MAX")
except Exception:
    MAXFD = 256

eleza close_all_fds_except(fds):
    fds = list(fds) + [-1, MAXFD]
    fds.sort()
    assert fds[-1] == MAXFD, 'fd too large'
    for i in range(len(fds) - 1):
        os.closerange(fds[i]+1, fds[i+1])
#
# Close sys.stdin and replace stdin with os.devnull
#

eleza _close_stdin():
    ikiwa sys.stdin is None:
        return

    try:
        sys.stdin.close()
    except (OSError, ValueError):
        pass

    try:
        fd = os.open(os.devnull, os.O_RDONLY)
        try:
            sys.stdin = open(fd, closefd=False)
        except:
            os.close(fd)
            raise
    except (OSError, ValueError):
        pass

#
# Flush standard streams, ikiwa any
#

eleza _flush_std_streams():
    try:
        sys.stdout.flush()
    except (AttributeError, ValueError):
        pass
    try:
        sys.stderr.flush()
    except (AttributeError, ValueError):
        pass

#
# Start a program with only specified fds kept open
#

eleza spawnv_passfds(path, args, passfds):
    agiza _posixsubprocess
    passfds = tuple(sorted(map(int, passfds)))
    errpipe_read, errpipe_write = os.pipe()
    try:
        rudisha _posixsubprocess.fork_exec(
            args, [os.fsencode(path)], True, passfds, None, None,
            -1, -1, -1, -1, -1, -1, errpipe_read, errpipe_write,
            False, False, None)
    finally:
        os.close(errpipe_read)
        os.close(errpipe_write)


eleza close_fds(*fds):
    """Close each file descriptor given as an argument"""
    for fd in fds:
        os.close(fd)
