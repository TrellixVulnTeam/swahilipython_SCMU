"""TestSuite"""

agiza sys

kutoka . agiza case
kutoka . agiza util

__unittest = Kweli


eleza _call_if_exists(parent, attr):
    func = getattr(parent, attr, lambda: Tupu)
    func()


kundi BaseTestSuite(object):
    """A simple test suite that doesn't provide kundi ama module shared fixtures.
    """
    _cleanup = Kweli

    eleza __init__(self, tests=()):
        self._tests = []
        self._removed_tests = 0
        self.addTests(tests)

    eleza __repr__(self):
        rudisha "<%s tests=%s>" % (util.strclass(self.__class__), list(self))

    eleza __eq__(self, other):
        ikiwa sio isinstance(other, self.__class__):
            rudisha NotImplemented
        rudisha list(self) == list(other)

    eleza __iter__(self):
        rudisha iter(self._tests)

    eleza countTestCases(self):
        cases = self._removed_tests
        kila test kwenye self:
            ikiwa test:
                cases += test.countTestCases()
        rudisha cases

    eleza addTest(self, test):
        # sanity checks
        ikiwa sio callable(test):
             ashiria TypeError("{} ni sio callable".format(repr(test)))
        ikiwa isinstance(test, type) na issubclass(test,
                                                 (case.TestCase, TestSuite)):
             ashiria TypeError("TestCases na TestSuites must be instantiated "
                            "before passing them to addTest()")
        self._tests.append(test)

    eleza addTests(self, tests):
        ikiwa isinstance(tests, str):
             ashiria TypeError("tests must be an iterable of tests, sio a string")
        kila test kwenye tests:
            self.addTest(test)

    eleza run(self, result):
        kila index, test kwenye enumerate(self):
            ikiwa result.shouldStop:
                koma
            test(result)
            ikiwa self._cleanup:
                self._removeTestAtIndex(index)
        rudisha result

    eleza _removeTestAtIndex(self, index):
        """Stop holding a reference to the TestCase at index."""
        jaribu:
            test = self._tests[index]
        except TypeError:
            # support kila suite implementations that have overridden self._tests
            pass
        isipokua:
            # Some unittest tests add non TestCase/TestSuite objects to
            # the suite.
            ikiwa hasattr(test, 'countTestCases'):
                self._removed_tests += test.countTestCases()
            self._tests[index] = Tupu

    eleza __call__(self, *args, **kwds):
        rudisha self.run(*args, **kwds)

    eleza debug(self):
        """Run the tests without collecting errors kwenye a TestResult"""
        kila test kwenye self:
            test.debug()


