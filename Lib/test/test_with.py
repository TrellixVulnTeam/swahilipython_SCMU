"""Unit tests for the with statement specified in PEP 343."""


__author__ = "Mike Bland"
__email__ = "mbland at acm dot org"

agiza sys
agiza unittest
kutoka collections agiza deque
kutoka contextlib agiza _GeneratorContextManager, contextmanager


kundi MockContextManager(_GeneratorContextManager):
    eleza __init__(self, *args):
        super().__init__(*args)
        self.enter_called = False
        self.exit_called = False
        self.exit_args = None

    eleza __enter__(self):
        self.enter_called = True
        rudisha _GeneratorContextManager.__enter__(self)

    eleza __exit__(self, type, value, traceback):
        self.exit_called = True
        self.exit_args = (type, value, traceback)
        rudisha _GeneratorContextManager.__exit__(self, type,
                                                 value, traceback)


eleza mock_contextmanager(func):
    eleza helper(*args, **kwds):
        rudisha MockContextManager(func, args, kwds)
    rudisha helper


kundi MockResource(object):
    eleza __init__(self):
        self.yielded = False
        self.stopped = False


@mock_contextmanager
eleza mock_contextmanager_generator():
    mock = MockResource()
    try:
        mock.yielded = True
        yield mock
    finally:
        mock.stopped = True


kundi Nested(object):

    eleza __init__(self, *managers):
        self.managers = managers
        self.entered = None

    eleza __enter__(self):
        ikiwa self.entered is not None:
            raise RuntimeError("Context is not reentrant")
        self.entered = deque()
        vars = []
        try:
            for mgr in self.managers:
                vars.append(mgr.__enter__())
                self.entered.appendleft(mgr)
        except:
            ikiwa not self.__exit__(*sys.exc_info()):
                raise
        rudisha vars

    eleza __exit__(self, *exc_info):
        # Behave like nested with statements
        # first in, last out
        # New exceptions override old ones
        ex = exc_info
        for mgr in self.entered:
            try:
                ikiwa mgr.__exit__(*ex):
                    ex = (None, None, None)
            except:
                ex = sys.exc_info()
        self.entered = None
        ikiwa ex is not exc_info:
            raise ex[0](ex[1]).with_traceback(ex[2])


kundi MockNested(Nested):
    eleza __init__(self, *managers):
        Nested.__init__(self, *managers)
        self.enter_called = False
        self.exit_called = False
        self.exit_args = None

    eleza __enter__(self):
        self.enter_called = True
        rudisha Nested.__enter__(self)

    eleza __exit__(self, *exc_info):
        self.exit_called = True
        self.exit_args = exc_info
        rudisha Nested.__exit__(self, *exc_info)


kundi FailureTestCase(unittest.TestCase):
    eleza testNameError(self):
        eleza fooNotDeclared():
            with foo: pass
        self.assertRaises(NameError, fooNotDeclared)

    eleza testEnterAttributeError1(self):
        kundi LacksEnter(object):
            eleza __exit__(self, type, value, traceback):
                pass

        eleza fooLacksEnter():
            foo = LacksEnter()
            with foo: pass
        self.assertRaisesRegex(AttributeError, '__enter__', fooLacksEnter)

    eleza testEnterAttributeError2(self):
        kundi LacksEnterAndExit(object):
            pass

        eleza fooLacksEnterAndExit():
            foo = LacksEnterAndExit()
            with foo: pass
        self.assertRaisesRegex(AttributeError, '__enter__', fooLacksEnterAndExit)

    eleza testExitAttributeError(self):
        kundi LacksExit(object):
            eleza __enter__(self):
                pass

        eleza fooLacksExit():
            foo = LacksExit()
            with foo: pass
        self.assertRaisesRegex(AttributeError, '__exit__', fooLacksExit)

    eleza assertRaisesSyntaxError(self, codestr):
        eleza shouldRaiseSyntaxError(s):
            compile(s, '', 'single')
        self.assertRaises(SyntaxError, shouldRaiseSyntaxError, codestr)

    eleza testAssignmentToNoneError(self):
        self.assertRaisesSyntaxError('with mock as None:\n  pass')
        self.assertRaisesSyntaxError(
            'with mock as (None):\n'
            '  pass')

    eleza testAssignmentToTupleOnlyContainingNoneError(self):
        self.assertRaisesSyntaxError('with mock as None,:\n  pass')
        self.assertRaisesSyntaxError(
            'with mock as (None,):\n'
            '  pass')

    eleza testAssignmentToTupleContainingNoneError(self):
        self.assertRaisesSyntaxError(
            'with mock as (foo, None, bar):\n'
            '  pass')

    eleza testEnterThrows(self):
        kundi EnterThrows(object):
            eleza __enter__(self):
                raise RuntimeError("Enter threw")
            eleza __exit__(self, *args):
                pass

        eleza shouldThrow():
            ct = EnterThrows()
            self.foo = None
            with ct as self.foo:
                pass
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertEqual(self.foo, None)

    eleza testExitThrows(self):
        kundi ExitThrows(object):
            eleza __enter__(self):
                return
            eleza __exit__(self, *args):
                raise RuntimeError(42)
        eleza shouldThrow():
            with ExitThrows():
                pass
        self.assertRaises(RuntimeError, shouldThrow)

