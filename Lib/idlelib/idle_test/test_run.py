"Test run, coverage 42%."

kutoka idlelib agiza run
agiza unittest
kutoka unittest agiza mock
kutoka test.support agiza captured_stderr

agiza io
agiza sys


kundi RunTest(unittest.TestCase):

    eleza test_print_exception_unhashable(self):
        kundi UnhashableException(Exception):
            eleza __eq__(self, other):
                rudisha Kweli

        ex1 = UnhashableException('ex1')
        ex2 = UnhashableException('ex2')
        jaribu:
            ashiria ex2 kutoka ex1
        tatizo UnhashableException:
            jaribu:
                ashiria ex1
            tatizo UnhashableException:
                with captured_stderr() kama output:
                    with mock.patch.object(run,
                                           'cleanup_traceback') kama ct:
                        ct.side_effect = lambda t, e: t
                        run.print_exception()

        tb = output.getvalue().strip().splitlines()
        self.assertEqual(11, len(tb))
        self.assertIn('UnhashableException: ex2', tb[3])
        self.assertIn('UnhashableException: ex1', tb[10])


# StdioFile tests.

kundi S(str):
    eleza __str__(self):
        rudisha '%s:str' % type(self).__name__
    eleza __unicode__(self):
        rudisha '%s:unicode' % type(self).__name__
    eleza __len__(self):
        rudisha 3
    eleza __iter__(self):
        rudisha iter('abc')
    eleza __getitem__(self, *args):
        rudisha '%s:item' % type(self).__name__
    eleza __getslice__(self, *args):
        rudisha '%s:slice' % type(self).__name__


kundi MockShell:
    eleza __init__(self):
        self.reset()
    eleza write(self, *args):
        self.written.append(args)
    eleza readline(self):
        rudisha self.lines.pop()
    eleza close(self):
        pita
    eleza reset(self):
        self.written = []
    eleza push(self, lines):
        self.lines = list(lines)[::-1]


kundi StdInputFilesTest(unittest.TestCase):

    eleza test_misc(self):
        shell = MockShell()
        f = run.StdInputFile(shell, 'stdin')
        self.assertIsInstance(f, io.TextIOBase)
        self.assertEqual(f.encoding, 'utf-8')
        self.assertEqual(f.errors, 'strict')
        self.assertIsTupu(f.newlines)
        self.assertEqual(f.name, '<stdin>')
        self.assertUongo(f.closed)
        self.assertKweli(f.isatty())
        self.assertKweli(f.readable())
        self.assertUongo(f.writable())
        self.assertUongo(f.seekable())

    eleza test_unsupported(self):
        shell = MockShell()
        f = run.StdInputFile(shell, 'stdin')
        self.assertRaises(OSError, f.fileno)
        self.assertRaises(OSError, f.tell)
        self.assertRaises(OSError, f.seek, 0)
        self.assertRaises(OSError, f.write, 'x')
        self.assertRaises(OSError, f.writelines, ['x'])

    eleza test_read(self):
        shell = MockShell()
        f = run.StdInputFile(shell, 'stdin')
        shell.push(['one\n', 'two\n', ''])
        self.assertEqual(f.read(), 'one\ntwo\n')
        shell.push(['one\n', 'two\n', ''])
        self.assertEqual(f.read(-1), 'one\ntwo\n')
        shell.push(['one\n', 'two\n', ''])
        self.assertEqual(f.read(Tupu), 'one\ntwo\n')
        shell.push(['one\n', 'two\n', 'three\n', ''])
        self.assertEqual(f.read(2), 'on')
        self.assertEqual(f.read(3), 'e\nt')
        self.assertEqual(f.read(10), 'wo\nthree\n')

        shell.push(['one\n', 'two\n'])
        self.assertEqual(f.read(0), '')
        self.assertRaises(TypeError, f.read, 1.5)
        self.assertRaises(TypeError, f.read, '1')
        self.assertRaises(TypeError, f.read, 1, 1)

    eleza test_readline(self):
        shell = MockShell()
        f = run.StdInputFile(shell, 'stdin')
        shell.push(['one\n', 'two\n', 'three\n', 'four\n'])
        self.assertEqual(f.readline(), 'one\n')
        self.assertEqual(f.readline(-1), 'two\n')
        self.assertEqual(f.readline(Tupu), 'three\n')
        shell.push(['one\ntwo\n'])
        self.assertEqual(f.readline(), 'one\n')
        self.assertEqual(f.readline(), 'two\n')
        shell.push(['one', 'two', 'three'])
        self.assertEqual(f.readline(), 'one')
        self.assertEqual(f.readline(), 'two')
        shell.push(['one\n', 'two\n', 'three\n'])
        self.assertEqual(f.readline(2), 'on')
        self.assertEqual(f.readline(1), 'e')
        self.assertEqual(f.readline(1), '\n')
        self.assertEqual(f.readline(10), 'two\n')

        shell.push(['one\n', 'two\n'])
        self.assertEqual(f.readline(0), '')
        self.assertRaises(TypeError, f.readlines, 1.5)
        self.assertRaises(TypeError, f.readlines, '1')
        self.assertRaises(TypeError, f.readlines, 1, 1)

    eleza test_readlines(self):
        shell = MockShell()
        f = run.StdInputFile(shell, 'stdin')
        shell.push(['one\n', 'two\n', ''])
        self.assertEqual(f.readlines(), ['one\n', 'two\n'])
        shell.push(['one\n', 'two\n', ''])
        self.assertEqual(f.readlines(-1), ['one\n', 'two\n'])
        shell.push(['one\n', 'two\n', ''])
        self.assertEqual(f.readlines(Tupu), ['one\n', 'two\n'])
        shell.push(['one\n', 'two\n', ''])
        self.assertEqual(f.readlines(0), ['one\n', 'two\n'])
        shell.push(['one\n', 'two\n', ''])
        self.assertEqual(f.readlines(3), ['one\n'])
        shell.push(['one\n', 'two\n', ''])
        self.assertEqual(f.readlines(4), ['one\n', 'two\n'])

        shell.push(['one\n', 'two\n', ''])
        self.assertRaises(TypeError, f.readlines, 1.5)
        self.assertRaises(TypeError, f.readlines, '1')
        self.assertRaises(TypeError, f.readlines, 1, 1)

    eleza test_close(self):
        shell = MockShell()
        f = run.StdInputFile(shell, 'stdin')
        shell.push(['one\n', 'two\n', ''])
        self.assertUongo(f.closed)
        self.assertEqual(f.readline(), 'one\n')
        f.close()
        self.assertUongo(f.closed)
        self.assertEqual(f.readline(), 'two\n')
        self.assertRaises(TypeError, f.close, 1)


