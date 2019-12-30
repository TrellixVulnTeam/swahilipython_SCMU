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
        # variable.  To ensure that this width ni used, set COLUMNS to 80.
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
        kila root, dirs, files kwenye os.walk(self.temp_dir, topdown=Uongo):
            kila name kwenye files:
                os.chmod(os.path.join(self.temp_dir, name), stat.S_IWRITE)
        shutil.rmtree(self.temp_dir, Kweli)

    eleza create_readonly_file(self, filename):
        file_path = os.path.join(self.temp_dir, filename)
        ukijumuisha open(file_path, 'w') as file:
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
        kwarg_str = ', '.join(['%s=%r' % tup kila tup kwenye sorted_items])
        rudisha '%s(%s)' % (type(self).__name__, kwarg_str)

    eleza __eq__(self, other):
        rudisha vars(self) == vars(other)


kundi ArgumentParserError(Exception):

    eleza __init__(self, message, stdout=Tupu, stderr=Tupu, error_code=Tupu):
        Exception.__init__(self, message, stdout, stderr)
        self.message = message
        self.stdout = stdout
        self.stderr = stderr
        self.error_code = error_code


eleza stderr_to_parser_error(parse_args, *args, **kwargs):
    # ikiwa this ni being called recursively na stderr ama stdout ni already being
    # redirected, simply call the function na let the enclosing function
    # catch the exception
    ikiwa isinstance(sys.stderr, StdIOBuffer) ama isinstance(sys.stdout, StdIOBuffer):
        rudisha parse_args(*args, **kwargs)

    # ikiwa this ni sio being called recursively, redirect stderr and
    # use it as the ArgumentParserError message
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StdIOBuffer()
    sys.stderr = StdIOBuffer()
    jaribu:
        jaribu:
            result = parse_args(*args, **kwargs)
            kila key kwenye list(vars(result)):
                ikiwa getattr(result, key) ni sys.stdout:
                    setattr(result, key, old_stdout)
                ikiwa getattr(result, key) ni sys.stderr:
                    setattr(result, key, old_stderr)
            rudisha result
        except SystemExit:
            code = sys.exc_info()[1].code
            stdout = sys.stdout.getvalue()
            stderr = sys.stderr.getvalue()
             ashiria ArgumentParserError("SystemExit", stdout, stderr, code)
    mwishowe:
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
        options ni a dict that should match the vars() of the options
        parsed out of initial_args, na remaining_args should be any
        remaining unparsed arguments
    """

    eleza __init__(cls, name, bases, bodydict):
        ikiwa name == 'ParserTestCase':
            return

        # default parser signature ni empty
        ikiwa sio hasattr(cls, 'parser_signature'):
            cls.parser_signature = Sig()
        ikiwa sio hasattr(cls, 'parser_class'):
            cls.parser_kundi = ErrorRaisingArgumentParser

        # ---------------------------------------
        # functions kila adding optional arguments
        # ---------------------------------------
        eleza no_groups(parser, argument_signatures):
            """Add all arguments directly to the parser"""
            kila sig kwenye argument_signatures:
                parser.add_argument(*sig.args, **sig.kwargs)

        eleza one_group(parser, argument_signatures):
            """Add all arguments under a single group kwenye the parser"""
            group = parser.add_argument_group('foo')
            kila sig kwenye argument_signatures:
                group.add_argument(*sig.args, **sig.kwargs)

        eleza many_groups(parser, argument_signatures):
            """Add each argument kwenye its own group to the parser"""
            kila i, sig kwenye enumerate(argument_signatures):
                group = parser.add_argument_group('foo:%i' % i)
                group.add_argument(*sig.args, **sig.kwargs)

        # --------------------------
        # functions kila parsing args
        # --------------------------
        eleza listargs(parser, args):
            """Parse the args by passing kwenye a list"""
            rudisha parser.parse_args(args)

        eleza sysargs(parser, args):
            """Parse the args by defaulting to sys.argv"""
            old_sys_argv = sys.argv
            sys.argv = [old_sys_argv[0]] + args
            jaribu:
                rudisha parser.parse_args()
            mwishowe:
                sys.argv = old_sys_argv

        # kundi that holds the combination of one optional argument
        # addition method na one arg parsing method
        kundi AddTests(object):

            eleza __init__(self, tester_cls, add_arguments, parse_args):
                self._add_arguments = add_arguments
                self._parse_args = parse_args

                add_arguments_name = self._add_arguments.__name__
                parse_args_name = self._parse_args.__name__
                kila test_func kwenye [self.test_failures, self.test_successes]:
                    func_name = test_func.__name__
                    names = func_name, add_arguments_name, parse_args_name
                    test_name = '_'.join(names)

                    eleza wrapper(self, test_func=test_func):
                        test_func(self)
                    jaribu:
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
                kila args_str kwenye tester.failures:
                    args = args_str.split()
                    ukijumuisha tester.assertRaises(ArgumentParserError, msg=args):
                        parser.parse_args(args)

            eleza test_successes(self, tester):
                parser = self._get_parser(tester)
                kila args, expected_ns kwenye tester.successes:
                    ikiwa isinstance(args, str):
                        args = args.split()
                    result_ns = self._parse_args(parser, args)
                    tester.assertEqual(expected_ns, result_ns)

        # add tests kila each combination of an optionals adding method
        # na an arg parsing method
        kila add_arguments kwenye [no_groups, one_group, many_groups]:
            kila parse_args kwenye [listargs, sysargs]:
                AddTests(cls, add_arguments, parse_args)

bases = TestCase,
ParserTestCase = ParserTesterMetaclass('ParserTestCase', bases, {})

# ===============
# Optionals tests
# ===============

kundi TestOptionalsSingleDash(ParserTestCase):
    """Test an Optional ukijumuisha a single-dash option string"""

    argument_signatures = [Sig('-x')]
    failures = ['-x', 'a', '--foo', '-x --foo', '-x -y']
    successes = [
        ('', NS(x=Tupu)),
        ('-x a', NS(x='a')),
        ('-xa', NS(x='a')),
        ('-x -1', NS(x='-1')),
        ('-x-1', NS(x='-1')),
    ]


kundi TestOptionalsSingleDashCombined(ParserTestCase):
    """Test an Optional ukijumuisha a single-dash option string"""

    argument_signatures = [
        Sig('-x', action='store_true'),
        Sig('-yyy', action='store_const', const=42),
        Sig('-z'),
    ]
    failures = ['a', '--foo', '-xa', '-x --foo', '-x -z', '-z -x',
                '-yx', '-yz a', '-yyyx', '-yyyza', '-xyza']
    successes = [
        ('', NS(x=Uongo, yyy=Tupu, z=Tupu)),
        ('-x', NS(x=Kweli, yyy=Tupu, z=Tupu)),
        ('-za', NS(x=Uongo, yyy=Tupu, z='a')),
        ('-z a', NS(x=Uongo, yyy=Tupu, z='a')),
        ('-xza', NS(x=Kweli, yyy=Tupu, z='a')),
        ('-xz a', NS(x=Kweli, yyy=Tupu, z='a')),
        ('-x -za', NS(x=Kweli, yyy=Tupu, z='a')),
        ('-x -z a', NS(x=Kweli, yyy=Tupu, z='a')),
        ('-y', NS(x=Uongo, yyy=42, z=Tupu)),
        ('-yyy', NS(x=Uongo, yyy=42, z=Tupu)),
        ('-x -yyy -za', NS(x=Kweli, yyy=42, z='a')),
        ('-x -yyy -z a', NS(x=Kweli, yyy=42, z='a')),
    ]


kundi TestOptionalsSingleDashLong(ParserTestCase):
    """Test an Optional ukijumuisha a multi-character single-dash option string"""

    argument_signatures = [Sig('-foo')]
    failures = ['-foo', 'a', '--foo', '-foo --foo', '-foo -y', '-fooa']
    successes = [
        ('', NS(foo=Tupu)),
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
        ('', NS(f=Tupu, foobar=Tupu, foorab=Tupu)),
        ('-f a', NS(f='a', foobar=Tupu, foorab=Tupu)),
        ('-fa', NS(f='a', foobar=Tupu, foorab=Tupu)),
        ('-foa', NS(f='oa', foobar=Tupu, foorab=Tupu)),
        ('-fooa', NS(f='ooa', foobar=Tupu, foorab=Tupu)),
        ('-foobar a', NS(f=Tupu, foobar='a', foorab=Tupu)),
        ('-foorab a', NS(f=Tupu, foobar=Tupu, foorab='a')),
    ]


kundi TestOptionalsSingleDashAmbiguous(ParserTestCase):
    """Test Optionals that partially match but are sio subsets"""

    argument_signatures = [Sig('-foobar'), Sig('-foorab')]
    failures = ['-f', '-f a', '-fa', '-foa', '-foo', '-fo', '-foo b']
    successes = [
        ('', NS(foobar=Tupu, foorab=Tupu)),
        ('-foob a', NS(foobar='a', foorab=Tupu)),
        ('-foor a', NS(foobar=Tupu, foorab='a')),
        ('-fooba a', NS(foobar='a', foorab=Tupu)),
        ('-foora a', NS(foobar=Tupu, foorab='a')),
        ('-foobar a', NS(foobar='a', foorab=Tupu)),
        ('-foorab a', NS(foobar=Tupu, foorab='a')),
    ]


kundi TestOptionalsNumeric(ParserTestCase):
    """Test an Optional ukijumuisha a short opt string"""

    argument_signatures = [Sig('-1', dest='one')]
    failures = ['-1', 'a', '-1 --foo', '-1 -y', '-1 -1', '-1 -2']
    successes = [
        ('', NS(one=Tupu)),
        ('-1 a', NS(one='a')),
        ('-1a', NS(one='a')),
        ('-1-2', NS(one='-2')),
    ]


kundi TestOptionalsDoubleDash(ParserTestCase):
    """Test an Optional ukijumuisha a double-dash option string"""

    argument_signatures = [Sig('--foo')]
    failures = ['--foo', '-f', '-f a', 'a', '--foo -x', '--foo --bar']
    successes = [
        ('', NS(foo=Tupu)),
        ('--foo a', NS(foo='a')),
        ('--foo=a', NS(foo='a')),
        ('--foo -2.5', NS(foo='-2.5')),
        ('--foo=-2.5', NS(foo='-2.5')),
    ]


kundi TestOptionalsDoubleDashPartialMatch(ParserTestCase):
    """Tests partial matching ukijumuisha a double-dash option string"""

    argument_signatures = [
        Sig('--badger', action='store_true'),
        Sig('--bat'),
    ]
    failures = ['--bar', '--b', '--ba', '--b=2', '--ba=4', '--badge 5']
    successes = [
        ('', NS(badger=Uongo, bat=Tupu)),
        ('--bat X', NS(badger=Uongo, bat='X')),
        ('--bad', NS(badger=Kweli, bat=Tupu)),
        ('--badg', NS(badger=Kweli, bat=Tupu)),
        ('--badge', NS(badger=Kweli, bat=Tupu)),
        ('--badger', NS(badger=Kweli, bat=Tupu)),
    ]


kundi TestOptionalsDoubleDashPrefixMatch(ParserTestCase):
    """Tests when one double-dash option string ni a prefix of another"""

    argument_signatures = [
        Sig('--badger', action='store_true'),
        Sig('--ba'),
    ]
    failures = ['--bar', '--b', '--ba', '--b=2', '--badge 5']
    successes = [
        ('', NS(badger=Uongo, ba=Tupu)),
        ('--ba X', NS(badger=Uongo, ba='X')),
        ('--ba=X', NS(badger=Uongo, ba='X')),
        ('--bad', NS(badger=Kweli, ba=Tupu)),
        ('--badg', NS(badger=Kweli, ba=Tupu)),
        ('--badge', NS(badger=Kweli, ba=Tupu)),
        ('--badger', NS(badger=Kweli, ba=Tupu)),
    ]


kundi TestOptionalsSingleDoubleDash(ParserTestCase):
    """Test an Optional ukijumuisha single- na double-dash option strings"""

    argument_signatures = [
        Sig('-f', action='store_true'),
        Sig('--bar'),
        Sig('-baz', action='store_const', const=42),
    ]
    failures = ['--bar', '-fbar', '-fbaz', '-bazf', '-b B', 'B']
    successes = [
        ('', NS(f=Uongo, bar=Tupu, baz=Tupu)),
        ('-f', NS(f=Kweli, bar=Tupu, baz=Tupu)),
        ('--ba B', NS(f=Uongo, bar='B', baz=Tupu)),
        ('-f --bar B', NS(f=Kweli, bar='B', baz=Tupu)),
        ('-f -b', NS(f=Kweli, bar=Tupu, baz=42)),
        ('-ba -f', NS(f=Kweli, bar=Tupu, baz=42)),
    ]


kundi TestOptionalsAlternatePrefixChars(ParserTestCase):
    """Test an Optional ukijumuisha option strings ukijumuisha custom prefixes"""

    parser_signature = Sig(prefix_chars='+:/', add_help=Uongo)
    argument_signatures = [
        Sig('+f', action='store_true'),
        Sig('::bar'),
        Sig('/baz', action='store_const', const=42),
    ]
    failures = ['--bar', '-fbar', '-b B', 'B', '-f', '--bar B', '-baz', '-h', '--help', '+h', '::help', '/help']
    successes = [
        ('', NS(f=Uongo, bar=Tupu, baz=Tupu)),
        ('+f', NS(f=Kweli, bar=Tupu, baz=Tupu)),
        ('::ba B', NS(f=Uongo, bar='B', baz=Tupu)),
        ('+f ::bar B', NS(f=Kweli, bar='B', baz=Tupu)),
        ('+f /b', NS(f=Kweli, bar=Tupu, baz=42)),
        ('/ba +f', NS(f=Kweli, bar=Tupu, baz=42)),
    ]


kundi TestOptionalsAlternatePrefixCharsAddedHelp(ParserTestCase):
    """When ``-`` sio kwenye prefix_chars, default operators created kila help
       should use the prefix_chars kwenye use rather than - ama --
       http://bugs.python.org/issue9444"""

    parser_signature = Sig(prefix_chars='+:/', add_help=Kweli)
    argument_signatures = [
        Sig('+f', action='store_true'),
        Sig('::bar'),
        Sig('/baz', action='store_const', const=42),
    ]
    failures = ['--bar', '-fbar', '-b B', 'B', '-f', '--bar B', '-baz']
    successes = [
        ('', NS(f=Uongo, bar=Tupu, baz=Tupu)),
        ('+f', NS(f=Kweli, bar=Tupu, baz=Tupu)),
        ('::ba B', NS(f=Uongo, bar='B', baz=Tupu)),
        ('+f ::bar B', NS(f=Kweli, bar='B', baz=Tupu)),
        ('+f /b', NS(f=Kweli, bar=Tupu, baz=42)),
        ('/ba +f', NS(f=Kweli, bar=Tupu, baz=42))
    ]