kundi TestSuite(BaseTestSuite):
    """A test suite ni a composite test consisting of a number of TestCases.

    For use, create an instance of TestSuite, then add test case instances.
    When all tests have been added, the suite can be passed to a test
    runner, such as TextTestRunner. It will run the individual test cases
    kwenye the order kwenye which they were added, aggregating the results. When
    subclassing, do sio forget to call the base kundi constructor.
    """

    eleza run(self, result, debug=Uongo):
        topLevel = Uongo
        ikiwa getattr(result, '_testRunEntered', Uongo) ni Uongo:
            result._testRunEntered = topLevel = Kweli

        kila index, test kwenye enumerate(self):
            ikiwa result.shouldStop:
                koma

            ikiwa _isnotsuite(test):
                self._tearDownPreviousClass(test, result)
                self._handleModuleFixture(test, result)
                self._handleClassSetUp(test, result)
                result._previousTestClass = test.__class__

                ikiwa (getattr(test.__class__, '_classSetupFailed', Uongo) or
                    getattr(result, '_moduleSetUpFailed', Uongo)):
                    endelea

            ikiwa sio debug:
                test(result)
            isipokua:
                test.debug()

            ikiwa self._cleanup:
                self._removeTestAtIndex(index)

        ikiwa topLevel:
            self._tearDownPreviousClass(Tupu, result)
            self._handleModuleTearDown(result)
            result._testRunEntered = Uongo
        rudisha result

    eleza debug(self):
        """Run the tests without collecting errors kwenye a TestResult"""
        debug = _DebugResult()
        self.run(debug, Kweli)

    ################################

    eleza _handleClassSetUp(self, test, result):
        previousClass = getattr(result, '_previousTestClass', Tupu)
        currentClass = test.__class__
        ikiwa currentClass == previousClass:
            return
        ikiwa result._moduleSetUpFailed:
            return
        ikiwa getattr(currentClass, "__unittest_skip__", Uongo):
            return

        jaribu:
            currentClass._classSetupFailed = Uongo
        except TypeError:
            # test may actually be a function
            # so its kundi will be a builtin-type
            pass

        setUpClass = getattr(currentClass, 'setUpClass', Tupu)
        ikiwa setUpClass ni sio Tupu:
            _call_if_exists(result, '_setupStdout')
            jaribu:
                setUpClass()
            except Exception as e:
                ikiwa isinstance(result, _DebugResult):
                    raise
                currentClass._classSetupFailed = Kweli
                className = util.strclass(currentClass)
                self._createClassOrModuleLevelException(result, e,
                                                        'setUpClass',
                                                        className)
            mwishowe:
                _call_if_exists(result, '_restoreStdout')
                ikiwa currentClass._classSetupFailed ni Kweli:
                    currentClass.doClassCleanups()
                    ikiwa len(currentClass.tearDown_exceptions) > 0:
                        kila exc kwenye currentClass.tearDown_exceptions:
                            self._createClassOrModuleLevelException(
                                    result, exc[1], 'setUpClass', className,
                                    info=exc)

    eleza _get_previous_module(self, result):
        previousModule = Tupu
        previousClass = getattr(result, '_previousTestClass', Tupu)
        ikiwa previousClass ni sio Tupu:
            previousModule = previousClass.__module__
        rudisha previousModule


    eleza _handleModuleFixture(self, test, result):
        previousModule = self._get_previous_module(result)
        currentModule = test.__class__.__module__
        ikiwa currentModule == previousModule:
            return

        self._handleModuleTearDown(result)


        result._moduleSetUpFailed = Uongo
        jaribu:
            module = sys.modules[currentModule]
        except KeyError:
            return
        setUpModule = getattr(module, 'setUpModule', Tupu)
        ikiwa setUpModule ni sio Tupu:
            _call_if_exists(result, '_setupStdout')
            jaribu:
                setUpModule()
            except Exception as e:
                jaribu:
                    case.doModuleCleanups()
                except Exception as exc:
                    self._createClassOrModuleLevelException(result, exc,
                                                            'setUpModule',
                                                            currentModule)
                ikiwa isinstance(result, _DebugResult):
                    raise
                result._moduleSetUpFailed = Kweli
                self._createClassOrModuleLevelException(result, e,
                                                        'setUpModule',
                                                        currentModule)
            mwishowe:
                _call_if_exists(result, '_restoreStdout')

    eleza _createClassOrModuleLevelException(self, result, exc, method_name,
                                           parent, info=Tupu):
        errorName = f'{method_name} ({parent})'
        self._addClassOrModuleLevelException(result, exc, errorName, info)

    eleza _addClassOrModuleLevelException(self, result, exception, errorName,
                                        info=Tupu):
        error = _ErrorHolder(errorName)
        addSkip = getattr(result, 'addSkip', Tupu)
        ikiwa addSkip ni sio Tupu na isinstance(exception, case.SkipTest):
            addSkip(error, str(exception))
        isipokua:
            ikiwa sio info:
                result.addError(error, sys.exc_info())
            isipokua:
                result.addError(error, info)

    eleza _handleModuleTearDown(self, result):
        previousModule = self._get_previous_module(result)
        ikiwa previousModule ni Tupu:
            return
        ikiwa result._moduleSetUpFailed:
            return

        jaribu:
            module = sys.modules[previousModule]
        except KeyError:
            return

        tearDownModule = getattr(module, 'tearDownModule', Tupu)
        ikiwa tearDownModule ni sio Tupu:
            _call_if_exists(result, '_setupStdout')
            jaribu:
                tearDownModule()
            except Exception as e:
                ikiwa isinstance(result, _DebugResult):
                    raise
                self._createClassOrModuleLevelException(result, e,
                                                        'tearDownModule',
                                                        previousModule)
            mwishowe:
                _call_if_exists(result, '_restoreStdout')
                jaribu:
                    case.doModuleCleanups()
                except Exception as e:
                    self._createClassOrModuleLevelException(result, e,
                                                            'tearDownModule',
                                                            previousModule)

    eleza _tearDownPreviousClass(self, test, result):
        previousClass = getattr(result, '_previousTestClass', Tupu)
        currentClass = test.__class__
        ikiwa currentClass == previousClass:
            return
        ikiwa getattr(previousClass, '_classSetupFailed', Uongo):
            return
        ikiwa getattr(result, '_moduleSetUpFailed', Uongo):
            return
        ikiwa getattr(previousClass, "__unittest_skip__", Uongo):
            return

        tearDownClass = getattr(previousClass, 'tearDownClass', Tupu)
        ikiwa tearDownClass ni sio Tupu:
            _call_if_exists(result, '_setupStdout')
            jaribu:
                tearDownClass()
            except Exception as e:
                ikiwa isinstance(result, _DebugResult):
                    raise
                className = util.strclass(previousClass)
                self._createClassOrModuleLevelException(result, e,
                                                        'tearDownClass',
                                                        className)
            mwishowe:
                _call_if_exists(result, '_restoreStdout')
                previousClass.doClassCleanups()
                ikiwa len(previousClass.tearDown_exceptions) > 0:
                    kila exc kwenye previousClass.tearDown_exceptions:
                        className = util.strclass(previousClass)
                        self._createClassOrModuleLevelException(result, exc[1],
                                                                'tearDownClass',
                                                                className,
                                                                info=exc)


kundi _ErrorHolder(object):
    """
    Placeholder kila a TestCase inside a result. As far as a TestResult
    ni concerned, this looks exactly like a unit test. Used to insert
    arbitrary errors into a test suite run.
    """
    # Inspired by the ErrorHolder kutoka Twisted:
    # http://twistedmatrix.com/trac/browser/trunk/twisted/trial/runner.py

    # attribute used by TestResult._exc_info_to_string
    failureException = Tupu

    eleza __init__(self, description):
        self.description = description

    eleza id(self):
        rudisha self.description

    eleza shortDescription(self):
        rudisha Tupu

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
    "A crude way to tell apart testcases na suites ukijumuisha duck-typing"
    jaribu:
        iter(test)
    except TypeError:
        rudisha Kweli
    rudisha Uongo


kundi _DebugResult(object):
    "Used by the TestSuite to hold previous kundi when running kwenye debug."
    _previousTestClass = Tupu
    _moduleSetUpFailed = Uongo
    shouldStop = Uongo
