"""Unit tests for contextlib.py, and other context managers."""

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
            pass

        with self.assertRaises(TypeError):
            MissingExit()

    eleza test_structural_subclassing(self):
        kundi ManagerFromScratch:
            eleza __enter__(self):
                rudisha self
            eleza __exit__(self, exc_type, exc_value, traceback):
                rudisha None

        self.assertTrue(issubclass(ManagerFromScratch, AbstractContextManager))

        kundi DefaultEnter(AbstractContextManager):
            eleza __exit__(self, *args):
                super().__exit__(*args)

        self.assertTrue(issubclass(DefaultEnter, AbstractContextManager))

        kundi NoEnter(ManagerFromScratch):
            __enter__ = None

        self.assertFalse(issubclass(NoEnter, AbstractContextManager))

        kundi NoExit(ManagerFromScratch):
            __exit__ = None

        self.assertFalse(issubclass(NoExit, AbstractContextManager))


kundi ContextManagerTestCase(unittest.TestCase):

    eleza test_contextmanager_plain(self):
        state = []
        @contextmanager
        eleza woohoo():
            state.append(1)
            yield 42
            state.append(999)
        with woohoo() as x:
            self.assertEqual(state, [1])
            self.assertEqual(x, 42)
            state.append(x)
        self.assertEqual(state, [1, 42, 999])

    eleza test_contextmanager_finally(self):
        state = []
        @contextmanager
        eleza woohoo():
            state.append(1)
            try:
                yield 42
            finally:
                state.append(999)
        with self.assertRaises(ZeroDivisionError):
            with woohoo() as x:
                self.assertEqual(state, [1])
                self.assertEqual(x, 42)
                state.append(x)
                raise ZeroDivisionError()
        self.assertEqual(state, [1, 42, 999])

    eleza test_contextmanager_no_reraise(self):
        @contextmanager
        eleza whee():
            yield
        ctx = whee()
        ctx.__enter__()
        # Calling __exit__ should not result in an exception
        self.assertFalse(ctx.__exit__(TypeError, TypeError("foo"), None))

    eleza test_contextmanager_trap_yield_after_throw(self):
        @contextmanager
        eleza whoo():
            try:
                yield
            except:
                yield
        ctx = whoo()
        ctx.__enter__()
        self.assertRaises(
            RuntimeError, ctx.__exit__, TypeError, TypeError("foo"), None
        )

    eleza test_contextmanager_except(self):
        state = []
        @contextmanager
        eleza woohoo():
            state.append(1)
            try:
                yield 42
            except ZeroDivisionError as e:
                state.append(e.args[0])
                self.assertEqual(state, [1, 42, 999])
        with woohoo() as x:
            self.assertEqual(state, [1])
            self.assertEqual(x, 42)
            state.append(x)
            raise ZeroDivisionError(999)
        self.assertEqual(state, [1, 42, 999])

    eleza test_contextmanager_except_stopiter(self):
        stop_exc = StopIteration('spam')
        @contextmanager
        eleza woohoo():
            yield
        try:
            with self.assertWarnsRegex(DeprecationWarning,
                                       "StopIteration"):
                with woohoo():
                    raise stop_exc
        except Exception as ex:
            self.assertIs(ex, stop_exc)
        else:
            self.fail('StopIteration was suppressed')

    eleza test_contextmanager_except_pep479(self):
        code = """\
kutoka __future__ agiza generator_stop
kutoka contextlib agiza contextmanager
@contextmanager
eleza woohoo():
    yield
"""
        locals = {}
        exec(code, locals, locals)
        woohoo = locals['woohoo']

        stop_exc = StopIteration('spam')
        try:
            with woohoo():
                raise stop_exc
        except Exception as ex:
            self.assertIs(ex, stop_exc)
        else:
            self.fail('StopIteration was suppressed')

    eleza test_contextmanager_do_not_unchain_non_stopiteration_exceptions(self):
        @contextmanager
        eleza test_issue29692():
            try:
                yield
            except Exception as exc:
                raise RuntimeError('issue29692:Chained') kutoka exc
        try:
            with test_issue29692():
                raise ZeroDivisionError
        except Exception as ex:
            self.assertIs(type(ex), RuntimeError)
            self.assertEqual(ex.args[0], 'issue29692:Chained')
            self.assertIsInstance(ex.__cause__, ZeroDivisionError)

        try:
            with test_issue29692():
                raise StopIteration('issue29692:Unchained')
        except Exception as ex:
            self.assertIs(type(ex), StopIteration)
            self.assertEqual(ex.args[0], 'issue29692:Unchained')
            self.assertIsNone(ex.__cause__)

    eleza _create_contextmanager_attribs(self):
        eleza attribs(**kw):
            eleza decorate(func):
                for k,v in kw.items():
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
        baz = self._create_contextmanager_attribs()(None)
        self.assertEqual(baz.__doc__, "Whee!")

    eleza test_keywords(self):
        # Ensure no keyword arguments are inhibited
        @contextmanager
        eleza woohoo(self, func, args, kwds):
            yield (self, func, args, kwds)
        with woohoo(self=11, func=22, args=33, kwds=44) as target:
            self.assertEqual(target, (11, 22, 33, 44))

    eleza test_nokeepref(self):
        kundi A:
            pass

        @contextmanager
        eleza woohoo(a, b):
            a = weakref.ref(a)
            b = weakref.ref(b)
            self.assertIsNone(a())
            self.assertIsNone(b())
            yield

        with woohoo(A(), b=A()):
            pass

    eleza test_param_errors(self):
        @contextmanager
        eleza woohoo(a, *, b):
            yield

        with self.assertRaises(TypeError):
            woohoo()
        with self.assertRaises(TypeError):
            woohoo(3, 5)
        with self.assertRaises(TypeError):
            woohoo(b=3)

    eleza test_recursive(self):
        depth = 0
        @contextmanager
        eleza woohoo():
            nonlocal depth
            before = depth
            depth += 1
            yield
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
        obj = closing(None)
        self.assertEqual(obj.__doc__, cm_docstring)

    eleza test_closing(self):
        state = []
        kundi C:
            eleza close(self):
                state.append(1)
        x = C()
        self.assertEqual(state, [])
        with closing(x) as y:
            self.assertEqual(x, y)
        self.assertEqual(state, [1])

    eleza test_closing_error(self):
        state = []
        kundi C:
            eleza close(self):
                state.append(1)
        x = C()
        self.assertEqual(state, [])
        with self.assertRaises(ZeroDivisionError):
            with closing(x) as y:
                self.assertEqual(x, y)
                1 / 0
        self.assertEqual(state, [1])


