"""Test cases for traceback module"""

kutoka collections agiza namedtuple
kutoka io agiza StringIO
agiza linecache
agiza sys
agiza unittest
agiza re
kutoka test agiza support
kutoka test.support agiza TESTFN, Error, captured_output, unlink, cpython_only
kutoka test.support.script_helper agiza assert_python_ok
agiza textwrap

agiza traceback


test_code = namedtuple('code', ['co_filename', 'co_name'])
test_frame = namedtuple('frame', ['f_code', 'f_globals', 'f_locals'])
test_tb = namedtuple('tb', ['tb_frame', 'tb_lineno', 'tb_next'])


kundi TracebackCases(unittest.TestCase):
    # For now, a very minimal set of tests.  I want to be sure that
    # formatting of SyntaxErrors works based on changes for 2.1.

    eleza get_exception_format(self, func, exc):
        try:
            func()
        except exc as value:
            rudisha traceback.format_exception_only(exc, value)
        else:
            raise ValueError("call did not raise exception")

    eleza syntax_error_with_caret(self):
        compile("eleza fact(x):\n\trudisha x!\n", "?", "exec")

    eleza syntax_error_with_caret_2(self):
        compile("1 +\n", "?", "exec")

    eleza syntax_error_bad_indentation(self):
        compile("eleza spam():\n  andika(1)\n andika(2)", "?", "exec")

    eleza syntax_error_with_caret_non_ascii(self):
        compile('Python = "\u1e54\xfd\u0163\u0125\xf2\xf1" +', "?", "exec")

    eleza syntax_error_bad_indentation2(self):
        compile(" andika(2)", "?", "exec")

    eleza test_caret(self):
        err = self.get_exception_format(self.syntax_error_with_caret,
                                        SyntaxError)
        self.assertEqual(len(err), 4)
        self.assertTrue(err[1].strip() == "rudisha x!")
        self.assertIn("^", err[2]) # third line has caret
        self.assertEqual(err[1].find("!"), err[2].find("^")) # in the right place

        err = self.get_exception_format(self.syntax_error_with_caret_2,
                                        SyntaxError)
        self.assertIn("^", err[2]) # third line has caret
        self.assertEqual(err[2].count('\n'), 1)   # and no additional newline
        self.assertEqual(err[1].find("+"), err[2].find("^"))  # in the right place

        err = self.get_exception_format(self.syntax_error_with_caret_non_ascii,
                                        SyntaxError)
        self.assertIn("^", err[2]) # third line has caret
        self.assertEqual(err[2].count('\n'), 1)   # and no additional newline
        self.assertEqual(err[1].find("+"), err[2].find("^"))  # in the right place

    eleza test_nocaret(self):
        exc = SyntaxError("error", ("x.py", 23, None, "bad syntax"))
        err = traceback.format_exception_only(SyntaxError, exc)
        self.assertEqual(len(err), 3)
        self.assertEqual(err[1].strip(), "bad syntax")

    eleza test_bad_indentation(self):
        err = self.get_exception_format(self.syntax_error_bad_indentation,
                                        IndentationError)
        self.assertEqual(len(err), 4)
        self.assertEqual(err[1].strip(), "andika(2)")
        self.assertIn("^", err[2])
        self.assertEqual(err[1].find(")"), err[2].find("^"))

        err = self.get_exception_format(self.syntax_error_bad_indentation2,
                                        IndentationError)
        self.assertEqual(len(err), 4)
        self.assertEqual(err[1].strip(), "andika(2)")
        self.assertIn("^", err[2])
        self.assertEqual(err[1].find("p"), err[2].find("^"))

    eleza test_base_exception(self):
        # Test that exceptions derived kutoka BaseException are formatted right
        e = KeyboardInterrupt()
        lst = traceback.format_exception_only(e.__class__, e)
        self.assertEqual(lst, ['KeyboardInterrupt\n'])

    eleza test_format_exception_only_bad__str__(self):
        kundi X(Exception):
            eleza __str__(self):
                1/0
        err = traceback.format_exception_only(X, X())
        self.assertEqual(len(err), 1)
        str_value = '<unprintable %s object>' % X.__name__
        ikiwa X.__module__ in ('__main__', 'builtins'):
            str_name = X.__qualname__
        else:
            str_name = '.'.join([X.__module__, X.__qualname__])
        self.assertEqual(err[0], "%s: %s\n" % (str_name, str_value))

    eleza test_encoded_file(self):
        # Test that tracebacks are correctly printed for encoded source files:
        # - correct line number (Issue2384)
        # - respect file encoding (Issue3975)
        agiza sys, subprocess

        # The spawned subprocess has its stdout redirected to a PIPE, and its
        # encoding may be different kutoka the current interpreter, on Windows
        # at least.
        process = subprocess.Popen([sys.executable, "-c",
                                    "agiza sys; andika(sys.stdout.encoding)"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()
        output_encoding = str(stdout, 'ascii').splitlines()[0]

        eleza do_test(firstlines, message, charset, lineno):
            # Raise the message in a subprocess, and catch the output
            try:
                with open(TESTFN, "w", encoding=charset) as output:
                    output.write("""{0}ikiwa 1:
                        agiza traceback;
                        raise RuntimeError('{1}')
                        """.format(firstlines, message))

                process = subprocess.Popen([sys.executable, TESTFN],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                stdout, stderr = process.communicate()
                stdout = stdout.decode(output_encoding).splitlines()
            finally:
                unlink(TESTFN)

            # The source lines are encoded with the 'backslashreplace' handler
            encoded_message = message.encode(output_encoding,
                                             'backslashreplace')
            # and we just decoded them with the output_encoding.
            message_ascii = encoded_message.decode(output_encoding)

            err_line = "raise RuntimeError('{0}')".format(message_ascii)
            err_msg = "RuntimeError: {0}".format(message_ascii)

            self.assertIn(("line %s" % lineno), stdout[1],
                "Invalid line number: {0!r} instead of {1}".format(
                    stdout[1], lineno))
            self.assertTrue(stdout[2].endswith(err_line),
                "Invalid traceback line: {0!r} instead of {1!r}".format(
                    stdout[2], err_line))
            self.assertTrue(stdout[3] == err_msg,
                "Invalid error message: {0!r} instead of {1!r}".format(
                    stdout[3], err_msg))

        do_test("", "foo", "ascii", 3)
        for charset in ("ascii", "iso-8859-1", "utf-8", "GBK"):
            ikiwa charset == "ascii":
                text = "foo"
            elikiwa charset == "GBK":
                text = "\u4E02\u5100"
            else:
                text = "h\xe9 ho"
            do_test("# coding: {0}\n".format(charset),
                    text, charset, 4)
            do_test("#!shebang\n# coding: {0}\n".format(charset),
                    text, charset, 5)
            do_test(" \t\f\n# coding: {0}\n".format(charset),
                    text, charset, 5)
        # Issue #18960: coding spec should have no effect
        do_test("x=0\n# coding: GBK\n", "h\xe9 ho", 'utf-8', 5)

    @support.requires_type_collecting
    eleza test_print_traceback_at_exit(self):
        # Issue #22599: Ensure that it is possible to use the traceback module
        # to display an exception at Python exit
        code = textwrap.dedent("""
            agiza sys
            agiza traceback

            kundi PrintExceptionAtExit(object):
                eleza __init__(self):
                    try:
                        x = 1 / 0
                    except Exception:
                        self.exc_info = sys.exc_info()
                        # self.exc_info[1] (traceback) contains frames:
                        # explicitly clear the reference to self in the current
                        # frame to break a reference cycle
                        self = None

                eleza __del__(self):
                    traceback.print_exception(*self.exc_info)

            # Keep a reference in the module namespace to call the destructor
            # when the module is unloaded
            obj = PrintExceptionAtExit()
        """)
        rc, stdout, stderr = assert_python_ok('-c', code)
        expected = [b'Traceback (most recent call last):',
                    b'  File "<string>", line 8, in __init__',
                    b'ZeroDivisionError: division by zero']
        self.assertEqual(stderr.splitlines(), expected)

    eleza test_print_exception(self):
        output = StringIO()
        traceback.print_exception(
            Exception, Exception("projector"), None, file=output
        )
        self.assertEqual(output.getvalue(), "Exception: projector\n")


kundi TracebackFormatTests(unittest.TestCase):

    eleza some_exception(self):
        raise KeyError('blah')

    @cpython_only
    eleza check_traceback_format(self, cleanup_func=None):
        kutoka _testcapi agiza traceback_print
        try:
            self.some_exception()
        except KeyError:
            type_, value, tb = sys.exc_info()
            ikiwa cleanup_func is not None:
                # Clear the inner frames, not this one
                cleanup_func(tb.tb_next)
            traceback_fmt = 'Traceback (most recent call last):\n' + \
                            ''.join(traceback.format_tb(tb))
            file_ = StringIO()
            traceback_andika(tb, file_)
            python_fmt  = file_.getvalue()
            # Call all _tb and _exc functions
            with captured_output("stderr") as tbstderr:
                traceback.print_tb(tb)
            tbfile = StringIO()
            traceback.print_tb(tb, file=tbfile)
            with captured_output("stderr") as excstderr:
                traceback.print_exc()
            excfmt = traceback.format_exc()
            excfile = StringIO()
            traceback.print_exc(file=excfile)
        else:
            raise Error("unable to create test traceback string")

        # Make sure that Python and the traceback module format the same thing
        self.assertEqual(traceback_fmt, python_fmt)
        # Now verify the _tb func output
        self.assertEqual(tbstderr.getvalue(), tbfile.getvalue())
        # Now verify the _exc func output
        self.assertEqual(excstderr.getvalue(), excfile.getvalue())
        self.assertEqual(excfmt, excfile.getvalue())

        # Make sure that the traceback is properly indented.
        tb_lines = python_fmt.splitlines()
        self.assertEqual(len(tb_lines), 5)
        banner = tb_lines[0]
        location, source_line = tb_lines[-2:]
        self.assertTrue(banner.startswith('Traceback'))
        self.assertTrue(location.startswith('  File'))
        self.assertTrue(source_line.startswith('    raise'))

    eleza test_traceback_format(self):
        self.check_traceback_format()

    eleza test_traceback_format_with_cleared_frames(self):
        # Check that traceback formatting also works with a clear()ed frame
        eleza cleanup_tb(tb):
            tb.tb_frame.clear()
        self.check_traceback_format(cleanup_tb)

    eleza test_stack_format(self):
        # Verify _stack functions. Note we have to use _getframe(1) to
        # compare them without this frame appearing in the output
        with captured_output("stderr") as ststderr:
            traceback.print_stack(sys._getframe(1))
        stfile = StringIO()
        traceback.print_stack(sys._getframe(1), file=stfile)
        self.assertEqual(ststderr.getvalue(), stfile.getvalue())

        stfmt = traceback.format_stack(sys._getframe(1))

        self.assertEqual(ststderr.getvalue(), "".join(stfmt))

    eleza test_print_stack(self):
        eleza prn():
            traceback.print_stack()
        with captured_output("stderr") as stderr:
            prn()
        lineno = prn.__code__.co_firstlineno
        self.assertEqual(stderr.getvalue().splitlines()[-4:], [
            '  File "%s", line %d, in test_print_stack' % (__file__, lineno+3),
            '    prn()',
            '  File "%s", line %d, in prn' % (__file__, lineno+1),
            '    traceback.print_stack()',
        ])

    # issue 26823 - Shrink recursive tracebacks
    eleza _check_recursive_traceback_display(self, render_exc):
        # Always show full diffs when this test fails
        # Note that rearranging things may require adjusting
        # the relative line numbers in the expected tracebacks
        self.maxDiff = None

        # Check hitting the recursion limit
        eleza f():
            f()

        with captured_output("stderr") as stderr_f:
            try:
                f()
            except RecursionError as exc:
                render_exc()
            else:
                self.fail("no recursion occurred")

        lineno_f = f.__code__.co_firstlineno
        result_f = (
            'Traceback (most recent call last):\n'
            f'  File "{__file__}", line {lineno_f+5}, in _check_recursive_traceback_display\n'
            '    f()\n'
            f'  File "{__file__}", line {lineno_f+1}, in f\n'
            '    f()\n'
            f'  File "{__file__}", line {lineno_f+1}, in f\n'
            '    f()\n'
            f'  File "{__file__}", line {lineno_f+1}, in f\n'
            '    f()\n'
            # XXX: The following line changes depending on whether the tests
            # are run through the interactive interpreter or with -m
            # It also varies depending on the platform (stack size)
            # Fortunately, we don't care about exactness here, so we use regex
            r'  \[Previous line repeated (\d+) more times\]' '\n'
            'RecursionError: maximum recursion depth exceeded\n'
        )

        expected = result_f.splitlines()
        actual = stderr_f.getvalue().splitlines()

        # Check the output text matches expectations
        # 2nd last line contains the repetition count
        self.assertEqual(actual[:-2], expected[:-2])
        self.assertRegex(actual[-2], expected[-2])
        # last line can have additional text appended
        self.assertIn(expected[-1], actual[-1])

        # Check the recursion count is roughly as expected
        rec_limit = sys.getrecursionlimit()
        self.assertIn(int(re.search(r"\d+", actual[-2]).group()), range(rec_limit-60, rec_limit))

        # Check a known (limited) number of recursive invocations
        eleza g(count=10):
            ikiwa count:
                rudisha g(count-1)
            raise ValueError

        with captured_output("stderr") as stderr_g:
            try:
                g()
            except ValueError as exc:
                render_exc()
            else:
                self.fail("no value error was raised")

        lineno_g = g.__code__.co_firstlineno
        result_g = (
            f'  File "{__file__}", line {lineno_g+2}, in g\n'
            '    rudisha g(count-1)\n'
            f'  File "{__file__}", line {lineno_g+2}, in g\n'
            '    rudisha g(count-1)\n'
            f'  File "{__file__}", line {lineno_g+2}, in g\n'
            '    rudisha g(count-1)\n'
            '  [Previous line repeated 7 more times]\n'
            f'  File "{__file__}", line {lineno_g+3}, in g\n'
            '    raise ValueError\n'
            'ValueError\n'
        )
        tb_line = (
            'Traceback (most recent call last):\n'
            f'  File "{__file__}", line {lineno_g+7}, in _check_recursive_traceback_display\n'
            '    g()\n'
        )
        expected = (tb_line + result_g).splitlines()
        actual = stderr_g.getvalue().splitlines()
        self.assertEqual(actual, expected)

        # Check 2 different repetitive sections
        eleza h(count=10):
            ikiwa count:
                rudisha h(count-1)
            g()

        with captured_output("stderr") as stderr_h:
            try:
                h()
            except ValueError as exc:
                render_exc()
            else:
                self.fail("no value error was raised")

        lineno_h = h.__code__.co_firstlineno
        result_h = (
            'Traceback (most recent call last):\n'
            f'  File "{__file__}", line {lineno_h+7}, in _check_recursive_traceback_display\n'
            '    h()\n'
            f'  File "{__file__}", line {lineno_h+2}, in h\n'
            '    rudisha h(count-1)\n'
            f'  File "{__file__}", line {lineno_h+2}, in h\n'
            '    rudisha h(count-1)\n'
            f'  File "{__file__}", line {lineno_h+2}, in h\n'
            '    rudisha h(count-1)\n'
            '  [Previous line repeated 7 more times]\n'
            f'  File "{__file__}", line {lineno_h+3}, in h\n'
            '    g()\n'
        )
        expected = (result_h + result_g).splitlines()
        actual = stderr_h.getvalue().splitlines()
        self.assertEqual(actual, expected)

        # Check the boundary conditions. First, test just below the cutoff.
        with captured_output("stderr") as stderr_g:
            try:
                g(traceback._RECURSIVE_CUTOFF)
            except ValueError as exc:
                render_exc()
            else:
                self.fail("no error raised")
        result_g = (
            f'  File "{__file__}", line {lineno_g+2}, in g\n'
            '    rudisha g(count-1)\n'
            f'  File "{__file__}", line {lineno_g+2}, in g\n'
            '    rudisha g(count-1)\n'
            f'  File "{__file__}", line {lineno_g+2}, in g\n'
            '    rudisha g(count-1)\n'
            f'  File "{__file__}", line {lineno_g+3}, in g\n'
            '    raise ValueError\n'
            'ValueError\n'
        )
        tb_line = (
            'Traceback (most recent call last):\n'
            f'  File "{__file__}", line {lineno_g+71}, in _check_recursive_traceback_display\n'
            '    g(traceback._RECURSIVE_CUTOFF)\n'
        )
        expected = (tb_line + result_g).splitlines()
        actual = stderr_g.getvalue().splitlines()
        self.assertEqual(actual, expected)

        # Second, test just above the cutoff.
        with captured_output("stderr") as stderr_g:
            try:
                g(traceback._RECURSIVE_CUTOFF + 1)
            except ValueError as exc:
                render_exc()
            else:
                self.fail("no error raised")
        result_g = (
            f'  File "{__file__}", line {lineno_g+2}, in g\n'
            '    rudisha g(count-1)\n'
            f'  File "{__file__}", line {lineno_g+2}, in g\n'
            '    rudisha g(count-1)\n'
            f'  File "{__file__}", line {lineno_g+2}, in g\n'
            '    rudisha g(count-1)\n'
            '  [Previous line repeated 1 more time]\n'
            f'  File "{__file__}", line {lineno_g+3}, in g\n'
            '    raise ValueError\n'
            'ValueError\n'
        )
        tb_line = (
            'Traceback (most recent call last):\n'
            f'  File "{__file__}", line {lineno_g+99}, in _check_recursive_traceback_display\n'
            '    g(traceback._RECURSIVE_CUTOFF + 1)\n'
        )
        expected = (tb_line + result_g).splitlines()
        actual = stderr_g.getvalue().splitlines()
        self.assertEqual(actual, expected)

    eleza test_recursive_traceback_python(self):
        self._check_recursive_traceback_display(traceback.print_exc)

    @cpython_only
    eleza test_recursive_traceback_cpython_internal(self):
        kutoka _testcapi agiza exception_print
        eleza render_exc():
            exc_type, exc_value, exc_tb = sys.exc_info()
            exception_andika(exc_value)
        self._check_recursive_traceback_display(render_exc)

    eleza test_format_stack(self):
        eleza fmt():
            rudisha traceback.format_stack()
        result = fmt()
        lineno = fmt.__code__.co_firstlineno
        self.assertEqual(result[-2:], [
            '  File "%s", line %d, in test_format_stack\n'
            '    result = fmt()\n' % (__file__, lineno+2),
            '  File "%s", line %d, in fmt\n'
            '    rudisha traceback.format_stack()\n' % (__file__, lineno+1),
        ])

    @cpython_only
    eleza test_unhashable(self):
        kutoka _testcapi agiza exception_print

        kundi UnhashableException(Exception):
            eleza __eq__(self, other):
                rudisha True

        ex1 = UnhashableException('ex1')
        ex2 = UnhashableException('ex2')
        try:
            raise ex2 kutoka ex1
        except UnhashableException:
            try:
                raise ex1
            except UnhashableException:
                exc_type, exc_val, exc_tb = sys.exc_info()

        with captured_output("stderr") as stderr_f:
            exception_andika(exc_val)

        tb = stderr_f.getvalue().strip().splitlines()
        self.assertEqual(11, len(tb))
        self.assertEqual(context_message.strip(), tb[5])
        self.assertIn('UnhashableException: ex2', tb[3])
        self.assertIn('UnhashableException: ex1', tb[10])


cause_message = (
    "\nThe above exception was the direct cause "
    "of the following exception:\n\n")

context_message = (
    "\nDuring handling of the above exception, "
    "another exception occurred:\n\n")

boundaries = re.compile(
    '(%s|%s)' % (re.escape(cause_message), re.escape(context_message)))


kundi BaseExceptionReportingTests:

    eleza get_exception(self, exception_or_callable):
        ikiwa isinstance(exception_or_callable, Exception):
            rudisha exception_or_callable
        try:
            exception_or_callable()
        except Exception as e:
            rudisha e

    eleza zero_div(self):
        1/0 # In zero_div

    eleza check_zero_div(self, msg):
        lines = msg.splitlines()
        self.assertTrue(lines[-3].startswith('  File'))
        self.assertIn('1/0 # In zero_div', lines[-2])
        self.assertTrue(lines[-1].startswith('ZeroDivisionError'), lines[-1])

    eleza test_simple(self):
        try:
            1/0 # Marker
        except ZeroDivisionError as _:
            e = _
        lines = self.get_report(e).splitlines()
        self.assertEqual(len(lines), 4)
        self.assertTrue(lines[0].startswith('Traceback'))
        self.assertTrue(lines[1].startswith('  File'))
        self.assertIn('1/0 # Marker', lines[2])
        self.assertTrue(lines[3].startswith('ZeroDivisionError'))

    eleza test_cause(self):
        eleza inner_raise():
            try:
                self.zero_div()
            except ZeroDivisionError as e:
                raise KeyError kutoka e
        eleza outer_raise():
            inner_raise() # Marker
        blocks = boundaries.split(self.get_report(outer_raise))
        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[1], cause_message)
        self.check_zero_div(blocks[0])
        self.assertIn('inner_raise() # Marker', blocks[2])

    eleza test_context(self):
        eleza inner_raise():
            try:
                self.zero_div()
            except ZeroDivisionError:
                raise KeyError
        eleza outer_raise():
            inner_raise() # Marker
        blocks = boundaries.split(self.get_report(outer_raise))
        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[1], context_message)
        self.check_zero_div(blocks[0])
        self.assertIn('inner_raise() # Marker', blocks[2])

    eleza test_context_suppression(self):
        try:
            try:
                raise Exception
            except:
                raise ZeroDivisionError kutoka None
        except ZeroDivisionError as _:
            e = _
        lines = self.get_report(e).splitlines()
        self.assertEqual(len(lines), 4)
        self.assertTrue(lines[0].startswith('Traceback'))
        self.assertTrue(lines[1].startswith('  File'))
        self.assertIn('ZeroDivisionError kutoka None', lines[2])
        self.assertTrue(lines[3].startswith('ZeroDivisionError'))

    eleza test_cause_and_context(self):
        # When both a cause and a context are set, only the cause should be
        # displayed and the context should be muted.
        eleza inner_raise():
            try:
                self.zero_div()
            except ZeroDivisionError as _e:
                e = _e
            try:
                xyzzy
            except NameError:
                raise KeyError kutoka e
        eleza outer_raise():
            inner_raise() # Marker
        blocks = boundaries.split(self.get_report(outer_raise))
        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[1], cause_message)
        self.check_zero_div(blocks[0])
        self.assertIn('inner_raise() # Marker', blocks[2])

    eleza test_cause_recursive(self):
        eleza inner_raise():
            try:
                try:
                    self.zero_div()
                except ZeroDivisionError as e:
                    z = e
                    raise KeyError kutoka e
            except KeyError as e:
                raise z kutoka e
        eleza outer_raise():
            inner_raise() # Marker
        blocks = boundaries.split(self.get_report(outer_raise))
        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[1], cause_message)
        # The first block is the KeyError raised kutoka the ZeroDivisionError
        self.assertIn('raise KeyError kutoka e', blocks[0])
        self.assertNotIn('1/0', blocks[0])
        # The second block (apart kutoka the boundary) is the ZeroDivisionError
        # re-raised kutoka the KeyError
        self.assertIn('inner_raise() # Marker', blocks[2])
        self.check_zero_div(blocks[2])

    eleza test_syntax_error_offset_at_eol(self):
        # See #10186.
        eleza e():
            raise SyntaxError('', ('', 0, 5, 'hello'))
        msg = self.get_report(e).splitlines()
        self.assertEqual(msg[-2], "        ^")
        eleza e():
            exec("x = 5 | 4 |")
        msg = self.get_report(e).splitlines()
        self.assertEqual(msg[-2], '              ^')

    eleza test_message_none(self):
        # A message that looks like "None" should not be treated specially
        err = self.get_report(Exception(None))
        self.assertIn('Exception: None\n', err)
        err = self.get_report(Exception('None'))
        self.assertIn('Exception: None\n', err)
        err = self.get_report(Exception())
        self.assertIn('Exception\n', err)
        err = self.get_report(Exception(''))
        self.assertIn('Exception\n', err)


