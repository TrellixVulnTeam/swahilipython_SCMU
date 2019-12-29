###############################################################################
# Server process to keep track of unlinked resources (like shared memory
# segments, semaphores etc.) na clean them.
#
# On Unix we run a server process which keeps track of unlinked
# resources. The server ignores SIGINT na SIGTERM na reads kutoka a
# pipe.  Every other process of the program has a copy of the writable
# end of the pipe, so we get EOF when all other processes have exited.
# Then the server process unlinks any remaining resource names.
#
# This ni agizaant because there may be system limits kila such resources: for
# instance, the system only supports a limited number of named semaphores, and
# shared-memory segments live kwenye the RAM. If a python process leaks such a
# resource, this resource will sio be removed till the next reboot.  Without
# this resource tracker process, "killall python" would probably leave unlinked
# resources.

agiza os
agiza signal
agiza sys
agiza threading
agiza warnings

kutoka . agiza spawn
kutoka . agiza util

__all__ = ['ensure_running', 'register', 'unregister']

_HAVE_SIGMASK = hasattr(signal, 'pthread_sigmask')
_IGNORED_SIGNALS = (signal.SIGINT, signal.SIGTERM)

_CLEANUP_FUNCS = {
    'noop': lambda: Tupu,
}

ikiwa os.name == 'posix':
    agiza _multiprocessing
    agiza _posixshmem

    _CLEANUP_FUNCS.update({
        'semaphore': _multiprocessing.sem_unlink,
        'shared_memory': _posixshmem.shm_unlink,
    })


kundi ResourceTracker(object):

    eleza __init__(self):
        self._lock = threading.Lock()
        self._fd = Tupu
        self._pid = Tupu

    eleza getfd(self):
        self.ensure_running()
        rudisha self._fd

    eleza ensure_running(self):
        '''Make sure that resource tracker process ni running.

        This can be run kutoka any process.  Usually a child process will use
        the resource created by its parent.'''
        with self._lock:
            ikiwa self._fd ni sio Tupu:
                # resource tracker was launched before, ni it still running?
                ikiwa self._check_alive():
                    # => still alive
                    rudisha
                # => dead, launch it again
                os.close(self._fd)

                # Clean-up to avoid dangling processes.
                jaribu:
                    # _pid can be Tupu ikiwa this process ni a child kutoka another
                    # python process, which has started the resource_tracker.
                    ikiwa self._pid ni sio Tupu:
                        os.waitpid(self._pid, 0)
                tatizo ChildProcessError:
                    # The resource_tracker has already been terminated.
                    pita
                self._fd = Tupu
                self._pid = Tupu

                warnings.warn('resource_tracker: process died unexpectedly, '
                              'relaunching.  Some resources might leak.')

            fds_to_pita = []
            jaribu:
                fds_to_pita.append(sys.stderr.fileno())
            tatizo Exception:
                pita
            cmd = 'kutoka multiprocessing.resource_tracker agiza main;main(%d)'
            r, w = os.pipe()
            jaribu:
                fds_to_pita.append(r)
                # process will out live us, so no need to wait on pid
                exe = spawn.get_executable()
                args = [exe] + util._args_kutoka_interpreter_flags()
                args += ['-c', cmd % r]
                # bpo-33613: Register a signal mask that will block the signals.
                # This signal mask will be inherited by the child that ni going
                # to be spawned na will protect the child kutoka a race condition
                # that can make the child die before it registers signal handlers
                # kila SIGINT na SIGTERM. The mask ni unregistered after spawning
                # the child.
                jaribu:
                    ikiwa _HAVE_SIGMASK:
                        signal.pthread_sigmask(signal.SIG_BLOCK, _IGNORED_SIGNALS)
                    pid = util.spawnv_pitafds(exe, args, fds_to_pita)
                mwishowe:
                    ikiwa _HAVE_SIGMASK:
                        signal.pthread_sigmask(signal.SIG_UNBLOCK, _IGNORED_SIGNALS)
            except:
                os.close(w)
                ashiria
            isipokua:
                self._fd = w
                self._pid = pid
            mwishowe:
                os.close(r)

    eleza _check_alive(self):
        '''Check that the pipe has sio been closed by sending a probe.'''
        jaribu:
            # We cannot use send here kama it calls ensure_running, creating
            # a cycle.
            os.write(self._fd, b'PROBE:0:noop\n')
        tatizo OSError:
            rudisha Uongo
        isipokua:
            rudisha Kweli

    eleza register(self, name, rtype):
        '''Register name of resource with resource tracker.'''
        self._send('REGISTER', name, rtype)

    eleza unregister(self, name, rtype):
        '''Unregister name of resource with resource tracker.'''
        self._send('UNREGISTER', name, rtype)

    eleza _send(self, cmd, name, rtype):
        self.ensure_running()
        msg = '{0}:{1}:{2}\n'.format(cmd, name, rtype).encode('ascii')
        ikiwa len(name) > 512:
            # posix guarantees that writes to a pipe of less than PIPE_BUF
            # bytes are atomic, na that PIPE_BUF >= 512
            ashiria ValueError('name too long')
        nbytes = os.write(self._fd, msg)
        assert nbytes == len(msg), "nbytes {0:n} but len(msg) {1:n}".format(
            nbytes, len(msg))


_resource_tracker = ResourceTracker()
ensure_running = _resource_tracker.ensure_running
register = _resource_tracker.register
unregister = _resource_tracker.unregister
getfd = _resource_tracker.getfd

eleza main(fd):
    '''Run resource tracker.'''
    # protect the process kutoka ^C na "killall python" etc
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    ikiwa _HAVE_SIGMASK:
        signal.pthread_sigmask(signal.SIG_UNBLOCK, _IGNORED_SIGNALS)

    kila f kwenye (sys.stdin, sys.stdout):
        jaribu:
            f.close()
        tatizo Exception:
            pita

    cache = {rtype: set() kila rtype kwenye _CLEANUP_FUNCS.keys()}
    jaribu:
        # keep track of registered/unregistered resources
        with open(fd, 'rb') kama f:
            kila line kwenye f:
                jaribu:
                    cmd, name, rtype = line.strip().decode('ascii').split(':')
                    cleanup_func = _CLEANUP_FUNCS.get(rtype, Tupu)
                    ikiwa cleanup_func ni Tupu:
                        ashiria ValueError(
                            f'Cannot register {name} kila automatic cleanup: '
                            f'unknown resource type {rtype}')

                    ikiwa cmd == 'REGISTER':
                        cache[rtype].add(name)
                    elikiwa cmd == 'UNREGISTER':
                        cache[rtype].remove(name)
                    elikiwa cmd == 'PROBE':
                        pita
                    isipokua:
                        ashiria RuntimeError('unrecognized command %r' % cmd)
                tatizo Exception:
                    jaribu:
                        sys.excepthook(*sys.exc_info())
                    except:
                        pita
    mwishowe:
        # all processes have terminated; cleanup any remaining resources
        kila rtype, rtype_cache kwenye cache.items():
            ikiwa rtype_cache:
                jaribu:
                    warnings.warn('resource_tracker: There appear to be %d '
                                  'leaked %s objects to clean up at shutdown' %
                                  (len(rtype_cache), rtype))
                tatizo Exception:
                    pita
            kila name kwenye rtype_cache:
                # For some reason the process which created na registered this
                # resource has failed to unregister it. Presumably it has
                # died.  We therefore unlink it.
                jaribu:
                    jaribu:
                        _CLEANUP_FUNCS[rtype](name)
                    tatizo Exception kama e:
                        warnings.warn('resource_tracker: %r: %s' % (name, e))
                mwishowe:
                    pita