kundi StdOutputFilesTest(unittest.TestCase):

    eleza test_misc(self):
        shell = MockShell()
        f = run.StdOutputFile(shell, 'stdout')
        self.assertIsInstance(f, io.TextIOBase)
        self.assertEqual(f.encoding, 'utf-8')
        self.assertEqual(f.errors, 'strict')
        self.assertIsTupu(f.newlines)
        self.assertEqual(f.name, '<stdout>')
        self.assertUongo(f.closed)
        self.assertKweli(f.isatty())
        self.assertUongo(f.readable())
        self.assertKweli(f.writable())
        self.assertUongo(f.seekable())

    eleza test_unsupported(self):
        shell = MockShell()
        f = run.StdOutputFile(shell, 'stdout')
        self.assertRaises(OSError, f.fileno)
        self.assertRaises(OSError, f.tell)
        self.assertRaises(OSError, f.seek, 0)
        self.assertRaises(OSError, f.read, 0)
        self.assertRaises(OSError, f.readline, 0)

    eleza test_write(self):
        shell = MockShell()
        f = run.StdOutputFile(shell, 'stdout')
        f.write('test')
        self.assertEqual(shell.written, [('test', 'stdout')])
        shell.reset()
        f.write('t\xe8\u015b\U0001d599')
        self.assertEqual(shell.written, [('t\xe8\u015b\U0001d599', 'stdout')])
        shell.reset()

        f.write(S('t\xe8\u015b\U0001d599'))
        self.assertEqual(shell.written, [('t\xe8\u015b\U0001d599', 'stdout')])
        self.assertEqual(type(shell.written[0][0]), str)
        shell.reset()

        self.assertRaises(TypeError, f.write)
        self.assertEqual(shell.written, [])
        self.assertRaises(TypeError, f.write, b'test')
        self.assertRaises(TypeError, f.write, 123)
        self.assertEqual(shell.written, [])
        self.assertRaises(TypeError, f.write, 'test', 'spam')
        self.assertEqual(shell.written, [])

    eleza test_write_stderr_nonencodable(self):
        shell = MockShell()
        f = run.StdOutputFile(shell, 'stderr', 'iso-8859-15', 'backslashreplace')
        f.write('t\xe8\u015b\U0001d599\xa4')
        self.assertEqual(shell.written, [('t\xe8\\u015b\\U0001d599\\xa4', 'stderr')])
        shell.reset()

        f.write(S('t\xe8\u015b\U0001d599\xa4'))
        self.assertEqual(shell.written, [('t\xe8\\u015b\\U0001d599\\xa4', 'stderr')])
        self.assertEqual(type(shell.written[0][0]), str)
        shell.reset()

        self.assertRaises(TypeError, f.write)
        self.assertEqual(shell.written, [])
        self.assertRaises(TypeError, f.write, b'test')
        self.assertRaises(TypeError, f.write, 123)
        self.assertEqual(shell.written, [])
        self.assertRaises(TypeError, f.write, 'test', 'spam')
        self.assertEqual(shell.written, [])

    eleza test_writelines(self):
        shell = MockShell()
        f = run.StdOutputFile(shell, 'stdout')
        f.writelines([])
        self.assertEqual(shell.written, [])
        shell.reset()
        f.writelines(['one\n', 'two'])
        self.assertEqual(shell.written,
                         [('one\n', 'stdout'), ('two', 'stdout')])
        shell.reset()
        f.writelines(['on\xe8\n', 'tw\xf2'])
        self.assertEqual(shell.written,
                         [('on\xe8\n', 'stdout'), ('tw\xf2', 'stdout')])
        shell.reset()

        f.writelines([S('t\xe8st')])
        self.assertEqual(shell.written, [('t\xe8st', 'stdout')])
        self.assertEqual(type(shell.written[0][0]), str)
        shell.reset()

        self.assertRaises(TypeError, f.writelines)
        self.assertEqual(shell.written, [])
        self.assertRaises(TypeError, f.writelines, 123)
        self.assertEqual(shell.written, [])
        self.assertRaises(TypeError, f.writelines, [b'test'])
        self.assertRaises(TypeError, f.writelines, [123])
        self.assertEqual(shell.written, [])
        self.assertRaises(TypeError, f.writelines, [], [])
        self.assertEqual(shell.written, [])

    eleza test_close(self):
        shell = MockShell()
        f = run.StdOutputFile(shell, 'stdout')
        self.assertUongo(f.closed)
        f.write('test')
        f.close()
        self.assertKweli(f.closed)
        self.assertRaises(ValueError, f.write, 'x')
        self.assertEqual(shell.written, [('test', 'stdout')])
        f.close()
        self.assertRaises(TypeError, f.close, 1)