kundi ContextmanagerAssertionMixin(object):

    eleza setUp(self):
        self.TEST_EXCEPTION = RuntimeError("test exception")

    eleza assertInWithManagerInvariants(self, mock_manager):
        self.assertTrue(mock_manager.enter_called)
        self.assertFalse(mock_manager.exit_called)
        self.assertEqual(mock_manager.exit_args, None)

    eleza assertAfterWithManagerInvariants(self, mock_manager, exit_args):
        self.assertTrue(mock_manager.enter_called)
        self.assertTrue(mock_manager.exit_called)
        self.assertEqual(mock_manager.exit_args, exit_args)

    eleza assertAfterWithManagerInvariantsNoError(self, mock_manager):
        self.assertAfterWithManagerInvariants(mock_manager,
            (None, None, None))

    eleza assertInWithGeneratorInvariants(self, mock_generator):
        self.assertTrue(mock_generator.yielded)
        self.assertFalse(mock_generator.stopped)

    eleza assertAfterWithGeneratorInvariantsNoError(self, mock_generator):
        self.assertTrue(mock_generator.yielded)
        self.assertTrue(mock_generator.stopped)

    eleza raiseTestException(self):
        raise self.TEST_EXCEPTION

    eleza assertAfterWithManagerInvariantsWithError(self, mock_manager,
                                                  exc_type=None):
        self.assertTrue(mock_manager.enter_called)
        self.assertTrue(mock_manager.exit_called)
        ikiwa exc_type is None:
            self.assertEqual(mock_manager.exit_args[1], self.TEST_EXCEPTION)
            exc_type = type(self.TEST_EXCEPTION)
        self.assertEqual(mock_manager.exit_args[0], exc_type)
        # Test the __exit__ arguments. Issue #7853
        self.assertIsInstance(mock_manager.exit_args[1], exc_type)
        self.assertIsNot(mock_manager.exit_args[2], None)

    eleza assertAfterWithGeneratorInvariantsWithError(self, mock_generator):
        self.assertTrue(mock_generator.yielded)
        self.assertTrue(mock_generator.stopped)


