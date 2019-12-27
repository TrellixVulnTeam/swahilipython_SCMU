"""Testing `tabnanny` module.

Glossary:
    * errored    : Whitespace related problems present in file.
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
        'ikiwa True:\n'
        '    andika("hello")\n'
        '  andika("world")\n'
        'else:\n'
        '    andika("else called")\n'
    ),
    "nannynag_errored": (
        'ikiwa True:\n'
        ' \tandika("hello")\n'
        '\tandika("world")\n'
        'else:\n'
        '    andika("else called")\n'
    ),
    "error_free": (
        'ikiwa True:\n'
        '    andika("hello")\n'
        '    andika("world")\n'
        'else:\n'
        '    andika("else called")\n'
    ),
    "tab_space_errored_1": (
        'eleza my_func():\n'
        '\t  andika("hello world")\n'
        '\t  ikiwa True:\n'
        '\t\tandika("If called")'
    ),
    "tab_space_errored_2": (
        'eleza my_func():\n'
        '\t\tandika("Hello world")\n'
        '\t\tikiwa True:\n'
        '\t        andika("If called")'
    )
}


kundi TemporaryPyFile:
    """Create a temporary python source code file."""

    eleza __init__(self, source_code='', directory=None):
        self.source_code = source_code
        self.dir = directory

    eleza __enter__(self):
        with tempfile.NamedTemporaryFile(
            mode='w', dir=self.dir, suffix=".py", delete=False
        ) as f:
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

        for words, expected in tests:
            with self.subTest(words=words, expected=expected):
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

        for args, expected in tests:
            with self.subTest(arguments=args, expected=expected):
                with captured_stderr() as stderr:
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
        for nanny, expected in tests:
            line_number = nanny.get_lineno()
            msg = nanny.get_msg()
            line = nanny.get_line()
            with self.subTest(
                line_number=line_number, expected=expected['lineno']
            ):
                self.assertEqual(expected['lineno'], line_number)
            with self.subTest(msg=msg, expected=expected['msg']):
                self.assertEqual(expected['msg'], msg)
            with self.subTest(line=line, expected=expected['line']):
                self.assertEqual(expected['line'], line)


kundi TestCheck(TestCase):
    """Testing tabnanny.check()."""

    eleza setUp(self):
        self.addCleanup(setattr, tabnanny, 'verbose', tabnanny.verbose)
        tabnanny.verbose = 0  # Forcefully deactivating verbose mode.

    eleza verify_tabnanny_check(self, dir_or_file, out="", err=""):
        """Common verification for tabnanny.check().

        Use this method to assert expected values of `stdout` and `stderr` after
        running tabnanny.check() on given `dir` or `file` path. Because
        tabnanny.check() captures exceptions and writes to `stdout` and
        `stderr`, asserting standard outputs is the only way.
        """
        with captured_stdout() as stdout, captured_stderr() as stderr:
            tabnanny.check(dir_or_file)
        self.assertEqual(stdout.getvalue(), out)
        self.assertEqual(stderr.getvalue(), err)

    eleza test_correct_file(self):
        """A python source code file without any errors."""
        with TemporaryPyFile(SOURCE_CODES["error_free"]) as file_path:
            self.verify_tabnanny_check(file_path)

    eleza test_correct_directory_verbose(self):
        """Directory containing few error free python source code files.

        Because order of files returned by `os.lsdir()` is not fixed, verify the
        existence of each output lines at `stdout` using `in` operator.
        `verbose` mode of `tabnanny.verbose` asserts `stdout`.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            lines = [f"{tmp_dir!r}: listing directory\n",]
            file1 = TemporaryPyFile(SOURCE_CODES["error_free"], directory=tmp_dir)
            file2 = TemporaryPyFile(SOURCE_CODES["error_free"], directory=tmp_dir)
            with file1 as file1_path, file2 as file2_path:
                for file_path in (file1_path, file2_path):
                    lines.append(f"{file_path!r}: Clean bill of health.\n")

                tabnanny.verbose = 1
                with captured_stdout() as stdout, captured_stderr() as stderr:
                    tabnanny.check(tmp_dir)
                stdout = stdout.getvalue()
                for line in lines:
                    with self.subTest(line=line):
                        self.assertIn(line, stdout)
                self.assertEqual(stderr.getvalue(), "")

    eleza test_correct_directory(self):
        """Directory which contains few error free python source code files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with TemporaryPyFile(SOURCE_CODES["error_free"], directory=tmp_dir):
                self.verify_tabnanny_check(tmp_dir)

    eleza test_when_wrong_indented(self):
        """A python source code file eligible for raising `IndentationError`."""
        with TemporaryPyFile(SOURCE_CODES["wrong_indented"]) as file_path:
            err = ('unindent does not match any outer indentation level'
                ' (<tokenize>, line 3)\n')
            err = f"{file_path!r}: Indentation Error: {err}"
            self.verify_tabnanny_check(file_path, err=err)

    eleza test_when_tokenize_tokenerror(self):
        """A python source code file eligible for raising 'tokenize.TokenError'."""
        with TemporaryPyFile(SOURCE_CODES["incomplete_expression"]) as file_path:
            err = "('EOF in multi-line statement', (7, 0))\n"
            err = f"{file_path!r}: Token Error: {err}"
            self.verify_tabnanny_check(file_path, err=err)

    eleza test_when_nannynag_error_verbose(self):
        """A python source code file eligible for raising `tabnanny.NannyNag`.

        Tests will assert `stdout` after activating `tabnanny.verbose` mode.
        """
        with TemporaryPyFile(SOURCE_CODES["nannynag_errored"]) as file_path:
            out = f"{file_path!r}: *** Line 3: trouble in tab city! ***\n"
            out += "offending line: '\\tandika(\"world\")\\n'\n"
            out += "indent not equal e.g. at tab size 1\n"

            tabnanny.verbose = 1
            self.verify_tabnanny_check(file_path, out=out)

    eleza test_when_nannynag_error(self):
        """A python source code file eligible for raising `tabnanny.NannyNag`."""
        with TemporaryPyFile(SOURCE_CODES["nannynag_errored"]) as file_path:
            out = f"{file_path} 3 '\\tandika(\"world\")\\n'\n"
            self.verify_tabnanny_check(file_path, out=out)

    eleza test_when_no_file(self):
        """A python file which does not exist actually in system."""
        path = 'no_file.py'
        err = (f"{path!r}: I/O Error: [Errno {errno.ENOENT}] "
              f"{os.strerror(errno.ENOENT)}: {path!r}\n")
        self.verify_tabnanny_check(path, err=err)

    eleza test_errored_directory(self):
        """Directory containing wrongly indented python source code files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            error_file = TemporaryPyFile(
                SOURCE_CODES["wrong_indented"], directory=tmp_dir
            )
            code_file = TemporaryPyFile(
                SOURCE_CODES["error_free"], directory=tmp_dir
            )
            with error_file as e_file, code_file as c_file:
                err = ('unindent does not match any outer indentation level'
                            ' (<tokenize>, line 3)\n')
                err = f"{e_file!r}: Indentation Error: {err}"
                self.verify_tabnanny_check(tmp_dir, err=err)


