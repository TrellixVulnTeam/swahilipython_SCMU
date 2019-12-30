"""Test case implementation"""

agiza sys
agiza functools
agiza difflib
agiza logging
agiza pprint
agiza re
agiza warnings
agiza collections
agiza contextlib
agiza traceback
agiza types

kutoka . agiza result
kutoka .util agiza (strclass, safe_repr, _count_diff_all_purpose,
                   _count_diff_hashable, _common_shorten_repr)

__unittest = Kweli

_subtest_msg_sentinel = object()

DIFF_OMITTED = ('\nDiff ni %s characters long. '
                 'Set self.maxDiff to Tupu to see it.')

kundi SkipTest(Exception):
    """
    Raise this exception kwenye a test to skip it.

    Usually you can use TestCase.skipTest() ama one of the skipping decorators
    instead of raising this directly.
    """

kundi _ShouldStop(Exception):
    """
    The test should stop.
    """

kundi _UnexpectedSuccess(Exception):
    """
    The test was supposed to fail, but it didn't!
    """


kundi _Outcome(object):
    eleza __init__(self, result=Tupu):
        self.expecting_failure = Uongo
        self.result = result
        self.result_supports_subtests = hasattr(result, "addSubTest")
        self.success = Kweli
        self.skipped = []
        self.expectedFailure = Tupu
        self.errors = []

    @contextlib.contextmanager
    eleza testPartExecutor(self, test_case, isTest=Uongo):
        old_success = self.success
        self.success = Kweli
        jaribu:
            tuma
        tatizo KeyboardInterrupt:
            ashiria
        tatizo SkipTest kama e:
            self.success = Uongo
            self.skipped.append((test_case, str(e)))
        tatizo _ShouldStop:
            pita
        tatizo:
            exc_info = sys.exc_info()
            ikiwa self.expecting_failure:
                self.expectedFailure = exc_info
            isipokua:
                self.success = Uongo
                self.errors.append((test_case, exc_info))
            # explicitly koma a reference cycle:
            # exc_info -> frame -> exc_info
            exc_info = Tupu
        isipokua:
            ikiwa self.result_supports_subtests na self.success:
                self.errors.append((test_case, Tupu))
        mwishowe:
            self.success = self.success na old_success


eleza _id(obj):
    rudisha obj


_module_cleanups = []
eleza addModuleCleanup(function, /, *args, **kwargs):
    """Same kama addCleanup, tatizo the cleanup items are called even if
    setUpModule fails (unlike tearDownModule)."""
    _module_cleanups.append((function, args, kwargs))


eleza doModuleCleanups():
    """Execute all module cleanup functions. Normally called kila you after
    tearDownModule."""
    exceptions = []
    wakati _module_cleanups:
        function, args, kwargs = _module_cleanups.pop()
        jaribu:
            function(*args, **kwargs)
        tatizo Exception kama exc:
            exceptions.append(exc)
    ikiwa exceptions:
        # Swallows all but first exception. If a multi-exception handler
        # gets written we should use that here instead.
        ashiria exceptions[0]


eleza skip(reason):
    """
    Unconditionally skip a test.
    """
    eleza decorator(test_item):
        ikiwa sio isinstance(test_item, type):
            @functools.wraps(test_item)
            eleza skip_wrapper(*args, **kwargs):
                ashiria SkipTest(reason)
            test_item = skip_wrapper

        test_item.__unittest_skip__ = Kweli
        test_item.__unittest_skip_why__ = reason
        rudisha test_item
    ikiwa isinstance(reason, types.FunctionType):
        test_item = reason
        reason = ''
        rudisha decorator(test_item)
    rudisha decorator

eleza skipIf(condition, reason):
    """
    Skip a test ikiwa the condition ni true.
    """
    ikiwa condition:
        rudisha skip(reason)
    rudisha _id

eleza skipUnless(condition, reason):
    """
    Skip a test unless the condition ni true.
    """
    ikiwa sio condition:
        rudisha skip(reason)
    rudisha _id

eleza expectedFailure(test_item):
    test_item.__unittest_expecting_failure__ = Kweli
    rudisha test_item

eleza _is_subtype(expected, basetype):
    ikiwa isinstance(expected, tuple):
        rudisha all(_is_subtype(e, basetype) kila e kwenye expected)
    rudisha isinstance(expected, type) na issubclass(expected, basetype)

kundi _BaseTestCaseContext:

    eleza __init__(self, test_case):
        self.test_case = test_case

    eleza _ashiriaFailure(self, standardMsg):
        msg = self.test_case._formatMessage(self.msg, standardMsg)
        ashiria self.test_case.failureException(msg)

kundi _AssertRaisesBaseContext(_BaseTestCaseContext):

    eleza __init__(self, expected, test_case, expected_regex=Tupu):
        _BaseTestCaseContext.__init__(self, test_case)
        self.expected = expected
        self.test_case = test_case
        ikiwa expected_regex ni sio Tupu:
            expected_regex = re.compile(expected_regex)
        self.expected_regex = expected_regex
        self.obj_name = Tupu
        self.msg = Tupu

    eleza handle(self, name, args, kwargs):
        """
        If args ni empty, assertRaises/Warns ni being used kama a
        context manager, so check kila a 'msg' kwarg na rudisha self.
        If args ni sio empty, call a callable pitaing positional na keyword
        arguments.
        """
        jaribu:
            ikiwa sio _is_subtype(self.expected, self._base_type):
                ashiria TypeError('%s() arg 1 must be %s' %
                                (name, self._base_type_str))
            ikiwa sio args:
                self.msg = kwargs.pop('msg', Tupu)
                ikiwa kwargs:
                    ashiria TypeError('%r ni an invalid keyword argument kila '
                                    'this function' % (next(iter(kwargs)),))
                rudisha self

            callable_obj, *args = args
            jaribu:
                self.obj_name = callable_obj.__name__
            tatizo AttributeError:
                self.obj_name = str(callable_obj)
            ukijumuisha self:
                callable_obj(*args, **kwargs)
        mwishowe:
            # bpo-23890: manually koma a reference cycle
            self = Tupu


kundi _AssertRaisesContext(_AssertRaisesBaseContext):
    """A context manager used to implement TestCase.assertRaises* methods."""

    _base_type = BaseException
    _base_type_str = 'an exception type ama tuple of exception types'

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, exc_type, exc_value, tb):
        ikiwa exc_type ni Tupu:
            jaribu:
                exc_name = self.expected.__name__
            tatizo AttributeError:
                exc_name = str(self.expected)
            ikiwa self.obj_name:
                self._ashiriaFailure("{} sio ashiriad by {}".format(exc_name,
                                                                self.obj_name))
            isipokua:
                self._ashiriaFailure("{} sio ashiriad".format(exc_name))
        isipokua:
            traceback.clear_frames(tb)
        ikiwa sio issubclass(exc_type, self.expected):
            # let unexpected exceptions pita through
            rudisha Uongo
        # store exception, without traceback, kila later retrieval
        self.exception = exc_value.with_traceback(Tupu)
        ikiwa self.expected_regex ni Tupu:
            rudisha Kweli

        expected_regex = self.expected_regex
        ikiwa sio expected_regex.search(str(exc_value)):
            self._ashiriaFailure('"{}" does sio match "{}"'.format(
                     expected_regex.pattern, str(exc_value)))
        rudisha Kweli


