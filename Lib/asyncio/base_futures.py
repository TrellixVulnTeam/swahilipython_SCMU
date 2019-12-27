__all__ = ()

agiza reprlib

kutoka . agiza format_helpers

# States for Future.
_PENDING = 'PENDING'
_CANCELLED = 'CANCELLED'
_FINISHED = 'FINISHED'


eleza isfuture(obj):
    """Check for a Future.

    This returns True when obj is a Future instance or is advertising
    itself as duck-type compatible by setting _asyncio_future_blocking.
    See comment in Future for more details.
    """
    rudisha (hasattr(obj.__class__, '_asyncio_future_blocking') and
            obj._asyncio_future_blocking is not None)


eleza _format_callbacks(cb):
    """helper function for Future.__repr__"""
    size = len(cb)
    ikiwa not size:
        cb = ''

    eleza format_cb(callback):
        rudisha format_helpers._format_callback_source(callback, ())

    ikiwa size == 1:
        cb = format_cb(cb[0][0])
    elikiwa size == 2:
        cb = '{}, {}'.format(format_cb(cb[0][0]), format_cb(cb[1][0]))
    elikiwa size > 2:
        cb = '{}, <{} more>, {}'.format(format_cb(cb[0][0]),
                                        size - 2,
                                        format_cb(cb[-1][0]))
    rudisha f'cb=[{cb}]'


eleza _future_repr_info(future):
    # (Future) -> str
    """helper function for Future.__repr__"""
    info = [future._state.lower()]
    ikiwa future._state == _FINISHED:
        ikiwa future._exception is not None:
            info.append(f'exception={future._exception!r}')
        else:
            # use reprlib to limit the length of the output, especially
            # for very long strings
            result = reprlib.repr(future._result)
            info.append(f'result={result}')
    ikiwa future._callbacks:
        info.append(_format_callbacks(future._callbacks))
    ikiwa future._source_traceback:
        frame = future._source_traceback[-1]
        info.append(f'created at {frame[0]}:{frame[1]}')
    rudisha info
