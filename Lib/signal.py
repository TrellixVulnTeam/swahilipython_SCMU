agiza _signal
kutoka _signal agiza *
kutoka functools agiza wraps as _wraps
kutoka enum agiza IntEnum as _IntEnum

_globals = globals()

_IntEnum._convert_(
        'Signals', __name__,
        lambda name:
            name.isupper()
            and (name.startswith('SIG') and not name.startswith('SIG_'))
            or name.startswith('CTRL_'))

_IntEnum._convert_(
        'Handlers', __name__,
        lambda name: name in ('SIG_DFL', 'SIG_IGN'))

ikiwa 'pthread_sigmask' in _globals:
    _IntEnum._convert_(
            'Sigmasks', __name__,
            lambda name: name in ('SIG_BLOCK', 'SIG_UNBLOCK', 'SIG_SETMASK'))


eleza _int_to_enum(value, enum_klass):
    """Convert a numeric value to an IntEnum member.
    If it's not a known member, rudisha the numeric value itself.
    """
    try:
        rudisha enum_klass(value)
    except ValueError:
        rudisha value


eleza _enum_to_int(value):
    """Convert an IntEnum member to a numeric value.
    If it's not an IntEnum member rudisha the value itself.
    """
    try:
        rudisha int(value)
    except (ValueError, TypeError):
        rudisha value


@_wraps(_signal.signal)
eleza signal(signalnum, handler):
    handler = _signal.signal(_enum_to_int(signalnum), _enum_to_int(handler))
    rudisha _int_to_enum(handler, Handlers)


@_wraps(_signal.getsignal)
eleza getsignal(signalnum):
    handler = _signal.getsignal(signalnum)
    rudisha _int_to_enum(handler, Handlers)


ikiwa 'pthread_sigmask' in _globals:
    @_wraps(_signal.pthread_sigmask)
    eleza pthread_sigmask(how, mask):
        sigs_set = _signal.pthread_sigmask(how, mask)
        rudisha set(_int_to_enum(x, Signals) for x in sigs_set)
    pthread_sigmask.__doc__ = _signal.pthread_sigmask.__doc__


ikiwa 'sigpending' in _globals:
    @_wraps(_signal.sigpending)
    eleza sigpending():
        rudisha {_int_to_enum(x, Signals) for x in _signal.sigpending()}


ikiwa 'sigwait' in _globals:
    @_wraps(_signal.sigwait)
    eleza sigwait(sigset):
        retsig = _signal.sigwait(sigset)
        rudisha _int_to_enum(retsig, Signals)
    sigwait.__doc__ = _signal.sigwait


ikiwa 'valid_signals' in _globals:
    @_wraps(_signal.valid_signals)
    eleza valid_signals():
        rudisha {_int_to_enum(x, Signals) for x in _signal.valid_signals()}


del _globals, _wraps
