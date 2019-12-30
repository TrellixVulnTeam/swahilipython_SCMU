"""Unit tests kila the ukijumuisha statement specified kwenye PEP 343."""


__author__ = "Mike Bland"
__email__ = "mbland at acm dot org"

agiza sys
agiza unittest
kutoka collections agiza deque
kutoka contextlib agiza _GeneratorContextManager, contextmanager


kundi MockContextManager(_GeneratorContextManager):
    eleza __init__(self, *args):
        super().__init__(*args)
        self.enter_called = Uongo
        self.exit_called = Uongo
        self.exit_args = Tupu

    eleza __enter__(self):
        self.enter_called = Kweli
        rudisha _GeneratorContextManager.__enter__(self)

    eleza __exit__(self, type, value, traceback):
        self.exit_called = Kweli
        self.exit_args = (type, value, traceback)
        rudisha _GeneratorContextManager.__exit__(self, type,
                                                 value, traceback)


eleza mock_contextmanager(func):
    eleza helper(*args, **kwds):
        rudisha MockContextManager(func, args, kwds)
    rudisha helper


kundi MockResource(object):
    eleza __init__(self):
        self.tumaed = Uongo
        self.stopped = Uongo


@mock_contextmanager
eleza mock_contextmanager_generator():
    mock = MockResource()
    jaribu:
        mock.tumaed = Kweli
        tuma mock
    mwishowe:
        mock.stopped = Kweli


kundi Nested(object):

    eleza __init__(self, *managers):
        self.managers = managers
        self.entered = Tupu

    eleza __enter__(self):
        ikiwa self.entered ni sio Tupu:
            ashiria RuntimeError("Context ni sio reentrant")
        self.entered = deque()
        vars = []
        jaribu:
            kila mgr kwenye self.managers:
                vars.append(mgr.__enter__())
                self.entered.appendleft(mgr)
        tatizo:
            ikiwa sio self.__exit__(*sys.exc_info()):
                raise
        rudisha vars

    eleza __exit__(self, *exc_info):
        # Behave like nested ukijumuisha statements
        # first in, last out
        # New exceptions override old ones
        ex = exc_info
        kila mgr kwenye self.entered:
            jaribu:
                ikiwa mgr.__exit__(*ex):
                    ex = (Tupu, Tupu, Tupu)
            tatizo:
                ex = sys.exc_info()
        self.entered = Tupu
        ikiwa ex ni sio exc_info:
            ashiria ex[0](ex[1]).with_traceback(ex[2])


kundi MockNested(Nested):
    eleza __init__(self, *managers):
        Nested.__init__(self, *managers)
        self.enter_called = Uongo
        self.exit_called = Uongo
        self.exit_args = Tupu

    eleza __enter__(self):
        self.enter_called = Kweli
        rudisha Nested.__enter__(self)

    eleza __exit__(self, *exc_info):
        self.exit_called = Kweli
        self.exit_args = exc_info
        rudisha Nested.__exit__(self, *exc_info)


kundi FailureTestCase(unittest.TestCase):
    eleza testNameError(self):
        eleza fooNotDeclared():
            ukijumuisha foo: pita
        self.assertRaises(NameError, fooNotDeclared)

    eleza testEnterAttributeError1(self):
        kundi LacksEnter(object):
            eleza __exit__(self, type, value, traceback):
                pita

        eleza fooLacksEnter():
            foo = LacksEnter()
            ukijumuisha foo: pita
        self.assertRaisesRegex(AttributeError, '__enter__', fooLacksEnter)

    eleza testEnterAttributeError2(self):
        kundi LacksEnterAndExit(object):
            pita

        eleza fooLacksEnterAndExit():
            foo = LacksEnterAndExit()
            ukijumuisha foo: pita
        self.assertRaisesRegex(AttributeError, '__enter__', fooLacksEnterAndExit)

    eleza testExitAttributeError(self):
        kundi LacksExit(object):
            eleza __enter__(self):
                pita

        eleza fooLacksExit():
            foo = LacksExit()
            ukijumuisha foo: pita
        self.assertRaisesRegex(AttributeError, '__exit__', fooLacksExit)

    eleza assertRaisesSyntaxError(self, codestr):
        eleza shouldRaiseSyntaxError(s):
            compile(s, '', 'single')
        self.assertRaises(SyntaxError, shouldRaiseSyntaxError, codestr)

    eleza testAssignmentToTupuError(self):
        self.assertRaisesSyntaxError('ukijumuisha mock kama Tupu:\n  pita')
        self.assertRaisesSyntaxError(
            'ukijumuisha mock kama (Tupu):\n'
            '  pita')

    eleza testAssignmentToTupleOnlyContainingTupuError(self):
        self.assertRaisesSyntaxError('ukijumuisha mock kama Tupu,:\n  pita')
        self.assertRaisesSyntaxError(
            'ukijumuisha mock kama (Tupu,):\n'
            '  pita')

    eleza testAssignmentToTupleContainingTupuError(self):
        self.assertRaisesSyntaxError(
            'ukijumuisha mock kama (foo, Tupu, bar):\n'
            '  pita')

    eleza testEnterThrows(self):
        kundi EnterThrows(object):
            eleza __enter__(self):
                ashiria RuntimeError("Enter threw")
            eleza __exit__(self, *args):
                pita

        eleza shouldThrow():
            ct = EnterThrows()
            self.foo = Tupu
            ukijumuisha ct kama self.foo:
                pita
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertEqual(self.foo, Tupu)

    eleza testExitThrows(self):
        kundi ExitThrows(object):
            eleza __enter__(self):
                rudisha
            eleza __exit__(self, *args):
                ashiria RuntimeError(42)
        eleza shouldThrow():
            ukijumuisha ExitThrows():
                pita
        self.assertRaises(RuntimeError, shouldThrow)

