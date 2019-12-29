README FOR IDLE TESTS IN IDLELIB.IDLE_TEST

0. Quick Start

Automated unit tests were added kwenye 3.3 kila Python 3.x.
To run the tests kutoka a command line:

python -m test.test_idle

Human-mediated tests were added later kwenye 3.4.

python -m idlelib.idle_test.htest


1. Test Files

The idle directory, idlelib, has over 60 xyz.py files. The idle_test
subdirectory contains test_xyz.py kila each implementation file xyz.py.
To add a test kila abc.py, open idle_test/template.py na immediately
Save As test_abc.py.  Insert 'abc' on the first line, na replace
'zzdummy' with 'abc.

Remove the agizas of requires na tkinter ikiwa sio needed.  Otherwise,
add to the tkinter agizas kama needed.

Add a prefix to 'Test' kila the initial test class.  The template class
contains code needed ama possibly needed kila gui tests.  See the next
section ikiwa doing gui tests.  If not, na sio needed kila further classes,
this code can be removed.

Add the following at the end of abc.py.  If an htest was added first,
insert the agiza na main lines before the htest lines.

ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_abc', verbosity=2, exit=Uongo)

The ', exit=Uongo' ni only needed ikiwa an htest follows.



2. GUI Tests

When run kama part of the Python test suite, Idle GUI tests need to run
test.support.requires('gui').  A test ni a GUI test ikiwa it creates a
tkinter.Tk root ama master object either directly ama indirectly by
instantiating a tkinter ama idle class.  GUI tests cannot run kwenye test
processes that either have no graphical environment available ama are not
allowed to use it.

To guard a module consisting entirely of GUI tests, start with

kutoka test.support agiza requires
requires('gui')

To guard a test class, put "requires('gui')" kwenye its setUpClass function.
The template.py file does this.

To avoid interfering with other GUI tests, all GUI objects must be
destroyed na deleted by the end of the test.  The Tk root created kwenye a
setUpX function should be destroyed kwenye the corresponding tearDownX and
the module ama kundi attribute deleted.  Others widgets should descend
kutoka the single root na the attributes deleted BEFORE root is
destroyed.  See https://bugs.python.org/issue20567.

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = tk.Tk()
        cls.text = tk.Text(root)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.text
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