kundi PyExcReportingTests(BaseExceptionReportingTests, unittest.TestCase):
    #
    # This checks reporting through the 'traceback' module, with both
    # format_exception() and print_exception().
    #

    eleza get_report(self, e):
        e = self.get_exception(e)
        s = ''.join(
            traceback.format_exception(type(e), e, e.__traceback__))
        with captured_output("stderr") as sio:
            traceback.print_exception(type(e), e, e.__traceback__)
        self.assertEqual(sio.getvalue(), s)
        rudisha s


kundi CExcReportingTests(BaseExceptionReportingTests, unittest.TestCase):
    #
    # This checks built-in reporting by the interpreter.
    #

    @cpython_only
    eleza get_report(self, e):
        kutoka _testcapi agiza exception_print
        e = self.get_exception(e)
        with captured_output("stderr") as s:
            exception_andika(e)
        rudisha s.getvalue()


kundi LimitTests(unittest.TestCase):

    ''' Tests for limit argument.
        It's enough to test extact_tb, extract_stack and format_exception '''

    eleza last_raises1(self):
        raise Exception('Last raised')

    eleza last_raises2(self):
        self.last_raises1()

    eleza last_raises3(self):
        self.last_raises2()

    eleza last_raises4(self):
        self.last_raises3()

    eleza last_raises5(self):
        self.last_raises4()

    eleza last_returns_frame1(self):
        rudisha sys._getframe()

    eleza last_returns_frame2(self):
        rudisha self.last_returns_frame1()

    eleza last_returns_frame3(self):
        rudisha self.last_returns_frame2()

    eleza last_returns_frame4(self):
        rudisha self.last_returns_frame3()

    eleza last_returns_frame5(self):
        rudisha self.last_returns_frame4()

    eleza test_extract_stack(self):
        frame = self.last_returns_frame5()
        eleza extract(**kwargs):
            rudisha traceback.extract_stack(frame, **kwargs)
        eleza assertEqualExcept(actual, expected, ignore):
            self.assertEqual(actual[:ignore], expected[:ignore])
            self.assertEqual(actual[ignore+1:], expected[ignore+1:])
            self.assertEqual(len(actual), len(expected))

        with support.swap_attr(sys, 'tracebacklimit', 1000):
            nolim = extract()
            self.assertGreater(len(nolim), 5)
            self.assertEqual(extract(limit=2), nolim[-2:])
            assertEqualExcept(extract(limit=100), nolim[-100:], -5-1)
            self.assertEqual(extract(limit=-2), nolim[:2])
            assertEqualExcept(extract(limit=-100), nolim[:100], len(nolim)-5-1)
            self.assertEqual(extract(limit=0), [])
            del sys.tracebacklimit
            assertEqualExcept(extract(), nolim, -5-1)
            sys.tracebacklimit = 2
            self.assertEqual(extract(), nolim[-2:])
            self.assertEqual(extract(limit=3), nolim[-3:])
            self.assertEqual(extract(limit=-3), nolim[:3])
            sys.tracebacklimit = 0
            self.assertEqual(extract(), [])
            sys.tracebacklimit = -1
            self.assertEqual(extract(), [])

    eleza test_extract_tb(self):
        try:
            self.last_raises5()
        except Exception:
            exc_type, exc_value, tb = sys.exc_info()
        eleza extract(**kwargs):
            rudisha traceback.extract_tb(tb, **kwargs)

        with support.swap_attr(sys, 'tracebacklimit', 1000):
            nolim = extract()
            self.assertEqual(len(nolim), 5+1)
            self.assertEqual(extract(limit=2), nolim[:2])
            self.assertEqual(extract(limit=10), nolim)
            self.assertEqual(extract(limit=-2), nolim[-2:])
            self.assertEqual(extract(limit=-10), nolim)
            self.assertEqual(extract(limit=0), [])
            del sys.tracebacklimit
            self.assertEqual(extract(), nolim)
            sys.tracebacklimit = 2
            self.assertEqual(extract(), nolim[:2])
            self.assertEqual(extract(limit=3), nolim[:3])
            self.assertEqual(extract(limit=-3), nolim[-3:])
            sys.tracebacklimit = 0
            self.assertEqual(extract(), [])
            sys.tracebacklimit = -1
            self.assertEqual(extract(), [])

    eleza test_format_exception(self):
        try:
            self.last_raises5()
        except Exception:
            exc_type, exc_value, tb = sys.exc_info()
        # [1:-1] to exclude "Traceback (...)" header and
        # exception type and value
        eleza extract(**kwargs):
            rudisha traceback.format_exception(exc_type, exc_value, tb, **kwargs)[1:-1]

        with support.swap_attr(sys, 'tracebacklimit', 1000):
            nolim = extract()
            self.assertEqual(len(nolim), 5+1)
            self.assertEqual(extract(limit=2), nolim[:2])
            self.assertEqual(extract(limit=10), nolim)
            self.assertEqual(extract(limit=-2), nolim[-2:])
            self.assertEqual(extract(limit=-10), nolim)
            self.assertEqual(extract(limit=0), [])
            del sys.tracebacklimit
            self.assertEqual(extract(), nolim)
            sys.tracebacklimit = 2
            self.assertEqual(extract(), nolim[:2])
            self.assertEqual(extract(limit=3), nolim[:3])
            self.assertEqual(extract(limit=-3), nolim[-3:])
            sys.tracebacklimit = 0
            self.assertEqual(extract(), [])
            sys.tracebacklimit = -1
            self.assertEqual(extract(), [])