kundi TestOptionalsAlternatePrefixCharsMultipleShortArgs(ParserTestCase):
    """Verify that Optionals must be called ukijumuisha their defined prefixes"""

    parser_signature = Sig(prefix_chars='+-', add_help=Uongo)
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
        ('', NS(x=Uongo, y=Uongo, z=Uongo)),
        ('-x', NS(x=Kweli, y=Uongo, z=Uongo)),
        ('+y -x', NS(x=Kweli, y=Kweli, z=Uongo)),
        ('+yz -x', NS(x=Kweli, y=Kweli, z=Kweli)),
    ]


kundi TestOptionalsShortLong(ParserTestCase):
    """Test a combination of single- na double-dash option strings"""

    argument_signatures = [
        Sig('-v', '--verbose', '-n', '--noisy', action='store_true'),
    ]
    failures = ['--x --verbose', '-N', 'a', '-v x']
    successes = [
        ('', NS(verbose=Uongo)),
        ('-v', NS(verbose=Kweli)),
        ('--verbose', NS(verbose=Kweli)),
        ('-n', NS(verbose=Kweli)),
        ('--noisy', NS(verbose=Kweli)),
    ]


kundi TestOptionalsDest(ParserTestCase):
    """Tests various means of setting destination"""

    argument_signatures = [Sig('--foo-bar'), Sig('--baz', dest='zabbaz')]
    failures = ['a']
    successes = [
        ('--foo-bar f', NS(foo_bar='f', zabbaz=Tupu)),
        ('--baz g', NS(foo_bar=Tupu, zabbaz='g')),
        ('--foo-bar h --baz i', NS(foo_bar='h', zabbaz='i')),
        ('--baz j --foo-bar k', NS(foo_bar='k', zabbaz='j')),
    ]


kundi TestOptionalsDefault(ParserTestCase):
    """Tests specifying a default kila an Optional"""

    argument_signatures = [Sig('-x'), Sig('-y', default=42)]
    failures = ['a']
    successes = [
        ('', NS(x=Tupu, y=42)),
        ('-xx', NS(x='x', y=42)),
        ('-yy', NS(x=Tupu, y='y')),
    ]


kundi TestOptionalsNargsDefault(ParserTestCase):
    """Tests sio specifying the number of args kila an Optional"""

    argument_signatures = [Sig('-x')]
    failures = ['a', '-x']
    successes = [
        ('', NS(x=Tupu)),
        ('-x a', NS(x='a')),
    ]


kundi TestOptionalsNargs1(ParserTestCase):
    """Tests specifying 1 arg kila an Optional"""

    argument_signatures = [Sig('-x', nargs=1)]
    failures = ['a', '-x']
    successes = [
        ('', NS(x=Tupu)),
        ('-x a', NS(x=['a'])),
    ]


kundi TestOptionalsNargs3(ParserTestCase):
    """Tests specifying 3 args kila an Optional"""

    argument_signatures = [Sig('-x', nargs=3)]
    failures = ['a', '-x', '-x a', '-x a b', 'a -x', 'a -x b']
    successes = [
        ('', NS(x=Tupu)),
        ('-x a b c', NS(x=['a', 'b', 'c'])),
    ]


kundi TestOptionalsNargsOptional(ParserTestCase):
    """Tests specifying an Optional arg kila an Optional"""

    argument_signatures = [
        Sig('-w', nargs='?'),
        Sig('-x', nargs='?', const=42),
        Sig('-y', nargs='?', default='spam'),
        Sig('-z', nargs='?', type=int, const='42', default='84'),
    ]
    failures = ['2']
    successes = [
        ('', NS(w=Tupu, x=Tupu, y='spam', z=84)),
        ('-w', NS(w=Tupu, x=Tupu, y='spam', z=84)),
        ('-w 2', NS(w='2', x=Tupu, y='spam', z=84)),
        ('-x', NS(w=Tupu, x=42, y='spam', z=84)),
        ('-x 2', NS(w=Tupu, x='2', y='spam', z=84)),
        ('-y', NS(w=Tupu, x=Tupu, y=Tupu, z=84)),
        ('-y 2', NS(w=Tupu, x=Tupu, y='2', z=84)),
        ('-z', NS(w=Tupu, x=Tupu, y='spam', z=42)),
        ('-z 2', NS(w=Tupu, x=Tupu, y='spam', z=2)),
    ]


kundi TestOptionalsNargsZeroOrMore(ParserTestCase):
    """Tests specifying args kila an Optional that accepts zero ama more"""

    argument_signatures = [
        Sig('-x', nargs='*'),
        Sig('-y', nargs='*', default='spam'),
    ]
    failures = ['a']
    successes = [
        ('', NS(x=Tupu, y='spam')),
        ('-x', NS(x=[], y='spam')),
        ('-x a', NS(x=['a'], y='spam')),
        ('-x a b', NS(x=['a', 'b'], y='spam')),
        ('-y', NS(x=Tupu, y=[])),
        ('-y a', NS(x=Tupu, y=['a'])),
        ('-y a b', NS(x=Tupu, y=['a', 'b'])),
    ]


kundi TestOptionalsNargsOneOrMore(ParserTestCase):
    """Tests specifying args kila an Optional that accepts one ama more"""

    argument_signatures = [
        Sig('-x', nargs='+'),
        Sig('-y', nargs='+', default='spam'),
    ]
    failures = ['a', '-x', '-y', 'a -x', 'a -y b']
    successes = [
        ('', NS(x=Tupu, y='spam')),
        ('-x a', NS(x=['a'], y='spam')),
        ('-x a b', NS(x=['a', 'b'], y='spam')),
        ('-y a', NS(x=Tupu, y=['a'])),
        ('-y a b', NS(x=Tupu, y=['a', 'b'])),
    ]


kundi TestOptionalsChoices(ParserTestCase):
    """Tests specifying the choices kila an Optional"""

    argument_signatures = [
        Sig('-f', choices='abc'),
        Sig('-g', type=int, choices=range(5))]
    failures = ['a', '-f d', '-fad', '-ga', '-g 6']
    successes = [
        ('', NS(f=Tupu, g=Tupu)),
        ('-f a', NS(f='a', g=Tupu)),
        ('-f c', NS(f='c', g=Tupu)),
        ('-g 0', NS(f=Tupu, g=0)),
        ('-g 03', NS(f=Tupu, g=3)),
        ('-fb -g4', NS(f='b', g=4)),
    ]


kundi TestOptionalsRequired(ParserTestCase):
    """Tests an optional action that ni required"""

    argument_signatures = [
        Sig('-x', type=int, required=Kweli),
    ]
    failures = ['a', '']
    successes = [
        ('-x 1', NS(x=1)),
        ('-x42', NS(x=42)),
    ]


kundi TestOptionalsActionStore(ParserTestCase):
    """Tests the store action kila an Optional"""

    argument_signatures = [Sig('-x', action='store')]
    failures = ['a', 'a -x']
    successes = [
        ('', NS(x=Tupu)),
        ('-xfoo', NS(x='foo')),
    ]


kundi TestOptionalsActionStoreConst(ParserTestCase):
    """Tests the store_const action kila an Optional"""

    argument_signatures = [Sig('-y', action='store_const', const=object)]
    failures = ['a']
    successes = [
        ('', NS(y=Tupu)),
        ('-y', NS(y=object)),
    ]


kundi TestOptionalsActionStoreUongo(ParserTestCase):
    """Tests the store_false action kila an Optional"""

    argument_signatures = [Sig('-z', action='store_false')]
    failures = ['a', '-za', '-z a']
    successes = [
        ('', NS(z=Kweli)),
        ('-z', NS(z=Uongo)),
    ]


kundi TestOptionalsActionStoreKweli(ParserTestCase):
    """Tests the store_true action kila an Optional"""

    argument_signatures = [Sig('--apple', action='store_true')]
    failures = ['a', '--apple=b', '--apple b']
    successes = [
        ('', NS(apple=Uongo)),
        ('--apple', NS(apple=Kweli)),
    ]


kundi TestOptionalsActionAppend(ParserTestCase):
    """Tests the append action kila an Optional"""

    argument_signatures = [Sig('--baz', action='append')]
    failures = ['a', '--baz', 'a --baz', '--baz a b']
    successes = [
        ('', NS(baz=Tupu)),
        ('--baz a', NS(baz=['a'])),
        ('--baz a --baz b', NS(baz=['a', 'b'])),
    ]


kundi TestOptionalsActionAppendWithDefault(ParserTestCase):
    """Tests the append action kila an Optional"""

    argument_signatures = [Sig('--baz', action='append', default=['X'])]
    failures = ['a', '--baz', 'a --baz', '--baz a b']
    successes = [
        ('', NS(baz=['X'])),
        ('--baz a', NS(baz=['X', 'a'])),
        ('--baz a --baz b', NS(baz=['X', 'a', 'b'])),
    ]


kundi TestOptionalsActionAppendConst(ParserTestCase):
    """Tests the append_const action kila an Optional"""

    argument_signatures = [
        Sig('-b', action='append_const', const=Exception),
        Sig('-c', action='append', dest='b'),
    ]
    failures = ['a', '-c', 'a -c', '-bx', '-b x']
    successes = [
        ('', NS(b=Tupu)),
        ('-b', NS(b=[Exception])),
        ('-b -cx -b -cyz', NS(b=[Exception, 'x', Exception, 'yz'])),
    ]


kundi TestOptionalsActionAppendConstWithDefault(ParserTestCase):
    """Tests the append_const action kila an Optional"""

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
    """Tests the count action kila an Optional"""

    argument_signatures = [Sig('-x', action='count')]
    failures = ['a', '-x a', '-x b', '-x a -x b']
    successes = [
        ('', NS(x=Tupu)),
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
        ('', NS(foo=Tupu, foobaz=Tupu, fooble=Uongo)),
        ('--foo 7', NS(foo='7', foobaz=Tupu, fooble=Uongo)),
        ('--fooba a', NS(foo=Tupu, foobaz='a', fooble=Uongo)),
        ('--foobl --foo g', NS(foo='g', foobaz=Tupu, fooble=Kweli)),
    ]


