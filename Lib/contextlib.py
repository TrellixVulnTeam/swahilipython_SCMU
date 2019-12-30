"""Utilities kila with-statement contexts.  See PEP 343."""
agiza abc
agiza sys
agiza _collections_abc
kutoka collections agiza deque
kutoka functools agiza wraps
kutoka types agiza MethodType

__all__ = ["asynccontextmanager", "contextmanager", "closing", "nullcontext",
           "AbstractContextManager", "AbstractAsyncContextManager",
           "AsyncExitStack", "ContextDecorator", "ExitStack",
           "redirect_stdout", "redirect_stderr", "suppress"]


kundi AbstractContextManager(abc.ABC):

    """An abstract base kundi kila context managers."""

    eleza __enter__(self):
        """Return `self` upon entering the runtime context."""
        rudisha self

    @abc.abstractmethod
    eleza __exit__(self, exc_type, exc_value, traceback):
        """Raise any exception triggered within the runtime context."""
        rudisha Tupu

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni AbstractContextManager:
            rudisha _collections_abc._check_methods(C, "__enter__", "__exit__")
        rudisha NotImplemented


kundi AbstractAsyncContextManager(abc.ABC):

    """An abstract base kundi kila asynchronous context managers."""

    async eleza __aenter__(self):
        """Return `self` upon entering the runtime context."""
        rudisha self

    @abc.abstractmethod
    async eleza __aexit__(self, exc_type, exc_value, traceback):
        """Raise any exception triggered within the runtime context."""
        rudisha Tupu

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni AbstractAsyncContextManager:
            rudisha _collections_abc._check_methods(C, "__aenter__",
                                                   "__aexit__")
        rudisha NotImplemented


kundi ContextDecorator(object):
    "A base kundi ama mixin that enables context managers to work kama decorators."

    eleza _recreate_cm(self):
        """Return a recreated instance of self.

        Allows an otherwise one-shot context manager like
        _GeneratorContextManager to support use as
        a decorator via implicit recreation.

        This ni a private interface just kila _GeneratorContextManager.
        See issue #11647 kila details.
        """
        rudisha self

    eleza __call__(self, func):
        @wraps(func)
        eleza inner(*args, **kwds):
            ukijumuisha self._recreate_cm():
                rudisha func(*args, **kwds)
        rudisha inner


kundi _GeneratorContextManagerBase:
    """Shared functionality kila @contextmanager na @asynccontextmanager."""

    eleza __init__(self, func, args, kwds):
        self.gen = func(*args, **kwds)
        self.func, self.args, self.kwds = func, args, kwds
        # Issue 19330: ensure context manager instances have good docstrings
        doc = getattr(func, "__doc__", Tupu)
        ikiwa doc ni Tupu:
            doc = type(self).__doc__
        self.__doc__ = doc
        # Unfortunately, this still doesn't provide good help output when
        # inspecting the created context manager instances, since pydoc
        # currently bypitaes the instance docstring na shows the docstring
        # kila the kundi instead.
        # See http://bugs.python.org/issue19404 kila more details.