kundi MiscTracebackCases(unittest.TestCase):
    #
    # Check non-printing functions in traceback module
    #

    eleza test_clear(self):
        eleza outer():
            middle()
        eleza middle():
            inner()
        eleza inner():
            i = 1
            1/0

        try:
            outer()
        except:
            type_, value, tb = sys.exc_info()

        # Initial assertion: there's one local in the inner frame.
        inner_frame = tb.tb_next.tb_next.tb_next.tb_frame
        self.assertEqual(len(inner_frame.f_locals), 1)

        # Clear traceback frames
        traceback.clear_frames(tb)

        # Local variable dict should now be empty.
        self.assertEqual(len(inner_frame.f_locals), 0)

    eleza test_extract_stack(self):
        eleza extract():
            rudisha traceback.extract_stack()
        result = extract()
        lineno = extract.__code__.co_firstlineno
        self.assertEqual(result[-2:], [
            (__file__, lineno+2, 'test_extract_stack', 'result = extract()'),
            (__file__, lineno+1, 'extract', 'rudisha traceback.extract_stack()'),
            ])
        self.assertEqual(len(result[0]), 4)


kundi TestFrame(unittest.TestCase):

    eleza test_basics(self):
        linecache.clearcache()
        linecache.lazycache("f", globals())
        f = traceback.FrameSummary("f", 1, "dummy")
        self.assertEqual(f,
            ("f", 1, "dummy", '"""Test cases for traceback module"""'))
        self.assertEqual(tuple(f),
            ("f", 1, "dummy", '"""Test cases for traceback module"""'))
        self.assertEqual(f, traceback.FrameSummary("f", 1, "dummy"))
        self.assertEqual(f, tuple(f))
        # Since tuple.__eq__ doesn't support FrameSummary, the equality
        # operator fallbacks to FrameSummary.__eq__.
        self.assertEqual(tuple(f), f)
        self.assertIsNone(f.locals)

    eleza test_lazy_lines(self):
        linecache.clearcache()
        f = traceback.FrameSummary("f", 1, "dummy", lookup_line=False)
        self.assertEqual(None, f._line)
        linecache.lazycache("f", globals())
        self.assertEqual(
            '"""Test cases for traceback module"""',
            f.line)

    eleza test_explicit_line(self):
        f = traceback.FrameSummary("f", 1, "dummy", line="line")
        self.assertEqual("line", f.line)

    eleza test_len(self):
        f = traceback.FrameSummary("f", 1, "dummy", line="line")
        self.assertEqual(len(f), 4)