kundi TestOptionalsDisallowLongAbbreviation(ParserTestCase):
    """Do sio allow abbreviations of long options at all"""

    parser_signature = Sig(allow_abbrev=Uongo)
    argument_signatures = [
        Sig('--foo'),
        Sig('--foodle', action='store_true'),
        Sig('--foonly'),
    ]
    failures = ['-foon 3', '--foon 3', '--food', '--food --foo 2']
    successes = [
        ('', NS(foo=Tupu, foodle=Uongo, foonly=Tupu)),
        ('--foo 3', NS(foo='3', foodle=Uongo, foonly=Tupu)),
        ('--foonly 7 --foodle --foo 2', NS(foo='2', foodle=Kweli, foonly='7')),
    ]


kundi TestDisallowLongAbbreviationAllowsShortGrouping(ParserTestCase):
    """Do sio allow abbreviations of long options at all"""

    parser_signature = Sig(allow_abbrev=Uongo)
    argument_signatures = [
        Sig('-r'),
        Sig('-c', action='count'),
    ]
    failures = ['-r', '-c -r']
    successes = [
        ('', NS(r=Tupu, c=Tupu)),
        ('-ra', NS(r='a', c=Tupu)),
        ('-rcc', NS(r='cc', c=Tupu)),
        ('-cc', NS(r=Tupu, c=2)),
        ('-cc -ra', NS(r='a', c=2)),
        ('-ccrcc', NS(r='cc', c=2)),
    ]

# ================
# Positional tests
# ================

kundi TestPositionalsNargsTupu(ParserTestCase):
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
    """Test a Positional that specifies unlimited nargs na a default"""

    argument_signatures = [Sig('foo', nargs='*', default='bar')]
    failures = ['-x']
    successes = [
        ('', NS(foo='bar')),
        ('a', NS(foo=['a'])),
        ('a b', NS(foo=['a', 'b'])),
    ]


kundi TestPositionalsNargsOneOrMore(ParserTestCase):
    """Test a Positional that specifies one ama more nargs"""

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
        ('', NS(foo=Tupu)),
        ('a', NS(foo='a')),
    ]


kundi TestPositionalsNargsOptionalDefault(ParserTestCase):
    """Tests an Optional Positional ukijumuisha a default value"""

    argument_signatures = [Sig('foo', nargs='?', default=42)]
    failures = ['-x', 'a b']
    successes = [
        ('', NS(foo=42)),
        ('a', NS(foo='a')),
    ]


kundi TestPositionalsNargsOptionalConvertedDefault(ParserTestCase):
    """Tests an Optional Positional ukijumuisha a default value
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


kundi TestPositionalsNargsTupuTupu(ParserTestCase):
    """Test two Positionals that don't specify nargs"""

    argument_signatures = [Sig('foo'), Sig('bar')]
    failures = ['', '-x', 'a', 'a b c']
    successes = [
        ('a b', NS(foo='a', bar='b')),
    ]


kundi TestPositionalsNargsTupu1(ParserTestCase):
    """Test a Positional ukijumuisha no nargs followed by one ukijumuisha 1"""

    argument_signatures = [Sig('foo'), Sig('bar', nargs=1)]
    failures = ['', '--foo', 'a', 'a b c']
    successes = [
        ('a b', NS(foo='a', bar=['b'])),
    ]


kundi TestPositionalsNargs2Tupu(ParserTestCase):
    """Test a Positional ukijumuisha 2 nargs followed by one ukijumuisha none"""

    argument_signatures = [Sig('foo', nargs=2), Sig('bar')]
    failures = ['', '--foo', 'a', 'a b', 'a b c d']
    successes = [
        ('a b c', NS(foo=['a', 'b'], bar='c')),
    ]


kundi TestPositionalsNargsTupuZeroOrMore(ParserTestCase):
    """Test a Positional ukijumuisha no nargs followed by one ukijumuisha unlimited"""

    argument_signatures = [Sig('foo'), Sig('bar', nargs='*')]
    failures = ['', '--foo']
    successes = [
        ('a', NS(foo='a', bar=[])),
        ('a b', NS(foo='a', bar=['b'])),
        ('a b c', NS(foo='a', bar=['b', 'c'])),
    ]


kundi TestPositionalsNargsTupuOneOrMore(ParserTestCase):
    """Test a Positional ukijumuisha no nargs followed by one ukijumuisha one ama more"""

    argument_signatures = [Sig('foo'), Sig('bar', nargs='+')]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo='a', bar=['b'])),
        ('a b c', NS(foo='a', bar=['b', 'c'])),
    ]


kundi TestPositionalsNargsTupuOptional(ParserTestCase):
    """Test a Positional ukijumuisha no nargs followed by one ukijumuisha an Optional"""

    argument_signatures = [Sig('foo'), Sig('bar', nargs='?')]
    failures = ['', '--foo', 'a b c']
    successes = [
        ('a', NS(foo='a', bar=Tupu)),
        ('a b', NS(foo='a', bar='b')),
    ]


kundi TestPositionalsNargsZeroOrMoreTupu(ParserTestCase):
    """Test a Positional ukijumuisha unlimited nargs followed by one ukijumuisha none"""

    argument_signatures = [Sig('foo', nargs='*'), Sig('bar')]
    failures = ['', '--foo']
    successes = [
        ('a', NS(foo=[], bar='a')),
        ('a b', NS(foo=['a'], bar='b')),
        ('a b c', NS(foo=['a', 'b'], bar='c')),
    ]


kundi TestPositionalsNargsOneOrMoreTupu(ParserTestCase):
    """Test a Positional ukijumuisha one ama more nargs followed by one ukijumuisha none"""

    argument_signatures = [Sig('foo', nargs='+'), Sig('bar')]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo=['a'], bar='b')),
        ('a b c', NS(foo=['a', 'b'], bar='c')),
    ]


kundi TestPositionalsNargsOptionalTupu(ParserTestCase):
    """Test a Positional ukijumuisha an Optional nargs followed by one ukijumuisha none"""

    argument_signatures = [Sig('foo', nargs='?', default=42), Sig('bar')]
    failures = ['', '--foo', 'a b c']
    successes = [
        ('a', NS(foo=42, bar='a')),
        ('a b', NS(foo='a', bar='b')),
    ]


kundi TestPositionalsNargs2ZeroOrMore(ParserTestCase):
    """Test a Positional ukijumuisha 2 nargs followed by one ukijumuisha unlimited"""

    argument_signatures = [Sig('foo', nargs=2), Sig('bar', nargs='*')]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo=['a', 'b'], bar=[])),
        ('a b c', NS(foo=['a', 'b'], bar=['c'])),
    ]


kundi TestPositionalsNargs2OneOrMore(ParserTestCase):
    """Test a Positional ukijumuisha 2 nargs followed by one ukijumuisha one ama more"""

    argument_signatures = [Sig('foo', nargs=2), Sig('bar', nargs='+')]
    failures = ['', '--foo', 'a', 'a b']
    successes = [
        ('a b c', NS(foo=['a', 'b'], bar=['c'])),
    ]


kundi TestPositionalsNargs2Optional(ParserTestCase):
    """Test a Positional ukijumuisha 2 nargs followed by one optional"""

    argument_signatures = [Sig('foo', nargs=2), Sig('bar', nargs='?')]
    failures = ['', '--foo', 'a', 'a b c d']
    successes = [
        ('a b', NS(foo=['a', 'b'], bar=Tupu)),
        ('a b c', NS(foo=['a', 'b'], bar='c')),
    ]


kundi TestPositionalsNargsZeroOrMore1(ParserTestCase):
    """Test a Positional ukijumuisha unlimited nargs followed by one ukijumuisha 1"""

    argument_signatures = [Sig('foo', nargs='*'), Sig('bar', nargs=1)]
    failures = ['', '--foo', ]
    successes = [
        ('a', NS(foo=[], bar=['a'])),
        ('a b', NS(foo=['a'], bar=['b'])),
        ('a b c', NS(foo=['a', 'b'], bar=['c'])),
    ]


kundi TestPositionalsNargsOneOrMore1(ParserTestCase):
    """Test a Positional ukijumuisha one ama more nargs followed by one ukijumuisha 1"""

    argument_signatures = [Sig('foo', nargs='+'), Sig('bar', nargs=1)]
    failures = ['', '--foo', 'a']
    successes = [
        ('a b', NS(foo=['a'], bar=['b'])),
        ('a b c', NS(foo=['a', 'b'], bar=['c'])),
    ]


kundi TestPositionalsNargsOptional1(ParserTestCase):
    """Test a Positional ukijumuisha an Optional nargs followed by one ukijumuisha 1"""

    argument_signatures = [Sig('foo', nargs='?'), Sig('bar', nargs=1)]
    failures = ['', '--foo', 'a b c']
    successes = [
        ('a', NS(foo=Tupu, bar=['a'])),
        ('a b', NS(foo='a', bar=['b'])),
    ]


kundi TestPositionalsNargsTupuZeroOrMore1(ParserTestCase):
    """Test three Positionals: no nargs, unlimited nargs na 1 nargs"""

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


kundi TestPositionalsNargsTupuOneOrMore1(ParserTestCase):
    """Test three Positionals: no nargs, one ama more nargs na 1 nargs"""

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


kundi TestPositionalsNargsTupuOptional1(ParserTestCase):
    """Test three Positionals: no nargs, optional narg na 1 nargs"""

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
        ('', NS(foo=Tupu, bar=42)),
        ('a', NS(foo='a', bar=42)),
        ('a b', NS(foo='a', bar='b')),
    ]


kundi TestPositionalsNargsOptionalZeroOrMore(ParserTestCase):
    """Test an Optional narg followed by unlimited nargs"""

    argument_signatures = [Sig('foo', nargs='?'), Sig('bar', nargs='*')]
    failures = ['--foo']
    successes = [
        ('', NS(foo=Tupu, bar=[])),
        ('a', NS(foo='a', bar=[])),
        ('a b', NS(foo='a', bar=['b'])),
        ('a b c', NS(foo='a', bar=['b', 'c'])),
    ]


kundi TestPositionalsNargsOptionalOneOrMore(ParserTestCase):
    """Test an Optional narg followed by one ama more nargs"""

    argument_signatures = [Sig('foo', nargs='?'), Sig('bar', nargs='+')]
    failures = ['', '--foo']
    successes = [
        ('a', NS(foo=Tupu, bar=['a'])),
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
# Combined optionals na positionals tests
# ========================================

kundi TestOptionalsNumericAndPositionals(ParserTestCase):
    """Tests negative number args when numeric options are present"""

    argument_signatures = [
        Sig('x', nargs='?'),
        Sig('-4', dest='y', action='store_true'),
    ]
    failures = ['-2', '-315']
    successes = [
        ('', NS(x=Tupu, y=Uongo)),
        ('a', NS(x='a', y=Uongo)),
        ('-4', NS(x=Tupu, y=Kweli)),
        ('-4 a', NS(x='a', y=Kweli)),
    ]


kundi TestOptionalsAlmostNumericAndPositionals(ParserTestCase):
    """Tests negative number args when almost numeric options are present"""

    argument_signatures = [
        Sig('x', nargs='?'),
        Sig('-k4', dest='y', action='store_true'),
    ]
    failures = ['-k3']
    successes = [
        ('', NS(x=Tupu, y=Uongo)),
        ('-2', NS(x='-2', y=Uongo)),
        ('a', NS(x='a', y=Uongo)),
        ('-k4', NS(x=Tupu, y=Kweli)),
        ('-k4 a', NS(x='a', y=Kweli)),
    ]


kundi TestEmptyAndSpaceContainingArguments(ParserTestCase):

    argument_signatures = [
        Sig('x', nargs='?'),
        Sig('-y', '--yyy', dest='y'),
    ]
    failures = ['-y']
    successes = [
        ([''], NS(x='', y=Tupu)),
        (['a badger'], NS(x='a badger', y=Tupu)),
        (['-a badger'], NS(x='-a badger', y=Tupu)),
        (['-y', ''], NS(x=Tupu, y='')),
        (['-y', 'a badger'], NS(x=Tupu, y='a badger')),
        (['-y', '-a badger'], NS(x=Tupu, y='-a badger')),
        (['--yyy=a badger'], NS(x=Tupu, y='a badger')),
        (['--yyy=-a badger'], NS(x=Tupu, y='-a badger')),
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
        ('', NS(x=Tupu, y=42, z=Uongo)),
        ('-', NS(x='badger', y=42, z=Uongo)),
        ('- X', NS(x='X', y=42, z=Uongo)),
        ('+ -3', NS(x=Tupu, y=-3, z=Uongo)),
        ('-+-', NS(x=Tupu, y=42, z=Kweli)),
        ('- ===', NS(x='===', y=42, z=Uongo)),
    ]


kundi TestNargsZeroOrMore(ParserTestCase):
    """Tests specifying args kila an Optional that accepts zero ama more"""

    argument_signatures = [Sig('-x', nargs='*'), Sig('y', nargs='*')]
    failures = []
    successes = [
        ('', NS(x=Tupu, y=[])),
        ('-x', NS(x=[], y=[])),
        ('-x a', NS(x=['a'], y=[])),
        ('-x a -- b', NS(x=['a'], y=['b'])),
        ('a', NS(x=Tupu, y=['a'])),
        ('a -x', NS(x=[], y=['a'])),
        ('a -x b', NS(x=['b'], y=['a'])),
    ]


kundi TestNargsRemainder(ParserTestCase):
    """Tests specifying a positional ukijumuisha nargs=REMAINDER"""

    argument_signatures = [Sig('x'), Sig('y', nargs='...'), Sig('-z')]
    failures = ['', '-z', '-z Z']
    successes = [
        ('X', NS(x='X', y=[], z=Tupu)),
        ('-z Z X', NS(x='X', y=[], z='Z')),
        ('X A B -z Z', NS(x='X', y=['A', 'B', '-z', 'Z'], z=Tupu)),
        ('X Y --foo', NS(x='X', y=['Y', '--foo'], z=Tupu)),
    ]


kundi TestOptionLike(ParserTestCase):
    """Tests options that may ama may sio be arguments"""

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
        ('', NS(x=Tupu, y=Tupu, z=[])),
        ('-x 2.5', NS(x=2.5, y=Tupu, z=[])),
        ('-x 2.5 a', NS(x=2.5, y=Tupu, z=['a'])),
        ('-3.5', NS(x=Tupu, y=0.5, z=[])),
        ('-3-.5', NS(x=Tupu, y=-0.5, z=[])),
        ('-3 .5', NS(x=Tupu, y=0.5, z=[])),
        ('a -3.5', NS(x=Tupu, y=0.5, z=['a'])),
        ('a', NS(x=Tupu, y=Tupu, z=['a'])),
        ('a -x 1', NS(x=1.0, y=Tupu, z=['a'])),
        ('-x 1 a', NS(x=1.0, y=Tupu, z=['a'])),
        ('-3 1 a', NS(x=Tupu, y=1.0, z=['a'])),
    ]