kundi _AssertWarnsContext(_AssertRaisesBaseContext):
    """A context manager used to implement TestCase.assertWarns* methods."""

    _base_type = Warning
    _base_type_str = 'a warning type ama tuple of warning types'

    eleza __enter__(self):
        # The __warningregistry__'s need to be kwenye a pristine state kila tests
        # to work properly.
        kila v kwenye sys.modules.values():
            ikiwa getattr(v, '__warningregistry__', Tupu):
                v.__warningregistry__ = {}
        self.warnings_manager = warnings.catch_warnings(record=Kweli)
        self.warnings = self.warnings_manager.__enter__()
        warnings.simplefilter("always", self.expected)
        rudisha self

    eleza __exit__(self, exc_type, exc_value, tb):
        self.warnings_manager.__exit__(exc_type, exc_value, tb)
        ikiwa exc_type ni sio Tupu:
            # let unexpected exceptions pita through
            rudisha
        jaribu:
            exc_name = self.expected.__name__
        tatizo AttributeError:
            exc_name = str(self.expected)
        first_matching = Tupu
        kila m kwenye self.warnings:
            w = m.message
            ikiwa sio isinstance(w, self.expected):
                endelea
            ikiwa first_matching ni Tupu:
                first_matching = w
            ikiwa (self.expected_regex ni sio Tupu na
                sio self.expected_regex.search(str(w))):
                endelea
            # store warning kila later retrieval
            self.warning = w
            self.filename = m.filename
            self.lineno = m.lineno
            rudisha
        # Now we simply try to choose a helpful failure message
        ikiwa first_matching ni sio Tupu:
            self._ashiriaFailure('"{}" does sio match "{}"'.format(
                     self.expected_regex.pattern, str(first_matching)))
        ikiwa self.obj_name:
            self._ashiriaFailure("{} sio triggered by {}".format(exc_name,
                                                               self.obj_name))
        isipokua:
            self._ashiriaFailure("{} sio triggered".format(exc_name))



_LoggingWatcher = collections.namedtuple("_LoggingWatcher",
                                         ["records", "output"])


kundi _CapturingHandler(logging.Handler):
    """
    A logging handler capturing all (raw na formatted) logging output.
    """

    eleza __init__(self):
        logging.Handler.__init__(self)
        self.watcher = _LoggingWatcher([], [])

    eleza flush(self):
        pita

    eleza emit(self, record):
        self.watcher.records.append(record)
        msg = self.format(record)
        self.watcher.output.append(msg)



kundi _AssertLogsContext(_BaseTestCaseContext):
    """A context manager used to implement TestCase.assertLogs()."""

    LOGGING_FORMAT = "%(levelname)s:%(name)s:%(message)s"

    eleza __init__(self, test_case, logger_name, level):
        _BaseTestCaseContext.__init__(self, test_case)
        self.logger_name = logger_name
        ikiwa level:
            self.level = logging._nameToLevel.get(level, level)
        isipokua:
            self.level = logging.INFO
        self.msg = Tupu

    eleza __enter__(self):
        ikiwa isinstance(self.logger_name, logging.Logger):
            logger = self.logger = self.logger_name
        isipokua:
            logger = self.logger = logging.getLogger(self.logger_name)
        formatter = logging.Formatter(self.LOGGING_FORMAT)
        handler = _CapturingHandler()
        handler.setFormatter(formatter)
        self.watcher = handler.watcher
        self.old_handlers = logger.handlers[:]
        self.old_level = logger.level
        self.old_propagate = logger.propagate
        logger.handlers = [handler]
        logger.setLevel(self.level)
        logger.propagate = Uongo
        rudisha handler.watcher

    eleza __exit__(self, exc_type, exc_value, tb):
        self.logger.handlers = self.old_handlers
        self.logger.propagate = self.old_propagate
        self.logger.setLevel(self.old_level)
        ikiwa exc_type ni sio Tupu:
            # let unexpected exceptions pita through
            rudisha Uongo
        ikiwa len(self.watcher.records) == 0:
            self._ashiriaFailure(
                "no logs of level {} ama higher triggered on {}"
                .format(logging.getLevelName(self.level), self.logger.name))


kundi _OrderedChainMap(collections.ChainMap):
    eleza __iter__(self):
        seen = set()
        kila mapping kwenye self.maps:
            kila k kwenye mapping:
                ikiwa k haiko kwenye seen:
                    seen.add(k)
                    tuma k


