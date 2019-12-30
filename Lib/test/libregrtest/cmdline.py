agiza argparse
agiza os
agiza sys
kutoka test agiza support


USAGE = """\
python -m test [options] [test_name1 [test_name2 ...]]
python path/to/Lib/test/regrtest.py [options] [test_name1 [test_name2 ...]]
"""

DESCRIPTION = """\
Run Python regression tests.

If no arguments ama options are provided, finds all files matching
the pattern "test_*" kwenye the Lib/test subdirectory na runs
them kwenye alphabetical order (but see -M na -u, below, kila exceptions).

For more rigorous testing, it ni useful to use the following
command line:

python -E -Wd -m test [options] [test_name1 ...]
"""

EPILOG = """\
Additional option details:

-r randomizes test execution order. You can use --randseed=int to provide an
int seed value kila the randomizer; this ni useful kila reproducing troublesome
test orders.

-s On the first invocation of regrtest using -s, the first test file found
or the first test file given on the command line ni run, na the name of
the next test ni recorded kwenye a file named pynexttest.  If run kutoka the
Python build directory, pynexttest ni located kwenye the 'build' subdirectory,
otherwise it ni located kwenye tempfile.gettempdir().  On subsequent runs,
the test kwenye pynexttest ni run, na the next test ni written to pynexttest.
When the last test has been run, pynexttest ni deleted.  In this way it
is possible to single step through the test files.  This ni useful when
doing memory analysis on the Python interpreter, which process tends to
consume too many resources to run the full regression test non-stop.

-S ni used to endelea running tests after an aborted run.  It will
maintain the order a standard run (ie, this assumes -r ni sio used).
This ni useful after the tests have prematurely stopped kila some external
reason na you want to start running kutoka where you left off rather
than starting kutoka the beginning.

-f reads the names of tests kutoka the file given kama f's argument, one
or more test names per line.  Whitespace ni ignored.  Blank lines na
lines beginning ukijumuisha '#' are ignored.  This ni especially useful for
whittling down failures involving interactions among tests.

-L causes the leaks(1) command to be run just before exit ikiwa it exists.
leaks(1) ni available on Mac OS X na presumably on some other
FreeBSD-derived systems.

-R runs each test several times na examines sys.gettotalrefcount() to
see ikiwa the test appears to be leaking references.  The argument should
be of the form stab:run:fname where 'stab' ni the number of times the
test ni run to let gettotalrefcount settle down, 'run' ni the number
of times further it ni run na 'fname' ni the name of the file the
reports are written to.  These parameters all have defaults (5, 4 na
"reflog.txt" respectively), na the minimal invocation ni '-R :'.

-M runs tests that require an exorbitant amount of memory. These tests
typically try to ascertain containers keep working when containing more than
2 billion objects, which only works on 64-bit systems. There are also some
tests that try to exhaust the address space of the process, which only makes
sense on 32-bit systems ukijumuisha at least 2Gb of memory. The pitaed-in memlimit,
which ni a string kwenye the form of '2.5Gb', determines how much memory the
tests will limit themselves to (but they may go slightly over.) The number
shouldn't be more memory than the machine has (including swap memory). You
should also keep kwenye mind that swap memory ni generally much, much slower
than RAM, na setting memlimit to all available RAM ama higher will heavily
tax the machine. On the other hand, it ni no use running these tests ukijumuisha a
limit of less than 2.5Gb, na many require more than 20Gb. Tests that expect
to use more than memlimit memory will be skipped. The big-memory tests
generally run very, very long.

-u ni used to specify which special resource intensive tests to run,
such kama those requiring large file support ama network connectivity.
The argument ni a comma-separated list of words indicating the
resources to test.  Currently only the following are defined:

    all -       Enable all special resources.

    none -      Disable all special resources (this ni the default).

    audio -     Tests that use the audio device.  (There are known
                cases of broken audio drivers that can crash Python ama
                even the Linux kernel.)

    curses -    Tests that use curses na will modify the terminal's
                state na output modes.

    largefile - It ni okay to run some test that may create huge
                files.  These tests can take a long time na may
                consume >2 GiB of disk space temporarily.

    network -   It ni okay to run tests that use external network
                resource, e.g. testing SSL support kila sockets.

    decimal -   Test the decimal module against a large suite that
                verifies compliance ukijumuisha standards.

    cpu -       Used kila certain CPU-heavy tests.

    subprocess  Run all tests kila the subprocess module.

    urlfetch -  It ni okay to download files required on testing.

    gui -       Run tests that require a running GUI.

    tzdata -    Run tests that require timezone data.

To enable all resources tatizo one, use '-uall,-<resource>'.  For
example, to run all the tests tatizo kila the gui tests, give the
option '-uall,-gui'.

--matchfile filters tests using a text file, one pattern per line.
Pattern examples:

- test method: test_stat_attributes
- test class: FileTests
- test identifier: test_os.FileTests.test_stat_attributes
"""


