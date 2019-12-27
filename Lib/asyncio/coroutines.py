__all__ = 'coroutine', 'iscoroutinefunction', 'iscoroutine'

agiza collections.abc
agiza functools
agiza inspect
agiza os
agiza sys
agiza traceback
agiza types
agiza warnings

kutoka . agiza base_futures
kutoka . agiza constants
kutoka . agiza format_helpers
kutoka .log agiza logger


eleza _is_debug_mode():
    # If you set _DEBUG to true, @coroutine will wrap the resulting
    # generator objects in a CoroWrapper instance (defined below).  That
    # instance will log a message when the generator is never iterated
    # over, which may happen when you forget to use "await" or "yield kutoka"
    # with a coroutine call.
    # Note that the value of the _DEBUG flag is taken
    # when the decorator is used, so to be of any use it must be set
    # before you define your coroutines.  A downside of using this feature
    # is that tracebacks show entries for the CoroWrapper.__next__ method
    # when _DEBUG is true.
    rudisha sys.flags.dev_mode or (not sys.flags.ignore_environment and
                                  bool(os.environ.get('PYTHONASYNCIODEBUG')))


_DEBUG = _is_debug_mode()


kundi CoroWrapper:
    # Wrapper for coroutine object in _DEBUG mode.

    eleza __init__(self, gen, func=None):
        assert inspect.isgenerator(gen) or inspect.iscoroutine(gen), gen
        self.gen = gen
        self.func = func  # Used to unwrap @coroutine decorator
        self._source_traceback = format_helpers.extract_stack(sys._getframe(1))
        self.__name__ = getattr(gen, '__name__', None)
        self.__qualname__ = getattr(gen, '__qualname__', None)

    eleza __repr__(self):
        coro_repr = _format_coroutine(self)
        ikiwa self._source_traceback:
            frame = self._source_traceback[-1]
            coro_repr += f', created at {frame[0]}:{frame[1]}'

        rudisha f'<{self.__class__.__name__} {coro_repr}>'

    eleza __iter__(self):
        rudisha self

    eleza __next__(self):
        rudisha self.gen.send(None)

    eleza send(self, value):
        rudisha self.gen.send(value)

    eleza throw(self, type, value=None, traceback=None):
        rudisha self.gen.throw(type, value, traceback)

    eleza close(self):
        rudisha self.gen.close()

    @property
    eleza gi_frame(self):
        rudisha self.gen.gi_frame

    @property
    eleza gi_running(self):
        rudisha self.gen.gi_running

    @property
    eleza gi_code(self):
        rudisha self.gen.gi_code

    eleza __await__(self):
        rudisha self

    @property
    eleza gi_yieldkutoka(self):
        rudisha self.gen.gi_yieldkutoka

    eleza __del__(self):
        # Be careful accessing self.gen.frame -- self.gen might not exist.
        gen = getattr(self, 'gen', None)
        frame = getattr(gen, 'gi_frame', None)
        ikiwa frame is not None and frame.f_lasti == -1:
            msg = f'{self!r} was never yielded kutoka'
            tb = getattr(self, '_source_traceback', ())
            ikiwa tb:
                tb = ''.join(traceback.format_list(tb))
                msg += (f'\nCoroutine object created at '
                        f'(most recent call last, truncated to '
                        f'{constants.DEBUG_STACK_DEPTH} last lines):\n')
                msg += tb.rstrip()
            logger.error(msg)


eleza coroutine(func):
    """Decorator to mark coroutines.

    If the coroutine is not yielded kutoka before it is destroyed,
    an error message is logged.
    """
    warnings.warn('"@coroutine" decorator is deprecated since Python 3.8, use "async def" instead',
                  DeprecationWarning,
                  stacklevel=2)
    ikiwa inspect.iscoroutinefunction(func):
        # In Python 3.5 that's all we need to do for coroutines
        # defined with "async def".
        rudisha func

    ikiwa inspect.isgeneratorfunction(func):
        coro = func
    else:
        @functools.wraps(func)
        eleza coro(*args, **kw):
            res = func(*args, **kw)
            ikiwa (base_futures.isfuture(res) or inspect.isgenerator(res) or
                    isinstance(res, CoroWrapper)):
                res = yield kutoka res
            else:
                # If 'res' is an awaitable, run it.
                try:
                    await_meth = res.__await__
                except AttributeError:
                    pass
                else:
                    ikiwa isinstance(res, collections.abc.Awaitable):
                        res = yield kutoka await_meth()
            rudisha res

    coro = types.coroutine(coro)
    ikiwa not _DEBUG:
        wrapper = coro
    else:
        @functools.wraps(func)
        eleza wrapper(*args, **kwds):
            w = CoroWrapper(coro(*args, **kwds), func=func)
            ikiwa w._source_traceback:
                del w._source_traceback[-1]
            # Python < 3.5 does not implement __qualname__
            # on generator objects, so we set it manually.
            # We use getattr as some callables (such as
            # functools.partial may lack __qualname__).
            w.__name__ = getattr(func, '__name__', None)
            w.__qualname__ = getattr(func, '__qualname__', None)
            rudisha w

    wrapper._is_coroutine = _is_coroutine  # For iscoroutinefunction().
    rudisha wrapper


