"""Testing `tabnanny` module.

Glossary:
    * errored    : Whitespace related problems present kwenye file.
"""
kutoka unittest agiza TestCase, mock
kutoka unittest agiza mock
agiza errno
agiza os
agiza tabnanny
agiza tokenize
agiza tempfile
agiza textwrap
kutoka test.support agiza (captured_stderr, captured_stdout, script_helper,
                          findfile, unlink)


SOURCE_CODES = {
    "incomplete_expression": (
        'fruits = [\n'
        '    "Apple",\n'
        '    "Orange",\n'
        '    "Banana",\n'
        '\n'
        'andika(fruits)\n'
    ),
    "wrong_indented": (
        'ikiwa Kweli:\n'
        '    andika("hello")\n'
        '  andika("world")\n'
        'isipokua:\n'
        '    andika("else called")\n'
    ),
    "nannynag_errored": (
        'ikiwa Kweli:\n'
        ' \tandika("hello")\n'
        '\tandika("world")\n'
        'isipokua:\n'
        '    andika("else called")\n'
    ),
    "error_free": (
        'ikiwa Kweli:\n'
        '    andika("hello")\n'
        '    andika("world")\n'
        'isipokua:\n'
        '    andika("else called")\n'
    ),
    "tab_space_errored_1": (
        'eleza my_func():\n'
        '\t  andika("hello world")\n'
        '\t  ikiwa Kweli:\n'
        '\t\tandika("If called")'
    ),
    "tab_space_errored_2": (
        'eleza my_func():\n'
        '\t\tandika("Hello world")\n'
        '\t\tikiwa Kweli:\n'
        '\t        andika("If called")'
    )
}


kundi TemporaryPyFile:
    """Create a temporary python source code file."""

    eleza __init__(self, source_code='', directory=Tupu):
        self.source_code = source_code
        self.dir = directory

    eleza __enter__(self):
        ukijumuisha tempfile.NamedTemporaryFile(
            mode='w', dir=self.dir, suffix=".py", delete=Uongo
        ) kama f:
            f.write(self.source_code)
        self.file_path = f.name
        rudisha self.file_path

    eleza __exit__(self, exc_type, exc_value, exc_traceback):
        unlink(self.file_path)


kundi TestFormatWitnesses(TestCase):
    """Testing `tabnanny.format_witnesses()`."""

    eleza test_format_witnesses(self):
        """Asserting formatter result by giving various input samples."""
        tests = [
            ('Test', 'at tab sizes T, e, s, t'),
            ('', 'at tab size '),
            ('t', 'at tab size t'),
            ('  t  ', 'at tab sizes  ,  , t,  ,  '),
        ]

        kila words, expected kwenye tests:
            ukijumuisha self.subTest(words=words, expected=expected):
                self.assertEqual(tabnanny.format_witnesses(words), expected)


kundi TestErrPrint(TestCase):
    """Testing `tabnanny.errandika()`."""

    eleza test_errandika(self):
        """Asserting result of `tabnanny.errandika()` by giving sample inputs."""
        tests = [
            (['first', 'second'], 'first second\n'),
            (['first'], 'first\n'),
            ([1, 2, 3], '1 2 3\n'),
            ([], '\n')
        ]

        kila args, expected kwenye tests:
            ukijumuisha self.subTest(arguments=args, expected=expected):
                ukijumuisha captured_stderr() kama stderr:
                    tabnanny.errandika(*args)
                self.assertEqual(stderr.getvalue() , expected)


kundi TestNannyNag(TestCase):
    eleza test_all_methods(self):
        """Asserting behaviour of `tabnanny.NannyNag` exception."""
        tests = [
            (
                tabnanny.NannyNag(0, "foo", "bar"),
                {'lineno': 0, 'msg': 'foo', 'line': 'bar'}
            ),
            (
                tabnanny.NannyNag(5, "testmsg", "testline"),
                {'lineno': 5, 'msg': 'testmsg', 'line': 'testline'}
            )
        ]
        kila nanny, expected kwenye tests:
            line_number = nanny.get_lineno()
            msg = nanny.get_msg()
            line = nanny.get_line()
            ukijumuisha self.subTest(
                line_number=line_number, expected=expected['lineno']
            ):
                self.assertEqual(expected['lineno'], line_number)
            ukijumuisha self.subTest(msg=msg, expected=expected['msg']):
                self.assertEqual(expected['msg'], msg)
            ukijumuisha self.subTest(line=line, expected=expected['line']):
                self.assertEqual(expected['line'], line)


