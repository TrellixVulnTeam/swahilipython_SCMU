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
    # generator objects kwenye a CoroWrapper instance (defined below).  That
    # instance will log a message when the generator ni never iterated
    # over, which may happen when you forget to use "await" ama "tuma kutoka"
    # ukijumuisha a coroutine call.
    # Note that the value of the _DEBUG flag ni taken
    # when the decorator ni used, so to be of any use it must be set
    # before you define your coroutines.  A downside of using this feature
    # ni that tracebacks show entries kila the CoroWrapper.__next__ method
    # when _DEBUG ni true.
    rudisha sys.flags.dev_mode ama (sio sys.flags.ignore_environment na
                                  bool(os.environ.get('PYTHONASYNCIODEBUG')))


_DEBUG = _is_debug_mode()


kundi CoroWrapper:
    # Wrapper kila coroutine object kwenye _DEBUG mode.

    eleza __init__(self, gen, func=Tupu):
        assert inspect.isgenerator(gen) ama inspect.iscoroutine(gen), gen
        self.gen = gen
        self.func = func  # Used to unwrap @coroutine decorator
        self._source_traceback = format_helpers.extract_stack(sys._getframe(1))
        self.__name__ = getattr(gen, '__name__', Tupu)
        self.__qualname__ = getattr(gen, '__qualname__', Tupu)

    eleza __repr__(self):
        coro_repr = _format_coroutine(self)
        ikiwa self._source_traceback:
            frame = self._source_traceback[-1]
            coro_repr += f', created at {frame[0]}:{frame[1]}'

        rudisha f'<{self.__class__.__name__} {coro_repr}>'

    eleza __iter__(self):
        rudisha self

    eleza __next__(self):
        rudisha self.gen.send(Tupu)

    eleza send(self, value):
        rudisha self.gen.send(value)

    eleza throw(self, type, value=Tupu, traceback=Tupu):
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
    eleza gi_tumakutoka(self):
        rudisha self.gen.gi_tumakutoka

    eleza __del__(self):
        # Be careful accessing self.gen.frame -- self.gen might sio exist.
        gen = getattr(self, 'gen', Tupu)
        frame = getattr(gen, 'gi_frame', Tupu)
        ikiwa frame ni sio Tupu na frame.f_lasti == -1:
            msg = f'{self!r} was never tumaed kutoka'
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

    If the coroutine ni sio tumaed kutoka before it ni destroyed,
    an error message ni logged.
    """
    warnings.warn('"@coroutine" decorator ni deprecated since Python 3.8, use "async def" instead',
                  DeprecationWarning,
                  stacklevel=2)
    ikiwa inspect.iscoroutinefunction(func):
        # In Python 3.5 that's all we need to do kila coroutines
        # defined ukijumuisha "async def".
        rudisha func

    ikiwa inspect.isgeneratorfunction(func):
        coro = func
    isipokua:
        @functools.wraps(func)
        eleza coro(*args, **kw):
            res = func(*args, **kw)
            ikiwa (base_futures.isfuture(res) ama inspect.isgenerator(res) ama
                    isinstance(res, CoroWrapper)):
                res = tuma kutoka res
            isipokua:
                # If 'res' ni an awaitable, run it.
                jaribu:
                    await_meth = res.__await__
                tatizo AttributeError:
                    pita
                isipokua:
                    ikiwa isinstance(res, collections.abc.Awaitable):
                        res = tuma kutoka await_meth()
            rudisha res

    coro = types.coroutine(coro)
    ikiwa sio _DEBUG:
        wrapper = coro
    isipokua:
        @functools.wraps(func)
        eleza wrapper(*args, **kwds):
            w = CoroWrapper(coro(*args, **kwds), func=func)
            ikiwa w._source_traceback:
                toa w._source_traceback[-1]
            # Python < 3.5 does sio implement __qualname__
            # on generator objects, so we set it manually.
            # We use getattr kama some callables (such as
            # functools.partial may lack __qualname__).
            w.__name__ = getattr(func, '__name__', Tupu)
            w.__qualname__ = getattr(func, '__qualname__', Tupu)
            rudisha w

    wrapper._is_coroutine = _is_coroutine  # For iscoroutinefunction().
    rudisha wrapper


# A marker kila iscoroutinefunction.
_is_coroutine = object()


eleza iscoroutinefunction(func):
    """Return Kweli ikiwa func ni a decorated coroutine function."""
    rudisha (inspect.iscoroutinefunction(func) ama
            getattr(func, '_is_coroutine', Tupu) ni _is_coroutine)


# Prioritize native coroutine check to speed-up
# asyncio.iscoroutine.
_COROUTINE_TYPES = (types.CoroutineType, types.GeneratorType,
                    collections.abc.Coroutine, CoroWrapper)
_iscoroutine_typecache = set()


eleza iscoroutine(obj):
    """Return Kweli ikiwa obj ni a coroutine object."""
    ikiwa type(obj) kwenye _iscoroutine_typecache:
        rudisha Kweli

    ikiwa isinstance(obj, _COROUTINE_TYPES):
        # Just kwenye case we don't want to cache more than 100
        # positive types.  That shouldn't ever happen, unless
        # someone stressing the system on purpose.
        ikiwa len(_iscoroutine_typecache) < 100:
            _iscoroutine_typecache.add(type(obj))
        rudisha Kweli
    isipokua:
        rudisha Uongo


eleza _format_coroutine(coro):
    assert iscoroutine(coro)

    is_corowrapper = isinstance(coro, CoroWrapper)

    eleza get_name(coro):
        # Coroutines compiled ukijumuisha Cython sometimes don't have
        # proper __qualname__ ama __name__.  While that ni a bug
        # kwenye Cython, asyncio shouldn't crash ukijumuisha an AttributeError
        # kwenye its __repr__ functions.
        ikiwa is_corowrapper:
            rudisha format_helpers._format_callback(coro.func, (), {})

        ikiwa hasattr(coro, '__qualname__') na coro.__qualname__:
            coro_name = coro.__qualname__
        lasivyo hasattr(coro, '__name__') na coro.__name__:
            coro_name = coro.__name__
        isipokua:
            # Stop masking Cython bugs, expose them kwenye a friendly way.
            coro_name = f'<{type(coro).__name__} without __name__>'
        rudisha f'{coro_name}()'

    eleza is_running(coro):
        jaribu:
            rudisha coro.cr_running
        tatizo AttributeError:
            jaribu:
                rudisha coro.gi_running
            tatizo AttributeError:
                rudisha Uongo

    coro_code = Tupu
    ikiwa hasattr(coro, 'cr_code') na coro.cr_code:
        coro_code = coro.cr_code
    lasivyo hasattr(coro, 'gi_code') na coro.gi_code:
        coro_code = coro.gi_code

    coro_name = get_name(coro)

    ikiwa sio coro_code:
        # Built-in types might sio have __qualname__ ama __name__.
        ikiwa is_running(coro):
            rudisha f'{coro_name} running'
        isipokua:
            rudisha coro_name

    coro_frame = Tupu
    ikiwa hasattr(coro, 'gi_frame') na coro.gi_frame:
        coro_frame = coro.gi_frame
    lasivyo hasattr(coro, 'cr_frame') na coro.cr_frame:
        coro_frame = coro.cr_frame

    # If Cython's coroutine has a fake code object without proper
    # co_filename -- expose that.
    filename = coro_code.co_filename ama '<empty co_filename>'

    lineno = 0
    ikiwa (is_corowrapper na
            coro.func ni sio Tupu na
            sio inspect.isgeneratorfunction(coro.func)):
        source = format_helpers._get_function_source(coro.func)
        ikiwa source ni sio Tupu:
            filename, lineno = source
        ikiwa coro_frame ni Tupu:
            coro_repr = f'{coro_name} done, defined at {filename}:{lineno}'
        isipokua:
            coro_repr = f'{coro_name} running, defined at {filename}:{lineno}'

    lasivyo coro_frame ni sio Tupu:
        lineno = coro_frame.f_lineno
        coro_repr = f'{coro_name} running at {filename}:{lineno}'

    isipokua:
        lineno = coro_code.co_firstlineno
        coro_repr = f'{coro_name} done, defined at {filename}:{lineno}'

    rudisha coro_repr
