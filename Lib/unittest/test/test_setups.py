agiza io
agiza sys

agiza unittest


eleza resultFactory(*_):
    rudisha unittest.TestResult()


kundi TestSetups(unittest.TestCase):

    eleza getRunner(self):
        rudisha unittest.TextTestRunner(resultclass=resultFactory,
                                          stream=io.StringIO())
    eleza runTests(self, *cases):
        suite = unittest.TestSuite()
        kila case kwenye cases:
            tests = unittest.defaultTestLoader.loadTestsFromTestCase(case)
            suite.addTests(tests)

        runner = self.getRunner()

        # creating a nested suite exposes some potential bugs
        realSuite = unittest.TestSuite()
        realSuite.addTest(suite)
        # adding empty suites to the end exposes potential bugs
        suite.addTest(unittest.TestSuite())
        realSuite.addTest(unittest.TestSuite())
        rudisha runner.run(realSuite)

    eleza test_setup_class(self):
        kundi Test(unittest.TestCase):
            setUpCalled = 0
            @classmethod
            eleza setUpClass(cls):
                Test.setUpCalled += 1
                unittest.TestCase.setUpClass()
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita

        result = self.runTests(Test)

        self.assertEqual(Test.setUpCalled, 1)
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.errors), 0)

    eleza test_teardown_class(self):
        kundi Test(unittest.TestCase):
            tearDownCalled = 0
            @classmethod
            eleza tearDownClass(cls):
                Test.tearDownCalled += 1
                unittest.TestCase.tearDownClass()
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita

        result = self.runTests(Test)

        self.assertEqual(Test.tearDownCalled, 1)
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.errors), 0)

    eleza test_teardown_class_two_classes(self):
        kundi Test(unittest.TestCase):
            tearDownCalled = 0
            @classmethod
            eleza tearDownClass(cls):
                Test.tearDownCalled += 1
                unittest.TestCase.tearDownClass()
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita

        kundi Test2(unittest.TestCase):
            tearDownCalled = 0
            @classmethod
            eleza tearDownClass(cls):
                Test2.tearDownCalled += 1
                unittest.TestCase.tearDownClass()
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita

        result = self.runTests(Test, Test2)

        self.assertEqual(Test.tearDownCalled, 1)
        self.assertEqual(Test2.tearDownCalled, 1)
        self.assertEqual(result.testsRun, 4)
        self.assertEqual(len(result.errors), 0)

    eleza test_error_in_setupclass(self):
        kundi BrokenTest(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ashiria TypeError('foo')
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita

        result = self.runTests(BrokenTest)

        self.assertEqual(result.testsRun, 0)
        self.assertEqual(len(result.errors), 1)
        error, _ = result.errors[0]
        self.assertEqual(str(error),
                    'setUpClass (%s.%s)' % (__name__, BrokenTest.__qualname__))

    eleza test_error_in_teardown_class(self):
        kundi Test(unittest.TestCase):
            tornDown = 0
            @classmethod
            eleza tearDownClass(cls):
                Test.tornDown += 1
                ashiria TypeError('foo')
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita

        kundi Test2(unittest.TestCase):
            tornDown = 0
            @classmethod
            eleza tearDownClass(cls):
                Test2.tornDown += 1
                ashiria TypeError('foo')
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita

        result = self.runTests(Test, Test2)
        self.assertEqual(result.testsRun, 4)
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(Test.tornDown, 1)
        self.assertEqual(Test2.tornDown, 1)

        error, _ = result.errors[0]
        self.assertEqual(str(error),
                    'tearDownClass (%s.%s)' % (__name__, Test.__qualname__))

    eleza test_class_not_torndown_when_setup_fails(self):
        kundi Test(unittest.TestCase):
            tornDown = Uongo
            @classmethod
            eleza setUpClass(cls):
                ashiria TypeError
            @classmethod
            eleza tearDownClass(cls):
                Test.tornDown = Kweli
                ashiria TypeError('foo')
            eleza test_one(self):
                pita

        self.runTests(Test)
        self.assertUongo(Test.tornDown)

    eleza test_class_not_setup_or_torndown_when_skipped(self):
        kundi Test(unittest.TestCase):
            classSetUp = Uongo
            tornDown = Uongo
            @classmethod
            eleza setUpClass(cls):
                Test.classSetUp = Kweli
            @classmethod
            eleza tearDownClass(cls):
                Test.tornDown = Kweli
            eleza test_one(self):
                pita

        Test = unittest.skip("hop")(Test)
        self.runTests(Test)
        self.assertUongo(Test.classSetUp)
        self.assertUongo(Test.tornDown)

    eleza test_setup_teardown_order_with_pathological_suite(self):
        results = []

        kundi Module1(object):
            @staticmethod
            eleza setUpModule():
                results.append('Module1.setUpModule')
            @staticmethod
            eleza tearDownModule():
                results.append('Module1.tearDownModule')

        kundi Module2(object):
            @staticmethod
            eleza setUpModule():
                results.append('Module2.setUpModule')
            @staticmethod
            eleza tearDownModule():
                results.append('Module2.tearDownModule')

        kundi Test1(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                results.append('setup 1')
            @classmethod
            eleza tearDownClass(cls):
                results.append('teardown 1')
            eleza testOne(self):
                results.append('Test1.testOne')
            eleza testTwo(self):
                results.append('Test1.testTwo')

        kundi Test2(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                results.append('setup 2')
            @classmethod
            eleza tearDownClass(cls):
                results.append('teardown 2')
            eleza testOne(self):
                results.append('Test2.testOne')
            eleza testTwo(self):
                results.append('Test2.testTwo')

        kundi Test3(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                results.append('setup 3')
            @classmethod
            eleza tearDownClass(cls):
                results.append('teardown 3')
            eleza testOne(self):
                results.append('Test3.testOne')
            eleza testTwo(self):
                results.append('Test3.testTwo')

        Test1.__module__ = Test2.__module__ = 'Module'
        Test3.__module__ = 'Module2'
        sys.modules['Module'] = Module1
        sys.modules['Module2'] = Module2

        first = unittest.TestSuite((Test1('testOne'),))
        second = unittest.TestSuite((Test1('testTwo'),))
        third = unittest.TestSuite((Test2('testOne'),))
        fourth = unittest.TestSuite((Test2('testTwo'),))
        fifth = unittest.TestSuite((Test3('testOne'),))
        sixth = unittest.TestSuite((Test3('testTwo'),))
        suite = unittest.TestSuite((first, second, third, fourth, fifth, sixth))

        runner = self.getRunner()
        result = runner.run(suite)
        self.assertEqual(result.testsRun, 6)
        self.assertEqual(len(result.errors), 0)

        self.assertEqual(results,
                         ['Module1.setUpModule', 'setup 1',
                          'Test1.testOne', 'Test1.testTwo', 'teardown 1',
                          'setup 2', 'Test2.testOne', 'Test2.testTwo',
                          'teardown 2', 'Module1.tearDownModule',
                          'Module2.setUpModule', 'setup 3',
                          'Test3.testOne', 'Test3.testTwo',
                          'teardown 3', 'Module2.tearDownModule'])

    eleza test_setup_module(self):
        kundi Module(object):
            moduleSetup = 0
            @staticmethod
            eleza setUpModule():
                Module.moduleSetup += 1

        kundi Test(unittest.TestCase):
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita
        Test.__module__ = 'Module'
        sys.modules['Module'] = Module

        result = self.runTests(Test)
        self.assertEqual(Module.moduleSetup, 1)
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.errors), 0)

    eleza test_error_in_setup_module(self):
        kundi Module(object):
            moduleSetup = 0
            moduleTornDown = 0
            @staticmethod
            eleza setUpModule():
                Module.moduleSetup += 1
                ashiria TypeError('foo')
            @staticmethod
            eleza tearDownModule():
                Module.moduleTornDown += 1

        kundi Test(unittest.TestCase):
            classSetUp = Uongo
            classTornDown = Uongo
            @classmethod
            eleza setUpClass(cls):
                Test.classSetUp = Kweli
            @classmethod
            eleza tearDownClass(cls):
                Test.classTornDown = Kweli
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita

        kundi Test2(unittest.TestCase):
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita
        Test.__module__ = 'Module'
        Test2.__module__ = 'Module'
        sys.modules['Module'] = Module

        result = self.runTests(Test, Test2)
        self.assertEqual(Module.moduleSetup, 1)
        self.assertEqual(Module.moduleTornDown, 0)
        self.assertEqual(result.testsRun, 0)
        self.assertUongo(Test.classSetUp)
        self.assertUongo(Test.classTornDown)
        self.assertEqual(len(result.errors), 1)
        error, _ = result.errors[0]
        self.assertEqual(str(error), 'setUpModule (Module)')

    eleza test_testcase_with_missing_module(self):
        kundi Test(unittest.TestCase):
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita
        Test.__module__ = 'Module'
        sys.modules.pop('Module', Tupu)

        result = self.runTests(Test)
        self.assertEqual(result.testsRun, 2)

    eleza test_teardown_module(self):
        kundi Module(object):
            moduleTornDown = 0
            @staticmethod
            eleza tearDownModule():
                Module.moduleTornDown += 1

        kundi Test(unittest.TestCase):
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita
        Test.__module__ = 'Module'
        sys.modules['Module'] = Module

        result = self.runTests(Test)
        self.assertEqual(Module.moduleTornDown, 1)
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.errors), 0)

    eleza test_error_in_teardown_module(self):
        kundi Module(object):
            moduleTornDown = 0
            @staticmethod
            eleza tearDownModule():
                Module.moduleTornDown += 1
                ashiria TypeError('foo')

        kundi Test(unittest.TestCase):
            classSetUp = Uongo
            classTornDown = Uongo
            @classmethod
            eleza setUpClass(cls):
                Test.classSetUp = Kweli
            @classmethod
            eleza tearDownClass(cls):
                Test.classTornDown = Kweli
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita

        kundi Test2(unittest.TestCase):
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita
        Test.__module__ = 'Module'
        Test2.__module__ = 'Module'
        sys.modules['Module'] = Module

        result = self.runTests(Test, Test2)
        self.assertEqual(Module.moduleTornDown, 1)
        self.assertEqual(result.testsRun, 4)
        self.assertKweli(Test.classSetUp)
        self.assertKweli(Test.classTornDown)
        self.assertEqual(len(result.errors), 1)
        error, _ = result.errors[0]
        self.assertEqual(str(error), 'tearDownModule (Module)')

    eleza test_skiptest_in_setupclass(self):
        kundi Test(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ashiria unittest.SkipTest('foo')
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita

        result = self.runTests(Test)
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.skipped), 1)
        skipped = result.skipped[0][0]
        self.assertEqual(str(skipped),
                    'setUpClass (%s.%s)' % (__name__, Test.__qualname__))

    eleza test_skiptest_in_setupmodule(self):
        kundi Test(unittest.TestCase):
            eleza test_one(self):
                pita
            eleza test_two(self):
                pita

        kundi Module(object):
            @staticmethod
            eleza setUpModule():
                ashiria unittest.SkipTest('foo')

        Test.__module__ = 'Module'
        sys.modules['Module'] = Module

        result = self.runTests(Test)
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.skipped), 1)
        skipped = result.skipped[0][0]
        self.assertEqual(str(skipped), 'setUpModule (Module)')

    eleza test_suite_debug_executes_setups_and_teardowns(self):
        ordering = []

        kundi Module(object):
            @staticmethod
            eleza setUpModule():
                ordering.append('setUpModule')
            @staticmethod
            eleza tearDownModule():
                ordering.append('tearDownModule')

        kundi Test(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ordering.append('setUpClass')
            @classmethod
            eleza tearDownClass(cls):
                ordering.append('tearDownClass')
            eleza test_something(self):
                ordering.append('test_something')

        Test.__module__ = 'Module'
        sys.modules['Module'] = Module

        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
        suite.debug()
        expectedOrder = ['setUpModule', 'setUpClass', 'test_something', 'tearDownClass', 'tearDownModule']
        self.assertEqual(ordering, expectedOrder)

    eleza test_suite_debug_propagates_exceptions(self):
        kundi Module(object):
            @staticmethod
            eleza setUpModule():
                ikiwa phase == 0:
                    ashiria Exception('setUpModule')
            @staticmethod
            eleza tearDownModule():
                ikiwa phase == 1:
                    ashiria Exception('tearDownModule')

        kundi Test(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                ikiwa phase == 2:
                    ashiria Exception('setUpClass')
            @classmethod
            eleza tearDownClass(cls):
                ikiwa phase == 3:
                    ashiria Exception('tearDownClass')
            eleza test_something(self):
                ikiwa phase == 4:
                    ashiria Exception('test_something')

        Test.__module__ = 'Module'
        sys.modules['Module'] = Module

        messages = ('setUpModule', 'tearDownModule', 'setUpClass', 'tearDownClass', 'test_something')
        kila phase, msg kwenye enumerate(messages):
            _suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
            suite = unittest.TestSuite([_suite])
            ukijumuisha self.assertRaisesRegex(Exception, msg):
                suite.debug()


ikiwa __name__ == '__main__':
    unittest.main()