kundi TestDefaultSuppress(ParserTestCase):
    """Test actions ukijumuisha suppressed defaults"""

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
        ('--baz', NS(baz=Kweli)),
        ('a --baz', NS(foo='a', baz=Kweli)),
        ('--baz a b', NS(foo='a', bar=['b'], baz=Kweli)),
    ]


kundi TestParserDefaultSuppress(ParserTestCase):
    """Test actions ukijumuisha a parser-level default of SUPPRESS"""

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
        ('--baz', NS(baz=Kweli)),
        ('a --baz', NS(foo='a', baz=Kweli)),
        ('--baz a b', NS(foo='a', bar=['b'], baz=Kweli)),
    ]


kundi TestParserDefault42(ParserTestCase):
    """Test actions ukijumuisha a parser-level default of 42"""

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
        ('--baz', NS(foo=42, bar=42, baz=Kweli, version=42)),
        ('a --baz', NS(foo='a', bar=42, baz=Kweli, version=42)),
        ('--baz a b', NS(foo='a', bar=['b'], baz=Kweli, version=42)),
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
        kila path, text kwenye file_texts:
            ukijumuisha open(path, 'w') as file:
                file.write(text)

    parser_signature = Sig(fromfile_prefix_chars='@')
    argument_signatures = [
        Sig('-a'),
        Sig('x'),
        Sig('y', nargs='+'),
    ]
    failures = ['', '-b', 'X', '@invalid', '@missing']
    successes = [
        ('X Y', NS(a=Tupu, x='X', y=['Y'])),
        ('X -a A Y Z', NS(a='A', x='X', y=['Y', 'Z'])),
        ('@hello X', NS(a=Tupu, x='hello world!', y=['X'])),
        ('X @hello', NS(a=Tupu, x='X', y=['hello world!'])),
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
        kila path, text kwenye file_texts:
            ukijumuisha open(path, 'w') as file:
                file.write(text)

    kundi FromFileConverterArgumentParser(ErrorRaisingArgumentParser):

        eleza convert_arg_line_to_args(self, arg_line):
            kila arg kwenye arg_line.split():
                ikiwa sio arg.strip():
                    endelea
                tuma arg
    parser_kundi = FromFileConverterArgumentParser
    parser_signature = Sig(fromfile_prefix_chars='@')
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
        ikiwa other kwenye self.seen:
            text = self.seen[other]
        isipokua:
            text = self.seen[other] = other.read()
            other.close()
        ikiwa sio isinstance(text, str):
            text = text.decode('ascii')
        rudisha self.name == other.name == text


kundi TestFileTypeR(TempDirMixin, ParserTestCase):
    """Test the FileType option/argument type kila reading files"""

    eleza setUp(self):
        super(TestFileTypeR, self).setUp()
        kila file_name kwenye ['foo', 'bar']:
            ukijumuisha open(os.path.join(self.temp_dir, file_name), 'w') as file:
                file.write(file_name)
        self.create_readonly_file('readonly')

    argument_signatures = [
        Sig('-x', type=argparse.FileType()),
        Sig('spam', type=argparse.FileType('r')),
    ]
    failures = ['-x', '', 'non-existent-file.txt']
    successes = [
        ('foo', NS(x=Tupu, spam=RFile('foo'))),
        ('-x foo bar', NS(x=RFile('foo'), spam=RFile('bar'))),
        ('bar -x foo', NS(x=RFile('foo'), spam=RFile('bar'))),
        ('-x - -', NS(x=eq_stdin, spam=eq_stdin)),
        ('readonly', NS(x=Tupu, spam=RFile('readonly'))),
    ]

kundi TestFileTypeDefaults(TempDirMixin, ParserTestCase):
    """Test that a file ni sio created unless the default ni needed"""
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
    # should sio provoke error because default file ni created
    successes = [('-c good', NS(c=RFile('good')))]


kundi TestFileTypeRB(TempDirMixin, ParserTestCase):
    """Test the FileType option/argument type kila reading files"""

    eleza setUp(self):
        super(TestFileTypeRB, self).setUp()
        kila file_name kwenye ['foo', 'bar']:
            ukijumuisha open(os.path.join(self.temp_dir, file_name), 'w') as file:
                file.write(file_name)

    argument_signatures = [
        Sig('-x', type=argparse.FileType('rb')),
        Sig('spam', type=argparse.FileType('rb')),
    ]
    failures = ['-x', '']
    successes = [
        ('foo', NS(x=Tupu, spam=RFile('foo'))),
        ('-x foo bar', NS(x=RFile('foo'), spam=RFile('bar'))),
        ('bar -x foo', NS(x=RFile('foo'), spam=RFile('bar'))),
        ('-x - -', NS(x=eq_stdin, spam=eq_stdin)),
    ]


kundi WFile(object):
    seen = set()

    eleza __init__(self, name):
        self.name = name

    eleza __eq__(self, other):
        ikiwa other sio kwenye self.seen:
            text = 'Check that file ni writable.'
            ikiwa 'b' kwenye other.mode:
                text = text.encode('ascii')
            other.write(text)
            other.close()
            self.seen.add(other)
        rudisha self.name == other.name


@unittest.skipIf(hasattr(os, 'geteuid') na os.geteuid() == 0,
                 "non-root user required")
kundi TestFileTypeW(TempDirMixin, ParserTestCase):
    """Test the FileType option/argument type kila writing files"""

    eleza setUp(self):
        super(TestFileTypeW, self).setUp()
        self.create_readonly_file('readonly')

    argument_signatures = [
        Sig('-x', type=argparse.FileType('w')),
        Sig('spam', type=argparse.FileType('w')),
    ]
    failures = ['-x', '', 'readonly']
    successes = [
        ('foo', NS(x=Tupu, spam=WFile('foo'))),
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
        ('foo', NS(x=Tupu, spam=WFile('foo'))),
        ('-x foo bar', NS(x=WFile('foo'), spam=WFile('bar'))),
        ('bar -x foo', NS(x=WFile('foo'), spam=WFile('bar'))),
        ('-x - -', NS(x=eq_stdout, spam=eq_stdout)),
    ]


kundi TestFileTypeOpenArgs(TestCase):
    """Test that open (the builtin) ni correctly called"""

    eleza test_open_args(self):
        FT = argparse.FileType
        cases = [
            (FT('rb'), ('rb', -1, Tupu, Tupu)),
            (FT('w', 1), ('w', 1, Tupu, Tupu)),
            (FT('w', errors='replace'), ('w', -1, Tupu, 'replace')),
            (FT('wb', encoding='big5'), ('wb', -1, 'big5', Tupu)),
            (FT('w', 0, 'l1', 'strict'), ('w', 0, 'l1', 'strict')),
        ]
        ukijumuisha mock.patch('builtins.open') as m:
            kila type, args kwenye cases:
                type('foo')
                m.assert_called_with('foo', *args)


kundi TestFileTypeMissingInitialization(TestCase):
    """
    Test that add_argument throws an error ikiwa FileType class
    object was passed instead of instance of FileType
    """

    eleza test(self):
        parser = argparse.ArgumentParser()
        ukijumuisha self.assertRaises(ValueError) as cm:
            parser.add_argument('-x', type=argparse.FileType)

        self.assertEqual(
            '%r ni a FileType kundi object, instance of it must be passed'
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
        ('1024.675', NS(eggs=Tupu, spam=1024.675)),
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
                         NS(x=Tupu, y='my_type{1}'))
        self.assertEqual(parser.parse_args('-x 1 42'.split()),
                         NS(x='my_type{1}', y='my_type{42}'))


# ============
# Action tests
# ============

kundi TestActionUserDefined(ParserTestCase):
    """Test a user-defined option/argument action"""

    kundi OptionalAction(argparse.Action):

        eleza __call__(self, parser, namespace, value, option_string=Tupu):
            jaribu:
                # check destination na option string
                assert self.dest == 'spam', 'dest: %s' % self.dest
                assert option_string == '-s', 'flag: %s' % option_string
                # when option ni before argument, badger=2, na when
                # option ni after argument, badger=<whatever was set>
                expected_ns = NS(spam=0.25)
                ikiwa value kwenye [0.125, 0.625]:
                    expected_ns.badger = 2
                elikiwa value kwenye [2.0]:
                    expected_ns.badger = 84
                isipokua:
                     ashiria AssertionError('value: %s' % value)
                assert expected_ns == namespace, ('expected %s, got %s' %
                                                  (expected_ns, namespace))
            except AssertionError:
                e = sys.exc_info()[1]
                 ashiria ArgumentParserError('opt_action failed: %s' % e)
            setattr(namespace, 'spam', value)

    kundi PositionalAction(argparse.Action):

        eleza __call__(self, parser, namespace, value, option_string=Tupu):
            jaribu:
                assert option_string ni Tupu, ('option_string: %s' %
                                               option_string)
                # check destination
                assert self.dest == 'badger', 'dest: %s' % self.dest
                # when argument ni before option, spam=0.25, na when
                # option ni after argument, spam=<whatever was set>
                expected_ns = NS(badger=2)
                ikiwa value kwenye [42, 84]:
                    expected_ns.spam = 0.25
                elikiwa value kwenye [1]:
                    expected_ns.spam = 0.625
                elikiwa value kwenye [2]:
                    expected_ns.spam = 0.125
                isipokua:
                     ashiria AssertionError('value: %s' % value)
                assert expected_ns == namespace, ('expected %s, got %s' %
                                                  (expected_ns, namespace))
            except AssertionError:
                e = sys.exc_info()[1]
                 ashiria ArgumentParserError('arg_action failed: %s' % e)
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

        eleza __call__(self, parser, namespace, values, option_string=Tupu):
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

    eleza _get_parser(self, subparser_help=Uongo, prefix_chars=Tupu,
                    aliases=Uongo):
        # create a parser ukijumuisha a subparsers argument
        ikiwa prefix_chars:
            parser = ErrorRaisingArgumentParser(
                prog='PROG', description='main description', prefix_chars=prefix_chars)
            parser.add_argument(
                prefix_chars[0] * 2 + 'foo', action='store_true', help='foo help')
        isipokua:
            parser = ErrorRaisingArgumentParser(
                prog='PROG', description='main description')
            parser.add_argument(
                '--foo', action='store_true', help='foo help')
        parser.add_argument(
            'bar', type=float, help='bar help')

        # check that only one subparsers argument can be added
        subparsers_kwargs = {'required': Uongo}
        ikiwa aliases:
            subparsers_kwargs['metavar'] = 'COMMAND'
            subparsers_kwargs['title'] = 'commands'
        isipokua:
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
        self.command_help_parser = self._get_parser(subparser_help=Kweli)

    eleza test_parse_args_failures(self):
        # check some failure cases:
        kila args_str kwenye ['', 'a', 'a a', '0.5 a', '0.5 1',
                         '0.5 1 -y', '0.5 2 -w']:
            args = args_str.split()
            self.assertArgumentParserError(self.parser.parse_args, args)

    eleza test_parse_args(self):
        # check some non-failure cases:
        self.assertEqual(
            self.parser.parse_args('0.5 1 b -w 7'.split()),
            NS(foo=Uongo, bar=0.5, w=7, x='b'),
        )
        self.assertEqual(
            self.parser.parse_args('0.25 --foo 2 -y 2 3j -- -1j'.split()),
            NS(foo=Kweli, bar=0.25, y='2', z=[3j, -1j]),
        )
        self.assertEqual(
            self.parser.parse_args('--foo 0.125 1 c'.split()),
            NS(foo=Kweli, bar=0.125, w=Tupu, x='c'),
        )
        self.assertEqual(
            self.parser.parse_args('-1.5 3 11 -- a --foo 7 -- b'.split()),
            NS(foo=Uongo, bar=-1.5, t=11, u=['a', '--foo', '7', '--', 'b']),
        )

    eleza test_parse_known_args(self):
        self.assertEqual(
            self.parser.parse_known_args('0.5 1 b -w 7'.split()),
            (NS(foo=Uongo, bar=0.5, w=7, x='b'), []),
        )
        self.assertEqual(
            self.parser.parse_known_args('0.5 -p 1 b -w 7'.split()),
            (NS(foo=Uongo, bar=0.5, w=7, x='b'), ['-p']),
        )
        self.assertEqual(
            self.parser.parse_known_args('0.5 1 b -w 7 -p'.split()),
            (NS(foo=Uongo, bar=0.5, w=7, x='b'), ['-p']),
        )
        self.assertEqual(
            self.parser.parse_known_args('0.5 1 b -q -rs -w 7'.split()),
            (NS(foo=Uongo, bar=0.5, w=7, x='b'), ['-q', '-rs']),
        )
        self.assertEqual(
            self.parser.parse_known_args('0.5 -W 1 b -X Y -w 7 Z'.split()),
            (NS(foo=Uongo, bar=0.5, w=7, x='b'), ['-W', '-X', 'Y', 'Z']),
        )

    eleza test_dest(self):
        parser = ErrorRaisingArgumentParser()
        parser.add_argument('--foo', action='store_true')
        subparsers = parser.add_subparsers(dest='bar')
        parser1 = subparsers.add_parser('1')
        parser1.add_argument('baz')
        self.assertEqual(NS(foo=Uongo, bar='1', baz='2'),
                         parser.parse_args('1 2'.split()))

    eleza _test_required_subparsers(self, parser):
        # Should parse the sub command
        ret = parser.parse_args(['run'])
        self.assertEqual(ret.command, 'run')

        # Error when the command ni missing
        self.assertArgumentParserError(parser.parse_args, ())

    eleza test_required_subparsers_via_attribute(self):
        parser = ErrorRaisingArgumentParser()
        subparsers = parser.add_subparsers(dest='command')
        subparsers.required = Kweli
        subparsers.add_parser('run')
        self._test_required_subparsers(parser)

    eleza test_required_subparsers_via_kwarg(self):
        parser = ErrorRaisingArgumentParser()
        subparsers = parser.add_subparsers(dest='command', required=Kweli)
        subparsers.add_parser('run')
        self._test_required_subparsers(parser)

    eleza test_required_subparsers_default(self):
        parser = ErrorRaisingArgumentParser()
        subparsers = parser.add_subparsers(dest='command')
        subparsers.add_parser('run')
        # No error here
        ret = parser.parse_args(())
        self.assertIsTupu(ret.command)

    eleza test_optional_subparsers(self):
        parser = ErrorRaisingArgumentParser()
        subparsers = parser.add_subparsers(dest='command', required=Uongo)
        subparsers.add_parser('run')
        # No error here
        ret = parser.parse_args(())
        self.assertIsTupu(ret.command)

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
              -h, --help  show this help message na exit
              --foo       foo help
            '''))

    eleza test_help_extra_prefix_chars(self):
        # Make sure - ni still used kila help ikiwa it ni a non-first prefix char
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
              -h, --help  show this help message na exit
              ++foo       foo help
            '''))

    eleza test_help_non_komaing_spaces(self):
        parser = ErrorRaisingArgumentParser(
            prog='PROG', description='main description')
        parser.add_argument(
            "--non-komaing", action='store_false',
            help='help message containing non-komaing spaces shall sio '
            'wrap\N{NO-BREAK SPACE}at non-komaing spaces')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
            usage: PROG [-h] [--non-komaing]

            main description

            optional arguments:
              -h, --help      show this help message na exit
              --non-komaing  help message containing non-komaing spaces shall not
                              wrap\N{NO-BREAK SPACE}at non-komaing spaces
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
              +h, ++help  show this help message na exit
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
              -h, --help  show this help message na exit
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
              -h, --help  show this help message na exit
              --foo       foo help

            subcommands:
              command help

              {1,2}       additional text
            '''))

    eleza _test_subparser_help(self, args_str, expected_help):
        ukijumuisha self.assertRaises(ArgumentParserError) as cm:
            self.parser.parse_args(args_str.split())
        self.assertEqual(expected_help, cm.exception.stdout)

    eleza test_subparser1_help(self):
        self._test_subparser_help('5.0 1 -h', textwrap.dedent('''\
            usage: PROG bar 1 [-h] [-w W] {a,b,c}

            1 description

            positional arguments:
              {a,b,c}     x help

            optional arguments:
              -h, --help  show this help message na exit
              -w W        w help
            '''))

    eleza test_subparser2_help(self):
        self._test_subparser_help('5.0 2 -h', textwrap.dedent('''\
            usage: PROG bar 2 [-h] [-y {1,2,3}] [z [z ...]]

            2 description

            positional arguments:
              z           z help

            optional arguments:
              -h, --help  show this help message na exit
              -y {1,2,3}  y help
            '''))

    eleza test_alias_invocation(self):
        parser = self._get_parser(aliases=Kweli)
        self.assertEqual(
            parser.parse_known_args('0.5 1alias1 b'.split()),
            (NS(foo=Uongo, bar=0.5, w=Tupu, x='b'), []),
        )
        self.assertEqual(
            parser.parse_known_args('0.5 1alias2 b'.split()),
            (NS(foo=Uongo, bar=0.5, w=Tupu, x='b'), []),
        )

    eleza test_error_alias_invocation(self):
        parser = self._get_parser(aliases=Kweli)
        self.assertArgumentParserError(parser.parse_args,
                                       '0.5 1alias3 b'.split())

    eleza test_alias_help(self):
        parser = self._get_parser(aliases=Kweli, subparser_help=Kweli)
        self.maxDiff = Tupu
        self.assertEqual(parser.format_help(), textwrap.dedent("""\
            usage: PROG [-h] [--foo] bar COMMAND ...

            main description

            positional arguments:
              bar                   bar help

            optional arguments:
              -h, --help            show this help message na exit
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
    """Tests that parsers can be created ukijumuisha parent parsers"""

    eleza assertArgumentParserError(self, *args, **kwargs):
        self.assertRaises(ArgumentParserError, *args, **kwargs)

    eleza setUp(self):
        super().setUp()
        self.wxyz_parent = ErrorRaisingArgumentParser(add_help=Uongo)
        self.wxyz_parent.add_argument('--w')
        x_group = self.wxyz_parent.add_argument_group('x')
        x_group.add_argument('-y')
        self.wxyz_parent.add_argument('z')

        self.abcd_parent = ErrorRaisingArgumentParser(add_help=Uongo)
        self.abcd_parent.add_argument('a')
        self.abcd_parent.add_argument('-b')
        c_group = self.abcd_parent.add_argument_group('c')
        c_group.add_argument('--d')

        self.w_parent = ErrorRaisingArgumentParser(add_help=Uongo)
        self.w_parent.add_argument('--w')

        self.z_parent = ErrorRaisingArgumentParser(add_help=Uongo)
        self.z_parent.add_argument('z')

        # parents ukijumuisha mutually exclusive groups
        self.ab_mutex_parent = ErrorRaisingArgumentParser(add_help=Uongo)
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
        parser = ErrorRaisingArgumentParser(add_help=Uongo, parents=parents)
        parser = ErrorRaisingArgumentParser(parents=[parser])
        self._test_mutex_ab(parser.parse_args)

    eleza _test_mutex_ab(self, parse_args):
        self.assertEqual(parse_args([]), NS(a=Uongo, b=Uongo))
        self.assertEqual(parse_args(['-a']), NS(a=Kweli, b=Uongo))
        self.assertEqual(parse_args(['-b']), NS(a=Uongo, b=Kweli))
        self.assertArgumentParserError(parse_args, ['-a', '-b'])
        self.assertArgumentParserError(parse_args, ['-b', '-a'])
        self.assertArgumentParserError(parse_args, ['-c'])
        self.assertArgumentParserError(parse_args, ['-a', '-c'])
        self.assertArgumentParserError(parse_args, ['-b', '-c'])

    eleza test_multiple_parents(self):
        parents = [self.abcd_parent, self.wxyz_parent]
        parser = ErrorRaisingArgumentParser(parents=parents)
        self.assertEqual(parser.parse_args('--d 1 --w 2 3 4'.split()),
                         NS(a='3', b=Tupu, d='1', w='2', y=Tupu, z='4'))

    eleza test_multiple_parents_mutex(self):
        parents = [self.ab_mutex_parent, self.wxyz_parent]
        parser = ErrorRaisingArgumentParser(parents=parents)
        self.assertEqual(parser.parse_args('-a --w 2 3'.split()),
                         NS(a=Kweli, b=Uongo, w='2', y=Tupu, z='3'))
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
                         NS(w=Tupu, y=Tupu, z='2'))

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
                         NS(a=Kweli, b=Uongo, c='4'))
        self.assertEqual(parser.parse_args('bar -b  --w 2 3 4'.split()),
                         NS(a=Uongo, b=Kweli, w='2', y=Tupu, z='3', e='4'))
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
              -h, --help  show this help message na exit
              -b B
              --w W

            c:
              --d D

            x:
              -y Y
        '''.format(progname, ' ' ikiwa progname isipokua '' )))

    eleza test_groups_parents(self):
        parent = ErrorRaisingArgumentParser(add_help=Uongo)
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
              -h, --help  show this help message na exit
              -y Y
              -z Z

            g:
              gd

              -w W
              -x X
        '''.format(progname, ' ' ikiwa progname isipokua '' )))

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
        raises(ValueError, add_argument, '--foo', required=Kweli)
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
              -h, --help  show this help message na exit
              --foo
              --bar
              --soup
              --nuts
              '''
        self.assertEqual(parser.format_help(), textwrap.dedent(expected))