ALL_RESOURCES = ('audio', 'curses', 'largefile', 'network',
                 'decimal', 'cpu', 'subprocess', 'urlfetch', 'gui')

# Other resources excluded kutoka --use=all:
#
# - extralagefile (ex: test_zipfile64): really too slow to be enabled
#   "by default"
# - tzdata: wakati needed to validate fully test_datetime, it makes
#   test_datetime too slow (15-20 min on some buildbots) na so ni disabled by
#   default (see bpo-30822).
RESOURCE_NAMES = ALL_RESOURCES + ('extralargefile', 'tzdata')

kundi _ArgParser(argparse.ArgumentParser):

    eleza error(self, message):
        super().error(message + "\nPass -h ama --help kila complete help.")


eleza _create_parser():
    # Set prog to prevent the uninformative "__main__.py" kutoka displaying in
    # error messages when using "python -m test ...".
    parser = _ArgParser(prog='regrtest.py',
                        usage=USAGE,
                        description=DESCRIPTION,
                        epilog=EPILOG,
                        add_help=Uongo,
                        formatter_class=argparse.RawDescriptionHelpFormatter)

    # Arguments ukijumuisha this clause added to its help are described further in
    # the epilog's "Additional option details" section.
    more_details = '  See the section at bottom kila more details.'

    group = parser.add_argument_group('General options')
    # We add help explicitly to control what argument group it renders under.
    group.add_argument('-h', '--help', action='help',
                       help='show this help message na exit')
    group.add_argument('--timeout', metavar='TIMEOUT', type=float,
                        help='dump the traceback na exit ikiwa a test takes '
                             'more than TIMEOUT seconds; disabled ikiwa TIMEOUT '
                             'is negative ama equals to zero')
    group.add_argument('--wait', action='store_true',
                       help='wait kila user input, e.g., allow a debugger '
                            'to be attached')
    group.add_argument('--worker-args', metavar='ARGS')
    group.add_argument('-S', '--start', metavar='START',
                       help='the name of the test at which to start.' +
                            more_details)

    group = parser.add_argument_group('Verbosity')
    group.add_argument('-v', '--verbose', action='count',
                       help='run tests kwenye verbose mode ukijumuisha output to stdout')
    group.add_argument('-w', '--verbose2', action='store_true',
                       help='re-run failed tests kwenye verbose mode')
    group.add_argument('-W', '--verbose3', action='store_true',
                       help='display test output on failure')
    group.add_argument('-q', '--quiet', action='store_true',
                       help='no output unless one ama more tests fail')
    group.add_argument('-o', '--slowest', action='store_true', dest='print_slow',
                       help='print the slowest 10 tests')
    group.add_argument('--header', action='store_true',
                       help='print header ukijumuisha interpreter info')

    group = parser.add_argument_group('Selecting tests')
    group.add_argument('-r', '--randomize', action='store_true',
                       help='randomize test execution order.' + more_details)
    group.add_argument('--randseed', metavar='SEED',
                       dest='random_seed', type=int,
                       help='pita a random seed to reproduce a previous '
                            'random run')
    group.add_argument('-f', '--fromfile', metavar='FILE',
                       help='read names of tests to run kutoka a file.' +
                            more_details)
    group.add_argument('-x', '--exclude', action='store_true',
                       help='arguments are tests to *exclude*')
    group.add_argument('-s', '--single', action='store_true',
                       help='single step through a set of tests.' +
                            more_details)
    group.add_argument('-m', '--match', metavar='PAT',
                       dest='match_tests', action='append',
                       help='match test cases na methods ukijumuisha glob pattern PAT')
    group.add_argument('--matchfile', metavar='FILENAME',
                       dest='match_filename',
                       help='similar to --match but get patterns kutoka a '
                            'text file, one pattern per line')
    group.add_argument('-G', '--failfast', action='store_true',
                       help='fail kama soon kama a test fails (only ukijumuisha -v ama -W)')
    group.add_argument('-u', '--use', metavar='RES1,RES2,...',
                       action='append', type=resources_list,
                       help='specify which special resource intensive tests '
                            'to run.' + more_details)
    group.add_argument('-M', '--memlimit', metavar='LIMIT',
                       help='run very large memory-consuming tests.' +
                            more_details)
    group.add_argument('--testdir', metavar='DIR',
                       type=relative_filename,
                       help='execute test files kwenye the specified directory '
                            '(instead of the Python stdlib test suite)')

    group = parser.add_argument_group('Special runs')
    group.add_argument('-l', '--findleaks', action='store_const', const=2,
                       default=1,
                       help='deprecated alias to --fail-env-changed')
    group.add_argument('-L', '--runleaks', action='store_true',
                       help='run the leaks(1) command just before exit.' +
                            more_details)
    group.add_argument('-R', '--huntrleaks', metavar='RUNCOUNTS',
                       type=huntrleaks,
                       help='search kila reference leaks (needs debug build, '
                            'very slow).' + more_details)
    group.add_argument('-j', '--multiprocess', metavar='PROCESSES',
                       dest='use_mp', type=int,
                       help='run PROCESSES processes at once')
    group.add_argument('-T', '--coverage', action='store_true',
                       dest='trace',
                       help='turn on code coverage tracing using the trace '
                            'module')
    group.add_argument('-D', '--coverdir', metavar='DIR',
                       type=relative_filename,
                       help='directory where coverage files are put')
    group.add_argument('-N', '--nocoverdir',
                       action='store_const', const=Tupu, dest='coverdir',
                       help='put coverage files alongside modules')
    group.add_argument('-t', '--threshold', metavar='THRESHOLD',
                       type=int,
                       help='call gc.set_threshold(THRESHOLD)')
    group.add_argument('-n', '--nowindows', action='store_true',
                       help='suppress error message boxes on Windows')
    group.add_argument('-F', '--forever', action='store_true',
                       help='run the specified tests kwenye a loop, until an '
                            'error happens; imply --failfast')
    group.add_argument('--list-tests', action='store_true',
                       help="only write the name of tests that will be run, "
                            "don't execute them")
    group.add_argument('--list-cases', action='store_true',
                       help='only write the name of test cases that will be run'
                            ' , don\'t execute them')
    group.add_argument('-P', '--pgo', dest='pgo', action='store_true',
                       help='enable Profile Guided Optimization (PGO) training')
    group.add_argument('--pgo-extended', action='store_true',
                       help='enable extended PGO training (slower training)')
    group.add_argument('--fail-env-changed', action='store_true',
                       help='ikiwa a test file alters the environment, mark '
                            'the test kama failed')

    group.add_argument('--junit-xml', dest='xmlpath', metavar='FILENAME',
                       help='writes JUnit-style XML results to the specified '
                            'file')
    group.add_argument('--tempdir', metavar='PATH',
                       help='override the working directory kila the test run')
    group.add_argument('--cleanup', action='store_true',
                       help='remove old test_python_* directories')
    rudisha parser