kundi TestCase(object):
    """A kundi whose instances are single test cases.

    By default, the test code itself should be placed kwenye a method named
    'runTest'.

    If the fixture may be used kila many test cases, create as
    many test methods kama are needed. When instantiating such a TestCase
    subclass, specify kwenye the constructor arguments the name of the test method
    that the instance ni to execute.

    Test authors should subkundi TestCase kila their own tests. Construction
    na deconstruction of the test's environment ('fixture') can be
    implemented by overriding the 'setUp' na 'tearDown' methods respectively.

    If it ni necessary to override the __init__ method, the base class
    __init__ method must always be called. It ni agizaant that subclasses
    should sio change the signature of their __init__ method, since instances
    of the classes are instantiated automatically by parts of the framework
    kwenye order to be run.

    When subclassing TestCase, you can set these attributes:
    * failureException: determines which exception will be ashiriad when
        the instance's assertion methods fail; test methods raising this
        exception will be deemed to have 'failed' rather than 'errored'.
    * longMessage: determines whether long messages (including repr of
        objects used kwenye assert methods) will be printed on failure kwenye *addition*
        to any explicit message pitaed.
    * maxDiff: sets the maximum length of a diff kwenye failure messages
        by assert methods using difflib. It ni looked up kama an instance
        attribute so can be configured by individual tests ikiwa required.
    """

    failureException = AssertionError

    longMessage = Kweli

    maxDiff = 80*8

    # If a string ni longer than _diffThreshold, use normal comparison instead
    # of difflib.  See #11763.
    _diffThreshold = 2**16

    # Attribute used by TestSuite kila classSetUp

    _classSetupFailed = Uongo

    _class_cleanups = []

    eleza __init__(self, methodName='runTest'):
        """Create an instance of the kundi that will use the named test
           method when executed. Raises a ValueError ikiwa the instance does
           sio have a method ukijumuisha the specified name.
        """
        self._testMethodName = methodName
        self._outcome = Tupu
        self._testMethodDoc = 'No test'
        jaribu:
            testMethod = getattr(self, methodName)
        tatizo AttributeError:
            ikiwa methodName != 'runTest':
                # we allow instantiation ukijumuisha no explicit method name
                # but sio an *incorrect* ama missing method name
                ashiria ValueError("no such test method kwenye %s: %s" %
                      (self.__class__, methodName))
        isipokua:
            self._testMethodDoc = testMethod.__doc__
        self._cleanups = []
        self._subtest = Tupu

        # Map types to custom assertEqual functions that will compare
        # instances of said type kwenye more detail to generate a more useful
        # error message.
        self._type_equality_funcs = {}
        self.addTypeEqualityFunc(dict, 'assertDictEqual')
        self.addTypeEqualityFunc(list, 'assertListEqual')
        self.addTypeEqualityFunc(tuple, 'assertTupleEqual')
        self.addTypeEqualityFunc(set, 'assertSetEqual')
        self.addTypeEqualityFunc(frozenset, 'assertSetEqual')
        self.addTypeEqualityFunc(str, 'assertMultiLineEqual')

    eleza addTypeEqualityFunc(self, typeobj, function):
        """Add a type specific assertEqual style function to compare a type.

        This method ni kila use by TestCase subclasses that need to register
        their own type equality functions to provide nicer error messages.

        Args:
            typeobj: The data type to call this function on when both values
                    are of the same type kwenye assertEqual().
            function: The callable taking two arguments na an optional
                    msg= argument that ashirias self.failureException ukijumuisha a
                    useful error message when the two arguments are sio equal.
        """
        self._type_equality_funcs[typeobj] = function

    eleza addCleanup(*args, **kwargs):
        """Add a function, ukijumuisha arguments, to be called when the test is
        completed. Functions added are called on a LIFO basis na are
        called after tearDown on test failure ama success.

        Cleanup items are called even ikiwa setUp fails (unlike tearDown)."""
        ikiwa len(args) >= 2:
            self, function, *args = args
        lasivyo sio args:
            ashiria TypeError("descriptor 'addCleanup' of 'TestCase' object "
                            "needs an argument")
        lasivyo 'function' kwenye kwargs:
            function = kwargs.pop('function')
            self, *args = args
            agiza warnings
            warnings.warn("Passing 'function' kama keyword argument ni deprecated",
                          DeprecationWarning, stacklevel=2)
        isipokua:
            ashiria TypeError('addCleanup expected at least 1 positional '
                            'argument, got %d' % (len(args)-1))
        args = tuple(args)

        self._cleanups.append((function, args, kwargs))
    addCleanup.__text_signature__ = '($self, function, /, *args, **kwargs)'

    @classmethod
    eleza addClassCleanup(cls, function, /, *args, **kwargs):
        """Same kama addCleanup, tatizo the cleanup items are called even if
        setUpClass fails (unlike tearDownClass)."""
        cls._class_cleanups.append((function, args, kwargs))

    eleza setUp(self):
        "Hook method kila setting up the test fixture before exercising it."
        pita

    eleza tearDown(self):
        "Hook method kila deconstructing the test fixture after testing it."
        pita

    @classmethod
    eleza setUpClass(cls):
        "Hook method kila setting up kundi fixture before running tests kwenye the class."

    @classmethod
    eleza tearDownClass(cls):
        "Hook method kila deconstructing the kundi fixture after running all tests kwenye the class."

    eleza countTestCases(self):
        rudisha 1

    eleza defaultTestResult(self):
        rudisha result.TestResult()

    eleza shortDescription(self):
        """Returns a one-line description of the test, ama Tupu ikiwa no
        description has been provided.

        The default implementation of this method rudishas the first line of
        the specified test method's docstring.
        """
        doc = self._testMethodDoc
        rudisha doc na doc.split("\n")[0].strip() ama Tupu


    eleza id(self):
        rudisha "%s.%s" % (strclass(self.__class__), self._testMethodName)

    eleza __eq__(self, other):
        ikiwa type(self) ni sio type(other):
            rudisha NotImplemented

        rudisha self._testMethodName == other._testMethodName

    eleza __hash__(self):
        rudisha hash((type(self), self._testMethodName))

    eleza __str__(self):
        rudisha "%s (%s)" % (self._testMethodName, strclass(self.__class__))

    eleza __repr__(self):
        rudisha "<%s testMethod=%s>" % \
               (strclass(self.__class__), self._testMethodName)

    eleza _addSkip(self, result, test_case, reason):
        addSkip = getattr(result, 'addSkip', Tupu)
        ikiwa addSkip ni sio Tupu:
            addSkip(test_case, reason)
        isipokua:
            warnings.warn("TestResult has no addSkip method, skips sio reported",
                          RuntimeWarning, 2)
            result.addSuccess(test_case)

    @contextlib.contextmanager
    eleza subTest(self, msg=_subtest_msg_sentinel, **params):
        """Return a context manager that will rudisha the enclosed block
        of code kwenye a subtest identified by the optional message na
        keyword parameters.  A failure kwenye the subtest marks the test
        case kama failed but resumes execution at the end of the enclosed
        block, allowing further test code to be executed.
        """
        ikiwa self._outcome ni Tupu ama sio self._outcome.result_supports_subtests:
            tuma
            rudisha
        parent = self._subtest
        ikiwa parent ni Tupu:
            params_map = _OrderedChainMap(params)
        isipokua:
            params_map = parent.params.new_child(params)
        self._subtest = _SubTest(self, msg, params_map)
        jaribu:
            ukijumuisha self._outcome.testPartExecutor(self._subtest, isTest=Kweli):
                tuma
            ikiwa sio self._outcome.success:
                result = self._outcome.result
                ikiwa result ni sio Tupu na result.failfast:
                    ashiria _ShouldStop
            lasivyo self._outcome.expectedFailure:
                # If the test ni expecting a failure, we really want to
                # stop now na register the expected failure.
                ashiria _ShouldStop
        mwishowe:
            self._subtest = parent

    eleza _feedErrorsToResult(self, result, errors):
        kila test, exc_info kwenye errors:
            ikiwa isinstance(test, _SubTest):
                result.addSubTest(test.test_case, test, exc_info)
            lasivyo exc_info ni sio Tupu:
                ikiwa issubclass(exc_info[0], self.failureException):
                    result.addFailure(test, exc_info)
                isipokua:
                    result.addError(test, exc_info)

    eleza _addExpectedFailure(self, result, exc_info):
        jaribu:
            addExpectedFailure = result.addExpectedFailure
        tatizo AttributeError:
            warnings.warn("TestResult has no addExpectedFailure method, reporting kama pitaes",
                          RuntimeWarning)
            result.addSuccess(self)
        isipokua:
            addExpectedFailure(self, exc_info)

    eleza _addUnexpectedSuccess(self, result):
        jaribu:
            addUnexpectedSuccess = result.addUnexpectedSuccess
        tatizo AttributeError:
            warnings.warn("TestResult has no addUnexpectedSuccess method, reporting kama failure",
                          RuntimeWarning)
            # We need to pita an actual exception na traceback to addFailure,
            # otherwise the legacy result can choke.
            jaribu:
                ashiria _UnexpectedSuccess kutoka Tupu
            tatizo _UnexpectedSuccess:
                result.addFailure(self, sys.exc_info())
        isipokua:
            addUnexpectedSuccess(self)

    eleza _callSetUp(self):
        self.setUp()

    eleza _callTestMethod(self, method):
        method()

    eleza _callTearDown(self):
        self.tearDown()

    eleza _callCleanup(self, function, /, *args, **kwargs):
        function(*args, **kwargs)

    eleza run(self, result=Tupu):
        orig_result = result
        ikiwa result ni Tupu:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', Tupu)
            ikiwa startTestRun ni sio Tupu:
                startTestRun()

        result.startTest(self)

        testMethod = getattr(self, self._testMethodName)
        ikiwa (getattr(self.__class__, "__unittest_skip__", Uongo) ama
            getattr(testMethod, "__unittest_skip__", Uongo)):
            # If the kundi ama method was skipped.
            jaribu:
                skip_why = (getattr(self.__class__, '__unittest_skip_why__', '')
                            ama getattr(testMethod, '__unittest_skip_why__', ''))
                self._addSkip(result, self, skip_why)
            mwishowe:
                result.stopTest(self)
            rudisha
        expecting_failure_method = getattr(testMethod,
                                           "__unittest_expecting_failure__", Uongo)
        expecting_failure_kundi = getattr(self,
                                          "__unittest_expecting_failure__", Uongo)
        expecting_failure = expecting_failure_kundi ama expecting_failure_method
        outcome = _Outcome(result)
        jaribu:
            self._outcome = outcome

            ukijumuisha outcome.testPartExecutor(self):
                self._callSetUp()
            ikiwa outcome.success:
                outcome.expecting_failure = expecting_failure
                ukijumuisha outcome.testPartExecutor(self, isTest=Kweli):
                    self._callTestMethod(testMethod)
                outcome.expecting_failure = Uongo
                ukijumuisha outcome.testPartExecutor(self):
                    self._callTearDown()

            self.doCleanups()
            kila test, reason kwenye outcome.skipped:
                self._addSkip(result, test, reason)
            self._feedErrorsToResult(result, outcome.errors)
            ikiwa outcome.success:
                ikiwa expecting_failure:
                    ikiwa outcome.expectedFailure:
                        self._addExpectedFailure(result, outcome.expectedFailure)
                    isipokua:
                        self._addUnexpectedSuccess(result)
                isipokua:
                    result.addSuccess(self)
            rudisha result
        mwishowe:
            result.stopTest(self)
            ikiwa orig_result ni Tupu:
                stopTestRun = getattr(result, 'stopTestRun', Tupu)
                ikiwa stopTestRun ni sio Tupu:
                    stopTestRun()

            # explicitly koma reference cycles:
            # outcome.errors -> frame -> outcome -> outcome.errors
            # outcome.expectedFailure -> frame -> outcome -> outcome.expectedFailure
            outcome.errors.clear()
            outcome.expectedFailure = Tupu

            # clear the outcome, no more needed
            self._outcome = Tupu

    eleza doCleanups(self):
        """Execute all cleanup functions. Normally called kila you after
        tearDown."""
        outcome = self._outcome ama _Outcome()
        wakati self._cleanups:
            function, args, kwargs = self._cleanups.pop()
            ukijumuisha outcome.testPartExecutor(self):
                self._callCleanup(function, *args, **kwargs)

        # rudisha this kila backwards compatibility
        # even though we no longer use it internally
        rudisha outcome.success

    @classmethod
    eleza doClassCleanups(cls):
        """Execute all kundi cleanup functions. Normally called kila you after
        tearDownClass."""
        cls.tearDown_exceptions = []
        wakati cls._class_cleanups:
            function, args, kwargs = cls._class_cleanups.pop()
            jaribu:
                function(*args, **kwargs)
            tatizo Exception kama exc:
                cls.tearDown_exceptions.append(sys.exc_info())

    eleza __call__(self, *args, **kwds):
        rudisha self.run(*args, **kwds)

    eleza debug(self):
        """Run the test without collecting errors kwenye a TestResult"""
        self.setUp()
        getattr(self, self._testMethodName)()
        self.tearDown()
        wakati self._cleanups:
            function, args, kwargs = self._cleanups.pop(-1)
            function(*args, **kwargs)

    eleza skipTest(self, reason):
        """Skip this test."""
        ashiria SkipTest(reason)

    eleza fail(self, msg=Tupu):
        """Fail immediately, ukijumuisha the given message."""
        ashiria self.failureException(msg)

    eleza assertUongo(self, expr, msg=Tupu):
        """Check that the expression ni false."""
        ikiwa expr:
            msg = self._formatMessage(msg, "%s ni sio false" % safe_repr(expr))
            ashiria self.failureException(msg)

    eleza assertKweli(self, expr, msg=Tupu):
        """Check that the expression ni true."""
        ikiwa sio expr:
            msg = self._formatMessage(msg, "%s ni sio true" % safe_repr(expr))
            ashiria self.failureException(msg)

    eleza _formatMessage(self, msg, standardMsg):
        """Honour the longMessage attribute when generating failure messages.
        If longMessage ni Uongo this means:
        * Use only an explicit message ikiwa it ni provided
        * Otherwise use the standard message kila the assert

        If longMessage ni Kweli:
        * Use the standard message
        * If an explicit message ni provided, plus ' : ' na the explicit message
        """
        ikiwa sio self.longMessage:
            rudisha msg ama standardMsg
        ikiwa msg ni Tupu:
            rudisha standardMsg
        jaribu:
            # don't switch to '{}' formatting kwenye Python 2.X
            # it changes the way unicode input ni handled
            rudisha '%s : %s' % (standardMsg, msg)
        tatizo UnicodeDecodeError:
            rudisha  '%s : %s' % (safe_repr(standardMsg), safe_repr(msg))

    eleza assertRaises(self, expected_exception, *args, **kwargs):
        """Fail unless an exception of kundi expected_exception ni ashiriad
           by the callable when invoked ukijumuisha specified positional na
           keyword arguments. If a different type of exception is
           ashiriad, it will sio be caught, na the test case will be
           deemed to have suffered an error, exactly kama kila an
           unexpected exception.

           If called ukijumuisha the callable na arguments omitted, will rudisha a
           context object used like this::

                ukijumuisha self.assertRaises(SomeException):
                    do_something()

           An optional keyword argument 'msg' can be provided when assertRaises
           ni used kama a context object.

           The context manager keeps a reference to the exception as
           the 'exception' attribute. This allows you to inspect the
           exception after the assertion::

               ukijumuisha self.assertRaises(SomeException) kama cm:
                   do_something()
               the_exception = cm.exception
               self.assertEqual(the_exception.error_code, 3)
        """
        context = _AssertRaisesContext(expected_exception, self)
        jaribu:
            rudisha context.handle('assertRaises', args, kwargs)
        mwishowe:
            # bpo-23890: manually koma a reference cycle
            context = Tupu

    eleza assertWarns(self, expected_warning, *args, **kwargs):
        """Fail unless a warning of kundi warnClass ni triggered
           by the callable when invoked ukijumuisha specified positional na
           keyword arguments.  If a different type of warning is
           triggered, it will sio be handled: depending on the other
           warning filtering rules kwenye effect, it might be silenced, printed
           out, ama ashiriad kama an exception.

           If called ukijumuisha the callable na arguments omitted, will rudisha a
           context object used like this::

                ukijumuisha self.assertWarns(SomeWarning):
                    do_something()

           An optional keyword argument 'msg' can be provided when assertWarns
           ni used kama a context object.

           The context manager keeps a reference to the first matching
           warning kama the 'warning' attribute; similarly, the 'filename'
           na 'lineno' attributes give you information about the line
           of Python code kutoka which the warning was triggered.
           This allows you to inspect the warning after the assertion::

               ukijumuisha self.assertWarns(SomeWarning) kama cm:
                   do_something()
               the_warning = cm.warning
               self.assertEqual(the_warning.some_attribute, 147)
        """
        context = _AssertWarnsContext(expected_warning, self)
        rudisha context.handle('assertWarns', args, kwargs)

    eleza assertLogs(self, logger=Tupu, level=Tupu):
        """Fail unless a log message of level *level* ama higher ni emitted
        on *logger_name* ama its children.  If omitted, *level* defaults to
        INFO na *logger* defaults to the root logger.

        This method must be used kama a context manager, na will tuma
        a recording object ukijumuisha two attributes: `output` na `records`.
        At the end of the context manager, the `output` attribute will
        be a list of the matching formatted log messages na the
        `records` attribute will be a list of the corresponding LogRecord
        objects.

        Example::

            ukijumuisha self.assertLogs('foo', level='INFO') kama cm:
                logging.getLogger('foo').info('first message')
                logging.getLogger('foo.bar').error('second message')
            self.assertEqual(cm.output, ['INFO:foo:first message',
                                         'ERROR:foo.bar:second message'])
        """
        rudisha _AssertLogsContext(self, logger, level)

    eleza _getAssertEqualityFunc(self, first, second):
        """Get a detailed comparison function kila the types of the two args.

        Returns: A callable accepting (first, second, msg=Tupu) that will
        ashiria a failure exception ikiwa first != second ukijumuisha a useful human
        readable error message kila those types.
        """
        #
        # NOTE(gregory.p.smith): I considered isinstance(first, type(second))
        # na vice versa.  I opted kila the conservative approach kwenye case
        # subclasses are sio intended to be compared kwenye detail to their super
        # kundi instances using a type equality func.  This means testing
        # subtypes won't automagically use the detailed comparison.  Callers
        # should use their type specific assertSpamEqual method to compare
        # subclasses ikiwa the detailed comparison ni desired na appropriate.
        # See the discussion kwenye http://bugs.python.org/issue2578.
        #
        ikiwa type(first) ni type(second):
            asserter = self._type_equality_funcs.get(type(first))
            ikiwa asserter ni sio Tupu:
                ikiwa isinstance(asserter, str):
                    asserter = getattr(self, asserter)
                rudisha asserter

        rudisha self._baseAssertEqual

    eleza _baseAssertEqual(self, first, second, msg=Tupu):
        """The default assertEqual implementation, sio type specific."""
        ikiwa sio first == second:
            standardMsg = '%s != %s' % _common_shorten_repr(first, second)
            msg = self._formatMessage(msg, standardMsg)
            ashiria self.failureException(msg)

    eleza assertEqual(self, first, second, msg=Tupu):
        """Fail ikiwa the two objects are unequal kama determined by the '=='
           operator.
        """
        assertion_func = self._getAssertEqualityFunc(first, second)
        assertion_func(first, second, msg=msg)

    eleza assertNotEqual(self, first, second, msg=Tupu):
        """Fail ikiwa the two objects are equal kama determined by the '!='
           operator.
        """
        ikiwa sio first != second:
            msg = self._formatMessage(msg, '%s == %s' % (safe_repr(first),
                                                          safe_repr(second)))
            ashiria self.failureException(msg)

    eleza assertAlmostEqual(self, first, second, places=Tupu, msg=Tupu,
                          delta=Tupu):
        """Fail ikiwa the two objects are unequal kama determined by their
           difference rounded to the given number of decimal places
           (default 7) na comparing to zero, ama by comparing that the
           difference between the two objects ni more than the given
           delta.

           Note that decimal places (kutoka zero) are usually sio the same
           kama significant digits (measured kutoka the most significant digit).

           If the two objects compare equal then they will automatically
           compare almost equal.
        """
        ikiwa first == second:
            # shortcut
            rudisha
        ikiwa delta ni sio Tupu na places ni sio Tupu:
            ashiria TypeError("specify delta ama places sio both")

        diff = abs(first - second)
        ikiwa delta ni sio Tupu:
            ikiwa diff <= delta:
                rudisha

            standardMsg = '%s != %s within %s delta (%s difference)' % (
                safe_repr(first),
                safe_repr(second),
                safe_repr(delta),
                safe_repr(diff))
        isipokua:
            ikiwa places ni Tupu:
                places = 7

            ikiwa round(diff, places) == 0:
                rudisha

            standardMsg = '%s != %s within %r places (%s difference)' % (
                safe_repr(first),
                safe_repr(second),
                places,
                safe_repr(diff))
        msg = self._formatMessage(msg, standardMsg)
        ashiria self.failureException(msg)

    eleza assertNotAlmostEqual(self, first, second, places=Tupu, msg=Tupu,
                             delta=Tupu):
        """Fail ikiwa the two objects are equal kama determined by their
           difference rounded to the given number of decimal places
           (default 7) na comparing to zero, ama by comparing that the
           difference between the two objects ni less than the given delta.

           Note that decimal places (kutoka zero) are usually sio the same
           kama significant digits (measured kutoka the most significant digit).

           Objects that are equal automatically fail.
        """
        ikiwa delta ni sio Tupu na places ni sio Tupu:
            ashiria TypeError("specify delta ama places sio both")
        diff = abs(first - second)
        ikiwa delta ni sio Tupu:
            ikiwa sio (first == second) na diff > delta:
                rudisha
            standardMsg = '%s == %s within %s delta (%s difference)' % (
                safe_repr(first),
                safe_repr(second),
                safe_repr(delta),
                safe_repr(diff))
        isipokua:
            ikiwa places ni Tupu:
                places = 7
            ikiwa sio (first == second) na round(diff, places) != 0:
                rudisha
            standardMsg = '%s == %s within %r places' % (safe_repr(first),
                                                         safe_repr(second),
                                                         places)

        msg = self._formatMessage(msg, standardMsg)
        ashiria self.failureException(msg)

    eleza assertSequenceEqual(self, seq1, seq2, msg=Tupu, seq_type=Tupu):
        """An equality assertion kila ordered sequences (like lists na tuples).

        For the purposes of this function, a valid ordered sequence type ni one
        which can be indexed, has a length, na has an equality operator.

        Args:
            seq1: The first sequence to compare.
            seq2: The second sequence to compare.
            seq_type: The expected datatype of the sequences, ama Tupu ikiwa no
                    datatype should be enforced.
            msg: Optional message to use on failure instead of a list of
                    differences.
        """
        ikiwa seq_type ni sio Tupu:
            seq_type_name = seq_type.__name__
            ikiwa sio isinstance(seq1, seq_type):
                ashiria self.failureException('First sequence ni sio a %s: %s'
                                        % (seq_type_name, safe_repr(seq1)))
            ikiwa sio isinstance(seq2, seq_type):
                ashiria self.failureException('Second sequence ni sio a %s: %s'
                                        % (seq_type_name, safe_repr(seq2)))
        isipokua:
            seq_type_name = "sequence"

        differing = Tupu
        jaribu:
            len1 = len(seq1)
        tatizo (TypeError, NotImplementedError):
            differing = 'First %s has no length.    Non-sequence?' % (
                    seq_type_name)

        ikiwa differing ni Tupu:
            jaribu:
                len2 = len(seq2)
            tatizo (TypeError, NotImplementedError):
                differing = 'Second %s has no length.    Non-sequence?' % (
                        seq_type_name)

        ikiwa differing ni Tupu:
            ikiwa seq1 == seq2:
                rudisha

            differing = '%ss differ: %s != %s\n' % (
                    (seq_type_name.capitalize(),) +
                    _common_shorten_repr(seq1, seq2))

            kila i kwenye range(min(len1, len2)):
                jaribu:
                    item1 = seq1[i]
                tatizo (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of first %s\n' %
                                 (i, seq_type_name))
                    koma

                jaribu:
                    item2 = seq2[i]
                tatizo (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of second %s\n' %
                                 (i, seq_type_name))
                    koma

                ikiwa item1 != item2:
                    differing += ('\nFirst differing element %d:\n%s\n%s\n' %
                                 ((i,) + _common_shorten_repr(item1, item2)))
                    koma
            isipokua:
                ikiwa (len1 == len2 na seq_type ni Tupu na
                    type(seq1) != type(seq2)):
                    # The sequences are the same, but have differing types.
                    rudisha

            ikiwa len1 > len2:
                differing += ('\nFirst %s contains %d additional '
                             'elements.\n' % (seq_type_name, len1 - len2))
                jaribu:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len2, safe_repr(seq1[len2])))
                tatizo (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of first %s\n' % (len2, seq_type_name))
            lasivyo len1 < len2:
                differing += ('\nSecond %s contains %d additional '
                             'elements.\n' % (seq_type_name, len2 - len1))
                jaribu:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len1, safe_repr(seq2[len1])))
                tatizo (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of second %s\n' % (len1, seq_type_name))
        standardMsg = differing
        diffMsg = '\n' + '\n'.join(
            difflib.ndiff(pprint.pformat(seq1).splitlines(),
                          pprint.pformat(seq2).splitlines()))

        standardMsg = self._truncateMessage(standardMsg, diffMsg)
        msg = self._formatMessage(msg, standardMsg)
        self.fail(msg)

    eleza _truncateMessage(self, message, diff):
        max_diff = self.maxDiff
        ikiwa max_diff ni Tupu ama len(diff) <= max_diff:
            rudisha message + diff
        rudisha message + (DIFF_OMITTED % len(diff))

    eleza assertListEqual(self, list1, list2, msg=Tupu):
        """A list-specific equality assertion.

        Args:
            list1: The first list to compare.
            list2: The second list to compare.
            msg: Optional message to use on failure instead of a list of
                    differences.

        """
        self.assertSequenceEqual(list1, list2, msg, seq_type=list)

    eleza assertTupleEqual(self, tuple1, tuple2, msg=Tupu):
        """A tuple-specific equality assertion.

        Args:
            tuple1: The first tuple to compare.
            tuple2: The second tuple to compare.
            msg: Optional message to use on failure instead of a list of
                    differences.
        """
        self.assertSequenceEqual(tuple1, tuple2, msg, seq_type=tuple)

    eleza assertSetEqual(self, set1, set2, msg=Tupu):
        """A set-specific equality assertion.

        Args:
            set1: The first set to compare.
            set2: The second set to compare.
            msg: Optional message to use on failure instead of a list of
                    differences.

        assertSetEqual uses ducktyping to support different types of sets, na
        ni optimized kila sets specifically (parameters must support a
        difference method).
        """
        jaribu:
            difference1 = set1.difference(set2)
        tatizo TypeError kama e:
            self.fail('invalid type when attempting set difference: %s' % e)
        tatizo AttributeError kama e:
            self.fail('first argument does sio support set difference: %s' % e)

        jaribu:
            difference2 = set2.difference(set1)
        tatizo TypeError kama e:
            self.fail('invalid type when attempting set difference: %s' % e)
        tatizo AttributeError kama e:
            self.fail('second argument does sio support set difference: %s' % e)

        ikiwa sio (difference1 ama difference2):
            rudisha

        lines = []
        ikiwa difference1:
            lines.append('Items kwenye the first set but sio the second:')
            kila item kwenye difference1:
                lines.append(repr(item))
        ikiwa difference2:
            lines.append('Items kwenye the second set but sio the first:')
            kila item kwenye difference2:
                lines.append(repr(item))

        standardMsg = '\n'.join(lines)
        self.fail(self._formatMessage(msg, standardMsg))

    eleza assertIn(self, member, container, msg=Tupu):
        """Just like self.assertKweli(a kwenye b), but ukijumuisha a nicer default message."""
        ikiwa member haiko kwenye container:
            standardMsg = '%s sio found kwenye %s' % (safe_repr(member),
                                                  safe_repr(container))
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertNotIn(self, member, container, msg=Tupu):
        """Just like self.assertKweli(a haiko kwenye b), but ukijumuisha a nicer default message."""
        ikiwa member kwenye container:
            standardMsg = '%s unexpectedly found kwenye %s' % (safe_repr(member),
                                                        safe_repr(container))
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertIs(self, expr1, expr2, msg=Tupu):
        """Just like self.assertKweli(a ni b), but ukijumuisha a nicer default message."""
        ikiwa expr1 ni sio expr2:
            standardMsg = '%s ni sio %s' % (safe_repr(expr1),
                                             safe_repr(expr2))
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertIsNot(self, expr1, expr2, msg=Tupu):
        """Just like self.assertKweli(a ni sio b), but ukijumuisha a nicer default message."""
        ikiwa expr1 ni expr2:
            standardMsg = 'unexpectedly identical: %s' % (safe_repr(expr1),)
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertDictEqual(self, d1, d2, msg=Tupu):
        self.assertIsInstance(d1, dict, 'First argument ni sio a dictionary')
        self.assertIsInstance(d2, dict, 'Second argument ni sio a dictionary')

        ikiwa d1 != d2:
            standardMsg = '%s != %s' % _common_shorten_repr(d1, d2)
            diff = ('\n' + '\n'.join(difflib.ndiff(
                           pprint.pformat(d1).splitlines(),
                           pprint.pformat(d2).splitlines())))
            standardMsg = self._truncateMessage(standardMsg, diff)
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertDictContainsSubset(self, subset, dictionary, msg=Tupu):
        """Checks whether dictionary ni a superset of subset."""
        warnings.warn('assertDictContainsSubset ni deprecated',
                      DeprecationWarning)
        missing = []
        mismatched = []
        kila key, value kwenye subset.items():
            ikiwa key haiko kwenye dictionary:
                missing.append(key)
            lasivyo value != dictionary[key]:
                mismatched.append('%s, expected: %s, actual: %s' %
                                  (safe_repr(key), safe_repr(value),
                                   safe_repr(dictionary[key])))

        ikiwa sio (missing ama mismatched):
            rudisha

        standardMsg = ''
        ikiwa missing:
            standardMsg = 'Missing: %s' % ','.join(safe_repr(m) kila m in
                                                    missing)
        ikiwa mismatched:
            ikiwa standardMsg:
                standardMsg += '; '
            standardMsg += 'Mismatched values: %s' % ','.join(mismatched)

        self.fail(self._formatMessage(msg, standardMsg))


    eleza assertCountEqual(self, first, second, msg=Tupu):
        """Asserts that two iterables have the same elements, the same number of
        times, without regard to order.

            self.assertEqual(Counter(list(first)),
                             Counter(list(second)))

         Example:
            - [0, 1, 1] na [1, 0, 1] compare equal.
            - [0, 0, 1] na [0, 1] compare unequal.

        """
        first_seq, second_seq = list(first), list(second)
        jaribu:
            first = collections.Counter(first_seq)
            second = collections.Counter(second_seq)
        tatizo TypeError:
            # Handle case ukijumuisha unhashable elements
            differences = _count_diff_all_purpose(first_seq, second_seq)
        isipokua:
            ikiwa first == second:
                rudisha
            differences = _count_diff_hashable(first_seq, second_seq)

        ikiwa differences:
            standardMsg = 'Element counts were sio equal:\n'
            lines = ['First has %d, Second has %d:  %r' % diff kila diff kwenye differences]
            diffMsg = '\n'.join(lines)
            standardMsg = self._truncateMessage(standardMsg, diffMsg)
            msg = self._formatMessage(msg, standardMsg)
            self.fail(msg)

    eleza assertMultiLineEqual(self, first, second, msg=Tupu):
        """Assert that two multi-line strings are equal."""
        self.assertIsInstance(first, str, 'First argument ni sio a string')
        self.assertIsInstance(second, str, 'Second argument ni sio a string')

        ikiwa first != second:
            # don't use difflib ikiwa the strings are too long
            ikiwa (len(first) > self._diffThreshold ama
                len(second) > self._diffThreshold):
                self._baseAssertEqual(first, second, msg)
            firstlines = first.splitlines(keepends=Kweli)
            secondlines = second.splitlines(keepends=Kweli)
            ikiwa len(firstlines) == 1 na first.strip('\r\n') == first:
                firstlines = [first + '\n']
                secondlines = [second + '\n']
            standardMsg = '%s != %s' % _common_shorten_repr(first, second)
            diff = '\n' + ''.join(difflib.ndiff(firstlines, secondlines))
            standardMsg = self._truncateMessage(standardMsg, diff)
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertLess(self, a, b, msg=Tupu):
        """Just like self.assertKweli(a < b), but ukijumuisha a nicer default message."""
        ikiwa sio a < b:
            standardMsg = '%s sio less than %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertLessEqual(self, a, b, msg=Tupu):
        """Just like self.assertKweli(a <= b), but ukijumuisha a nicer default message."""
        ikiwa sio a <= b:
            standardMsg = '%s sio less than ama equal to %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertGreater(self, a, b, msg=Tupu):
        """Just like self.assertKweli(a > b), but ukijumuisha a nicer default message."""
        ikiwa sio a > b:
            standardMsg = '%s sio greater than %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertGreaterEqual(self, a, b, msg=Tupu):
        """Just like self.assertKweli(a >= b), but ukijumuisha a nicer default message."""
        ikiwa sio a >= b:
            standardMsg = '%s sio greater than ama equal to %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertIsTupu(self, obj, msg=Tupu):
        """Same kama self.assertKweli(obj ni Tupu), ukijumuisha a nicer default message."""
        ikiwa obj ni sio Tupu:
            standardMsg = '%s ni sio Tupu' % (safe_repr(obj),)
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertIsNotTupu(self, obj, msg=Tupu):
        """Included kila symmetry ukijumuisha assertIsTupu."""
        ikiwa obj ni Tupu:
            standardMsg = 'unexpectedly Tupu'
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertIsInstance(self, obj, cls, msg=Tupu):
        """Same kama self.assertKweli(isinstance(obj, cls)), ukijumuisha a nicer
        default message."""
        ikiwa sio isinstance(obj, cls):
            standardMsg = '%s ni sio an instance of %r' % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertNotIsInstance(self, obj, cls, msg=Tupu):
        """Included kila symmetry ukijumuisha assertIsInstance."""
        ikiwa isinstance(obj, cls):
            standardMsg = '%s ni an instance of %r' % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))

    eleza assertRaisesRegex(self, expected_exception, expected_regex,
                          *args, **kwargs):
        """Asserts that the message kwenye a ashiriad exception matches a regex.

        Args:
            expected_exception: Exception kundi expected to be ashiriad.
            expected_regex: Regex (re.Pattern object ama string) expected
                    to be found kwenye error message.
            args: Function to be called na extra positional args.
            kwargs: Extra kwargs.
            msg: Optional message used kwenye case of failure. Can only be used
                    when assertRaisesRegex ni used kama a context manager.
        """
        context = _AssertRaisesContext(expected_exception, self, expected_regex)
        rudisha context.handle('assertRaisesRegex', args, kwargs)

    eleza assertWarnsRegex(self, expected_warning, expected_regex,
                         *args, **kwargs):
        """Asserts that the message kwenye a triggered warning matches a regexp.
        Basic functioning ni similar to assertWarns() ukijumuisha the addition
        that only warnings whose messages also match the regular expression
        are considered successful matches.

        Args:
            expected_warning: Warning kundi expected to be triggered.
            expected_regex: Regex (re.Pattern object ama string) expected
                    to be found kwenye error message.
            args: Function to be called na extra positional args.
            kwargs: Extra kwargs.
            msg: Optional message used kwenye case of failure. Can only be used
                    when assertWarnsRegex ni used kama a context manager.
        """
        context = _AssertWarnsContext(expected_warning, self, expected_regex)
        rudisha context.handle('assertWarnsRegex', args, kwargs)

    eleza assertRegex(self, text, expected_regex, msg=Tupu):
        """Fail the test unless the text matches the regular expression."""
        ikiwa isinstance(expected_regex, (str, bytes)):
            assert expected_regex, "expected_regex must sio be empty."
            expected_regex = re.compile(expected_regex)
        ikiwa sio expected_regex.search(text):
            standardMsg = "Regex didn't match: %r sio found kwenye %r" % (
                expected_regex.pattern, text)
            # _formatMessage ensures the longMessage option ni respected
            msg = self._formatMessage(msg, standardMsg)
            ashiria self.failureException(msg)

    eleza assertNotRegex(self, text, unexpected_regex, msg=Tupu):
        """Fail the test ikiwa the text matches the regular expression."""
        ikiwa isinstance(unexpected_regex, (str, bytes)):
            unexpected_regex = re.compile(unexpected_regex)
        match = unexpected_regex.search(text)
        ikiwa match:
            standardMsg = 'Regex matched: %r matches %r kwenye %r' % (
                text[match.start() : match.end()],
                unexpected_regex.pattern,
                text)
            # _formatMessage ensures the longMessage option ni respected
            msg = self._formatMessage(msg, standardMsg)
            ashiria self.failureException(msg)


    eleza _deprecate(original_func):
        eleza deprecated_func(*args, **kwargs):
            warnings.warn(
                'Please use {0} instead.'.format(original_func.__name__),
                DeprecationWarning, 2)
            rudisha original_func(*args, **kwargs)
        rudisha deprecated_func

    # see #9424
    failUnlessEqual = assertEquals = _deprecate(assertEqual)
    failIfEqual = assertNotEquals = _deprecate(assertNotEqual)
    failUnlessAlmostEqual = assertAlmostEquals = _deprecate(assertAlmostEqual)
    failIfAlmostEqual = assertNotAlmostEquals = _deprecate(assertNotAlmostEqual)
    failUnless = assert_ = _deprecate(assertKweli)
    failUnlessRaises = _deprecate(assertRaises)
    failIf = _deprecate(assertUongo)
    assertRaisesRegexp = _deprecate(assertRaisesRegex)
    assertRegexpMatches = _deprecate(assertRegex)
    assertNotRegexpMatches = _deprecate(assertNotRegex)



