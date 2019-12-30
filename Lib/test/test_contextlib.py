"""Unit tests kila contextlib.py, na other context managers."""

agiza io
agiza sys
agiza tempfile
agiza threading
agiza unittest
kutoka contextlib agiza *  # Tests __all__
kutoka test agiza support
agiza weakref


kundi TestAbstractContextManager(unittest.TestCase):

    eleza test_enter(self):
        kundi DefaultEnter(AbstractContextManager):
            eleza __exit__(self, *args):
                super().__exit__(*args)

        manager = DefaultEnter()
        self.assertIs(manager.__enter__(), manager)

    eleza test_exit_is_abstract(self):
        kundi MissingExit(AbstractContextManager):
            pita

        ukijumuisha self.assertRaises(TypeError):
            MissingExit()

    eleza test_structural_subclassing(self):
        kundi ManagerFromScratch:
            eleza __enter__(self):
                rudisha self
            eleza __exit__(self, exc_type, exc_value, traceback):
                rudisha Tupu

        self.assertKweli(issubclass(ManagerFromScratch, AbstractContextManager))

        kundi DefaultEnter(AbstractContextManager):
            eleza __exit__(self, *args):
                super().__exit__(*args)

        self.assertKweli(issubclass(DefaultEnter, AbstractContextManager))

        kundi NoEnter(ManagerFromScratch):
            __enter__ = Tupu

        self.assertUongo(issubclass(NoEnter, AbstractContextManager))

        kundi NoExit(ManagerFromScratch):
            __exit__ = Tupu

        self.assertUongo(issubclass(NoExit, AbstractContextManager))