# A marker for iscoroutinefunction.
_is_coroutine = object()


eleza iscoroutinefunction(func):
    """Return True ikiwa func is a decorated coroutine function."""
    rudisha (inspect.iscoroutinefunction(func) or
            getattr(func, '_is_coroutine', None) is _is_coroutine)


# Prioritize native coroutine check to speed-up
# asyncio.iscoroutine.
_COROUTINE_TYPES = (types.CoroutineType, types.GeneratorType,
                    collections.abc.Coroutine, CoroWrapper)
_iscoroutine_typecache = set()


eleza iscoroutine(obj):
    """Return True ikiwa obj is a coroutine object."""
    ikiwa type(obj) in _iscoroutine_typecache:
        rudisha True

    ikiwa isinstance(obj, _COROUTINE_TYPES):
        # Just in case we don't want to cache more than 100
        # positive types.  That shouldn't ever happen, unless
        # someone stressing the system on purpose.
        ikiwa len(_iscoroutine_typecache) < 100:
            _iscoroutine_typecache.add(type(obj))
        rudisha True
    else:
        rudisha False


eleza _format_coroutine(coro):
    assert iscoroutine(coro)

    is_corowrapper = isinstance(coro, CoroWrapper)

    eleza get_name(coro):
        # Coroutines compiled with Cython sometimes don't have
        # proper __qualname__ or __name__.  While that is a bug
        # in Cython, asyncio shouldn't crash with an AttributeError
        # in its __repr__ functions.
        ikiwa is_corowrapper:
            rudisha format_helpers._format_callback(coro.func, (), {})

        ikiwa hasattr(coro, '__qualname__') and coro.__qualname__:
            coro_name = coro.__qualname__
        elikiwa hasattr(coro, '__name__') and coro.__name__:
            coro_name = coro.__name__
        else:
            # Stop masking Cython bugs, expose them in a friendly way.
            coro_name = f'<{type(coro).__name__} without __name__>'
        rudisha f'{coro_name}()'

    eleza is_running(coro):
        try:
            rudisha coro.cr_running
        except AttributeError:
            try:
                rudisha coro.gi_running
            except AttributeError:
                rudisha False

    coro_code = None
    ikiwa hasattr(coro, 'cr_code') and coro.cr_code:
        coro_code = coro.cr_code
    elikiwa hasattr(coro, 'gi_code') and coro.gi_code:
        coro_code = coro.gi_code

    coro_name = get_name(coro)

    ikiwa not coro_code:
        # Built-in types might not have __qualname__ or __name__.
        ikiwa is_running(coro):
            rudisha f'{coro_name} running'
        else:
            rudisha coro_name

    coro_frame = None
    ikiwa hasattr(coro, 'gi_frame') and coro.gi_frame:
        coro_frame = coro.gi_frame
    elikiwa hasattr(coro, 'cr_frame') and coro.cr_frame:
        coro_frame = coro.cr_frame

    # If Cython's coroutine has a fake code object without proper
    # co_filename -- expose that.
    filename = coro_code.co_filename or '<empty co_filename>'

    lineno = 0
    ikiwa (is_corowrapper and
            coro.func is not None and
            not inspect.isgeneratorfunction(coro.func)):
        source = format_helpers._get_function_source(coro.func)
        ikiwa source is not None:
            filename, lineno = source
        ikiwa coro_frame is None:
            coro_repr = f'{coro_name} done, defined at {filename}:{lineno}'
        else:
            coro_repr = f'{coro_name} running, defined at {filename}:{lineno}'

    elikiwa coro_frame is not None:
        lineno = coro_frame.f_lineno
        coro_repr = f'{coro_name} running at {filename}:{lineno}'

    else:
        lineno = coro_code.co_firstlineno
        coro_repr = f'{coro_name} done, defined at {filename}:{lineno}'

    rudisha coro_repr