kundi NonexceptionalTestCase(unittest.TestCase, ContextmanagerAssertionMixin):
    eleza testInlineGeneratorSyntax(self):
        with mock_contextmanager_generator():
            pass

    eleza testUnboundGenerator(self):
        mock = mock_contextmanager_generator()
        with mock:
            pass
        self.assertAfterWithManagerInvariantsNoError(mock)

    eleza testInlineGeneratorBoundSyntax(self):
        with mock_contextmanager_generator() as foo:
            self.assertInWithGeneratorInvariants(foo)
        # FIXME: In the future, we'll try to keep the bound names kutoka leaking
        self.assertAfterWithGeneratorInvariantsNoError(foo)

    eleza testInlineGeneratorBoundToExistingVariable(self):
        foo = None
        with mock_contextmanager_generator() as foo:
            self.assertInWithGeneratorInvariants(foo)
        self.assertAfterWithGeneratorInvariantsNoError(foo)

    eleza testInlineGeneratorBoundToDottedVariable(self):
        with mock_contextmanager_generator() as self.foo:
            self.assertInWithGeneratorInvariants(self.foo)
        self.assertAfterWithGeneratorInvariantsNoError(self.foo)

    eleza testBoundGenerator(self):
        mock = mock_contextmanager_generator()
        with mock as foo:
            self.assertInWithGeneratorInvariants(foo)
            self.assertInWithManagerInvariants(mock)
        self.assertAfterWithGeneratorInvariantsNoError(foo)
        self.assertAfterWithManagerInvariantsNoError(mock)

    eleza testNestedSingleStatements(self):
        mock_a = mock_contextmanager_generator()
        with mock_a as foo:
            mock_b = mock_contextmanager_generator()
            with mock_b as bar:
                self.assertInWithManagerInvariants(mock_a)
                self.assertInWithManagerInvariants(mock_b)
                self.assertInWithGeneratorInvariants(foo)
                self.assertInWithGeneratorInvariants(bar)
            self.assertAfterWithManagerInvariantsNoError(mock_b)
            self.assertAfterWithGeneratorInvariantsNoError(bar)
            self.assertInWithManagerInvariants(mock_a)
            self.assertInWithGeneratorInvariants(foo)
        self.assertAfterWithManagerInvariantsNoError(mock_a)
        self.assertAfterWithGeneratorInvariantsNoError(foo)


kundi NestedNonexceptionalTestCase(unittest.TestCase,
    ContextmanagerAssertionMixin):
    eleza testSingleArgInlineGeneratorSyntax(self):
        with Nested(mock_contextmanager_generator()):
            pass

    eleza testSingleArgBoundToNonTuple(self):
        m = mock_contextmanager_generator()
        # This will bind all the arguments to nested() into a single list
        # assigned to foo.
        with Nested(m) as foo:
            self.assertInWithManagerInvariants(m)
        self.assertAfterWithManagerInvariantsNoError(m)

    eleza testSingleArgBoundToSingleElementParenthesizedList(self):
        m = mock_contextmanager_generator()
        # This will bind all the arguments to nested() into a single list
        # assigned to foo.
        with Nested(m) as (foo):
            self.assertInWithManagerInvariants(m)
        self.assertAfterWithManagerInvariantsNoError(m)

    eleza testSingleArgBoundToMultipleElementTupleError(self):
        eleza shouldThrowValueError():
            with Nested(mock_contextmanager_generator()) as (foo, bar):
                pass
        self.assertRaises(ValueError, shouldThrowValueError)

    eleza testSingleArgUnbound(self):
        mock_contextmanager = mock_contextmanager_generator()
        mock_nested = MockNested(mock_contextmanager)
        with mock_nested:
            self.assertInWithManagerInvariants(mock_contextmanager)
            self.assertInWithManagerInvariants(mock_nested)
        self.assertAfterWithManagerInvariantsNoError(mock_contextmanager)
        self.assertAfterWithManagerInvariantsNoError(mock_nested)

    eleza testMultipleArgUnbound(self):
        m = mock_contextmanager_generator()
        n = mock_contextmanager_generator()
        o = mock_contextmanager_generator()
        mock_nested = MockNested(m, n, o)
        with mock_nested:
            self.assertInWithManagerInvariants(m)
            self.assertInWithManagerInvariants(n)
            self.assertInWithManagerInvariants(o)
            self.assertInWithManagerInvariants(mock_nested)
        self.assertAfterWithManagerInvariantsNoError(m)
        self.assertAfterWithManagerInvariantsNoError(n)
        self.assertAfterWithManagerInvariantsNoError(o)
        self.assertAfterWithManagerInvariantsNoError(mock_nested)

    eleza testMultipleArgBound(self):
        mock_nested = MockNested(mock_contextmanager_generator(),
            mock_contextmanager_generator(), mock_contextmanager_generator())
        with mock_nested as (m, n, o):
            self.assertInWithGeneratorInvariants(m)
            self.assertInWithGeneratorInvariants(n)
            self.assertInWithGeneratorInvariants(o)
            self.assertInWithManagerInvariants(mock_nested)
        self.assertAfterWithGeneratorInvariantsNoError(m)
        self.assertAfterWithGeneratorInvariantsNoError(n)
        self.assertAfterWithGeneratorInvariantsNoError(o)
        self.assertAfterWithManagerInvariantsNoError(mock_nested)