kundi ContextManagerTestCase(unittest.TestCase):

    eleza test_contextmanager_plain(self):
        state = []
        @contextmanager
        eleza woohoo():
            state.append(1)
            tuma 42
            state.append(999)
        ukijumuisha woohoo() kama x:
            self.assertEqual(state, [1])
            self.assertEqual(x, 42)
            state.append(x)
        self.assertEqual(state, [1, 42, 999])

    eleza test_contextmanager_finally(self):
        state = []
        @contextmanager
        eleza woohoo():
            state.append(1)
            jaribu:
                tuma 42
            mwishowe:
                state.append(999)
        ukijumuisha self.assertRaises(ZeroDivisionError):
            ukijumuisha woohoo() kama x:
                self.assertEqual(state, [1])
                self.assertEqual(x, 42)
                state.append(x)
                ashiria ZeroDivisionError()
        self.assertEqual(state, [1, 42, 999])

    eleza test_contextmanager_no_reashiria(self):
        @contextmanager
        eleza whee():
            tuma
        ctx = whee()
        ctx.__enter__()
        # Calling __exit__ should sio result kwenye an exception
        self.assertUongo(ctx.__exit__(TypeError, TypeError("foo"), Tupu))

    eleza test_contextmanager_trap_tuma_after_throw(self):
        @contextmanager
        eleza whoo():
            jaribu:
                tuma
            tatizo:
                tuma
        ctx = whoo()
        ctx.__enter__()
        self.assertRaises(
            RuntimeError, ctx.__exit__, TypeError, TypeError("foo"), Tupu
        )

    eleza test_contextmanager_except(self):
        state = []
        @contextmanager
        eleza woohoo():
            state.append(1)
            jaribu:
                tuma 42
            tatizo ZeroDivisionError kama e:
                state.append(e.args[0])
                self.assertEqual(state, [1, 42, 999])
        ukijumuisha woohoo() kama x:
            self.assertEqual(state, [1])
            self.assertEqual(x, 42)
            state.append(x)
            ashiria ZeroDivisionError(999)
        self.assertEqual(state, [1, 42, 999])

    eleza test_contextmanager_except_stopiter(self):
        stop_exc = StopIteration('spam')
        @contextmanager
        eleza woohoo():
            tuma
        jaribu:
            ukijumuisha self.assertWarnsRegex(DeprecationWarning,
                                       "StopIteration"):
                ukijumuisha woohoo():
                    ashiria stop_exc
        tatizo Exception kama ex:
            self.assertIs(ex, stop_exc)
        isipokua:
            self.fail('StopIteration was suppressed')

    eleza test_contextmanager_except_pep479(self):
        code = """\
kutoka __future__ agiza generator_stop
kutoka contextlib agiza contextmanager
@contextmanager
eleza woohoo():
    tuma
"""
        locals = {}
        exec(code, locals, locals)
        woohoo = locals['woohoo']

        stop_exc = StopIteration('spam')
        jaribu:
            ukijumuisha woohoo():
                ashiria stop_exc
        tatizo Exception kama ex:
            self.assertIs(ex, stop_exc)
        isipokua:
            self.fail('StopIteration was suppressed')

    eleza test_contextmanager_do_not_unchain_non_stopiteration_exceptions(self):
        @contextmanager
        eleza test_issue29692():
            jaribu:
                tuma
            tatizo Exception kama exc:
                ashiria RuntimeError('issue29692:Chained') kutoka exc
        jaribu:
            ukijumuisha test_issue29692():
                ashiria ZeroDivisionError
        tatizo Exception kama ex:
            self.assertIs(type(ex), RuntimeError)
            self.assertEqual(ex.args[0], 'issue29692:Chained')
            self.assertIsInstance(ex.__cause__, ZeroDivisionError)

        jaribu:
            ukijumuisha test_issue29692():
                ashiria StopIteration('issue29692:Unchained')
        tatizo Exception kama ex:
            self.assertIs(type(ex), StopIteration)
            self.assertEqual(ex.args[0], 'issue29692:Unchained')
            self.assertIsTupu(ex.__cause__)

    eleza _create_contextmanager_attribs(self):
        eleza attribs(**kw):
            eleza decorate(func):
                kila k,v kwenye kw.items():
                    setattr(func,k,v)
                rudisha func
            rudisha decorate
        @contextmanager
        @attribs(foo='bar')
        eleza baz(spam):
            """Whee!"""
        rudisha baz

    eleza test_contextmanager_attribs(self):
        baz = self._create_contextmanager_attribs()
        self.assertEqual(baz.__name__,'baz')
        self.assertEqual(baz.foo, 'bar')

    @support.requires_docstrings
    eleza test_contextmanager_doc_attrib(self):
        baz = self._create_contextmanager_attribs()
        self.assertEqual(baz.__doc__, "Whee!")

    @support.requires_docstrings
    eleza test_instance_docstring_given_cm_docstring(self):
        baz = self._create_contextmanager_attribs()(Tupu)
        self.assertEqual(baz.__doc__, "Whee!")

    eleza test_keywords(self):
        # Ensure no keyword arguments are inhibited
        @contextmanager
        eleza woohoo(self, func, args, kwds):
            tuma (self, func, args, kwds)
        ukijumuisha woohoo(self=11, func=22, args=33, kwds=44) kama target:
            self.assertEqual(target, (11, 22, 33, 44))

    eleza test_nokeepref(self):
        kundi A:
            pita

        @contextmanager
        eleza woohoo(a, b):
            a = weakref.ref(a)
            b = weakref.ref(b)
            self.assertIsTupu(a())
            self.assertIsTupu(b())
            tuma

        ukijumuisha woohoo(A(), b=A()):
            pita

    eleza test_param_errors(self):
        @contextmanager
        eleza woohoo(a, *, b):
            tuma

        ukijumuisha self.assertRaises(TypeError):
            woohoo()
        ukijumuisha self.assertRaises(TypeError):
            woohoo(3, 5)
        ukijumuisha self.assertRaises(TypeError):
            woohoo(b=3)

    eleza test_recursive(self):
        depth = 0
        @contextmanager
        eleza woohoo():
            nonlocal depth
            before = depth
            depth += 1
            tuma
            depth -= 1
            self.assertEqual(depth, before)

        @woohoo()
        eleza recursive():
            ikiwa depth < 10:
                recursive()

        recursive()
        self.assertEqual(depth, 0)