kundi ContextmanagerAssertionMixin(object):

    eleza setUp(self):
        self.TEST_EXCEPTION = RuntimeError("test exception")

    eleza assertInWithManagerInvariants(self, mock_manager):
        self.assertKweli(mock_manager.enter_called)
        self.assertUongo(mock_manager.exit_called)
        self.assertEqual(mock_manager.exit_args, Tupu)

    eleza assertAfterWithManagerInvariants(self, mock_manager, exit_args):
        self.assertKweli(mock_manager.enter_called)
        self.assertKweli(mock_manager.exit_called)
        self.assertEqual(mock_manager.exit_args, exit_args)

    eleza assertAfterWithManagerInvariantsNoError(self, mock_manager):
        self.assertAfterWithManagerInvariants(mock_manager,
            (Tupu, Tupu, Tupu))

    eleza assertInWithGeneratorInvariants(self, mock_generator):
        self.assertKweli(mock_generator.tumaed)
        self.assertUongo(mock_generator.stopped)

    eleza assertAfterWithGeneratorInvariantsNoError(self, mock_generator):
        self.assertKweli(mock_generator.tumaed)
        self.assertKweli(mock_generator.stopped)

    eleza raiseTestException(self):
        ashiria self.TEST_EXCEPTION

    eleza assertAfterWithManagerInvariantsWithError(self, mock_manager,
                                                  exc_type=Tupu):
        self.assertKweli(mock_manager.enter_called)
        self.assertKweli(mock_manager.exit_called)
        ikiwa exc_type ni Tupu:
            self.assertEqual(mock_manager.exit_args[1], self.TEST_EXCEPTION)
            exc_type = type(self.TEST_EXCEPTION)
        self.assertEqual(mock_manager.exit_args[0], exc_type)
        # Test the __exit__ arguments. Issue #7853
        self.assertIsInstance(mock_manager.exit_args[1], exc_type)
        self.assertIsNot(mock_manager.exit_args[2], Tupu)

    eleza assertAfterWithGeneratorInvariantsWithError(self, mock_generator):
        self.assertKweli(mock_generator.tumaed)
        self.assertKweli(mock_generator.stopped)


kundi TupuxceptionalTestCase(unittest.TestCase, ContextmanagerAssertionMixin):
    eleza testInlineGeneratorSyntax(self):
        ukijumuisha mock_contextmanager_generator():
            pita

    eleza testUnboundGenerator(self):
        mock = mock_contextmanager_generator()
        ukijumuisha mock:
            pita
        self.assertAfterWithManagerInvariantsNoError(mock)

    eleza testInlineGeneratorBoundSyntax(self):
        ukijumuisha mock_contextmanager_generator() kama foo:
            self.assertInWithGeneratorInvariants(foo)
        # FIXME: In the future, we'll try to keep the bound names kutoka leaking
        self.assertAfterWithGeneratorInvariantsNoError(foo)

    eleza testInlineGeneratorBoundToExistingVariable(self):
        foo = Tupu
        ukijumuisha mock_contextmanager_generator() kama foo:
            self.assertInWithGeneratorInvariants(foo)
        self.assertAfterWithGeneratorInvariantsNoError(foo)

    eleza testInlineGeneratorBoundToDottedVariable(self):
        ukijumuisha mock_contextmanager_generator() kama self.foo:
            self.assertInWithGeneratorInvariants(self.foo)
        self.assertAfterWithGeneratorInvariantsNoError(self.foo)

    eleza testBoundGenerator(self):
        mock = mock_contextmanager_generator()
        ukijumuisha mock kama foo:
            self.assertInWithGeneratorInvariants(foo)
            self.assertInWithManagerInvariants(mock)
        self.assertAfterWithGeneratorInvariantsNoError(foo)
        self.assertAfterWithManagerInvariantsNoError(mock)

    eleza testNestedSingleStatements(self):
        mock_a = mock_contextmanager_generator()
        ukijumuisha mock_a kama foo:
            mock_b = mock_contextmanager_generator()
            ukijumuisha mock_b kama bar:
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