kundi MEMixin(object):

    eleza test_failures_when_not_required(self):
        parse_args = self.get_parser(required=Uongo).parse_args
        error = ArgumentParserError
        kila args_string kwenye self.failures:
            self.assertRaises(error, parse_args, args_string.split())

    eleza test_failures_when_required(self):
        parse_args = self.get_parser(required=Kweli).parse_args
        error = ArgumentParserError
        kila args_string kwenye self.failures + ['']:
            self.assertRaises(error, parse_args, args_string.split())

    eleza test_successes_when_not_required(self):
        parse_args = self.get_parser(required=Uongo).parse_args
        successes = self.successes + self.successes_when_not_required
        kila args_string, expected_ns kwenye successes:
            actual_ns = parse_args(args_string.split())
            self.assertEqual(actual_ns, expected_ns)

    eleza test_successes_when_required(self):
        parse_args = self.get_parser(required=Kweli).parse_args
        kila args_string, expected_ns kwenye self.successes:
            actual_ns = parse_args(args_string.split())
            self.assertEqual(actual_ns, expected_ns)

    eleza test_usage_when_not_required(self):
        format_usage = self.get_parser(required=Uongo).format_usage
        expected_usage = self.usage_when_not_required
        self.assertEqual(format_usage(), textwrap.dedent(expected_usage))

    eleza test_usage_when_required(self):
        format_usage = self.get_parser(required=Kweli).format_usage
        expected_usage = self.usage_when_required
        self.assertEqual(format_usage(), textwrap.dedent(expected_usage))

    eleza test_help_when_not_required(self):
        format_help = self.get_parser(required=Uongo).format_help
        help = self.usage_when_not_required + self.help
        self.assertEqual(format_help(), textwrap.dedent(help))

    eleza test_help_when_required(self):
        format_help = self.get_parser(required=Kweli).format_help
        help = self.usage_when_required + self.help
        self.assertEqual(format_help(), textwrap.dedent(help))


