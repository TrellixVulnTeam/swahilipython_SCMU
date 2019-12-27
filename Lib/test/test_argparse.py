# Author: Steven J. Bethard <steven.bethard@gmail.com>.

agiza inspect
agiza os
agiza shutil
agiza stat
agiza sys
agiza textwrap
agiza tempfile
agiza unittest
agiza argparse

kutoka io agiza StringIO

kutoka test agiza support
kutoka unittest agiza mock
kundi StdIOBuffer(StringIO):
    pass

kundi TestCase(unittest.TestCase):

    eleza setUp(self):
        # The tests assume that line wrapping occurs at 80 columns, but this
        # behaviour can be overridden by setting the COLUMNS environment
        # variable.  To ensure that this width is used, set COLUMNS to 80.
        env = support.EnvironmentVarGuard()
        env['COLUMNS'] = '80'
        self.addCleanup(env.__exit__)


kundi TempDirMixin(object):

    eleza setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.old_dir = os.getcwd()
        os.chdir(self.temp_dir)

    eleza tearDown(self):
        os.chdir(self.old_dir)
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.chmod(os.path.join(self.temp_dir, name), stat.S_IWRITE)
        shutil.rmtree(self.temp_dir, True)

    eleza create_readonly_file(self, filename):
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w') as file:
            file.write(filename)
        os.chmod(file_path, stat.S_IREAD)

kundi Sig(object):

    eleza __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


kundi NS(object):

    eleza __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    eleza __repr__(self):
        sorted_items = sorted(self.__dict__.items())
        kwarg_str = ', '.join(['%s=%r' % tup for tup in sorted_items])
        rudisha '%s(%s)' % (type(self).__name__, kwarg_str)

    eleza __eq__(self, other):
        rudisha vars(self) == vars(other)


kundi ArgumentParserError(Exception):

    eleza __init__(self, message, stdout=None, stderr=None, error_code=None):
        Exception.__init__(self, message, stdout, stderr)
        self.message = message
        self.stdout = stdout
        self.stderr = stderr
        self.error_code = error_code


eleza stderr_to_parser_error(parse_args, *args, **kwargs):
    # ikiwa this is being called recursively and stderr or stdout is already being
    # redirected, simply call the function and let the enclosing function
    # catch the exception
    ikiwa isinstance(sys.stderr, StdIOBuffer) or isinstance(sys.stdout, StdIOBuffer):
        rudisha parse_args(*args, **kwargs)

    # ikiwa this is not being called recursively, redirect stderr and
    # use it as the ArgumentParserError message
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StdIOBuffer()
    sys.stderr = StdIOBuffer()
    try:
        try:
            result = parse_args(*args, **kwargs)
            for key in list(vars(result)):
                ikiwa getattr(result, key) is sys.stdout:
                    setattr(result, key, old_stdout)
                ikiwa getattr(result, key) is sys.stderr:
                    setattr(result, key, old_stderr)
            rudisha result
        except SystemExit:
            code = sys.exc_info()[1].code
            stdout = sys.stdout.getvalue()
            stderr = sys.stderr.getvalue()
            raise ArgumentParserError("SystemExit", stdout, stderr, code)
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


kundi ErrorRaisingArgumentParser(argparse.ArgumentParser):

    eleza parse_args(self, *args, **kwargs):
        parse_args = super(ErrorRaisingArgumentParser, self).parse_args
        rudisha stderr_to_parser_error(parse_args, *args, **kwargs)

    eleza exit(self, *args, **kwargs):
        exit = super(ErrorRaisingArgumentParser, self).exit
        rudisha stderr_to_parser_error(exit, *args, **kwargs)

    eleza error(self, *args, **kwargs):
        error = super(ErrorRaisingArgumentParser, self).error
        rudisha stderr_to_parser_error(error, *args, **kwargs)


kundi ParserTesterMetaclass(type):
    """Adds parser tests using the kundi attributes.

    Classes of this type should specify the following attributes:

    argument_signatures -- a list of Sig objects which specify
        the signatures of Argument objects to be created
    failures -- a list of args lists that should cause the parser
        to fail
    successes -- a list of (initial_args, options, remaining_args) tuples
        where initial_args specifies the string args to be parsed,
        options is a dict that should match the vars() of the options
        parsed out of initial_args, and remaining_args should be any
        remaining unparsed arguments
    """

    eleza __init__(cls, name, bases, bodydict):
        ikiwa name == 'ParserTestCase':
            return

        # default parser signature is empty
        ikiwa not hasattr(cls, 'parser_signature'):
            cls.parser_signature = Sig()
        ikiwa not hasattr(cls, 'parser_class'):
            cls.parser_kundi = ErrorRaisingArgumentParser

        # ---------------------------------------
        # functions for adding optional arguments
        # ---------------------------------------
        eleza no_groups(parser, argument_signatures):
            """Add all arguments directly to the parser"""
            for sig in argument_signatures:
                parser.add_argument(*sig.args, **sig.kwargs)

        eleza one_group(parser, argument_signatures):
            """Add all arguments under a single group in the parser"""
            group = parser.add_argument_group('foo')
            for sig in argument_signatures:
                group.add_argument(*sig.args, **sig.kwargs)

        eleza many_groups(parser, argument_signatures):
            """Add each argument in its own group to the parser"""
            for i, sig in enumerate(argument_signatures):
                group = parser.add_argument_group('foo:%i' % i)
                group.add_argument(*sig.args, **sig.kwargs)

        # --------------------------
        # functions for parsing args
        # --------------------------
        eleza listargs(parser, args):
            """Parse the args by passing in a list"""
            rudisha parser.parse_args(args)

        eleza sysargs(parser, args):
            """Parse the args by defaulting to sys.argv"""
            old_sys_argv = sys.argv
            sys.argv = [old_sys_argv[0]] + args
            try:
                rudisha parser.parse_args()
            finally:
                sys.argv = old_sys_argv

        # kundi that holds the combination of one optional argument
        # addition method and one arg parsing method
        kundi AddTests(object):

            eleza __init__(self, tester_cls, add_arguments, parse_args):
                self._add_arguments = add_arguments
                self._parse_args = parse_args

                add_arguments_name = self._add_arguments.__name__
                parse_args_name = self._parse_args.__name__
                for test_func in [self.test_failures, self.test_successes]:
                    func_name = test_func.__name__
                    names = func_name, add_arguments_name, parse_args_name
                    test_name = '_'.join(names)

                    eleza wrapper(self, test_func=test_func):
                        test_func(self)
                    try:
                        wrapper.__name__ = test_name
                    except TypeError:
                        pass
                    setattr(tester_cls, test_name, wrapper)

            eleza _get_parser(self, tester):
                args = tester.parser_signature.args
                kwargs = tester.parser_signature.kwargs
                parser = tester.parser_class(*args, **kwargs)
                self._add_arguments(parser, tester.argument_signatures)
                rudisha parser

            eleza test_failures(self, tester):
                parser = self._get_parser(tester)
                for args_str in tester.failures:
                    args = args_str.split()
                    with tester.assertRaises(ArgumentParserError, msg=args):
                        parser.parse_args(args)

            eleza test_successes(self, tester):
                parser = self._get_parser(tester)
                for args, expected_ns in tester.successes:
                    ikiwa isinstance(args, str):
                        args = args.split()
                    result_ns = self._parse_args(parser, args)
                    tester.assertEqual(expected_ns, result_ns)

        # add tests for each combination of an optionals adding method
        # and an arg parsing method
        for add_arguments in [no_groups, one_group, many_groups]:
            for parse_args in [listargs, sysargs]:
                AddTests(cls, add_arguments, parse_args)

bases = TestCase,
ParserTestCase = ParserTesterMetaclass('ParserTestCase', bases, {})

# ===============
# Optionals tests
# ===============

kundi TestOptionalsSingleDash(ParserTestCase):
    """Test an Optional with a single-dash option string"""

    argument_signatures = [Sig('-x')]
    failures = ['-x', 'a', '--foo', '-x --foo', '-x -y']
    successes = [
        ('', NS(x=None)),
        ('-x a', NS(x='a')),
        ('-xa', NS(x='a')),
        ('-x -1', NS(x='-1')),
        ('-x-1', NS(x='-1')),
    ]


kundi TestOptionalsSingleDashCombined(ParserTestCase):
    """Test an Optional with a single-dash option string"""

    argument_signatures = [
        Sig('-x', action='store_true'),
        Sig('-yyy', action='store_const', const=42),
        Sig('-z'),
    ]
    failures = ['a', '--foo', '-xa', '-x --foo', '-x -z', '-z -x',
                '-yx', '-yz a', '-yyyx', '-yyyza', '-xyza']
    successes = [
        ('', NS(x=False, yyy=None, z=None)),
        ('-x', NS(x=True, yyy=None, z=None)),
        ('-za', NS(x=False, yyy=None, z='a')),
        ('-z a', NS(x=False, yyy=None, z='a')),
        ('-xza', NS(x=True, yyy=None, z='a')),
        ('-xz a', NS(x=True, yyy=None, z='a')),
        ('-x -za', NS(x=True, yyy=None, z='a')),
        ('-x -z a', NS(x=True, yyy=None, z='a')),
        ('-y', NS(x=False, yyy=42, z=None)),
        ('-yyy', NS(x=False, yyy=42, z=None)),
        ('-x -yyy -za', NS(x=True, yyy=42, z='a')),
        ('-x -yyy -z a', NS(x=True, yyy=42, z='a')),
    ]


kundi TestOptionalsSingleDashLong(ParserTestCase):
    """Test an Optional with a multi-character single-dash option string"""

    argument_signatures = [Sig('-foo')]
    failures = ['-foo', 'a', '--foo', '-foo --foo', '-foo -y', '-fooa']
    successes = [
        ('', NS(foo=None)),
        ('-foo a', NS(foo='a')),
        ('-foo -1', NS(foo='-1')),
        ('-fo a', NS(foo='a')),
        ('-f a', NS(foo='a')),
    ]


kundi TestOptionalsSingleDashSubsetAmbiguous(ParserTestCase):
    """Test Optionals where option strings are subsets of each other"""

    argument_signatures = [Sig('-f'), Sig('-foobar'), Sig('-foorab')]
    failures = ['-f', '-foo', '-fo', '-foo b', '-foob', '-fooba', '-foora']
    successes = [
        ('', NS(f=None, foobar=None, foorab=None)),
        ('-f a', NS(f='a', foobar=None, foorab=None)),
        ('-fa', NS(f='a', foobar=None, foorab=None)),
        ('-foa', NS(f='oa', foobar=None, foorab=None)),
        ('-fooa', NS(f='ooa', foobar=None, foorab=None)),
        ('-foobar a', NS(f=None, foobar='a', foorab=None)),
        ('-foorab a', NS(f=None, foobar=None, foorab='a')),
    ]


kundi TestOptionalsSingleDashAmbiguous(ParserTestCase):
    """Test Optionals that partially match but are not subsets"""

    argument_signatures = [Sig('-foobar'), Sig('-foorab')]
    failures = ['-f', '-f a', '-fa', '-foa', '-foo', '-fo', '-foo b']
    successes = [
        ('', NS(foobar=None, foorab=None)),
        ('-foob a', NS(foobar='a', foorab=None)),
        ('-foor a', NS(foobar=None, foorab='a')),
        ('-fooba a', NS(foobar='a', foorab=None)),
        ('-foora a', NS(foobar=None, foorab='a')),
        ('-foobar a', NS(foobar='a', foorab=None)),
        ('-foorab a', NS(foobar=None, foorab='a')),
    ]


kundi TestOptionalsNumeric(ParserTestCase):
    """Test an Optional with a short opt string"""

    argument_signatures = [Sig('-1', dest='one')]
    failures = ['-1', 'a', '-1 --foo', '-1 -y', '-1 -1', '-1 -2']
    successes = [
        ('', NS(one=None)),
        ('-1 a', NS(one='a')),
        ('-1a', NS(one='a')),
        ('-1-2', NS(one='-2')),
    ]


kundi TestOptionalsDoubleDash(ParserTestCase):
    """Test an Optional with a double-dash option string"""

    argument_signatures = [Sig('--foo')]
    failures = ['--foo', '-f', '-f a', 'a', '--foo -x', '--foo --bar']
    successes = [
        ('', NS(foo=None)),
        ('--foo a', NS(foo='a')),
        ('--foo=a', NS(foo='a')),
        ('--foo -2.5', NS(foo='-2.5')),
        ('--foo=-2.5', NS(foo='-2.5')),
    ]


kundi TestOptionalsDoubleDashPartialMatch(ParserTestCase):
    """Tests partial matching with a double-dash option string"""

    argument_signatures = [
        Sig('--badger', action='store_true'),
        Sig('--bat'),
    ]
    failures = ['--bar', '--b', '--ba', '--b=2', '--ba=4', '--badge 5']
    successes = [
        ('', NS(badger=False, bat=None)),
        ('--bat X', NS(badger=False, bat='X')),
        ('--bad', NS(badger=True, bat=None)),
        ('--badg', NS(badger=True, bat=None)),
        ('--badge', NS(badger=True, bat=None)),
        ('--badger', NS(badger=True, bat=None)),
    ]


kundi TestOptionalsDoubleDashPrefixMatch(ParserTestCase):
    """Tests when one double-dash option string is a prefix of another"""

    argument_signatures = [
        Sig('--badger', action='store_true'),
        Sig('--ba'),
    ]
    failures = ['--bar', '--b', '--ba', '--b=2', '--badge 5']
    successes = [
        ('', NS(badger=False, ba=None)),
        ('--ba X', NS(badger=False, ba='X')),
        ('--ba=X', NS(badger=False, ba='X')),
        ('--bad', NS(badger=True, ba=None)),
        ('--badg', NS(badger=True, ba=None)),
        ('--badge', NS(badger=True, ba=None)),
        ('--badger', NS(badger=True, ba=None)),
    ]


kundi TestOptionalsSingleDoubleDash(ParserTestCase):
    """Test an Optional with single- and double-dash option strings"""

    argument_signatures = [
        Sig('-f', action='store_true'),
        Sig('--bar'),
        Sig('-baz', action='store_const', const=42),
    ]
    failures = ['--bar', '-fbar', '-fbaz', '-bazf', '-b B', 'B']
    successes = [
        ('', NS(f=False, bar=None, baz=None)),
        ('-f', NS(f=True, bar=None, baz=None)),
        ('--ba B', NS(f=False, bar='B', baz=None)),
        ('-f --bar B', NS(f=True, bar='B', baz=None)),
        ('-f -b', NS(f=True, bar=None, baz=42)),
        ('-ba -f', NS(f=True, bar=None, baz=42)),
    ]


kundi TestOptionalsAlternatePrefixChars(ParserTestCase):
    """Test an Optional with option strings with custom prefixes"""

    parser_signature = Sig(prefix_chars='+:/', add_help=False)
    argument_signatures = [
        Sig('+f', action='store_true'),
        Sig('::bar'),
        Sig('/baz', action='store_const', const=42),
    ]
    failures = ['--bar', '-fbar', '-b B', 'B', '-f', '--bar B', '-baz', '-h', '--help', '+h', '::help', '/help']
    successes = [
        ('', NS(f=False, bar=None, baz=None)),
        ('+f', NS(f=True, bar=None, baz=None)),
        ('::ba B', NS(f=False, bar='B', baz=None)),
        ('+f ::bar B', NS(f=True, bar='B', baz=None)),
        ('+f /b', NS(f=True, bar=None, baz=42)),
        ('/ba +f', NS(f=True, bar=None, baz=42)),
    ]


kundi TestOptionalsAlternatePrefixCharsAddedHelp(ParserTestCase):
    """When ``-`` not in prefix_chars, default operators created for help
       should use the prefix_chars in use rather than - or --
       http://bugs.python.org/issue9444"""

    parser_signature = Sig(prefix_chars='+:/', add_help=True)
    argument_signatures = [
        Sig('+f', action='store_true'),
        Sig('::bar'),
        Sig('/baz', action='store_const', const=42),
    ]
    failures = ['--bar', '-fbar', '-b B', 'B', '-f', '--bar B', '-baz']
    successes = [
        ('', NS(f=False, bar=None, baz=None)),
        ('+f', NS(f=True, bar=None, baz=None)),
        ('::ba B', NS(f=False, bar='B', baz=None)),
        ('+f ::bar B', NS(f=True, bar='B', baz=None)),
        ('+f /b', NS(f=True, bar=None, baz=42)),
        ('/ba +f', NS(f=True, bar=None, baz=42))
    ]


kundi TestOptionalsAlternatePrefixCharsMultipleShortArgs(ParserTestCase):
    """Verify that Optionals must be called with their defined prefixes"""

    parser_signature = Sig(prefix_chars='+-', add_help=False)
    argument_signatures = [
        Sig('-x', action='store_true'),
        Sig('+y', action='store_true'),
        Sig('+z', action='store_true'),
    ]
    failures = ['-w',
                '-xyz',
                '+x',
                '-y',
                '+xyz',
    ]
    successes = [
        ('', NS(x=False, y=False, z=False)),
        ('-x', NS(x=True, y=False, z=False)),
        ('+y -x', NS(x=True, y=True, z=False)),
        ('+yz -x', NS(x=True, y=True, z=True)),
    ]


kundi TestOptionalsShortLong(ParserTestCase):
    """Test a combination of single- and double-dash option strings"""

    argument_signatures = [
        Sig('-v', '--verbose', '-n', '--noisy', action='store_true'),
    ]
    failures = ['--x --verbose', '-N', 'a', '-v x']
    successes = [
        ('', NS(verbose=False)),
        ('-v', NS(verbose=True)),
        ('--verbose', NS(verbose=True)),
        ('-n', NS(verbose=True)),
        ('--noisy', NS(verbose=True)),
    ]


kundi TestOptionalsDest(ParserTestCase):
    """Tests various means of setting destination"""

    argument_signatures = [Sig('--foo-bar'), Sig('--baz', dest='zabbaz')]
    failures = ['a']
    successes = [
        ('--foo-bar f', NS(foo_bar='f', zabbaz=None)),
        ('--baz g', NS(foo_bar=None, zabbaz='g')),
        ('--foo-bar h --baz i', NS(foo_bar='h', zabbaz='i')),
        ('--baz j --foo-bar k', NS(foo_bar='k', zabbaz='j')),
    ]


kundi TestOptionalsDefault(ParserTestCase):
    """Tests specifying a default for an Optional"""

    argument_signatures = [Sig('-x'), Sig('-y', default=42)]
    failures = ['a']
    successes = [
        ('', NS(x=None, y=42)),
        ('-xx', NS(x='x', y=42)),
        ('-yy', NS(x=None, y='y')),
    ]


kundi TestOptionalsNargsDefault(ParserTestCase):
    """Tests not specifying the number of args for an Optional"""

    argument_signatures = [Sig('-x')]
    failures = ['a', '-x']
    successes = [
        ('', NS(x=None)),
        ('-x a', NS(x='a')),
    ]


kundi TestOptionalsNargs1(ParserTestCase):
    """Tests specifying 1 arg for an Optional"""

    argument_signatures = [Sig('-x', nargs=1)]
    failures = ['a', '-x']
    successes = [
        ('', NS(x=None)),
        ('-x a', NS(x=['a'])),
    ]


kundi TestOptionalsNargs3(ParserTestCase):
    """Tests specifying 3 args for an Optional"""

    argument_signatures = [Sig('-x', nargs=3)]
    failures = ['a', '-x', '-x a', '-x a b', 'a -x', 'a -x b']
    successes = [
        ('', NS(x=None)),
        ('-x a b c', NS(x=['a', 'b', 'c'])),
    ]


kundi TestOptionalsNargsOptional(ParserTestCase):
    """Tests specifying an Optional arg for an Optional"""

    argument_signatures = [
        Sig('-w', nargs='?'),
        Sig('-x', nargs='?', const=42),
        Sig('-y', nargs='?', default='spam'),
        Sig('-z', nargs='?', type=int, const='42', default='84'),
    ]
    failures = ['2']
    successes = [
        ('', NS(w=None, x=None, y='spam', z=84)),
        ('-w', NS(w=None, x=None, y='spam', z=84)),
        ('-w 2', NS(w='2', x=None, y='spam', z=84)),
        ('-x', NS(w=None, x=42, y='spam', z=84)),
        ('-x 2', NS(w=None, x='2', y='spam', z=84)),
        ('-y', NS(w=None, x=None, y=None, z=84)),
        ('-y 2', NS(w=None, x=None, y='2', z=84)),
        ('-z', NS(w=None, x=None, y='spam', z=42)),
        ('-z 2', NS(w=None, x=None, y='spam', z=2)),
    ]


kundi TestOptionalsNargsZeroOrMore(ParserTestCase):
    """Tests specifying args for an Optional that accepts zero or more"""

    argument_signatures = [
        Sig('-x', nargs='*'),
        Sig('-y', nargs='*', default='spam'),
    ]
    failures = ['a']
    successes = [
        ('', NS(x=None, y='spam')),
        ('-x', NS(x=[], y='spam')),
        ('-x a', NS(x=['a'], y='spam')),
        ('-x a b', NS(x=['a', 'b'], y='spam')),
        ('-y', NS(x=None, y=[])),
        ('-y a', NS(x=None, y=['a'])),
        ('-y a b', NS(x=None, y=['a', 'b'])),
    ]