kundi TestCheck(TestCase):
    """Testing tabnanny.check()."""

    eleza setUp(self):
        self.addCleanup(setattr, tabnanny, 'verbose', tabnanny.verbose)
        tabnanny.verbose = 0  # Forcefully deactivating verbose mode.

    eleza verify_tabnanny_check(self, dir_or_file, out="", err=""):
        """Common verification kila tabnanny.check().

        Use this method to assert expected values of `stdout` na `stderr` after
        running tabnanny.check() on given `dir` ama `file` path. Because
        tabnanny.check() captures exceptions na writes to `stdout` na
        `stderr`, asserting standard outputs ni the only way.
        """
        ukijumuisha captured_stdout() kama stdout, captured_stderr() kama stderr:
            tabnanny.check(dir_or_file)
        self.assertEqual(stdout.getvalue(), out)
        self.assertEqual(stderr.getvalue(), err)

    eleza test_correct_file(self):
        """A python source code file without any errors."""
        ukijumuisha TemporaryPyFile(SOURCE_CODES["error_free"]) kama file_path:
            self.verify_tabnanny_check(file_path)

    eleza test_correct_directory_verbose(self):
        """Directory containing few error free python source code files.

        Because order of files returned by `os.lsdir()` ni sio fixed, verify the
        existence of each output lines at `stdout` using `in` operator.
        `verbose` mode of `tabnanny.verbose` asserts `stdout`.
        """
        ukijumuisha tempfile.TemporaryDirectory() kama tmp_dir:
            lines = [f"{tmp_dir!r}: listing directory\n",]
            file1 = TemporaryPyFile(SOURCE_CODES["error_free"], directory=tmp_dir)
            file2 = TemporaryPyFile(SOURCE_CODES["error_free"], directory=tmp_dir)
            ukijumuisha file1 kama file1_path, file2 kama file2_path:
                kila file_path kwenye (file1_path, file2_path):
                    lines.append(f"{file_path!r}: Clean bill of health.\n")

                tabnanny.verbose = 1
                ukijumuisha captured_stdout() kama stdout, captured_stderr() kama stderr:
                    tabnanny.check(tmp_dir)
                stdout = stdout.getvalue()
                kila line kwenye lines:
                    ukijumuisha self.subTest(line=line):
                        self.assertIn(line, stdout)
                self.assertEqual(stderr.getvalue(), "")

    eleza test_correct_directory(self):
        """Directory which contains few error free python source code files."""
        ukijumuisha tempfile.TemporaryDirectory() kama tmp_dir:
            ukijumuisha TemporaryPyFile(SOURCE_CODES["error_free"], directory=tmp_dir):
                self.verify_tabnanny_check(tmp_dir)

    eleza test_when_wrong_indented(self):
        """A python source code file eligible kila raising `IndentationError`."""
        ukijumuisha TemporaryPyFile(SOURCE_CODES["wrong_indented"]) kama file_path:
            err = ('unindent does sio match any outer indentation level'
                ' (<tokenize>, line 3)\n')
            err = f"{file_path!r}: Indentation Error: {err}"
            self.verify_tabnanny_check(file_path, err=err)

    eleza test_when_tokenize_tokenerror(self):
        """A python source code file eligible kila raising 'tokenize.TokenError'."""
        ukijumuisha TemporaryPyFile(SOURCE_CODES["incomplete_expression"]) kama file_path:
            err = "('EOF kwenye multi-line statement', (7, 0))\n"
            err = f"{file_path!r}: Token Error: {err}"
            self.verify_tabnanny_check(file_path, err=err)

    eleza test_when_nannynag_error_verbose(self):
        """A python source code file eligible kila raising `tabnanny.NannyNag`.

        Tests will assert `stdout` after activating `tabnanny.verbose` mode.
        """
        ukijumuisha TemporaryPyFile(SOURCE_CODES["nannynag_errored"]) kama file_path:
            out = f"{file_path!r}: *** Line 3: trouble kwenye tab city! ***\n"
            out += "offending line: '\\tandika(\"world\")\\n'\n"
            out += "indent sio equal e.g. at tab size 1\n"

            tabnanny.verbose = 1
            self.verify_tabnanny_check(file_path, out=out)

    eleza test_when_nannynag_error(self):
        """A python source code file eligible kila raising `tabnanny.NannyNag`."""
        ukijumuisha TemporaryPyFile(SOURCE_CODES["nannynag_errored"]) kama file_path:
            out = f"{file_path} 3 '\\tandika(\"world\")\\n'\n"
            self.verify_tabnanny_check(file_path, out=out)

    eleza test_when_no_file(self):
        """A python file which does sio exist actually kwenye system."""
        path = 'no_file.py'
        err = (f"{path!r}: I/O Error: [Errno {errno.ENOENT}] "
              f"{os.strerror(errno.ENOENT)}: {path!r}\n")
        self.verify_tabnanny_check(path, err=err)

    eleza test_errored_directory(self):
        """Directory containing wrongly indented python source code files."""
        ukijumuisha tempfile.TemporaryDirectory() kama tmp_dir:
            error_file = TemporaryPyFile(
                SOURCE_CODES["wrong_indented"], directory=tmp_dir
            )
            code_file = TemporaryPyFile(
                SOURCE_CODES["error_free"], directory=tmp_dir
            )
            ukijumuisha error_file kama e_file, code_file kama c_file:
                err = ('unindent does sio match any outer indentation level'
                            ' (<tokenize>, line 3)\n')
                err = f"{e_file!r}: Indentation Error: {err}"
                self.verify_tabnanny_check(tmp_dir, err=err)