kundi TestProcessTokens(TestCase):
    """Testing `tabnanny.process_tokens()`."""

    @mock.patch('tabnanny.NannyNag')
    eleza test_with_correct_code(self, MockNannyNag):
        """A python source code without any whitespace related problems."""

        with TemporaryPyFile(SOURCE_CODES["error_free"]) as file_path:
            with open(file_path) as f:
                tabnanny.process_tokens(tokenize.generate_tokens(f.readline))
            self.assertFalse(MockNannyNag.called)

    eleza test_with_errored_codes_samples(self):
        """A python source code with whitespace related sampled problems."""

        # "tab_space_errored_1": executes block under type == tokenize.INDENT
        #                        at `tabnanny.process_tokens()`.
        # "tab space_errored_2": executes block under
        #                        `check_equal and type not in JUNK` condition at
        #                        `tabnanny.process_tokens()`.

        for key in ["tab_space_errored_1", "tab_space_errored_2"]:
            with self.subTest(key=key):
                with TemporaryPyFile(SOURCE_CODES[key]) as file_path:
                    with open(file_path) as f:
                        tokens = tokenize.generate_tokens(f.readline)
                        with self.assertRaises(tabnanny.NannyNag):
                            tabnanny.process_tokens(tokens)


kundi TestCommandLine(TestCase):
    """Tests command line interface of `tabnanny`."""

    eleza validate_cmd(self, *args, stdout="", stderr="", partial=False):
        """Common function to assert the behaviour of command line interface."""
        _, out, err = script_helper.assert_python_ok('-m', 'tabnanny', *args)
        # Note: The `splitlines()` will solve the problem of CRLF(\r) added
        # by OS Windows.
        out = out.decode('ascii')
        err = err.decode('ascii')
        ikiwa partial:
            for std, output in ((stdout, out), (stderr, err)):
                _output = output.splitlines()
                for _std in std.splitlines():
                    with self.subTest(std=_std, output=_output):
                        self.assertIn(_std, _output)
        else:
            self.assertListEqual(out.splitlines(), stdout.splitlines())
            self.assertListEqual(err.splitlines(), stderr.splitlines())

    eleza test_with_errored_file(self):
        """Should displays error when errored python file is given."""
        with TemporaryPyFile(SOURCE_CODES["wrong_indented"]) as file_path:
            stderr  = f"{file_path!r}: Indentation Error: "
            stderr += ('unindent does not match any outer indentation level'
                    ' (<tokenize>, line 3)')
            self.validate_cmd(file_path, stderr=stderr)

    eleza test_with_error_free_file(self):
        """Should not display anything ikiwa python file is correctly indented."""
        with TemporaryPyFile(SOURCE_CODES["error_free"]) as file_path:
            self.validate_cmd(file_path)

    eleza test_command_usage(self):
        """Should display usage on no arguments."""
        path = findfile('tabnanny.py')
        stderr = f"Usage: {path} [-v] file_or_directory ..."
        self.validate_cmd(stderr=stderr)

    eleza test_quiet_flag(self):
        """Should display less when quite mode is on."""
        with TemporaryPyFile(SOURCE_CODES["nannynag_errored"]) as file_path:
            stdout = f"{file_path}\n"
            self.validate_cmd("-q", file_path, stdout=stdout)

    eleza test_verbose_mode(self):
        """Should display more error information ikiwa verbose mode is on."""
        with TemporaryPyFile(SOURCE_CODES["nannynag_errored"]) as path:
            stdout = textwrap.dedent(
                "offending line: '\\tandika(\"world\")\\n'"
            ).strip()
            self.validate_cmd("-v", path, stdout=stdout, partial=True)

    eleza test_double_verbose_mode(self):
        """Should display detailed error information ikiwa double verbose is on."""
        with TemporaryPyFile(SOURCE_CODES["nannynag_errored"]) as path:
            stdout = textwrap.dedent(
                "offending line: '\\tandika(\"world\")\\n'"
            ).strip()
            self.validate_cmd("-vv", path, stdout=stdout, partial=True)