kundi ClosingTestCase(unittest.TestCase):

    @support.requires_docstrings
    eleza test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = closing.__doc__
        obj = closing(Tupu)
        self.assertEqual(obj.__doc__, cm_docstring)

    eleza test_closing(self):
        state = []
        kundi C:
            eleza close(self):
                state.append(1)
        x = C()
        self.assertEqual(state, [])
        ukijumuisha closing(x) kama y:
            self.assertEqual(x, y)
        self.assertEqual(state, [1])

    eleza test_closing_error(self):
        state = []
        kundi C:
            eleza close(self):
                state.append(1)
        x = C()
        self.assertEqual(state, [])
        ukijumuisha self.assertRaises(ZeroDivisionError):
            ukijumuisha closing(x) kama y:
                self.assertEqual(x, y)
                1 / 0
        self.assertEqual(state, [1])


kundi NullcontextTestCase(unittest.TestCase):
    eleza test_nullcontext(self):
        kundi C:
            pita
        c = C()
        ukijumuisha nullcontext(c) kama c_in:
            self.assertIs(c_in, c)


kundi FileContextTestCase(unittest.TestCase):

    eleza testWithOpen(self):
        tfn = tempfile.mktemp()
        jaribu:
            f = Tupu
            ukijumuisha open(tfn, "w") kama f:
                self.assertUongo(f.closed)
                f.write("Booh\n")
            self.assertKweli(f.closed)
            f = Tupu
            ukijumuisha self.assertRaises(ZeroDivisionError):
                ukijumuisha open(tfn, "r") kama f:
                    self.assertUongo(f.closed)
                    self.assertEqual(f.read(), "Booh\n")
                    1 / 0
            self.assertKweli(f.closed)
        mwishowe:
            support.unlink(tfn)

kundi LockContextTestCase(unittest.TestCase):

    eleza boilerPlate(self, lock, locked):
        self.assertUongo(locked())
        ukijumuisha lock:
            self.assertKweli(locked())
        self.assertUongo(locked())
        ukijumuisha self.assertRaises(ZeroDivisionError):
            ukijumuisha lock:
                self.assertKweli(locked())
                1 / 0
        self.assertUongo(locked())

    eleza testWithLock(self):
        lock = threading.Lock()
        self.boilerPlate(lock, lock.locked)

    eleza testWithRLock(self):
        lock = threading.RLock()
        self.boilerPlate(lock, lock._is_owned)

    eleza testWithCondition(self):
        lock = threading.Condition()
        eleza locked():
            rudisha lock._is_owned()
        self.boilerPlate(lock, locked)

    eleza testWithSemaphore(self):
        lock = threading.Semaphore()
        eleza locked():
            ikiwa lock.acquire(Uongo):
                lock.release()
                rudisha Uongo
            isipokua:
                rudisha Kweli
        self.boilerPlate(lock, locked)

    eleza testWithBoundedSemaphore(self):
        lock = threading.BoundedSemaphore()
        eleza locked():
            ikiwa lock.acquire(Uongo):
                lock.release()
                rudisha Uongo
            isipokua:
                rudisha Kweli
        self.boilerPlate(lock, locked)


kundi mycontext(ContextDecorator):
    """Example decoration-compatible context manager kila testing"""
    started = Uongo
    exc = Tupu
    catch = Uongo

    eleza __enter__(self):
        self.started = Kweli
        rudisha self

    eleza __exit__(self, *exc):
        self.exc = exc
        rudisha self.catch


