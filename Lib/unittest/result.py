"""Test result object"""

agiza io
agiza sys
agiza traceback

kutoka . agiza util
kutoka functools agiza wraps

__unittest = True

eleza failfast(method):
    @wraps(method)
    eleza inner(self, *args, **kw):
        ikiwa getattr(self, 'failfast', False):
            self.stop()
        rudisha method(self, *args, **kw)
    rudisha inner

STDOUT_LINE = '\nStdout:\n%s'
STDERR_LINE = '\nStderr:\n%s'


kundi TestResult(object):
    """Holder for test result information.

    Test results are automatically managed by the TestCase and TestSuite
    classes, and do not need to be explicitly manipulated by writers of tests.

    Each instance holds the total number of tests run, and collections of
    failures and errors that occurred among those test runs. The collections
    contain tuples of (testcase, exceptioninfo), where exceptioninfo is the
    formatted traceback of the error that occurred.
    """
    _previousTestClass = None
    _testRunEntered = False
    _moduleSetUpFailed = False
    eleza __init__(self, stream=None, descriptions=None, verbosity=None):
        self.failfast = False
        self.failures = []
        self.errors = []
        self.testsRun = 0
        self.skipped = []
        self.expectedFailures = []
        self.unexpectedSuccesses = []
        self.shouldStop = False
        self.buffer = False
        self.tb_locals = False
        self._stdout_buffer = None
        self._stderr_buffer = None
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._mirrorOutput = False

    eleza printErrors(self):
        "Called by TestRunner after test run"

    eleza startTest(self, test):
        "Called when the given test is about to be run"
        self.testsRun += 1
        self._mirrorOutput = False
        self._setupStdout()

    eleza _setupStdout(self):
        ikiwa self.buffer:
            ikiwa self._stderr_buffer is None:
                self._stderr_buffer = io.StringIO()
                self._stdout_buffer = io.StringIO()
            sys.stdout = self._stdout_buffer
            sys.stderr = self._stderr_buffer

    eleza startTestRun(self):
        """Called once before any tests are executed.

        See startTest for a method called before each test.
        """

    eleza stopTest(self, test):
        """Called when the given test has been run"""
        self._restoreStdout()
        self._mirrorOutput = False

    eleza _restoreStdout(self):
        ikiwa self.buffer:
            ikiwa self._mirrorOutput:
                output = sys.stdout.getvalue()
                error = sys.stderr.getvalue()
                ikiwa output:
                    ikiwa not output.endswith('\n'):
                        output += '\n'
                    self._original_stdout.write(STDOUT_LINE % output)
                ikiwa error:
                    ikiwa not error.endswith('\n'):
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

        See stopTest for a method called after each test.
        """

    @failfast
    eleza addError(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info().
        """
        self.errors.append((test, self._exc_info_to_string(err, test)))
        self._mirrorOutput = True

    @failfast
    eleza addFailure(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info()."""
        self.failures.append((test, self._exc_info_to_string(err, test)))
        self._mirrorOutput = True

    eleza addSubTest(self, test, subtest, err):
        """Called at the end of a subtest.
        'err' is None ikiwa the subtest ended successfully, otherwise it's a
        tuple of values as returned by sys.exc_info().
        """
        # By default, we don't do anything with successful subtests, but
        # more sophisticated test results might want to record them.
        ikiwa err is not None:
            ikiwa getattr(self, 'failfast', False):
                self.stop()
            ikiwa issubclass(err[0], test.failureException):
                errors = self.failures
            else:
                errors = self.errors
            errors.append((subtest, self._exc_info_to_string(err, test)))
            self._mirrorOutput = True

    eleza addSuccess(self, test):
        "Called when a test has completed successfully"
        pass

    eleza addSkip(self, test, reason):
        """Called when a test is skipped."""
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
        """Tells whether or not this result was a success."""
        # The hasattr check is for test_result's OldResult test.  That
        # way this method works on objects that lack the attribute.
        # (where would such result intances come kutoka? old stored pickles?)
        rudisha ((len(self.failures) == len(self.errors) == 0) and
                (not hasattr(self, 'unexpectedSuccesses') or
                 len(self.unexpectedSuccesses) == 0))

    eleza stop(self):
        """Indicates that the tests should be aborted."""
        self.shouldStop = True

    eleza _exc_info_to_string(self, err, test):
        """Converts a sys.exc_info()-style tuple of values into a string."""
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        ikiwa exctype is test.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
        else:
            length = None
        tb_e = traceback.TracebackException(
            exctype, value, tb, limit=length, capture_locals=self.tb_locals)
        msgLines = list(tb_e.format())

        ikiwa self.buffer:
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            ikiwa output:
                ikiwa not output.endswith('\n'):
                    output += '\n'
                msgLines.append(STDOUT_LINE % output)
            ikiwa error:
                ikiwa not error.endswith('\n'):
                    error += '\n'
                msgLines.append(STDERR_LINE % error)
        rudisha ''.join(msgLines)


    eleza _is_relevant_tb_level(self, tb):
        rudisha '__unittest' in tb.tb_frame.f_globals

    eleza _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        rudisha length

    eleza __repr__(self):
        rudisha ("<%s run=%i errors=%i failures=%i>" %
               (util.strclass(self.__class__), self.testsRun, len(self.errors),
                len(self.failures)))