kundi TestOptionalsNargsOneOrMore(ParserTestCase):
    """Tests specifying args for an Optional that accepts one or more"""

    argument_signatures = [
        Sig('-x', nargs='+'),
        Sig('-y', nargs='+', default='spam'),
    ]
    failures = ['a', '-x', '-y', 'a -x', 'a -y b']
    successes = [
        ('', NS(x=None, y='spam')),
        ('-x a', NS(x=['a'], y='spam')),
        ('-x a b', NS(x=['a', 'b'], y='spam')),
        ('-y a', NS(x=None, y=['a'])),
        ('-y a b', NS(x=None, y=['a', 'b'])),
    ]


kundi TestOptionalsChoices(ParserTestCase):
    """Tests specifying the choices for an Optional"""

    argument_signatures = [
        Sig('-f', choices='abc'),
        Sig('-g', type=int, choices=range(5))]
    failures = ['a', '-f d', '-fad', '-ga', '-g 6']
    successes = [
        ('', NS(f=None, g=None)),
        ('-f a', NS(f='a', g=None)),
        ('-f c', NS(f='c', g=None)),
        ('-g 0', NS(f=None, g=0)),
        ('-g 03', NS(f=None, g=3)),
        ('-fb -g4', NS(f='b', g=4)),
    ]


kundi TestOptionalsRequired(ParserTestCase):
    """Tests an optional action that is required"""

    argument_signatures = [
        Sig('-x', type=int, required=True),
    ]
    failures = ['a', '']
    successes = [
        ('-x 1', NS(x=1)),
        ('-x42', NS(x=42)),
    ]


kundi TestOptionalsActionStore(ParserTestCase):
    """Tests the store action for an Optional"""

    argument_signatures = [Sig('-x', action='store')]
    failures = ['a', 'a -x']
    successes = [
        ('', NS(x=None)),
        ('-xfoo', NS(x='foo')),
    ]


kundi TestOptionalsActionStoreConst(ParserTestCase):
    """Tests the store_const action for an Optional"""

    argument_signatures = [Sig('-y', action='store_const', const=object)]
    failures = ['a']
    successes = [
        ('', NS(y=None)),
        ('-y', NS(y=object)),
    ]


kundi TestOptionalsActionStoreFalse(ParserTestCase):
    """Tests the store_false action for an Optional"""

    argument_signatures = [Sig('-z', action='store_false')]
    failures = ['a', '-za', '-z a']
    successes = [
        ('', NS(z=True)),
        ('-z', NS(z=False)),
    ]


kundi TestOptionalsActionStoreTrue(ParserTestCase):
    """Tests the store_true action for an Optional"""

    argument_signatures = [Sig('--apple', action='store_true')]
    failures = ['a', '--apple=b', '--apple b']
    successes = [
        ('', NS(apple=False)),
        ('--apple', NS(apple=True)),
    ]


kundi TestOptionalsActionAppend(ParserTestCase):
    """Tests the append action for an Optional"""

    argument_signatures = [Sig('--baz', action='append')]
    failures = ['a', '--baz', 'a --baz', '--baz a b']
    successes = [
        ('', NS(baz=None)),
        ('--baz a', NS(baz=['a'])),
        ('--baz a --baz b', NS(baz=['a', 'b'])),
    ]


kundi TestOptionalsActionAppendWithDefault(ParserTestCase):
    """Tests the append action for an Optional"""

    argument_signatures = [Sig('--baz', action='append', default=['X'])]
    failures = ['a', '--baz', 'a --baz', '--baz a b']
    successes = [
        ('', NS(baz=['X'])),
        ('--baz a', NS(baz=['X', 'a'])),
        ('--baz a --baz b', NS(baz=['X', 'a', 'b'])),
    ]


kundi TestOptionalsActionAppendConst(ParserTestCase):
    """Tests the append_const action for an Optional"""

    argument_signatures = [
        Sig('-b', action='append_const', const=Exception),
        Sig('-c', action='append', dest='b'),
    ]
    failures = ['a', '-c', 'a -c', '-bx', '-b x']
    successes = [
        ('', NS(b=None)),
        ('-b', NS(b=[Exception])),
        ('-b -cx -b -cyz', NS(b=[Exception, 'x', Exception, 'yz'])),
    ]


kundi TestOptionalsActionAppendConstWithDefault(ParserTestCase):
    """Tests the append_const action for an Optional"""

    argument_signatures = [
        Sig('-b', action='append_const', const=Exception, default=['X']),
        Sig('-c', action='append', dest='b'),
    ]
    failures = ['a', '-c', 'a -c', '-bx', '-b x']
    successes = [
        ('', NS(b=['X'])),
        ('-b', NS(b=['X', Exception])),
        ('-b -cx -b -cyz', NS(b=['X', Exception, 'x', Exception, 'yz'])),
    ]


kundi TestOptionalsActionCount(ParserTestCase):
    """Tests the count action for an Optional"""

    argument_signatures = [Sig('-x', action='count')]
    failures = ['a', '-x a', '-x b', '-x a -x b']
    successes = [
        ('', NS(x=None)),
        ('-x', NS(x=1)),
    ]


kundi TestOptionalsAllowLongAbbreviation(ParserTestCase):
    """Allow long options to be abbreviated unambiguously"""

    argument_signatures = [
        Sig('--foo'),
        Sig('--foobaz'),
        Sig('--fooble', action='store_true'),
    ]
    failures = ['--foob 5', '--foob']
    successes = [
        ('', NS(foo=None, foobaz=None, fooble=False)),
        ('--foo 7', NS(foo='7', foobaz=None, fooble=False)),
        ('--fooba a', NS(foo=None, foobaz='a', fooble=False)),
        ('--foobl --foo g', NS(foo='g', foobaz=None, fooble=True)),
    ]


kundi TestOptionalsDisallowLongAbbreviation(ParserTestCase):
    """Do not allow abbreviations of long options at all"""

    parser_signature = Sig(allow_abbrev=False)
    argument_signatures = [
        Sig('--foo'),
        Sig('--foodle', action='store_true'),
        Sig('--foonly'),
    ]
    failures = ['-foon 3', '--foon 3', '--food', '--food --foo 2']
    successes = [
        ('', NS(foo=None, foodle=False, foonly=None)),
        ('--foo 3', NS(foo='3', foodle=False, foonly=None)),
        ('--foonly 7 --foodle --foo 2', NS(foo='2', foodle=True, foonly='7')),
    ]


kundi TestDisallowLongAbbreviationAllowsShortGrouping(ParserTestCase):
    """Do not allow abbreviations of long options at all"""

    parser_signature = Sig(allow_abbrev=False)
    argument_signatures = [
        Sig('-r'),
        Sig('-c', action='count'),
    ]
    failures = ['-r', '-c -r']
    successes = [
        ('', NS(r=None, c=None)),
        ('-ra', NS(r='a', c=None)),
        ('-rcc', NS(r='cc', c=None)),
        ('-cc', NS(r=None, c=2)),
        ('-cc -ra', NS(r='a', c=2)),
        ('-ccrcc', NS(r='cc', c=2)),
    ]

# ================
# Positional tests
# ================

kundi TestPositionalsNargsNone(ParserTestCase):
    """Test a Positional that doesn't specify nargs"""

    argument_signatures = [Sig('foo')]
    failures = ['', '-x', 'a b']
    successes = [
        ('a', NS(foo='a')),
    ]


kundi TestPositionalsNargs1(ParserTestCase):
    """Test a Positional that specifies an nargs of 1"""

    argument_signatures = [Sig('foo', nargs=1)]
    failures = ['', '-x', 'a b']
    successes = [
        ('a', NS(foo=['a'])),
    ]


kundi TestPositionalsNargs2(ParserTestCase):
    """Test a Positional that specifies an nargs of 2"""

    argument_signatures = [Sig('foo', nargs=2)]
    failures = ['', 'a', '-x', 'a b c']
    successes = [
        ('a b', NS(foo=['a', 'b'])),
    ]


kundi TestPositionalsNargsZeroOrMore(ParserTestCase):
    """Test a Positional that specifies unlimited nargs"""

    argument_signatures = [Sig('foo', nargs='*')]
    failures = ['-x']
    successes = [
        ('', NS(foo=[])),
        ('a', NS(foo=['a'])),
        ('a b', NS(foo=['a', 'b'])),
    ]


kundi TestPositionalsNargsZeroOrMoreDefault(ParserTestCase):
    """Test a Positional that specifies unlimited nargs and a default"""

    argument_signatures = [Sig('foo', nargs='*', default='bar')]
    failures = ['-x']
    successes = [
        ('', NS(foo='bar')),
        ('a', NS(foo=['a'])),
        ('a b', NS(foo=['a', 'b'])),
    ]


kundi TestPositionalsNargsOneOrMore(ParserTestCase):
    """Test a Positional that specifies one or more nargs"""

    argument_signatures = [Sig('foo', nargs='+')]
    failures = ['', '-x']
    successes = [
        ('a', NS(foo=['a'])),
        ('a b', NS(foo=['a', 'b'])),
    ]


kundi TestPositionalsNargsOptional(ParserTestCase):
    """Tests an Optional Positional"""

    argument_signatures = [Sig('foo', nargs='?')]
    failures = ['-x', 'a b']
    successes = [
        ('', NS(foo=None)),
        ('a', NS(foo='a')),
    ]


kundi TestPositionalsNargsOptionalDefault(ParserTestCase):
    """Tests an Optional Positional with a default value"""

    argument_signatures = [Sig('foo', nargs='?', default=42)]
    failures = ['-x', 'a b']
    successes = [
        ('', NS(foo=42)),
        ('a', NS(foo='a')),
    ]


kundi TestPositionalsNargsOptionalConvertedDefault(ParserTestCase):
    """Tests an Optional Positional with a default value
    that needs to be converted to the appropriate type.
    """

    argument_signatures = [
        Sig('foo', nargs='?', type=int, default='42'),
    ]
    failures = ['-x', 'a b', '1 2']
    successes = [
        ('', NS(foo=42)),
        ('1', NS(foo=1)),
    ]


kundi TestPositionalsNargsNoneNone(ParserTestCase):
    """Test two Positionals that don't specify nargs"""

    argument_signatures = [Sig('foo'), Sig('bar')]
    failures = ['', '-x', 'a', 'a b c']
    successes = [
        ('a b', NS(foo='a', bar='b')),
    ]


kundi TestPositionalsNargsNone1(ParserTestCase):
    """Test a Positional with no nargs followed by one with 1"""

    argument_signatures = [Sig('foo'), Sig('bar', nargs=1)]
    failures = ['', '--foo', 'a', 'a b c']
    successes = [
        ('a b', NS(foo='a', bar=['b'])),
    ]


kundi TestPositionalsNargs2None(ParserTestCase):
    """Test a Positional with 2 nargs followed by one with none"""

    argument_signatures = [Sig('foo', nargs=2), Sig('bar')]
    failures = ['', '--foo', 'a', 'a b', 'a b c d']
    successes = [
        ('a b c', NS(foo=['a', 'b'], bar='c')),
    ]


kundi TestPositionalsNargsNoneZeroOrMore(ParserTestCase):
    """Test a Positional with no nargs followed by one with unlimited"""

    argument_signatures = [Sig('foo'), Sig('bar', nargs='*')]
    failures = ['', '--foo']
    successes = [
        ('a', NS(foo='a', bar=[])),
        ('a b', NS(foo='a', bar=['b'])),
        ('a b c', NS(foo='a', bar=['b', 'c'])),
    ]


kundi TestPositionalsNargsNoneOneOrMore(ParserTestCase):
    """Test a Positional with no nargs followed by one with one or more"""

    argument_signatures = [Sig('foo'), Sig('bar', nargs='+')]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo='a', bar=['b'])),
        ('a b c', NS(foo='a', bar=['b', 'c'])),
    ]


kundi TestPositionalsNargsNoneOptional(ParserTestCase):
    """Test a Positional with no nargs followed by one with an Optional"""

    argument_signatures = [Sig('foo'), Sig('bar', nargs='?')]
    failures = ['', '--foo', 'a b c']
    successes = [
        ('a', NS(foo='a', bar=None)),
        ('a b', NS(foo='a', bar='b')),
    ]


kundi TestPositionalsNargsZeroOrMoreNone(ParserTestCase):
    """Test a Positional with unlimited nargs followed by one with none"""

    argument_signatures = [Sig('foo', nargs='*'), Sig('bar')]
    failures = ['', '--foo']
    successes = [
        ('a', NS(foo=[], bar='a')),
        ('a b', NS(foo=['a'], bar='b')),
        ('a b c', NS(foo=['a', 'b'], bar='c')),
    ]


kundi TestPositionalsNargsOneOrMoreNone(ParserTestCase):
    """Test a Positional with one or more nargs followed by one with none"""

    argument_signatures = [Sig('foo', nargs='+'), Sig('bar')]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo=['a'], bar='b')),
        ('a b c', NS(foo=['a', 'b'], bar='c')),
    ]


kundi TestPositionalsNargsOptionalNone(ParserTestCase):
    """Test a Positional with an Optional nargs followed by one with none"""

    argument_signatures = [Sig('foo', nargs='?', default=42), Sig('bar')]
    failures = ['', '--foo', 'a b c']
    successes = [
        ('a', NS(foo=42, bar='a')),
        ('a b', NS(foo='a', bar='b')),
    ]


kundi TestPositionalsNargs2ZeroOrMore(ParserTestCase):
    """Test a Positional with 2 nargs followed by one with unlimited"""

    argument_signatures = [Sig('foo', nargs=2), Sig('bar', nargs='*')]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo=['a', 'b'], bar=[])),
        ('a b c', NS(foo=['a', 'b'], bar=['c'])),
    ]


kundi TestPositionalsNargs2OneOrMore(ParserTestCase):
    """Test a Positional with 2 nargs followed by one with one or more"""

    argument_signatures = [Sig('foo', nargs=2), Sig('bar', nargs='+')]
    failures = ['', '--foo', 'a', 'a b']
    successes = [
        ('a b c', NS(foo=['a', 'b'], bar=['c'])),
    ]


kundi TestPositionalsNargs2Optional(ParserTestCase):
    """Test a Positional with 2 nargs followed by one optional"""

    argument_signatures = [Sig('foo', nargs=2), Sig('bar', nargs='?')]
    failures = ['', '--foo', 'a', 'a b c d']
    successes = [
        ('a b', NS(foo=['a', 'b'], bar=None)),
        ('a b c', NS(foo=['a', 'b'], bar='c')),
    ]


kundi TestPositionalsNargsZeroOrMore1(ParserTestCase):
    """Test a Positional with unlimited nargs followed by one with 1"""

    argument_signatures = [Sig('foo', nargs='*'), Sig('bar', nargs=1)]
    failures = ['', '--foo', ]
    successes = [
        ('a', NS(foo=[], bar=['a'])),
        ('a b', NS(foo=['a'], bar=['b'])),
        ('a b c', NS(foo=['a', 'b'], bar=['c'])),
    ]


kundi TestPositionalsNargsOneOrMore1(ParserTestCase):
    """Test a Positional with one or more nargs followed by one with 1"""

    argument_signatures = [Sig('foo', nargs='+'), Sig('bar', nargs=1)]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo=['a'], bar=['b'])),
        ('a b c', NS(foo=['a', 'b'], bar=['c'])),
    ]


kundi TestPositionalsNargsOptional1(ParserTestCase):
    """Test a Positional with an Optional nargs followed by one with 1"""

    argument_signatures = [Sig('foo', nargs='?'), Sig('bar', nargs=1)]
    failures = ['', '--foo', 'a b c']
    successes = [
        ('a', NS(foo=None, bar=['a'])),
        ('a b', NS(foo='a', bar=['b'])),
    ]


kundi TestPositionalsNargsNoneZeroOrMore1(ParserTestCase):
    """Test three Positionals: no nargs, unlimited nargs and 1 nargs"""

    argument_signatures = [
        Sig('foo'),
        Sig('bar', nargs='*'),
        Sig('baz', nargs=1),
    ]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo='a', bar=[], baz=['b'])),
        ('a b c', NS(foo='a', bar=['b'], baz=['c'])),
    ]


kundi TestPositionalsNargsNoneOneOrMore1(ParserTestCase):
    """Test three Positionals: no nargs, one or more nargs and 1 nargs"""

    argument_signatures = [
        Sig('foo'),
        Sig('bar', nargs='+'),
        Sig('baz', nargs=1),
    ]
    failures = ['', '--foo', 'a', 'b']
    successes = [
        ('a b c', NS(foo='a', bar=['b'], baz=['c'])),
        ('a b c d', NS(foo='a', bar=['b', 'c'], baz=['d'])),
    ]


kundi TestPositionalsNargsNoneOptional1(ParserTestCase):
    """Test three Positionals: no nargs, optional narg and 1 nargs"""

    argument_signatures = [
        Sig('foo'),
        Sig('bar', nargs='?', default=0.625),
        Sig('baz', nargs=1),
    ]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo='a', bar=0.625, baz=['b'])),
        ('a b c', NS(foo='a', bar='b', baz=['c'])),
    ]


kundi TestPositionalsNargsOptionalOptional(ParserTestCase):
    """Test two optional nargs"""

    argument_signatures = [
        Sig('foo', nargs='?'),
        Sig('bar', nargs='?', default=42),
    ]
    failures = ['--foo', 'a b c']
    successes = [
        ('', NS(foo=None, bar=42)),
        ('a', NS(foo='a', bar=42)),
        ('a b', NS(foo='a', bar='b')),
    ]


kundi TestPositionalsNargsOptionalZeroOrMore(ParserTestCase):
    """Test an Optional narg followed by unlimited nargs"""

    argument_signatures = [Sig('foo', nargs='?'), Sig('bar', nargs='*')]
    failures = ['--foo']
    successes = [
        ('', NS(foo=None, bar=[])),
        ('a', NS(foo='a', bar=[])),
        ('a b', NS(foo='a', bar=['b'])),
        ('a b c', NS(foo='a', bar=['b', 'c'])),
    ]


kundi TestPositionalsNargsOptionalOneOrMore(ParserTestCase):
    """Test an Optional narg followed by one or more nargs"""

    argument_signatures = [Sig('foo', nargs='?'), Sig('bar', nargs='+')]
    failures = ['', '--foo']
    successes = [
        ('a', NS(foo=None, bar=['a'])),
        ('a b', NS(foo='a', bar=['b'])),
        ('a b c', NS(foo='a', bar=['b', 'c'])),
    ]


kundi TestPositionalsChoicesString(ParserTestCase):
    """Test a set of single-character choices"""

    argument_signatures = [Sig('spam', choices=set('abcdefg'))]
    failures = ['', '--foo', 'h', '42', 'ef']
    successes = [
        ('a', NS(spam='a')),
        ('g', NS(spam='g')),
    ]


kundi TestPositionalsChoicesInt(ParserTestCase):
    """Test a set of integer choices"""

    argument_signatures = [Sig('spam', type=int, choices=range(20))]
    failures = ['', '--foo', 'h', '42', 'ef']
    successes = [
        ('4', NS(spam=4)),
        ('15', NS(spam=15)),
    ]


kundi TestPositionalsActionAppend(ParserTestCase):
    """Test the 'append' action"""

    argument_signatures = [
        Sig('spam', action='append'),
        Sig('spam', action='append', nargs=2),
    ]
    failures = ['', '--foo', 'a', 'a b', 'a b c d']
    successes = [
        ('a b c', NS(spam=['a', ['b', 'c']])),
    ]

# ========================================
# Combined optionals and positionals tests
# ========================================

kundi TestOptionalsNumericAndPositionals(ParserTestCase):
    """Tests negative number args when numeric options are present"""

    argument_signatures = [
        Sig('x', nargs='?'),
        Sig('-4', dest='y', action='store_true'),
    ]
    failures = ['-2', '-315']
    successes = [
        ('', NS(x=None, y=False)),
        ('a', NS(x='a', y=False)),
        ('-4', NS(x=None, y=True)),
        ('-4 a', NS(x='a', y=True)),
    ]


kundi TestOptionalsAlmostNumericAndPositionals(ParserTestCase):
    """Tests negative number args when almost numeric options are present"""

    argument_signatures = [
        Sig('x', nargs='?'),
        Sig('-k4', dest='y', action='store_true'),
    ]
    failures = ['-k3']
    successes = [
        ('', NS(x=None, y=False)),
        ('-2', NS(x='-2', y=False)),
        ('a', NS(x='a', y=False)),
        ('-k4', NS(x=None, y=True)),
        ('-k4 a', NS(x='a', y=True)),
    ]


kundi TestEmptyAndSpaceContainingArguments(ParserTestCase):

    argument_signatures = [
        Sig('x', nargs='?'),
        Sig('-y', '--yyy', dest='y'),
    ]
    failures = ['-y']
    successes = [
        ([''], NS(x='', y=None)),
        (['a badger'], NS(x='a badger', y=None)),
        (['-a badger'], NS(x='-a badger', y=None)),
        (['-y', ''], NS(x=None, y='')),
        (['-y', 'a badger'], NS(x=None, y='a badger')),
        (['-y', '-a badger'], NS(x=None, y='-a badger')),
        (['--yyy=a badger'], NS(x=None, y='a badger')),
        (['--yyy=-a badger'], NS(x=None, y='-a badger')),
    ]