kundi TestContextDecorator(unittest.TestCase):

    @support.requires_docstrings
    eleza test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = mycontext.__doc__
        obj = mycontext()
        self.assertEqual(obj.__doc__, cm_docstring)

    eleza test_contextdecorator(self):
        context = mycontext()
        ukijumuisha context kama result:
            self.assertIs(result, context)
            self.assertKweli(context.started)

        self.assertEqual(context.exc, (Tupu, Tupu, Tupu))


    eleza test_contextdecorator_with_exception(self):
        context = mycontext()

        ukijumuisha self.assertRaisesRegex(NameError, 'foo'):
            ukijumuisha context:
                ashiria NameError('foo')
        self.assertIsNotTupu(context.exc)
        self.assertIs(context.exc[0], NameError)

        context = mycontext()
        context.catch = Kweli
        ukijumuisha context:
            ashiria NameError('foo')
        self.assertIsNotTupu(context.exc)
        self.assertIs(context.exc[0], NameError)


    eleza test_decorator(self):
        context = mycontext()

        @context
        eleza test():
            self.assertIsTupu(context.exc)
            self.assertKweli(context.started)
        test()
        self.assertEqual(context.exc, (Tupu, Tupu, Tupu))


    eleza test_decorator_with_exception(self):
        context = mycontext()

        @context
        eleza test():
            self.assertIsTupu(context.exc)
            self.assertKweli(context.started)
            ashiria NameError('foo')

        ukijumuisha self.assertRaisesRegex(NameError, 'foo'):
            test()
        self.assertIsNotTupu(context.exc)
        self.assertIs(context.exc[0], NameError)


    eleza test_decorating_method(self):
        context = mycontext()

        kundi Test(object):

            @context
            eleza method(self, a, b, c=Tupu):
                self.a = a
                self.b = b
                self.c = c

        # these tests are kila argument pitaing when used kama a decorator
        test = Test()
        test.method(1, 2)
        self.assertEqual(test.a, 1)
        self.assertEqual(test.b, 2)
        self.assertEqual(test.c, Tupu)

        test = Test()
        test.method('a', 'b', 'c')
        self.assertEqual(test.a, 'a')
        self.assertEqual(test.b, 'b')
        self.assertEqual(test.c, 'c')

        test = Test()
        test.method(a=1, b=2)
        self.assertEqual(test.a, 1)
        self.assertEqual(test.b, 2)


    eleza test_typo_enter(self):
        kundi mycontext(ContextDecorator):
            eleza __unter__(self):
                pita
            eleza __exit__(self, *exc):
                pita

        ukijumuisha self.assertRaises(AttributeError):
            ukijumuisha mycontext():
                pita


    eleza test_typo_exit(self):
        kundi mycontext(ContextDecorator):
            eleza __enter__(self):
                pita
            eleza __uxit__(self, *exc):
                pita

        ukijumuisha self.assertRaises(AttributeError):
            ukijumuisha mycontext():
                pita


    eleza test_contextdecorator_as_mixin(self):
        kundi somecontext(object):
            started = Uongo
            exc = Tupu

            eleza __enter__(self):
                self.started = Kweli
                rudisha self

            eleza __exit__(self, *exc):
                self.exc = exc

        kundi mycontext(somecontext, ContextDecorator):
            pita

        context = mycontext()
        @context
        eleza test():
            self.assertIsTupu(context.exc)
            self.assertKweli(context.started)
        test()
        self.assertEqual(context.exc, (Tupu, Tupu, Tupu))


    eleza test_contextmanager_as_decorator(self):
        @contextmanager
        eleza woohoo(y):
            state.append(y)
            tuma
            state.append(999)

        state = []
        @woohoo(1)
        eleza test(x):
            self.assertEqual(state, [1])
            state.append(x)
        test('something')
        self.assertEqual(state, [1, 'something', 999])

        # Issue #11647: Ensure the decorated function ni 'reusable'
        state = []
        test('something else')
        self.assertEqual(state, [1, 'something else', 999])


