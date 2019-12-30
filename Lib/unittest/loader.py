"""Loading unittests."""

agiza os
agiza re
agiza sys
agiza traceback
agiza types
agiza functools
agiza warnings

kutoka fnmatch agiza fnmatch, fnmatchcase

kutoka . agiza case, suite, util

__unittest = Kweli

# what about .pyc (etc)
# we would need to avoid loading the same tests multiple times
# kutoka '.py', *and* '.pyc'
VALID_MODULE_NAME = re.compile(r'[_a-z]\w*\.py$', re.IGNORECASE)


kundi _FailedTest(case.TestCase):
    _testMethodName = Tupu

    eleza __init__(self, method_name, exception):
        self._exception = exception
        super(_FailedTest, self).__init__(method_name)

    eleza __getattr__(self, name):
        ikiwa name != self._testMethodName:
            rudisha super(_FailedTest, self).__getattr__(name)
        eleza testFailure():
            ashiria self._exception
        rudisha testFailure


eleza _make_failed_import_test(name, suiteClass):
    message = 'Failed to agiza test module: %s\n%s' % (
        name, traceback.format_exc())
    rudisha _make_failed_test(name, ImportError(message), suiteClass, message)

eleza _make_failed_load_tests(name, exception, suiteClass):
    message = 'Failed to call load_tests:\n%s' % (traceback.format_exc(),)
    rudisha _make_failed_test(
        name, exception, suiteClass, message)

eleza _make_failed_test(methodname, exception, suiteClass, message):
    test = _FailedTest(methodname, exception)
    rudisha suiteClass((test,)), message

eleza _make_skipped_test(methodname, exception, suiteClass):
    @case.skip(str(exception))
    eleza testSkipped(self):
        pita
    attrs = {methodname: testSkipped}
    TestClass = type("ModuleSkipped", (case.TestCase,), attrs)
    rudisha suiteClass((TestClass(methodname),))

eleza _jython_aware_splitext(path):
    ikiwa path.lower().endswith('$py.class'):
        rudisha path[:-9]
    rudisha os.path.splitext(path)[0]


