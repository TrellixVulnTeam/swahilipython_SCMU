"""Test result object"""

agiza io
agiza sys
agiza traceback

kutoka . agiza util
kutoka functools agiza wraps

__unittest = Kweli

eleza failfast(method):
    @wraps(method)
    eleza inner(self, *args, **kw):
        ikiwa getattr(self, 'failfast', Uongo):
            self.stop()
        rudisha method(self, *args, **kw)
    rudisha inner

STDOUT_LINE = '\nStdout:\n%s'
STDERR_LINE = '\nStderr:\n%s'


kundi TestResult(object):
    """Holder kila test result information.

    Test results are automatically managed by the TestCase na TestSuite
    classes, na do sio need to be explicitly manipulated by writers of tests.

    Each instance holds the total number of tests run, na collections of
    failures na errors that occurred among those test runs. The collections
    contain tuples of (testcase, exceptioninfo), where exceptioninfo ni the
    formatted traceback of the error that occurred.
    """
    _previousTestClass = Tupu
    _testRunEntered = Uongo
    _moduleSetUpFailed = Uongo
    eleza __init__(self, stream=Tupu, descriptions=Tupu, verbosity=Tupu):
        self.failfast = Uongo
        self.failures = []
        self.errors = []
        self.testsRun = 0
        self.skipped = []
        self.expectedFailures = []
        self.unexpectedSuccesses = []
        self.shouldStop = Uongo
        self.buffer = Uongo
        self.tb_locals = Uongo
        self._stdout_buffer = Tupu
        self._stderr_buffer = Tupu
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._mirrorOutput = Uongo

    eleza printErrors(self):
        "Called by TestRunner after test run"

    eleza startTest(self, test):
        "Called when the given test ni about to be run"
        self.testsRun += 1
        self._mirrorOutput = Uongo
        self._setupStdout()

    eleza _setupStdout(self):
        ikiwa self.buffer:
            ikiwa self._stderr_buffer ni Tupu:
                self._stderr_buffer = io.StringIO()
                self._stdout_buffer = io.StringIO()
            sys.stdout = self._stdout_buffer
            sys.stderr = self._stderr_buffer

    eleza startTestRun(self):
        """Called once before any tests are executed.

        See startTest kila a method called before each test.
        """

    eleza stopTest(self, test):
        """Called when the given test has been run"""
        self._restoreStdout()
        self._mirrorOutput = Uongo

    eleza _restoreStdout(self):
        ikiwa self.buffer:
            ikiwa self._mirrorOutput:
                output = sys.stdout.getvalue()
                error = sys.stderr.getvalue()
                ikiwa output:
                    ikiwa sio output.endswith('\n'):
                        output += '\n'
                    self._original_stdout.write(STDOUT_LINE % output)
                ikiwa error:
                    ikiwa sio error.endswith('\n'):
                        error += '\n'
                    self._original_stderr.write(STDERR_LINE % error)

            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
            self._stdout_buffer.seek(0)
            self._stdout_buffer.truncate()
            self._stderr_buffer.seek(0)
            self._stderr_buffer.truncate()

    eleza stopTestRun(self):
        """Called once after all tests are executed.

        See stopTest kila a method called after each test.
        """

    @failfast
    eleza addError(self, test, err):
        """Called when an error has occurred. 'err' ni a tuple of values as
        rudishaed by sys.exc_info().
        """
        self.errors.append((test, self._exc_info_to_string(err, test)))
        self._mirrorOutput = Kweli

    @failfast
    eleza addFailure(self, test, err):
        """Called when an error has occurred. 'err' ni a tuple of values as
        rudishaed by sys.exc_info()."""
        self.failures.append((test, self._exc_info_to_string(err, test)))
        self._mirrorOutput = Kweli

    eleza addSubTest(self, test, subtest, err):
        """Called at the end of a subtest.
        'err' ni Tupu ikiwa the subtest ended successfully, otherwise it's a
        tuple of values kama rudishaed by sys.exc_info().
        """
        # By default, we don't do anything with successful subtests, but
        # more sophisticated test results might want to record them.
        ikiwa err ni sio Tupu:
            ikiwa getattr(self, 'failfast', Uongo):
                self.stop()
            ikiwa issubclass(err[0], test.failureException):
                errors = self.failures
            isipokua:
                errors = self.errors
            errors.append((subtest, self._exc_info_to_string(err, test)))
            self._mirrorOutput = Kweli

    eleza addSuccess(self, test):
        "Called when a test has completed successfully"
        pita

    eleza addSkip(self, test, reason):
        """Called when a test ni skipped."""
        self.skipped.append((test, reason))

    eleza addExpectedFailure(self, test, err):
        """Called when an expected failure/error occurred."""
        self.expectedFailures.append(
            (test, self._exc_info_to_string(err, test)))

    @failfast
    eleza addUnexpectedSuccess(self, test):
        """Called when a test was expected to fail, but succeed."""
        self.unexpectedSuccesses.append(test)

    eleza wasSuccessful(self):
        """Tells whether ama sio this result was a success."""
        # The hasattr check ni kila test_result's OldResult test.  That
        # way this method works on objects that lack the attribute.
        # (where would such result intances come kutoka? old stored pickles?)
        rudisha ((len(self.failures) == len(self.errors) == 0) and
                (not hasattr(self, 'unexpectedSuccesses') or
                 len(self.unexpectedSuccesses) == 0))

    eleza stop(self):
        """Indicates that the tests should be aborted."""
        self.shouldStop = Kweli

    eleza _exc_info_to_string(self, err, test):
        """Converts a sys.exc_info()-style tuple of values into a string."""
        exctype, value, tb = err
        # Skip test runner traceback levels
        wakati tb na self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        ikiwa exctype ni test.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
        isipokua:
            length = Tupu
        tb_e = traceback.TracebackException(
            exctype, value, tb, limit=length, capture_locals=self.tb_locals)
        msgLines = list(tb_e.format())

        ikiwa self.buffer:
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            ikiwa output:
                ikiwa sio output.endswith('\n'):
                    output += '\n'
                msgLines.append(STDOUT_LINE % output)
            ikiwa error:
                ikiwa sio error.endswith('\n'):
                    error += '\n'
                msgLines.append(STDERR_LINE % error)
        rudisha ''.join(msgLines)


    eleza _is_relevant_tb_level(self, tb):
        rudisha '__unittest' kwenye tb.tb_frame.f_globals

    eleza _count_relevant_tb_levels(self, tb):
        length = 0
        wakati tb na sio self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        rudisha length

    eleza __repr__(self):
        rudisha ("<%s run=%i errors=%i failures=%i>" %
               (util.strclass(self.__class__), self.testsRun, len(self.errors),
                len(self.failures)))