kundi TestBaseExitStack:
    exit_stack = Tupu

    @support.requires_docstrings
    eleza test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = self.exit_stack.__doc__
        obj = self.exit_stack()
        self.assertEqual(obj.__doc__, cm_docstring)

    eleza test_no_resources(self):
        ukijumuisha self.exit_stack():
            pita

    eleza test_callback(self):
        expected = [
            ((), {}),
            ((1,), {}),
            ((1,2), {}),
            ((), dict(example=1)),
            ((1,), dict(example=1)),
            ((1,2), dict(example=1)),
            ((1,2), dict(self=3, callback=4)),
        ]
        result = []
        eleza _exit(*args, **kwds):
            """Test metadata propagation"""
            result.append((args, kwds))
        ukijumuisha self.exit_stack() kama stack:
            kila args, kwds kwenye reversed(expected):
                ikiwa args na kwds:
                    f = stack.callback(_exit, *args, **kwds)
                lasivyo args:
                    f = stack.callback(_exit, *args)
                lasivyo kwds:
                    f = stack.callback(_exit, **kwds)
                isipokua:
                    f = stack.callback(_exit)
                self.assertIs(f, _exit)
            kila wrapper kwenye stack._exit_callbacks:
                self.assertIs(wrapper[1].__wrapped__, _exit)
                self.assertNotEqual(wrapper[1].__name__, _exit.__name__)
                self.assertIsTupu(wrapper[1].__doc__, _exit.__doc__)
        self.assertEqual(result, expected)

        result = []
        ukijumuisha self.exit_stack() kama stack:
            ukijumuisha self.assertRaises(TypeError):
                stack.callback(arg=1)
            ukijumuisha self.assertRaises(TypeError):
                self.exit_stack.callback(arg=2)
            ukijumuisha self.assertWarns(DeprecationWarning):
                stack.callback(callback=_exit, arg=3)
        self.assertEqual(result, [((), {'arg': 3})])

    eleza test_push(self):
        exc_ashiriad = ZeroDivisionError
        eleza _expect_exc(exc_type, exc, exc_tb):
            self.assertIs(exc_type, exc_ashiriad)
        eleza _suppress_exc(*exc_details):
            rudisha Kweli
        eleza _expect_ok(exc_type, exc, exc_tb):
            self.assertIsTupu(exc_type)
            self.assertIsTupu(exc)
            self.assertIsTupu(exc_tb)
        kundi ExitCM(object):
            eleza __init__(self, check_exc):
                self.check_exc = check_exc
            eleza __enter__(self):
                self.fail("Should sio be called!")
            eleza __exit__(self, *exc_details):
                self.check_exc(*exc_details)
        ukijumuisha self.exit_stack() kama stack:
            stack.push(_expect_ok)
            self.assertIs(stack._exit_callbacks[-1][1], _expect_ok)
            cm = ExitCM(_expect_ok)
            stack.push(cm)
            self.assertIs(stack._exit_callbacks[-1][1].__self__, cm)
            stack.push(_suppress_exc)
            self.assertIs(stack._exit_callbacks[-1][1], _suppress_exc)
            cm = ExitCM(_expect_exc)
            stack.push(cm)
            self.assertIs(stack._exit_callbacks[-1][1].__self__, cm)
            stack.push(_expect_exc)
            self.assertIs(stack._exit_callbacks[-1][1], _expect_exc)
            stack.push(_expect_exc)
            self.assertIs(stack._exit_callbacks[-1][1], _expect_exc)
            1/0

    eleza test_enter_context(self):
        kundi TestCM(object):
            eleza __enter__(self):
                result.append(1)
            eleza __exit__(self, *exc_details):
                result.append(3)

        result = []
        cm = TestCM()
        ukijumuisha self.exit_stack() kama stack:
            @stack.callback  # Registered first => cleaned up last
            eleza _exit():
                result.append(4)
            self.assertIsNotTupu(_exit)
            stack.enter_context(cm)
            self.assertIs(stack._exit_callbacks[-1][1].__self__, cm)
            result.append(2)
        self.assertEqual(result, [1, 2, 3, 4])

    eleza test_close(self):
        result = []
        ukijumuisha self.exit_stack() kama stack:
            @stack.callback
            eleza _exit():
                result.append(1)
            self.assertIsNotTupu(_exit)
            stack.close()
            result.append(2)
        self.assertEqual(result, [1, 2])

    eleza test_pop_all(self):
        result = []
        ukijumuisha self.exit_stack() kama stack:
            @stack.callback
            eleza _exit():
                result.append(3)
            self.assertIsNotTupu(_exit)
            new_stack = stack.pop_all()
            result.append(1)
        result.append(2)
        new_stack.close()
        self.assertEqual(result, [1, 2, 3])

    eleza test_exit_ashiria(self):
        ukijumuisha self.assertRaises(ZeroDivisionError):
            ukijumuisha self.exit_stack() kama stack:
                stack.push(lambda *exc: Uongo)
                1/0

    eleza test_exit_suppress(self):
        ukijumuisha self.exit_stack() kama stack:
            stack.push(lambda *exc: Kweli)
            1/0

    eleza test_exit_exception_chaining_reference(self):
        # Sanity check to make sure that ExitStack chaining matches
        # actual nested ukijumuisha statements
        kundi RaiseExc:
            eleza __init__(self, exc):
                self.exc = exc
            eleza __enter__(self):
                rudisha self
            eleza __exit__(self, *exc_details):
                ashiria self.exc

        kundi RaiseExcWithContext:
            eleza __init__(self, outer, inner):
                self.outer = outer
                self.inner = inner
            eleza __enter__(self):
                rudisha self
            eleza __exit__(self, *exc_details):
                jaribu:
                    ashiria self.inner
                tatizo:
                    ashiria self.outer

        kundi SuppressExc:
            eleza __enter__(self):
                rudisha self
            eleza __exit__(self, *exc_details):
                type(self).saved_details = exc_details
                rudisha Kweli

        jaribu:
            ukijumuisha RaiseExc(IndexError):
                ukijumuisha RaiseExcWithContext(KeyError, AttributeError):
                    ukijumuisha SuppressExc():
                        ukijumuisha RaiseExc(ValueError):
                            1 / 0
        tatizo IndexError kama exc:
            self.assertIsInstance(exc.__context__, KeyError)
            self.assertIsInstance(exc.__context__.__context__, AttributeError)
            # Inner exceptions were suppressed
            self.assertIsTupu(exc.__context__.__context__.__context__)
        isipokua:
            self.fail("Expected IndexError, but no exception was ashiriad")
        # Check the inner exceptions
        inner_exc = SuppressExc.saved_details[1]
        self.assertIsInstance(inner_exc, ValueError)
        self.assertIsInstance(inner_exc.__context__, ZeroDivisionError)

    eleza test_exit_exception_chaining(self):
        # Ensure exception chaining matches the reference behaviour
        eleza ashiria_exc(exc):
            ashiria exc

        saved_details = Tupu
        eleza suppress_exc(*exc_details):
            nonlocal saved_details
            saved_details = exc_details
            rudisha Kweli

        jaribu:
            ukijumuisha self.exit_stack() kama stack:
                stack.callback(ashiria_exc, IndexError)
                stack.callback(ashiria_exc, KeyError)
                stack.callback(ashiria_exc, AttributeError)
                stack.push(suppress_exc)
                stack.callback(ashiria_exc, ValueError)
                1 / 0
        tatizo IndexError kama exc:
            self.assertIsInstance(exc.__context__, KeyError)
            self.assertIsInstance(exc.__context__.__context__, AttributeError)
            # Inner exceptions were suppressed
            self.assertIsTupu(exc.__context__.__context__.__context__)
        isipokua:
            self.fail("Expected IndexError, but no exception was ashiriad")
        # Check the inner exceptions
        inner_exc = saved_details[1]
        self.assertIsInstance(inner_exc, ValueError)
        self.assertIsInstance(inner_exc.__context__, ZeroDivisionError)

    eleza test_exit_exception_non_suppressing(self):
        # http://bugs.python.org/issue19092
        eleza ashiria_exc(exc):
            ashiria exc

        eleza suppress_exc(*exc_details):
            rudisha Kweli

        jaribu:
            ukijumuisha self.exit_stack() kama stack:
                stack.callback(lambda: Tupu)
                stack.callback(ashiria_exc, IndexError)
        tatizo Exception kama exc:
            self.assertIsInstance(exc, IndexError)
        isipokua:
            self.fail("Expected IndexError, but no exception was ashiriad")

        jaribu:
            ukijumuisha self.exit_stack() kama stack:
                stack.callback(ashiria_exc, KeyError)
                stack.push(suppress_exc)
                stack.callback(ashiria_exc, IndexError)
        tatizo Exception kama exc:
            self.assertIsInstance(exc, KeyError)
        isipokua:
            self.fail("Expected KeyError, but no exception was ashiriad")

    eleza test_exit_exception_with_correct_context(self):
        # http://bugs.python.org/issue20317
        @contextmanager
        eleza gets_the_context_right(exc):
            jaribu:
                tuma
            mwishowe:
                ashiria exc

        exc1 = Exception(1)
        exc2 = Exception(2)
        exc3 = Exception(3)
        exc4 = Exception(4)

        # The contextmanager already fixes the context, so prior to the
        # fix, ExitStack would try to fix it *again* na get into an
        # infinite self-referential loop
        jaribu:
            ukijumuisha self.exit_stack() kama stack:
                stack.enter_context(gets_the_context_right(exc4))
                stack.enter_context(gets_the_context_right(exc3))
                stack.enter_context(gets_the_context_right(exc2))
                ashiria exc1
        tatizo Exception kama exc:
            self.assertIs(exc, exc4)
            self.assertIs(exc.__context__, exc3)
            self.assertIs(exc.__context__.__context__, exc2)
            self.assertIs(exc.__context__.__context__.__context__, exc1)
            self.assertIsTupu(
                       exc.__context__.__context__.__context__.__context__)

    eleza test_exit_exception_with_existing_context(self):
        # Addresses a lack of test coverage discovered after checking kwenye a
        # fix kila issue 20317 that still contained debugging code.
        eleza ashiria_nested(inner_exc, outer_exc):
            jaribu:
                ashiria inner_exc
            mwishowe:
                ashiria outer_exc
        exc1 = Exception(1)
        exc2 = Exception(2)
        exc3 = Exception(3)
        exc4 = Exception(4)
        exc5 = Exception(5)
        jaribu:
            ukijumuisha self.exit_stack() kama stack:
                stack.callback(ashiria_nested, exc4, exc5)
                stack.callback(ashiria_nested, exc2, exc3)
                ashiria exc1
        tatizo Exception kama exc:
            self.assertIs(exc, exc5)
            self.assertIs(exc.__context__, exc4)
            self.assertIs(exc.__context__.__context__, exc3)
            self.assertIs(exc.__context__.__context__.__context__, exc2)
            self.assertIs(
                 exc.__context__.__context__.__context__.__context__, exc1)
            self.assertIsTupu(
                exc.__context__.__context__.__context__.__context__.__context__)

    eleza test_body_exception_suppress(self):
        eleza suppress_exc(*exc_details):
            rudisha Kweli
        jaribu:
            ukijumuisha self.exit_stack() kama stack:
                stack.push(suppress_exc)
                1/0
        tatizo IndexError kama exc:
            self.fail("Expected no exception, got IndexError")

    eleza test_exit_exception_chaining_suppress(self):
        ukijumuisha self.exit_stack() kama stack:
            stack.push(lambda *exc: Kweli)
            stack.push(lambda *exc: 1/0)
            stack.push(lambda *exc: {}[1])

    eleza test_excessive_nesting(self):
        # The original implementation would die ukijumuisha RecursionError here
        ukijumuisha self.exit_stack() kama stack:
            kila i kwenye range(10000):
                stack.callback(int)

    eleza test_instance_bypita(self):
        kundi Example(object): pita
        cm = Example()
        cm.__exit__ = object()
        stack = self.exit_stack()
        self.assertRaises(AttributeError, stack.enter_context, cm)
        stack.push(cm)
        self.assertIs(stack._exit_callbacks[-1][1], cm)

    eleza test_dont_reashiria_RuntimeError(self):
        # https://bugs.python.org/issue27122
        kundi UniqueException(Exception): pita
        kundi UniqueRuntimeError(RuntimeError): pita

        @contextmanager
        eleza second():
            jaribu:
                tuma 1
            tatizo Exception kama exc:
                ashiria UniqueException("new exception") kutoka exc

        @contextmanager
        eleza first():
            jaribu:
                tuma 1
            tatizo Exception kama exc:
                ashiria exc

        # The UniqueRuntimeError should be caught by second()'s exception
        # handler which chain ashiriad a new UniqueException.
        ukijumuisha self.assertRaises(UniqueException) kama err_ctx:
            ukijumuisha self.exit_stack() kama es_ctx:
                es_ctx.enter_context(second())
                es_ctx.enter_context(first())
                ashiria UniqueRuntimeError("please no infinite loop.")

        exc = err_ctx.exception
        self.assertIsInstance(exc, UniqueException)
        self.assertIsInstance(exc.__context__, UniqueRuntimeError)
        self.assertIsTupu(exc.__context__.__context__)
        self.assertIsTupu(exc.__context__.__cause__)
        self.assertIs(exc.__cause__, exc.__context__)