kundi _GeneratorContextManager(_GeneratorContextManagerBase,
                               AbstractContextManager,
                               ContextDecorator):
    """Helper kila @contextmanager decorator."""

    eleza _recreate_cm(self):
        # _GCM instances are one-shot context managers, so the
        # CM must be recreated each time a decorated function is
        # called
        rudisha self.__class__(self.func, self.args, self.kwds)

    eleza __enter__(self):
        # do sio keep args na kwds alive unnecessarily
        # they are only needed kila recreation, which ni sio possible anymore
        toa self.args, self.kwds, self.func
        jaribu:
            rudisha next(self.gen)
        tatizo StopIteration:
            ashiria RuntimeError("generator didn't tuma") kutoka Tupu

    eleza __exit__(self, type, value, traceback):
        ikiwa type ni Tupu:
            jaribu:
                next(self.gen)
            tatizo StopIteration:
                rudisha Uongo
            isipokua:
                ashiria RuntimeError("generator didn't stop")
        isipokua:
            ikiwa value ni Tupu:
                # Need to force instantiation so we can reliably
                # tell ikiwa we get the same exception back
                value = type()
            jaribu:
                self.gen.throw(type, value, traceback)
            tatizo StopIteration kama exc:
                # Suppress StopIteration *unless* it's the same exception that
                # was pitaed to throw().  This prevents a StopIteration
                # raised inside the "with" statement kutoka being suppressed.
                rudisha exc ni sio value
            tatizo RuntimeError kama exc:
                # Don't re-ashiria the pitaed kwenye exception. (issue27122)
                ikiwa exc ni value:
                    rudisha Uongo
                # Likewise, avoid suppressing ikiwa a StopIteration exception
                # was pitaed to throw() na later wrapped into a RuntimeError
                # (see PEP 479).
                ikiwa type ni StopIteration na exc.__cause__ ni value:
                    rudisha Uongo
                raise
            tatizo:
                # only re-ashiria ikiwa it's *not* the exception that was
                # pitaed to throw(), because __exit__() must sio raise
                # an exception unless __exit__() itself failed.  But throw()
                # has to ashiria the exception to signal propagation, so this
                # fixes the impedance mismatch between the throw() protocol
                # na the __exit__() protocol.
                #
                # This cannot use 'tatizo BaseException kama exc' (as kwenye the
                # async implementation) to maintain compatibility with
                # Python 2, where old-style kundi exceptions are sio caught
                # by 'tatizo BaseException'.
                ikiwa sys.exc_info()[1] ni value:
                    rudisha Uongo
                raise
            ashiria RuntimeError("generator didn't stop after throw()")


kundi _AsyncGeneratorContextManager(_GeneratorContextManagerBase,
                                    AbstractAsyncContextManager):
    """Helper kila @asynccontextmanager."""

    async eleza __aenter__(self):
        jaribu:
            rudisha await self.gen.__anext__()
        tatizo StopAsyncIteration:
            ashiria RuntimeError("generator didn't tuma") kutoka Tupu

    async eleza __aexit__(self, typ, value, traceback):
        ikiwa typ ni Tupu:
            jaribu:
                await self.gen.__anext__()
            tatizo StopAsyncIteration:
                return
            isipokua:
                ashiria RuntimeError("generator didn't stop")
        isipokua:
            ikiwa value ni Tupu:
                value = typ()
            # See _GeneratorContextManager.__exit__ kila comments on subtleties
            # kwenye this implementation
            jaribu:
                await self.gen.athrow(typ, value, traceback)
                ashiria RuntimeError("generator didn't stop after athrow()")
            tatizo StopAsyncIteration kama exc:
                rudisha exc ni sio value
            tatizo RuntimeError kama exc:
                ikiwa exc ni value:
                    rudisha Uongo
                # Avoid suppressing ikiwa a StopIteration exception
                # was pitaed to throw() na later wrapped into a RuntimeError
                # (see PEP 479 kila sync generators; async generators also
                # have this behavior). But do this only ikiwa the exception wrapped
                # by the RuntimeError ni actully Stop(Async)Iteration (see
                # issue29692).
                ikiwa isinstance(value, (StopIteration, StopAsyncIteration)):
                    ikiwa exc.__cause__ ni value:
                        rudisha Uongo
                raise
            tatizo BaseException kama exc:
                ikiwa exc ni sio value:
                    raise


eleza contextmanager(func):
    """@contextmanager decorator.

    Typical usage:

        @contextmanager
        eleza some_generator(<arguments>):
            <setup>
            jaribu:
                tuma <value>
            mwishowe:
                <cleanup>

    This makes this:

        ukijumuisha some_generator(<arguments>) kama <variable>:
            <body>

    equivalent to this:

        <setup>
        jaribu:
            <variable> = <value>
            <body>
        mwishowe:
            <cleanup>
    """
    @wraps(func)
    eleza helper(*args, **kwds):
        rudisha _GeneratorContextManager(func, args, kwds)
    rudisha helper


