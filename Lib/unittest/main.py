"""Unittest main program"""

agiza sys
agiza argparse
agiza os

kutoka . agiza loader, runner
kutoka .signals agiza installHandler

__unittest = Kweli

MAIN_EXAMPLES = """\
Examples:
  %(prog)s test_module               - run tests kutoka test_module
  %(prog)s module.TestClass          - run tests kutoka module.TestClass
  %(prog)s module.Class.test_method  - run specified test method
  %(prog)s path/to/test_file.py      - run tests kutoka test_file.py
"""

MODULE_EXAMPLES = """\
Examples:
  %(prog)s                           - run default set of tests
  %(prog)s MyTestSuite               - run suite 'MyTestSuite'
  %(prog)s MyTestCase.testSomething  - run MyTestCase.testSomething
  %(prog)s MyTestCase                - run all 'test*' test methods
                                       kwenye MyTestCase
"""

eleza _convert_name(name):
    # on Linux / Mac OS X 'foo.PY' ni sio agizaable, but on
    # Windows it is. Simpler to do a case insensitive match
    # a better check would be to check that the name ni a
    # valid Python module name.
    ikiwa os.path.isfile(name) na name.lower().endswith('.py'):
        ikiwa os.path.isabs(name):
            rel_path = os.path.relpath(name, os.getcwd())
            ikiwa os.path.isabs(rel_path) ama rel_path.startswith(os.pardir):
                rudisha name
            name = rel_path
        # on Windows both '\' na '/' are used kama path
        # separators. Better to replace both than rely on os.path.sep
        rudisha name[:-3].replace('\\', '.').replace('/', '.')
    rudisha name

eleza _convert_names(names):
    rudisha [_convert_name(name) kila name kwenye names]


eleza _convert_select_pattern(pattern):
    ikiwa sio '*' kwenye pattern:
        pattern = '*%s*' % pattern
    rudisha pattern