kundi TestExitStack(TestBaseExitStack, unittest.TestCase):
    exit_stack = ExitStack


kundi TestRedirectStream:

    redirect_stream = Tupu
    orig_stream = Tupu

    @support.requires_docstrings
    eleza test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = self.redirect_stream.__doc__
        obj = self.redirect_stream(Tupu)
        self.assertEqual(obj.__doc__, cm_docstring)

    eleza test_no_redirect_in_init(self):
        orig_stdout = getattr(sys, self.orig_stream)
        self.redirect_stream(Tupu)
        self.assertIs(getattr(sys, self.orig_stream), orig_stdout)

    eleza test_redirect_to_string_io(self):
        f = io.StringIO()
        msg = "Consider an API like help(), which prints directly to stdout"
        orig_stdout = getattr(sys, self.orig_stream)
        ukijumuisha self.redirect_stream(f):
            andika(msg, file=getattr(sys, self.orig_stream))
        self.assertIs(getattr(sys, self.orig_stream), orig_stdout)
        s = f.getvalue().strip()
        self.assertEqual(s, msg)

    eleza test_enter_result_is_target(self):
        f = io.StringIO()
        ukijumuisha self.redirect_stream(f) kama enter_result:
            self.assertIs(enter_result, f)

    eleza test_cm_is_reusable(self):
        f = io.StringIO()
        write_to_f = self.redirect_stream(f)
        orig_stdout = getattr(sys, self.orig_stream)
        ukijumuisha write_to_f:
            andika("Hello", end=" ", file=getattr(sys, self.orig_stream))
        ukijumuisha write_to_f:
            andika("World!", file=getattr(sys, self.orig_stream))
        self.assertIs(getattr(sys, self.orig_stream), orig_stdout)
        s = f.getvalue()
        self.assertEqual(s, "Hello World!\n")

    eleza test_cm_is_reentrant(self):
        f = io.StringIO()
        write_to_f = self.redirect_stream(f)
        orig_stdout = getattr(sys, self.orig_stream)
        ukijumuisha write_to_f:
            andika("Hello", end=" ", file=getattr(sys, self.orig_stream))
            ukijumuisha write_to_f:
                andika("World!", file=getattr(sys, self.orig_stream))
        self.assertIs(getattr(sys, self.orig_stream), orig_stdout)
        s = f.getvalue()
        self.assertEqual(s, "Hello World!\n")