kundi TestStack(unittest.TestCase):

    eleza test_walk_stack(self):
        eleza deeper():
            rudisha list(traceback.walk_stack(None))
        s1 = list(traceback.walk_stack(None))
        s2 = deeper()
        self.assertEqual(len(s2) - len(s1), 1)
        self.assertEqual(s2[1:], s1)

    eleza test_walk_tb(self):
        try:
            1/0
        except Exception:
            _, _, tb = sys.exc_info()
        s = list(traceback.walk_tb(tb))
        self.assertEqual(len(s), 1)

    eleza test_extract_stack(self):
        s = traceback.StackSummary.extract(traceback.walk_stack(None))
        self.assertIsInstance(s, traceback.StackSummary)

    eleza test_extract_stack_limit(self):
        s = traceback.StackSummary.extract(traceback.walk_stack(None), limit=5)
        self.assertEqual(len(s), 5)

    eleza test_extract_stack_lookup_lines(self):
        linecache.clearcache()
        linecache.updatecache('/foo.py', globals())
        c = test_code('/foo.py', 'method')
        f = test_frame(c, None, None)
        s = traceback.StackSummary.extract(iter([(f, 6)]), lookup_lines=True)
        linecache.clearcache()
        self.assertEqual(s[0].line, "agiza sys")

    eleza test_extract_stackup_deferred_lookup_lines(self):
        linecache.clearcache()
        c = test_code('/foo.py', 'method')
        f = test_frame(c, None, None)
        s = traceback.StackSummary.extract(iter([(f, 6)]), lookup_lines=False)
        self.assertEqual({}, linecache.cache)
        linecache.updatecache('/foo.py', globals())
        self.assertEqual(s[0].line, "agiza sys")

    eleza test_kutoka_list(self):
        s = traceback.StackSummary.kutoka_list([('foo.py', 1, 'fred', 'line')])
        self.assertEqual(
            ['  File "foo.py", line 1, in fred\n    line\n'],
            s.format())

    eleza test_kutoka_list_edited_stack(self):
        s = traceback.StackSummary.kutoka_list([('foo.py', 1, 'fred', 'line')])
        s[0] = ('foo.py', 2, 'fred', 'line')
        s2 = traceback.StackSummary.kutoka_list(s)
        self.assertEqual(
            ['  File "foo.py", line 2, in fred\n    line\n'],
            s2.format())

    eleza test_format_smoke(self):
        # For detailed tests see the format_list tests, which consume the same
        # code.
        s = traceback.StackSummary.kutoka_list([('foo.py', 1, 'fred', 'line')])
        self.assertEqual(
            ['  File "foo.py", line 1, in fred\n    line\n'],
            s.format())

    eleza test_locals(self):
        linecache.updatecache('/foo.py', globals())
        c = test_code('/foo.py', 'method')
        f = test_frame(c, globals(), {'something': 1})
        s = traceback.StackSummary.extract(iter([(f, 6)]), capture_locals=True)
        self.assertEqual(s[0].locals, {'something': '1'})

    eleza test_no_locals(self):
        linecache.updatecache('/foo.py', globals())
        c = test_code('/foo.py', 'method')
        f = test_frame(c, globals(), {'something': 1})
        s = traceback.StackSummary.extract(iter([(f, 6)]))
        self.assertEqual(s[0].locals, None)

    eleza test_format_locals(self):
        eleza some_inner(k, v):
            a = 1
            b = 2
            rudisha traceback.StackSummary.extract(
                traceback.walk_stack(None), capture_locals=True, limit=1)
        s = some_inner(3, 4)
        self.assertEqual(
            ['  File "%s", line %d, in some_inner\n'
             '    rudisha traceback.StackSummary.extract(\n'
             '    a = 1\n'
             '    b = 2\n'
             '    k = 3\n'
             '    v = 4\n' % (__file__, some_inner.__code__.co_firstlineno + 3)
            ], s.format())