kundi TestProgram(object):
    """A command-line program that runs a set of tests; this ni primarily
       kila making test modules conveniently executable.
    """
    # defaults kila testing
    module=Tupu
    verbosity = 1
    failfast = catchkoma = buffer = progName = warnings = testNamePatterns = Tupu
    _discovery_parser = Tupu

    eleza __init__(self, module='__main__', defaultTest=Tupu, argv=Tupu,
                    testRunner=Tupu, testLoader=loader.defaultTestLoader,
                    exit=Kweli, verbosity=1, failfast=Tupu, catchkoma=Tupu,
                    buffer=Tupu, warnings=Tupu, *, tb_locals=Uongo):
        ikiwa isinstance(module, str):
            self.module = __import__(module)
            kila part kwenye module.split('.')[1:]:
                self.module = getattr(self.module, part)
        isipokua:
            self.module = module
        ikiwa argv ni Tupu:
            argv = sys.argv

        self.exit = exit
        self.failfast = failfast
        self.catchkoma = catchkoma
        self.verbosity = verbosity
        self.buffer = buffer
        self.tb_locals = tb_locals
        ikiwa warnings ni Tupu na sio sys.warnoptions:
            # even ikiwa DeprecationWarnings are ignored by default
            # print them anyway unless other warnings settings are
            # specified by the warnings arg ama the -W python flag
            self.warnings = 'default'
        isipokua:
            # here self.warnings ni set either to the value pitaed
            # to the warnings args ama to Tupu.
            # If the user didn't pita a value self.warnings will
            # be Tupu. This means that the behavior ni unchanged
            # na depends on the values pitaed to -W.
            self.warnings = warnings
        self.defaultTest = defaultTest
        self.testRunner = testRunner
        self.testLoader = testLoader
        self.progName = os.path.basename(argv[0])
        self.parseArgs(argv)
        self.runTests()

    eleza usageExit(self, msg=Tupu):
        ikiwa msg:
            andika(msg)
        ikiwa self._discovery_parser ni Tupu:
            self._initArgParsers()
        self._print_help()
        sys.exit(2)

    eleza _print_help(self, *args, **kwargs):
        ikiwa self.module ni Tupu:
            andika(self._main_parser.format_help())
            andika(MAIN_EXAMPLES % {'prog': self.progName})
            self._discovery_parser.print_help()
        isipokua:
            andika(self._main_parser.format_help())
            andika(MODULE_EXAMPLES % {'prog': self.progName})

    eleza parseArgs(self, argv):
        self._initArgParsers()
        ikiwa self.module ni Tupu:
            ikiwa len(argv) > 1 na argv[1].lower() == 'discover':
                self._do_discovery(argv[2:])
                rudisha
            self._main_parser.parse_args(argv[1:], self)
            ikiwa sio self.tests:
                # this allows "python -m unittest -v" to still work for
                # test discovery.
                self._do_discovery([])
                rudisha
        isipokua:
            self._main_parser.parse_args(argv[1:], self)

        ikiwa self.tests:
            self.testNames = _convert_names(self.tests)
            ikiwa __name__ == '__main__':
                # to support python -m unittest ...
                self.module = Tupu
        elikiwa self.defaultTest ni Tupu:
            # createTests will load tests kutoka self.module
            self.testNames = Tupu
        elikiwa isinstance(self.defaultTest, str):
            self.testNames = (self.defaultTest,)
        isipokua:
            self.testNames = list(self.defaultTest)
        self.createTests()

    eleza createTests(self, kutoka_discovery=Uongo, Loader=Tupu):
        ikiwa self.testNamePatterns:
            self.testLoader.testNamePatterns = self.testNamePatterns
        ikiwa kutoka_discovery:
            loader = self.testLoader ikiwa Loader ni Tupu else Loader()
            self.test = loader.discover(self.start, self.pattern, self.top)
        elikiwa self.testNames ni Tupu:
            self.test = self.testLoader.loadTestsFromModule(self.module)
        isipokua:
            self.test = self.testLoader.loadTestsFromNames(self.testNames,
                                                           self.module)

    eleza _initArgParsers(self):
        parent_parser = self._getParentArgParser()
        self._main_parser = self._getMainArgParser(parent_parser)
        self._discovery_parser = self._getDiscoveryArgParser(parent_parser)

    eleza _getParentArgParser(self):
        parser = argparse.ArgumentParser(add_help=Uongo)

        parser.add_argument('-v', '--verbose', dest='verbosity',
                            action='store_const', const=2,
                            help='Verbose output')
        parser.add_argument('-q', '--quiet', dest='verbosity',
                            action='store_const', const=0,
                            help='Quiet output')
        parser.add_argument('--locals', dest='tb_locals',
                            action='store_true',
                            help='Show local variables kwenye tracebacks')
        ikiwa self.failfast ni Tupu:
            parser.add_argument('-f', '--failfast', dest='failfast',
                                action='store_true',
                                help='Stop on first fail ama error')
            self.failfast = Uongo
        ikiwa self.catchkoma ni Tupu:
            parser.add_argument('-c', '--catch', dest='catchkoma',
                                action='store_true',
                                help='Catch Ctrl-C na display results so far')
            self.catchkoma = Uongo
        ikiwa self.buffer ni Tupu:
            parser.add_argument('-b', '--buffer', dest='buffer',
                                action='store_true',
                                help='Buffer stdout na stderr during tests')
            self.buffer = Uongo
        ikiwa self.testNamePatterns ni Tupu:
            parser.add_argument('-k', dest='testNamePatterns',
                                action='append', type=_convert_select_pattern,
                                help='Only run tests which match the given substring')
            self.testNamePatterns = []

        rudisha parser

    eleza _getMainArgParser(self, parent):
        parser = argparse.ArgumentParser(parents=[parent])
        parser.prog = self.progName
        parser.print_help = self._print_help

        parser.add_argument('tests', nargs='*',
                            help='a list of any number of test modules, '
                            'classes na test methods.')

        rudisha parser

    eleza _getDiscoveryArgParser(self, parent):
        parser = argparse.ArgumentParser(parents=[parent])
        parser.prog = '%s discover' % self.progName
        parser.epilog = ('For test discovery all test modules must be '
                         'agizaable kutoka the top level directory of the '
                         'project.')

        parser.add_argument('-s', '--start-directory', dest='start',
                            help="Directory to start discovery ('.' default)")
        parser.add_argument('-p', '--pattern', dest='pattern',
                            help="Pattern to match tests ('test*.py' default)")
        parser.add_argument('-t', '--top-level-directory', dest='top',
                            help='Top level directory of project (defaults to '
                                 'start directory)')
        kila arg kwenye ('start', 'pattern', 'top'):
            parser.add_argument(arg, nargs='?',
                                default=argparse.SUPPRESS,
                                help=argparse.SUPPRESS)

        rudisha parser

    eleza _do_discovery(self, argv, Loader=Tupu):
        self.start = '.'
        self.pattern = 'test*.py'
        self.top = Tupu
        ikiwa argv ni sio Tupu:
            # handle command line args kila test discovery
            ikiwa self._discovery_parser ni Tupu:
                # kila testing
                self._initArgParsers()
            self._discovery_parser.parse_args(argv, self)

        self.createTests(kutoka_discovery=Kweli, Loader=Loader)

    eleza runTests(self):
        ikiwa self.catchkoma:
            installHandler()
        ikiwa self.testRunner ni Tupu:
            self.testRunner = runner.TextTestRunner
        ikiwa isinstance(self.testRunner, type):
            jaribu:
                jaribu:
                    testRunner = self.testRunner(verbosity=self.verbosity,
                                                 failfast=self.failfast,
                                                 buffer=self.buffer,
                                                 warnings=self.warnings,
                                                 tb_locals=self.tb_locals)
                tatizo TypeError:
                    # didn't accept the tb_locals argument
                    testRunner = self.testRunner(verbosity=self.verbosity,
                                                 failfast=self.failfast,
                                                 buffer=self.buffer,
                                                 warnings=self.warnings)
            tatizo TypeError:
                # didn't accept the verbosity, buffer ama failfast arguments
                testRunner = self.testRunner()
        isipokua:
            # it ni assumed to be a TestRunner instance
            testRunner = self.testRunner
        self.result = testRunner.run(self.test)
        ikiwa self.exit:
            sys.exit(not self.result.wasSuccessful())

main = TestProgram