eleza asynccontextmanager(func):
    """@asynccontextmanager decorator.

    Typical usage:

        @asynccontextmanager
        async eleza some_async_generator(<arguments>):
            <setup>
            jaribu:
                tuma <value>
            mwishowe:
                <cleanup>

    This makes this:

        async ukijumuisha some_async_generator(<arguments>) kama <variable>:
            <body>

    equivalent to this:

        <setup>
        jaribu:
            <variable> = <value>
            <body>
        mwishowe:
            <cleanup>
    """
    @wraps(func)
    eleza helper(*args, **kwds):
        rudisha _AsyncGeneratorContextManager(func, args, kwds)
    rudisha helper


kundi closing(AbstractContextManager):
    """Context to automatically close something at the end of a block.

    Code like this:

        ukijumuisha closing(<module>.open(<arguments>)) kama f:
            <block>

    ni equivalent to this:

        f = <module>.open(<arguments>)
        jaribu:
            <block>
        mwishowe:
            f.close()

    """
    eleza __init__(self, thing):
        self.thing = thing
    eleza __enter__(self):
        rudisha self.thing
    eleza __exit__(self, *exc_info):
        self.thing.close()


kundi _RedirectStream(AbstractContextManager):

    _stream = Tupu

    eleza __init__(self, new_target):
        self._new_target = new_target
        # We use a list of old targets to make this CM re-entrant
        self._old_targets = []

    eleza __enter__(self):
        self._old_targets.append(getattr(sys, self._stream))
        setattr(sys, self._stream, self._new_target)
        rudisha self._new_target

    eleza __exit__(self, exctype, excinst, exctb):
        setattr(sys, self._stream, self._old_targets.pop())


kundi redirect_stdout(_RedirectStream):
    """Context manager kila temporarily redirecting stdout to another file.

        # How to send help() to stderr
        ukijumuisha redirect_stdout(sys.stderr):
            help(dir)

        # How to write help() to a file
        ukijumuisha open('help.txt', 'w') kama f:
            ukijumuisha redirect_stdout(f):
                help(pow)
    """

    _stream = "stdout"


kundi redirect_stderr(_RedirectStream):
    """Context manager kila temporarily redirecting stderr to another file."""

    _stream = "stderr"


kundi suppress(AbstractContextManager):
    """Context manager to suppress specified exceptions

    After the exception ni suppressed, execution proceeds ukijumuisha the next
    statement following the ukijumuisha statement.

         ukijumuisha suppress(FileNotFoundError):
             os.remove(somefile)
         # Execution still resumes here ikiwa the file was already removed
    """

    eleza __init__(self, *exceptions):
        self._exceptions = exceptions

    eleza __enter__(self):
        pita

    eleza __exit__(self, exctype, excinst, exctb):
        # Unlike isinstance na issubclass, CPython exception handling
        # currently only looks at the concrete type hierarchy (ignoring
        # the instance na subkundi checking hooks). While Guido considers
        # that a bug rather than a feature, it's a fairly hard one to fix
        # due to various internal implementation details. suppress provides
        # the simpler issubkundi based semantics, rather than trying to
        # exactly reproduce the limitations of the CPython interpreter.
        #
        # See http://bugs.python.org/issue12029 kila more details
        rudisha exctype ni sio Tupu na issubclass(exctype, self._exceptions)


