agiza io
agiza os
agiza sys
agiza pickle
agiza subprocess

agiza unittest
kutoka unittest.case agiza _Outcome

kutoka unittest.test.support agiza (LoggingResult,
                                   ResultWithNoStartTestRunStopTestRun)


eleza resultFactory(*_):
    rudisha unittest.TestResult()


eleza getRunner():
    rudisha unittest.TextTestRunner(resultclass=resultFactory,
                                   stream=io.StringIO())


eleza runTests(*cases):
    suite = unittest.TestSuite()
    kila case kwenye cases:
        tests = unittest.defaultTestLoader.loadTestsFromTestCase(case)
        suite.addTests(tests)

    runner = getRunner()

    # creating a nested suite exposes some potential bugs
    realSuite = unittest.TestSuite()
    realSuite.addTest(suite)
    # adding empty suites to the end exposes potential bugs
    suite.addTest(unittest.TestSuite())
    realSuite.addTest(unittest.TestSuite())
    rudisha runner.run(realSuite)


eleza cleanup(ordering, blowUp=Uongo):
    ikiwa sio blowUp:
        ordering.append('cleanup_good')
    isipokua:
        ordering.append('cleanup_exc')
        ashiria Exception('CleanUpExc')


kundi TestCleanUp(unittest.TestCase):
    eleza testCleanUp(self):
        kundi TestableTest(unittest.TestCase):
            eleza testNothing(self):
                pita

        test = TestableTest('testNothing')
        self.assertEqual(test._cleanups, [])

        cleanups = []

        eleza cleanup1(*args, **kwargs):
            cleanups.append((1, args, kwargs))

        eleza cleanup2(*args, **kwargs):
            cleanups.append((2, args, kwargs))

        test.addCleanup(cleanup1, 1, 2, 3, four='hello', five='goodbye')
        test.addCleanup(cleanup2)

        self.assertEqual(test._cleanups,
                         [(cleanup1, (1, 2, 3), dict(four='hello', five='goodbye')),
                          (cleanup2, (), {})])

        self.assertKweli(test.doCleanups())
        self.assertEqual(cleanups, [(2, (), {}), (1, (1, 2, 3), dict(four='hello', five='goodbye'))])

    eleza testCleanUpWithErrors(self):
        kundi TestableTest(unittest.TestCase):
            eleza testNothing(self):
                pita

        test = TestableTest('testNothing')
        outcome = test._outcome = _Outcome()

        CleanUpExc = Exception('foo')
        exc2 = Exception('bar')
        eleza cleanup1():
            ashiria CleanUpExc

        eleza cleanup2():
            ashiria exc2

        test.addCleanup(cleanup1)
        test.addCleanup(cleanup2)

        self.assertUongo(test.doCleanups())
        self.assertUongo(outcome.success)

        ((_, (Type1, instance1, _)),
         (_, (Type2, instance2, _))) = reversed(outcome.errors)
        self.assertEqual((Type1, instance1), (Exception, CleanUpExc))
        self.assertEqual((Type2, instance2), (Exception, exc2))

    eleza testCleanupInRun(self):
        blowUp = Uongo
        ordering = []

        kundi TestableTest(unittest.TestCase):
            eleza setUp(self):
                ordering.append('setUp')
                ikiwa blowUp:
                    ashiria Exception('foo')

            eleza testNothing(self):
                ordering.append('test')

            eleza tearDown(self):
                ordering.append('tearDown')

        test = TestableTest('testNothing')

        eleza cleanup1():
            ordering.append('cleanup1')
        eleza cleanup2():
            ordering.append('cleanup2')
        test.addCleanup(cleanup1)
        test.addCleanup(cleanup2)

        eleza success(some_test):
            self.assertEqual(some_test, test)
            ordering.append('success')

        result = unittest.TestResult()
        result.addSuccess = success

        test.run(result)
        self.assertEqual(ordering, ['setUp', 'test', 'tearDown',
                                    'cleanup2', 'cleanup1', 'success'])

        blowUp = Kweli
        ordering = []
        test = TestableTest('testNothing')
        test.addCleanup(cleanup1)
        test.run(result)
        self.assertEqual(ordering, ['setUp', 'cleanup1'])

    eleza testTestCaseDebugExecutesCleanups(self):
        ordering = []

        kundi TestableTest(unittest.TestCase):
            eleza setUp(self):
                ordering.append('setUp')
                self.addCleanup(cleanup1)

            eleza testNothing(self):
                ordering.append('test')

            eleza tearDown(self):
                ordering.append('tearDown')

        test = TestableTest('testNothing')

        eleza cleanup1():
            ordering.append('cleanup1')
            test.addCleanup(cleanup2)
        eleza cleanup2():
            ordering.append('cleanup2')

        test.debug()
        self.assertEqual(ordering, ['setUp', 'test', 'tearDown', 'cleanup1', 'cleanup2'])