kundi NullcontextTestCase(unittest.TestCase):
    eleza test_nullcontext(self):
        kundi C:
            pass
        c = C()
        with nullcontext(c) as c_in:
            self.assertIs(c_in, c)


kundi FileContextTestCase(unittest.TestCase):

    eleza testWithOpen(self):
        tfn = tempfile.mktemp()
        try:
            f = None
            with open(tfn, "w") as f:
                self.assertFalse(f.closed)
                f.write("Booh\n")
            self.assertTrue(f.closed)
            f = None
            with self.assertRaises(ZeroDivisionError):
                with open(tfn, "r") as f:
                    self.assertFalse(f.closed)
                    self.assertEqual(f.read(), "Booh\n")
                    1 / 0
            self.assertTrue(f.closed)
        finally:
            support.unlink(tfn)

kundi LockContextTestCase(unittest.TestCase):

    eleza boilerPlate(self, lock, locked):
        self.assertFalse(locked())
        with lock:
            self.assertTrue(locked())
        self.assertFalse(locked())
        with self.assertRaises(ZeroDivisionError):
            with lock:
                self.assertTrue(locked())
                1 / 0
        self.assertFalse(locked())

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
            ikiwa lock.acquire(False):
                lock.release()
                rudisha False
            else:
                rudisha True
        self.boilerPlate(lock, locked)

    eleza testWithBoundedSemaphore(self):
        lock = threading.BoundedSemaphore()
        eleza locked():
            ikiwa lock.acquire(False):
                lock.release()
                rudisha False
            else:
                rudisha True
        self.boilerPlate(lock, locked)