kundi TestPrefixCharacterOnlyArguments(ParserTestCase):

    parser_signature = Sig(prefix_chars='-+')
    argument_signatures = [
        Sig('-', dest='x', nargs='?', const='badger'),
        Sig('+', dest='y', type=int, default=42),
        Sig('-+-', dest='z', action='store_true'),
    ]
    failures = ['-y', '+ -']
    successes = [
        ('', NS(x=None, y=42, z=False)),
        ('-', NS(x='badger', y=42, z=False)),
        ('- X', NS(x='X', y=42, z=False)),
        ('+ -3', NS(x=None, y=-3, z=False)),
        ('-+-', NS(x=None, y=42, z=True)),
        ('- ===', NS(x='===', y=42, z=False)),
    ]


kundi TestNargsZeroOrMore(ParserTestCase):
    """Tests specifying args for an Optional that accepts zero or more"""

    argument_signatures = [Sig('-x', nargs='*'), Sig('y', nargs='*')]
    failures = []
    successes = [
        ('', NS(x=None, y=[])),
        ('-x', NS(x=[], y=[])),
        ('-x a', NS(x=['a'], y=[])),
        ('-x a -- b', NS(x=['a'], y=['b'])),
        ('a', NS(x=None, y=['a'])),
        ('a -x', NS(x=[], y=['a'])),
        ('a -x b', NS(x=['b'], y=['a'])),
    ]


kundi TestNargsRemainder(ParserTestCase):
    """Tests specifying a positional with nargs=REMAINDER"""

    argument_signatures = [Sig('x'), Sig('y', nargs='...'), Sig('-z')]
    failures = ['', '-z', '-z Z']
    successes = [
        ('X', NS(x='X', y=[], z=None)),
        ('-z Z X', NS(x='X', y=[], z='Z')),
        ('X A B -z Z', NS(x='X', y=['A', 'B', '-z', 'Z'], z=None)),
        ('X Y --foo', NS(x='X', y=['Y', '--foo'], z=None)),
    ]


kundi TestOptionLike(ParserTestCase):
    """Tests options that may or may not be arguments"""

    argument_signatures = [
        Sig('-x', type=float),
        Sig('-3', type=float, dest='y'),
        Sig('z', nargs='*'),
    ]
    failures = ['-x', '-y2.5', '-xa', '-x -a',
                '-x -3', '-x -3.5', '-3 -3.5',
                '-x -2.5', '-x -2.5 a', '-3 -.5',
                'a x -1', '-x -1 a', '-3 -1 a']
    successes = [
        ('', NS(x=None, y=None, z=[])),
        ('-x 2.5', NS(x=2.5, y=None, z=[])),
        ('-x 2.5 a', NS(x=2.5, y=None, z=['a'])),
        ('-3.5', NS(x=None, y=0.5, z=[])),
        ('-3-.5', NS(x=None, y=-0.5, z=[])),
        ('-3 .5', NS(x=None, y=0.5, z=[])),
        ('a -3.5', NS(x=None, y=0.5, z=['a'])),
        ('a', NS(x=None, y=None, z=['a'])),
        ('a -x 1', NS(x=1.0, y=None, z=['a'])),
        ('-x 1 a', NS(x=1.0, y=None, z=['a'])),
        ('-3 1 a', NS(x=None, y=1.0, z=['a'])),
    ]


kundi TestDefaultSuppress(ParserTestCase):
    """Test actions with suppressed defaults"""

    argument_signatures = [
        Sig('foo', nargs='?', default=argparse.SUPPRESS),
        Sig('bar', nargs='*', default=argparse.SUPPRESS),
        Sig('--baz', action='store_true', default=argparse.SUPPRESS),
    ]
    failures = ['-x']
    successes = [
        ('', NS()),
        ('a', NS(foo='a')),
        ('a b', NS(foo='a', bar=['b'])),
        ('--baz', NS(baz=True)),
        ('a --baz', NS(foo='a', baz=True)),
        ('--baz a b', NS(foo='a', bar=['b'], baz=True)),
    ]


kundi TestParserDefaultSuppress(ParserTestCase):
    """Test actions with a parser-level default of SUPPRESS"""

    parser_signature = Sig(argument_default=argparse.SUPPRESS)
    argument_signatures = [
        Sig('foo', nargs='?'),
        Sig('bar', nargs='*'),
        Sig('--baz', action='store_true'),
    ]
    failures = ['-x']
    successes = [
        ('', NS()),
        ('a', NS(foo='a')),
        ('a b', NS(foo='a', bar=['b'])),
        ('--baz', NS(baz=True)),
        ('a --baz', NS(foo='a', baz=True)),
        ('--baz a b', NS(foo='a', bar=['b'], baz=True)),
    ]


kundi TestParserDefault42(ParserTestCase):
    """Test actions with a parser-level default of 42"""

    parser_signature = Sig(argument_default=42)
    argument_signatures = [
        Sig('--version', action='version', version='1.0'),
        Sig('foo', nargs='?'),
        Sig('bar', nargs='*'),
        Sig('--baz', action='store_true'),
    ]
    failures = ['-x']
    successes = [
        ('', NS(foo=42, bar=42, baz=42, version=42)),
        ('a', NS(foo='a', bar=42, baz=42, version=42)),
        ('a b', NS(foo='a', bar=['b'], baz=42, version=42)),
        ('--baz', NS(foo=42, bar=42, baz=True, version=42)),
        ('a --baz', NS(foo='a', bar=42, baz=True, version=42)),
        ('--baz a b', NS(foo='a', bar=['b'], baz=True, version=42)),
    ]


kundi TestArgumentsFromFile(TempDirMixin, ParserTestCase):
    """Test reading arguments kutoka a file"""

    eleza setUp(self):
        super(TestArgumentsFromFile, self).setUp()
        file_texts = [
            ('hello', 'hello world!\n'),
            ('recursive', '-a\n'
                          'A\n'
                          '@hello'),
            ('invalid', '@no-such-path\n'),
        ]
        for path, text in file_texts:
            with open(path, 'w') as file:
                file.write(text)

    parser_signature = Sig(kutokafile_prefix_chars='@')
    argument_signatures = [
        Sig('-a'),
        Sig('x'),
        Sig('y', nargs='+'),
    ]
    failures = ['', '-b', 'X', '@invalid', '@missing']
    successes = [
        ('X Y', NS(a=None, x='X', y=['Y'])),
        ('X -a A Y Z', NS(a='A', x='X', y=['Y', 'Z'])),
        ('@hello X', NS(a=None, x='hello world!', y=['X'])),
        ('X @hello', NS(a=None, x='X', y=['hello world!'])),
        ('-a B @recursive Y Z', NS(a='A', x='hello world!', y=['Y', 'Z'])),
        ('X @recursive Z -a B', NS(a='B', x='X', y=['hello world!', 'Z'])),
        (["-a", "", "X", "Y"], NS(a='', x='X', y=['Y'])),
    ]


kundi TestArgumentsFromFileConverter(TempDirMixin, ParserTestCase):
    """Test reading arguments kutoka a file"""

    eleza setUp(self):
        super(TestArgumentsFromFileConverter, self).setUp()
        file_texts = [
            ('hello', 'hello world!\n'),
        ]
        for path, text in file_texts:
            with open(path, 'w') as file:
                file.write(text)

    kundi FromFileConverterArgumentParser(ErrorRaisingArgumentParser):

        eleza convert_arg_line_to_args(self, arg_line):
            for arg in arg_line.split():
                ikiwa not arg.strip():
                    continue
                yield arg
    parser_kundi = FromFileConverterArgumentParser
    parser_signature = Sig(kutokafile_prefix_chars='@')
    argument_signatures = [
        Sig('y', nargs='+'),
    ]
    failures = []
    successes = [
        ('@hello X', NS(y=['hello', 'world!', 'X'])),
    ]


# =====================
# Type conversion tests
# =====================

kundi TestFileTypeRepr(TestCase):

    eleza test_r(self):
        type = argparse.FileType('r')
        self.assertEqual("FileType('r')", repr(type))

    eleza test_wb_1(self):
        type = argparse.FileType('wb', 1)
        self.assertEqual("FileType('wb', 1)", repr(type))

    eleza test_r_latin(self):
        type = argparse.FileType('r', encoding='latin_1')
        self.assertEqual("FileType('r', encoding='latin_1')", repr(type))

    eleza test_w_big5_ignore(self):
        type = argparse.FileType('w', encoding='big5', errors='ignore')
        self.assertEqual("FileType('w', encoding='big5', errors='ignore')",
                         repr(type))

    eleza test_r_1_replace(self):
        type = argparse.FileType('r', 1, errors='replace')
        self.assertEqual("FileType('r', 1, errors='replace')", repr(type))

kundi StdStreamComparer:
    eleza __init__(self, attr):
        self.attr = attr

    eleza __eq__(self, other):
        rudisha other == getattr(sys, self.attr)

eq_stdin = StdStreamComparer('stdin')
eq_stdout = StdStreamComparer('stdout')
eq_stderr = StdStreamComparer('stderr')

kundi RFile(object):
    seen = {}

    eleza __init__(self, name):
        self.name = name

    eleza __eq__(self, other):
        ikiwa other in self.seen:
            text = self.seen[other]
        else:
            text = self.seen[other] = other.read()
            other.close()
        ikiwa not isinstance(text, str):
            text = text.decode('ascii')
        rudisha self.name == other.name == text


kundi TestFileTypeR(TempDirMixin, ParserTestCase):
    """Test the FileType option/argument type for reading files"""

    eleza setUp(self):
        super(TestFileTypeR, self).setUp()
        for file_name in ['foo', 'bar']:
            with open(os.path.join(self.temp_dir, file_name), 'w') as file:
                file.write(file_name)
        self.create_readonly_file('readonly')

    argument_signatures = [
        Sig('-x', type=argparse.FileType()),
        Sig('spam', type=argparse.FileType('r')),
    ]
    failures = ['-x', '', 'non-existent-file.txt']
    successes = [
        ('foo', NS(x=None, spam=RFile('foo'))),
        ('-x foo bar', NS(x=RFile('foo'), spam=RFile('bar'))),
        ('bar -x foo', NS(x=RFile('foo'), spam=RFile('bar'))),
        ('-x - -', NS(x=eq_stdin, spam=eq_stdin)),
        ('readonly', NS(x=None, spam=RFile('readonly'))),
    ]

kundi TestFileTypeDefaults(TempDirMixin, ParserTestCase):
    """Test that a file is not created unless the default is needed"""
    eleza setUp(self):
        super(TestFileTypeDefaults, self).setUp()
        file = open(os.path.join(self.temp_dir, 'good'), 'w')
        file.write('good')
        file.close()

    argument_signatures = [
        Sig('-c', type=argparse.FileType('r'), default='no-file.txt'),
    ]
    # should provoke no such file error
    failures = ['']
    # should not provoke error because default file is created
    successes = [('-c good', NS(c=RFile('good')))]


kundi TestFileTypeRB(TempDirMixin, ParserTestCase):
    """Test the FileType option/argument type for reading files"""

    eleza setUp(self):
        super(TestFileTypeRB, self).setUp()
        for file_name in ['foo', 'bar']:
            with open(os.path.join(self.temp_dir, file_name), 'w') as file:
                file.write(file_name)

    argument_signatures = [
        Sig('-x', type=argparse.FileType('rb')),
        Sig('spam', type=argparse.FileType('rb')),
    ]
    failures = ['-x', '']
    successes = [
        ('foo', NS(x=None, spam=RFile('foo'))),
        ('-x foo bar', NS(x=RFile('foo'), spam=RFile('bar'))),
        ('bar -x foo', NS(x=RFile('foo'), spam=RFile('bar'))),
        ('-x - -', NS(x=eq_stdin, spam=eq_stdin)),
    ]


kundi WFile(object):
    seen = set()

    eleza __init__(self, name):
        self.name = name

    eleza __eq__(self, other):
        ikiwa other not in self.seen:
            text = 'Check that file is writable.'
            ikiwa 'b' in other.mode:
                text = text.encode('ascii')
            other.write(text)
            other.close()
            self.seen.add(other)
        rudisha self.name == other.name


@unittest.skipIf(hasattr(os, 'geteuid') and os.geteuid() == 0,
                 "non-root user required")
kundi TestFileTypeW(TempDirMixin, ParserTestCase):
    """Test the FileType option/argument type for writing files"""

    eleza setUp(self):
        super(TestFileTypeW, self).setUp()
        self.create_readonly_file('readonly')

    argument_signatures = [
        Sig('-x', type=argparse.FileType('w')),
        Sig('spam', type=argparse.FileType('w')),
    ]
    failures = ['-x', '', 'readonly']
    successes = [
        ('foo', NS(x=None, spam=WFile('foo'))),
        ('-x foo bar', NS(x=WFile('foo'), spam=WFile('bar'))),
        ('bar -x foo', NS(x=WFile('foo'), spam=WFile('bar'))),
        ('-x - -', NS(x=eq_stdout, spam=eq_stdout)),
    ]


kundi TestFileTypeWB(TempDirMixin, ParserTestCase):

    argument_signatures = [
        Sig('-x', type=argparse.FileType('wb')),
        Sig('spam', type=argparse.FileType('wb')),
    ]
    failures = ['-x', '']
    successes = [
        ('foo', NS(x=None, spam=WFile('foo'))),
        ('-x foo bar', NS(x=WFile('foo'), spam=WFile('bar'))),
        ('bar -x foo', NS(x=WFile('foo'), spam=WFile('bar'))),
        ('-x - -', NS(x=eq_stdout, spam=eq_stdout)),
    ]


kundi TestFileTypeOpenArgs(TestCase):
    """Test that open (the builtin) is correctly called"""

    eleza test_open_args(self):
        FT = argparse.FileType
        cases = [
            (FT('rb'), ('rb', -1, None, None)),
            (FT('w', 1), ('w', 1, None, None)),
            (FT('w', errors='replace'), ('w', -1, None, 'replace')),
            (FT('wb', encoding='big5'), ('wb', -1, 'big5', None)),
            (FT('w', 0, 'l1', 'strict'), ('w', 0, 'l1', 'strict')),
        ]
        with mock.patch('builtins.open') as m:
            for type, args in cases:
                type('foo')
                m.assert_called_with('foo', *args)


kundi TestFileTypeMissingInitialization(TestCase):
    """
    Test that add_argument throws an error ikiwa FileType class
    object was passed instead of instance of FileType
    """

    eleza test(self):
        parser = argparse.ArgumentParser()
        with self.assertRaises(ValueError) as cm:
            parser.add_argument('-x', type=argparse.FileType)

        self.assertEqual(
            '%r is a FileType kundi object, instance of it must be passed'
            % (argparse.FileType,),
            str(cm.exception)
        )


kundi TestTypeCallable(ParserTestCase):
    """Test some callables as option/argument types"""

    argument_signatures = [
        Sig('--eggs', type=complex),
        Sig('spam', type=float),
    ]
    failures = ['a', '42j', '--eggs a', '--eggs 2i']
    successes = [
        ('--eggs=42 42', NS(eggs=42, spam=42.0)),
        ('--eggs 2j -- -1.5', NS(eggs=2j, spam=-1.5)),
        ('1024.675', NS(eggs=None, spam=1024.675)),
    ]


kundi TestTypeUserDefined(ParserTestCase):
    """Test a user-defined option/argument type"""

    kundi MyType(TestCase):

        eleza __init__(self, value):
            self.value = value

        eleza __eq__(self, other):
            rudisha (type(self), self.value) == (type(other), other.value)

    argument_signatures = [
        Sig('-x', type=MyType),
        Sig('spam', type=MyType),
    ]
    failures = []
    successes = [
        ('a -x b', NS(x=MyType('b'), spam=MyType('a'))),
        ('-xf g', NS(x=MyType('f'), spam=MyType('g'))),
    ]


kundi TestTypeClassicClass(ParserTestCase):
    """Test a classic kundi type"""

    kundi C:

        eleza __init__(self, value):
            self.value = value

        eleza __eq__(self, other):
            rudisha (type(self), self.value) == (type(other), other.value)

    argument_signatures = [
        Sig('-x', type=C),
        Sig('spam', type=C),
    ]
    failures = []
    successes = [
        ('a -x b', NS(x=C('b'), spam=C('a'))),
        ('-xf g', NS(x=C('f'), spam=C('g'))),
    ]


kundi TestTypeRegistration(TestCase):
    """Test a user-defined type by registering it"""

    eleza test(self):

        eleza get_my_type(string):
            rudisha 'my_type{%s}' % string

        parser = argparse.ArgumentParser()
        parser.register('type', 'my_type', get_my_type)
        parser.add_argument('-x', type='my_type')
        parser.add_argument('y', type='my_type')

        self.assertEqual(parser.parse_args('1'.split()),
                         NS(x=None, y='my_type{1}'))
        self.assertEqual(parser.parse_args('-x 1 42'.split()),
                         NS(x='my_type{1}', y='my_type{42}'))


# ============
# Action tests
# ============

kundi TestActionUserDefined(ParserTestCase):
    """Test a user-defined option/argument action"""

    kundi OptionalAction(argparse.Action):

        eleza __call__(self, parser, namespace, value, option_string=None):
            try:
                # check destination and option string
                assert self.dest == 'spam', 'dest: %s' % self.dest
                assert option_string == '-s', 'flag: %s' % option_string
                # when option is before argument, badger=2, and when
                # option is after argument, badger=<whatever was set>
                expected_ns = NS(spam=0.25)
                ikiwa value in [0.125, 0.625]:
                    expected_ns.badger = 2
                elikiwa value in [2.0]:
                    expected_ns.badger = 84
                else:
                    raise AssertionError('value: %s' % value)
                assert expected_ns == namespace, ('expected %s, got %s' %
                                                  (expected_ns, namespace))
            except AssertionError:
                e = sys.exc_info()[1]
                raise ArgumentParserError('opt_action failed: %s' % e)
            setattr(namespace, 'spam', value)

    kundi PositionalAction(argparse.Action):

        eleza __call__(self, parser, namespace, value, option_string=None):
            try:
                assert option_string is None, ('option_string: %s' %
                                               option_string)
                # check destination
                assert self.dest == 'badger', 'dest: %s' % self.dest
                # when argument is before option, spam=0.25, and when
                # option is after argument, spam=<whatever was set>
                expected_ns = NS(badger=2)
                ikiwa value in [42, 84]:
                    expected_ns.spam = 0.25
                elikiwa value in [1]:
                    expected_ns.spam = 0.625
                elikiwa value in [2]:
                    expected_ns.spam = 0.125
                else:
                    raise AssertionError('value: %s' % value)
                assert expected_ns == namespace, ('expected %s, got %s' %
                                                  (expected_ns, namespace))
            except AssertionError:
                e = sys.exc_info()[1]
                raise ArgumentParserError('arg_action failed: %s' % e)
            setattr(namespace, 'badger', value)

    argument_signatures = [
        Sig('-s', dest='spam', action=OptionalAction,
            type=float, default=0.25),
        Sig('badger', action=PositionalAction,
            type=int, nargs='?', default=2),
    ]
    failures = []
    successes = [
        ('-s0.125', NS(spam=0.125, badger=2)),
        ('42', NS(spam=0.25, badger=42)),
        ('-s 0.625 1', NS(spam=0.625, badger=1)),
        ('84 -s2', NS(spam=2.0, badger=84)),
    ]


kundi TestActionRegistration(TestCase):
    """Test a user-defined action supplied by registering it"""

    kundi MyAction(argparse.Action):

        eleza __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, 'foo[%s]' % values)

    eleza test(self):

        parser = argparse.ArgumentParser()
        parser.register('action', 'my_action', self.MyAction)
        parser.add_argument('badger', action='my_action')

        self.assertEqual(parser.parse_args(['1']), NS(badger='foo[1]'))
        self.assertEqual(parser.parse_args(['42']), NS(badger='foo[42]'))


kundi TestActionExtend(ParserTestCase):
    argument_signatures = [
        Sig('--foo', action="extend", nargs="+", type=str),
    ]
    failures = ()
    successes = [
        ('--foo f1 --foo f2 f3 f4', NS(foo=['f1', 'f2', 'f3', 'f4'])),
    ]

# ================
# Subparsers tests
# ================

