"""TestSuite"""

agiza sys

kutoka . agiza case
kutoka . agiza util

__unittest = True


eleza _call_if_exists(parent, attr):
    func = getattr(parent, attr, lambda: None)
    func()


kundi BaseTestSuite(object):
    """A simple test suite that doesn't provide kundi or module shared fixtures.
    """
    _cleanup = True

    eleza __init__(self, tests=()):
        self._tests = []
        self._removed_tests = 0
        self.addTests(tests)

    eleza __repr__(self):
        rudisha "<%s tests=%s>" % (util.strclass(self.__class__), list(self))

    eleza __eq__(self, other):
        ikiwa not isinstance(other, self.__class__):
            rudisha NotImplemented
        rudisha list(self) == list(other)

    eleza __iter__(self):
        rudisha iter(self._tests)

    eleza countTestCases(self):
        cases = self._removed_tests
        for test in self:
            ikiwa test:
                cases += test.countTestCases()
        rudisha cases

    eleza addTest(self, test):
        # sanity checks
        ikiwa not callable(test):
            raise TypeError("{} is not callable".format(repr(test)))
        ikiwa isinstance(test, type) and issubclass(test,
                                                 (case.TestCase, TestSuite)):
            raise TypeError("TestCases and TestSuites must be instantiated "
                            "before passing them to addTest()")
        self._tests.append(test)

    eleza addTests(self, tests):
        ikiwa isinstance(tests, str):
            raise TypeError("tests must be an iterable of tests, not a string")
        for test in tests:
            self.addTest(test)

    eleza run(self, result):
        for index, test in enumerate(self):
            ikiwa result.shouldStop:
                break
            test(result)
            ikiwa self._cleanup:
                self._removeTestAtIndex(index)
        rudisha result

    eleza _removeTestAtIndex(self, index):
        """Stop holding a reference to the TestCase at index."""
        try:
            test = self._tests[index]
        except TypeError:
            # support for suite implementations that have overridden self._tests
            pass
        else:
            # Some unittest tests add non TestCase/TestSuite objects to
            # the suite.
            ikiwa hasattr(test, 'countTestCases'):
                self._removed_tests += test.countTestCases()
            self._tests[index] = None

    eleza __call__(self, *args, **kwds):
        rudisha self.run(*args, **kwds)

    eleza debug(self):
        """Run the tests without collecting errors in a TestResult"""
        for test in self:
            test.debug()


