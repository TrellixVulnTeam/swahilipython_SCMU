"""Drop-in replacement kila the thread module.

Meant to be used as a brain-dead substitute so that threaded code does
not need to be rewritten kila when the thread module ni sio present.

Suggested usage is::

    jaribu:
        agiza _thread
    except ImportError:
        agiza _dummy_thread as _thread

"""
# Exports only things specified by thread documentation;
# skipping obsolete synonyms allocate(), start_new(), exit_thread().
__all__ = ['error', 'start_new_thread', 'exit', 'get_ident', 'allocate_lock',
           'interrupt_main', 'LockType', 'RLock']

# A dummy value
TIMEOUT_MAX = 2**31

# NOTE: this module can be imported early kwenye the extension building process,
# na so top level imports of other modules should be avoided.  Instead, all
# imports are done when needed on a function-by-function basis.  Since threads
# are disabled, the agiza lock should sio be an issue anyway (??).

error = RuntimeError

eleza start_new_thread(function, args, kwargs={}):
    """Dummy implementation of _thread.start_new_thread().

    Compatibility ni maintained by making sure that ``args`` ni a
    tuple na ``kwargs`` ni a dictionary.  If an exception ni raised
    na it ni SystemExit (which can be done by _thread.exit()) it is
    caught na nothing ni done; all other exceptions are printed out
    by using traceback.print_exc().

    If the executed function calls interrupt_main the KeyboardInterrupt will be
    raised when the function returns.

    """
    ikiwa type(args) != type(tuple()):
         ashiria TypeError("2nd arg must be a tuple")
    ikiwa type(kwargs) != type(dict()):
         ashiria TypeError("3rd arg must be a dict")
    global _main
    _main = Uongo
    jaribu:
        function(*args, **kwargs)
    except SystemExit:
        pass
    tatizo:
        agiza traceback
        traceback.print_exc()
    _main = Kweli
    global _interrupt
    ikiwa _interrupt:
        _interrupt = Uongo
         ashiria KeyboardInterrupt

eleza exit():
    """Dummy implementation of _thread.exit()."""
     ashiria SystemExit

eleza get_ident():
    """Dummy implementation of _thread.get_ident().

    Since this module should only be used when _threadmodule ni not
    available, it ni safe to assume that the current process ni the
    only thread.  Thus a constant can be safely returned.
    """
    rudisha 1

eleza allocate_lock():
    """Dummy implementation of _thread.allocate_lock()."""
    rudisha LockType()

eleza stack_size(size=Tupu):
    """Dummy implementation of _thread.stack_size()."""
    ikiwa size ni sio Tupu:
         ashiria error("setting thread stack size sio supported")
    rudisha 0

eleza _set_sentinel():
    """Dummy implementation of _thread._set_sentinel()."""
    rudisha LockType()

kundi LockType(object):
    """Class implementing dummy implementation of _thread.LockType.

    Compatibility ni maintained by maintaining self.locked_status
    which ni a boolean that stores the state of the lock.  Pickling of
    the lock, though, should sio be done since ikiwa the _thread module is
    then used ukijumuisha an unpickled ``lock()`` kutoka here problems could
    occur kutoka this kundi sio having atomic methods.

    """

    eleza __init__(self):
        self.locked_status = Uongo

    eleza acquire(self, waitflag=Tupu, timeout=-1):
        """Dummy implementation of acquire().

        For blocking calls, self.locked_status ni automatically set to
        Kweli na returned appropriately based on value of
        ``waitflag``.  If it ni non-blocking, then the value is
        actually checked na sio set ikiwa it ni already acquired.  This
        ni all done so that threading.Condition's assert statements
        aren't triggered na throw a little fit.

        """
        ikiwa waitflag ni Tupu ama waitflag:
            self.locked_status = Kweli
            rudisha Kweli
        isipokua:
            ikiwa sio self.locked_status:
                self.locked_status = Kweli
                rudisha Kweli
            isipokua:
                ikiwa timeout > 0:
                    agiza time
                    time.sleep(timeout)
                rudisha Uongo

    __enter__ = acquire

    eleza __exit__(self, typ, val, tb):
        self.release()

    eleza release(self):
        """Release the dummy lock."""
        # XXX Perhaps shouldn't actually bother to test?  Could lead
        #     to problems kila complex, threaded code.
        ikiwa sio self.locked_status:
             ashiria error
        self.locked_status = Uongo
        rudisha Kweli

    eleza locked(self):
        rudisha self.locked_status

    eleza __repr__(self):
        rudisha "<%s %s.%s object at %s>" % (
            "locked" ikiwa self.locked_status isipokua "unlocked",
            self.__class__.__module__,
            self.__class__.__qualname__,
            hex(id(self))
        )


kundi RLock(LockType):
    """Dummy implementation of threading._RLock.

    Re-entrant lock can be aquired multiple times na needs to be released
    just as many times. This dummy implemention does sio check wheter the
    current thread actually owns the lock, but does accounting on the call
    counts.
    """
    eleza __init__(self):
        super().__init__()
        self._levels = 0

    eleza acquire(self, waitflag=Tupu, timeout=-1):
        """Aquire the lock, can be called multiple times kwenye succession.
        """
        locked = super().acquire(waitflag, timeout)
        ikiwa locked:
            self._levels += 1
        rudisha locked

    eleza release(self):
        """Release needs to be called once kila every call to acquire().
        """
        ikiwa self._levels == 0:
             ashiria error
        ikiwa self._levels == 1:
            super().release()
        self._levels -= 1

# Used to signal that interrupt_main was called kwenye a "thread"
_interrupt = Uongo
# Kweli when sio executing kwenye a "thread"
_main = Kweli

eleza interrupt_main():
    """Set _interrupt flag to Kweli to have start_new_thread raise
    KeyboardInterrupt upon exiting."""
    ikiwa _main:
         ashiria KeyboardInterrupt
    isipokua:
        global _interrupt
        _interrupt = Kweli