kundi TestLoader(object):
    """
    This kundi ni responsible kila loading tests according to various criteria
    na rudishaing them wrapped kwenye a TestSuite
    """
    testMethodPrefix = 'test'
    sortTestMethodsUsing = staticmethod(util.three_way_cmp)
    testNamePatterns = Tupu
    suiteClass = suite.TestSuite
    _top_level_dir = Tupu

    eleza __init__(self):
        super(TestLoader, self).__init__()
        self.errors = []
        # Tracks packages which we have called into via load_tests, to
        # avoid infinite re-entrancy.
        self._loading_packages = set()

    eleza loadTestsFromTestCase(self, testCaseClass):
        """Return a suite of all test cases contained kwenye testCaseClass"""
        ikiwa issubclass(testCaseClass, suite.TestSuite):
            ashiria TypeError("Test cases should sio be derived kutoka "
                            "TestSuite. Maybe you meant to derive kutoka "
                            "TestCase?")
        testCaseNames = self.getTestCaseNames(testCaseClass)
        ikiwa sio testCaseNames na hasattr(testCaseClass, 'runTest'):
            testCaseNames = ['runTest']
        loaded_suite = self.suiteClass(map(testCaseClass, testCaseNames))
        rudisha loaded_suite

    # XXX After Python 3.5, remove backward compatibility hacks for
    # use_load_tests deprecation via *args na **kws.  See issue 16662.
    eleza loadTestsFromModule(self, module, *args, pattern=Tupu, **kws):
        """Return a suite of all test cases contained kwenye the given module"""
        # This method used to take an undocumented na unofficial
        # use_load_tests argument.  For backward compatibility, we still
        # accept the argument (which can also be the first position) but we
        # ignore it na issue a deprecation warning ikiwa it's present.
        ikiwa len(args) > 0 ama 'use_load_tests' kwenye kws:
            warnings.warn('use_load_tests ni deprecated na ignored',
                          DeprecationWarning)
            kws.pop('use_load_tests', Tupu)
        ikiwa len(args) > 1:
            # Complain about the number of arguments, but don't forget the
            # required `module` argument.
            complaint = len(args) + 1
            ashiria TypeError('loadTestsFromModule() takes 1 positional argument but {} were given'.format(complaint))
        ikiwa len(kws) != 0:
            # Since the keyword arguments are unsorted (see PEP 468), just
            # pick the alphabetically sorted first argument to complain about,
            # ikiwa multiple were given.  At least the error message will be
            # predictable.
            complaint = sorted(kws)[0]
            ashiria TypeError("loadTestsFromModule() got an unexpected keyword argument '{}'".format(complaint))
        tests = []
        kila name kwenye dir(module):
            obj = getattr(module, name)
            ikiwa isinstance(obj, type) na issubclass(obj, case.TestCase):
                tests.append(self.loadTestsFromTestCase(obj))

        load_tests = getattr(module, 'load_tests', Tupu)
        tests = self.suiteClass(tests)
        ikiwa load_tests ni sio Tupu:
            jaribu:
                rudisha load_tests(self, tests, pattern)
            tatizo Exception kama e:
                error_case, error_message = _make_failed_load_tests(
                    module.__name__, e, self.suiteClass)
                self.errors.append(error_message)
                rudisha error_case
        rudisha tests

    eleza loadTestsFromName(self, name, module=Tupu):
        """Return a suite of all test cases given a string specifier.

        The name may resolve either to a module, a test case class, a
        test method within a test case class, ama a callable object which
        rudishas a TestCase ama TestSuite instance.

        The method optionally resolves the names relative to a given module.
        """
        parts = name.split('.')
        error_case, error_message = Tupu, Tupu
        ikiwa module ni Tupu:
            parts_copy = parts[:]
            wakati parts_copy:
                jaribu:
                    module_name = '.'.join(parts_copy)
                    module = __import__(module_name)
                    koma
                tatizo ImportError:
                    next_attribute = parts_copy.pop()
                    # Last error so we can give it to the user ikiwa needed.
                    error_case, error_message = _make_failed_import_test(
                        next_attribute, self.suiteClass)
                    ikiwa sio parts_copy:
                        # Even the top level agiza failed: report that error.
                        self.errors.append(error_message)
                        rudisha error_case
            parts = parts[1:]
        obj = module
        kila part kwenye parts:
            jaribu:
                parent, obj = obj, getattr(obj, part)
            tatizo AttributeError kama e:
                # We can't traverse some part of the name.
                ikiwa (getattr(obj, '__path__', Tupu) ni sio Tupu
                    na error_case ni sio Tupu):
                    # This ni a package (no __path__ per importlib docs), na we
                    # encountered an error agizaing something. We cannot tell
                    # the difference between package.WrongNameTestClass na
                    # package.wrong_module_name so we just report the
                    # ImportError - it ni more informative.
                    self.errors.append(error_message)
                    rudisha error_case
                isipokua:
                    # Otherwise, we signal that an AttributeError has occurred.
                    error_case, error_message = _make_failed_test(
                        part, e, self.suiteClass,
                        'Failed to access attribute:\n%s' % (
                            traceback.format_exc(),))
                    self.errors.append(error_message)
                    rudisha error_case

        ikiwa isinstance(obj, types.ModuleType):
            rudisha self.loadTestsFromModule(obj)
        lasivyo isinstance(obj, type) na issubclass(obj, case.TestCase):
            rudisha self.loadTestsFromTestCase(obj)
        lasivyo (isinstance(obj, types.FunctionType) na
              isinstance(parent, type) na
              issubclass(parent, case.TestCase)):
            name = parts[-1]
            inst = parent(name)
            # static methods follow a different path
            ikiwa sio isinstance(getattr(inst, name), types.FunctionType):
                rudisha self.suiteClass([inst])
        lasivyo isinstance(obj, suite.TestSuite):
            rudisha obj
        ikiwa callable(obj):
            test = obj()
            ikiwa isinstance(test, suite.TestSuite):
                rudisha test
            lasivyo isinstance(test, case.TestCase):
                rudisha self.suiteClass([test])
            isipokua:
                ashiria TypeError("calling %s rudishaed %s, sio a test" %
                                (obj, test))
        isipokua:
            ashiria TypeError("don't know how to make test kutoka: %s" % obj)

    eleza loadTestsFromNames(self, names, module=Tupu):
        """Return a suite of all test cases found using the given sequence
        of string specifiers. See 'loadTestsFromName()'.
        """
        suites = [self.loadTestsFromName(name, module) kila name kwenye names]
        rudisha self.suiteClass(suites)

    eleza getTestCaseNames(self, testCaseClass):
        """Return a sorted sequence of method names found within testCaseClass
        """
        eleza shouldIncludeMethod(attrname):
            ikiwa sio attrname.startswith(self.testMethodPrefix):
                rudisha Uongo
            testFunc = getattr(testCaseClass, attrname)
            ikiwa sio callable(testFunc):
                rudisha Uongo
            fullName = f'%s.%s.%s' % (
                testCaseClass.__module__, testCaseClass.__qualname__, attrname
            )
            rudisha self.testNamePatterns ni Tupu ama \
                any(fnmatchcase(fullName, pattern) kila pattern kwenye self.testNamePatterns)
        testFnNames = list(filter(shouldIncludeMethod, dir(testCaseClass)))
        ikiwa self.sortTestMethodsUsing:
            testFnNames.sort(key=functools.cmp_to_key(self.sortTestMethodsUsing))
        rudisha testFnNames

    eleza discover(self, start_dir, pattern='test*.py', top_level_dir=Tupu):
        """Find na rudisha all test modules kutoka the specified start
        directory, recursing into subdirectories to find them na rudisha all
        tests found within them. Only test files that match the pattern will
        be loaded. (Using shell style pattern matching.)

        All test modules must be agizaable kutoka the top level of the project.
        If the start directory ni sio the top level directory then the top
        level directory must be specified separately.

        If a test package name (directory ukijumuisha '__init__.py') matches the
        pattern then the package will be checked kila a 'load_tests' function. If
        this exists then it will be called ukijumuisha (loader, tests, pattern) unless
        the package has already had load_tests called kutoka the same discovery
        invocation, kwenye which case the package module object ni sio scanned for
        tests - this ensures that when a package uses discover to further
        discover child tests that infinite recursion does sio happen.

        If load_tests exists then discovery does *not* recurse into the package,
        load_tests ni responsible kila loading all tests kwenye the package.

        The pattern ni deliberately sio stored kama a loader attribute so that
        packages can endelea discovery themselves. top_level_dir ni stored so
        load_tests does sio need to pita this argument kwenye to loader.discover().

        Paths are sorted before being imported to ensure reproducible execution
        order even on filesystems ukijumuisha non-alphabetical ordering like ext3/4.
        """
        set_implicit_top = Uongo
        ikiwa top_level_dir ni Tupu na self._top_level_dir ni sio Tupu:
            # make top_level_dir optional ikiwa called kutoka load_tests kwenye a package
            top_level_dir = self._top_level_dir
        lasivyo top_level_dir ni Tupu:
            set_implicit_top = Kweli
            top_level_dir = start_dir

        top_level_dir = os.path.abspath(top_level_dir)

        ikiwa sio top_level_dir kwenye sys.path:
            # all test modules must be agizaable kutoka the top level directory
            # should we *unconditionally* put the start directory kwenye first
            # kwenye sys.path to minimise likelihood of conflicts between installed
            # modules na development versions?
            sys.path.insert(0, top_level_dir)
        self._top_level_dir = top_level_dir

        is_not_agizaable = Uongo
        is_namespace = Uongo
        tests = []
        ikiwa os.path.isdir(os.path.abspath(start_dir)):
            start_dir = os.path.abspath(start_dir)
            ikiwa start_dir != top_level_dir:
                is_not_agizaable = sio os.path.isfile(os.path.join(start_dir, '__init__.py'))
        isipokua:
            # support kila discovery kutoka dotted module names
            jaribu:
                __import__(start_dir)
            tatizo ImportError:
                is_not_agizaable = Kweli
            isipokua:
                the_module = sys.modules[start_dir]
                top_part = start_dir.split('.')[0]
                jaribu:
                    start_dir = os.path.abspath(
                       os.path.dirname((the_module.__file__)))
                tatizo AttributeError:
                    # look kila namespace packages
                    jaribu:
                        spec = the_module.__spec__
                    tatizo AttributeError:
                        spec = Tupu

                    ikiwa spec na spec.loader ni Tupu:
                        ikiwa spec.submodule_search_locations ni sio Tupu:
                            is_namespace = Kweli

                            kila path kwenye the_module.__path__:
                                ikiwa (sio set_implicit_top na
                                    sio path.startswith(top_level_dir)):
                                    endelea
                                self._top_level_dir = \
                                    (path.split(the_module.__name__
                                         .replace(".", os.path.sep))[0])
                                tests.extend(self._find_tests(path,
                                                              pattern,
                                                              namespace=Kweli))
                    lasivyo the_module.__name__ kwenye sys.builtin_module_names:
                        # builtin module
                        ashiria TypeError('Can sio use builtin modules '
                                        'as dotted module names') kutoka Tupu
                    isipokua:
                        ashiria TypeError(
                            'don\'t know how to discover kutoka {!r}'
                            .format(the_module)) kutoka Tupu

                ikiwa set_implicit_top:
                    ikiwa sio is_namespace:
                        self._top_level_dir = \
                           self._get_directory_containing_module(top_part)
                        sys.path.remove(top_level_dir)
                    isipokua:
                        sys.path.remove(top_level_dir)

        ikiwa is_not_agizaable:
            ashiria ImportError('Start directory ni sio agizaable: %r' % start_dir)

        ikiwa sio is_namespace:
            tests = list(self._find_tests(start_dir, pattern))
        rudisha self.suiteClass(tests)

    eleza _get_directory_containing_module(self, module_name):
        module = sys.modules[module_name]
        full_path = os.path.abspath(module.__file__)

        ikiwa os.path.basename(full_path).lower().startswith('__init__.py'):
            rudisha os.path.dirname(os.path.dirname(full_path))
        isipokua:
            # here we have been given a module rather than a package - so
            # all we can do ni search the *same* directory the module ni in
            # should an exception be ashiriad instead
            rudisha os.path.dirname(full_path)

    eleza _get_name_from_path(self, path):
        ikiwa path == self._top_level_dir:
            rudisha '.'
        path = _jython_aware_splitext(os.path.normpath(path))

        _relpath = os.path.relpath(path, self._top_level_dir)
        assert sio os.path.isabs(_relpath), "Path must be within the project"
        assert sio _relpath.startswith('..'), "Path must be within the project"

        name = _relpath.replace(os.path.sep, '.')
        rudisha name

    eleza _get_module_from_name(self, name):
        __import__(name)
        rudisha sys.modules[name]

    eleza _match_path(self, path, full_path, pattern):
        # override this method to use alternative matching strategy
        rudisha fnmatch(path, pattern)

    eleza _find_tests(self, start_dir, pattern, namespace=Uongo):
        """Used by discovery. Yields test suites it loads."""
        # Handle the __init__ kwenye this package
        name = self._get_name_from_path(start_dir)
        # name ni '.' when start_dir == top_level_dir (and top_level_dir ni by
        # definition sio a package).
        ikiwa name != '.' na name haiko kwenye self._loading_packages:
            # name ni kwenye self._loading_packages wakati we have called into
            # loadTestsFromModule ukijumuisha name.
            tests, should_recurse = self._find_test_path(
                start_dir, pattern, namespace)
            ikiwa tests ni sio Tupu:
                tuma tests
            ikiwa sio should_recurse:
                # Either an error occurred, ama load_tests was used by the
                # package.
                rudisha
        # Handle the contents.
        paths = sorted(os.listdir(start_dir))
        kila path kwenye paths:
            full_path = os.path.join(start_dir, path)
            tests, should_recurse = self._find_test_path(
                full_path, pattern, namespace)
            ikiwa tests ni sio Tupu:
                tuma tests
            ikiwa should_recurse:
                # we found a package that didn't use load_tests.
                name = self._get_name_from_path(full_path)
                self._loading_packages.add(name)
                jaribu:
                    tuma kutoka self._find_tests(full_path, pattern, namespace)
                mwishowe:
                    self._loading_packages.discard(name)

    eleza _find_test_path(self, full_path, pattern, namespace=Uongo):
        """Used by discovery.

        Loads tests kutoka a single file, ama a directories' __init__.py when
        pitaed the directory.

        Returns a tuple (Tupu_or_tests_from_file, should_recurse).
        """
        basename = os.path.basename(full_path)
        ikiwa os.path.isfile(full_path):
            ikiwa sio VALID_MODULE_NAME.match(basename):
                # valid Python identifiers only
                rudisha Tupu, Uongo
            ikiwa sio self._match_path(basename, full_path, pattern):
                rudisha Tupu, Uongo
            # ikiwa the test file matches, load it
            name = self._get_name_from_path(full_path)
            jaribu:
                module = self._get_module_from_name(name)
            tatizo case.SkipTest kama e:
                rudisha _make_skipped_test(name, e, self.suiteClass), Uongo
            tatizo:
                error_case, error_message = \
                    _make_failed_import_test(name, self.suiteClass)
                self.errors.append(error_message)
                rudisha error_case, Uongo
            isipokua:
                mod_file = os.path.abspath(
                    getattr(module, '__file__', full_path))
                realpath = _jython_aware_splitext(
                    os.path.realpath(mod_file))
                fullpath_noext = _jython_aware_splitext(
                    os.path.realpath(full_path))
                ikiwa realpath.lower() != fullpath_noext.lower():
                    module_dir = os.path.dirname(realpath)
                    mod_name = _jython_aware_splitext(
                        os.path.basename(full_path))
                    expected_dir = os.path.dirname(full_path)
                    msg = ("%r module incorrectly imported kutoka %r. Expected "
                           "%r. Is this module globally installed?")
                    ashiria ImportError(
                        msg % (mod_name, module_dir, expected_dir))
                rudisha self.loadTestsFromModule(module, pattern=pattern), Uongo
        lasivyo os.path.isdir(full_path):
            ikiwa (sio namespace na
                sio os.path.isfile(os.path.join(full_path, '__init__.py'))):
                rudisha Tupu, Uongo

            load_tests = Tupu
            tests = Tupu
            name = self._get_name_from_path(full_path)
            jaribu:
                package = self._get_module_from_name(name)
            tatizo case.SkipTest kama e:
                rudisha _make_skipped_test(name, e, self.suiteClass), Uongo
            tatizo:
                error_case, error_message = \
                    _make_failed_import_test(name, self.suiteClass)
                self.errors.append(error_message)
                rudisha error_case, Uongo
            isipokua:
                load_tests = getattr(package, 'load_tests', Tupu)
                # Mark this package kama being kwenye load_tests (possibly ;))
                self._loading_packages.add(name)
                jaribu:
                    tests = self.loadTestsFromModule(package, pattern=pattern)
                    ikiwa load_tests ni sio Tupu:
                        # loadTestsFromModule(package) has loaded tests kila us.
                        rudisha tests, Uongo
                    rudisha tests, Kweli
                mwishowe:
                    self._loading_packages.discard(name)
        isipokua:
            rudisha Tupu, Uongo


defaultTestLoader = TestLoader()


eleza _makeLoader(prefix, sortUsing, suiteClass=Tupu, testNamePatterns=Tupu):
    loader = TestLoader()
    loader.sortTestMethodsUsing = sortUsing
    loader.testMethodPrefix = prefix
    loader.testNamePatterns = testNamePatterns
    ikiwa suiteClass:
        loader.suiteClass = suiteClass
    rudisha loader

eleza getTestCaseNames(testCaseClass, prefix, sortUsing=util.three_way_cmp, testNamePatterns=Tupu):
    rudisha _makeLoader(prefix, sortUsing, testNamePatterns=testNamePatterns).getTestCaseNames(testCaseClass)

eleza makeSuite(testCaseClass, prefix='test', sortUsing=util.three_way_cmp,
              suiteClass=suite.TestSuite):
    rudisha _makeLoader(prefix, sortUsing, suiteClass).loadTestsFromTestCase(
        testCaseClass)

eleza findTestCases(module, prefix='test', sortUsing=util.three_way_cmp,
                  suiteClass=suite.TestSuite):
    rudisha _makeLoader(prefix, sortUsing, suiteClass).loadTestsFromModule(\
        module)