kundi TestAddSubparsers(TestCase):
    """Test the add_subparsers method"""

    eleza assertArgumentParserError(self, *args, **kwargs):
        self.assertRaises(ArgumentParserError, *args, **kwargs)

    eleza _get_parser(self, subparser_help=False, prefix_chars=None,
                    aliases=False):
        # create a parser with a subparsers argument
        ikiwa prefix_chars:
            parser = ErrorRaisingArgumentParser(
                prog='PROG', description='main description', prefix_chars=prefix_chars)
            parser.add_argument(
                prefix_chars[0] * 2 + 'foo', action='store_true', help='foo help')
        else:
            parser = ErrorRaisingArgumentParser(
                prog='PROG', description='main description')
            parser.add_argument(
                '--foo', action='store_true', help='foo help')
        parser.add_argument(
            'bar', type=float, help='bar help')

        # check that only one subparsers argument can be added
        subparsers_kwargs = {'required': False}
        ikiwa aliases:
            subparsers_kwargs['metavar'] = 'COMMAND'
            subparsers_kwargs['title'] = 'commands'
        else:
            subparsers_kwargs['help'] = 'command help'
        subparsers = parser.add_subparsers(**subparsers_kwargs)
        self.assertArgumentParserError(parser.add_subparsers)

        # add first sub-parser
        parser1_kwargs = dict(description='1 description')
        ikiwa subparser_help:
            parser1_kwargs['help'] = '1 help'
        ikiwa aliases:
            parser1_kwargs['aliases'] = ['1alias1', '1alias2']
        parser1 = subparsers.add_parser('1', **parser1_kwargs)
        parser1.add_argument('-w', type=int, help='w help')
        parser1.add_argument('x', choices='abc', help='x help')

        # add second sub-parser
        parser2_kwargs = dict(description='2 description')
        ikiwa subparser_help:
            parser2_kwargs['help'] = '2 help'
        parser2 = subparsers.add_parser('2', **parser2_kwargs)
        parser2.add_argument('-y', choices='123', help='y help')
        parser2.add_argument('z', type=complex, nargs='*', help='z help')

        # add third sub-parser
        parser3_kwargs = dict(description='3 description')
        ikiwa subparser_help:
            parser3_kwargs['help'] = '3 help'
        parser3 = subparsers.add_parser('3', **parser3_kwargs)
        parser3.add_argument('t', type=int, help='t help')
        parser3.add_argument('u', nargs='...', help='u help')

        # rudisha the main parser
        rudisha parser

    eleza setUp(self):
        super().setUp()
        self.parser = self._get_parser()
        self.command_help_parser = self._get_parser(subparser_help=True)

    eleza test_parse_args_failures(self):
        # check some failure cases:
        for args_str in ['', 'a', 'a a', '0.5 a', '0.5 1',
                         '0.5 1 -y', '0.5 2 -w']:
            args = args_str.split()
            self.assertArgumentParserError(self.parser.parse_args, args)

    eleza test_parse_args(self):
        # check some non-failure cases:
        self.assertEqual(
            self.parser.parse_args('0.5 1 b -w 7'.split()),
            NS(foo=False, bar=0.5, w=7, x='b'),
        )
        self.assertEqual(
            self.parser.parse_args('0.25 --foo 2 -y 2 3j -- -1j'.split()),
            NS(foo=True, bar=0.25, y='2', z=[3j, -1j]),
        )
        self.assertEqual(
            self.parser.parse_args('--foo 0.125 1 c'.split()),
            NS(foo=True, bar=0.125, w=None, x='c'),
        )
        self.assertEqual(
            self.parser.parse_args('-1.5 3 11 -- a --foo 7 -- b'.split()),
            NS(foo=False, bar=-1.5, t=11, u=['a', '--foo', '7', '--', 'b']),
        )

    eleza test_parse_known_args(self):
        self.assertEqual(
            self.parser.parse_known_args('0.5 1 b -w 7'.split()),
            (NS(foo=False, bar=0.5, w=7, x='b'), []),
        )
        self.assertEqual(
            self.parser.parse_known_args('0.5 -p 1 b -w 7'.split()),
            (NS(foo=False, bar=0.5, w=7, x='b'), ['-p']),
        )
        self.assertEqual(
            self.parser.parse_known_args('0.5 1 b -w 7 -p'.split()),
            (NS(foo=False, bar=0.5, w=7, x='b'), ['-p']),
        )
        self.assertEqual(
            self.parser.parse_known_args('0.5 1 b -q -rs -w 7'.split()),
            (NS(foo=False, bar=0.5, w=7, x='b'), ['-q', '-rs']),
        )
        self.assertEqual(
            self.parser.parse_known_args('0.5 -W 1 b -X Y -w 7 Z'.split()),
            (NS(foo=False, bar=0.5, w=7, x='b'), ['-W', '-X', 'Y', 'Z']),
        )

    eleza test_dest(self):
        parser = ErrorRaisingArgumentParser()
        parser.add_argument('--foo', action='store_true')
        subparsers = parser.add_subparsers(dest='bar')
        parser1 = subparsers.add_parser('1')
        parser1.add_argument('baz')
        self.assertEqual(NS(foo=False, bar='1', baz='2'),
                         parser.parse_args('1 2'.split()))

    eleza _test_required_subparsers(self, parser):
        # Should parse the sub command
        ret = parser.parse_args(['run'])
        self.assertEqual(ret.command, 'run')

        # Error when the command is missing
        self.assertArgumentParserError(parser.parse_args, ())

    eleza test_required_subparsers_via_attribute(self):
        parser = ErrorRaisingArgumentParser()
        subparsers = parser.add_subparsers(dest='command')
        subparsers.required = True
        subparsers.add_parser('run')
        self._test_required_subparsers(parser)

    eleza test_required_subparsers_via_kwarg(self):
        parser = ErrorRaisingArgumentParser()
        subparsers = parser.add_subparsers(dest='command', required=True)
        subparsers.add_parser('run')
        self._test_required_subparsers(parser)

    eleza test_required_subparsers_default(self):
        parser = ErrorRaisingArgumentParser()
        subparsers = parser.add_subparsers(dest='command')
        subparsers.add_parser('run')
        # No error here
        ret = parser.parse_args(())
        self.assertIsNone(ret.command)

    eleza test_optional_subparsers(self):
        parser = ErrorRaisingArgumentParser()
        subparsers = parser.add_subparsers(dest='command', required=False)
        subparsers.add_parser('run')
        # No error here
        ret = parser.parse_args(())
        self.assertIsNone(ret.command)

    eleza test_help(self):
        self.assertEqual(self.parser.format_usage(),
                         'usage: PROG [-h] [--foo] bar {1,2,3} ...\n')
        self.assertEqual(self.parser.format_help(), textwrap.dedent('''\
            usage: PROG [-h] [--foo] bar {1,2,3} ...

            main description

            positional arguments:
              bar         bar help
              {1,2,3}     command help

            optional arguments:
              -h, --help  show this help message and exit
              --foo       foo help
            '''))

    eleza test_help_extra_prefix_chars(self):
        # Make sure - is still used for help ikiwa it is a non-first prefix char
        parser = self._get_parser(prefix_chars='+:-')
        self.assertEqual(parser.format_usage(),
                         'usage: PROG [-h] [++foo] bar {1,2,3} ...\n')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
            usage: PROG [-h] [++foo] bar {1,2,3} ...

            main description

            positional arguments:
              bar         bar help
              {1,2,3}     command help

            optional arguments:
              -h, --help  show this help message and exit
              ++foo       foo help
            '''))

    eleza test_help_non_breaking_spaces(self):
        parser = ErrorRaisingArgumentParser(
            prog='PROG', description='main description')
        parser.add_argument(
            "--non-breaking", action='store_false',
            help='help message containing non-breaking spaces shall not '
            'wrap\N{NO-BREAK SPACE}at non-breaking spaces')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
            usage: PROG [-h] [--non-breaking]

            main description

            optional arguments:
              -h, --help      show this help message and exit
              --non-breaking  help message containing non-breaking spaces shall not
                              wrap\N{NO-BREAK SPACE}at non-breaking spaces
        '''))

    eleza test_help_alternate_prefix_chars(self):
        parser = self._get_parser(prefix_chars='+:/')
        self.assertEqual(parser.format_usage(),
                         'usage: PROG [+h] [++foo] bar {1,2,3} ...\n')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
            usage: PROG [+h] [++foo] bar {1,2,3} ...

            main description

            positional arguments:
              bar         bar help
              {1,2,3}     command help

            optional arguments:
              +h, ++help  show this help message and exit
              ++foo       foo help
            '''))

    eleza test_parser_command_help(self):
        self.assertEqual(self.command_help_parser.format_usage(),
                         'usage: PROG [-h] [--foo] bar {1,2,3} ...\n')
        self.assertEqual(self.command_help_parser.format_help(),
                         textwrap.dedent('''\
            usage: PROG [-h] [--foo] bar {1,2,3} ...

            main description

            positional arguments:
              bar         bar help
              {1,2,3}     command help
                1         1 help
                2         2 help
                3         3 help

            optional arguments:
              -h, --help  show this help message and exit
              --foo       foo help
            '''))

    eleza test_subparser_title_help(self):
        parser = ErrorRaisingArgumentParser(prog='PROG',
                                            description='main description')
        parser.add_argument('--foo', action='store_true', help='foo help')
        parser.add_argument('bar', help='bar help')
        subparsers = parser.add_subparsers(title='subcommands',
                                           description='command help',
                                           help='additional text')
        parser1 = subparsers.add_parser('1')
        parser2 = subparsers.add_parser('2')
        self.assertEqual(parser.format_usage(),
                         'usage: PROG [-h] [--foo] bar {1,2} ...\n')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
            usage: PROG [-h] [--foo] bar {1,2} ...

            main description

            positional arguments:
              bar         bar help

            optional arguments:
              -h, --help  show this help message and exit
              --foo       foo help

            subcommands:
              command help

              {1,2}       additional text
            '''))

    eleza _test_subparser_help(self, args_str, expected_help):
        with self.assertRaises(ArgumentParserError) as cm:
            self.parser.parse_args(args_str.split())
        self.assertEqual(expected_help, cm.exception.stdout)

    eleza test_subparser1_help(self):
        self._test_subparser_help('5.0 1 -h', textwrap.dedent('''\
            usage: PROG bar 1 [-h] [-w W] {a,b,c}

            1 description

            positional arguments:
              {a,b,c}     x help

            optional arguments:
              -h, --help  show this help message and exit
              -w W        w help
            '''))

    eleza test_subparser2_help(self):
        self._test_subparser_help('5.0 2 -h', textwrap.dedent('''\
            usage: PROG bar 2 [-h] [-y {1,2,3}] [z [z ...]]

            2 description

            positional arguments:
              z           z help

            optional arguments:
              -h, --help  show this help message and exit
              -y {1,2,3}  y help
            '''))

    eleza test_alias_invocation(self):
        parser = self._get_parser(aliases=True)
        self.assertEqual(
            parser.parse_known_args('0.5 1alias1 b'.split()),
            (NS(foo=False, bar=0.5, w=None, x='b'), []),
        )
        self.assertEqual(
            parser.parse_known_args('0.5 1alias2 b'.split()),
            (NS(foo=False, bar=0.5, w=None, x='b'), []),
        )

    eleza test_error_alias_invocation(self):
        parser = self._get_parser(aliases=True)
        self.assertArgumentParserError(parser.parse_args,
                                       '0.5 1alias3 b'.split())

    eleza test_alias_help(self):
        parser = self._get_parser(aliases=True, subparser_help=True)
        self.maxDiff = None
        self.assertEqual(parser.format_help(), textwrap.dedent("""\
            usage: PROG [-h] [--foo] bar COMMAND ...

            main description

            positional arguments:
              bar                   bar help

            optional arguments:
              -h, --help            show this help message and exit
              --foo                 foo help

            commands:
              COMMAND
                1 (1alias1, 1alias2)
                                    1 help
                2                   2 help
                3                   3 help
            """))

# ============
# Groups tests
# ============

kundi TestPositionalsGroups(TestCase):
    """Tests that order of group positionals matches construction order"""

    eleza test_nongroup_first(self):
        parser = ErrorRaisingArgumentParser()
        parser.add_argument('foo')
        group = parser.add_argument_group('g')
        group.add_argument('bar')
        parser.add_argument('baz')
        expected = NS(foo='1', bar='2', baz='3')
        result = parser.parse_args('1 2 3'.split())
        self.assertEqual(expected, result)

    eleza test_group_first(self):
        parser = ErrorRaisingArgumentParser()
        group = parser.add_argument_group('xxx')
        group.add_argument('foo')
        parser.add_argument('bar')
        parser.add_argument('baz')
        expected = NS(foo='1', bar='2', baz='3')
        result = parser.parse_args('1 2 3'.split())
        self.assertEqual(expected, result)

    eleza test_interleaved_groups(self):
        parser = ErrorRaisingArgumentParser()
        group = parser.add_argument_group('xxx')
        parser.add_argument('foo')
        group.add_argument('bar')
        parser.add_argument('baz')
        group = parser.add_argument_group('yyy')
        group.add_argument('frell')
        expected = NS(foo='1', bar='2', baz='3', frell='4')
        result = parser.parse_args('1 2 3 4'.split())
        self.assertEqual(expected, result)

# ===================
# Parent parser tests
# ===================

kundi TestParentParsers(TestCase):
    """Tests that parsers can be created with parent parsers"""

    eleza assertArgumentParserError(self, *args, **kwargs):
        self.assertRaises(ArgumentParserError, *args, **kwargs)

    eleza setUp(self):
        super().setUp()
        self.wxyz_parent = ErrorRaisingArgumentParser(add_help=False)
        self.wxyz_parent.add_argument('--w')
        x_group = self.wxyz_parent.add_argument_group('x')
        x_group.add_argument('-y')
        self.wxyz_parent.add_argument('z')

        self.abcd_parent = ErrorRaisingArgumentParser(add_help=False)
        self.abcd_parent.add_argument('a')
        self.abcd_parent.add_argument('-b')
        c_group = self.abcd_parent.add_argument_group('c')
        c_group.add_argument('--d')

        self.w_parent = ErrorRaisingArgumentParser(add_help=False)
        self.w_parent.add_argument('--w')

        self.z_parent = ErrorRaisingArgumentParser(add_help=False)
        self.z_parent.add_argument('z')

        # parents with mutually exclusive groups
        self.ab_mutex_parent = ErrorRaisingArgumentParser(add_help=False)
        group = self.ab_mutex_parent.add_mutually_exclusive_group()
        group.add_argument('-a', action='store_true')
        group.add_argument('-b', action='store_true')

        self.main_program = os.path.basename(sys.argv[0])

    eleza test_single_parent(self):
        parser = ErrorRaisingArgumentParser(parents=[self.wxyz_parent])
        self.assertEqual(parser.parse_args('-y 1 2 --w 3'.split()),
                         NS(w='3', y='1', z='2'))

    eleza test_single_parent_mutex(self):
        self._test_mutex_ab(self.ab_mutex_parent.parse_args)
        parser = ErrorRaisingArgumentParser(parents=[self.ab_mutex_parent])
        self._test_mutex_ab(parser.parse_args)

    eleza test_single_granparent_mutex(self):
        parents = [self.ab_mutex_parent]
        parser = ErrorRaisingArgumentParser(add_help=False, parents=parents)
        parser = ErrorRaisingArgumentParser(parents=[parser])
        self._test_mutex_ab(parser.parse_args)

    eleza _test_mutex_ab(self, parse_args):
        self.assertEqual(parse_args([]), NS(a=False, b=False))
        self.assertEqual(parse_args(['-a']), NS(a=True, b=False))
        self.assertEqual(parse_args(['-b']), NS(a=False, b=True))
        self.assertArgumentParserError(parse_args, ['-a', '-b'])
        self.assertArgumentParserError(parse_args, ['-b', '-a'])
        self.assertArgumentParserError(parse_args, ['-c'])
        self.assertArgumentParserError(parse_args, ['-a', '-c'])
        self.assertArgumentParserError(parse_args, ['-b', '-c'])

    eleza test_multiple_parents(self):
        parents = [self.abcd_parent, self.wxyz_parent]
        parser = ErrorRaisingArgumentParser(parents=parents)
        self.assertEqual(parser.parse_args('--d 1 --w 2 3 4'.split()),
                         NS(a='3', b=None, d='1', w='2', y=None, z='4'))

    eleza test_multiple_parents_mutex(self):
        parents = [self.ab_mutex_parent, self.wxyz_parent]
        parser = ErrorRaisingArgumentParser(parents=parents)
        self.assertEqual(parser.parse_args('-a --w 2 3'.split()),
                         NS(a=True, b=False, w='2', y=None, z='3'))
        self.assertArgumentParserError(
            parser.parse_args, '-a --w 2 3 -b'.split())
        self.assertArgumentParserError(
            parser.parse_args, '-a -b --w 2 3'.split())

    eleza test_conflicting_parents(self):
        self.assertRaises(
            argparse.ArgumentError,
            argparse.ArgumentParser,
            parents=[self.w_parent, self.wxyz_parent])

    eleza test_conflicting_parents_mutex(self):
        self.assertRaises(
            argparse.ArgumentError,
            argparse.ArgumentParser,
            parents=[self.abcd_parent, self.ab_mutex_parent])

    eleza test_same_argument_name_parents(self):
        parents = [self.wxyz_parent, self.z_parent]
        parser = ErrorRaisingArgumentParser(parents=parents)
        self.assertEqual(parser.parse_args('1 2'.split()),
                         NS(w=None, y=None, z='2'))

    eleza test_subparser_parents(self):
        parser = ErrorRaisingArgumentParser()
        subparsers = parser.add_subparsers()
        abcde_parser = subparsers.add_parser('bar', parents=[self.abcd_parent])
        abcde_parser.add_argument('e')
        self.assertEqual(parser.parse_args('bar -b 1 --d 2 3 4'.split()),
                         NS(a='3', b='1', d='2', e='4'))

    eleza test_subparser_parents_mutex(self):
        parser = ErrorRaisingArgumentParser()
        subparsers = parser.add_subparsers()
        parents = [self.ab_mutex_parent]
        abc_parser = subparsers.add_parser('foo', parents=parents)
        c_group = abc_parser.add_argument_group('c_group')
        c_group.add_argument('c')
        parents = [self.wxyz_parent, self.ab_mutex_parent]
        wxyzabe_parser = subparsers.add_parser('bar', parents=parents)
        wxyzabe_parser.add_argument('e')
        self.assertEqual(parser.parse_args('foo -a 4'.split()),
                         NS(a=True, b=False, c='4'))
        self.assertEqual(parser.parse_args('bar -b  --w 2 3 4'.split()),
                         NS(a=False, b=True, w='2', y=None, z='3', e='4'))
        self.assertArgumentParserError(
            parser.parse_args, 'foo -a -b 4'.split())
        self.assertArgumentParserError(
            parser.parse_args, 'bar -b -a 4'.split())

    eleza test_parent_help(self):
        parents = [self.abcd_parent, self.wxyz_parent]
        parser = ErrorRaisingArgumentParser(parents=parents)
        parser_help = parser.format_help()
        progname = self.main_program
        self.assertEqual(parser_help, textwrap.dedent('''\
            usage: {}{}[-h] [-b B] [--d D] [--w W] [-y Y] a z

            positional arguments:
              a
              z

            optional arguments:
              -h, --help  show this help message and exit
              -b B
              --w W

            c:
              --d D

            x:
              -y Y
        '''.format(progname, ' ' ikiwa progname else '' )))

    eleza test_groups_parents(self):
        parent = ErrorRaisingArgumentParser(add_help=False)
        g = parent.add_argument_group(title='g', description='gd')
        g.add_argument('-w')
        g.add_argument('-x')
        m = parent.add_mutually_exclusive_group()
        m.add_argument('-y')
        m.add_argument('-z')
        parser = ErrorRaisingArgumentParser(parents=[parent])

        self.assertRaises(ArgumentParserError, parser.parse_args,
            ['-y', 'Y', '-z', 'Z'])

        parser_help = parser.format_help()
        progname = self.main_program
        self.assertEqual(parser_help, textwrap.dedent('''\
            usage: {}{}[-h] [-w W] [-x X] [-y Y | -z Z]

            optional arguments:
              -h, --help  show this help message and exit
              -y Y
              -z Z

            g:
              gd

              -w W
              -x X
        '''.format(progname, ' ' ikiwa progname else '' )))

# ==============================
# Mutually exclusive group tests
# ==============================

kundi TestMutuallyExclusiveGroupErrors(TestCase):

    eleza test_invalid_add_argument_group(self):
        parser = ErrorRaisingArgumentParser()
        raises = self.assertRaises
        raises(TypeError, parser.add_mutually_exclusive_group, title='foo')

    eleza test_invalid_add_argument(self):
        parser = ErrorRaisingArgumentParser()
        group = parser.add_mutually_exclusive_group()
        add_argument = group.add_argument
        raises = self.assertRaises
        raises(ValueError, add_argument, '--foo', required=True)
        raises(ValueError, add_argument, 'bar')
        raises(ValueError, add_argument, 'bar', nargs='+')
        raises(ValueError, add_argument, 'bar', nargs=1)
        raises(ValueError, add_argument, 'bar', nargs=argparse.PARSER)

    eleza test_help(self):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument('--foo', action='store_true')
        group1.add_argument('--bar', action='store_false')
        group2 = parser.add_mutually_exclusive_group()
        group2.add_argument('--soup', action='store_true')
        group2.add_argument('--nuts', action='store_false')
        expected = '''\
            usage: PROG [-h] [--foo | --bar] [--soup | --nuts]

            optional arguments:
              -h, --help  show this help message and exit
              --foo
              --bar
              --soup
              --nuts
              '''
        self.assertEqual(parser.format_help(), textwrap.dedent(expected))

