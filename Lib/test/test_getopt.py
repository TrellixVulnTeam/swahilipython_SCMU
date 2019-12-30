# test_getopt.py
# David Goodger <dgoodger@bigfoot.com> 2000-08-19

kutoka test.support agiza verbose, run_doctest, EnvironmentVarGuard
agiza unittest

agiza getopt

sentinel = object()

kundi GetoptTests(unittest.TestCase):
    eleza setUp(self):
        self.env = EnvironmentVarGuard()
        ikiwa "POSIXLY_CORRECT" kwenye self.env:
            toa self.env["POSIXLY_CORRECT"]

    eleza tearDown(self):
        self.env.__exit__()
        toa self.env

    eleza assertError(self, *args, **kwargs):
        self.assertRaises(getopt.GetoptError, *args, **kwargs)

    eleza test_short_has_arg(self):
        self.assertKweli(getopt.short_has_arg('a', 'a:'))
        self.assertUongo(getopt.short_has_arg('a', 'a'))
        self.assertError(getopt.short_has_arg, 'a', 'b')

    eleza test_long_has_args(self):
        has_arg, option = getopt.long_has_args('abc', ['abc='])
        self.assertKweli(has_arg)
        self.assertEqual(option, 'abc')

        has_arg, option = getopt.long_has_args('abc', ['abc'])
        self.assertUongo(has_arg)
        self.assertEqual(option, 'abc')

        has_arg, option = getopt.long_has_args('abc', ['abcd'])
        self.assertUongo(has_arg)
        self.assertEqual(option, 'abcd')

        self.assertError(getopt.long_has_args, 'abc', ['def'])
        self.assertError(getopt.long_has_args, 'abc', [])
        self.assertError(getopt.long_has_args, 'abc', ['abcd','abcde'])

    eleza test_do_shorts(self):
        opts, args = getopt.do_shorts([], 'a', 'a', [])
        self.assertEqual(opts, [('-a', '')])
        self.assertEqual(args, [])

        opts, args = getopt.do_shorts([], 'a1', 'a:', [])
        self.assertEqual(opts, [('-a', '1')])
        self.assertEqual(args, [])

        #opts, args = getopt.do_shorts([], 'a=1', 'a:', [])
        #self.assertEqual(opts, [('-a', '1')])
        #self.assertEqual(args, [])

        opts, args = getopt.do_shorts([], 'a', 'a:', ['1'])
        self.assertEqual(opts, [('-a', '1')])
        self.assertEqual(args, [])

        opts, args = getopt.do_shorts([], 'a', 'a:', ['1', '2'])
        self.assertEqual(opts, [('-a', '1')])
        self.assertEqual(args, ['2'])

        self.assertError(getopt.do_shorts, [], 'a1', 'a', [])
        self.assertError(getopt.do_shorts, [], 'a', 'a:', [])

    eleza test_do_longs(self):
        opts, args = getopt.do_longs([], 'abc', ['abc'], [])
        self.assertEqual(opts, [('--abc', '')])
        self.assertEqual(args, [])

        opts, args = getopt.do_longs([], 'abc=1', ['abc='], [])
        self.assertEqual(opts, [('--abc', '1')])
        self.assertEqual(args, [])

        opts, args = getopt.do_longs([], 'abc=1', ['abcd='], [])
        self.assertEqual(opts, [('--abcd', '1')])
        self.assertEqual(args, [])

        opts, args = getopt.do_longs([], 'abc', ['ab', 'abc', 'abcd'], [])
        self.assertEqual(opts, [('--abc', '')])
        self.assertEqual(args, [])

        # Much like the preceding, except ukijumuisha a non-alpha character ("-") in
        # option name that precedes "="; failed in
        # http://python.org/sf/126863
        opts, args = getopt.do_longs([], 'foo=42', ['foo-bar', 'foo=',], [])
        self.assertEqual(opts, [('--foo', '42')])
        self.assertEqual(args, [])

        self.assertError(getopt.do_longs, [], 'abc=1', ['abc'], [])
        self.assertError(getopt.do_longs, [], 'abc', ['abc='], [])

    eleza test_getopt(self):
        # note: the empty string between '-a' na '--beta' ni significant:
        # it simulates an empty string option argument ('-a ""') on the
        # command line.
        cmdline = ['-a', '1', '-b', '--alpha=2', '--beta', '-a', '3', '-a',
                   '', '--beta', 'arg1', 'arg2']

        opts, args = getopt.getopt(cmdline, 'a:b', ['alpha=', 'beta'])
        self.assertEqual(opts, [('-a', '1'), ('-b', ''),
                                ('--alpha', '2'), ('--beta', ''),
                                ('-a', '3'), ('-a', ''), ('--beta', '')])
        # Note ambiguity of ('-b', '') na ('-a', '') above. This must be
        # accounted kila kwenye the code that calls getopt().
        self.assertEqual(args, ['arg1', 'arg2'])

        self.assertError(getopt.getopt, cmdline, 'a:b', ['alpha', 'beta'])

    eleza test_gnu_getopt(self):
        # Test handling of GNU style scanning mode.
        cmdline = ['-a', 'arg1', '-b', '1', '--alpha', '--beta=2']

        # GNU style
        opts, args = getopt.gnu_getopt(cmdline, 'ab:', ['alpha', 'beta='])
        self.assertEqual(args, ['arg1'])
        self.assertEqual(opts, [('-a', ''), ('-b', '1'),
                                ('--alpha', ''), ('--beta', '2')])

        # recognize "-" as an argument
        opts, args = getopt.gnu_getopt(['-a', '-', '-b', '-'], 'ab:', [])
        self.assertEqual(args, ['-'])
        self.assertEqual(opts, [('-a', ''), ('-b', '-')])

        # Posix style via +
        opts, args = getopt.gnu_getopt(cmdline, '+ab:', ['alpha', 'beta='])
        self.assertEqual(opts, [('-a', '')])
        self.assertEqual(args, ['arg1', '-b', '1', '--alpha', '--beta=2'])

        # Posix style via POSIXLY_CORRECT
        self.env["POSIXLY_CORRECT"] = "1"
        opts, args = getopt.gnu_getopt(cmdline, 'ab:', ['alpha', 'beta='])
        self.assertEqual(opts, [('-a', '')])
        self.assertEqual(args, ['arg1', '-b', '1', '--alpha', '--beta=2'])

    eleza test_libref_examples(self):
        s = """
        Examples kutoka the Library Reference:  Doc/lib/libgetopt.tex

        An example using only Unix style options:


        >>> agiza getopt
        >>> args = '-a -b -cfoo -d bar a1 a2'.split()
        >>> args
        ['-a', '-b', '-cfoo', '-d', 'bar', 'a1', 'a2']
        >>> optlist, args = getopt.getopt(args, 'abc:d:')
        >>> optlist
        [('-a', ''), ('-b', ''), ('-c', 'foo'), ('-d', 'bar')]
        >>> args
        ['a1', 'a2']

        Using long option names ni equally easy:


        >>> s = '--condition=foo --testing --output-file abc.eleza -x a1 a2'
        >>> args = s.split()
        >>> args
        ['--condition=foo', '--testing', '--output-file', 'abc.def', '-x', 'a1', 'a2']
        >>> optlist, args = getopt.getopt(args, 'x', [
        ...     'condition=', 'output-file=', 'testing'])
        >>> optlist
        [('--condition', 'foo'), ('--testing', ''), ('--output-file', 'abc.def'), ('-x', '')]
        >>> args
        ['a1', 'a2']
        """

        agiza types
        m = types.ModuleType("libreftest", s)
        run_doctest(m, verbose)

    eleza test_issue4629(self):
        longopts, shortopts = getopt.getopt(['--help='], '', ['help='])
        self.assertEqual(longopts, [('--help', '')])
        longopts, shortopts = getopt.getopt(['--help=x'], '', ['help='])
        self.assertEqual(longopts, [('--help', 'x')])
        self.assertRaises(getopt.GetoptError, getopt.getopt, ['--help='], '', ['help'])

ikiwa __name__ == "__main__":
    unittest.main()