kundi _BaseExitStack:
    """A base kundi kila ExitStack na AsyncExitStack."""

    @staticmethod
    eleza _create_exit_wrapper(cm, cm_exit):
        rudisha MethodType(cm_exit, cm)

    @staticmethod
    eleza _create_cb_wrapper(callback, /, *args, **kwds):
        eleza _exit_wrapper(exc_type, exc, tb):
            callback(*args, **kwds)
        rudisha _exit_wrapper

    eleza __init__(self):
        self._exit_callbacks = deque()

    eleza pop_all(self):
        """Preserve the context stack by transferring it to a new instance."""
        new_stack = type(self)()
        new_stack._exit_callbacks = self._exit_callbacks
        self._exit_callbacks = deque()
        rudisha new_stack

    eleza push(self, exit):
        """Registers a callback ukijumuisha the standard __exit__ method signature.

        Can suppress exceptions the same way __exit__ method can.
        Also accepts any object ukijumuisha an __exit__ method (registering a call
        to the method instead of the object itself).
        """
        # We use an unbound method rather than a bound method to follow
        # the standard lookup behaviour kila special methods.
        _cb_type = type(exit)

        jaribu:
            exit_method = _cb_type.__exit__
        tatizo AttributeError:
            # Not a context manager, so assume it's a callable.
            self._push_exit_callback(exit)
        isipokua:
            self._push_cm_exit(exit, exit_method)
        rudisha exit  # Allow use kama a decorator.

    eleza enter_context(self, cm):
        """Enters the supplied context manager.

        If successful, also pushes its __exit__ method kama a callback na
        returns the result of the __enter__ method.
        """
        # We look up the special methods on the type to match the with
        # statement.
        _cm_type = type(cm)
        _exit = _cm_type.__exit__
        result = _cm_type.__enter__(cm)
        self._push_cm_exit(cm, _exit)
        rudisha result

    eleza callback(*args, **kwds):
        """Registers an arbitrary callback na arguments.

        Cannot suppress exceptions.
        """
        ikiwa len(args) >= 2:
            self, callback, *args = args
        lasivyo sio args:
            ashiria TypeError("descriptor 'callback' of '_BaseExitStack' object "
                            "needs an argument")
        lasivyo 'callback' kwenye kwds:
            callback = kwds.pop('callback')
            self, *args = args
            agiza warnings
            warnings.warn("Passing 'callback' kama keyword argument ni deprecated",
                          DeprecationWarning, stacklevel=2)
        isipokua:
            ashiria TypeError('callback expected at least 1 positional argument, '
                            'got %d' % (len(args)-1))

        _exit_wrapper = self._create_cb_wrapper(callback, *args, **kwds)

        # We changed the signature, so using @wraps ni sio appropriate, but
        # setting __wrapped__ may still help ukijumuisha introspection.
        _exit_wrapper.__wrapped__ = callback
        self._push_exit_callback(_exit_wrapper)
        rudisha callback  # Allow use kama a decorator
    callback.__text_signature__ = '($self, callback, /, *args, **kwds)'

    eleza _push_cm_exit(self, cm, cm_exit):
        """Helper to correctly register callbacks to __exit__ methods."""
        _exit_wrapper = self._create_exit_wrapper(cm, cm_exit)
        self._push_exit_callback(_exit_wrapper, Kweli)

    eleza _push_exit_callback(self, callback, is_sync=Kweli):
        self._exit_callbacks.append((is_sync, callback))