kundi mycontext(ContextDecorator):
    """Example decoration-compatible context manager for testing"""
    started = False
    exc = None
    catch = False

    eleza __enter__(self):
        self.started = True
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
        with context as result:
            self.assertIs(result, context)
            self.assertTrue(context.started)

        self.assertEqual(context.exc, (None, None, None))


    eleza test_contextdecorator_with_exception(self):
        context = mycontext()

        with self.assertRaisesRegex(NameError, 'foo'):
            with context:
                raise NameError('foo')
        self.assertIsNotNone(context.exc)
        self.assertIs(context.exc[0], NameError)

        context = mycontext()
        context.catch = True
        with context:
            raise NameError('foo')
        self.assertIsNotNone(context.exc)
        self.assertIs(context.exc[0], NameError)


    eleza test_decorator(self):
        context = mycontext()

        @context
        eleza test():
            self.assertIsNone(context.exc)
            self.assertTrue(context.started)
        test()
        self.assertEqual(context.exc, (None, None, None))


    eleza test_decorator_with_exception(self):
        context = mycontext()

        @context
        eleza test():
            self.assertIsNone(context.exc)
            self.assertTrue(context.started)
            raise NameError('foo')

        with self.assertRaisesRegex(NameError, 'foo'):
            test()
        self.assertIsNotNone(context.exc)
        self.assertIs(context.exc[0], NameError)


    eleza test_decorating_method(self):
        context = mycontext()

        kundi Test(object):

            @context
            eleza method(self, a, b, c=None):
                self.a = a
                self.b = b
                self.c = c

        # these tests are for argument passing when used as a decorator
        test = Test()
        test.method(1, 2)
        self.assertEqual(test.a, 1)
        self.assertEqual(test.b, 2)
        self.assertEqual(test.c, None)

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
                pass
            eleza __exit__(self, *exc):
                pass

        with self.assertRaises(AttributeError):
            with mycontext():
                pass


    eleza test_typo_exit(self):
        kundi mycontext(ContextDecorator):
            eleza __enter__(self):
                pass
            eleza __uxit__(self, *exc):
                pass

        with self.assertRaises(AttributeError):
            with mycontext():
                pass


    eleza test_contextdecorator_as_mixin(self):
        kundi somecontext(object):
            started = False
            exc = None

            eleza __enter__(self):
                self.started = True
                rudisha self

            eleza __exit__(self, *exc):
                self.exc = exc

        kundi mycontext(somecontext, ContextDecorator):
            pass

        context = mycontext()
        @context
        eleza test():
            self.assertIsNone(context.exc)
            self.assertTrue(context.started)
        test()
        self.assertEqual(context.exc, (None, None, None))


    eleza test_contextmanager_as_decorator(self):
        @contextmanager
        eleza woohoo(y):
            state.append(y)
            yield
            state.append(999)

        state = []
        @woohoo(1)
        eleza test(x):
            self.assertEqual(state, [1])
            state.append(x)
        test('something')
        self.assertEqual(state, [1, 'something', 999])

        # Issue #11647: Ensure the decorated function is 'reusable'
        state = []
        test('something else')
        self.assertEqual(state, [1, 'something else', 999])