kundi TestProcessTokens(TestCase):
    """Testing `tabnanny.process_tokens()`."""

    @mock.patch('tabnanny.NannyNag')
    eleza test_with_correct_code(self, MockNannyNag):
        """A python source code without any whitespace related problems."""

        ukijumuisha TemporaryPyFile(SOURCE_CODES["error_free"]) kama file_path:
            ukijumuisha open(file_path) kama f:
                tabnanny.process_tokens(tokenize.generate_tokens(f.readline))
            self.assertUongo(MockNannyNag.called)

    eleza test_with_errored_codes_samples(self):
        """A python source code ukijumuisha whitespace related sampled problems."""

        # "tab_space_errored_1": executes block under type == tokenize.INDENT
        #                        at `tabnanny.process_tokens()`.
        # "tab space_errored_2": executes block under
        #                        `check_equal na type haiko kwenye JUNK` condition at
        #                        `tabnanny.process_tokens()`.

        kila key kwenye ["tab_space_errored_1", "tab_space_errored_2"]:
            ukijumuisha self.subTest(key=key):
                ukijumuisha TemporaryPyFile(SOURCE_CODES[key]) kama file_path:
                    ukijumuisha open(file_path) kama f:
                        tokens = tokenize.generate_tokens(f.readline)
                        ukijumuisha self.assertRaises(tabnanny.NannyNag):
                            tabnanny.process_tokens(tokens)


kundi TestCommandLine(TestCase):
    """Tests command line interface of `tabnanny`."""

    eleza validate_cmd(self, *args, stdout="", stderr="", partial=Uongo):
        """Common function to assert the behaviour of command line interface."""
        _, out, err = script_helper.assert_python_ok('-m', 'tabnanny', *args)
        # Note: The `splitlines()` will solve the problem of CRLF(\r) added
        # by OS Windows.
        out = out.decode('ascii')
        err = err.decode('ascii')
        ikiwa partial:
            kila std, output kwenye ((stdout, out), (stderr, err)):
                _output = output.splitlines()
                kila _std kwenye std.splitlines():
                    ukijumuisha self.subTest(std=_std, output=_output):
                        self.assertIn(_std, _output)
        isipokua:
            self.assertListEqual(out.splitlines(), stdout.splitlines())
            self.assertListEqual(err.splitlines(), stderr.splitlines())

    eleza test_with_errored_file(self):
        """Should displays error when errored python file ni given."""
        ukijumuisha TemporaryPyFile(SOURCE_CODES["wrong_indented"]) kama file_path:
            stderr  = f"{file_path!r}: Indentation Error: "
            stderr += ('unindent does sio match any outer indentation level'
                    ' (<tokenize>, line 3)')
            self.validate_cmd(file_path, stderr=stderr)

    eleza test_with_error_free_file(self):
        """Should sio display anything ikiwa python file ni correctly indented."""
        ukijumuisha TemporaryPyFile(SOURCE_CODES["error_free"]) kama file_path:
            self.validate_cmd(file_path)

    eleza test_command_usage(self):
        """Should display usage on no arguments."""
        path = findfile('tabnanny.py')
        stderr = f"Usage: {path} [-v] file_or_directory ..."
        self.validate_cmd(stderr=stderr)

    eleza test_quiet_flag(self):
        """Should display less when quite mode ni on."""
        ukijumuisha TemporaryPyFile(SOURCE_CODES["nannynag_errored"]) kama file_path:
            stdout = f"{file_path}\n"
            self.validate_cmd("-q", file_path, stdout=stdout)

    eleza test_verbose_mode(self):
        """Should display more error information ikiwa verbose mode ni on."""
        ukijumuisha TemporaryPyFile(SOURCE_CODES["nannynag_errored"]) kama path:
            stdout = textwrap.dedent(
                "offending line: '\\tandika(\"world\")\\n'"
            ).strip()
            self.validate_cmd("-v", path, stdout=stdout, partial=Kweli)

    eleza test_double_verbose_mode(self):
        """Should display detailed error information ikiwa double verbose ni on."""
        ukijumuisha TemporaryPyFile(SOURCE_CODES["nannynag_errored"]) kama path:
            stdout = textwrap.dedent(
                "offending line: '\\tandika(\"world\")\\n'"
            ).strip()
            self.validate_cmd("-vv", path, stdout=stdout, partial=Kweli)