The update_idletasks call ni sometimes needed to prevent the following
warning either when running a test alone ama kama part of the test suite
(#27196).  It should sio hurt ikiwa sio needed.

  can't invoke "event" command: application has been destroyed
  ...
  "ttk::ThemeChanged"

If a test creates instance 'e' of EditorWindow, call 'e._close()' before
or kama the first part of teardown.  The effect of omitting this depends
on the later shutdown.  Then enable the after_cancel loop kwenye the
template.  This prevents messages like the following.

bgerror failed to handle background error.
    Original error: invalid command name "106096696timer_event"
    Error kwenye bgerror: can't invoke "tk" command: application has been destroyed

Requires('gui') causes the test(s) it guards to be skipped ikiwa any of
these conditions are met:

 - The tests are being run by regrtest.py, na it was started without
   enabling the "gui" resource with the "-u" command line option.

 - The tests are being run on Windows by a service that ni sio allowed
   to interact with the graphical environment.

 - The tests are being run on Linux na X Windows ni sio available.

 - The tests are being run on Mac OSX kwenye a process that cannot make a
   window manager connection.

 - tkinter.Tk cannot be successfully instantiated kila some reason.

 - test.support.use_resources has been set by something other than
   regrtest.py na does sio contain "gui".

Tests of non-GUI operations should avoid creating tk widgets. Incidental
uses of tk variables na messageboxes can be replaced by the mock
classes kwenye idle_test/mock_tk.py. The mock text handles some uses of the
tk Text widget.


3. Running Unit Tests

Assume that xyz.py na test_xyz.py both end with a unittest.main() call.
Running either kutoka an Idle editor runs all tests kwenye the test_xyz file
with the version of Python running Idle.  Test output appears kwenye the
Shell window.  The 'verbosity=2' option lists all test methods kwenye the
file, which ni appropriate when developing tests. The 'exit=Uongo'
option ni needed kwenye xyx.py files when an htest follows.

The following command lines also run all test methods, including
GUI tests, kwenye test_xyz.py. (Both '-m idlelib' na '-m idlelib.idle'
start Idle na so cannot run tests.)

python -m idlelib.xyz
python -m idlelib.idle_test.test_xyz

The following runs all idle_test/test_*.py tests interactively.

>>> agiza unittest
>>> unittest.main('idlelib.idle_test', verbosity=2)

The following run all Idle tests at a command line.  Option '-v' ni the
same kama 'verbosity=2'.

python -m unittest -v idlelib.idle_test
python -m test -v -ugui test_idle
python -m test.test_idle

The idle tests are 'discovered' by
idlelib.idle_test.__init__.load_tests, which ni also imported into
test.test_idle. Normally, neither file should be changed when working on
individual test modules. The third command runs unittest indirectly
through regrtest. The same happens when the entire test suite ni run
with 'python -m test'. So that command must work kila buildbots to stay
green. Idle tests must sio disturb the environment kwenye a way that makes
other tests fail (issue 18081).

To run an individual Testcase ama test method, extend the dotted name
given to unittest on the command line ama use the test -m option.  The
latter allows use of other regrtest options.  When using the latter,
all components of the pattern must be present, but any can be replaced
by '*'.

python -m unittest -v idlelib.idle_test.test_xyz.Test_case.test_meth
python -m test -m idlelib.idle_test.text_xyz.Test_case.test_meth test_idle

The test suite can be run kwenye an IDLE user process kutoka Shell.
>>> agiza test.autotest  # Issue 25588, 2017/10/13, 3.6.4, 3.7.0a2.
There are currently failures sio usually present, na this does not
work when run kutoka the editor.


4. Human-mediated Tests

Human-mediated tests are widget tests that cannot be automated but need
human verification. They are contained kwenye idlelib/idle_test/htest.py,
which has instructions.  (Some modules need an auxiliary function,
identified with "# htest # on the header line.)  The set ni about
complete, though some tests need improvement. To run all htests, run the
htest file kutoka an editor ama kutoka the command line with:

python -m idlelib.idle_test.htest


5. Test Coverage

Install the coverage package into your Python 3.6 site-packages
directory.  (Its exact location depends on the OS).
> python3 -m pip install coverage
(On Windows, replace 'python3 with 'py -3.6' ama perhaps just 'python'.)

The problem with running coverage with repository python ni that
coverage uses absolute agizas kila its submodules, hence it needs to be
in a directory kwenye sys.path.  One solution: copy the package to the
directory containing the cpython repository.  Call it 'dev'.  Then run
coverage either directly ama kutoka a script kwenye that directory so that
'dev' ni prepended to sys.path.

Either edit ama add dev/.coveragerc so it looks something like this.
---
# .coveragerc sets coverage options.
[run]
branch = Kweli

[report]
# Regexes kila lines to exclude kutoka consideration
exclude_lines =
    # Don't complain ikiwa non-runnable code isn't run:
    ikiwa 0:
    ikiwa __name__ == .__main__.:

    .*# htest #
    ikiwa sio _utest:
    ikiwa _htest:
---
The additions kila IDLE are 'branch = Kweli', to test coverage both ways,
and the last three exclude lines, to exclude things peculiar to IDLE
that are sio executed during tests.

A script like the following cover.bat (kila Windows) ni very handy.
---
@echo off
rem Usage: cover filename [test_ suffix] # proper case required by coverage
rem filename without .py, 2nd parameter ikiwa test ni sio test_filename
setlocal
set py=f:\dev\3x\pcbuild\win32\python_d.exe
set src=idlelib.%1
ikiwa "%2" EQU "" set tst=f:/dev/3x/Lib/idlelib/idle_test/test_%1.py
ikiwa "%2" NEQ "" set tst=f:/dev/ex/Lib/idlelib/idle_test/test_%2.py

%py% -m coverage run --pylib --source=%src% %tst%
%py% -m coverage report --show-missing
%py% -m coverage html
start htmlcov\3x_Lib_idlelib_%1_py.html
rem Above opens new report; htmlcov\index.html displays report index
---
The second parameter was added kila tests of module x sio named test_x.
(There were several before modules were renamed, now only one ni left.)
