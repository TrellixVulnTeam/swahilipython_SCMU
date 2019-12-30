agiza signal
agiza weakref

kutoka functools agiza wraps

__unittest = Kweli


kundi _InterruptHandler(object):
    eleza __init__(self, default_handler):
        self.called = Uongo
        self.original_handler = default_handler
        ikiwa isinstance(default_handler, int):
            ikiwa default_handler == signal.SIG_DFL:
                # Pretend it's signal.default_int_handler instead.
                default_handler = signal.default_int_handler
            elikiwa default_handler == signal.SIG_IGN:
                # Not quite the same thing as SIG_IGN, but the closest we
                # can make it: do nothing.
                eleza default_handler(unused_signum, unused_frame):
                    pass
            isipokua:
                 ashiria TypeError("expected SIGINT signal handler to be "
                                "signal.SIG_IGN, signal.SIG_DFL, ama a "
                                "callable object")
        self.default_handler = default_handler

    eleza __call__(self, signum, frame):
        installed_handler = signal.getsignal(signal.SIGINT)
        ikiwa installed_handler ni sio self:
            # ikiwa we aren't the installed handler, then delegate immediately
            # to the default handler
            self.default_handler(signum, frame)

        ikiwa self.called:
            self.default_handler(signum, frame)
        self.called = Kweli
        kila result kwenye _results.keys():
            result.stop()

_results = weakref.WeakKeyDictionary()
eleza registerResult(result):
    _results[result] = 1

eleza removeResult(result):
    rudisha bool(_results.pop(result, Tupu))

_interrupt_handler = Tupu
eleza installHandler():
    global _interrupt_handler
    ikiwa _interrupt_handler ni Tupu:
        default_handler = signal.getsignal(signal.SIGINT)
        _interrupt_handler = _InterruptHandler(default_handler)
        signal.signal(signal.SIGINT, _interrupt_handler)


eleza removeHandler(method=Tupu):
    ikiwa method ni sio Tupu:
        @wraps(method)
        eleza inner(*args, **kwargs):
            initial = signal.getsignal(signal.SIGINT)
            removeHandler()
            jaribu:
                rudisha method(*args, **kwargs)
            mwishowe:
                signal.signal(signal.SIGINT, initial)
        rudisha inner

    global _interrupt_handler
    ikiwa _interrupt_handler ni sio Tupu:
        signal.signal(signal.SIGINT, _interrupt_handler.original_handler)