# Inspired by discussions on http://bugs.python.org/issue13585
kundi ExitStack(_BaseExitStack, AbstractContextManager):
    """Context manager kila dynamic management of a stack of exit callbacks.

    For example:
        ukijumuisha ExitStack() kama stack:
            files = [stack.enter_context(open(fname)) kila fname kwenye filenames]
            # All opened files will automatically be closed at the end of
            # the ukijumuisha statement, even ikiwa attempts to open files later
            # kwenye the list ashiria an exception.
    """

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *exc_details):
        received_exc = exc_details[0] ni sio Tupu

        # We manipulate the exception state so it behaves kama though
        # we were actually nesting multiple ukijumuisha statements
        frame_exc = sys.exc_info()[1]
        eleza _fix_exception_context(new_exc, old_exc):
            # Context may sio be correct, so find the end of the chain
            wakati 1:
                exc_context = new_exc.__context__
                ikiwa exc_context ni old_exc:
                    # Context ni already set correctly (see issue 20317)
                    return
                ikiwa exc_context ni Tupu ama exc_context ni frame_exc:
                    koma
                new_exc = exc_context
            # Change the end of the chain to point to the exception
            # we expect it to reference
            new_exc.__context__ = old_exc

        # Callbacks are invoked kwenye LIFO order to match the behaviour of
        # nested context managers
        suppressed_exc = Uongo
        pending_ashiria = Uongo
        wakati self._exit_callbacks:
            is_sync, cb = self._exit_callbacks.pop()
            assert is_sync
            jaribu:
                ikiwa cb(*exc_details):
                    suppressed_exc = Kweli
                    pending_ashiria = Uongo
                    exc_details = (Tupu, Tupu, Tupu)
            tatizo:
                new_exc_details = sys.exc_info()
                # simulate the stack of exceptions by setting the context
                _fix_exception_context(new_exc_details[1], exc_details[1])
                pending_ashiria = Kweli
                exc_details = new_exc_details
        ikiwa pending_raise:
            jaribu:
                # bare "ashiria exc_details[1]" replaces our carefully
                # set-up context
                fixed_ctx = exc_details[1].__context__
                ashiria exc_details[1]
            tatizo BaseException:
                exc_details[1].__context__ = fixed_ctx
                raise
        rudisha received_exc na suppressed_exc

    eleza close(self):
        """Immediately unwind the context stack."""
        self.__exit__(Tupu, Tupu, Tupu)