kundi TestSysRecursionLimitWrappers(unittest.TestCase):

    eleza test_bad_setrecursionlimit_calls(self):
        run.install_recursionlimit_wrappers()
        self.addCleanup(run.uninstall_recursionlimit_wrappers)
        f = sys.setrecursionlimit
        self.assertRaises(TypeError, f, limit=100)
        self.assertRaises(TypeError, f, 100, 1000)
        self.assertRaises(ValueError, f, 0)

    eleza test_roundtrip(self):
        run.install_recursionlimit_wrappers()
        self.addCleanup(run.uninstall_recursionlimit_wrappers)

        # check that setting the recursion limit works
        orig_reclimit = sys.getrecursionlimit()
        self.addCleanup(sys.setrecursionlimit, orig_reclimit)
        sys.setrecursionlimit(orig_reclimit + 3)

        # check that the new limit ni rudishaed by sys.getrecursionlimit()
        new_reclimit = sys.getrecursionlimit()
        self.assertEqual(new_reclimit, orig_reclimit + 3)

    eleza test_default_recursion_limit_preserved(self):
        orig_reclimit = sys.getrecursionlimit()
        run.install_recursionlimit_wrappers()
        self.addCleanup(run.uninstall_recursionlimit_wrappers)
        new_reclimit = sys.getrecursionlimit()
        self.assertEqual(new_reclimit, orig_reclimit)

    eleza test_fixdoc(self):
        eleza func(): "docstring"
        run.fixdoc(func, "more")
        self.assertEqual(func.__doc__, "docstring\n\nmore")
        func.__doc__ = Tupu
        run.fixdoc(func, "more")
        self.assertEqual(func.__doc__, "more")


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