kundi MEMixin(object):

    eleza test_failures_when_not_required(self):
        parse_args = self.get_parser(required=False).parse_args
        error = ArgumentParserError
        for args_string in self.failures:
            self.assertRaises(error, parse_args, args_string.split())

    eleza test_failures_when_required(self):
        parse_args = self.get_parser(required=True).parse_args
        error = ArgumentParserError
        for args_string in self.failures + ['']:
            self.assertRaises(error, parse_args, args_string.split())

    eleza test_successes_when_not_required(self):
        parse_args = self.get_parser(required=False).parse_args
        successes = self.successes + self.successes_when_not_required
        for args_string, expected_ns in successes:
            actual_ns = parse_args(args_string.split())
            self.assertEqual(actual_ns, expected_ns)

    eleza test_successes_when_required(self):
        parse_args = self.get_parser(required=True).parse_args
        for args_string, expected_ns in self.successes:
            actual_ns = parse_args(args_string.split())
            self.assertEqual(actual_ns, expected_ns)

    eleza test_usage_when_not_required(self):
        format_usage = self.get_parser(required=False).format_usage
        expected_usage = self.usage_when_not_required
        self.assertEqual(format_usage(), textwrap.dedent(expected_usage))

    eleza test_usage_when_required(self):
        format_usage = self.get_parser(required=True).format_usage
        expected_usage = self.usage_when_required
        self.assertEqual(format_usage(), textwrap.dedent(expected_usage))

    eleza test_help_when_not_required(self):
        format_help = self.get_parser(required=False).format_help
        help = self.usage_when_not_required + self.help
        self.assertEqual(format_help(), textwrap.dedent(help))

    eleza test_help_when_required(self):
        format_help = self.get_parser(required=True).format_help
        help = self.usage_when_required + self.help
        self.assertEqual(format_help(), textwrap.dedent(help))


kundi TestMutuallyExclusiveSimple(MEMixin, TestCase):

    eleza get_parser(self, required=None):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('--bar', help='bar help')
        group.add_argument('--baz', nargs='?', const='Z', help='baz help')
        rudisha parser

    failures = ['--bar X --baz Y', '--bar X --baz']
    successes = [
        ('--bar X', NS(bar='X', baz=None)),
        ('--bar X --bar Z', NS(bar='Z', baz=None)),
        ('--baz Y', NS(bar=None, baz='Y')),
        ('--baz', NS(bar=None, baz='Z')),
    ]
    successes_when_not_required = [
        ('', NS(bar=None, baz=None)),
    ]

    usage_when_not_required = '''\
        usage: PROG [-h] [--bar BAR | --baz [BAZ]]
        '''
    usage_when_required = '''\
        usage: PROG [-h] (--bar BAR | --baz [BAZ])
        '''
    help = '''\

        optional arguments:
          -h, --help   show this help message and exit
          --bar BAR    bar help
          --baz [BAZ]  baz help
        '''


kundi TestMutuallyExclusiveLong(MEMixin, TestCase):

    eleza get_parser(self, required=None):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        parser.add_argument('--abcde', help='abcde help')
        parser.add_argument('--fghij', help='fghij help')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('--klmno', help='klmno help')
        group.add_argument('--pqrst', help='pqrst help')
        rudisha parser

    failures = ['--klmno X --pqrst Y']
    successes = [
        ('--klmno X', NS(abcde=None, fghij=None, klmno='X', pqrst=None)),
        ('--abcde Y --klmno X',
            NS(abcde='Y', fghij=None, klmno='X', pqrst=None)),
        ('--pqrst X', NS(abcde=None, fghij=None, klmno=None, pqrst='X')),
        ('--pqrst X --fghij Y',
            NS(abcde=None, fghij='Y', klmno=None, pqrst='X')),
    ]
    successes_when_not_required = [
        ('', NS(abcde=None, fghij=None, klmno=None, pqrst=None)),
    ]

    usage_when_not_required = '''\
    usage: PROG [-h] [--abcde ABCDE] [--fghij FGHIJ]
                [--klmno KLMNO | --pqrst PQRST]
    '''
    usage_when_required = '''\
    usage: PROG [-h] [--abcde ABCDE] [--fghij FGHIJ]
                (--klmno KLMNO | --pqrst PQRST)
    '''
    help = '''\

    optional arguments:
      -h, --help     show this help message and exit
      --abcde ABCDE  abcde help
      --fghij FGHIJ  fghij help
      --klmno KLMNO  klmno help
      --pqrst PQRST  pqrst help
    '''


kundi TestMutuallyExclusiveFirstSuppressed(MEMixin, TestCase):

    eleza get_parser(self, required):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('-x', help=argparse.SUPPRESS)
        group.add_argument('-y', action='store_false', help='y help')
        rudisha parser

    failures = ['-x X -y']
    successes = [
        ('-x X', NS(x='X', y=True)),
        ('-x X -x Y', NS(x='Y', y=True)),
        ('-y', NS(x=None, y=False)),
    ]
    successes_when_not_required = [
        ('', NS(x=None, y=True)),
    ]

    usage_when_not_required = '''\
        usage: PROG [-h] [-y]
        '''
    usage_when_required = '''\
        usage: PROG [-h] -y
        '''
    help = '''\

        optional arguments:
          -h, --help  show this help message and exit
          -y          y help
        '''


kundi TestMutuallyExclusiveManySuppressed(MEMixin, TestCase):

    eleza get_parser(self, required):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=required)
        add = group.add_argument
        add('--spam', action='store_true', help=argparse.SUPPRESS)
        add('--badger', action='store_false', help=argparse.SUPPRESS)
        add('--bladder', help=argparse.SUPPRESS)
        rudisha parser

    failures = [
        '--spam --badger',
        '--badger --bladder B',
        '--bladder B --spam',
    ]
    successes = [
        ('--spam', NS(spam=True, badger=True, bladder=None)),
        ('--badger', NS(spam=False, badger=False, bladder=None)),
        ('--bladder B', NS(spam=False, badger=True, bladder='B')),
        ('--spam --spam', NS(spam=True, badger=True, bladder=None)),
    ]
    successes_when_not_required = [
        ('', NS(spam=False, badger=True, bladder=None)),
    ]

    usage_when_required = usage_when_not_required = '''\
        usage: PROG [-h]
        '''
    help = '''\

        optional arguments:
          -h, --help  show this help message and exit
        '''


kundi TestMutuallyExclusiveOptionalAndPositional(MEMixin, TestCase):

    eleza get_parser(self, required):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('--foo', action='store_true', help='FOO')
        group.add_argument('--spam', help='SPAM')
        group.add_argument('badger', nargs='*', default='X', help='BADGER')
        rudisha parser

    failures = [
        '--foo --spam S',
        '--spam S X',
        'X --foo',
        'X Y Z --spam S',
        '--foo X Y',
    ]
    successes = [
        ('--foo', NS(foo=True, spam=None, badger='X')),
        ('--spam S', NS(foo=False, spam='S', badger='X')),
        ('X', NS(foo=False, spam=None, badger=['X'])),
        ('X Y Z', NS(foo=False, spam=None, badger=['X', 'Y', 'Z'])),
    ]
    successes_when_not_required = [
        ('', NS(foo=False, spam=None, badger='X')),
    ]

    usage_when_not_required = '''\
        usage: PROG [-h] [--foo | --spam SPAM | badger [badger ...]]
        '''
    usage_when_required = '''\
        usage: PROG [-h] (--foo | --spam SPAM | badger [badger ...])
        '''
    help = '''\

        positional arguments:
          badger       BADGER

        optional arguments:
          -h, --help   show this help message and exit
          --foo        FOO
          --spam SPAM  SPAM
        '''


kundi TestMutuallyExclusiveOptionalsMixed(MEMixin, TestCase):

    eleza get_parser(self, required):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        parser.add_argument('-x', action='store_true', help='x help')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('-a', action='store_true', help='a help')
        group.add_argument('-b', action='store_true', help='b help')
        parser.add_argument('-y', action='store_true', help='y help')
        group.add_argument('-c', action='store_true', help='c help')
        rudisha parser

    failures = ['-a -b', '-b -c', '-a -c', '-a -b -c']
    successes = [
        ('-a', NS(a=True, b=False, c=False, x=False, y=False)),
        ('-b', NS(a=False, b=True, c=False, x=False, y=False)),
        ('-c', NS(a=False, b=False, c=True, x=False, y=False)),
        ('-a -x', NS(a=True, b=False, c=False, x=True, y=False)),
        ('-y -b', NS(a=False, b=True, c=False, x=False, y=True)),
        ('-x -y -c', NS(a=False, b=False, c=True, x=True, y=True)),
    ]
    successes_when_not_required = [
        ('', NS(a=False, b=False, c=False, x=False, y=False)),
        ('-x', NS(a=False, b=False, c=False, x=True, y=False)),
        ('-y', NS(a=False, b=False, c=False, x=False, y=True)),
    ]

    usage_when_required = usage_when_not_required = '''\
        usage: PROG [-h] [-x] [-a] [-b] [-y] [-c]
        '''
    help = '''\

        optional arguments:
          -h, --help  show this help message and exit
          -x          x help
          -a          a help
          -b          b help
          -y          y help
          -c          c help
        '''


kundi TestMutuallyExclusiveInGroup(MEMixin, TestCase):

    eleza get_parser(self, required=None):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        titled_group = parser.add_argument_group(
            title='Titled group', description='Group description')
        mutex_group = \
            titled_group.add_mutually_exclusive_group(required=required)
        mutex_group.add_argument('--bar', help='bar help')
        mutex_group.add_argument('--baz', help='baz help')
        rudisha parser

    failures = ['--bar X --baz Y', '--baz X --bar Y']
    successes = [
        ('--bar X', NS(bar='X', baz=None)),
        ('--baz Y', NS(bar=None, baz='Y')),
    ]
    successes_when_not_required = [
        ('', NS(bar=None, baz=None)),
    ]

    usage_when_not_required = '''\
        usage: PROG [-h] [--bar BAR | --baz BAZ]
        '''
    usage_when_required = '''\
        usage: PROG [-h] (--bar BAR | --baz BAZ)
        '''
    help = '''\

        optional arguments:
          -h, --help  show this help message and exit

        Titled group:
          Group description

          --bar BAR   bar help
          --baz BAZ   baz help
        '''


kundi TestMutuallyExclusiveOptionalsAndPositionalsMixed(MEMixin, TestCase):

    eleza get_parser(self, required):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        parser.add_argument('x', help='x help')
        parser.add_argument('-y', action='store_true', help='y help')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('a', nargs='?', help='a help')
        group.add_argument('-b', action='store_true', help='b help')
        group.add_argument('-c', action='store_true', help='c help')
        rudisha parser

    failures = ['X A -b', '-b -c', '-c X A']
    successes = [
        ('X A', NS(a='A', b=False, c=False, x='X', y=False)),
        ('X -b', NS(a=None, b=True, c=False, x='X', y=False)),
        ('X -c', NS(a=None, b=False, c=True, x='X', y=False)),
        ('X A -y', NS(a='A', b=False, c=False, x='X', y=True)),
        ('X -y -b', NS(a=None, b=True, c=False, x='X', y=True)),
    ]
    successes_when_not_required = [
        ('X', NS(a=None, b=False, c=False, x='X', y=False)),
        ('X -y', NS(a=None, b=False, c=False, x='X', y=True)),
    ]

    usage_when_required = usage_when_not_required = '''\
        usage: PROG [-h] [-y] [-b] [-c] x [a]
        '''
    help = '''\

        positional arguments:
          x           x help
          a           a help

        optional arguments:
          -h, --help  show this help message and exit
          -y          y help
          -b          b help
          -c          c help
        '''

kundi TestMutuallyExclusiveNested(MEMixin, TestCase):

    eleza get_parser(self, required):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('-a')
        group.add_argument('-b')
        group2 = group.add_mutually_exclusive_group(required=required)
        group2.add_argument('-c')
        group2.add_argument('-d')
        group3 = group2.add_mutually_exclusive_group(required=required)
        group3.add_argument('-e')
        group3.add_argument('-f')
        rudisha parser

    usage_when_not_required = '''\
        usage: PROG [-h] [-a A | -b B | [-c C | -d D | [-e E | -f F]]]
        '''
    usage_when_required = '''\
        usage: PROG [-h] (-a A | -b B | (-c C | -d D | (-e E | -f F)))
        '''

    help = '''\

        optional arguments:
          -h, --help  show this help message and exit
          -a A
          -b B
          -c C
          -d D
          -e E
          -f F
        '''

    # We are only interested in testing the behavior of format_usage().
    test_failures_when_not_required = None
    test_failures_when_required = None
    test_successes_when_not_required = None
    test_successes_when_required = None

# =================================================
# Mutually exclusive group in parent parser tests
# =================================================

kundi MEPBase(object):

    eleza get_parser(self, required=None):
        parent = super(MEPBase, self).get_parser(required=required)
        parser = ErrorRaisingArgumentParser(
            prog=parent.prog, add_help=False, parents=[parent])
        rudisha parser


kundi TestMutuallyExclusiveGroupErrorsParent(
    MEPBase, TestMutuallyExclusiveGroupErrors):
    pass


kundi TestMutuallyExclusiveSimpleParent(
    MEPBase, TestMutuallyExclusiveSimple):
    pass


kundi TestMutuallyExclusiveLongParent(
    MEPBase, TestMutuallyExclusiveLong):
    pass


kundi TestMutuallyExclusiveFirstSuppressedParent(
    MEPBase, TestMutuallyExclusiveFirstSuppressed):
    pass


kundi TestMutuallyExclusiveManySuppressedParent(
    MEPBase, TestMutuallyExclusiveManySuppressed):
    pass


kundi TestMutuallyExclusiveOptionalAndPositionalParent(
    MEPBase, TestMutuallyExclusiveOptionalAndPositional):
    pass


kundi TestMutuallyExclusiveOptionalsMixedParent(
    MEPBase, TestMutuallyExclusiveOptionalsMixed):
    pass


kundi TestMutuallyExclusiveOptionalsAndPositionalsMixedParent(
    MEPBase, TestMutuallyExclusiveOptionalsAndPositionalsMixed):
    pass

# =================
# Set default tests
# =================

kundi TestSetDefaults(TestCase):

    eleza test_set_defaults_no_args(self):
        parser = ErrorRaisingArgumentParser()
        parser.set_defaults(x='foo')
        parser.set_defaults(y='bar', z=1)
        self.assertEqual(NS(x='foo', y='bar', z=1),
                         parser.parse_args([]))
        self.assertEqual(NS(x='foo', y='bar', z=1),
                         parser.parse_args([], NS()))
        self.assertEqual(NS(x='baz', y='bar', z=1),
                         parser.parse_args([], NS(x='baz')))
        self.assertEqual(NS(x='baz', y='bar', z=2),
                         parser.parse_args([], NS(x='baz', z=2)))

    eleza test_set_defaults_with_args(self):
        parser = ErrorRaisingArgumentParser()
        parser.set_defaults(x='foo', y='bar')
        parser.add_argument('-x', default='xfoox')
        self.assertEqual(NS(x='xfoox', y='bar'),
                         parser.parse_args([]))
        self.assertEqual(NS(x='xfoox', y='bar'),
                         parser.parse_args([], NS()))
        self.assertEqual(NS(x='baz', y='bar'),
                         parser.parse_args([], NS(x='baz')))
        self.assertEqual(NS(x='1', y='bar'),
                         parser.parse_args('-x 1'.split()))
        self.assertEqual(NS(x='1', y='bar'),
                         parser.parse_args('-x 1'.split(), NS()))
        self.assertEqual(NS(x='1', y='bar'),
                         parser.parse_args('-x 1'.split(), NS(x='baz')))

    eleza test_set_defaults_subparsers(self):
        parser = ErrorRaisingArgumentParser()
        parser.set_defaults(x='foo')
        subparsers = parser.add_subparsers()
        parser_a = subparsers.add_parser('a')
        parser_a.set_defaults(y='bar')
        self.assertEqual(NS(x='foo', y='bar'),
                         parser.parse_args('a'.split()))

    eleza test_set_defaults_parents(self):
        parent = ErrorRaisingArgumentParser(add_help=False)
        parent.set_defaults(x='foo')
        parser = ErrorRaisingArgumentParser(parents=[parent])
        self.assertEqual(NS(x='foo'), parser.parse_args([]))

    eleza test_set_defaults_on_parent_and_subparser(self):
        parser = argparse.ArgumentParser()
        xparser = parser.add_subparsers().add_parser('X')
        parser.set_defaults(foo=1)
        xparser.set_defaults(foo=2)
        self.assertEqual(NS(foo=2), parser.parse_args(['X']))

    eleza test_set_defaults_same_as_add_argument(self):
        parser = ErrorRaisingArgumentParser()
        parser.set_defaults(w='W', x='X', y='Y', z='Z')
        parser.add_argument('-w')
        parser.add_argument('-x', default='XX')
        parser.add_argument('y', nargs='?')
        parser.add_argument('z', nargs='?', default='ZZ')

        # defaults set previously
        self.assertEqual(NS(w='W', x='XX', y='Y', z='ZZ'),
                         parser.parse_args([]))

        # reset defaults
        parser.set_defaults(w='WW', x='X', y='YY', z='Z')
        self.assertEqual(NS(w='WW', x='X', y='YY', z='Z'),
                         parser.parse_args([]))

    eleza test_set_defaults_same_as_add_argument_group(self):
        parser = ErrorRaisingArgumentParser()
        parser.set_defaults(w='W', x='X', y='Y', z='Z')
        group = parser.add_argument_group('foo')
        group.add_argument('-w')
        group.add_argument('-x', default='XX')
        group.add_argument('y', nargs='?')
        group.add_argument('z', nargs='?', default='ZZ')


        # defaults set previously
        self.assertEqual(NS(w='W', x='XX', y='Y', z='ZZ'),
                         parser.parse_args([]))

        # reset defaults
        parser.set_defaults(w='WW', x='X', y='YY', z='Z')
        self.assertEqual(NS(w='WW', x='X', y='YY', z='Z'),
                         parser.parse_args([]))

# =================
# Get default tests
# =================

kundi TestGetDefault(TestCase):

    eleza test_get_default(self):
        parser = ErrorRaisingArgumentParser()
        self.assertIsNone(parser.get_default("foo"))
        self.assertIsNone(parser.get_default("bar"))

        parser.add_argument("--foo")
        self.assertIsNone(parser.get_default("foo"))
        self.assertIsNone(parser.get_default("bar"))

        parser.add_argument("--bar", type=int, default=42)
        self.assertIsNone(parser.get_default("foo"))
        self.assertEqual(42, parser.get_default("bar"))

        parser.set_defaults(foo="badger")
        self.assertEqual("badger", parser.get_default("foo"))
        self.assertEqual(42, parser.get_default("bar"))

# ==========================
# Namespace 'contains' tests
# ==========================

kundi TestNamespaceContainsSimple(TestCase):

    eleza test_empty(self):
        ns = argparse.Namespace()
        self.assertNotIn('', ns)
        self.assertNotIn('x', ns)

    eleza test_non_empty(self):
        ns = argparse.Namespace(x=1, y=2)
        self.assertNotIn('', ns)
        self.assertIn('x', ns)
        self.assertIn('y', ns)
        self.assertNotIn('xx', ns)
        self.assertNotIn('z', ns)

# =====================
# Help formatting tests
# =====================

kundi TestHelpFormattingMetaclass(type):

    eleza __init__(cls, name, bases, bodydict):
        ikiwa name == 'HelpTestCase':
            return

        kundi AddTests(object):

            eleza __init__(self, test_class, func_suffix, std_name):
                self.func_suffix = func_suffix
                self.std_name = std_name

                for test_func in [self.test_format,
                                  self.test_print,
                                  self.test_print_file]:
                    test_name = '%s_%s' % (test_func.__name__, func_suffix)

                    eleza test_wrapper(self, test_func=test_func):
                        test_func(self)
                    try:
                        test_wrapper.__name__ = test_name
                    except TypeError:
                        pass
                    setattr(test_class, test_name, test_wrapper)

            eleza _get_parser(self, tester):
                parser = argparse.ArgumentParser(
                    *tester.parser_signature.args,
                    **tester.parser_signature.kwargs)
                for argument_sig in getattr(tester, 'argument_signatures', []):
                    parser.add_argument(*argument_sig.args,
                                        **argument_sig.kwargs)
                group_sigs = getattr(tester, 'argument_group_signatures', [])
                for group_sig, argument_sigs in group_sigs:
                    group = parser.add_argument_group(*group_sig.args,
                                                      **group_sig.kwargs)
                    for argument_sig in argument_sigs:
                        group.add_argument(*argument_sig.args,
                                           **argument_sig.kwargs)
                subparsers_sigs = getattr(tester, 'subparsers_signatures', [])
                ikiwa subparsers_sigs:
                    subparsers = parser.add_subparsers()
                    for subparser_sig in subparsers_sigs:
                        subparsers.add_parser(*subparser_sig.args,
                                               **subparser_sig.kwargs)
                rudisha parser

            eleza _test(self, tester, parser_text):
                expected_text = getattr(tester, self.func_suffix)
                expected_text = textwrap.dedent(expected_text)
                tester.assertEqual(expected_text, parser_text)

            eleza test_format(self, tester):
                parser = self._get_parser(tester)
                format = getattr(parser, 'format_%s' % self.func_suffix)
                self._test(tester, format())

            eleza test_andika(self, tester):
                parser = self._get_parser(tester)
                print_ = getattr(parser, 'print_%s' % self.func_suffix)
                old_stream = getattr(sys, self.std_name)
                setattr(sys, self.std_name, StdIOBuffer())
                try:
                    print_()
                    parser_text = getattr(sys, self.std_name).getvalue()
                finally:
                    setattr(sys, self.std_name, old_stream)
                self._test(tester, parser_text)

            eleza test_print_file(self, tester):
                parser = self._get_parser(tester)
                print_ = getattr(parser, 'print_%s' % self.func_suffix)
                sfile = StdIOBuffer()
                print_(sfile)
                parser_text = sfile.getvalue()
                self._test(tester, parser_text)

        # add tests for {format,print}_{usage,help}
        for func_suffix, std_name in [('usage', 'stdout'),
                                      ('help', 'stdout')]:
            AddTests(cls, func_suffix, std_name)

