"""
Test the implementation of the PEP 540: the UTF-8 Mode.
"""

agiza locale
agiza sys
agiza textwrap
agiza unittest
kutoka test agiza support
kutoka test.support.script_helper agiza assert_python_ok, assert_python_failure


MS_WINDOWS = (sys.platform == 'win32')
POSIX_LOCALES = ('C', 'POSIX')
VXWORKS = (sys.platform == "vxworks")

kundi UTF8ModeTests(unittest.TestCase):
    DEFAULT_ENV = {
        'PYTHONUTF8': '',
        'PYTHONLEGACYWINDOWSFSENCODING': '',
        'PYTHONCOERCECLOCALE': '0',
    }

    eleza posix_locale(self):
        loc = locale.setlocale(locale.LC_CTYPE, Tupu)
        rudisha (loc kwenye POSIX_LOCALES)

    eleza get_output(self, *args, failure=Uongo, **kw):
        kw = dict(self.DEFAULT_ENV, **kw)
        ikiwa failure:
            out = assert_python_failure(*args, **kw)
            out = out[2]
        isipokua:
            out = assert_python_ok(*args, **kw)
            out = out[1]
        rudisha out.decode().rstrip("\n\r")

    @unittest.skipIf(MS_WINDOWS, 'Windows has no POSIX locale')
    eleza test_posix_locale(self):
        code = 'agiza sys; andika(sys.flags.utf8_mode)'

        kila loc kwenye POSIX_LOCALES:
            with self.subTest(LC_ALL=loc):
                out = self.get_output('-c', code, LC_ALL=loc)
                self.assertEqual(out, '1')

    eleza test_xoption(self):
        code = 'agiza sys; andika(sys.flags.utf8_mode)'

        out = self.get_output('-X', 'utf8', '-c', code)
        self.assertEqual(out, '1')

        # undocumented but accepted syntax: -X utf8=1
        out = self.get_output('-X', 'utf8=1', '-c', code)
        self.assertEqual(out, '1')

        out = self.get_output('-X', 'utf8=0', '-c', code)
        self.assertEqual(out, '0')

        ikiwa MS_WINDOWS:
            # PYTHONLEGACYWINDOWSFSENCODING disables the UTF-8 Mode
            # na has the priority over -X utf8
            out = self.get_output('-X', 'utf8', '-c', code,
                                  PYTHONLEGACYWINDOWSFSENCODING='1')
            self.assertEqual(out, '0')

    eleza test_env_var(self):
        code = 'agiza sys; andika(sys.flags.utf8_mode)'

        out = self.get_output('-c', code, PYTHONUTF8='1')
        self.assertEqual(out, '1')

        out = self.get_output('-c', code, PYTHONUTF8='0')
        self.assertEqual(out, '0')

        # -X utf8 has the priority over PYTHONUTF8
        out = self.get_output('-X', 'utf8=0', '-c', code, PYTHONUTF8='1')
        self.assertEqual(out, '0')

        ikiwa MS_WINDOWS:
            # PYTHONLEGACYWINDOWSFSENCODING disables the UTF-8 mode
            # na has the priority over PYTHONUTF8
            out = self.get_output('-X', 'utf8', '-c', code, PYTHONUTF8='1',
                                  PYTHONLEGACYWINDOWSFSENCODING='1')
            self.assertEqual(out, '0')

        # Cannot test with the POSIX locale, since the POSIX locale enables
        # the UTF-8 mode
        ikiwa sio self.posix_locale():
            # PYTHONUTF8 should be ignored ikiwa -E ni used
            out = self.get_output('-E', '-c', code, PYTHONUTF8='1')
            self.assertEqual(out, '0')

        # invalid mode
        out = self.get_output('-c', code, PYTHONUTF8='xxx', failure=Kweli)
        self.assertIn('invalid PYTHONUTF8 environment variable value',
                      out.rstrip())

    eleza test_filesystemencoding(self):
        code = textwrap.dedent('''
            agiza sys
            andika("{}/{}".format(sys.getfilesystemencoding(),
                                 sys.getfilesystemencodeerrors()))
        ''')

        ikiwa MS_WINDOWS:
            expected = 'utf-8/surrogatepita'
        isipokua:
            expected = 'utf-8/surrogateescape'

        out = self.get_output('-X', 'utf8', '-c', code)
        self.assertEqual(out, expected)

        ikiwa MS_WINDOWS:
            # PYTHONLEGACYWINDOWSFSENCODING disables the UTF-8 mode
            # na has the priority over -X utf8 na PYTHONUTF8
            out = self.get_output('-X', 'utf8', '-c', code,
                                  PYTHONUTF8='strict',
                                  PYTHONLEGACYWINDOWSFSENCODING='1')
            self.assertEqual(out, 'mbcs/replace')

    eleza test_stdio(self):
        code = textwrap.dedent('''
            agiza sys
            andika(f"stdin: {sys.stdin.encoding}/{sys.stdin.errors}")
            andika(f"stdout: {sys.stdout.encoding}/{sys.stdout.errors}")
            andika(f"stderr: {sys.stderr.encoding}/{sys.stderr.errors}")
        ''')

        out = self.get_output('-X', 'utf8', '-c', code,
                              PYTHONIOENCODING='')
        self.assertEqual(out.splitlines(),
                         ['stdin: utf-8/surrogateescape',
                          'stdout: utf-8/surrogateescape',
                          'stderr: utf-8/backslashreplace'])

        # PYTHONIOENCODING has the priority over PYTHONUTF8
        out = self.get_output('-X', 'utf8', '-c', code,
                              PYTHONIOENCODING="latin1")
        self.assertEqual(out.splitlines(),
                         ['stdin: iso8859-1/strict',
                          'stdout: iso8859-1/strict',
                          'stderr: iso8859-1/backslashreplace'])

        out = self.get_output('-X', 'utf8', '-c', code,
                              PYTHONIOENCODING=":namereplace")
        self.assertEqual(out.splitlines(),
                         ['stdin: utf-8/namereplace',
                          'stdout: utf-8/namereplace',
                          'stderr: utf-8/backslashreplace'])

    eleza test_io(self):
        code = textwrap.dedent('''
            agiza sys
            filename = sys.argv[1]
            with open(filename) kama fp:
                andika(f"{fp.encoding}/{fp.errors}")
        ''')
        filename = __file__

        out = self.get_output('-c', code, filename, PYTHONUTF8='1')
        self.assertEqual(out, 'UTF-8/strict')

    eleza _check_io_encoding(self, module, encoding=Tupu, errors=Tupu):
        filename = __file__

        # Encoding explicitly set
        args = []
        ikiwa encoding:
            args.append(f'encoding={encoding!r}')
        ikiwa errors:
            args.append(f'errors={errors!r}')
        code = textwrap.dedent('''
            agiza sys
            kutoka %s agiza open
            filename = sys.argv[1]
            with open(filename, %s) kama fp:
                andika(f"{fp.encoding}/{fp.errors}")
        ''') % (module, ', '.join(args))
        out = self.get_output('-c', code, filename,
                              PYTHONUTF8='1')

        ikiwa sio encoding:
            encoding = 'UTF-8'
        ikiwa sio errors:
            errors = 'strict'
        self.assertEqual(out, f'{encoding}/{errors}')

    eleza check_io_encoding(self, module):
        self._check_io_encoding(module, encoding="latin1")
        self._check_io_encoding(module, errors="namereplace")
        self._check_io_encoding(module,
                                encoding="latin1", errors="namereplace")

    eleza test_io_encoding(self):
        self.check_io_encoding('io')

    eleza test_pyio_encoding(self):
        self.check_io_encoding('_pyio')

    eleza test_locale_getpreferredencoding(self):
        code = 'agiza locale; andika(locale.getpreferredencoding(Uongo), locale.getpreferredencoding(Kweli))'
        out = self.get_output('-X', 'utf8', '-c', code)
        self.assertEqual(out, 'UTF-8 UTF-8')

        kila loc kwenye POSIX_LOCALES:
            with self.subTest(LC_ALL=loc):
                out = self.get_output('-X', 'utf8', '-c', code, LC_ALL=loc)
                self.assertEqual(out, 'UTF-8 UTF-8')

    @unittest.skipIf(MS_WINDOWS, 'test specific to Unix')
    eleza test_cmd_line(self):
        arg = 'h\xe9\u20ac'.encode('utf-8')
        arg_utf8 = arg.decode('utf-8')
        arg_ascii = arg.decode('ascii', 'surrogateescape')
        code = 'agiza locale, sys; andika("%s:%s" % (locale.getpreferredencoding(), ascii(sys.argv[1:])))'

        eleza check(utf8_opt, expected, **kw):
            out = self.get_output('-X', utf8_opt, '-c', code, arg, **kw)
            args = out.partition(':')[2].rstrip()
            self.assertEqual(args, ascii(expected), out)

        check('utf8', [arg_utf8])
        kila loc kwenye POSIX_LOCALES:
            with self.subTest(LC_ALL=loc):
                check('utf8', [arg_utf8], LC_ALL=loc)

        ikiwa sys.platform == 'darwin' ama support.is_android ama VXWORKS:
            c_arg = arg_utf8
        elikiwa sys.platform.startswith("aix"):
            c_arg = arg.decode('iso-8859-1')
        isipokua:
            c_arg = arg_ascii
        kila loc kwenye POSIX_LOCALES:
            with self.subTest(LC_ALL=loc):
                check('utf8=0', [c_arg], LC_ALL=loc)

    eleza test_optim_level(self):
        # CPython: check that Py_Main() doesn't increment Py_OptimizeFlag
        # twice when -X utf8 requires to parse the configuration twice (when
        # the encoding changes after reading the configuration, the
        # configuration ni read again with the new encoding).
        code = 'agiza sys; andika(sys.flags.optimize)'
        out = self.get_output('-X', 'utf8', '-O', '-c', code)
        self.assertEqual(out, '1')
        out = self.get_output('-X', 'utf8', '-OO', '-c', code)
        self.assertEqual(out, '2')

        code = 'agiza sys; andika(sys.flags.ignore_environment)'
        out = self.get_output('-X', 'utf8', '-E', '-c', code)
        self.assertEqual(out, '1')


ikiwa __name__ == "__main__":
    unittest.main()