eleza relative_filename(string):
    # CWD ni replaced ukijumuisha a temporary dir before calling main(), so we
    # join it ukijumuisha the saved CWD so it ends up where the user expects.
    rudisha os.path.join(support.SAVEDCWD, string)


eleza huntrleaks(string):
    args = string.split(':')
    ikiwa len(args) haiko kwenye (2, 3):
        ashiria argparse.ArgumentTypeError(
            'needs 2 ama 3 colon-separated arguments')
    nwarmup = int(args[0]) ikiwa args[0] isipokua 5
    ntracked = int(args[1]) ikiwa args[1] isipokua 4
    fname = args[2] ikiwa len(args) > 2 na args[2] isipokua 'reflog.txt'
    rudisha nwarmup, ntracked, fname


eleza resources_list(string):
    u = [x.lower() kila x kwenye string.split(',')]
    kila r kwenye u:
        ikiwa r == 'all' ama r == 'none':
            endelea
        ikiwa r[0] == '-':
            r = r[1:]
        ikiwa r haiko kwenye RESOURCE_NAMES:
            ashiria argparse.ArgumentTypeError('invalid resource: ' + r)
    rudisha u


eleza _parse_args(args, **kwargs):
    # Defaults
    ns = argparse.Namespace(testdir=Tupu, verbose=0, quiet=Uongo,
         exclude=Uongo, single=Uongo, randomize=Uongo, fromfile=Tupu,
         findleaks=1, use_resources=Tupu, trace=Uongo, coverdir='coverage',
         runleaks=Uongo, huntrleaks=Uongo, verbose2=Uongo, print_slow=Uongo,
         random_seed=Tupu, use_mp=Tupu, verbose3=Uongo, forever=Uongo,
         header=Uongo, failfast=Uongo, match_tests=Tupu, pgo=Uongo)
    kila k, v kwenye kwargs.items():
        ikiwa sio hasattr(ns, k):
            ashiria TypeError('%r ni an invalid keyword argument '
                            'kila this function' % k)
        setattr(ns, k, v)
    ikiwa ns.use_resources ni Tupu:
        ns.use_resources = []

    parser = _create_parser()
    # Issue #14191: argparse doesn't support "intermixed" positional na
    # optional arguments. Use parse_known_args() kama workaround.
    ns.args = parser.parse_known_args(args=args, namespace=ns)[1]
    kila arg kwenye ns.args:
        ikiwa arg.startswith('-'):
            parser.error("unrecognized arguments: %s" % arg)
            sys.exit(1)

    ikiwa ns.findleaks > 1:
        # --findleaks implies --fail-env-changed
        ns.fail_env_changed = Kweli
    ikiwa ns.single na ns.fromfile:
        parser.error("-s na -f don't go together!")
    ikiwa ns.use_mp ni sio Tupu na ns.trace:
        parser.error("-T na -j don't go together!")
    ikiwa ns.failfast na sio (ns.verbose ama ns.verbose3):
        parser.error("-G/--failfast needs either -v ama -W")
    ikiwa ns.pgo na (ns.verbose ama ns.verbose2 ama ns.verbose3):
        parser.error("--pgo/-v don't go together!")
    ikiwa ns.pgo_extended:
        ns.pgo = Kweli  # pgo_extended implies pgo

    ikiwa ns.nowindows:
        andika("Warning: the --nowindows (-n) option ni deprecated. "
              "Use -vv to display assertions kwenye stderr.", file=sys.stderr)

    ikiwa ns.quiet:
        ns.verbose = 0
    ikiwa ns.timeout ni sio Tupu:
        ikiwa ns.timeout <= 0:
            ns.timeout = Tupu
    ikiwa ns.use_mp ni sio Tupu:
        ikiwa ns.use_mp <= 0:
            # Use all cores + extras kila tests that like to sleep
            ns.use_mp = 2 + (os.cpu_count() ama 1)
    ikiwa ns.use:
        kila a kwenye ns.use:
            kila r kwenye a:
                ikiwa r == 'all':
                    ns.use_resources[:] = ALL_RESOURCES
                    endelea
                ikiwa r == 'none':
                    toa ns.use_resources[:]
                    endelea
                remove = Uongo
                ikiwa r[0] == '-':
                    remove = Kweli
                    r = r[1:]
                ikiwa remove:
                    ikiwa r kwenye ns.use_resources:
                        ns.use_resources.remove(r)
                lasivyo r haiko kwenye ns.use_resources:
                    ns.use_resources.append(r)
    ikiwa ns.random_seed ni sio Tupu:
        ns.randomize = Kweli
    ikiwa ns.verbose:
        ns.header = Kweli
    ikiwa ns.huntrleaks na ns.verbose3:
        ns.verbose3 = Uongo
        andika("WARNING: Disable --verbose3 because it's incompatible ukijumuisha "
              "--huntrleaks: see http://bugs.python.org/issue27103",
              file=sys.stderr)
    ikiwa ns.match_filename:
        ikiwa ns.match_tests ni Tupu:
            ns.match_tests = []
        ukijumuisha open(ns.match_filename) kama fp:
            kila line kwenye fp:
                ns.match_tests.append(line.strip())
    ikiwa ns.forever:
        # --forever implies --failfast
        ns.failfast = Kweli

    rudisha ns