kundi TestClassCleanup(unittest.TestCase):
    eleza test_addClassCleanUp(self):
        kundi TestableTest(unittest.TestCase):
            eleza testNothing(self):
                pita
        test = TestableTest('testNothing')
        self.assertEqual(test._class_cleanups, [])
        class_cleanups = []

        eleza class_cleanup1(*args, **kwargs):
            class_cleanups.append((3, args, kwargs))

        eleza class_cleanup2(*args, **kwargs):
            class_cleanups.append((4, args, kwargs))

        TestableTest.addClassCleanup(class_cleanup1, 1, 2, 3,
                                     four='hello', five='goodbye')
        TestableTest.addClassCleanup(class_cleanup2)

        self.assertEqual(test._class_cleanups,
                         [(class_cleanup1, (1, 2, 3),
                           dict(four='hello', five='goodbye')),
                          (class_cleanup2, (), {})])

        TestableTest.doClassCleanups()
        self.assertEqual(class_cleanups, [(4, (), {}), (3, (1, 2, 3),
                                          dict(four='hello', five='goodbye'))])

    eleza test_run_class_cleanUp(self):
        ordering = []
        blowUp = Kweli

        kundi TestableTest(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ordering.append('setUpClass')
                cls.addClassCleanup(cleanup, ordering)
                ikiwa blowUp:
                    ashiria Exception()
            eleza testNothing(self):
                ordering.append('test')
            @classmethod
            eleza tearDownClass(cls):
                ordering.append('tearDownClass')

        runTests(TestableTest)
        self.assertEqual(ordering, ['setUpClass', 'cleanup_good'])

        ordering = []
        blowUp = Uongo
        runTests(TestableTest)
        self.assertEqual(ordering,
                         ['setUpClass', 'test', 'tearDownClass', 'cleanup_good'])

    eleza test_debug_executes_classCleanUp(self):
        ordering = []

        kundi TestableTest(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ordering.append('setUpClass')
                cls.addClassCleanup(cleanup, ordering)
            eleza testNothing(self):
                ordering.append('test')
            @classmethod
            eleza tearDownClass(cls):
                ordering.append('tearDownClass')

        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestableTest)
        suite.debug()
        self.assertEqual(ordering,
                         ['setUpClass', 'test', 'tearDownClass', 'cleanup_good'])

    eleza test_doClassCleanups_with_errors_addClassCleanUp(self):
        kundi TestableTest(unittest.TestCase):
            eleza testNothing(self):
                pita

        eleza cleanup1():
            ashiria Exception('cleanup1')

        eleza cleanup2():
            ashiria Exception('cleanup2')

        TestableTest.addClassCleanup(cleanup1)
        TestableTest.addClassCleanup(cleanup2)
        ukijumuisha self.assertRaises(Exception) kama e:
            TestableTest.doClassCleanups()
            self.assertEqual(e, 'cleanup1')

    eleza test_with_errors_addCleanUp(self):
        ordering = []
        kundi TestableTest(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ordering.append('setUpClass')
                cls.addClassCleanup(cleanup, ordering)
            eleza setUp(self):
                ordering.append('setUp')
                self.addCleanup(cleanup, ordering, blowUp=Kweli)
            eleza testNothing(self):
                pita
            @classmethod
            eleza tearDownClass(cls):
                ordering.append('tearDownClass')

        result = runTests(TestableTest)
        self.assertEqual(result.errors[0][1].splitlines()[-1],
                         'Exception: CleanUpExc')
        self.assertEqual(ordering,
                         ['setUpClass', 'setUp', 'cleanup_exc',
                          'tearDownClass', 'cleanup_good'])

    eleza test_run_with_errors_addClassCleanUp(self):
        ordering = []
        kundi TestableTest(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ordering.append('setUpClass')
                cls.addClassCleanup(cleanup, ordering, blowUp=Kweli)
            eleza setUp(self):
                ordering.append('setUp')
                self.addCleanup(cleanup, ordering)
            eleza testNothing(self):
                ordering.append('test')
            @classmethod
            eleza tearDownClass(cls):
                ordering.append('tearDownClass')

        result = runTests(TestableTest)
        self.assertEqual(result.errors[0][1].splitlines()[-1],
                         'Exception: CleanUpExc')
        self.assertEqual(ordering,
                         ['setUpClass', 'setUp', 'test', 'cleanup_good',
                          'tearDownClass', 'cleanup_exc'])

    eleza test_with_errors_in_addClassCleanup_and_setUps(self):
        ordering = []
        class_blow_up = Uongo
        method_blow_up = Uongo

        kundi TestableTest(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ordering.append('setUpClass')
                cls.addClassCleanup(cleanup, ordering, blowUp=Kweli)
                ikiwa class_blow_up:
                    ashiria Exception('ClassExc')
            eleza setUp(self):
                ordering.append('setUp')
                ikiwa method_blow_up:
                    ashiria Exception('MethodExc')
            eleza testNothing(self):
                ordering.append('test')
            @classmethod
            eleza tearDownClass(cls):
                ordering.append('tearDownClass')

        result = runTests(TestableTest)
        self.assertEqual(result.errors[0][1].splitlines()[-1],
                         'Exception: CleanUpExc')
        self.assertEqual(ordering,
                         ['setUpClass', 'setUp', 'test',
                          'tearDownClass', 'cleanup_exc'])
        ordering = []
        class_blow_up = Kweli
        method_blow_up = Uongo
        result = runTests(TestableTest)
        self.assertEqual(result.errors[0][1].splitlines()[-1],
                         'Exception: ClassExc')
        self.assertEqual(result.errors[1][1].splitlines()[-1],
                         'Exception: CleanUpExc')
        self.assertEqual(ordering,
                         ['setUpClass', 'cleanup_exc'])

        ordering = []
        class_blow_up = Uongo
        method_blow_up = Kweli
        result = runTests(TestableTest)
        self.assertEqual(result.errors[0][1].splitlines()[-1],
                         'Exception: MethodExc')
        self.assertEqual(result.errors[1][1].splitlines()[-1],
                         'Exception: CleanUpExc')
        self.assertEqual(ordering,
                         ['setUpClass', 'setUp', 'tearDownClass',
                          'cleanup_exc'])


kundi TestModuleCleanUp(unittest.TestCase):
    eleza test_add_and_do_ModuleCleanup(self):
        module_cleanups = []

        eleza module_cleanup1(*args, **kwargs):
            module_cleanups.append((3, args, kwargs))

        eleza module_cleanup2(*args, **kwargs):
            module_cleanups.append((4, args, kwargs))

        kundi Module(object):
            unittest.addModuleCleanup(module_cleanup1, 1, 2, 3,
                                      four='hello', five='goodbye')
            unittest.addModuleCleanup(module_cleanup2)

        self.assertEqual(unittest.case._module_cleanups,
                         [(module_cleanup1, (1, 2, 3),
                           dict(four='hello', five='goodbye')),
                          (module_cleanup2, (), {})])

        unittest.case.doModuleCleanups()
        self.assertEqual(module_cleanups, [(4, (), {}), (3, (1, 2, 3),
                                          dict(four='hello', five='goodbye'))])
        self.assertEqual(unittest.case._module_cleanups, [])

    eleza test_doModuleCleanup_with_errors_in_addModuleCleanup(self):
        module_cleanups = []

        eleza module_cleanup_good(*args, **kwargs):
            module_cleanups.append((3, args, kwargs))

        eleza module_cleanup_bad(*args, **kwargs):
            ashiria Exception('CleanUpExc')

        kundi Module(object):
            unittest.addModuleCleanup(module_cleanup_good, 1, 2, 3,
                                      four='hello', five='goodbye')
            unittest.addModuleCleanup(module_cleanup_bad)
        self.assertEqual(unittest.case._module_cleanups,
                         [(module_cleanup_good, (1, 2, 3),
                           dict(four='hello', five='goodbye')),
                          (module_cleanup_bad, (), {})])
        ukijumuisha self.assertRaises(Exception) kama e:
            unittest.case.doModuleCleanups()
        self.assertEqual(str(e.exception), 'CleanUpExc')
        self.assertEqual(unittest.case._module_cleanups, [])

    eleza test_addModuleCleanup_arg_errors(self):
        cleanups = []
        eleza cleanup(*args, **kwargs):
            cleanups.append((args, kwargs))

        kundi Module(object):
            unittest.addModuleCleanup(cleanup, 1, 2, function='hello')
            ukijumuisha self.assertRaises(TypeError):
                unittest.addModuleCleanup(function=cleanup, arg='hello')
            ukijumuisha self.assertRaises(TypeError):
                unittest.addModuleCleanup()
        unittest.case.doModuleCleanups()
        self.assertEqual(cleanups,
                         [((1, 2), {'function': 'hello'})])

    eleza test_run_module_cleanUp(self):
        blowUp = Kweli
        ordering = []
        kundi Module(object):
            @staticmethod
            eleza setUpModule():
                ordering.append('setUpModule')
                unittest.addModuleCleanup(cleanup, ordering)
                ikiwa blowUp:
                    ashiria Exception('setUpModule Exc')
            @staticmethod
            eleza tearDownModule():
                ordering.append('tearDownModule')

        kundi TestableTest(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ordering.append('setUpClass')
            eleza testNothing(self):
                ordering.append('test')
            @classmethod
            eleza tearDownClass(cls):
                ordering.append('tearDownClass')

        TestableTest.__module__ = 'Module'
        sys.modules['Module'] = Module
        result = runTests(TestableTest)
        self.assertEqual(ordering, ['setUpModule', 'cleanup_good'])
        self.assertEqual(result.errors[0][1].splitlines()[-1],
                         'Exception: setUpModule Exc')

        ordering = []
        blowUp = Uongo
        runTests(TestableTest)
        self.assertEqual(ordering,
                         ['setUpModule', 'setUpClass', 'test', 'tearDownClass',
                          'tearDownModule', 'cleanup_good'])
        self.assertEqual(unittest.case._module_cleanups, [])

    eleza test_run_multiple_module_cleanUp(self):
        blowUp = Kweli
        blowUp2 = Uongo
        ordering = []
        kundi Module1(object):
            @staticmethod
            eleza setUpModule():
                ordering.append('setUpModule')
                unittest.addModuleCleanup(cleanup, ordering)
                ikiwa blowUp:
                    ashiria Exception()
            @staticmethod
            eleza tearDownModule():
                ordering.append('tearDownModule')

        kundi Module2(object):
            @staticmethod
            eleza setUpModule():
                ordering.append('setUpModule2')
                unittest.addModuleCleanup(cleanup, ordering)
                ikiwa blowUp2:
                    ashiria Exception()
            @staticmethod
            eleza tearDownModule():
                ordering.append('tearDownModule2')

        kundi TestableTest(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ordering.append('setUpClass')
            eleza testNothing(self):
                ordering.append('test')
            @classmethod
            eleza tearDownClass(cls):
                ordering.append('tearDownClass')

        kundi TestableTest2(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ordering.append('setUpClass2')
            eleza testNothing(self):
                ordering.append('test2')
            @classmethod
            eleza tearDownClass(cls):
                ordering.append('tearDownClass2')

        TestableTest.__module__ = 'Module1'
        sys.modules['Module1'] = Module1
        TestableTest2.__module__ = 'Module2'
        sys.modules['Module2'] = Module2
        runTests(TestableTest, TestableTest2)
        self.assertEqual(ordering, ['setUpModule', 'cleanup_good',
                                    'setUpModule2', 'setUpClass2', 'test2',
                                    'tearDownClass2', 'tearDownModule2',
                                    'cleanup_good'])
        ordering = []
        blowUp = Uongo
        blowUp2 = Kweli
        runTests(TestableTest, TestableTest2)
        self.assertEqual(ordering, ['setUpModule', 'setUpClass', 'test',
                                    'tearDownClass', 'tearDownModule',
                                    'cleanup_good', 'setUpModule2',
                                    'cleanup_good'])

        ordering = []
        blowUp = Uongo
        blowUp2 = Uongo
        runTests(TestableTest, TestableTest2)
        self.assertEqual(ordering,
                         ['setUpModule', 'setUpClass', 'test', 'tearDownClass',
                          'tearDownModule', 'cleanup_good', 'setUpModule2',
                          'setUpClass2', 'test2', 'tearDownClass2',
                          'tearDownModule2', 'cleanup_good'])
        self.assertEqual(unittest.case._module_cleanups, [])

    eleza test_debug_module_executes_cleanUp(self):
        ordering = []
        kundi Module(object):
            @staticmethod
            eleza setUpModule():
                ordering.append('setUpModule')
                unittest.addModuleCleanup(cleanup, ordering)
            @staticmethod
            eleza tearDownModule():
                ordering.append('tearDownModule')

        kundi TestableTest(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ordering.append('setUpClass')
            eleza testNothing(self):
                ordering.append('test')
            @classmethod
            eleza tearDownClass(cls):
                ordering.append('tearDownClass')

        TestableTest.__module__ = 'Module'
        sys.modules['Module'] = Module
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestableTest)
        suite.debug()
        self.assertEqual(ordering,
                         ['setUpModule', 'setUpClass', 'test', 'tearDownClass',
                          'tearDownModule', 'cleanup_good'])
        self.assertEqual(unittest.case._module_cleanups, [])

    eleza test_addClassCleanup_arg_errors(self):
        cleanups = []
        eleza cleanup(*args, **kwargs):
            cleanups.append((args, kwargs))

        kundi TestableTest(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                cls.addClassCleanup(cleanup, 1, 2, function=3, cls=4)
                ukijumuisha self.assertRaises(TypeError):
                    cls.addClassCleanup(function=cleanup, arg='hello')
            eleza testNothing(self):
                pita

        ukijumuisha self.assertRaises(TypeError):
            TestableTest.addClassCleanup()
        ukijumuisha self.assertRaises(TypeError):
            unittest.TestCase.addCleanup(cls=TestableTest(), function=cleanup)
        runTests(TestableTest)
        self.assertEqual(cleanups,
                         [((1, 2), {'function': 3, 'cls': 4})])

    eleza test_addCleanup_arg_errors(self):
        cleanups = []
        eleza cleanup(*args, **kwargs):
            cleanups.append((args, kwargs))

        kundi TestableTest(unittest.TestCase):
            eleza setUp(self2):
                self2.addCleanup(cleanup, 1, 2, function=3, self=4)
                ukijumuisha self.assertWarns(DeprecationWarning):
                    self2.addCleanup(function=cleanup, arg='hello')
            eleza testNothing(self):
                pita

        ukijumuisha self.assertRaises(TypeError):
            TestableTest().addCleanup()
        ukijumuisha self.assertRaises(TypeError):
            unittest.TestCase.addCleanup(self=TestableTest(), function=cleanup)
        runTests(TestableTest)
        self.assertEqual(cleanups,
                         [((), {'arg': 'hello'}),
                          ((1, 2), {'function': 3, 'self': 4})])

    eleza test_with_errors_in_addClassCleanup(self):
        ordering = []

        kundi Module(object):
            @staticmethod
            eleza setUpModule():
                ordering.append('setUpModule')
                unittest.addModuleCleanup(cleanup, ordering)
            @staticmethod
            eleza tearDownModule():
                ordering.append('tearDownModule')

        kundi TestableTest(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ordering.append('setUpClass')
                cls.addClassCleanup(cleanup, ordering, blowUp=Kweli)
            eleza testNothing(self):
                ordering.append('test')
            @classmethod
            eleza tearDownClass(cls):
                ordering.append('tearDownClass')

        TestableTest.__module__ = 'Module'
        sys.modules['Module'] = Module

        result = runTests(TestableTest)
        self.assertEqual(result.errors[0][1].splitlines()[-1],
                         'Exception: CleanUpExc')
        self.assertEqual(ordering,
                         ['setUpModule', 'setUpClass', 'test', 'tearDownClass',
                          'cleanup_exc', 'tearDownModule', 'cleanup_good'])

    eleza test_with_errors_in_addCleanup(self):
        ordering = []
        kundi Module(object):
            @staticmethod
            eleza setUpModule():
                ordering.append('setUpModule')
                unittest.addModuleCleanup(cleanup, ordering)
            @staticmethod
            eleza tearDownModule():
                ordering.append('tearDownModule')

        kundi TestableTest(unittest.TestCase):
            eleza setUp(self):
                ordering.append('setUp')
                self.addCleanup(cleanup, ordering, blowUp=Kweli)
            eleza testNothing(self):
                ordering.append('test')
            eleza tearDown(self):
                ordering.append('tearDown')

        TestableTest.__module__ = 'Module'
        sys.modules['Module'] = Module

        result = runTests(TestableTest)
        self.assertEqual(result.errors[0][1].splitlines()[-1],
                         'Exception: CleanUpExc')
        self.assertEqual(ordering,
                         ['setUpModule', 'setUp', 'test', 'tearDown',
                          'cleanup_exc', 'tearDownModule', 'cleanup_good'])

    eleza test_with_errors_in_addModuleCleanup_and_setUps(self):
        ordering = []
        module_blow_up = Uongo
        class_blow_up = Uongo
        method_blow_up = Uongo
        kundi Module(object):
            @staticmethod
            eleza setUpModule():
                ordering.append('setUpModule')
                unittest.addModuleCleanup(cleanup, ordering, blowUp=Kweli)
                ikiwa module_blow_up:
                    ashiria Exception('ModuleExc')
            @staticmethod
            eleza tearDownModule():
                ordering.append('tearDownModule')

        kundi TestableTest(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ordering.append('setUpClass')
                ikiwa class_blow_up:
                    ashiria Exception('ClassExc')
            eleza setUp(self):
                ordering.append('setUp')
                ikiwa method_blow_up:
                    ashiria Exception('MethodExc')
            eleza testNothing(self):
                ordering.append('test')
            @classmethod
            eleza tearDownClass(cls):
                ordering.append('tearDownClass')

        TestableTest.__module__ = 'Module'
        sys.modules['Module'] = Module

        result = runTests(TestableTest)
        self.assertEqual(result.errors[0][1].splitlines()[-1],
                         'Exception: CleanUpExc')
        self.assertEqual(ordering,
                         ['setUpModule', 'setUpClass', 'setUp', 'test',
                          'tearDownClass', 'tearDownModule',
                          'cleanup_exc'])

        ordering = []
        module_blow_up = Kweli
        class_blow_up = Uongo
        method_blow_up = Uongo
        result = runTests(TestableTest)
        self.assertEqual(result.errors[0][1].splitlines()[-1],
                         'Exception: CleanUpExc')
        self.assertEqual(result.errors[1][1].splitlines()[-1],
                         'Exception: ModuleExc')
        self.assertEqual(ordering, ['setUpModule', 'cleanup_exc'])

        ordering = []
        module_blow_up = Uongo
        class_blow_up = Kweli
        method_blow_up = Uongo
        result = runTests(TestableTest)
        self.assertEqual(result.errors[0][1].splitlines()[-1],
                         'Exception: ClassExc')
        self.assertEqual(result.errors[1][1].splitlines()[-1],
                         'Exception: CleanUpExc')
        self.assertEqual(ordering, ['setUpModule', 'setUpClass',
                                    'tearDownModule', 'cleanup_exc'])

        ordering = []
        module_blow_up = Uongo
        class_blow_up = Uongo
        method_blow_up = Kweli
        result = runTests(TestableTest)
        self.assertEqual(result.errors[0][1].splitlines()[-1],
                         'Exception: MethodExc')
        self.assertEqual(result.errors[1][1].splitlines()[-1],
                         'Exception: CleanUpExc')
        self.assertEqual(ordering, ['setUpModule', 'setUpClass', 'setUp',
                                    'tearDownClass', 'tearDownModule',
                                    'cleanup_exc'])

    eleza test_module_cleanUp_with_multiple_classes(self):
        ordering =[]
        eleza cleanup1():
            ordering.append('cleanup1')

        eleza cleanup2():
            ordering.append('cleanup2')

        eleza cleanup3():
            ordering.append('cleanup3')

        kundi Module(object):
            @staticmethod
            eleza setUpModule():
                ordering.append('setUpModule')
                unittest.addModuleCleanup(cleanup1)
            @staticmethod
            eleza tearDownModule():
                ordering.append('tearDownModule')

        kundi TestableTest(unittest.TestCase):
            eleza setUp(self):
                ordering.append('setUp')
                self.addCleanup(cleanup2)
            eleza testNothing(self):
                ordering.append('test')
            eleza tearDown(self):
                ordering.append('tearDown')

        kundi OtherTestableTest(unittest.TestCase):
            eleza setUp(self):
                ordering.append('setUp2')
                self.addCleanup(cleanup3)
            eleza testNothing(self):
                ordering.append('test2')
            eleza tearDown(self):
                ordering.append('tearDown2')

        TestableTest.__module__ = 'Module'
        OtherTestableTest.__module__ = 'Module'
        sys.modules['Module'] = Module
        runTests(TestableTest, OtherTestableTest)
        self.assertEqual(ordering,
                         ['setUpModule', 'setUp', 'test', 'tearDown',
                          'cleanup2',  'setUp2', 'test2', 'tearDown2',
                          'cleanup3', 'tearDownModule', 'cleanup1'])


kundi Test_TextTestRunner(unittest.TestCase):
    """Tests kila TextTestRunner."""

    eleza setUp(self):
        # clean the environment kutoka pre-existing PYTHONWARNINGS to make
        # test_warnings results consistent
        self.pythonwarnings = os.environ.get('PYTHONWARNINGS')
        ikiwa self.pythonwarnings:
            toa os.environ['PYTHONWARNINGS']

    eleza tearDown(self):
        # bring back pre-existing PYTHONWARNINGS ikiwa present
        ikiwa self.pythonwarnings:
            os.environ['PYTHONWARNINGS'] = self.pythonwarnings

    eleza test_init(self):
        runner = unittest.TextTestRunner()
        self.assertUongo(runner.failfast)
        self.assertUongo(runner.buffer)
        self.assertEqual(runner.verbosity, 1)
        self.assertEqual(runner.warnings, Tupu)
        self.assertKweli(runner.descriptions)
        self.assertEqual(runner.resultclass, unittest.TextTestResult)
        self.assertUongo(runner.tb_locals)

    eleza test_multiple_inheritance(self):
        kundi AResult(unittest.TestResult):
            eleza __init__(self, stream, descriptions, verbosity):
                super(AResult, self).__init__(stream, descriptions, verbosity)

        kundi ATextResult(unittest.TextTestResult, AResult):
            pita

        # This used to ashiria an exception due to TextTestResult sio pitaing
        # on arguments kwenye its __init__ super call
        ATextResult(Tupu, Tupu, 1)

    eleza testBufferAndFailfast(self):
        kundi Test(unittest.TestCase):
            eleza testFoo(self):
                pita
        result = unittest.TestResult()
        runner = unittest.TextTestRunner(stream=io.StringIO(), failfast=Kweli,
                                         buffer=Kweli)
        # Use our result object
        runner._makeResult = lambda: result
        runner.run(Test('testFoo'))

        self.assertKweli(result.failfast)
        self.assertKweli(result.buffer)

    eleza test_locals(self):
        runner = unittest.TextTestRunner(stream=io.StringIO(), tb_locals=Kweli)
        result = runner.run(unittest.TestSuite())
        self.assertEqual(Kweli, result.tb_locals)

    eleza testRunnerRegistersResult(self):
        kundi Test(unittest.TestCase):
            eleza testFoo(self):
                pita
        originalRegisterResult = unittest.runner.registerResult
        eleza cleanup():
            unittest.runner.registerResult = originalRegisterResult
        self.addCleanup(cleanup)

        result = unittest.TestResult()
        runner = unittest.TextTestRunner(stream=io.StringIO())
        # Use our result object
        runner._makeResult = lambda: result

        self.wasRegistered = 0
        eleza fakeRegisterResult(thisResult):
            self.wasRegistered += 1
            self.assertEqual(thisResult, result)
        unittest.runner.registerResult = fakeRegisterResult

        runner.run(unittest.TestSuite())
        self.assertEqual(self.wasRegistered, 1)

    eleza test_works_with_result_without_startTestRun_stopTestRun(self):
        kundi OldTextResult(ResultWithNoStartTestRunStopTestRun):
            separator2 = ''
            eleza printErrors(self):
                pita

        kundi Runner(unittest.TextTestRunner):
            eleza __init__(self):
                super(Runner, self).__init__(io.StringIO())

            eleza _makeResult(self):
                rudisha OldTextResult()

        runner = Runner()
        runner.run(unittest.TestSuite())

    eleza test_startTestRun_stopTestRun_called(self):
        kundi LoggingTextResult(LoggingResult):
            separator2 = ''
            eleza printErrors(self):
                pita

        kundi LoggingRunner(unittest.TextTestRunner):
            eleza __init__(self, events):
                super(LoggingRunner, self).__init__(io.StringIO())
                self._events = events

            eleza _makeResult(self):
                rudisha LoggingTextResult(self._events)

        events = []
        runner = LoggingRunner(events)
        runner.run(unittest.TestSuite())
        expected = ['startTestRun', 'stopTestRun']
        self.assertEqual(events, expected)

    eleza test_pickle_unpickle(self):
        # Issue #7197: a TextTestRunner should be (un)pickleable. This is
        # required by test_multiprocessing under Windows (in verbose mode).
        stream = io.StringIO("foo")
        runner = unittest.TextTestRunner(stream)
        kila protocol kwenye range(2, pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(runner, protocol)
            obj = pickle.loads(s)
            # StringIO objects never compare equal, a cheap test instead.
            self.assertEqual(obj.stream.getvalue(), stream.getvalue())

    eleza test_resultclass(self):
        eleza MockResultClass(*args):
            rudisha args
        STREAM = object()
        DESCRIPTIONS = object()
        VERBOSITY = object()
        runner = unittest.TextTestRunner(STREAM, DESCRIPTIONS, VERBOSITY,
                                         resultclass=MockResultClass)
        self.assertEqual(runner.resultclass, MockResultClass)

        expectedresult = (runner.stream, DESCRIPTIONS, VERBOSITY)
        self.assertEqual(runner._makeResult(), expectedresult)

    eleza test_warnings(self):
        """
        Check that warnings argument of TextTestRunner correctly affects the
        behavior of the warnings.
        """
        # see #10535 na the _test_warnings file kila more information

        eleza get_parse_out_err(p):
            rudisha [b.splitlines() kila b kwenye p.communicate()]
        opts = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    cwd=os.path.dirname(__file__))
        ae_msg = b'Please use assertEqual instead.'
        at_msg = b'Please use assertKweli instead.'

        # no args -> all the warnings are printed, unittest warnings only once
        p = subprocess.Popen([sys.executable, '-E', '_test_warnings.py'], **opts)
        ukijumuisha p:
            out, err = get_parse_out_err(p)
        self.assertIn(b'OK', err)
        # check that the total number of warnings kwenye the output ni correct
        self.assertEqual(len(out), 12)
        # check that the numbers of the different kind of warnings ni correct
        kila msg kwenye [b'dw', b'iw', b'uw']:
            self.assertEqual(out.count(msg), 3)
        kila msg kwenye [ae_msg, at_msg, b'rw']:
            self.assertEqual(out.count(msg), 1)

        args_list = (
            # pitaing 'ignore' kama warnings arg -> no warnings
            [sys.executable, '_test_warnings.py', 'ignore'],
            # -W doesn't affect the result ikiwa the arg ni pitaed
            [sys.executable, '-Wa', '_test_warnings.py', 'ignore'],
            # -W affects the result ikiwa the arg ni sio pitaed
            [sys.executable, '-Wi', '_test_warnings.py']
        )
        # kwenye all these cases no warnings are printed
        kila args kwenye args_list:
            p = subprocess.Popen(args, **opts)
            ukijumuisha p:
                out, err = get_parse_out_err(p)
            self.assertIn(b'OK', err)
            self.assertEqual(len(out), 0)


        # pitaing 'always' kama warnings arg -> all the warnings printed,
        #                                     unittest warnings only once
        p = subprocess.Popen([sys.executable, '_test_warnings.py', 'always'],
                             **opts)
        ukijumuisha p:
            out, err = get_parse_out_err(p)
        self.assertIn(b'OK', err)
        self.assertEqual(len(out), 14)
        kila msg kwenye [b'dw', b'iw', b'uw', b'rw']:
            self.assertEqual(out.count(msg), 3)
        kila msg kwenye [ae_msg, at_msg]:
            self.assertEqual(out.count(msg), 1)

    eleza testStdErrLookedUpAtInstantiationTime(self):
        # see issue 10786
        old_stderr = sys.stderr
        f = io.StringIO()
        sys.stderr = f
        jaribu:
            runner = unittest.TextTestRunner()
            self.assertKweli(runner.stream.stream ni f)
        mwishowe:
            sys.stderr = old_stderr

    eleza testSpecifiedStreamUsed(self):
        # see issue 10786
        f = io.StringIO()
        runner = unittest.TextTestRunner(f)
        self.assertKweli(runner.stream.stream ni f)


ikiwa __name__ == "__main__":
    unittest.main()