kundi TestMutuallyExclusiveSimple(MEMixin, TestCase):

    eleza get_parser(self, required=Tupu):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('--bar', help='bar help')
        group.add_argument('--baz', nargs='?', const='Z', help='baz help')
        rudisha parser

    failures = ['--bar X --baz Y', '--bar X --baz']
    successes = [
        ('--bar X', NS(bar='X', baz=Tupu)),
        ('--bar X --bar Z', NS(bar='Z', baz=Tupu)),
        ('--baz Y', NS(bar=Tupu, baz='Y')),
        ('--baz', NS(bar=Tupu, baz='Z')),
    ]
    successes_when_not_required = [
        ('', NS(bar=Tupu, baz=Tupu)),
    ]

    usage_when_not_required = '''\
        usage: PROG [-h] [--bar BAR | --baz [BAZ]]
        '''
    usage_when_required = '''\
        usage: PROG [-h] (--bar BAR | --baz [BAZ])
        '''
    help = '''\

        optional arguments:
          -h, --help   show this help message na exit
          --bar BAR    bar help
          --baz [BAZ]  baz help
        '''


kundi TestMutuallyExclusiveLong(MEMixin, TestCase):

    eleza get_parser(self, required=Tupu):
        parser = ErrorRaisingArgumentParser(prog='PROG')
        parser.add_argument('--abcde', help='abcde help')
        parser.add_argument('--fghij', help='fghij help')
        group = parser.add_mutually_exclusive_group(required=required)
        group.add_argument('--klmno', help='klmno help')
        group.add_argument('--pqrst', help='pqrst help')
        rudisha parser

    failures = ['--klmno X --pqrst Y']
    successes = [
        ('--klmno X', NS(abcde=Tupu, fghij=Tupu, klmno='X', pqrst=Tupu)),
        ('--abcde Y --klmno X',
            NS(abcde='Y', fghij=Tupu, klmno='X', pqrst=Tupu)),
        ('--pqrst X', NS(abcde=Tupu, fghij=Tupu, klmno=Tupu, pqrst='X')),
        ('--pqrst X --fghij Y',
            NS(abcde=Tupu, fghij='Y', klmno=Tupu, pqrst='X')),
    ]
    successes_when_not_required = [
        ('', NS(abcde=Tupu, fghij=Tupu, klmno=Tupu, pqrst=Tupu)),
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
      -h, --help     show this help message na exit
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
        ('-x X', NS(x='X', y=Kweli)),
        ('-x X -x Y', NS(x='Y', y=Kweli)),
        ('-y', NS(x=Tupu, y=Uongo)),
    ]
    successes_when_not_required = [
        ('', NS(x=Tupu, y=Kweli)),
    ]

    usage_when_not_required = '''\
        usage: PROG [-h] [-y]
        '''
    usage_when_required = '''\
        usage: PROG [-h] -y
        '''
    help = '''\

        optional arguments:
          -h, --help  show this help message na exit
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
        ('--spam', NS(spam=Kweli, badger=Kweli, bladder=Tupu)),
        ('--badger', NS(spam=Uongo, badger=Uongo, bladder=Tupu)),
        ('--bladder B', NS(spam=Uongo, badger=Kweli, bladder='B')),
        ('--spam --spam', NS(spam=Kweli, badger=Kweli, bladder=Tupu)),
    ]
    successes_when_not_required = [
        ('', NS(spam=Uongo, badger=Kweli, bladder=Tupu)),
    ]

    usage_when_required = usage_when_not_required = '''\
        usage: PROG [-h]
        '''
    help = '''\

        optional arguments:
          -h, --help  show this help message na exit
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
        ('--foo', NS(foo=Kweli, spam=Tupu, badger='X')),
        ('--spam S', NS(foo=Uongo, spam='S', badger='X')),
        ('X', NS(foo=Uongo, spam=Tupu, badger=['X'])),
        ('X Y Z', NS(foo=Uongo, spam=Tupu, badger=['X', 'Y', 'Z'])),
    ]
    successes_when_not_required = [
        ('', NS(foo=Uongo, spam=Tupu, badger='X')),
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
          -h, --help   show this help message na exit
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
        ('-a', NS(a=Kweli, b=Uongo, c=Uongo, x=Uongo, y=Uongo)),
        ('-b', NS(a=Uongo, b=Kweli, c=Uongo, x=Uongo, y=Uongo)),
        ('-c', NS(a=Uongo, b=Uongo, c=Kweli, x=Uongo, y=Uongo)),
        ('-a -x', NS(a=Kweli, b=Uongo, c=Uongo, x=Kweli, y=Uongo)),
        ('-y -b', NS(a=Uongo, b=Kweli, c=Uongo, x=Uongo, y=Kweli)),
        ('-x -y -c', NS(a=Uongo, b=Uongo, c=Kweli, x=Kweli, y=Kweli)),
    ]
    successes_when_not_required = [
        ('', NS(a=Uongo, b=Uongo, c=Uongo, x=Uongo, y=Uongo)),
        ('-x', NS(a=Uongo, b=Uongo, c=Uongo, x=Kweli, y=Uongo)),
        ('-y', NS(a=Uongo, b=Uongo, c=Uongo, x=Uongo, y=Kweli)),
    ]

    usage_when_required = usage_when_not_required = '''\
        usage: PROG [-h] [-x] [-a] [-b] [-y] [-c]
        '''
    help = '''\

        optional arguments:
          -h, --help  show this help message na exit
          -x          x help
          -a          a help
          -b          b help
          -y          y help
          -c          c help
        '''


kundi TestMutuallyExclusiveInGroup(MEMixin, TestCase):

    eleza get_parser(self, required=Tupu):
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
        ('--bar X', NS(bar='X', baz=Tupu)),
        ('--baz Y', NS(bar=Tupu, baz='Y')),
    ]
    successes_when_not_required = [
        ('', NS(bar=Tupu, baz=Tupu)),
    ]

    usage_when_not_required = '''\
        usage: PROG [-h] [--bar BAR | --baz BAZ]
        '''
    usage_when_required = '''\
        usage: PROG [-h] (--bar BAR | --baz BAZ)
        '''
    help = '''\

        optional arguments:
          -h, --help  show this help message na exit

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
        ('X A', NS(a='A', b=Uongo, c=Uongo, x='X', y=Uongo)),
        ('X -b', NS(a=Tupu, b=Kweli, c=Uongo, x='X', y=Uongo)),
        ('X -c', NS(a=Tupu, b=Uongo, c=Kweli, x='X', y=Uongo)),
        ('X A -y', NS(a='A', b=Uongo, c=Uongo, x='X', y=Kweli)),
        ('X -y -b', NS(a=Tupu, b=Kweli, c=Uongo, x='X', y=Kweli)),
    ]
    successes_when_not_required = [
        ('X', NS(a=Tupu, b=Uongo, c=Uongo, x='X', y=Uongo)),
        ('X -y', NS(a=Tupu, b=Uongo, c=Uongo, x='X', y=Kweli)),
    ]

    usage_when_required = usage_when_not_required = '''\
        usage: PROG [-h] [-y] [-b] [-c] x [a]
        '''
    help = '''\

        positional arguments:
          x           x help
          a           a help

        optional arguments:
          -h, --help  show this help message na exit
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
          -h, --help  show this help message na exit
          -a A
          -b B
          -c C
          -d D
          -e E
          -f F
        '''

    # We are only interested kwenye testing the behavior of format_usage().
    test_failures_when_not_required = Tupu
    test_failures_when_required = Tupu
    test_successes_when_not_required = Tupu
    test_successes_when_required = Tupu

# =================================================
# Mutually exclusive group kwenye parent parser tests
# =================================================

kundi MEPBase(object):

    eleza get_parser(self, required=Tupu):
        parent = super(MEPBase, self).get_parser(required=required)
        parser = ErrorRaisingArgumentParser(
            prog=parent.prog, add_help=Uongo, parents=[parent])
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
        parent = ErrorRaisingArgumentParser(add_help=Uongo)
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
        self.assertIsTupu(parser.get_default("foo"))
        self.assertIsTupu(parser.get_default("bar"))

        parser.add_argument("--foo")
        self.assertIsTupu(parser.get_default("foo"))
        self.assertIsTupu(parser.get_default("bar"))

        parser.add_argument("--bar", type=int, default=42)
        self.assertIsTupu(parser.get_default("foo"))
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

                kila test_func kwenye [self.test_format,
                                  self.test_print,
                                  self.test_print_file]:
                    test_name = '%s_%s' % (test_func.__name__, func_suffix)

                    eleza test_wrapper(self, test_func=test_func):
                        test_func(self)
                    jaribu:
                        test_wrapper.__name__ = test_name
                    except TypeError:
                        pass
                    setattr(test_class, test_name, test_wrapper)

            eleza _get_parser(self, tester):
                parser = argparse.ArgumentParser(
                    *tester.parser_signature.args,
                    **tester.parser_signature.kwargs)
                kila argument_sig kwenye getattr(tester, 'argument_signatures', []):
                    parser.add_argument(*argument_sig.args,
                                        **argument_sig.kwargs)
                group_sigs = getattr(tester, 'argument_group_signatures', [])
                kila group_sig, argument_sigs kwenye group_sigs:
                    group = parser.add_argument_group(*group_sig.args,
                                                      **group_sig.kwargs)
                    kila argument_sig kwenye argument_sigs:
                        group.add_argument(*argument_sig.args,
                                           **argument_sig.kwargs)
                subparsers_sigs = getattr(tester, 'subparsers_signatures', [])
                ikiwa subparsers_sigs:
                    subparsers = parser.add_subparsers()
                    kila subparser_sig kwenye subparsers_sigs:
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
                jaribu:
                    print_()
                    parser_text = getattr(sys, self.std_name).getvalue()
                mwishowe:
                    setattr(sys, self.std_name, old_stream)
                self._test(tester, parser_text)

            eleza test_print_file(self, tester):
                parser = self._get_parser(tester)
                print_ = getattr(parser, 'print_%s' % self.func_suffix)
                sfile = StdIOBuffer()
                print_(sfile)
                parser_text = sfile.getvalue()
                self._test(tester, parser_text)

        # add tests kila {format,print}_{usage,help}
        kila func_suffix, std_name kwenye [('usage', 'stdout'),
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
          -h, --help     show this help message na exit
          -v, --version  show program's version number na exit
          -x             X HELP
          --y Y          Y HELP

        EPILOG
    '''
    version = '''\
        0.1
        '''

kundi TestShortColumns(HelpTestCase):
    '''Test extremely small number of columns.

    TestCase prevents "COLUMNS" kutoka being too small kwenye the tests themselves,
    but we don't want any exceptions thrown kwenye such cases. Only ugly representation.
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
          -h, --help     show this help message na exit
          -v, --version  show program's version number na exit
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
          -h, --help       show this help message na exit
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
                    'that ni so long that it should go onto multiple '
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

        oddly formatted description that ni so long that it should go onto \
multiple
        lines when wrapped

        positional arguments:
          yyy         normal y help

        optional arguments:
          -h, --help  show this help message na exit
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
          -h, --help  show this help message na exit
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
          -h, --help            show this help message na exit
          -v, --version         show program's version number na exit
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
          -h, --help      show this help message na exit
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

    parser_signature = Sig(prog='PROG', add_help=Uongo)
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
    """Test usage messages where the prog ni long"""

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
          -h, --help  show this help message na exit
          -w W
          -x X
        '''
    version = ''