bases = TestCase,
HelpTestCase = TestHelpFormattingMetaclass('HelpTestCase', bases, {})


kundi TestHelpBiggerOptionals(HelpTestCase):
    """Make sure that argument help aligns when options are longer"""

    parser_signature = Sig(prog='PROG', description='DESCRIPTION',
                           epilog='EPILOG')
    argument_signatures = [
        Sig('-v', '--version', action='version', version='0.1'),
        Sig('-x', action='store_true', help='X HELP'),
        Sig('--y', help='Y HELP'),
        Sig('foo', help='FOO HELP'),
        Sig('bar', help='BAR HELP'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-v] [-x] [--y Y] foo bar
        '''
    help = usage + '''\

        DESCRIPTION

        positional arguments:
          foo            FOO HELP
          bar            BAR HELP

        optional arguments:
          -h, --help     show this help message and exit
          -v, --version  show program's version number and exit
          -x             X HELP
          --y Y          Y HELP

        EPILOG
    '''
    version = '''\
        0.1
        '''

kundi TestShortColumns(HelpTestCase):
    '''Test extremely small number of columns.

    TestCase prevents "COLUMNS" kutoka being too small in the tests themselves,
    but we don't want any exceptions thrown in such cases. Only ugly representation.
    '''
    eleza setUp(self):
        env = support.EnvironmentVarGuard()
        env.set("COLUMNS", '15')
        self.addCleanup(env.__exit__)

    parser_signature            = TestHelpBiggerOptionals.parser_signature
    argument_signatures         = TestHelpBiggerOptionals.argument_signatures
    argument_group_signatures   = TestHelpBiggerOptionals.argument_group_signatures
    usage = '''\
        usage: PROG
               [-h]
               [-v]
               [-x]
               [--y Y]
               foo
               bar
        '''
    help = usage + '''\

        DESCRIPTION

        positional arguments:
          foo
            FOO HELP
          bar
            BAR HELP

        optional arguments:
          -h, --help
            show this
            help
            message and
            exit
          -v, --version
            show
            program's
            version
            number and
            exit
          -x
            X HELP
          --y Y
            Y HELP

        EPILOG
    '''
    version                     = TestHelpBiggerOptionals.version


kundi TestHelpBiggerOptionalGroups(HelpTestCase):
    """Make sure that argument help aligns when options are longer"""

    parser_signature = Sig(prog='PROG', description='DESCRIPTION',
                           epilog='EPILOG')
    argument_signatures = [
        Sig('-v', '--version', action='version', version='0.1'),
        Sig('-x', action='store_true', help='X HELP'),
        Sig('--y', help='Y HELP'),
        Sig('foo', help='FOO HELP'),
        Sig('bar', help='BAR HELP'),
    ]
    argument_group_signatures = [
        (Sig('GROUP TITLE', description='GROUP DESCRIPTION'), [
            Sig('baz', help='BAZ HELP'),
            Sig('-z', nargs='+', help='Z HELP')]),
    ]
    usage = '''\
        usage: PROG [-h] [-v] [-x] [--y Y] [-z Z [Z ...]] foo bar baz
        '''
    help = usage + '''\

        DESCRIPTION

        positional arguments:
          foo            FOO HELP
          bar            BAR HELP

        optional arguments:
          -h, --help     show this help message and exit
          -v, --version  show program's version number and exit
          -x             X HELP
          --y Y          Y HELP

        GROUP TITLE:
          GROUP DESCRIPTION

          baz            BAZ HELP
          -z Z [Z ...]   Z HELP

        EPILOG
    '''
    version = '''\
        0.1
        '''


kundi TestHelpBiggerPositionals(HelpTestCase):
    """Make sure that help aligns when arguments are longer"""

    parser_signature = Sig(usage='USAGE', description='DESCRIPTION')
    argument_signatures = [
        Sig('-x', action='store_true', help='X HELP'),
        Sig('--y', help='Y HELP'),
        Sig('ekiekiekifekang', help='EKI HELP'),
        Sig('bar', help='BAR HELP'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: USAGE
        '''
    help = usage + '''\

        DESCRIPTION

        positional arguments:
          ekiekiekifekang  EKI HELP
          bar              BAR HELP

        optional arguments:
          -h, --help       show this help message and exit
          -x               X HELP
          --y Y            Y HELP
        '''

    version = ''


kundi TestHelpReformatting(HelpTestCase):
    """Make sure that text after short names starts on the first line"""

    parser_signature = Sig(
        prog='PROG',
        description='   oddly    formatted\n'
                    'description\n'
                    '\n'
                    'that is so long that it should go onto multiple '
                    'lines when wrapped')
    argument_signatures = [
        Sig('-x', metavar='XX', help='oddly\n'
                                     '    formatted -x help'),
        Sig('y', metavar='yyy', help='normal y help'),
    ]
    argument_group_signatures = [
        (Sig('title', description='\n'
                                  '    oddly formatted group\n'
                                  '\n'
                                  'description'),
         [Sig('-a', action='store_true',
              help=' oddly \n'
                   'formatted    -a  help  \n'
                   '    again, so long that it should be wrapped over '
                   'multiple lines')]),
    ]
    usage = '''\
        usage: PROG [-h] [-x XX] [-a] yyy
        '''
    help = usage + '''\

        oddly formatted description that is so long that it should go onto \
multiple
        lines when wrapped

        positional arguments:
          yyy         normal y help

        optional arguments:
          -h, --help  show this help message and exit
          -x XX       oddly formatted -x help

        title:
          oddly formatted group description

          -a          oddly formatted -a help again, so long that it should \
be wrapped
                      over multiple lines
        '''
    version = ''


kundi TestHelpWrappingShortNames(HelpTestCase):
    """Make sure that text after short names starts on the first line"""

    parser_signature = Sig(prog='PROG', description= 'D\nD' * 30)
    argument_signatures = [
        Sig('-x', metavar='XX', help='XHH HX' * 20),
        Sig('y', metavar='yyy', help='YH YH' * 20),
    ]
    argument_group_signatures = [
        (Sig('ALPHAS'), [
            Sig('-a', action='store_true', help='AHHH HHA' * 10)]),
    ]
    usage = '''\
        usage: PROG [-h] [-x XX] [-a] yyy
        '''
    help = usage + '''\

        D DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD \
DD DD DD
        DD DD DD DD D

        positional arguments:
          yyy         YH YHYH YHYH YHYH YHYH YHYH YHYH YHYH YHYH YHYH YHYH \
YHYH YHYH
                      YHYH YHYH YHYH YHYH YHYH YHYH YHYH YH

        optional arguments:
          -h, --help  show this help message and exit
          -x XX       XHH HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH \
HXXHH HXXHH
                      HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH HXXHH HX

        ALPHAS:
          -a          AHHH HHAAHHH HHAAHHH HHAAHHH HHAAHHH HHAAHHH HHAAHHH \
HHAAHHH
                      HHAAHHH HHAAHHH HHA
        '''
    version = ''


kundi TestHelpWrappingLongNames(HelpTestCase):
    """Make sure that text after long names starts on the next line"""

    parser_signature = Sig(usage='USAGE', description= 'D D' * 30)
    argument_signatures = [
        Sig('-v', '--version', action='version', version='V V' * 30),
        Sig('-x', metavar='X' * 25, help='XH XH' * 20),
        Sig('y', metavar='y' * 25, help='YH YH' * 20),
    ]
    argument_group_signatures = [
        (Sig('ALPHAS'), [
            Sig('-a', metavar='A' * 25, help='AH AH' * 20),
            Sig('z', metavar='z' * 25, help='ZH ZH' * 20)]),
    ]
    usage = '''\
        usage: USAGE
        '''
    help = usage + '''\

        D DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD DD \
DD DD DD
        DD DD DD DD D

        positional arguments:
          yyyyyyyyyyyyyyyyyyyyyyyyy
                                YH YHYH YHYH YHYH YHYH YHYH YHYH YHYH YHYH \
YHYH YHYH
                                YHYH YHYH YHYH YHYH YHYH YHYH YHYH YHYH YHYH YH

        optional arguments:
          -h, --help            show this help message and exit
          -v, --version         show program's version number and exit
          -x XXXXXXXXXXXXXXXXXXXXXXXXX
                                XH XHXH XHXH XHXH XHXH XHXH XHXH XHXH XHXH \
XHXH XHXH
                                XHXH XHXH XHXH XHXH XHXH XHXH XHXH XHXH XHXH XH

        ALPHAS:
          -a AAAAAAAAAAAAAAAAAAAAAAAAA
                                AH AHAH AHAH AHAH AHAH AHAH AHAH AHAH AHAH \
AHAH AHAH
                                AHAH AHAH AHAH AHAH AHAH AHAH AHAH AHAH AHAH AH
          zzzzzzzzzzzzzzzzzzzzzzzzz
                                ZH ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH \
ZHZH ZHZH
                                ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH ZHZH ZH
        '''
    version = '''\
        V VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV VV \
VV VV VV
        VV VV VV VV V
        '''


kundi TestHelpUsage(HelpTestCase):
    """Test basic usage messages"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-w', nargs='+', help='w'),
        Sig('-x', nargs='*', help='x'),
        Sig('a', help='a'),
        Sig('b', help='b', nargs=2),
        Sig('c', help='c', nargs='?'),
    ]
    argument_group_signatures = [
        (Sig('group'), [
            Sig('-y', nargs='?', help='y'),
            Sig('-z', nargs=3, help='z'),
            Sig('d', help='d', nargs='*'),
            Sig('e', help='e', nargs='+'),
        ])
    ]
    usage = '''\
        usage: PROG [-h] [-w W [W ...]] [-x [X [X ...]]] [-y [Y]] [-z Z Z Z]
                    a b b [c] [d [d ...]] e [e ...]
        '''
    help = usage + '''\

        positional arguments:
          a               a
          b               b
          c               c

        optional arguments:
          -h, --help      show this help message and exit
          -w W [W ...]    w
          -x [X [X ...]]  x

        group:
          -y [Y]          y
          -z Z Z Z        z
          d               d
          e               e
        '''
    version = ''


kundi TestHelpOnlyUserGroups(HelpTestCase):
    """Test basic usage messages"""

    parser_signature = Sig(prog='PROG', add_help=False)
    argument_signatures = []
    argument_group_signatures = [
        (Sig('xxxx'), [
            Sig('-x', help='x'),
            Sig('a', help='a'),
        ]),
        (Sig('yyyy'), [
            Sig('b', help='b'),
            Sig('-y', help='y'),
        ]),
    ]
    usage = '''\
        usage: PROG [-x X] [-y Y] a b
        '''
    help = usage + '''\

        xxxx:
          -x X  x
          a     a

        yyyy:
          b     b
          -y Y  y
        '''
    version = ''


kundi TestHelpUsageLongProg(HelpTestCase):
    """Test usage messages where the prog is long"""

    parser_signature = Sig(prog='P' * 60)
    argument_signatures = [
        Sig('-w', metavar='W'),
        Sig('-x', metavar='X'),
        Sig('a'),
        Sig('b'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
               [-h] [-w W] [-x X] a b
        '''
    help = usage + '''\

        positional arguments:
          a
          b

        optional arguments:
          -h, --help  show this help message and exit
          -w W
          -x X
        '''
    version = ''


kundi TestHelpUsageLongProgOptionsWrap(HelpTestCase):
    """Test usage messages where the prog is long and the optionals wrap"""

    parser_signature = Sig(prog='P' * 60)
    argument_signatures = [
        Sig('-w', metavar='W' * 25),
        Sig('-x', metavar='X' * 25),
        Sig('-y', metavar='Y' * 25),
        Sig('-z', metavar='Z' * 25),
        Sig('a'),
        Sig('b'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
               [-h] [-w WWWWWWWWWWWWWWWWWWWWWWWWW] \
[-x XXXXXXXXXXXXXXXXXXXXXXXXX]
               [-y YYYYYYYYYYYYYYYYYYYYYYYYY] [-z ZZZZZZZZZZZZZZZZZZZZZZZZZ]
               a b
        '''
    help = usage + '''\

        positional arguments:
          a
          b

        optional arguments:
          -h, --help            show this help message and exit
          -w WWWWWWWWWWWWWWWWWWWWWWWWW
          -x XXXXXXXXXXXXXXXXXXXXXXXXX
          -y YYYYYYYYYYYYYYYYYYYYYYYYY
          -z ZZZZZZZZZZZZZZZZZZZZZZZZZ
        '''
    version = ''


kundi TestHelpUsageLongProgPositionalsWrap(HelpTestCase):
    """Test usage messages where the prog is long and the positionals wrap"""

    parser_signature = Sig(prog='P' * 60, add_help=False)
    argument_signatures = [
        Sig('a' * 25),
        Sig('b' * 25),
        Sig('c' * 25),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
               aaaaaaaaaaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbbbbbbbbbb
               ccccccccccccccccccccccccc
        '''
    help = usage + '''\

        positional arguments:
          aaaaaaaaaaaaaaaaaaaaaaaaa
          bbbbbbbbbbbbbbbbbbbbbbbbb
          ccccccccccccccccccccccccc
        '''
    version = ''


kundi TestHelpUsageOptionalsWrap(HelpTestCase):
    """Test usage messages where the optionals wrap"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-w', metavar='W' * 25),
        Sig('-x', metavar='X' * 25),
        Sig('-y', metavar='Y' * 25),
        Sig('-z', metavar='Z' * 25),
        Sig('a'),
        Sig('b'),
        Sig('c'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-w WWWWWWWWWWWWWWWWWWWWWWWWW] \
[-x XXXXXXXXXXXXXXXXXXXXXXXXX]
                    [-y YYYYYYYYYYYYYYYYYYYYYYYYY] \
[-z ZZZZZZZZZZZZZZZZZZZZZZZZZ]
                    a b c
        '''
    help = usage + '''\

        positional arguments:
          a
          b
          c

        optional arguments:
          -h, --help            show this help message and exit
          -w WWWWWWWWWWWWWWWWWWWWWWWWW
          -x XXXXXXXXXXXXXXXXXXXXXXXXX
          -y YYYYYYYYYYYYYYYYYYYYYYYYY
          -z ZZZZZZZZZZZZZZZZZZZZZZZZZ
        '''
    version = ''


kundi TestHelpUsagePositionalsWrap(HelpTestCase):
    """Test usage messages where the positionals wrap"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-x'),
        Sig('-y'),
        Sig('-z'),
        Sig('a' * 25),
        Sig('b' * 25),
        Sig('c' * 25),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-x X] [-y Y] [-z Z]
                    aaaaaaaaaaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbbbbbbbbbb
                    ccccccccccccccccccccccccc
        '''
    help = usage + '''\

        positional arguments:
          aaaaaaaaaaaaaaaaaaaaaaaaa
          bbbbbbbbbbbbbbbbbbbbbbbbb
          ccccccccccccccccccccccccc

        optional arguments:
          -h, --help            show this help message and exit
          -x X
          -y Y
          -z Z
        '''
    version = ''


kundi TestHelpUsageOptionalsPositionalsWrap(HelpTestCase):
    """Test usage messages where the optionals and positionals wrap"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-x', metavar='X' * 25),
        Sig('-y', metavar='Y' * 25),
        Sig('-z', metavar='Z' * 25),
        Sig('a' * 25),
        Sig('b' * 25),
        Sig('c' * 25),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-x XXXXXXXXXXXXXXXXXXXXXXXXX] \
[-y YYYYYYYYYYYYYYYYYYYYYYYYY]
                    [-z ZZZZZZZZZZZZZZZZZZZZZZZZZ]
                    aaaaaaaaaaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbbbbbbbbbb
                    ccccccccccccccccccccccccc
        '''
    help = usage + '''\

        positional arguments:
          aaaaaaaaaaaaaaaaaaaaaaaaa
          bbbbbbbbbbbbbbbbbbbbbbbbb
          ccccccccccccccccccccccccc

        optional arguments:
          -h, --help            show this help message and exit
          -x XXXXXXXXXXXXXXXXXXXXXXXXX
          -y YYYYYYYYYYYYYYYYYYYYYYYYY
          -z ZZZZZZZZZZZZZZZZZZZZZZZZZ
        '''
    version = ''


kundi TestHelpUsageOptionalsOnlyWrap(HelpTestCase):
    """Test usage messages where there are only optionals and they wrap"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-x', metavar='X' * 25),
        Sig('-y', metavar='Y' * 25),
        Sig('-z', metavar='Z' * 25),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-x XXXXXXXXXXXXXXXXXXXXXXXXX] \
[-y YYYYYYYYYYYYYYYYYYYYYYYYY]
                    [-z ZZZZZZZZZZZZZZZZZZZZZZZZZ]
        '''
    help = usage + '''\

        optional arguments:
          -h, --help            show this help message and exit
          -x XXXXXXXXXXXXXXXXXXXXXXXXX
          -y YYYYYYYYYYYYYYYYYYYYYYYYY
          -z ZZZZZZZZZZZZZZZZZZZZZZZZZ
        '''
    version = ''


kundi TestHelpUsagePositionalsOnlyWrap(HelpTestCase):
    """Test usage messages where there are only positionals and they wrap"""

    parser_signature = Sig(prog='PROG', add_help=False)
    argument_signatures = [
        Sig('a' * 25),
        Sig('b' * 25),
        Sig('c' * 25),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG aaaaaaaaaaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbbbbbbbbbb
                    ccccccccccccccccccccccccc
        '''
    help = usage + '''\

        positional arguments:
          aaaaaaaaaaaaaaaaaaaaaaaaa
          bbbbbbbbbbbbbbbbbbbbbbbbb
          ccccccccccccccccccccccccc
        '''
    version = ''


kundi TestHelpVariableExpansion(HelpTestCase):
    """Test that variables are expanded properly in help messages"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-x', type=int,
            help='x %(prog)s %(default)s %(type)s %%'),
        Sig('-y', action='store_const', default=42, const='XXX',
            help='y %(prog)s %(default)s %(const)s'),
        Sig('--foo', choices='abc',
            help='foo %(prog)s %(default)s %(choices)s'),
        Sig('--bar', default='baz', choices=[1, 2], metavar='BBB',
            help='bar %(prog)s %(default)s %(dest)s'),
        Sig('spam', help='spam %(prog)s %(default)s'),
        Sig('badger', default=0.5, help='badger %(prog)s %(default)s'),
    ]
    argument_group_signatures = [
        (Sig('group'), [
            Sig('-a', help='a %(prog)s %(default)s'),
            Sig('-b', default=-1, help='b %(prog)s %(default)s'),
        ])
    ]
    usage = ('''\
        usage: PROG [-h] [-x X] [-y] [--foo {a,b,c}] [--bar BBB] [-a A] [-b B]
                    spam badger
        ''')
    help = usage + '''\

        positional arguments:
          spam           spam PROG None
          badger         badger PROG 0.5

        optional arguments:
          -h, --help     show this help message and exit
          -x X           x PROG None int %
          -y             y PROG 42 XXX
          --foo {a,b,c}  foo PROG None a, b, c
          --bar BBB      bar PROG baz bar

        group:
          -a A           a PROG None
          -b B           b PROG -1
        '''
    version = ''


kundi TestHelpVariableExpansionUsageSupplied(HelpTestCase):
    """Test that variables are expanded properly when usage= is present"""

    parser_signature = Sig(prog='PROG', usage='%(prog)s FOO')
    argument_signatures = []
    argument_group_signatures = []
    usage = ('''\
        usage: PROG FOO
        ''')
    help = usage + '''\

        optional arguments:
          -h, --help  show this help message and exit
        '''
    version = ''


kundi TestHelpVariableExpansionNoArguments(HelpTestCase):
    """Test that variables are expanded properly with no arguments"""

    parser_signature = Sig(prog='PROG', add_help=False)
    argument_signatures = []
    argument_group_signatures = []
    usage = ('''\
        usage: PROG
        ''')
    help = usage
    version = ''


kundi TestHelpSuppressUsage(HelpTestCase):
    """Test that items can be suppressed in usage messages"""

    parser_signature = Sig(prog='PROG', usage=argparse.SUPPRESS)
    argument_signatures = [
        Sig('--foo', help='foo help'),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = []
    help = '''\
        positional arguments:
          spam        spam help

        optional arguments:
          -h, --help  show this help message and exit
          --foo FOO   foo help
        '''
    usage = ''
    version = ''


kundi TestHelpSuppressOptional(HelpTestCase):
    """Test that optional arguments can be suppressed in help messages"""

    parser_signature = Sig(prog='PROG', add_help=False)
    argument_signatures = [
        Sig('--foo', help=argparse.SUPPRESS),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG spam
        '''
    help = usage + '''\

        positional arguments:
          spam  spam help
        '''
    version = ''


kundi TestHelpSuppressOptionalGroup(HelpTestCase):
    """Test that optional groups can be suppressed in help messages"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('--foo', help='foo help'),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = [
        (Sig('group'), [Sig('--bar', help=argparse.SUPPRESS)]),
    ]
    usage = '''\
        usage: PROG [-h] [--foo FOO] spam
        '''
    help = usage + '''\

        positional arguments:
          spam        spam help

        optional arguments:
          -h, --help  show this help message and exit
          --foo FOO   foo help
        '''
    version = ''