# Inspired by discussions on https://bugs.python.org/issue29302
kundi AsyncExitStack(_BaseExitStack, AbstractAsyncContextManager):
    """Async context manager kila dynamic management of a stack of exit
    callbacks.

    For example:
        async ukijumuisha AsyncExitStack() kama stack:
            connections = [await stack.enter_async_context(get_connection())
                kila i kwenye range(5)]
            # All opened connections will automatically be released at the
            # end of the async ukijumuisha statement, even ikiwa attempts to open a
            # connection later kwenye the list ashiria an exception.
    """

    @staticmethod
    eleza _create_async_exit_wrapper(cm, cm_exit):
        rudisha MethodType(cm_exit, cm)

    @staticmethod
    eleza _create_async_cb_wrapper(callback, /, *args, **kwds):
        async eleza _exit_wrapper(exc_type, exc, tb):
            await callback(*args, **kwds)
        rudisha _exit_wrapper

    async eleza enter_async_context(self, cm):
        """Enters the supplied async context manager.

        If successful, also pushes its __aexit__ method kama a callback na
        returns the result of the __aenter__ method.
        """
        _cm_type = type(cm)
        _exit = _cm_type.__aexit__
        result = await _cm_type.__aenter__(cm)
        self._push_async_cm_exit(cm, _exit)
        rudisha result

    eleza push_async_exit(self, exit):
        """Registers a coroutine function ukijumuisha the standard __aexit__ method
        signature.

        Can suppress exceptions the same way __aexit__ method can.
        Also accepts any object ukijumuisha an __aexit__ method (registering a call
        to the method instead of the object itself).
        """
        _cb_type = type(exit)
        jaribu:
            exit_method = _cb_type.__aexit__
        tatizo AttributeError:
            # Not an async context manager, so assume it's a coroutine function
            self._push_exit_callback(exit, Uongo)
        isipokua:
            self._push_async_cm_exit(exit, exit_method)
        rudisha exit  # Allow use kama a decorator

    eleza push_async_callback(*args, **kwds):
        """Registers an arbitrary coroutine function na arguments.

        Cannot suppress exceptions.
        """
        ikiwa len(args) >= 2:
            self, callback, *args = args
        lasivyo sio args:
            ashiria TypeError("descriptor 'push_async_callback' of "
                            "'AsyncExitStack' object needs an argument")
        lasivyo 'callback' kwenye kwds:
            callback = kwds.pop('callback')
            self, *args = args
            agiza warnings
            warnings.warn("Passing 'callback' kama keyword argument ni deprecated",
                          DeprecationWarning, stacklevel=2)
        isipokua:
            ashiria TypeError('push_async_callback expected at least 1 '
                            'positional argument, got %d' % (len(args)-1))

        _exit_wrapper = self._create_async_cb_wrapper(callback, *args, **kwds)

        # We changed the signature, so using @wraps ni sio appropriate, but
        # setting __wrapped__ may still help ukijumuisha introspection.
        _exit_wrapper.__wrapped__ = callback
        self._push_exit_callback(_exit_wrapper, Uongo)
        rudisha callback  # Allow use kama a decorator
    push_async_callback.__text_signature__ = '($self, callback, /, *args, **kwds)'

    async eleza aclose(self):
        """Immediately unwind the context stack."""
        await self.__aexit__(Tupu, Tupu, Tupu)

    eleza _push_async_cm_exit(self, cm, cm_exit):
        """Helper to correctly register coroutine function to __aexit__
        method."""
        _exit_wrapper = self._create_async_exit_wrapper(cm, cm_exit)
        self._push_exit_callback(_exit_wrapper, Uongo)

    async eleza __aenter__(self):
        rudisha self

    async eleza __aexit__(self, *exc_details):
        received_exc = exc_details[0] ni sio Tupu

        # We manipulate the exception state so it behaves kama though
        # we were actually nesting multiple ukijumuisha statements
        frame_exc = sys.exc_info()[1]
        eleza _fix_exception_context(new_exc, old_exc):
            # Context may sio be correct, so find the end of the chain
            wakati 1:
                exc_context = new_exc.__context__
                ikiwa exc_context ni old_exc:
                    # Context ni already set correctly (see issue 20317)
                    return
                ikiwa exc_context ni Tupu ama exc_context ni frame_exc:
                    koma
                new_exc = exc_context
            # Change the end of the chain to point to the exception
            # we expect it to reference
            new_exc.__context__ = old_exc

        # Callbacks are invoked kwenye LIFO order to match the behaviour of
        # nested context managers
        suppressed_exc = Uongo
        pending_ashiria = Uongo
        wakati self._exit_callbacks:
            is_sync, cb = self._exit_callbacks.pop()
            jaribu:
                ikiwa is_sync:
                    cb_suppress = cb(*exc_details)
                isipokua:
                    cb_suppress = await cb(*exc_details)

                ikiwa cb_suppress:
                    suppressed_exc = Kweli
                    pending_ashiria = Uongo
                    exc_details = (Tupu, Tupu, Tupu)
            tatizo:
                new_exc_details = sys.exc_info()
                # simulate the stack of exceptions by setting the context
                _fix_exception_context(new_exc_details[1], exc_details[1])
                pending_ashiria = Kweli
                exc_details = new_exc_details
        ikiwa pending_raise:
            jaribu:
                # bare "ashiria exc_details[1]" replaces our carefully
                # set-up context
                fixed_ctx = exc_details[1].__context__
                ashiria exc_details[1]
            tatizo BaseException:
                exc_details[1].__context__ = fixed_ctx
                raise
        rudisha received_exc na suppressed_exc


kundi nullcontext(AbstractContextManager):
    """Context manager that does no additional processing.

    Used kama a stand-in kila a normal context manager, when a particular
    block of code ni only sometimes used ukijumuisha a normal context manager:

    cm = optional_cm ikiwa condition isipokua nullcontext()
    ukijumuisha cm:
        # Perform operation, using optional_cm ikiwa condition ni Kweli
    """

    eleza __init__(self, enter_result=Tupu):
        self.enter_result = enter_result

    eleza __enter__(self):
        rudisha self.enter_result

    eleza __exit__(self, *excinfo):
        pita