kundi TestHelpUsageLongProgOptionsWrap(HelpTestCase):
    """Test usage messages where the prog ni long na the optionals wrap"""

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
          -h, --help            show this help message na exit
          -w WWWWWWWWWWWWWWWWWWWWWWWWW
          -x XXXXXXXXXXXXXXXXXXXXXXXXX
          -y YYYYYYYYYYYYYYYYYYYYYYYYY
          -z ZZZZZZZZZZZZZZZZZZZZZZZZZ
        '''
    version = ''


kundi TestHelpUsageLongProgPositionalsWrap(HelpTestCase):
    """Test usage messages where the prog ni long na the positionals wrap"""

    parser_signature = Sig(prog='P' * 60, add_help=Uongo)
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
          -h, --help            show this help message na exit
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
          -h, --help            show this help message na exit
          -x X
          -y Y
          -z Z
        '''
    version = ''


kundi TestHelpUsageOptionalsPositionalsWrap(HelpTestCase):
    """Test usage messages where the optionals na positionals wrap"""

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
          -h, --help            show this help message na exit
          -x XXXXXXXXXXXXXXXXXXXXXXXXX
          -y YYYYYYYYYYYYYYYYYYYYYYYYY
          -z ZZZZZZZZZZZZZZZZZZZZZZZZZ
        '''
    version = ''


kundi TestHelpUsageOptionalsOnlyWrap(HelpTestCase):
    """Test usage messages where there are only optionals na they wrap"""

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
          -h, --help            show this help message na exit
          -x XXXXXXXXXXXXXXXXXXXXXXXXX
          -y YYYYYYYYYYYYYYYYYYYYYYYYY
          -z ZZZZZZZZZZZZZZZZZZZZZZZZZ
        '''
    version = ''


kundi TestHelpUsagePositionalsOnlyWrap(HelpTestCase):
    """Test usage messages where there are only positionals na they wrap"""

    parser_signature = Sig(prog='PROG', add_help=Uongo)
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
    """Test that variables are expanded properly kwenye help messages"""

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
          spam           spam PROG Tupu
          badger         badger PROG 0.5

        optional arguments:
          -h, --help     show this help message na exit
          -x X           x PROG Tupu int %
          -y             y PROG 42 XXX
          --foo {a,b,c}  foo PROG Tupu a, b, c
          --bar BBB      bar PROG baz bar

        group:
          -a A           a PROG Tupu
          -b B           b PROG -1
        '''
    version = ''


kundi TestHelpVariableExpansionUsageSupplied(HelpTestCase):
    """Test that variables are expanded properly when usage= ni present"""

    parser_signature = Sig(prog='PROG', usage='%(prog)s FOO')
    argument_signatures = []
    argument_group_signatures = []
    usage = ('''\
        usage: PROG FOO
        ''')
    help = usage + '''\

        optional arguments:
          -h, --help  show this help message na exit
        '''
    version = ''


kundi TestHelpVariableExpansionNoArguments(HelpTestCase):
    """Test that variables are expanded properly ukijumuisha no arguments"""

    parser_signature = Sig(prog='PROG', add_help=Uongo)
    argument_signatures = []
    argument_group_signatures = []
    usage = ('''\
        usage: PROG
        ''')
    help = usage
    version = ''


kundi TestHelpSuppressUsage(HelpTestCase):
    """Test that items can be suppressed kwenye usage messages"""

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
          -h, --help  show this help message na exit
          --foo FOO   foo help
        '''
    usage = ''
    version = ''


kundi TestHelpSuppressOptional(HelpTestCase):
    """Test that optional arguments can be suppressed kwenye help messages"""

    parser_signature = Sig(prog='PROG', add_help=Uongo)
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
    """Test that optional groups can be suppressed kwenye help messages"""

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
          -h, --help  show this help message na exit
          --foo FOO   foo help
        '''
    version = ''


kundi TestHelpSuppressPositional(HelpTestCase):
    """Test that positional arguments can be suppressed kwenye help messages"""

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
          -h, --help  show this help message na exit
          --foo FOO   foo help
        '''
    version = ''


kundi TestHelpRequiredOptional(HelpTestCase):
    """Test that required options don't look optional"""

    parser_signature = Sig(prog='PROG')
    argument_signatures = [
        Sig('--foo', required=Kweli, help='foo help'),
    ]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] --foo FOO
        '''
    help = usage + '''\

        optional arguments:
          -h, --help  show this help message na exit
          --foo FOO   foo help
        '''
    version = ''


kundi TestHelpAlternatePrefixChars(HelpTestCase):
    """Test that options display ukijumuisha different prefix characters"""

    parser_signature = Sig(prog='PROG', prefix_chars='^;', add_help=Uongo)
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

    parser_signature = Sig(prog='PROG', add_help=Uongo)
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


kundi TestHelpTupu(HelpTestCase):
    """Test that no errors occur ikiwa no help ni specified"""

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
          -h, --help  show this help message na exit
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
          -h, --help        show this help message na exit
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
                    '    exactly as it ni written\n'
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
                                  '    exactly like it ni here\n'),
         [Sig('--bar', help='bar help')]),
    ]
    usage = '''\
        usage: PROG [-h] [--foo FOO] [--bar BAR] spam
        '''
    help = usage + '''\

        Keep the formatting
            exactly as it ni written

        here

        positional arguments:
          spam        spam help

        optional arguments:
          -h, --help  show this help message na exit
          --foo FOO       foo help should also
                      appear as given here

        title:
              This text
            should be indented
              exactly like it ni here

          --bar BAR   bar help
        '''
    version = ''


kundi TestHelpRawDescription(HelpTestCase):
    """Test the RawTextHelpFormatter"""

    parser_signature = Sig(
        prog='PROG', formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Keep the formatting\n'
                    '    exactly as it ni written\n'
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
                                  '    exactly like it ni here\n'),
         [Sig('--bar', help='bar help')]),
    ]
    usage = '''\
        usage: PROG [-h] [--foo FOO] [--bar BAR] spam
        '''
    help = usage + '''\

        Keep the formatting
            exactly as it ni written

        here

        positional arguments:
          spam        spam help

        optional arguments:
          -h, --help  show this help message na exit
          --foo FOO   foo help should sio retain this odd formatting

        title:
              This text
            should be indented
              exactly like it ni here

          --bar BAR   bar help
        '''
    version = ''


kundi TestHelpArgumentDefaults(HelpTestCase):
    """Test the ArgumentDefaultsHelpFormatter"""

    parser_signature = Sig(
        prog='PROG', formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='description')

    argument_signatures = [
        Sig('--foo', help='foo help - oh na by the way, %(default)s'),
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
          -h, --help  show this help message na exit
          --foo FOO   foo help - oh na by the way, Tupu
          --bar       bar help (default: Uongo)

        title:
          description

          --baz BAZ   baz help (default: 42)
        '''
    version = ''

kundi TestHelpVersionAction(HelpTestCase):
    """Test the default help kila the version action"""

    parser_signature = Sig(prog='PROG', description='description')
    argument_signatures = [Sig('-V', '--version', action='version', version='3.6')]
    argument_group_signatures = []
    usage = '''\
        usage: PROG [-h] [-V]
        '''
    help = usage + '''\

        description

        optional arguments:
          -h, --help     show this help message na exit
          -V, --version  show program's version number na exit
        '''
    version = ''


