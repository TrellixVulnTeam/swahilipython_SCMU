"""Running tests"""

agiza sys
agiza time
agiza warnings

kutoka . agiza result
kutoka .signals agiza registerResult

__unittest = True


kundi _WritelnDecorator(object):
    """Used to decorate file-like objects with a handy 'writeln' method"""
    eleza __init__(self,stream):
        self.stream = stream

    eleza __getattr__(self, attr):
        ikiwa attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        rudisha getattr(self.stream,attr)

    eleza writeln(self, arg=None):
        ikiwa arg:
            self.write(arg)
        self.write('\n') # text-mode streams translate to \r\n ikiwa needed


kundi TextTestResult(result.TestResult):
    """A test result kundi that can print formatted text results to a stream.

    Used by TextTestRunner.
    """
    separator1 = '=' * 70
    separator2 = '-' * 70

    eleza __init__(self, stream, descriptions, verbosity):
        super(TextTestResult, self).__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions

    eleza getDescription(self, test):
        doc_first_line = test.shortDescription()
        ikiwa self.descriptions and doc_first_line:
            rudisha '\n'.join((str(test), doc_first_line))
        else:
            rudisha str(test)

    eleza startTest(self, test):
        super(TextTestResult, self).startTest(test)
        ikiwa self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.write(" ... ")
            self.stream.flush()

    eleza addSuccess(self, test):
        super(TextTestResult, self).addSuccess(test)
        ikiwa self.showAll:
            self.stream.writeln("ok")
        elikiwa self.dots:
            self.stream.write('.')
            self.stream.flush()

    eleza addError(self, test, err):
        super(TextTestResult, self).addError(test, err)
        ikiwa self.showAll:
            self.stream.writeln("ERROR")
        elikiwa self.dots:
            self.stream.write('E')
            self.stream.flush()

    eleza addFailure(self, test, err):
        super(TextTestResult, self).addFailure(test, err)
        ikiwa self.showAll:
            self.stream.writeln("FAIL")
        elikiwa self.dots:
            self.stream.write('F')
            self.stream.flush()

    eleza addSkip(self, test, reason):
        super(TextTestResult, self).addSkip(test, reason)
        ikiwa self.showAll:
            self.stream.writeln("skipped {0!r}".format(reason))
        elikiwa self.dots:
            self.stream.write("s")
            self.stream.flush()

    eleza addExpectedFailure(self, test, err):
        super(TextTestResult, self).addExpectedFailure(test, err)
        ikiwa self.showAll:
            self.stream.writeln("expected failure")
        elikiwa self.dots:
            self.stream.write("x")
            self.stream.flush()

    eleza addUnexpectedSuccess(self, test):
        super(TextTestResult, self).addUnexpectedSuccess(test)
        ikiwa self.showAll:
            self.stream.writeln("unexpected success")
        elikiwa self.dots:
            self.stream.write("u")
            self.stream.flush()

    eleza printErrors(self):
        ikiwa self.dots or self.showAll:
            self.stream.writeln()
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

    eleza printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (flavour,self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln("%s" % err)


kundi TextTestRunner(object):
    """A test runner kundi that displays results in textual form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """
    resultkundi = TextTestResult

    eleza __init__(self, stream=None, descriptions=True, verbosity=1,
                 failfast=False, buffer=False, resultclass=None, warnings=None,
                 *, tb_locals=False):
        """Construct a TextTestRunner.

        Subclasses should accept **kwargs to ensure compatibility as the
        interface changes.
        """
        ikiwa stream is None:
            stream = sys.stderr
        self.stream = _WritelnDecorator(stream)
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.buffer = buffer
        self.tb_locals = tb_locals
        self.warnings = warnings
        ikiwa resultkundi is not None:
            self.resultkundi = resultclass

    eleza _makeResult(self):
        rudisha self.resultclass(self.stream, self.descriptions, self.verbosity)

    eleza run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        result.tb_locals = self.tb_locals
        with warnings.catch_warnings():
            ikiwa self.warnings:
                # ikiwa self.warnings is set, use it to filter all the warnings
                warnings.simplefilter(self.warnings)
                # ikiwa the filter is 'default' or 'always', special-case the
                # warnings kutoka the deprecated unittest methods to show them
                # no more than once per module, because they can be fairly
                # noisy.  The -Wd and -Wa flags can be used to bypass this
                # only when self.warnings is None.
                ikiwa self.warnings in ['default', 'always']:
                    warnings.filterwarnings('module',
                            category=DeprecationWarning,
                            message=r'Please use assert\w+ instead.')
            startTime = time.perf_counter()
            startTestRun = getattr(result, 'startTestRun', None)
            ikiwa startTestRun is not None:
                startTestRun()
            try:
                test(result)
            finally:
                stopTestRun = getattr(result, 'stopTestRun', None)
                ikiwa stopTestRun is not None:
                    stopTestRun()
            stopTime = time.perf_counter()
        timeTaken = stopTime - startTime
        result.printErrors()
        ikiwa hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run != 1 and "s" or "", timeTaken))
        self.stream.writeln()

        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        ikiwa not result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = len(result.failures), len(result.errors)
            ikiwa failed:
                infos.append("failures=%d" % failed)
            ikiwa errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("OK")
        ikiwa skipped:
            infos.append("skipped=%d" % skipped)
        ikiwa expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        ikiwa unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        ikiwa infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        rudisha result
