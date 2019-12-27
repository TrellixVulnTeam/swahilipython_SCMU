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

__unittest = True

# what about .pyc (etc)
# we would need to avoid loading the same tests multiple times
# kutoka '.py', *and* '.pyc'
VALID_MODULE_NAME = re.compile(r'[_a-z]\w*\.py$', re.IGNORECASE)


kundi _FailedTest(case.TestCase):
    _testMethodName = None

    eleza __init__(self, method_name, exception):
        self._exception = exception
        super(_FailedTest, self).__init__(method_name)

    eleza __getattr__(self, name):
        ikiwa name != self._testMethodName:
            rudisha super(_FailedTest, self).__getattr__(name)
        eleza testFailure():
            raise self._exception
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
        pass
    attrs = {methodname: testSkipped}
    TestClass = type("ModuleSkipped", (case.TestCase,), attrs)
    rudisha suiteClass((TestClass(methodname),))

eleza _jython_aware_splitext(path):
    ikiwa path.lower().endswith('$py.class'):
        rudisha path[:-9]
    rudisha os.path.splitext(path)[0]


kundi TestLoader(object):
    """
    This kundi is responsible for loading tests according to various criteria
    and returning them wrapped in a TestSuite
    """
    testMethodPrefix = 'test'
    sortTestMethodsUsing = staticmethod(util.three_way_cmp)
    testNamePatterns = None
    suiteClass = suite.TestSuite
    _top_level_dir = None

    eleza __init__(self):
        super(TestLoader, self).__init__()
        self.errors = []
        # Tracks packages which we have called into via load_tests, to
        # avoid infinite re-entrancy.
        self._loading_packages = set()

    eleza loadTestsFromTestCase(self, testCaseClass):
        """Return a suite of all test cases contained in testCaseClass"""
        ikiwa issubclass(testCaseClass, suite.TestSuite):
            raise TypeError("Test cases should not be derived kutoka "
                            "TestSuite. Maybe you meant to derive kutoka "
                            "TestCase?")
        testCaseNames = self.getTestCaseNames(testCaseClass)
        ikiwa not testCaseNames and hasattr(testCaseClass, 'runTest'):
            testCaseNames = ['runTest']
        loaded_suite = self.suiteClass(map(testCaseClass, testCaseNames))
        rudisha loaded_suite

    # XXX After Python 3.5, remove backward compatibility hacks for
    # use_load_tests deprecation via *args and **kws.  See issue 16662.
    eleza loadTestsFromModule(self, module, *args, pattern=None, **kws):
        """Return a suite of all test cases contained in the given module"""
        # This method used to take an undocumented and unofficial
        # use_load_tests argument.  For backward compatibility, we still
        # accept the argument (which can also be the first position) but we
        # ignore it and issue a deprecation warning ikiwa it's present.
        ikiwa len(args) > 0 or 'use_load_tests' in kws:
            warnings.warn('use_load_tests is deprecated and ignored',
                          DeprecationWarning)
            kws.pop('use_load_tests', None)
        ikiwa len(args) > 1:
            # Complain about the number of arguments, but don't forget the
            # required `module` argument.
            complaint = len(args) + 1
            raise TypeError('loadTestsFromModule() takes 1 positional argument but {} were given'.format(complaint))
        ikiwa len(kws) != 0:
            # Since the keyword arguments are unsorted (see PEP 468), just
            # pick the alphabetically sorted first argument to complain about,
            # ikiwa multiple were given.  At least the error message will be
            # predictable.
            complaint = sorted(kws)[0]
            raise TypeError("loadTestsFromModule() got an unexpected keyword argument '{}'".format(complaint))
        tests = []
        for name in dir(module):
            obj = getattr(module, name)
            ikiwa isinstance(obj, type) and issubclass(obj, case.TestCase):
                tests.append(self.loadTestsFromTestCase(obj))

        load_tests = getattr(module, 'load_tests', None)
        tests = self.suiteClass(tests)
        ikiwa load_tests is not None:
            try:
                rudisha load_tests(self, tests, pattern)
            except Exception as e:
                error_case, error_message = _make_failed_load_tests(
                    module.__name__, e, self.suiteClass)
                self.errors.append(error_message)
                rudisha error_case
        rudisha tests

    eleza loadTestsFromName(self, name, module=None):
        """Return a suite of all test cases given a string specifier.

        The name may resolve either to a module, a test case class, a
        test method within a test case class, or a callable object which
        returns a TestCase or TestSuite instance.

        The method optionally resolves the names relative to a given module.
        """
        parts = name.split('.')
        error_case, error_message = None, None
        ikiwa module is None:
            parts_copy = parts[:]
            while parts_copy:
                try:
                    module_name = '.'.join(parts_copy)
                    module = __import__(module_name)
                    break
                except ImportError:
                    next_attribute = parts_copy.pop()
                    # Last error so we can give it to the user ikiwa needed.
                    error_case, error_message = _make_failed_import_test(
                        next_attribute, self.suiteClass)
                    ikiwa not parts_copy:
                        # Even the top level agiza failed: report that error.
                        self.errors.append(error_message)
                        rudisha error_case
            parts = parts[1:]
        obj = module
        for part in parts:
            try:
                parent, obj = obj, getattr(obj, part)
            except AttributeError as e:
                # We can't traverse some part of the name.
                ikiwa (getattr(obj, '__path__', None) is not None
                    and error_case is not None):
                    # This is a package (no __path__ per importlib docs), and we
                    # encountered an error agizaing something. We cannot tell
                    # the difference between package.WrongNameTestClass and
                    # package.wrong_module_name so we just report the
                    # ImportError - it is more informative.
                    self.errors.append(error_message)
                    rudisha error_case
                else:
                    # Otherwise, we signal that an AttributeError has occurred.
                    error_case, error_message = _make_failed_test(
                        part, e, self.suiteClass,
                        'Failed to access attribute:\n%s' % (
                            traceback.format_exc(),))
                    self.errors.append(error_message)
                    rudisha error_case

        ikiwa isinstance(obj, types.ModuleType):
            rudisha self.loadTestsFromModule(obj)
        elikiwa isinstance(obj, type) and issubclass(obj, case.TestCase):
            rudisha self.loadTestsFromTestCase(obj)
        elikiwa (isinstance(obj, types.FunctionType) and
              isinstance(parent, type) and
              issubclass(parent, case.TestCase)):
            name = parts[-1]
            inst = parent(name)
            # static methods follow a different path
            ikiwa not isinstance(getattr(inst, name), types.FunctionType):
                rudisha self.suiteClass([inst])
        elikiwa isinstance(obj, suite.TestSuite):
            rudisha obj
        ikiwa callable(obj):
            test = obj()
            ikiwa isinstance(test, suite.TestSuite):
                rudisha test
            elikiwa isinstance(test, case.TestCase):
                rudisha self.suiteClass([test])
            else:
                raise TypeError("calling %s returned %s, not a test" %
                                (obj, test))
        else:
            raise TypeError("don't know how to make test kutoka: %s" % obj)

    eleza loadTestsFromNames(self, names, module=None):
        """Return a suite of all test cases found using the given sequence
        of string specifiers. See 'loadTestsFromName()'.
        """
        suites = [self.loadTestsFromName(name, module) for name in names]
        rudisha self.suiteClass(suites)

    eleza getTestCaseNames(self, testCaseClass):
        """Return a sorted sequence of method names found within testCaseClass
        """
        eleza shouldIncludeMethod(attrname):
            ikiwa not attrname.startswith(self.testMethodPrefix):
                rudisha False
            testFunc = getattr(testCaseClass, attrname)
            ikiwa not callable(testFunc):
                rudisha False
            fullName = f'%s.%s.%s' % (
                testCaseClass.__module__, testCaseClass.__qualname__, attrname
            )
            rudisha self.testNamePatterns is None or \
                any(fnmatchcase(fullName, pattern) for pattern in self.testNamePatterns)
        testFnNames = list(filter(shouldIncludeMethod, dir(testCaseClass)))
        ikiwa self.sortTestMethodsUsing:
            testFnNames.sort(key=functools.cmp_to_key(self.sortTestMethodsUsing))
        rudisha testFnNames

    eleza discover(self, start_dir, pattern='test*.py', top_level_dir=None):
        """Find and rudisha all test modules kutoka the specified start
        directory, recursing into subdirectories to find them and rudisha all
        tests found within them. Only test files that match the pattern will
        be loaded. (Using shell style pattern matching.)

        All test modules must be agizaable kutoka the top level of the project.
        If the start directory is not the top level directory then the top
        level directory must be specified separately.

        If a test package name (directory with '__init__.py') matches the
        pattern then the package will be checked for a 'load_tests' function. If
        this exists then it will be called with (loader, tests, pattern) unless
        the package has already had load_tests called kutoka the same discovery
        invocation, in which case the package module object is not scanned for
        tests - this ensures that when a package uses discover to further
        discover child tests that infinite recursion does not happen.

        If load_tests exists then discovery does *not* recurse into the package,
        load_tests is responsible for loading all tests in the package.

        The pattern is deliberately not stored as a loader attribute so that
        packages can continue discovery themselves. top_level_dir is stored so
        load_tests does not need to pass this argument in to loader.discover().

        Paths are sorted before being imported to ensure reproducible execution
        order even on filesystems with non-alphabetical ordering like ext3/4.
        """
        set_implicit_top = False
        ikiwa top_level_dir is None and self._top_level_dir is not None:
            # make top_level_dir optional ikiwa called kutoka load_tests in a package
            top_level_dir = self._top_level_dir
        elikiwa top_level_dir is None:
            set_implicit_top = True
            top_level_dir = start_dir

        top_level_dir = os.path.abspath(top_level_dir)

        ikiwa not top_level_dir in sys.path:
            # all test modules must be agizaable kutoka the top level directory
            # should we *unconditionally* put the start directory in first
            # in sys.path to minimise likelihood of conflicts between installed
            # modules and development versions?
            sys.path.insert(0, top_level_dir)
        self._top_level_dir = top_level_dir

        is_not_agizaable = False
        is_namespace = False
        tests = []
        ikiwa os.path.isdir(os.path.abspath(start_dir)):
            start_dir = os.path.abspath(start_dir)
            ikiwa start_dir != top_level_dir:
                is_not_agizaable = not os.path.isfile(os.path.join(start_dir, '__init__.py'))
        else:
            # support for discovery kutoka dotted module names
            try:
                __import__(start_dir)
            except ImportError:
                is_not_agizaable = True
            else:
                the_module = sys.modules[start_dir]
                top_part = start_dir.split('.')[0]
                try:
                    start_dir = os.path.abspath(
                       os.path.dirname((the_module.__file__)))
                except AttributeError:
                    # look for namespace packages
                    try:
                        spec = the_module.__spec__
                    except AttributeError:
                        spec = None

                    ikiwa spec and spec.loader is None:
                        ikiwa spec.submodule_search_locations is not None:
                            is_namespace = True

                            for path in the_module.__path__:
                                ikiwa (not set_implicit_top and
                                    not path.startswith(top_level_dir)):
                                    continue
                                self._top_level_dir = \
                                    (path.split(the_module.__name__
                                         .replace(".", os.path.sep))[0])
                                tests.extend(self._find_tests(path,
                                                              pattern,
                                                              namespace=True))
                    elikiwa the_module.__name__ in sys.builtin_module_names:
                        # builtin module
                        raise TypeError('Can not use builtin modules '
                                        'as dotted module names') kutoka None
                    else:
                        raise TypeError(
                            'don\'t know how to discover kutoka {!r}'
                            .format(the_module)) kutoka None

                ikiwa set_implicit_top:
                    ikiwa not is_namespace:
                        self._top_level_dir = \
                           self._get_directory_containing_module(top_part)
                        sys.path.remove(top_level_dir)
                    else:
                        sys.path.remove(top_level_dir)

        ikiwa is_not_agizaable:
            raise ImportError('Start directory is not agizaable: %r' % start_dir)

        ikiwa not is_namespace:
            tests = list(self._find_tests(start_dir, pattern))
        rudisha self.suiteClass(tests)

    eleza _get_directory_containing_module(self, module_name):
        module = sys.modules[module_name]
        full_path = os.path.abspath(module.__file__)

        ikiwa os.path.basename(full_path).lower().startswith('__init__.py'):
            rudisha os.path.dirname(os.path.dirname(full_path))
        else:
            # here we have been given a module rather than a package - so
            # all we can do is search the *same* directory the module is in
            # should an exception be raised instead
            rudisha os.path.dirname(full_path)

    eleza _get_name_kutoka_path(self, path):
        ikiwa path == self._top_level_dir:
            rudisha '.'
        path = _jython_aware_splitext(os.path.normpath(path))

        _relpath = os.path.relpath(path, self._top_level_dir)
        assert not os.path.isabs(_relpath), "Path must be within the project"
        assert not _relpath.startswith('..'), "Path must be within the project"

        name = _relpath.replace(os.path.sep, '.')
        rudisha name

    eleza _get_module_kutoka_name(self, name):
        __import__(name)
        rudisha sys.modules[name]

    eleza _match_path(self, path, full_path, pattern):
        # override this method to use alternative matching strategy
        rudisha fnmatch(path, pattern)

    eleza _find_tests(self, start_dir, pattern, namespace=False):
        """Used by discovery. Yields test suites it loads."""
        # Handle the __init__ in this package
        name = self._get_name_kutoka_path(start_dir)
        # name is '.' when start_dir == top_level_dir (and top_level_dir is by
        # definition not a package).
        ikiwa name != '.' and name not in self._loading_packages:
            # name is in self._loading_packages while we have called into
            # loadTestsFromModule with name.
            tests, should_recurse = self._find_test_path(
                start_dir, pattern, namespace)
            ikiwa tests is not None:
                yield tests
            ikiwa not should_recurse:
                # Either an error occurred, or load_tests was used by the
                # package.
                return
        # Handle the contents.
        paths = sorted(os.listdir(start_dir))
        for path in paths:
            full_path = os.path.join(start_dir, path)
            tests, should_recurse = self._find_test_path(
                full_path, pattern, namespace)
            ikiwa tests is not None:
                yield tests
            ikiwa should_recurse:
                # we found a package that didn't use load_tests.
                name = self._get_name_kutoka_path(full_path)
                self._loading_packages.add(name)
                try:
                    yield kutoka self._find_tests(full_path, pattern, namespace)
                finally:
                    self._loading_packages.discard(name)

    eleza _find_test_path(self, full_path, pattern, namespace=False):
        """Used by discovery.

        Loads tests kutoka a single file, or a directories' __init__.py when
        passed the directory.

        Returns a tuple (None_or_tests_kutoka_file, should_recurse).
        """
        basename = os.path.basename(full_path)
        ikiwa os.path.isfile(full_path):
            ikiwa not VALID_MODULE_NAME.match(basename):
                # valid Python identifiers only
                rudisha None, False
            ikiwa not self._match_path(basename, full_path, pattern):
                rudisha None, False
            # ikiwa the test file matches, load it
            name = self._get_name_kutoka_path(full_path)
            try:
                module = self._get_module_kutoka_name(name)
            except case.SkipTest as e:
                rudisha _make_skipped_test(name, e, self.suiteClass), False
            except:
                error_case, error_message = \
                    _make_failed_import_test(name, self.suiteClass)
                self.errors.append(error_message)
                rudisha error_case, False
            else:
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
                    raise ImportError(
                        msg % (mod_name, module_dir, expected_dir))
                rudisha self.loadTestsFromModule(module, pattern=pattern), False
        elikiwa os.path.isdir(full_path):
            ikiwa (not namespace and
                not os.path.isfile(os.path.join(full_path, '__init__.py'))):
                rudisha None, False

            load_tests = None
            tests = None
            name = self._get_name_kutoka_path(full_path)
            try:
                package = self._get_module_kutoka_name(name)
            except case.SkipTest as e:
                rudisha _make_skipped_test(name, e, self.suiteClass), False
            except:
                error_case, error_message = \
                    _make_failed_import_test(name, self.suiteClass)
                self.errors.append(error_message)
                rudisha error_case, False
            else:
                load_tests = getattr(package, 'load_tests', None)
                # Mark this package as being in load_tests (possibly ;))
                self._loading_packages.add(name)
                try:
                    tests = self.loadTestsFromModule(package, pattern=pattern)
                    ikiwa load_tests is not None:
                        # loadTestsFromModule(package) has loaded tests for us.
                        rudisha tests, False
                    rudisha tests, True
                finally:
                    self._loading_packages.discard(name)
        else:
            rudisha None, False


defaultTestLoader = TestLoader()


eleza _makeLoader(prefix, sortUsing, suiteClass=None, testNamePatterns=None):
    loader = TestLoader()
    loader.sortTestMethodsUsing = sortUsing
    loader.testMethodPrefix = prefix
    loader.testNamePatterns = testNamePatterns
    ikiwa suiteClass:
        loader.suiteClass = suiteClass
    rudisha loader

eleza getTestCaseNames(testCaseClass, prefix, sortUsing=util.three_way_cmp, testNamePatterns=None):
    rudisha _makeLoader(prefix, sortUsing, testNamePatterns=testNamePatterns).getTestCaseNames(testCaseClass)

eleza makeSuite(testCaseClass, prefix='test', sortUsing=util.three_way_cmp,
              suiteClass=suite.TestSuite):
    rudisha _makeLoader(prefix, sortUsing, suiteClass).loadTestsFromTestCase(
        testCaseClass)

eleza findTestCases(module, prefix='test', sortUsing=util.three_way_cmp,
                  suiteClass=suite.TestSuite):
    rudisha _makeLoader(prefix, sortUsing, suiteClass).loadTestsFromModule(\
        module)