kundi ExceptionalTestCase(ContextmanagerAssertionMixin, unittest.TestCase):
    eleza testSingleResource(self):
        cm = mock_contextmanager_generator()
        eleza shouldThrow():
            with cm as self.resource:
                self.assertInWithManagerInvariants(cm)
                self.assertInWithGeneratorInvariants(self.resource)
                self.raiseTestException()
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(cm)
        self.assertAfterWithGeneratorInvariantsWithError(self.resource)

    eleza testExceptionNormalized(self):
        cm = mock_contextmanager_generator()
        eleza shouldThrow():
            with cm as self.resource:
                # Note this relies on the fact that 1 // 0 produces an exception
                # that is not normalized immediately.
                1 // 0
        self.assertRaises(ZeroDivisionError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(cm, ZeroDivisionError)

    eleza testNestedSingleStatements(self):
        mock_a = mock_contextmanager_generator()
        mock_b = mock_contextmanager_generator()
        eleza shouldThrow():
            with mock_a as self.foo:
                with mock_b as self.bar:
                    self.assertInWithManagerInvariants(mock_a)
                    self.assertInWithManagerInvariants(mock_b)
                    self.assertInWithGeneratorInvariants(self.foo)
                    self.assertInWithGeneratorInvariants(self.bar)
                    self.raiseTestException()
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(mock_a)
        self.assertAfterWithManagerInvariantsWithError(mock_b)
        self.assertAfterWithGeneratorInvariantsWithError(self.foo)
        self.assertAfterWithGeneratorInvariantsWithError(self.bar)

    eleza testMultipleResourcesInSingleStatement(self):
        cm_a = mock_contextmanager_generator()
        cm_b = mock_contextmanager_generator()
        mock_nested = MockNested(cm_a, cm_b)
        eleza shouldThrow():
            with mock_nested as (self.resource_a, self.resource_b):
                self.assertInWithManagerInvariants(cm_a)
                self.assertInWithManagerInvariants(cm_b)
                self.assertInWithManagerInvariants(mock_nested)
                self.assertInWithGeneratorInvariants(self.resource_a)
                self.assertInWithGeneratorInvariants(self.resource_b)
                self.raiseTestException()
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(cm_a)
        self.assertAfterWithManagerInvariantsWithError(cm_b)
        self.assertAfterWithManagerInvariantsWithError(mock_nested)
        self.assertAfterWithGeneratorInvariantsWithError(self.resource_a)
        self.assertAfterWithGeneratorInvariantsWithError(self.resource_b)

    eleza testNestedExceptionBeforeInnerStatement(self):
        mock_a = mock_contextmanager_generator()
        mock_b = mock_contextmanager_generator()
        self.bar = None
        eleza shouldThrow():
            with mock_a as self.foo:
                self.assertInWithManagerInvariants(mock_a)
                self.assertInWithGeneratorInvariants(self.foo)
                self.raiseTestException()
                with mock_b as self.bar:
                    pass
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(mock_a)
        self.assertAfterWithGeneratorInvariantsWithError(self.foo)

        # The inner statement stuff should never have been touched
        self.assertEqual(self.bar, None)
        self.assertFalse(mock_b.enter_called)
        self.assertFalse(mock_b.exit_called)
        self.assertEqual(mock_b.exit_args, None)

    eleza testNestedExceptionAfterInnerStatement(self):
        mock_a = mock_contextmanager_generator()
        mock_b = mock_contextmanager_generator()
        eleza shouldThrow():
            with mock_a as self.foo:
                with mock_b as self.bar:
                    self.assertInWithManagerInvariants(mock_a)
                    self.assertInWithManagerInvariants(mock_b)
                    self.assertInWithGeneratorInvariants(self.foo)
                    self.assertInWithGeneratorInvariants(self.bar)
                self.raiseTestException()
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(mock_a)
        self.assertAfterWithManagerInvariantsNoError(mock_b)
        self.assertAfterWithGeneratorInvariantsWithError(self.foo)
        self.assertAfterWithGeneratorInvariantsNoError(self.bar)

    eleza testRaisedStopIteration1(self):
        # From bug 1462485
        @contextmanager
        eleza cm():
            yield

        eleza shouldThrow():
            with cm():
                raise StopIteration("kutoka with")

        with self.assertRaisesRegex(StopIteration, 'kutoka with'):
            shouldThrow()

    eleza testRaisedStopIteration2(self):
        # From bug 1462485
        kundi cm(object):
            eleza __enter__(self):
                pass
            eleza __exit__(self, type, value, traceback):
                pass

        eleza shouldThrow():
            with cm():
                raise StopIteration("kutoka with")

        with self.assertRaisesRegex(StopIteration, 'kutoka with'):
            shouldThrow()

    eleza testRaisedStopIteration3(self):
        # Another variant where the exception hasn't been instantiated
        # From bug 1705170
        @contextmanager
        eleza cm():
            yield

        eleza shouldThrow():
            with cm():
                raise next(iter([]))

        with self.assertRaises(StopIteration):
            shouldThrow()

    eleza testRaisedGeneratorExit1(self):
        # From bug 1462485
        @contextmanager
        eleza cm():
            yield

        eleza shouldThrow():
            with cm():
                raise GeneratorExit("kutoka with")

        self.assertRaises(GeneratorExit, shouldThrow)

    eleza testRaisedGeneratorExit2(self):
        # From bug 1462485
        kundi cm (object):
            eleza __enter__(self):
                pass
            eleza __exit__(self, type, value, traceback):
                pass

        eleza shouldThrow():
            with cm():
                raise GeneratorExit("kutoka with")

        self.assertRaises(GeneratorExit, shouldThrow)

    eleza testErrorsInBool(self):
        # issue4589: __exit__ rudisha code may raise an exception
        # when looking at its truth value.

        kundi cm(object):
            eleza __init__(self, bool_conversion):
                kundi Bool:
                    eleza __bool__(self):
                        rudisha bool_conversion()
                self.exit_result = Bool()
            eleza __enter__(self):
                rudisha 3
            eleza __exit__(self, a, b, c):
                rudisha self.exit_result

        eleza trueAsBool():
            with cm(lambda: True):
                self.fail("Should NOT see this")
        trueAsBool()

        eleza falseAsBool():
            with cm(lambda: False):
                self.fail("Should raise")
        self.assertRaises(AssertionError, falseAsBool)

        eleza failAsBool():
            with cm(lambda: 1//0):
                self.fail("Should NOT see this")
        self.assertRaises(ZeroDivisionError, failAsBool)


kundi NonLocalFlowControlTestCase(unittest.TestCase):

    eleza testWithBreak(self):
        counter = 0
        while True:
            counter += 1
            with mock_contextmanager_generator():
                counter += 10
                break
            counter += 100 # Not reached
        self.assertEqual(counter, 11)

    eleza testWithContinue(self):
        counter = 0
        while True:
            counter += 1
            ikiwa counter > 2:
                break
            with mock_contextmanager_generator():
                counter += 10
                continue
            counter += 100 # Not reached
        self.assertEqual(counter, 12)

    eleza testWithReturn(self):
        eleza foo():
            counter = 0
            while True:
                counter += 1
                with mock_contextmanager_generator():
                    counter += 10
                    rudisha counter
                counter += 100 # Not reached
        self.assertEqual(foo(), 11)

    eleza testWithYield(self):
        eleza gen():
            with mock_contextmanager_generator():
                yield 12
                yield 13
        x = list(gen())
        self.assertEqual(x, [12, 13])

    eleza testWithRaise(self):
        counter = 0
        try:
            counter += 1
            with mock_contextmanager_generator():
                counter += 10
                raise RuntimeError
            counter += 100 # Not reached
        except RuntimeError:
            self.assertEqual(counter, 11)
        else:
            self.fail("Didn't raise RuntimeError")


kundi AssignmentTargetTestCase(unittest.TestCase):

    eleza testSingleComplexTarget(self):
        targets = {1: [0, 1, 2]}
        with mock_contextmanager_generator() as targets[1][0]:
            self.assertEqual(list(targets.keys()), [1])
            self.assertEqual(targets[1][0].__class__, MockResource)
        with mock_contextmanager_generator() as list(targets.values())[0][1]:
            self.assertEqual(list(targets.keys()), [1])
            self.assertEqual(targets[1][1].__class__, MockResource)
        with mock_contextmanager_generator() as targets[2]:
            keys = list(targets.keys())
            keys.sort()
            self.assertEqual(keys, [1, 2])
        kundi C: pass
        blah = C()
        with mock_contextmanager_generator() as blah.foo:
            self.assertEqual(hasattr(blah, "foo"), True)

    eleza testMultipleComplexTargets(self):
        kundi C:
            eleza __enter__(self): rudisha 1, 2, 3
            eleza __exit__(self, t, v, tb): pass
        targets = {1: [0, 1, 2]}
        with C() as (targets[1][0], targets[1][1], targets[1][2]):
            self.assertEqual(targets, {1: [1, 2, 3]})
        with C() as (list(targets.values())[0][2], list(targets.values())[0][1], list(targets.values())[0][0]):
            self.assertEqual(targets, {1: [3, 2, 1]})
        with C() as (targets[1], targets[2], targets[3]):
            self.assertEqual(targets, {1: 1, 2: 2, 3: 3})
        kundi B: pass
        blah = B()
        with C() as (blah.one, blah.two, blah.three):
            self.assertEqual(blah.one, 1)
            self.assertEqual(blah.two, 2)
            self.assertEqual(blah.three, 3)


kundi ExitSwallowsExceptionTestCase(unittest.TestCase):

    eleza testExitTrueSwallowsException(self):
        kundi AfricanSwallow:
            eleza __enter__(self): pass
            eleza __exit__(self, t, v, tb): rudisha True
        try:
            with AfricanSwallow():
                1/0
        except ZeroDivisionError:
            self.fail("ZeroDivisionError should have been swallowed")

    eleza testExitFalseDoesntSwallowException(self):
        kundi EuropeanSwallow:
            eleza __enter__(self): pass
            eleza __exit__(self, t, v, tb): rudisha False
        try:
            with EuropeanSwallow():
                1/0
        except ZeroDivisionError:
            pass
        else:
            self.fail("ZeroDivisionError should have been raised")


kundi NestedWith(unittest.TestCase):

    kundi Dummy(object):
        eleza __init__(self, value=None, gobble=False):
            ikiwa value is None:
                value = self
            self.value = value
            self.gobble = gobble
            self.enter_called = False
            self.exit_called = False

        eleza __enter__(self):
            self.enter_called = True
            rudisha self.value

        eleza __exit__(self, *exc_info):
            self.exit_called = True
            self.exc_info = exc_info
            ikiwa self.gobble:
                rudisha True

    kundi InitRaises(object):
        eleza __init__(self): raise RuntimeError()

    kundi EnterRaises(object):
        eleza __enter__(self): raise RuntimeError()
        eleza __exit__(self, *exc_info): pass

    kundi ExitRaises(object):
        eleza __enter__(self): pass
        eleza __exit__(self, *exc_info): raise RuntimeError()

    eleza testNoExceptions(self):
        with self.Dummy() as a, self.Dummy() as b:
            self.assertTrue(a.enter_called)
            self.assertTrue(b.enter_called)
        self.assertTrue(a.exit_called)
        self.assertTrue(b.exit_called)

    eleza testExceptionInExprList(self):
        try:
            with self.Dummy() as a, self.InitRaises():
                pass
        except:
            pass
        self.assertTrue(a.enter_called)
        self.assertTrue(a.exit_called)

    eleza testExceptionInEnter(self):
        try:
            with self.Dummy() as a, self.EnterRaises():
                self.fail('body of bad with executed')
        except RuntimeError:
            pass
        else:
            self.fail('RuntimeError not reraised')
        self.assertTrue(a.enter_called)
        self.assertTrue(a.exit_called)

    eleza testExceptionInExit(self):
        body_executed = False
        with self.Dummy(gobble=True) as a, self.ExitRaises():
            body_executed = True
        self.assertTrue(a.enter_called)
        self.assertTrue(a.exit_called)
        self.assertTrue(body_executed)
        self.assertNotEqual(a.exc_info[0], None)

    eleza testEnterReturnsTuple(self):
        with self.Dummy(value=(1,2)) as (a1, a2), \
             self.Dummy(value=(10, 20)) as (b1, b2):
            self.assertEqual(1, a1)
            self.assertEqual(2, a2)
            self.assertEqual(10, b1)
            self.assertEqual(20, b2)

ikiwa __name__ == '__main__':
    unittest.main()