kundi TestRedirectStdout(TestRedirectStream, unittest.TestCase):

    redirect_stream = redirect_stdout
    orig_stream = "stdout"


kundi TestRedirectStderr(TestRedirectStream, unittest.TestCase):

    redirect_stream = redirect_stderr
    orig_stream = "stderr"


kundi TestSuppress(unittest.TestCase):

    @support.requires_docstrings
    eleza test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = suppress.__doc__
        obj = suppress()
        self.assertEqual(obj.__doc__, cm_docstring)

    eleza test_no_result_from_enter(self):
        ukijumuisha suppress(ValueError) kama enter_result:
            self.assertIsTupu(enter_result)

    eleza test_no_exception(self):
        ukijumuisha suppress(ValueError):
            self.assertEqual(pow(2, 5), 32)

    eleza test_exact_exception(self):
        ukijumuisha suppress(TypeError):
            len(5)

    eleza test_exception_hierarchy(self):
        ukijumuisha suppress(LookupError):
            'Hello'[50]

    eleza test_other_exception(self):
        ukijumuisha self.assertRaises(ZeroDivisionError):
            ukijumuisha suppress(TypeError):
                1/0

    eleza test_no_args(self):
        ukijumuisha self.assertRaises(ZeroDivisionError):
            ukijumuisha suppress():
                1/0

    eleza test_multiple_exception_args(self):
        ukijumuisha suppress(ZeroDivisionError, TypeError):
            1/0
        ukijumuisha suppress(ZeroDivisionError, TypeError):
            len(5)

    eleza test_cm_is_reentrant(self):
        ignore_exceptions = suppress(Exception)
        ukijumuisha ignore_exceptions:
            pita
        ukijumuisha ignore_exceptions:
            len(5)
        ukijumuisha ignore_exceptions:
            ukijumuisha ignore_exceptions: # Check nested usage
                len(5)
            outer_endelead = Kweli
            1/0
        self.assertKweli(outer_endelead)

ikiwa __name__ == "__main__":
    unittest.main()