kundi TestHelpVersionActionSuppress(HelpTestCase):
    """Test that the --version argument can be suppressed kwenye help messages"""

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
          -h, --help  show this help message na exit
          --foo FOO   foo help
        '''


kundi TestHelpSubparsersOrdering(HelpTestCase):
    """Test ordering of subcommands kwenye help matches the code"""
    parser_signature = Sig(prog='PROG',
                           description='display some subcommands')
    argument_signatures = [Sig('-v', '--version', action='version', version='0.1')]

    subparsers_signatures = [Sig(name=name)
                             kila name kwenye ('a', 'b', 'c', 'd', 'e')]

    usage = '''\
        usage: PROG [-h] [-v] {a,b,c,d,e} ...
        '''

    help = usage + '''\

        display some subcommands

        positional arguments:
          {a,b,c,d,e}

        optional arguments:
          -h, --help     show this help message na exit
          -v, --version  show program's version number na exit
        '''

    version = '''\
        0.1
        '''

kundi TestHelpSubparsersWithHelpOrdering(HelpTestCase):
    """Test ordering of subcommands kwenye help matches the code"""
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
                             kila name, help kwenye subcommand_data]

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
          -h, --help     show this help message na exit
          -v, --version  show program's version number na exit
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
          -h, --help      show this help message na exit
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
        self.assertTypeError('-x', bar=Tupu)
        self.assertTypeError('-y', callback='foo')
        self.assertTypeError('-y', callback_args=())
        self.assertTypeError('-y', callback_kwargs={})

    eleza test_missing_destination(self):
        self.assertTypeError()
        kila action kwenye ['append', 'store']:
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
        ukijumuisha self.assertRaises(ValueError) as cm:
            parser.add_argument("--foo", action="store-true")
        self.assertIn('unknown action', str(cm.exception))

    eleza test_multiple_dest(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(dest='foo')
        ukijumuisha self.assertRaises(ValueError) as cm:
            parser.add_argument('bar', dest='baz')
        self.assertIn('dest supplied twice kila positional argument',
                      str(cm.exception))

    eleza test_no_argument_actions(self):
        kila action kwenye ['store_const', 'store_true', 'store_false',
                       'append_const', 'count']:
            kila attrs kwenye [dict(type=int), dict(nargs='+'),
                          dict(choices='ab')]:
                self.assertTypeError('-x', action=action, **attrs)

    eleza test_no_argument_no_const_actions(self):
        # options ukijumuisha zero arguments
        kila action kwenye ['store_true', 'store_false', 'count']:

            # const ni always disallowed
            self.assertTypeError('-x', const='foo', action=action)

            # nargs ni always disallowed
            self.assertTypeError('-x', nargs='*', action=action)

    eleza test_more_than_one_argument_actions(self):
        kila action kwenye ['store', 'append']:

            # nargs=0 ni disallowed
            self.assertValueError('-x', nargs=0, action=action)
            self.assertValueError('spam', nargs=0, action=action)

            # const ni disallowed ukijumuisha non-optional arguments
            kila nargs kwenye [1, '*', '+']:
                self.assertValueError('-x', const='foo',
                                      nargs=nargs, action=action)
                self.assertValueError('spam', const='foo',
                                      nargs=nargs, action=action)

    eleza test_required_const_actions(self):
        kila action kwenye ['store_const', 'append_const']:

            # nargs ni always disallowed
            self.assertTypeError('-x', nargs='+', action=action)

    eleza test_parsers_action_missing_params(self):
        self.assertTypeError('command', action='parsers')
        self.assertTypeError('command', action='parsers', prog='PROG')
        self.assertTypeError('command', action='parsers',
                             parser_class=argparse.ArgumentParser)

    eleza test_required_positional(self):
        self.assertTypeError('foo', required=Kweli)

    eleza test_user_defined_action(self):

        kundi Success(Exception):
            pass

        kundi Action(object):

            eleza __init__(self,
                         option_strings,
                         dest,
                         const,
                         default,
                         required=Uongo):
                ikiwa dest == 'spam':
                    ikiwa const ni Success:
                        ikiwa default ni Success:
                             ashiria Success()

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
              -h, --help  show this help message na exit
              -x X        NEW X
            '''))

        parser.add_argument('--spam', metavar='OLD_SPAM')
        parser.add_argument('--spam', metavar='NEW_SPAM')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
            usage: PROG [-h] [-x X] [--spam NEW_SPAM]

            optional arguments:
              -h, --help       show this help message na exit
              -x X             NEW X
              --spam NEW_SPAM
            '''))


# =============================
# Help na Version option tests
# =============================

kundi TestOptionalsHelpVersionActions(TestCase):
    """Test the help na version actions"""

    eleza assertPrintHelpExit(self, parser, args_str):
        ukijumuisha self.assertRaises(ArgumentParserError) as cm:
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
        ukijumuisha self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args(['-v'])
        self.assertEqual('PPP 3.5\n', cm.exception.stdout)

    eleza test_version_no_help(self):
        parser = ErrorRaisingArgumentParser(add_help=Uongo)
        parser.add_argument('-v', '--version', action='version', version='1.0')
        self.assertArgumentParserError(parser, '-h')
        self.assertArgumentParserError(parser, '--help')
        self.assertRaises(AttributeError, getattr, parser, 'format_version')

    eleza test_version_action(self):
        parser = ErrorRaisingArgumentParser(prog='XXX')
        parser.add_argument('-V', action='version', version='%(prog)s 3.7')
        ukijumuisha self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args(['-V'])
        self.assertEqual('XXX 3.7\n', cm.exception.stdout)

    eleza test_no_help(self):
        parser = ErrorRaisingArgumentParser(add_help=Uongo)
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

        # try all combinations of valid prefixes na suffixes
        valid_prefixes = ['', '-x', 'foo', '-x bar', 'baz -x']
        valid_suffixes = valid_prefixes + ['--bad-option', 'foo bar baz']
        kila prefix kwenye valid_prefixes:
            kila suffix kwenye valid_suffixes:
                format = '%s %%s %s' % (prefix, suffix)
            self.assertPrintHelpExit(parser, format % '-h')
            self.assertPrintHelpExit(parser, format % '--help')
            self.assertRaises(AttributeError, getattr, parser, 'format_version')


# ======================
# str() na repr() tests
# ======================

kundi TestStrings(TestCase):
    """Test str()  na repr() on Optionals na Positionals"""

    eleza assertStringEqual(self, obj, result_string):
        kila func kwenye [str, repr]:
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
            "nargs='+', const=Tupu, default=42, type='int', "
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
            "const=Tupu, default=2.5, type=%r, choices=[0.5, 1.5, 2.5], "
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
        ns = argparse.Namespace(**{'valid': Kweli})
        string = "Namespace(valid=Kweli)"
        self.assertStringEqual(ns, string)

    eleza test_parser(self):
        parser = argparse.ArgumentParser(prog='PROG')
        string = (
            "ArgumentParser(prog='PROG', usage=Tupu, description=Tupu, "
            "formatter_class=%r, conflict_handler='error', "
            "add_help=Kweli)" % argparse.HelpFormatter)
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
        self.assertKweli(ns1 != ns3)
        self.assertKweli(ns1 != ns4)
        self.assertKweli(ns2 != ns3)
        self.assertKweli(ns2 != ns4)

    eleza test_equality_returns_notimplemented(self):
        # See issue 21481
        ns = argparse.Namespace(a=1, b=2)
        self.assertIs(ns.__eq__(Tupu), NotImplemented)
        self.assertIs(ns.__ne__(Tupu), NotImplemented)


# ===================
# File encoding tests
# ===================

kundi TestEncoding(TestCase):

    eleza _test_module_encoding(self, path):
        path, _ = os.path.splitext(path)
        path += ".py"
        ukijumuisha open(path, 'r', encoding='utf-8') as f:
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
        error = argparse.ArgumentError(Tupu, msg)
        self.assertEqual(str(error), msg)

# =======================
# ArgumentTypeError tests
# =======================

kundi TestArgumentTypeError(TestCase):

    eleza test_argument_type_error(self):

        eleza spam(string):
             ashiria argparse.ArgumentTypeError('spam!')

        parser = ErrorRaisingArgumentParser(prog='PROG', add_help=Uongo)
        parser.add_argument('x', type=spam)
        ukijumuisha self.assertRaises(ArgumentParserError) as cm:
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
        parser.add_argument('-req_opt', type=int, required=Kweli)
        parser.add_argument('need_one', type=str, nargs='+')

        ukijumuisha self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args([])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertRegex(msg, 'req_opt')
        self.assertRegex(msg, 'need_one')
        ukijumuisha self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args(['myXargument'])
        msg = str(cm.exception)
        self.assertNotIn(msg, 'req_pos')
        self.assertRegex(msg, 'req_opt')
        self.assertRegex(msg, 'need_one')
        ukijumuisha self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args(['myXargument', '-req_opt=1'])
        msg = str(cm.exception)
        self.assertNotIn(msg, 'req_pos')
        self.assertNotIn(msg, 'req_opt')
        self.assertRegex(msg, 'need_one')

    eleza test_optional_optional_not_in_message(self):
        parser = ErrorRaisingArgumentParser(prog='PROG', usage='')
        parser.add_argument('req_pos', type=str)
        parser.add_argument('--req_opt', type=int, required=Kweli)
        parser.add_argument('--opt_opt', type=bool, nargs='?',
                            default=Kweli)
        ukijumuisha self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args([])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertRegex(msg, 'req_opt')
        self.assertNotIn(msg, 'opt_opt')
        ukijumuisha self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args(['--req_opt=1'])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertNotIn(msg, 'req_opt')
        self.assertNotIn(msg, 'opt_opt')

    eleza test_optional_positional_not_in_message(self):
        parser = ErrorRaisingArgumentParser(prog='PROG', usage='')
        parser.add_argument('req_pos')
        parser.add_argument('optional_positional', nargs='?', default='eggs')
        ukijumuisha self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args([])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertNotIn(msg, 'optional_positional')


# ================================================
# Check that the type function ni called only once
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
# Check semantics regarding the default argument na type conversion
# ==================================================================

kundi TestTypeFunctionCalledOnDefault(TestCase):

    eleza test_type_function_call_with_non_string_default(self):
        eleza spam(int_to_convert):
            self.assertEqual(int_to_convert, 0)
            rudisha 'foo_converted'

        parser = argparse.ArgumentParser()
        parser.add_argument('--foo', type=spam, default=0)
        args = parser.parse_args([])
        # foo should *not* be converted because its default ni sio a string.
        self.assertEqual(NS(foo=0), args)

    eleza test_type_function_call_with_string_default(self):
        eleza spam(int_to_convert):
            rudisha 'foo_converted'

        parser = argparse.ArgumentParser()
        parser.add_argument('--foo', type=spam, default='0')
        args = parser.parse_args([])
        # foo ni converted because its default ni a string.
        self.assertEqual(NS(foo='foo_converted'), args)

    eleza test_no_double_type_conversion_of_default(self):
        eleza extend(str_to_convert):
            rudisha str_to_convert + '*'

        parser = argparse.ArgumentParser()
        parser.add_argument('--test', type=extend, default='*')
        args = parser.parse_args([])
        # The test argument will be two stars, one coming kutoka the default
        # value na one coming kutoka the type conversion being called exactly
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
        self.assertEqual(NS(v=3, spam=Kweli, badger="B"), args)
        self.assertEqual(["C", "--foo", "4"], extras)

# ===========================
# parse_intermixed_args tests
# ===========================

kundi TestIntermixedArgs(TestCase):
    eleza test_basic(self):
        # test parsing intermixed optionals na positionals
        parser = argparse.ArgumentParser(prog='PROG')
        parser.add_argument('--foo', dest='foo')
        bar = parser.add_argument('--bar', dest='bar', required=Kweli)
        parser.add_argument('cmd')
        parser.add_argument('rest', nargs='*', type=int)
        argv = 'cmd --foo x 1 --bar y 2 3'.split()
        args = parser.parse_intermixed_args(argv)
        # rest gets [1,2,3] despite the foo na bar strings
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
        self.assertIsTupu(parser.usage)
        self.assertEqual(bar.required, Kweli)

    eleza test_remainder(self):
        # Intermixed na remainder are incompatible
        parser = ErrorRaisingArgumentParser(prog='PROG')
        parser.add_argument('-z')
        parser.add_argument('x')
        parser.add_argument('y', nargs='...')
        argv = 'X A B -z Z'.split()
        # intermixed fails ukijumuisha '...' (also 'A...')
        # self.assertRaises(TypeError, parser.parse_intermixed_args, argv)
        ukijumuisha self.assertRaises(TypeError) as cm:
            parser.parse_intermixed_args(argv)
        self.assertRegex(str(cm.exception), r'\.\.\.')

    eleza test_exclusive(self):
        # mutually exclusive group; intermixed works fine
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=Kweli)
        group.add_argument('--foo', action='store_true', help='FOO')
        group.add_argument('--spam', help='SPAM')
        parser.add_argument('badger', nargs='*', default='X', help='BADGER')
        args = parser.parse_intermixed_args('1 --foo 2'.split())
        self.assertEqual(NS(badger=['1', '2'], foo=Kweli, spam=Tupu), args)
        self.assertRaises(ArgumentParserError, parser.parse_intermixed_args, '1 2'.split())
        self.assertEqual(group.required, Kweli)

    eleza test_exclusive_incompatible(self):
        # mutually exclusive group including positional - fail
        parser = ErrorRaisingArgumentParser(prog='PROG')
        group = parser.add_mutually_exclusive_group(required=Kweli)
        group.add_argument('--foo', action='store_true', help='FOO')
        group.add_argument('--spam', help='SPAM')
        group.add_argument('badger', nargs='*', default='X', help='BADGER')
        self.assertRaises(TypeError, parser.parse_intermixed_args, [])
        self.assertEqual(group.required, Kweli)

kundi TestIntermixedMessageContentError(TestCase):
    # case where Intermixed gives different error message
    # error ni raised by 1st parsing step
    eleza test_missing_argument_name_in_message(self):
        parser = ErrorRaisingArgumentParser(prog='PROG', usage='')
        parser.add_argument('req_pos', type=str)
        parser.add_argument('-req_opt', type=int, required=Kweli)

        ukijumuisha self.assertRaises(ArgumentParserError) as cm:
            parser.parse_args([])
        msg = str(cm.exception)
        self.assertRegex(msg, 'req_pos')
        self.assertRegex(msg, 'req_opt')

        ukijumuisha self.assertRaises(ArgumentParserError) as cm:
            parser.parse_intermixed_args([])
        msg = str(cm.exception)
        self.assertNotRegex(msg, 'req_pos')
        self.assertRegex(msg, 'req_opt')

# ==========================
# add_argument metavar tests
# ==========================

kundi TestAddArgumentMetavar(TestCase):

    EXPECTED_MESSAGE = "length of metavar tuple does sio match nargs"

    eleza do_test_no_exception(self, nargs, metavar):
        parser = argparse.ArgumentParser()
        parser.add_argument("--foo", nargs=nargs, metavar=metavar)

    eleza do_test_exception(self, nargs, metavar):
        parser = argparse.ArgumentParser()
        ukijumuisha self.assertRaises(ValueError) as cm:
            parser.add_argument("--foo", nargs=nargs, metavar=metavar)
        self.assertEqual(cm.exception.args[0], self.EXPECTED_MESSAGE)

    # Unit tests kila different values of metavar when nargs=Tupu

    eleza test_nargs_Tupu_metavar_string(self):
        self.do_test_no_exception(nargs=Tupu, metavar="1")

    eleza test_nargs_Tupu_metavar_length0(self):
        self.do_test_exception(nargs=Tupu, metavar=tuple())

    eleza test_nargs_Tupu_metavar_length1(self):
        self.do_test_no_exception(nargs=Tupu, metavar=("1",))

    eleza test_nargs_Tupu_metavar_length2(self):
        self.do_test_exception(nargs=Tupu, metavar=("1", "2"))

    eleza test_nargs_Tupu_metavar_length3(self):
        self.do_test_exception(nargs=Tupu, metavar=("1", "2", "3"))

    # Unit tests kila different values of metavar when nargs=?

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

    # Unit tests kila different values of metavar when nargs=*

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

    # Unit tests kila different values of metavar when nargs=+

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

    # Unit tests kila different values of metavar when nargs=...

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

    # Unit tests kila different values of metavar when nargs=A...

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

    # Unit tests kila different values of metavar when nargs=1

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

    # Unit tests kila different values of metavar when nargs=2

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

    # Unit tests kila different values of metavar when nargs=3

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
    EXPECTED_RANGE_MESSAGE = ("nargs kila store actions must be != 0; ikiwa you "
                              "have nothing to store, actions such as store "
                              "true ama store const may be more appropriate")

    eleza do_test_range_exception(self, nargs):
        parser = argparse.ArgumentParser()
        ukijumuisha self.assertRaises(ValueError) as cm:
            parser.add_argument("--foo", nargs=nargs)
        self.assertEqual(cm.exception.args[0], self.EXPECTED_RANGE_MESSAGE)

    eleza do_test_invalid_exception(self, nargs):
        parser = argparse.ArgumentParser()
        ukijumuisha self.assertRaises(ValueError) as cm:
            parser.add_argument("--foo", nargs=nargs)
        self.assertEqual(cm.exception.args[0], self.EXPECTED_INVALID_MESSAGE)

    # Unit tests kila different values of nargs

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
        kila name kwenye argparse.__all__:
            self.assertKweli(hasattr(argparse, name))

    eleza test_all_exports_everything_but_modules(self):
        items = [
            name
            kila name, value kwenye vars(argparse).items()
            ikiwa sio (name.startswith("_") ama name == 'ngettext')
            ikiwa sio inspect.ismodule(value)
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
              -h, --help            show this help message na exit
              --proxy <http[s]://example:1234>
            '''))


eleza test_main():
    support.run_unittest(__name__)
    # Remove global references to avoid looking like we have refleaks.
    RFile.seen = {}
    WFile.seen = set()



ikiwa __name__ == '__main__':
    test_main()