kundi FunctionTestCase(TestCase):
    """A test case that wraps a test function.

    This ni useful kila slipping pre-existing test functions into the
    unittest framework. Optionally, set-up na tidy-up functions can be
    supplied. As ukijumuisha TestCase, the tidy-up ('tearDown') function will
    always be called ikiwa the set-up ('setUp') function ran successfully.
    """

    eleza __init__(self, testFunc, setUp=Tupu, tearDown=Tupu, description=Tupu):
        super(FunctionTestCase, self).__init__()
        self._setUpFunc = setUp
        self._tearDownFunc = tearDown
        self._testFunc = testFunc
        self._description = description

    eleza setUp(self):
        ikiwa self._setUpFunc ni sio Tupu:
            self._setUpFunc()

    eleza tearDown(self):
        ikiwa self._tearDownFunc ni sio Tupu:
            self._tearDownFunc()

    eleza runTest(self):
        self._testFunc()

    eleza id(self):
        rudisha self._testFunc.__name__

    eleza __eq__(self, other):
        ikiwa sio isinstance(other, self.__class__):
            rudisha NotImplemented

        rudisha self._setUpFunc == other._setUpFunc na \
               self._tearDownFunc == other._tearDownFunc na \
               self._testFunc == other._testFunc na \
               self._description == other._description

    eleza __hash__(self):
        rudisha hash((type(self), self._setUpFunc, self._tearDownFunc,
                     self._testFunc, self._description))

    eleza __str__(self):
        rudisha "%s (%s)" % (strclass(self.__class__),
                            self._testFunc.__name__)

    eleza __repr__(self):
        rudisha "<%s tec=%s>" % (strclass(self.__class__),
                                     self._testFunc)

    eleza shortDescription(self):
        ikiwa self._description ni sio Tupu:
            rudisha self._description
        doc = self._testFunc.__doc__
        rudisha doc na doc.split("\n")[0].strip() ama Tupu


kundi _SubTest(TestCase):

    eleza __init__(self, test_case, message, params):
        super().__init__()
        self._message = message
        self.test_case = test_case
        self.params = params
        self.failureException = test_case.failureException

    eleza runTest(self):
        ashiria NotImplementedError("subtests cannot be run directly")

    eleza _subDescription(self):
        parts = []
        ikiwa self._message ni sio _subtest_msg_sentinel:
            parts.append("[{}]".format(self._message))
        ikiwa self.params:
            params_desc = ', '.join(
                "{}={!r}".format(k, v)
                kila (k, v) kwenye self.params.items())
            parts.append("({})".format(params_desc))
        rudisha " ".join(parts) ama '(<subtest>)'

    eleza id(self):
        rudisha "{} {}".format(self.test_case.id(), self._subDescription())

    eleza shortDescription(self):
        """Returns a one-line description of the subtest, ama Tupu ikiwa no
        description has been provided.
        """
        rudisha self.test_case.shortDescription()

    eleza __str__(self):
        rudisha "{} {}".format(self.test_case, self._subDescription())
