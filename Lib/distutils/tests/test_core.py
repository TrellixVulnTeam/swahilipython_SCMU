"""Tests kila distutils.core."""

agiza io
agiza distutils.core
agiza os
agiza shutil
agiza sys
agiza test.support
kutoka test.support agiza captured_stdout, run_unittest
agiza unittest
kutoka distutils.tests agiza support
kutoka distutils agiza log

# setup script that uses __file__
setup_using___file__ = """\

__file__

kutoka distutils.core agiza setup
setup()
"""

setup_prints_cwd = """\

agiza os
andika(os.getcwd())

kutoka distutils.core agiza setup
setup()
"""

setup_does_nothing = """\
kutoka distutils.core agiza setup
setup()
"""


setup_defines_subkundi = """\
kutoka distutils.core agiza setup
kutoka distutils.command.install agiza install kama _install

kundi install(_install):
    sub_commands = _install.sub_commands + ['cmd']

setup(cmdclass={'install': install})
"""

kundi CoreTestCase(support.EnvironGuard, unittest.TestCase):

    eleza setUp(self):
        super(CoreTestCase, self).setUp()
        self.old_stdout = sys.stdout
        self.cleanup_testfn()
        self.old_argv = sys.argv, sys.argv[:]
        self.addCleanup(log.set_threshold, log._global_log.threshold)

    eleza tearDown(self):
        sys.stdout = self.old_stdout
        self.cleanup_testfn()
        sys.argv = self.old_argv[0]
        sys.argv[:] = self.old_argv[1]
        super(CoreTestCase, self).tearDown()

    eleza cleanup_testfn(self):
        path = test.support.TESTFN
        ikiwa os.path.isfile(path):
            os.remove(path)
        lasivyo os.path.isdir(path):
            shutil.rmtree(path)

    eleza write_setup(self, text, path=test.support.TESTFN):
        f = open(path, "w")
        jaribu:
            f.write(text)
        mwishowe:
            f.close()
        rudisha path

    eleza test_run_setup_provides_file(self):
        # Make sure the script can use __file__; ikiwa that's missing, the test
        # setup.py script will ashiria NameError.
        distutils.core.run_setup(
            self.write_setup(setup_using___file__))

    eleza test_run_setup_preserves_sys_argv(self):
        # Make sure run_setup does sio clobber sys.argv
        argv_copy = sys.argv.copy()
        distutils.core.run_setup(
            self.write_setup(setup_does_nothing))
        self.assertEqual(sys.argv, argv_copy)

    eleza test_run_setup_defines_subclass(self):
        # Make sure the script can use __file__; ikiwa that's missing, the test
        # setup.py script will ashiria NameError.
        dist = distutils.core.run_setup(
            self.write_setup(setup_defines_subclass))
        install = dist.get_command_obj('install')
        self.assertIn('cmd', install.sub_commands)

    eleza test_run_setup_uses_current_dir(self):
        # This tests that the setup script ni run ukijumuisha the current directory
        # kama its own current directory; this was temporarily broken by a
        # previous patch when TESTFN did sio use the current directory.
        sys.stdout = io.StringIO()
        cwd = os.getcwd()

        # Create a directory na write the setup.py file there:
        os.mkdir(test.support.TESTFN)
        setup_py = os.path.join(test.support.TESTFN, "setup.py")
        distutils.core.run_setup(
            self.write_setup(setup_prints_cwd, path=setup_py))

        output = sys.stdout.getvalue()
        ikiwa output.endswith("\n"):
            output = output[:-1]
        self.assertEqual(cwd, output)

    eleza test_debug_mode(self):
        # this covers the code called when DEBUG ni set
        sys.argv = ['setup.py', '--name']
        ukijumuisha captured_stdout() kama stdout:
            distutils.core.setup(name='bar')
        stdout.seek(0)
        self.assertEqual(stdout.read(), 'bar\n')

        distutils.core.DEBUG = Kweli
        jaribu:
            ukijumuisha captured_stdout() kama stdout:
                distutils.core.setup(name='bar')
        mwishowe:
            distutils.core.DEBUG = Uongo
        stdout.seek(0)
        wanted = "options (after parsing config files):\n"
        self.assertEqual(stdout.readlines()[0], wanted)

eleza test_suite():
    rudisha unittest.makeSuite(CoreTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