kundi TestBaseExitStack:
    exit_stack = None

    @support.requires_docstrings
    eleza test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = self.exit_stack.__doc__
        obj = self.exit_stack()
        self.assertEqual(obj.__doc__, cm_docstring)

    eleza test_no_resources(self):
        with self.exit_stack():
            pass

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
        with self.exit_stack() as stack:
            for args, kwds in reversed(expected):
                ikiwa args and kwds:
                    f = stack.callback(_exit, *args, **kwds)
                elikiwa args:
                    f = stack.callback(_exit, *args)
                elikiwa kwds:
                    f = stack.callback(_exit, **kwds)
                else:
                    f = stack.callback(_exit)
                self.assertIs(f, _exit)
            for wrapper in stack._exit_callbacks:
                self.assertIs(wrapper[1].__wrapped__, _exit)
                self.assertNotEqual(wrapper[1].__name__, _exit.__name__)
                self.assertIsNone(wrapper[1].__doc__, _exit.__doc__)
        self.assertEqual(result, expected)

        result = []
        with self.exit_stack() as stack:
            with self.assertRaises(TypeError):
                stack.callback(arg=1)
            with self.assertRaises(TypeError):
                self.exit_stack.callback(arg=2)
            with self.assertWarns(DeprecationWarning):
                stack.callback(callback=_exit, arg=3)
        self.assertEqual(result, [((), {'arg': 3})])

    eleza test_push(self):
        exc_raised = ZeroDivisionError
        eleza _expect_exc(exc_type, exc, exc_tb):
            self.assertIs(exc_type, exc_raised)
        eleza _suppress_exc(*exc_details):
            rudisha True
        eleza _expect_ok(exc_type, exc, exc_tb):
            self.assertIsNone(exc_type)
            self.assertIsNone(exc)
            self.assertIsNone(exc_tb)
        kundi ExitCM(object):
            eleza __init__(self, check_exc):
                self.check_exc = check_exc
            eleza __enter__(self):
                self.fail("Should not be called!")
            eleza __exit__(self, *exc_details):
                self.check_exc(*exc_details)
        with self.exit_stack() as stack:
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
        with self.exit_stack() as stack:
            @stack.callback  # Registered first => cleaned up last
            eleza _exit():
                result.append(4)
            self.assertIsNotNone(_exit)
            stack.enter_context(cm)
            self.assertIs(stack._exit_callbacks[-1][1].__self__, cm)
            result.append(2)
        self.assertEqual(result, [1, 2, 3, 4])

    eleza test_close(self):
        result = []
        with self.exit_stack() as stack:
            @stack.callback
            eleza _exit():
                result.append(1)
            self.assertIsNotNone(_exit)
            stack.close()
            result.append(2)
        self.assertEqual(result, [1, 2])

    eleza test_pop_all(self):
        result = []
        with self.exit_stack() as stack:
            @stack.callback
            eleza _exit():
                result.append(3)
            self.assertIsNotNone(_exit)
            new_stack = stack.pop_all()
            result.append(1)
        result.append(2)
        new_stack.close()
        self.assertEqual(result, [1, 2, 3])

    eleza test_exit_raise(self):
        with self.assertRaises(ZeroDivisionError):
            with self.exit_stack() as stack:
                stack.push(lambda *exc: False)
                1/0

    eleza test_exit_suppress(self):
        with self.exit_stack() as stack:
            stack.push(lambda *exc: True)
            1/0

    eleza test_exit_exception_chaining_reference(self):
        # Sanity check to make sure that ExitStack chaining matches
        # actual nested with statements
        kundi RaiseExc:
            eleza __init__(self, exc):
                self.exc = exc
            eleza __enter__(self):
                rudisha self
            eleza __exit__(self, *exc_details):
                raise self.exc

        kundi RaiseExcWithContext:
            eleza __init__(self, outer, inner):
                self.outer = outer
                self.inner = inner
            eleza __enter__(self):
                rudisha self
            eleza __exit__(self, *exc_details):
                try:
                    raise self.inner
                except:
                    raise self.outer

        kundi SuppressExc:
            eleza __enter__(self):
                rudisha self
            eleza __exit__(self, *exc_details):
                type(self).saved_details = exc_details
                rudisha True

        try:
            with RaiseExc(IndexError):
                with RaiseExcWithContext(KeyError, AttributeError):
                    with SuppressExc():
                        with RaiseExc(ValueError):
                            1 / 0
        except IndexError as exc:
            self.assertIsInstance(exc.__context__, KeyError)
            self.assertIsInstance(exc.__context__.__context__, AttributeError)
            # Inner exceptions were suppressed
            self.assertIsNone(exc.__context__.__context__.__context__)
        else:
            self.fail("Expected IndexError, but no exception was raised")
        # Check the inner exceptions
        inner_exc = SuppressExc.saved_details[1]
        self.assertIsInstance(inner_exc, ValueError)
        self.assertIsInstance(inner_exc.__context__, ZeroDivisionError)

    eleza test_exit_exception_chaining(self):
        # Ensure exception chaining matches the reference behaviour
        eleza raise_exc(exc):
            raise exc

        saved_details = None
        eleza suppress_exc(*exc_details):
            nonlocal saved_details
            saved_details = exc_details
            rudisha True

        try:
            with self.exit_stack() as stack:
                stack.callback(raise_exc, IndexError)
                stack.callback(raise_exc, KeyError)
                stack.callback(raise_exc, AttributeError)
                stack.push(suppress_exc)
                stack.callback(raise_exc, ValueError)
                1 / 0
        except IndexError as exc:
            self.assertIsInstance(exc.__context__, KeyError)
            self.assertIsInstance(exc.__context__.__context__, AttributeError)
            # Inner exceptions were suppressed
            self.assertIsNone(exc.__context__.__context__.__context__)
        else:
            self.fail("Expected IndexError, but no exception was raised")
        # Check the inner exceptions
        inner_exc = saved_details[1]
        self.assertIsInstance(inner_exc, ValueError)
        self.assertIsInstance(inner_exc.__context__, ZeroDivisionError)

    eleza test_exit_exception_non_suppressing(self):
        # http://bugs.python.org/issue19092
        eleza raise_exc(exc):
            raise exc

        eleza suppress_exc(*exc_details):
            rudisha True

        try:
            with self.exit_stack() as stack:
                stack.callback(lambda: None)
                stack.callback(raise_exc, IndexError)
        except Exception as exc:
            self.assertIsInstance(exc, IndexError)
        else:
            self.fail("Expected IndexError, but no exception was raised")

        try:
            with self.exit_stack() as stack:
                stack.callback(raise_exc, KeyError)
                stack.push(suppress_exc)
                stack.callback(raise_exc, IndexError)
        except Exception as exc:
            self.assertIsInstance(exc, KeyError)
        else:
            self.fail("Expected KeyError, but no exception was raised")

    eleza test_exit_exception_with_correct_context(self):
        # http://bugs.python.org/issue20317
        @contextmanager
        eleza gets_the_context_right(exc):
            try:
                yield
            finally:
                raise exc

        exc1 = Exception(1)
        exc2 = Exception(2)
        exc3 = Exception(3)
        exc4 = Exception(4)

        # The contextmanager already fixes the context, so prior to the
        # fix, ExitStack would try to fix it *again* and get into an
        # infinite self-referential loop
        try:
            with self.exit_stack() as stack:
                stack.enter_context(gets_the_context_right(exc4))
                stack.enter_context(gets_the_context_right(exc3))
                stack.enter_context(gets_the_context_right(exc2))
                raise exc1
        except Exception as exc:
            self.assertIs(exc, exc4)
            self.assertIs(exc.__context__, exc3)
            self.assertIs(exc.__context__.__context__, exc2)
            self.assertIs(exc.__context__.__context__.__context__, exc1)
            self.assertIsNone(
                       exc.__context__.__context__.__context__.__context__)

    eleza test_exit_exception_with_existing_context(self):
        # Addresses a lack of test coverage discovered after checking in a
        # fix for issue 20317 that still contained debugging code.
        eleza raise_nested(inner_exc, outer_exc):
            try:
                raise inner_exc
            finally:
                raise outer_exc
        exc1 = Exception(1)
        exc2 = Exception(2)
        exc3 = Exception(3)
        exc4 = Exception(4)
        exc5 = Exception(5)
        try:
            with self.exit_stack() as stack:
                stack.callback(raise_nested, exc4, exc5)
                stack.callback(raise_nested, exc2, exc3)
                raise exc1
        except Exception as exc:
            self.assertIs(exc, exc5)
            self.assertIs(exc.__context__, exc4)
            self.assertIs(exc.__context__.__context__, exc3)
            self.assertIs(exc.__context__.__context__.__context__, exc2)
            self.assertIs(
                 exc.__context__.__context__.__context__.__context__, exc1)
            self.assertIsNone(
                exc.__context__.__context__.__context__.__context__.__context__)

    eleza test_body_exception_suppress(self):
        eleza suppress_exc(*exc_details):
            rudisha True
        try:
            with self.exit_stack() as stack:
                stack.push(suppress_exc)
                1/0
        except IndexError as exc:
            self.fail("Expected no exception, got IndexError")

    eleza test_exit_exception_chaining_suppress(self):
        with self.exit_stack() as stack:
            stack.push(lambda *exc: True)
            stack.push(lambda *exc: 1/0)
            stack.push(lambda *exc: {}[1])

    eleza test_excessive_nesting(self):
        # The original implementation would die with RecursionError here
        with self.exit_stack() as stack:
            for i in range(10000):
                stack.callback(int)

    eleza test_instance_bypass(self):
        kundi Example(object): pass
        cm = Example()
        cm.__exit__ = object()
        stack = self.exit_stack()
        self.assertRaises(AttributeError, stack.enter_context, cm)
        stack.push(cm)
        self.assertIs(stack._exit_callbacks[-1][1], cm)

    eleza test_dont_reraise_RuntimeError(self):
        # https://bugs.python.org/issue27122
        kundi UniqueException(Exception): pass
        kundi UniqueRuntimeError(RuntimeError): pass

        @contextmanager
        eleza second():
            try:
                yield 1
            except Exception as exc:
                raise UniqueException("new exception") kutoka exc

        @contextmanager
        eleza first():
            try:
                yield 1
            except Exception as exc:
                raise exc

        # The UniqueRuntimeError should be caught by second()'s exception
        # handler which chain raised a new UniqueException.
        with self.assertRaises(UniqueException) as err_ctx:
            with self.exit_stack() as es_ctx:
                es_ctx.enter_context(second())
                es_ctx.enter_context(first())
                raise UniqueRuntimeError("please no infinite loop.")

        exc = err_ctx.exception
        self.assertIsInstance(exc, UniqueException)
        self.assertIsInstance(exc.__context__, UniqueRuntimeError)
        self.assertIsNone(exc.__context__.__context__)
        self.assertIsNone(exc.__context__.__cause__)
        self.assertIs(exc.__cause__, exc.__context__)