kundi NestedTupuxceptionalTestCase(unittest.TestCase,
    ContextmanagerAssertionMixin):
    eleza testSingleArgInlineGeneratorSyntax(self):
        ukijumuisha Nested(mock_contextmanager_generator()):
            pita

    eleza testSingleArgBoundToNonTuple(self):
        m = mock_contextmanager_generator()
        # This will bind all the arguments to nested() into a single list
        # assigned to foo.
        ukijumuisha Nested(m) kama foo:
            self.assertInWithManagerInvariants(m)
        self.assertAfterWithManagerInvariantsNoError(m)

    eleza testSingleArgBoundToSingleElementParenthesizedList(self):
        m = mock_contextmanager_generator()
        # This will bind all the arguments to nested() into a single list
        # assigned to foo.
        ukijumuisha Nested(m) kama (foo):
            self.assertInWithManagerInvariants(m)
        self.assertAfterWithManagerInvariantsNoError(m)

    eleza testSingleArgBoundToMultipleElementTupleError(self):
        eleza shouldThrowValueError():
            ukijumuisha Nested(mock_contextmanager_generator()) kama (foo, bar):
                pita
        self.assertRaises(ValueError, shouldThrowValueError)

    eleza testSingleArgUnbound(self):
        mock_contextmanager = mock_contextmanager_generator()
        mock_nested = MockNested(mock_contextmanager)
        ukijumuisha mock_nested:
            self.assertInWithManagerInvariants(mock_contextmanager)
            self.assertInWithManagerInvariants(mock_nested)
        self.assertAfterWithManagerInvariantsNoError(mock_contextmanager)
        self.assertAfterWithManagerInvariantsNoError(mock_nested)

    eleza testMultipleArgUnbound(self):
        m = mock_contextmanager_generator()
        n = mock_contextmanager_generator()
        o = mock_contextmanager_generator()
        mock_nested = MockNested(m, n, o)
        ukijumuisha mock_nested:
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
        ukijumuisha mock_nested kama (m, n, o):
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
            ukijumuisha cm kama self.resource:
                self.assertInWithManagerInvariants(cm)
                self.assertInWithGeneratorInvariants(self.resource)
                self.raiseTestException()
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(cm)
        self.assertAfterWithGeneratorInvariantsWithError(self.resource)

    eleza testExceptionNormalized(self):
        cm = mock_contextmanager_generator()
        eleza shouldThrow():
            ukijumuisha cm kama self.resource:
                # Note this relies on the fact that 1 // 0 produces an exception
                # that ni sio normalized immediately.
                1 // 0
        self.assertRaises(ZeroDivisionError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(cm, ZeroDivisionError)

    eleza testNestedSingleStatements(self):
        mock_a = mock_contextmanager_generator()
        mock_b = mock_contextmanager_generator()
        eleza shouldThrow():
            ukijumuisha mock_a kama self.foo:
                ukijumuisha mock_b kama self.bar:
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
            ukijumuisha mock_nested kama (self.resource_a, self.resource_b):
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
        self.bar = Tupu
        eleza shouldThrow():
            ukijumuisha mock_a kama self.foo:
                self.assertInWithManagerInvariants(mock_a)
                self.assertInWithGeneratorInvariants(self.foo)
                self.raiseTestException()
                ukijumuisha mock_b kama self.bar:
                    pita
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(mock_a)
        self.assertAfterWithGeneratorInvariantsWithError(self.foo)

        # The inner statement stuff should never have been touched
        self.assertEqual(self.bar, Tupu)
        self.assertUongo(mock_b.enter_called)
        self.assertUongo(mock_b.exit_called)
        self.assertEqual(mock_b.exit_args, Tupu)

    eleza testNestedExceptionAfterInnerStatement(self):
        mock_a = mock_contextmanager_generator()
        mock_b = mock_contextmanager_generator()
        eleza shouldThrow():
            ukijumuisha mock_a kama self.foo:
                ukijumuisha mock_b kama self.bar:
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
            tuma

        eleza shouldThrow():
            ukijumuisha cm():
                ashiria StopIteration("kutoka with")

        ukijumuisha self.assertRaisesRegex(StopIteration, 'kutoka with'):
            shouldThrow()

    eleza testRaisedStopIteration2(self):
        # From bug 1462485
        kundi cm(object):
            eleza __enter__(self):
                pita
            eleza __exit__(self, type, value, traceback):
                pita

        eleza shouldThrow():
            ukijumuisha cm():
                ashiria StopIteration("kutoka with")

        ukijumuisha self.assertRaisesRegex(StopIteration, 'kutoka with'):
            shouldThrow()

    eleza testRaisedStopIteration3(self):
        # Another variant where the exception hasn't been instantiated
        # From bug 1705170
        @contextmanager
        eleza cm():
            tuma

        eleza shouldThrow():
            ukijumuisha cm():
                ashiria next(iter([]))

        ukijumuisha self.assertRaises(StopIteration):
            shouldThrow()

    eleza testRaisedGeneratorExit1(self):
        # From bug 1462485
        @contextmanager
        eleza cm():
            tuma

        eleza shouldThrow():
            ukijumuisha cm():
                ashiria GeneratorExit("kutoka with")

        self.assertRaises(GeneratorExit, shouldThrow)

    eleza testRaisedGeneratorExit2(self):
        # From bug 1462485
        kundi cm (object):
            eleza __enter__(self):
                pita
            eleza __exit__(self, type, value, traceback):
                pita

        eleza shouldThrow():
            ukijumuisha cm():
                ashiria GeneratorExit("kutoka with")

        self.assertRaises(GeneratorExit, shouldThrow)

    eleza testErrorsInBool(self):
        # issue4589: __exit__ rudisha code may ashiria an exception
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
            ukijumuisha cm(lambda: Kweli):
                self.fail("Should NOT see this")
        trueAsBool()

        eleza falseAsBool():
            ukijumuisha cm(lambda: Uongo):
                self.fail("Should raise")
        self.assertRaises(AssertionError, falseAsBool)

        eleza failAsBool():
            ukijumuisha cm(lambda: 1//0):
                self.fail("Should NOT see this")
        self.assertRaises(ZeroDivisionError, failAsBool)


kundi NonLocalFlowControlTestCase(unittest.TestCase):

    eleza testWithBreak(self):
        counter = 0
        wakati Kweli:
            counter += 1
            ukijumuisha mock_contextmanager_generator():
                counter += 10
                koma
            counter += 100 # Not reached
        self.assertEqual(counter, 11)

    eleza testWithContinue(self):
        counter = 0
        wakati Kweli:
            counter += 1
            ikiwa counter > 2:
                koma
            ukijumuisha mock_contextmanager_generator():
                counter += 10
                endelea
            counter += 100 # Not reached
        self.assertEqual(counter, 12)

    eleza testWithReturn(self):
        eleza foo():
            counter = 0
            wakati Kweli:
                counter += 1
                ukijumuisha mock_contextmanager_generator():
                    counter += 10
                    rudisha counter
                counter += 100 # Not reached
        self.assertEqual(foo(), 11)

    eleza testWithYield(self):
        eleza gen():
            ukijumuisha mock_contextmanager_generator():
                tuma 12
                tuma 13
        x = list(gen())
        self.assertEqual(x, [12, 13])

    eleza testWithRaise(self):
        counter = 0
        jaribu:
            counter += 1
            ukijumuisha mock_contextmanager_generator():
                counter += 10
                ashiria RuntimeError
            counter += 100 # Not reached
        tatizo RuntimeError:
            self.assertEqual(counter, 11)
        isipokua:
            self.fail("Didn't ashiria RuntimeError")


kundi AssignmentTargetTestCase(unittest.TestCase):

    eleza testSingleComplexTarget(self):
        targets = {1: [0, 1, 2]}
        ukijumuisha mock_contextmanager_generator() kama targets[1][0]:
            self.assertEqual(list(targets.keys()), [1])
            self.assertEqual(targets[1][0].__class__, MockResource)
        ukijumuisha mock_contextmanager_generator() kama list(targets.values())[0][1]:
            self.assertEqual(list(targets.keys()), [1])
            self.assertEqual(targets[1][1].__class__, MockResource)
        ukijumuisha mock_contextmanager_generator() kama targets[2]:
            keys = list(targets.keys())
            keys.sort()
            self.assertEqual(keys, [1, 2])
        kundi C: pita
        blah = C()
        ukijumuisha mock_contextmanager_generator() kama blah.foo:
            self.assertEqual(hasattr(blah, "foo"), Kweli)

    eleza testMultipleComplexTargets(self):
        kundi C:
            eleza __enter__(self): rudisha 1, 2, 3
            eleza __exit__(self, t, v, tb): pita
        targets = {1: [0, 1, 2]}
        ukijumuisha C() kama (targets[1][0], targets[1][1], targets[1][2]):
            self.assertEqual(targets, {1: [1, 2, 3]})
        ukijumuisha C() kama (list(targets.values())[0][2], list(targets.values())[0][1], list(targets.values())[0][0]):
            self.assertEqual(targets, {1: [3, 2, 1]})
        ukijumuisha C() kama (targets[1], targets[2], targets[3]):
            self.assertEqual(targets, {1: 1, 2: 2, 3: 3})
        kundi B: pita
        blah = B()
        ukijumuisha C() kama (blah.one, blah.two, blah.three):
            self.assertEqual(blah.one, 1)
            self.assertEqual(blah.two, 2)
            self.assertEqual(blah.three, 3)


kundi ExitSwallowsExceptionTestCase(unittest.TestCase):

    eleza testExitKweliSwallowsException(self):
        kundi AfricanSwallow:
            eleza __enter__(self): pita
            eleza __exit__(self, t, v, tb): rudisha Kweli
        jaribu:
            ukijumuisha AfricanSwallow():
                1/0
        tatizo ZeroDivisionError:
            self.fail("ZeroDivisionError should have been swallowed")

    eleza testExitUongoDoesntSwallowException(self):
        kundi EuropeanSwallow:
            eleza __enter__(self): pita
            eleza __exit__(self, t, v, tb): rudisha Uongo
        jaribu:
            ukijumuisha EuropeanSwallow():
                1/0
        tatizo ZeroDivisionError:
            pita
        isipokua:
            self.fail("ZeroDivisionError should have been raised")


kundi NestedWith(unittest.TestCase):

    kundi Dummy(object):
        eleza __init__(self, value=Tupu, gobble=Uongo):
            ikiwa value ni Tupu:
                value = self
            self.value = value
            self.gobble = gobble
            self.enter_called = Uongo
            self.exit_called = Uongo

        eleza __enter__(self):
            self.enter_called = Kweli
            rudisha self.value

        eleza __exit__(self, *exc_info):
            self.exit_called = Kweli
            self.exc_info = exc_info
            ikiwa self.gobble:
                rudisha Kweli

    kundi InitRaises(object):
        eleza __init__(self): ashiria RuntimeError()

    kundi EnterRaises(object):
        eleza __enter__(self): ashiria RuntimeError()
        eleza __exit__(self, *exc_info): pita

    kundi ExitRaises(object):
        eleza __enter__(self): pita
        eleza __exit__(self, *exc_info): ashiria RuntimeError()

    eleza testNoExceptions(self):
        ukijumuisha self.Dummy() kama a, self.Dummy() kama b:
            self.assertKweli(a.enter_called)
            self.assertKweli(b.enter_called)
        self.assertKweli(a.exit_called)
        self.assertKweli(b.exit_called)

    eleza testExceptionInExprList(self):
        jaribu:
            ukijumuisha self.Dummy() kama a, self.InitRaises():
                pita
        tatizo:
            pita
        self.assertKweli(a.enter_called)
        self.assertKweli(a.exit_called)

    eleza testExceptionInEnter(self):
        jaribu:
            ukijumuisha self.Dummy() kama a, self.EnterRaises():
                self.fail('body of bad ukijumuisha executed')
        tatizo RuntimeError:
            pita
        isipokua:
            self.fail('RuntimeError sio reraised')
        self.assertKweli(a.enter_called)
        self.assertKweli(a.exit_called)

    eleza testExceptionInExit(self):
        body_executed = Uongo
        ukijumuisha self.Dummy(gobble=Kweli) kama a, self.ExitRaises():
            body_executed = Kweli
        self.assertKweli(a.enter_called)
        self.assertKweli(a.exit_called)
        self.assertKweli(body_executed)
        self.assertNotEqual(a.exc_info[0], Tupu)

    eleza testEnterReturnsTuple(self):
        ukijumuisha self.Dummy(value=(1,2)) kama (a1, a2), \
             self.Dummy(value=(10, 20)) kama (b1, b2):
            self.assertEqual(1, a1)
            self.assertEqual(2, a2)
            self.assertEqual(10, b1)
            self.assertEqual(20, b2)

ikiwa __name__ == '__main__':
    unittest.main()
