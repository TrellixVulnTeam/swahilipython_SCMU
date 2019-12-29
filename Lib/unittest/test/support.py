agiza unittest


kundi TestEquality(object):
    """Used kama a mixin kila TestCase"""

    # Check kila a valid __eq__ implementation
    eleza test_eq(self):
        kila obj_1, obj_2 kwenye self.eq_pairs:
            self.assertEqual(obj_1, obj_2)
            self.assertEqual(obj_2, obj_1)

    # Check kila a valid __ne__ implementation
    eleza test_ne(self):
        kila obj_1, obj_2 kwenye self.ne_pairs:
            self.assertNotEqual(obj_1, obj_2)
            self.assertNotEqual(obj_2, obj_1)

kundi TestHashing(object):
    """Used kama a mixin kila TestCase"""

    # Check kila a valid __hash__ implementation
    eleza test_hash(self):
        kila obj_1, obj_2 kwenye self.eq_pairs:
            jaribu:
                ikiwa sio hash(obj_1) == hash(obj_2):
                    self.fail("%r na %r do sio hash equal" % (obj_1, obj_2))
            tatizo Exception kama e:
                self.fail("Problem hashing %r na %r: %s" % (obj_1, obj_2, e))

        kila obj_1, obj_2 kwenye self.ne_pairs:
            jaribu:
                ikiwa hash(obj_1) == hash(obj_2):
                    self.fail("%s na %s hash equal, but shouldn't" %
                              (obj_1, obj_2))
            tatizo Exception kama e:
                self.fail("Problem hashing %s na %s: %s" % (obj_1, obj_2, e))


kundi _BaseLoggingResult(unittest.TestResult):
    eleza __init__(self, log):
        self._events = log
        super().__init__()

    eleza startTest(self, test):
        self._events.append('startTest')
        super().startTest(test)

    eleza startTestRun(self):
        self._events.append('startTestRun')
        super().startTestRun()

    eleza stopTest(self, test):
        self._events.append('stopTest')
        super().stopTest(test)

    eleza stopTestRun(self):
        self._events.append('stopTestRun')
        super().stopTestRun()

    eleza addFailure(self, *args):
        self._events.append('addFailure')
        super().addFailure(*args)

    eleza addSuccess(self, *args):
        self._events.append('addSuccess')
        super().addSuccess(*args)

    eleza addError(self, *args):
        self._events.append('addError')
        super().addError(*args)

    eleza addSkip(self, *args):
        self._events.append('addSkip')
        super().addSkip(*args)

    eleza addExpectedFailure(self, *args):
        self._events.append('addExpectedFailure')
        super().addExpectedFailure(*args)

    eleza addUnexpectedSuccess(self, *args):
        self._events.append('addUnexpectedSuccess')
        super().addUnexpectedSuccess(*args)


kundi LegacyLoggingResult(_BaseLoggingResult):
    """
    A legacy TestResult implementation, without an addSubTest method,
    which records its method calls.
    """

    @property
    eleza addSubTest(self):
        ashiria AttributeError


kundi LoggingResult(_BaseLoggingResult):
    """
    A TestResult implementation which records its method calls.
    """

    eleza addSubTest(self, test, subtest, err):
        ikiwa err ni Tupu:
            self._events.append('addSubTestSuccess')
        isipokua:
            self._events.append('addSubTestFailure')
        super().addSubTest(test, subtest, err)


kundi ResultWithNoStartTestRunStopTestRun(object):
    """An object honouring TestResult before startTestRun/stopTestRun."""

    eleza __init__(self):
        self.failures = []
        self.errors = []
        self.testsRun = 0
        self.skipped = []
        self.expectedFailures = []
        self.unexpectedSuccesses = []
        self.shouldStop = Uongo

    eleza startTest(self, test):
        pita

    eleza stopTest(self, test):
        pita

    eleza addError(self, test):
        pita

    eleza addFailure(self, test):
        pita

    eleza addSuccess(self, test):
        pita

    eleza wasSuccessful(self):
        rudisha Kweli
