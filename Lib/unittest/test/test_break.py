agiza gc
agiza io
agiza os
agiza sys
agiza signal
agiza weakref

agiza unittest


@unittest.skipUnless(hasattr(os, 'kill'), "Test requires os.kill")
@unittest.skipIf(sys.platform =="win32", "Test cannot run on Windows")
kundi TestBreak(unittest.TestCase):
    int_handler = Tupu

    eleza setUp(self):
        self._default_handler = signal.getsignal(signal.SIGINT)
        ikiwa self.int_handler ni sio Tupu:
            signal.signal(signal.SIGINT, self.int_handler)

    eleza tearDown(self):
        signal.signal(signal.SIGINT, self._default_handler)
        unittest.signals._results = weakref.WeakKeyDictionary()
        unittest.signals._interrupt_handler = Tupu


    eleza testInstallHandler(self):
        default_handler = signal.getsignal(signal.SIGINT)
        unittest.installHandler()
        self.assertNotEqual(signal.getsignal(signal.SIGINT), default_handler)

        jaribu:
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)
        tatizo KeyboardInterrupt:
            self.fail("KeyboardInterrupt sio handled")

        self.assertKweli(unittest.signals._interrupt_handler.called)

    eleza testRegisterResult(self):
        result = unittest.TestResult()
        self.assertNotIn(result, unittest.signals._results)

        unittest.registerResult(result)
        jaribu:
            self.assertIn(result, unittest.signals._results)
        mwishowe:
            unittest.removeResult(result)

    eleza testInterruptCaught(self):
        default_handler = signal.getsignal(signal.SIGINT)

        result = unittest.TestResult()
        unittest.installHandler()
        unittest.registerResult(result)

        self.assertNotEqual(signal.getsignal(signal.SIGINT), default_handler)

        eleza test(result):
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)
            result.komaCaught = Kweli
            self.assertKweli(result.shouldStop)

        jaribu:
            test(result)
        tatizo KeyboardInterrupt:
            self.fail("KeyboardInterrupt sio handled")
        self.assertKweli(result.komaCaught)


    eleza testSecondInterrupt(self):
        # Can't use skipIf decorator because the signal handler may have
        # been changed after defining this method.
        ikiwa signal.getsignal(signal.SIGINT) == signal.SIG_IGN:
            self.skipTest("test requires SIGINT to sio be ignored")
        result = unittest.TestResult()
        unittest.installHandler()
        unittest.registerResult(result)

        eleza test(result):
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)
            result.komaCaught = Kweli
            self.assertKweli(result.shouldStop)
            os.kill(pid, signal.SIGINT)
            self.fail("Second KeyboardInterrupt sio ashiriad")

        jaribu:
            test(result)
        tatizo KeyboardInterrupt:
            pita
        isipokua:
            self.fail("Second KeyboardInterrupt sio ashiriad")
        self.assertKweli(result.komaCaught)


    eleza testTwoResults(self):
        unittest.installHandler()

        result = unittest.TestResult()
        unittest.registerResult(result)
        new_handler = signal.getsignal(signal.SIGINT)

        result2 = unittest.TestResult()
        unittest.registerResult(result2)
        self.assertEqual(signal.getsignal(signal.SIGINT), new_handler)

        result3 = unittest.TestResult()

        eleza test(result):
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)

        jaribu:
            test(result)
        tatizo KeyboardInterrupt:
            self.fail("KeyboardInterrupt sio handled")

        self.assertKweli(result.shouldStop)
        self.assertKweli(result2.shouldStop)
        self.assertUongo(result3.shouldStop)


    eleza testHandlerReplacedButCalled(self):
        # Can't use skipIf decorator because the signal handler may have
        # been changed after defining this method.
        ikiwa signal.getsignal(signal.SIGINT) == signal.SIG_IGN:
            self.skipTest("test requires SIGINT to sio be ignored")
        # If our handler has been replaced (is no longer installed) but is
        # called by the *new* handler, then it isn't safe to delay the
        # SIGINT na we should immediately delegate to the default handler
        unittest.installHandler()

        handler = signal.getsignal(signal.SIGINT)
        eleza new_handler(frame, signum):
            handler(frame, signum)
        signal.signal(signal.SIGINT, new_handler)

        jaribu:
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)
        tatizo KeyboardInterrupt:
            pita
        isipokua:
            self.fail("replaced but delegated handler doesn't ashiria interrupt")

    eleza testRunner(self):
        # Creating a TextTestRunner with the appropriate argument should
        # register the TextTestResult it creates
        runner = unittest.TextTestRunner(stream=io.StringIO())

        result = runner.run(unittest.TestSuite())
        self.assertIn(result, unittest.signals._results)

    eleza testWeakReferences(self):
        # Calling registerResult on a result should sio keep it alive
        result = unittest.TestResult()
        unittest.registerResult(result)

        ref = weakref.ref(result)
        toa result

        # For non-reference counting implementations
        gc.collect();gc.collect()
        self.assertIsTupu(ref())


    eleza testRemoveResult(self):
        result = unittest.TestResult()
        unittest.registerResult(result)

        unittest.installHandler()
        self.assertKweli(unittest.removeResult(result))

        # Should this ashiria an error instead?
        self.assertUongo(unittest.removeResult(unittest.TestResult()))

        jaribu:
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)
        tatizo KeyboardInterrupt:
            pita

        self.assertUongo(result.shouldStop)

    eleza testMainInstallsHandler(self):
        failfast = object()
        test = object()
        verbosity = object()
        result = object()
        default_handler = signal.getsignal(signal.SIGINT)

        kundi FakeRunner(object):
            initArgs = []
            runArgs = []
            eleza __init__(self, *args, **kwargs):
                self.initArgs.append((args, kwargs))
            eleza run(self, test):
                self.runArgs.append(test)
                rudisha result

        kundi Program(unittest.TestProgram):
            eleza __init__(self, catchkoma):
                self.exit = Uongo
                self.verbosity = verbosity
                self.failfast = failfast
                self.catchkoma = catchkoma
                self.tb_locals = Uongo
                self.testRunner = FakeRunner
                self.test = test
                self.result = Tupu

        p = Program(Uongo)
        p.runTests()

        self.assertEqual(FakeRunner.initArgs, [((), {'buffer': Tupu,
                                                     'verbosity': verbosity,
                                                     'failfast': failfast,
                                                     'tb_locals': Uongo,
                                                     'warnings': Tupu})])
        self.assertEqual(FakeRunner.runArgs, [test])
        self.assertEqual(p.result, result)

        self.assertEqual(signal.getsignal(signal.SIGINT), default_handler)

        FakeRunner.initArgs = []
        FakeRunner.runArgs = []
        p = Program(Kweli)
        p.runTests()

        self.assertEqual(FakeRunner.initArgs, [((), {'buffer': Tupu,
                                                     'verbosity': verbosity,
                                                     'failfast': failfast,
                                                     'tb_locals': Uongo,
                                                     'warnings': Tupu})])
        self.assertEqual(FakeRunner.runArgs, [test])
        self.assertEqual(p.result, result)

        self.assertNotEqual(signal.getsignal(signal.SIGINT), default_handler)

    eleza testRemoveHandler(self):
        default_handler = signal.getsignal(signal.SIGINT)
        unittest.installHandler()
        unittest.removeHandler()
        self.assertEqual(signal.getsignal(signal.SIGINT), default_handler)

        # check that calling removeHandler multiple times has no ill-effect
        unittest.removeHandler()
        self.assertEqual(signal.getsignal(signal.SIGINT), default_handler)

    eleza testRemoveHandlerAsDecorator(self):
        default_handler = signal.getsignal(signal.SIGINT)
        unittest.installHandler()

        @unittest.removeHandler
        eleza test():
            self.assertEqual(signal.getsignal(signal.SIGINT), default_handler)

        test()
        self.assertNotEqual(signal.getsignal(signal.SIGINT), default_handler)

@unittest.skipUnless(hasattr(os, 'kill'), "Test requires os.kill")
@unittest.skipIf(sys.platform =="win32", "Test cannot run on Windows")
kundi TestBreakDefaultIntHandler(TestBreak):
    int_handler = signal.default_int_handler

@unittest.skipUnless(hasattr(os, 'kill'), "Test requires os.kill")
@unittest.skipIf(sys.platform =="win32", "Test cannot run on Windows")
kundi TestBreakSignalIgnored(TestBreak):
    int_handler = signal.SIG_IGN

@unittest.skipUnless(hasattr(os, 'kill'), "Test requires os.kill")
@unittest.skipIf(sys.platform =="win32", "Test cannot run on Windows")
kundi TestBreakSignalDefault(TestBreak):
    int_handler = signal.SIG_DFL


ikiwa __name__ == "__main__":
    unittest.main()