kundi TestHelpSuppressPositional(HelpTestCase):
    """Test that positional arguments can be suppressed in help messages"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('--foo', help='foo help'),
        Sig('spam', help=argparse.SUPPRESS),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [--foo FOO]
        '''
    help = usage + '''\

        optional arguments:
          -h, --help  show this help message and exit
          --foo FOO   foo help
        '''
    version = ''


kundi TestHelpRequiredOptional(HelpTestCase):
    """Test that required options don't look optional"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('--foo', required=True, help='foo help'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] --foo FOO
        '''
    help = usage + '''\

        optional arguments:
          -h, --help  show this help message and exit
          --foo FOO   foo help
        '''
    version = ''


kundi TestHelpAlternatePrefixChars(HelpTestCase):
    """Test that options display with different prefix characters"""

    parser_signature = Sig(prog='PROG', prefix_chars='^;', add_help=False)
    argument_signatures = [
        Sig('^^foo', action='store_true', help='foo help'),
        Sig(';b', ';;bar', help='bar help'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [^^foo] [;b BAR]
        '''
    help = usage + '''\

        optional arguments:
          ^^foo              foo help
          ;b BAR, ;;bar BAR  bar help
        '''
    version = ''


kundi TestHelpNoHelpOptional(HelpTestCase):
    """Test that the --help argument can be suppressed help messages"""

    parser_signature = Sig(prog='PROG', add_help=False)
    argument_signatures = [
        Sig('--foo', help='foo help'),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [--foo FOO] spam
        '''
    help = usage + '''\

        positional arguments:
          spam       spam help

        optional arguments:
          --foo FOO  foo help
        '''
    version = ''


kundi TestHelpNone(HelpTestCase):
    """Test that no errors occur ikiwa no help is specified"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('--foo'),
        Sig('spam'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [--foo FOO] spam
        '''
    help = usage + '''\

        positional arguments:
          spam

        optional arguments:
          -h, --help  show this help message and exit
          --foo FOO
        '''
    version = ''


kundi TestHelpTupleMetavar(HelpTestCase):
    """Test specifying metavar as a tuple"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-w', help='w', nargs='+', metavar=('W1', 'W2')),
        Sig('-x', help='x', nargs='*', metavar=('X1', 'X2')),
        Sig('-y', help='y', nargs=3, metavar=('Y1', 'Y2', 'Y3')),
        Sig('-z', help='z', nargs='?', metavar=('Z1', )),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-w W1 [W2 ...]] [-x [X1 [X2 ...]]] [-y Y1 Y2 Y3] \
[-z [Z1]]
        '''
    help = usage + '''\

        optional arguments:
          -h, --help        show this help message and exit
          -w W1 [W2 ...]    w
          -x [X1 [X2 ...]]  x
          -y Y1 Y2 Y3       y
          -z [Z1]           z
        '''
    version = ''


kundi TestHelpRawText(HelpTestCase):
    """Test the RawTextHelpFormatter"""

    parser_signature = Sig(
        prog='PROG', formatter_class=argparse.RawTextHelpFormatter,
        description='Keep the formatting\n'
                    '    exactly as it is written\n'
                    '\n'
                    'here\n')

    argument_signatures = [
        Sig('--foo', help='    foo help should also\n'
                          'appear as given here'),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = [
        (Sig('title', description='    This text\n'
                                  '  should be indented\n'
                                  '    exactly like it is here\n'),
         [Sig('--bar', help='bar help')]),
    ]
    usage = '''\
        usage: PROG [-h] [--foo FOO] [--bar BAR] spam
        '''
    help = usage + '''\

        Keep the formatting
            exactly as it is written

        here

        positional arguments:
          spam        spam help

        optional arguments:
          -h, --help  show this help message and exit
          --foo FOO       foo help should also
                      appear as given here

        title:
              This text
            should be indented
              exactly like it is here

          --bar BAR   bar help
        '''
    version = ''


kundi TestHelpRawDescription(HelpTestCase):
    """Test the RawTextHelpFormatter"""

    parser_signature = Sig(
        prog='PROG', formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Keep the formatting\n'
                    '    exactly as it is written\n'
                    '\n'
                    'here\n')

    argument_signatures = [
        Sig('--foo', help='  foo help should not\n'
                          '    retain this odd formatting'),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = [
        (Sig('title', description='    This text\n'
                                  '  should be indented\n'
                                  '    exactly like it is here\n'),
         [Sig('--bar', help='bar help')]),
    ]
    usage = '''\
        usage: PROG [-h] [--foo FOO] [--bar BAR] spam
        '''
    help = usage + '''\

        Keep the formatting
            exactly as it is written

        here

        positional arguments:
          spam        spam help

        optional arguments:
          -h, --help  show this help message and exit
          --foo FOO   foo help should not retain this odd formatting

        title:
              This text
            should be indented
              exactly like it is here

          --bar BAR   bar help
        '''
    version = ''


kundi TestHelpArgumentDefaults(HelpTestCase):
    """Test the ArgumentDefaultsHelpFormatter"""

    parser_signature = Sig(
        prog='PROG', formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='description')

    argument_signatures = [
        Sig('--foo', help='foo help - oh and by the way, %(default)s'),
        Sig('--bar', action='store_true', help='bar help'),
        Sig('spam', help='spam help'),
        Sig('badger', nargs='?', default='wooden', help='badger help'),
    ]
    argument_group_signatures = [
        (Sig('title', description='description'),
         [Sig('--baz', type=int, default=42, help='baz help')]),
    ]
    usage = '''\
        usage: PROG [-h] [--foo FOO] [--bar] [--baz BAZ] spam [badger]
        '''
    help = usage + '''\

        description

        positional arguments:
          spam        spam help
          badger      badger help (default: wooden)

        optional arguments:
          -h, --help  show this help message and exit
          --foo FOO   foo help - oh and by the way, None
          --bar       bar help (default: False)

        title:
          description

          --baz BAZ   baz help (default: 42)
        '''
    version = ''

kundi TestHelpVersionAction(HelpTestCase):
    """Test the default help for the version action"""

    parser_signature = Sig(prog='PROG', description='description')
    argument_signatures = [Sig('-V', '--version', action='version', version='3.6')]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-V]
        '''
    help = usage + '''\

        description

        optional arguments:
          -h, --help     show this help message and exit
          -V, --version  show program's version number and exit
        '''
    version = ''


kundi TestHelpVersionActionSuppress(HelpTestCase):
    """Test that the --version argument can be suppressed in help messages"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('-v', '--version', action='version', version='1.0',
            help=argparse.SUPPRESS),
        Sig('--foo', help='foo help'),
        Sig('spam', help='spam help'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [--foo FOO] spam
        '''
    help = usage + '''\

        positional arguments:
          spam        spam help

        optional arguments:
          -h, --help  show this help message and exit
          --foo FOO   foo help
        '''


kundi TestHelpSubparsersOrdering(HelpTestCase):
    """Test ordering of subcommands in help matches the code"""
    parser_signature = Sig(prog='PROG',
                           description='display some subcommands')
    argument_signatures = [Sig('-v', '--version', action='version', version='0.1')]

    subparsers_signatures = [Sig(name=name)
                             for name in ('a', 'b', 'c', 'd', 'e')]

    usage = '''\
        usage: PROG [-h] [-v] {a,b,c,d,e} ...
        '''

    help = usage + '''\

        display some subcommands

        positional arguments:
          {a,b,c,d,e}

        optional arguments:
          -h, --help     show this help message and exit
          -v, --version  show program's version number and exit
        '''

    version = '''\
        0.1
        '''

kundi TestHelpSubparsersWithHelpOrdering(HelpTestCase):
    """Test ordering of subcommands in help matches the code"""
    parser_signature = Sig(prog='PROG',
                           description='display some subcommands')
    argument_signatures = [Sig('-v', '--version', action='version', version='0.1')]

    subcommand_data = (('a', 'a subcommand help'),
                       ('b', 'b subcommand help'),
                       ('c', 'c subcommand help'),
                       ('d', 'd subcommand help'),
                       ('e', 'e subcommand help'),
                       )

    subparsers_signatures = [Sig(name=name, help=help)
                             for name, help in subcommand_data]

    usage = '''\
        usage: PROG [-h] [-v] {a,b,c,d,e} ...
        '''

    help = usage + '''\

        display some subcommands

        positional arguments:
          {a,b,c,d,e}
            a            a subcommand help
            b            b subcommand help
            c            c subcommand help
            d            d subcommand help
            e            e subcommand help

        optional arguments:
          -h, --help     show this help message and exit
          -v, --version  show program's version number and exit
        '''

    version = '''\
        0.1
        '''



kundi TestHelpMetavarTypeFormatter(HelpTestCase):

    eleza custom_type(string):
        rudisha string

    parser_signature = Sig(prog='PROG', description='description',
                           formatter_class=argparse.MetavarTypeHelpFormatter)
    argument_signatures = [Sig('a', type=int),
                           Sig('-b', type=custom_type),
                           Sig('-c', type=float, metavar='SOME FLOAT')]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-b custom_type] [-c SOME FLOAT] int
        '''
    help = usage + '''\

        description

        positional arguments:
          int

        optional arguments:
          -h, --help      show this help message and exit
          -b custom_type
          -c SOME FLOAT
        '''
    version = ''


# =====================================
# Optional/Positional constructor tests
# =====================================

kundi TestInvalidArgumentConstructors(TestCase):
    """Test a bunch of invalid Argument constructors"""

    eleza assertTypeError(self, *args, **kwargs):
        parser = argparse.ArgumentParser()
        self.assertRaises(TypeError, parser.add_argument,
                          *args, **kwargs)

    eleza assertValueError(self, *args, **kwargs):
        parser = argparse.ArgumentParser()
        self.assertRaises(ValueError, parser.add_argument,
                          *args, **kwargs)

    eleza test_invalid_keyword_arguments(self):
        self.assertTypeError('-x', bar=None)
        self.assertTypeError('-y', callback='foo')
        self.assertTypeError('-y', callback_args=())
        self.assertTypeError('-y', callback_kwargs={})

    eleza test_missing_destination(self):
        self.assertTypeError()
        for action in ['append', 'store']:
            self.assertTypeError(action=action)

    eleza test_invalid_option_strings(self):
        self.assertValueError('--')
        self.assertValueError('---')

    eleza test_invalid_type(self):
        self.assertValueError('--foo', type='int')
        self.assertValueError('--foo', type=(int, float))

    eleza test_invalid_action(self):
        self.assertValueError('-x', action='foo')
        self.assertValueError('foo', action='baz')
        self.assertValueError('--foo', action=('store', 'append'))
        parser = argparse.ArgumentParser()
        with self.assertRaises(ValueError) as cm:
            parser.add_argument("--foo", action="store-true")
        self.assertIn('unknown action', str(cm.exception))

    eleza test_multiple_dest(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(dest='foo')
        with self.assertRaises(ValueError) as cm:
            parser.add_argument('bar', dest='baz')
        self.assertIn('dest supplied twice for positional argument',
                      str(cm.exception))

    eleza test_no_argument_actions(self):
        for action in ['store_const', 'store_true', 'store_false',
                       'append_const', 'count']:
            for attrs in [dict(type=int), dict(nargs='+'),
                          dict(choices='ab')]:
                self.assertTypeError('-x', action=action, **attrs)

    eleza test_no_argument_no_const_actions(self):
        # options with zero arguments
        for action in ['store_true', 'store_false', 'count']:

            # const is always disallowed
            self.assertTypeError('-x', const='foo', action=action)

            # nargs is always disallowed
            self.assertTypeError('-x', nargs='*', action=action)

    eleza test_more_than_one_argument_actions(self):
        for action in ['store', 'append']:

            # nargs=0 is disallowed
            self.assertValueError('-x', nargs=0, action=action)
            self.assertValueError('spam', nargs=0, action=action)

            # const is disallowed with non-optional arguments
            for nargs in [1, '*', '+']:
                self.assertValueError('-x', const='foo',
                                      nargs=nargs, action=action)
                self.assertValueError('spam', const='foo',
                                      nargs=nargs, action=action)

    eleza test_required_const_actions(self):
        for action in ['store_const', 'append_const']:

            # nargs is always disallowed
            self.assertTypeError('-x', nargs='+', action=action)

    eleza test_parsers_action_missing_params(self):
        self.assertTypeError('command', action='parsers')
        self.assertTypeError('command', action='parsers', prog='PROG')
        self.assertTypeError('command', action='parsers',
                             parser_class=argparse.ArgumentParser)

    eleza test_required_positional(self):
        self.assertTypeError('foo', required=True)

    eleza test_user_defined_action(self):

        kundi Success(Exception):
            pass

        kundi Action(object):

            eleza __init__(self,
                         option_strings,
                         dest,
                         const,
                         default,
                         required=False):
                ikiwa dest == 'spam':
                    ikiwa const is Success:
                        ikiwa default is Success:
                            raise Success()

            eleza __call__(self, *args, **kwargs):
                pass

        parser = argparse.ArgumentParser()
        self.assertRaises(Success, parser.add_argument, '--spam',
                          action=Action, default=Success, const=Success)
        self.assertRaises(Success, parser.add_argument, 'spam',
                          action=Action, default=Success, const=Success)

# ================================
# Actions returned by add_argument
# ================================

kundi TestActionsReturned(TestCase):

    eleza test_dest(self):
        parser = argparse.ArgumentParser()
        action = parser.add_argument('--foo')
        self.assertEqual(action.dest, 'foo')
        action = parser.add_argument('-b', '--bar')
        self.assertEqual(action.dest, 'bar')
        action = parser.add_argument('-x', '-y')
        self.assertEqual(action.dest, 'x')

    eleza test_misc(self):
        parser = argparse.ArgumentParser()
        action = parser.add_argument('--foo', nargs='?', const=42,
                                     default=84, type=int, choices=[1, 2],
                                     help='FOO', metavar='BAR', dest='baz')
        self.assertEqual(action.nargs, '?')
        self.assertEqual(action.const, 42)
        self.assertEqual(action.default, 84)
        self.assertEqual(action.type, int)
        self.assertEqual(action.choices, [1, 2])
        self.assertEqual(action.help, 'FOO')
        self.assertEqual(action.metavar, 'BAR')
        self.assertEqual(action.dest, 'baz')


# ================================
# Argument conflict handling tests
# ================================

kundi TestConflictHandling(TestCase):

    eleza test_bad_type(self):
        self.assertRaises(ValueError, argparse.ArgumentParser,
                          conflict_handler='foo')

    eleza test_conflict_error(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-x')
        self.assertRaises(argparse.ArgumentError,
                          parser.add_argument, '-x')
        parser.add_argument('--spam')
        self.assertRaises(argparse.ArgumentError,
                          parser.add_argument, '--spam')

    eleza test_resolve_error(self):
        get_parser = argparse.ArgumentParser
        parser = get_parser(prog='PROG', conflict_handler='resolve')

        parser.add_argument('-x', help='OLD X')
        parser.add_argument('-x', help='NEW X')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
            usage: PROG [-h] [-x X]

            optional arguments:
              -h, --help  show this help message and exit
              -x X        NEW X
            '''))

        parser.add_argument('--spam', metavar='OLD_SPAM')
        parser.add_argument('--spam', metavar='NEW_SPAM')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
            usage: PROG [-h] [-x X] [--spam NEW_SPAM]

            optional arguments:
              -h, --help       show this help message and exit
              -x X             NEW X
              --spam NEW_SPAM
            '''))


# =============================
# Help and Version option tests
# =============================

kundi TestOptionalsHelpVersionActions(TestCase):
    """Test the help and version actions"""

    eleza assertPrintHelpExit(self, parser, args_str):
        with self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args(args_str.split())
        self.assertEqual(parser.format_help(), cm.exception.stdout)

    eleza assertArgumentParserError(self, parser, *args):
        self.assertRaises(ArgumentParserError, parser.parse_args, args)

    eleza test_version(self):
        parser = ErrorRaisingArgumentParser()
        parser.add_argument('-v', '--version', action='version', version='1.0')
        self.assertPrintHelpExit(parser, '-h')
        self.assertPrintHelpExit(parser, '--help')
        self.assertRaises(AttributeError, getattr, parser, 'format_version')

    eleza test_version_format(self):
        parser = ErrorRaisingArgumentParser(prog='PPP')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s 3.5')
        with self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args(['-v'])
        self.assertEqual('PPP 3.5\n', cm.exception.stdout)

    eleza test_version_no_help(self):
        parser = ErrorRaisingArgumentParser(add_help=False)
        parser.add_argument('-v', '--version', action='version', version='1.0')
        self.assertArgumentParserError(parser, '-h')
        self.assertArgumentParserError(parser, '--help')
        self.assertRaises(AttributeError, getattr, parser, 'format_version')

    eleza test_version_action(self):
        parser = ErrorRaisingArgumentParser(prog='XXX')
        parser.add_argument('-V', action='version', version='%(prog)s 3.7')
        with self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args(['-V'])
        self.assertEqual('XXX 3.7\n', cm.exception.stdout)

    eleza test_no_help(self):
        parser = ErrorRaisingArgumentParser(add_help=False)
        self.assertArgumentParserError(parser, '-h')
        self.assertArgumentParserError(parser, '--help')
        self.assertArgumentParserError(parser, '-v')
        self.assertArgumentParserError(parser, '--version')

    eleza test_alternate_help_version(self):
        parser = ErrorRaisingArgumentParser()
        parser.add_argument('-x', action='help')
        parser.add_argument('-y', action='version')
        self.assertPrintHelpExit(parser, '-x')
        self.assertArgumentParserError(parser, '-v')
        self.assertArgumentParserError(parser, '--version')
        self.assertRaises(AttributeError, getattr, parser, 'format_version')

    eleza test_help_version_extra_arguments(self):
        parser = ErrorRaisingArgumentParser()
        parser.add_argument('--version', action='version', version='1.0')
        parser.add_argument('-x', action='store_true')
        parser.add_argument('y')

        # try all combinations of valid prefixes and suffixes
        valid_prefixes = ['', '-x', 'foo', '-x bar', 'baz -x']
        valid_suffixes = valid_prefixes + ['--bad-option', 'foo bar baz']
        for prefix in valid_prefixes:
            for suffix in valid_suffixes:
                format = '%s %%s %s' % (prefix, suffix)
            self.assertPrintHelpExit(parser, format % '-h')
            self.assertPrintHelpExit(parser, format % '--help')
            self.assertRaises(AttributeError, getattr, parser, 'format_version')


# ======================
# str() and repr() tests
# ======================

kundi TestStrings(TestCase):
    """Test str()  and repr() on Optionals and Positionals"""

    eleza assertStringEqual(self, obj, result_string):
        for func in [str, repr]:
            self.assertEqual(func(obj), result_string)

    eleza test_optional(self):
        option = argparse.Action(
            option_strings=['--foo', '-a', '-b'],
            dest='b',
            type='int',
            nargs='+',
            default=42,
            choices=[1, 2, 3],
            help='HELP',
            metavar='METAVAR')
        string = (
            "Action(option_strings=['--foo', '-a', '-b'], dest='b', "
            "nargs='+', const=None, default=42, type='int', "
            "choices=[1, 2, 3], help='HELP', metavar='METAVAR')")
        self.assertStringEqual(option, string)

    eleza test_argument(self):
        argument = argparse.Action(
            option_strings=[],
            dest='x',
            type=float,
            nargs='?',
            default=2.5,
            choices=[0.5, 1.5, 2.5],
            help='H HH H',
            metavar='MV MV MV')
        string = (
            "Action(option_strings=[], dest='x', nargs='?', "
            "const=None, default=2.5, type=%r, choices=[0.5, 1.5, 2.5], "
            "help='H HH H', metavar='MV MV MV')" % float)
        self.assertStringEqual(argument, string)

    eleza test_namespace(self):
        ns = argparse.Namespace(foo=42, bar='spam')
        string = "Namespace(bar='spam', foo=42)"
        self.assertStringEqual(ns, string)

    eleza test_namespace_starkwargs_notidentifier(self):
        ns = argparse.Namespace(**{'"': 'quote'})
        string = """Namespace(**{'"': 'quote'})"""
        self.assertStringEqual(ns, string)

    eleza test_namespace_kwargs_and_starkwargs_notidentifier(self):
        ns = argparse.Namespace(a=1, **{'"': 'quote'})
        string = """Namespace(a=1, **{'"': 'quote'})"""
        self.assertStringEqual(ns, string)

    eleza test_namespace_starkwargs_identifier(self):
        ns = argparse.Namespace(**{'valid': True})
        string = "Namespace(valid=True)"
        self.assertStringEqual(ns, string)

    eleza test_parser(self):
        parser = argparse.ArgumentParser(prog='PROG')
        string = (
            "ArgumentParser(prog='PROG', usage=None, description=None, "
            "formatter_class=%r, conflict_handler='error', "
            "add_help=True)" % argparse.HelpFormatter)
        self.assertStringEqual(parser, string)

# ===============
# Namespace tests
# ===============

kundi TestNamespace(TestCase):

    eleza test_constructor(self):
        ns = argparse.Namespace()
        self.assertRaises(AttributeError, getattr, ns, 'x')

        ns = argparse.Namespace(a=42, b='spam')
        self.assertEqual(ns.a, 42)
        self.assertEqual(ns.b, 'spam')

    eleza test_equality(self):
        ns1 = argparse.Namespace(a=1, b=2)
        ns2 = argparse.Namespace(b=2, a=1)
        ns3 = argparse.Namespace(a=1)
        ns4 = argparse.Namespace(b=2)

        self.assertEqual(ns1, ns2)
        self.assertNotEqual(ns1, ns3)
        self.assertNotEqual(ns1, ns4)
        self.assertNotEqual(ns2, ns3)
        self.assertNotEqual(ns2, ns4)
        self.assertTrue(ns1 != ns3)
        self.assertTrue(ns1 != ns4)
        self.assertTrue(ns2 != ns3)
        self.assertTrue(ns2 != ns4)

    eleza test_equality_returns_notimplemented(self):
        # See issue 21481
        ns = argparse.Namespace(a=1, b=2)
        self.assertIs(ns.__eq__(None), NotImplemented)
        self.assertIs(ns.__ne__(None), NotImplemented)


# ===================
# File encoding tests
# ===================

kundi TestEncoding(TestCase):

    eleza _test_module_encoding(self, path):
        path, _ = os.path.splitext(path)
        path += ".py"
        with open(path, 'r', encoding='utf-8') as f:
            f.read()

    eleza test_argparse_module_encoding(self):
        self._test_module_encoding(argparse.__file__)

    eleza test_test_argparse_module_encoding(self):
        self._test_module_encoding(__file__)

# ===================
# ArgumentError tests
# ===================

kundi TestArgumentError(TestCase):

    eleza test_argument_error(self):
        msg = "my error here"
        error = argparse.ArgumentError(None, msg)
        self.assertEqual(str(error), msg)

# =======================
# ArgumentTypeError tests
# =======================

kundi TestArgumentTypeError(TestCase):

    eleza test_argument_type_error(self):

        eleza spam(string):
            raise argparse.ArgumentTypeError('spam!')

        parser = ErrorRaisingArgumentParser(prog='PROG', add_help=False)
        parser.add_argument('x', type=spam)
        with self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args(['XXX'])
        self.assertEqual('usage: PROG x\nPROG: error: argument x: spam!\n',
                         cm.exception.stderr)

# =========================
# MessageContentError tests
# =========================

kundi TestMessageContentError(TestCase):

    eleza test_missing_argument_name_in_message(self):
        parser = ErrorRaisingArgumentParser(prog='PROG', usage='')
        parser.add_argument('req_pos', type=str)
        parser.add_argument('-req_opt', type=int, required=True)
        parser.add_argument('need_one', type=str, nargs='+')

        with self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args([])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertRegex(msg, 'req_opt')
        self.assertRegex(msg, 'need_one')
        with self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args(['myXargument'])
        msg = str(cm.exception)
        self.assertNotIn(msg, 'req_pos')
        self.assertRegex(msg, 'req_opt')
        self.assertRegex(msg, 'need_one')
        with self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args(['myXargument', '-req_opt=1'])
        msg = str(cm.exception)
        self.assertNotIn(msg, 'req_pos')
        self.assertNotIn(msg, 'req_opt')
        self.assertRegex(msg, 'need_one')

    eleza test_optional_optional_not_in_message(self):
        parser = ErrorRaisingArgumentParser(prog='PROG', usage='')
        parser.add_argument('req_pos', type=str)
        parser.add_argument('--req_opt', type=int, required=True)
        parser.add_argument('--opt_opt', type=bool, nargs='?',
                            default=True)
        with self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args([])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertRegex(msg, 'req_opt')
        self.assertNotIn(msg, 'opt_opt')
        with self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args(['--req_opt=1'])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertNotIn(msg, 'req_opt')
        self.assertNotIn(msg, 'opt_opt')

    eleza test_optional_positional_not_in_message(self):
        parser = ErrorRaisingArgumentParser(prog='PROG', usage='')
        parser.add_argument('req_pos')
        parser.add_argument('optional_positional', nargs='?', default='eggs')
        with self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args([])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertNotIn(msg, 'optional_positional')


# ================================================
# Check that the type function is called only once
# ================================================

kundi TestTypeFunctionCallOnlyOnce(TestCase):

    eleza test_type_function_call_only_once(self):
        eleza spam(string_to_convert):
            self.assertEqual(string_to_convert, 'spam!')
            rudisha 'foo_converted'

        parser = argparse.ArgumentParser()
        parser.add_argument('--foo', type=spam, default='bar')
        args = parser.parse_args('--foo spam!'.split())
        self.assertEqual(NS(foo='foo_converted'), args)

# ==================================================================
# Check semantics regarding the default argument and type conversion
# ==================================================================

kundi TestTypeFunctionCalledOnDefault(TestCase):

    eleza test_type_function_call_with_non_string_default(self):
        eleza spam(int_to_convert):
            self.assertEqual(int_to_convert, 0)
            rudisha 'foo_converted'

        parser = argparse.ArgumentParser()
        parser.add_argument('--foo', type=spam, default=0)
        args = parser.parse_args([])
        # foo should *not* be converted because its default is not a string.
        self.assertEqual(NS(foo=0), args)

    eleza test_type_function_call_with_string_default(self):
        eleza spam(int_to_convert):
            rudisha 'foo_converted'

        parser = argparse.ArgumentParser()
        parser.add_argument('--foo', type=spam, default='0')
        args = parser.parse_args([])
        # foo is converted because its default is a string.
        self.assertEqual(NS(foo='foo_converted'), args)

    eleza test_no_double_type_conversion_of_default(self):
        eleza extend(str_to_convert):
            rudisha str_to_convert + '*'

        parser = argparse.ArgumentParser()
        parser.add_argument('--test', type=extend, default='*')
        args = parser.parse_args([])
        # The test argument will be two stars, one coming kutoka the default
        # value and one coming kutoka the type conversion being called exactly
        # once.
        self.assertEqual(NS(test='**'), args)

    eleza test_issue_15906(self):
        # Issue #15906: When action='append', type=str, default=[] are
        # providing, the dest value was the string representation "[]" when it
        # should have been an empty list.
        parser = argparse.ArgumentParser()
        parser.add_argument('--test', dest='test', type=str,
                            default=[], action='append')
        args = parser.parse_args([])
        self.assertEqual(args.test, [])

# ======================
# parse_known_args tests
# ======================

kundi TestParseKnownArgs(TestCase):

    eleza test_arguments_tuple(self):
        parser = argparse.ArgumentParser()
        parser.parse_args(())

    eleza test_arguments_list(self):
        parser = argparse.ArgumentParser()
        parser.parse_args([])

    eleza test_arguments_tuple_positional(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('x')
        parser.parse_args(('x',))

    eleza test_arguments_list_positional(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('x')
        parser.parse_args(['x'])

    eleza test_optionals(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--foo')
        args, extras = parser.parse_known_args('--foo F --bar --baz'.split())
        self.assertEqual(NS(foo='F'), args)
        self.assertEqual(['--bar', '--baz'], extras)

    eleza test_mixed(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', nargs='?', const=1, type=int)
        parser.add_argument('--spam', action='store_false')
        parser.add_argument('badger')

        argv = ["B", "C", "--foo", "-v", "3", "4"]
        args, extras = parser.parse_known_args(argv)
        self.assertEqual(NS(v=3, spam=True, badger="B"), args)
        self.assertEqual(["C", "--foo", "4"], extras)

# ===========================
# parse_intermixed_args tests
# ===========================

kundi TestIntermixedArgs(TestCase):
    eleza test_basic(self):
        # test parsing intermixed optionals and positionals
        parser = argparse.ArgumentParser(prog='PROG')
        parser.add_argument('--foo', dest='foo')
        bar = parser.add_argument('--bar', dest='bar', required=True)
        parser.add_argument('cmd')
        parser.add_argument('rest', nargs='*', type=int)
        argv = 'cmd --foo x 1 --bar y 2 3'.split()
        args = parser.parse_intermixed_args(argv)
        # rest gets [1,2,3] despite the foo and bar strings
        self.assertEqual(NS(bar='y', cmd='cmd', foo='x', rest=[1, 2, 3]), args)

        args, extras = parser.parse_known_args(argv)
        # cannot parse the '1,2,3'
        self.assertEqual(NS(bar='y', cmd='cmd', foo='x', rest=[]), args)
        self.assertEqual(["1", "2", "3"], extras)

        argv = 'cmd --foo x 1 --error 2 --bar y 3'.split()
        args, extras = parser.parse_known_intermixed_args(argv)
        # unknown optionals go into extras
        self.assertEqual(NS(bar='y', cmd='cmd', foo='x', rest=[1]), args)
        self.assertEqual(['--error', '2', '3'], extras)

        # restores attributes that were temporarily changed
        self.assertIsNone(parser.usage)
        self.assertEqual(bar.required, True)

    eleza test_remainder(self):
        # Intermixed and remainder are incompatible
        parser = ErrorRaisingArgumentParser(prog='PROG')
        parser.add_argument('-z')
        parser.add_argument('x')
        parser.add_argument('y', nargs='...')
        argv = 'X A B -z Z'.split()
        # intermixed fails with '...' (also 'A...')
        # self.assertRaises(TypeError, parser.parse_intermixed_args, argv)
        with self.assertRaises(TypeError) as cm:
            parser.parse_intermixed_args(argv)
        self.assertRegex(str(cm.exception), r'\.\.\.')

    eleza test_exclusive(self):
        # mutually exclusive group; intermixed works fine
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--foo', action='store_true', help='FOO')
        group.add_argument('--spam', help='SPAM')
        parser.add_argument('badger', nargs='*', default='X', help='BADGER')
        args = parser.parse_intermixed_args('1 --foo 2'.split())
        self.assertEqual(NS(badger=['1', '2'], foo=True, spam=None), args)
        self.assertRaises(ArgumentParserError, parser.parse_intermixed_args, '1 2'.split())
        self.assertEqual(group.required, True)

    eleza test_exclusive_incompatible(self):
        # mutually exclusive group including positional - fail
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--foo', action='store_true', help='FOO')
        group.add_argument('--spam', help='SPAM')
        group.add_argument('badger', nargs='*', default='X', help='BADGER')
        self.assertRaises(TypeError, parser.parse_intermixed_args, [])
        self.assertEqual(group.required, True)

kundi TestIntermixedMessageContentError(TestCase):
    # case where Intermixed gives different error message
    # error is raised by 1st parsing step
    eleza test_missing_argument_name_in_message(self):
        parser = ErrorRaisingArgumentParser(prog='PROG', usage='')
        parser.add_argument('req_pos', type=str)
        parser.add_argument('-req_opt', type=int, required=True)

        with self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args([])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertRegex(msg, 'req_opt')

        with self.assertRaises(ArgumentParserError) as cm:
            parser.parse_intermixed_args([])
        msg = str(cm.exception)
        self.assertNotRegex(msg, 'req_pos')
        self.assertRegex(msg, 'req_opt')

# ==========================
# add_argument metavar tests
# ==========================

kundi TestAddArgumentMetavar(TestCase):

    EXPECTED_MESSAGE = "length of metavar tuple does not match nargs"

    eleza do_test_no_exception(self, nargs, metavar):
        parser = argparse.ArgumentParser()
        parser.add_argument("--foo", nargs=nargs, metavar=metavar)

    eleza do_test_exception(self, nargs, metavar):
        parser = argparse.ArgumentParser()
        with self.assertRaises(ValueError) as cm:
            parser.add_argument("--foo", nargs=nargs, metavar=metavar)
        self.assertEqual(cm.exception.args[0], self.EXPECTED_MESSAGE)

    # Unit tests for different values of metavar when nargs=None

    eleza test_nargs_None_metavar_string(self):
        self.do_test_no_exception(nargs=None, metavar="1")

    eleza test_nargs_None_metavar_length0(self):
        self.do_test_exception(nargs=None, metavar=tuple())

    eleza test_nargs_None_metavar_length1(self):
        self.do_test_no_exception(nargs=None, metavar=("1",))

    eleza test_nargs_None_metavar_length2(self):
        self.do_test_exception(nargs=None, metavar=("1", "2"))

    eleza test_nargs_None_metavar_length3(self):
        self.do_test_exception(nargs=None, metavar=("1", "2", "3"))

    # Unit tests for different values of metavar when nargs=?

    eleza test_nargs_optional_metavar_string(self):
        self.do_test_no_exception(nargs="?", metavar="1")

    eleza test_nargs_optional_metavar_length0(self):
        self.do_test_exception(nargs="?", metavar=tuple())

    eleza test_nargs_optional_metavar_length1(self):
        self.do_test_no_exception(nargs="?", metavar=("1",))

    eleza test_nargs_optional_metavar_length2(self):
        self.do_test_exception(nargs="?", metavar=("1", "2"))

    eleza test_nargs_optional_metavar_length3(self):
        self.do_test_exception(nargs="?", metavar=("1", "2", "3"))

    # Unit tests for different values of metavar when nargs=*

    eleza test_nargs_zeroormore_metavar_string(self):
        self.do_test_no_exception(nargs="*", metavar="1")

    eleza test_nargs_zeroormore_metavar_length0(self):
        self.do_test_exception(nargs="*", metavar=tuple())

    eleza test_nargs_zeroormore_metavar_length1(self):
        self.do_test_exception(nargs="*", metavar=("1",))

    eleza test_nargs_zeroormore_metavar_length2(self):
        self.do_test_no_exception(nargs="*", metavar=("1", "2"))

    eleza test_nargs_zeroormore_metavar_length3(self):
        self.do_test_exception(nargs="*", metavar=("1", "2", "3"))

    # Unit tests for different values of metavar when nargs=+

    eleza test_nargs_oneormore_metavar_string(self):
        self.do_test_no_exception(nargs="+", metavar="1")

    eleza test_nargs_oneormore_metavar_length0(self):
        self.do_test_exception(nargs="+", metavar=tuple())

    eleza test_nargs_oneormore_metavar_length1(self):
        self.do_test_exception(nargs="+", metavar=("1",))

    eleza test_nargs_oneormore_metavar_length2(self):
        self.do_test_no_exception(nargs="+", metavar=("1", "2"))

    eleza test_nargs_oneormore_metavar_length3(self):
        self.do_test_exception(nargs="+", metavar=("1", "2", "3"))

    # Unit tests for different values of metavar when nargs=...

    eleza test_nargs_remainder_metavar_string(self):
        self.do_test_no_exception(nargs="...", metavar="1")

    eleza test_nargs_remainder_metavar_length0(self):
        self.do_test_no_exception(nargs="...", metavar=tuple())

    eleza test_nargs_remainder_metavar_length1(self):
        self.do_test_no_exception(nargs="...", metavar=("1",))

    eleza test_nargs_remainder_metavar_length2(self):
        self.do_test_no_exception(nargs="...", metavar=("1", "2"))

    eleza test_nargs_remainder_metavar_length3(self):
        self.do_test_no_exception(nargs="...", metavar=("1", "2", "3"))

    # Unit tests for different values of metavar when nargs=A...

    eleza test_nargs_parser_metavar_string(self):
        self.do_test_no_exception(nargs="A...", metavar="1")

    eleza test_nargs_parser_metavar_length0(self):
        self.do_test_exception(nargs="A...", metavar=tuple())

    eleza test_nargs_parser_metavar_length1(self):
        self.do_test_no_exception(nargs="A...", metavar=("1",))

    eleza test_nargs_parser_metavar_length2(self):
        self.do_test_exception(nargs="A...", metavar=("1", "2"))

    eleza test_nargs_parser_metavar_length3(self):
        self.do_test_exception(nargs="A...", metavar=("1", "2", "3"))

    # Unit tests for different values of metavar when nargs=1

    eleza test_nargs_1_metavar_string(self):
        self.do_test_no_exception(nargs=1, metavar="1")

    eleza test_nargs_1_metavar_length0(self):
        self.do_test_exception(nargs=1, metavar=tuple())

    eleza test_nargs_1_metavar_length1(self):
        self.do_test_no_exception(nargs=1, metavar=("1",))

    eleza test_nargs_1_metavar_length2(self):
        self.do_test_exception(nargs=1, metavar=("1", "2"))

    eleza test_nargs_1_metavar_length3(self):
        self.do_test_exception(nargs=1, metavar=("1", "2", "3"))

    # Unit tests for different values of metavar when nargs=2

    eleza test_nargs_2_metavar_string(self):
        self.do_test_no_exception(nargs=2, metavar="1")

    eleza test_nargs_2_metavar_length0(self):
        self.do_test_exception(nargs=2, metavar=tuple())

    eleza test_nargs_2_metavar_length1(self):
        self.do_test_exception(nargs=2, metavar=("1",))

    eleza test_nargs_2_metavar_length2(self):
        self.do_test_no_exception(nargs=2, metavar=("1", "2"))

    eleza test_nargs_2_metavar_length3(self):
        self.do_test_exception(nargs=2, metavar=("1", "2", "3"))

    # Unit tests for different values of metavar when nargs=3

    eleza test_nargs_3_metavar_string(self):
        self.do_test_no_exception(nargs=3, metavar="1")

    eleza test_nargs_3_metavar_length0(self):
        self.do_test_exception(nargs=3, metavar=tuple())

    eleza test_nargs_3_metavar_length1(self):
        self.do_test_exception(nargs=3, metavar=("1",))

    eleza test_nargs_3_metavar_length2(self):
        self.do_test_exception(nargs=3, metavar=("1", "2"))

    eleza test_nargs_3_metavar_length3(self):
        self.do_test_no_exception(nargs=3, metavar=("1", "2", "3"))


kundi TestInvalidNargs(TestCase):

    EXPECTED_INVALID_MESSAGE = "invalid nargs value"
    EXPECTED_RANGE_MESSAGE = ("nargs for store actions must be != 0; ikiwa you "
                              "have nothing to store, actions such as store "
                              "true or store const may be more appropriate")

    eleza do_test_range_exception(self, nargs):
        parser = argparse.ArgumentParser()
        with self.assertRaises(ValueError) as cm:
            parser.add_argument("--foo", nargs=nargs)
        self.assertEqual(cm.exception.args[0], self.EXPECTED_RANGE_MESSAGE)

    eleza do_test_invalid_exception(self, nargs):
        parser = argparse.ArgumentParser()
        with self.assertRaises(ValueError) as cm:
            parser.add_argument("--foo", nargs=nargs)
        self.assertEqual(cm.exception.args[0], self.EXPECTED_INVALID_MESSAGE)

    # Unit tests for different values of nargs

    eleza test_nargs_alphabetic(self):
        self.do_test_invalid_exception(nargs='a')
        self.do_test_invalid_exception(nargs="abcd")

    eleza test_nargs_zero(self):
        self.do_test_range_exception(nargs=0)

# ============================
# kutoka argparse agiza * tests
# ============================

kundi TestImportStar(TestCase):

    eleza test(self):
        for name in argparse.__all__:
            self.assertTrue(hasattr(argparse, name))

    eleza test_all_exports_everything_but_modules(self):
        items = [
            name
            for name, value in vars(argparse).items()
            ikiwa not (name.startswith("_") or name == 'ngettext')
            ikiwa not inspect.ismodule(value)
        ]
        self.assertEqual(sorted(items), sorted(argparse.__all__))


kundi TestWrappingMetavar(TestCase):

    eleza setUp(self):
        super().setUp()
        self.parser = ErrorRaisingArgumentParser(
            'this_is_spammy_prog_with_a_long_name_sorry_about_the_name'
        )
        # this metavar was triggering library assertion errors due to usage
        # message formatting incorrectly splitting on the ] chars within
        metavar = '<http[s]://example:1234>'
        self.parser.add_argument('--proxy', metavar=metavar)

    eleza test_help_with_metavar(self):
        help_text = self.parser.format_help()
        self.assertEqual(help_text, textwrap.dedent('''\
            usage: this_is_spammy_prog_with_a_long_name_sorry_about_the_name
                   [-h] [--proxy <http[s]://example:1234>]

            optional arguments:
              -h, --help            show this help message and exit
              --proxy <http[s]://example:1234>
            '''))


eleza test_main():
    support.run_unittest(__name__)
    # Remove global references to avoid looking like we have refleaks.
    RFile.seen = {}
    WFile.seen = set()



ikiwa __name__ == '__main__':
    test_main()