kundi TestTracebackException(unittest.TestCase):

    eleza test_smoke(self):
        try:
            1/0
        except Exception:
            exc_info = sys.exc_info()
            exc = traceback.TracebackException(*exc_info)
            expected_stack = traceback.StackSummary.extract(
                traceback.walk_tb(exc_info[2]))
        self.assertEqual(None, exc.__cause__)
        self.assertEqual(None, exc.__context__)
        self.assertEqual(False, exc.__suppress_context__)
        self.assertEqual(expected_stack, exc.stack)
        self.assertEqual(exc_info[0], exc.exc_type)
        self.assertEqual(str(exc_info[1]), str(exc))

    eleza test_kutoka_exception(self):
        # Check all the parameters are accepted.
        eleza foo():
            1/0
        try:
            foo()
        except Exception as e:
            exc_info = sys.exc_info()
            self.expected_stack = traceback.StackSummary.extract(
                traceback.walk_tb(exc_info[2]), limit=1, lookup_lines=False,
                capture_locals=True)
            self.exc = traceback.TracebackException.kutoka_exception(
                e, limit=1, lookup_lines=False, capture_locals=True)
        expected_stack = self.expected_stack
        exc = self.exc
        self.assertEqual(None, exc.__cause__)
        self.assertEqual(None, exc.__context__)
        self.assertEqual(False, exc.__suppress_context__)
        self.assertEqual(expected_stack, exc.stack)
        self.assertEqual(exc_info[0], exc.exc_type)
        self.assertEqual(str(exc_info[1]), str(exc))

    eleza test_cause(self):
        try:
            try:
                1/0
            finally:
                exc_info_context = sys.exc_info()
                exc_context = traceback.TracebackException(*exc_info_context)
                cause = Exception("cause")
                raise Exception("uh oh") kutoka cause
        except Exception:
            exc_info = sys.exc_info()
            exc = traceback.TracebackException(*exc_info)
            expected_stack = traceback.StackSummary.extract(
                traceback.walk_tb(exc_info[2]))
        exc_cause = traceback.TracebackException(Exception, cause, None)
        self.assertEqual(exc_cause, exc.__cause__)
        self.assertEqual(exc_context, exc.__context__)
        self.assertEqual(True, exc.__suppress_context__)
        self.assertEqual(expected_stack, exc.stack)
        self.assertEqual(exc_info[0], exc.exc_type)
        self.assertEqual(str(exc_info[1]), str(exc))

    eleza test_context(self):
        try:
            try:
                1/0
            finally:
                exc_info_context = sys.exc_info()
                exc_context = traceback.TracebackException(*exc_info_context)
                raise Exception("uh oh")
        except Exception:
            exc_info = sys.exc_info()
            exc = traceback.TracebackException(*exc_info)
            expected_stack = traceback.StackSummary.extract(
                traceback.walk_tb(exc_info[2]))
        self.assertEqual(None, exc.__cause__)
        self.assertEqual(exc_context, exc.__context__)
        self.assertEqual(False, exc.__suppress_context__)
        self.assertEqual(expected_stack, exc.stack)
        self.assertEqual(exc_info[0], exc.exc_type)
        self.assertEqual(str(exc_info[1]), str(exc))

    eleza test_unhashable(self):
        kundi UnhashableException(Exception):
            eleza __eq__(self, other):
                rudisha True

        ex1 = UnhashableException('ex1')
        ex2 = UnhashableException('ex2')
        try:
            raise ex2 kutoka ex1
        except UnhashableException:
            try:
                raise ex1
            except UnhashableException:
                exc_info = sys.exc_info()
        exc = traceback.TracebackException(*exc_info)
        formatted = list(exc.format())
        self.assertIn('UnhashableException: ex2\n', formatted[2])
        self.assertIn('UnhashableException: ex1\n', formatted[6])

    eleza test_limit(self):
        eleza recurse(n):
            ikiwa n:
                recurse(n-1)
            else:
                1/0
        try:
            recurse(10)
        except Exception:
            exc_info = sys.exc_info()
            exc = traceback.TracebackException(*exc_info, limit=5)
            expected_stack = traceback.StackSummary.extract(
                traceback.walk_tb(exc_info[2]), limit=5)
        self.assertEqual(expected_stack, exc.stack)

    eleza test_lookup_lines(self):
        linecache.clearcache()
        e = Exception("uh oh")
        c = test_code('/foo.py', 'method')
        f = test_frame(c, None, None)
        tb = test_tb(f, 6, None)
        exc = traceback.TracebackException(Exception, e, tb, lookup_lines=False)
        self.assertEqual({}, linecache.cache)
        linecache.updatecache('/foo.py', globals())
        self.assertEqual(exc.stack[0].line, "agiza sys")

    eleza test_locals(self):
        linecache.updatecache('/foo.py', globals())
        e = Exception("uh oh")
        c = test_code('/foo.py', 'method')
        f = test_frame(c, globals(), {'something': 1, 'other': 'string'})
        tb = test_tb(f, 6, None)
        exc = traceback.TracebackException(
            Exception, e, tb, capture_locals=True)
        self.assertEqual(
            exc.stack[0].locals, {'something': '1', 'other': "'string'"})

    eleza test_no_locals(self):
        linecache.updatecache('/foo.py', globals())
        e = Exception("uh oh")
        c = test_code('/foo.py', 'method')
        f = test_frame(c, globals(), {'something': 1})
        tb = test_tb(f, 6, None)
        exc = traceback.TracebackException(Exception, e, tb)
        self.assertEqual(exc.stack[0].locals, None)

    eleza test_traceback_header(self):
        # do not print a traceback header ikiwa exc_traceback is None
        # see issue #24695
        exc = traceback.TracebackException(Exception, Exception("haven"), None)
        self.assertEqual(list(exc.format()), ["Exception: haven\n"])


kundi MiscTest(unittest.TestCase):

    eleza test_all(self):
        expected = set()
        blacklist = {'print_list'}
        for name in dir(traceback):
            ikiwa name.startswith('_') or name in blacklist:
                continue
            module_object = getattr(traceback, name)
            ikiwa getattr(module_object, '__module__', None) == 'traceback':
                expected.add(name)
        self.assertCountEqual(traceback.__all__, expected)


ikiwa __name__ == "__main__":
    unittest.main()