kundi TestExitStack(TestBaseExitStack, unittest.TestCase):
    exit_stack = ExitStack


kundi TestRedirectStream:

    redirect_stream = None
    orig_stream = None

    @support.requires_docstrings
    eleza test_instance_docs(self):
        # Issue 19330: ensure context manager instances have good docstrings
        cm_docstring = self.redirect_stream.__doc__
        obj = self.redirect_stream(None)
        self.assertEqual(obj.__doc__, cm_docstring)

    eleza test_no_redirect_in_init(self):
        orig_stdout = getattr(sys, self.orig_stream)
        self.redirect_stream(None)
        self.assertIs(getattr(sys, self.orig_stream), orig_stdout)

    eleza test_redirect_to_string_io(self):
        f = io.StringIO()
        msg = "Consider an API like help(), which prints directly to stdout"
        orig_stdout = getattr(sys, self.orig_stream)
        with self.redirect_stream(f):
            andika(msg, file=getattr(sys, self.orig_stream))
        self.assertIs(getattr(sys, self.orig_stream), orig_stdout)
        s = f.getvalue().strip()
        self.assertEqual(s, msg)

    eleza test_enter_result_is_target(self):
        f = io.StringIO()
        with self.redirect_stream(f) as enter_result:
            self.assertIs(enter_result, f)

    eleza test_cm_is_reusable(self):
        f = io.StringIO()
        write_to_f = self.redirect_stream(f)
        orig_stdout = getattr(sys, self.orig_stream)
        with write_to_f:
            andika("Hello", end=" ", file=getattr(sys, self.orig_stream))
        with write_to_f:
            andika("World!", file=getattr(sys, self.orig_stream))
        self.assertIs(getattr(sys, self.orig_stream), orig_stdout)
        s = f.getvalue()
        self.assertEqual(s, "Hello World!\n")

    eleza test_cm_is_reentrant(self):
        f = io.StringIO()
        write_to_f = self.redirect_stream(f)
        orig_stdout = getattr(sys, self.orig_stream)
        with write_to_f:
            andika("Hello", end=" ", file=getattr(sys, self.orig_stream))
            with write_to_f:
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

    eleza test_no_result_kutoka_enter(self):
        with suppress(ValueError) as enter_result:
            self.assertIsNone(enter_result)

    eleza test_no_exception(self):
        with suppress(ValueError):
            self.assertEqual(pow(2, 5), 32)

    eleza test_exact_exception(self):
        with suppress(TypeError):
            len(5)

    eleza test_exception_hierarchy(self):
        with suppress(LookupError):
            'Hello'[50]

    eleza test_other_exception(self):
        with self.assertRaises(ZeroDivisionError):
            with suppress(TypeError):
                1/0

    eleza test_no_args(self):
        with self.assertRaises(ZeroDivisionError):
            with suppress():
                1/0

    eleza test_multiple_exception_args(self):
        with suppress(ZeroDivisionError, TypeError):
            1/0
        with suppress(ZeroDivisionError, TypeError):
            len(5)

    eleza test_cm_is_reentrant(self):
        ignore_exceptions = suppress(Exception)
        with ignore_exceptions:
            pass
        with ignore_exceptions:
            len(5)
        with ignore_exceptions:
            with ignore_exceptions: # Check nested usage
                len(5)
            outer_continued = True
            1/0
        self.assertTrue(outer_continued)

ikiwa __name__ == "__main__":
    unittest.main()