kundi TestSuite(BaseTestSuite):
    """A test suite is a composite test consisting of a number of TestCases.

    For use, create an instance of TestSuite, then add test case instances.
    When all tests have been added, the suite can be passed to a test
    runner, such as TextTestRunner. It will run the individual test cases
    in the order in which they were added, aggregating the results. When
    subclassing, do not forget to call the base kundi constructor.
    """

    eleza run(self, result, debug=False):
        topLevel = False
        ikiwa getattr(result, '_testRunEntered', False) is False:
            result._testRunEntered = topLevel = True

        for index, test in enumerate(self):
            ikiwa result.shouldStop:
                break

            ikiwa _isnotsuite(test):
                self._tearDownPreviousClass(test, result)
                self._handleModuleFixture(test, result)
                self._handleClassSetUp(test, result)
                result._previousTestClass = test.__class__

                ikiwa (getattr(test.__class__, '_classSetupFailed', False) or
                    getattr(result, '_moduleSetUpFailed', False)):
                    continue

            ikiwa not debug:
                test(result)
            else:
                test.debug()

            ikiwa self._cleanup:
                self._removeTestAtIndex(index)

        ikiwa topLevel:
            self._tearDownPreviousClass(None, result)
            self._handleModuleTearDown(result)
            result._testRunEntered = False
        rudisha result

    eleza debug(self):
        """Run the tests without collecting errors in a TestResult"""
        debug = _DebugResult()
        self.run(debug, True)

    ################################

    eleza _handleClassSetUp(self, test, result):
        previousClass = getattr(result, '_previousTestClass', None)
        currentClass = test.__class__
        ikiwa currentClass == previousClass:
            return
        ikiwa result._moduleSetUpFailed:
            return
        ikiwa getattr(currentClass, "__unittest_skip__", False):
            return

        try:
            currentClass._classSetupFailed = False
        except TypeError:
            # test may actually be a function
            # so its kundi will be a builtin-type
            pass

        setUpClass = getattr(currentClass, 'setUpClass', None)
        ikiwa setUpClass is not None:
            _call_if_exists(result, '_setupStdout')
            try:
                setUpClass()
            except Exception as e:
                ikiwa isinstance(result, _DebugResult):
                    raise
                currentClass._classSetupFailed = True
                className = util.strclass(currentClass)
                self._createClassOrModuleLevelException(result, e,
                                                        'setUpClass',
                                                        className)
            finally:
                _call_if_exists(result, '_restoreStdout')
                ikiwa currentClass._classSetupFailed is True:
                    currentClass.doClassCleanups()
                    ikiwa len(currentClass.tearDown_exceptions) > 0:
                        for exc in currentClass.tearDown_exceptions:
                            self._createClassOrModuleLevelException(
                                    result, exc[1], 'setUpClass', className,
                                    info=exc)

    eleza _get_previous_module(self, result):
        previousModule = None
        previousClass = getattr(result, '_previousTestClass', None)
        ikiwa previousClass is not None:
            previousModule = previousClass.__module__
        rudisha previousModule


    eleza _handleModuleFixture(self, test, result):
        previousModule = self._get_previous_module(result)
        currentModule = test.__class__.__module__
        ikiwa currentModule == previousModule:
            return

        self._handleModuleTearDown(result)


        result._moduleSetUpFailed = False
        try:
            module = sys.modules[currentModule]
        except KeyError:
            return
        setUpModule = getattr(module, 'setUpModule', None)
        ikiwa setUpModule is not None:
            _call_if_exists(result, '_setupStdout')
            try:
                setUpModule()
            except Exception as e:
                try:
                    case.doModuleCleanups()
                except Exception as exc:
                    self._createClassOrModuleLevelException(result, exc,
                                                            'setUpModule',
                                                            currentModule)
                ikiwa isinstance(result, _DebugResult):
                    raise
                result._moduleSetUpFailed = True
                self._createClassOrModuleLevelException(result, e,
                                                        'setUpModule',
                                                        currentModule)
            finally:
                _call_if_exists(result, '_restoreStdout')

    eleza _createClassOrModuleLevelException(self, result, exc, method_name,
                                           parent, info=None):
        errorName = f'{method_name} ({parent})'
        self._addClassOrModuleLevelException(result, exc, errorName, info)

    eleza _addClassOrModuleLevelException(self, result, exception, errorName,
                                        info=None):
        error = _ErrorHolder(errorName)
        addSkip = getattr(result, 'addSkip', None)
        ikiwa addSkip is not None and isinstance(exception, case.SkipTest):
            addSkip(error, str(exception))
        else:
            ikiwa not info:
                result.addError(error, sys.exc_info())
            else:
                result.addError(error, info)

    eleza _handleModuleTearDown(self, result):
        previousModule = self._get_previous_module(result)
        ikiwa previousModule is None:
            return
        ikiwa result._moduleSetUpFailed:
            return

        try:
            module = sys.modules[previousModule]
        except KeyError:
            return

        tearDownModule = getattr(module, 'tearDownModule', None)
        ikiwa tearDownModule is not None:
            _call_if_exists(result, '_setupStdout')
            try:
                tearDownModule()
            except Exception as e:
                ikiwa isinstance(result, _DebugResult):
                    raise
                self._createClassOrModuleLevelException(result, e,
                                                        'tearDownModule',
                                                        previousModule)
            finally:
                _call_if_exists(result, '_restoreStdout')
                try:
                    case.doModuleCleanups()
                except Exception as e:
                    self._createClassOrModuleLevelException(result, e,
                                                            'tearDownModule',
                                                            previousModule)

    eleza _tearDownPreviousClass(self, test, result):
        previousClass = getattr(result, '_previousTestClass', None)
        currentClass = test.__class__
        ikiwa currentClass == previousClass:
            return
        ikiwa getattr(previousClass, '_classSetupFailed', False):
            return
        ikiwa getattr(result, '_moduleSetUpFailed', False):
            return
        ikiwa getattr(previousClass, "__unittest_skip__", False):
            return

        tearDownClass = getattr(previousClass, 'tearDownClass', None)
        ikiwa tearDownClass is not None:
            _call_if_exists(result, '_setupStdout')
            try:
                tearDownClass()
            except Exception as e:
                ikiwa isinstance(result, _DebugResult):
                    raise
                className = util.strclass(previousClass)
                self._createClassOrModuleLevelException(result, e,
                                                        'tearDownClass',
                                                        className)
            finally:
                _call_if_exists(result, '_restoreStdout')
                previousClass.doClassCleanups()
                ikiwa len(previousClass.tearDown_exceptions) > 0:
                    for exc in previousClass.tearDown_exceptions:
                        className = util.strclass(previousClass)
                        self._createClassOrModuleLevelException(result, exc[1],
                                                                'tearDownClass',
                                                                className,
                                                                info=exc)


kundi _ErrorHolder(object):
    """
    Placeholder for a TestCase inside a result. As far as a TestResult
    is concerned, this looks exactly like a unit test. Used to insert
    arbitrary errors into a test suite run.
    """
    # Inspired by the ErrorHolder kutoka Twisted:
    # http://twistedmatrix.com/trac/browser/trunk/twisted/trial/runner.py

    # attribute used by TestResult._exc_info_to_string
    failureException = None

    eleza __init__(self, description):
        self.description = description

    eleza id(self):
        rudisha self.description

    eleza shortDescription(self):
        rudisha None

    eleza __repr__(self):
        rudisha "<ErrorHolder description=%r>" % (self.description,)

    eleza __str__(self):
        rudisha self.id()

    eleza run(self, result):
        # could call result.addError(...) - but this test-like object
        # shouldn't be run anyway
        pass

    eleza __call__(self, result):
        rudisha self.run(result)

    eleza countTestCases(self):
        rudisha 0

eleza _isnotsuite(test):
    "A crude way to tell apart testcases and suites with duck-typing"
    try:
        iter(test)
    except TypeError:
        rudisha True
    rudisha False


kundi _DebugResult(object):
    "Used by the TestSuite to hold previous kundi when running in debug."
    _previousTestClass = None
    _moduleSetUpFailed = False
    shouldStop = False
