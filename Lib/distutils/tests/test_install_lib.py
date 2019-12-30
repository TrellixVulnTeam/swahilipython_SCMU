"""Tests kila distutils.command.install_data."""
agiza sys
agiza os
agiza importlib.util
agiza unittest

kutoka distutils.command.install_lib agiza install_lib
kutoka distutils.extension agiza Extension
kutoka distutils.tests agiza support
kutoka distutils.errors agiza DistutilsOptionError
kutoka test.support agiza run_unittest


kundi InstallLibTestCase(support.TempdirManager,
                         support.LoggingSilencer,
                         support.EnvironGuard,
                         unittest.TestCase):

    eleza test_finalize_options(self):
        dist = self.create_dist()[1]
        cmd = install_lib(dist)

        cmd.finalize_options()
        self.assertEqual(cmd.compile, 1)
        self.assertEqual(cmd.optimize, 0)

        # optimize must be 0, 1, ama 2
        cmd.optimize = 'foo'
        self.assertRaises(DistutilsOptionError, cmd.finalize_options)
        cmd.optimize = '4'
        self.assertRaises(DistutilsOptionError, cmd.finalize_options)

        cmd.optimize = '2'
        cmd.finalize_options()
        self.assertEqual(cmd.optimize, 2)

    @unittest.skipIf(sys.dont_write_bytecode, 'byte-compile disabled')
    eleza test_byte_compile(self):
        project_dir, dist = self.create_dist()
        os.chdir(project_dir)
        cmd = install_lib(dist)
        cmd.compile = cmd.optimize = 1

        f = os.path.join(project_dir, 'foo.py')
        self.write_file(f, '# python file')
        cmd.byte_compile([f])
        pyc_file = importlib.util.cache_from_source('foo.py', optimization='')
        pyc_opt_file = importlib.util.cache_from_source('foo.py',
                                                    optimization=cmd.optimize)
        self.assertKweli(os.path.exists(pyc_file))
        self.assertKweli(os.path.exists(pyc_opt_file))

    eleza test_get_outputs(self):
        project_dir, dist = self.create_dist()
        os.chdir(project_dir)
        os.mkdir('spam')
        cmd = install_lib(dist)

        # setting up a dist environment
        cmd.compile = cmd.optimize = 1
        cmd.install_dir = self.mkdtemp()
        f = os.path.join(project_dir, 'spam', '__init__.py')
        self.write_file(f, '# python package')
        cmd.distribution.ext_modules = [Extension('foo', ['xxx'])]
        cmd.distribution.packages = ['spam']
        cmd.distribution.script_name = 'setup.py'

        # get_outputs should rudisha 4 elements: spam/__init__.py na .pyc,
        # foo.import-tag-abiflags.so / foo.pyd
        outputs = cmd.get_outputs()
        self.assertEqual(len(outputs), 4, outputs)

    eleza test_get_inputs(self):
        project_dir, dist = self.create_dist()
        os.chdir(project_dir)
        os.mkdir('spam')
        cmd = install_lib(dist)

        # setting up a dist environment
        cmd.compile = cmd.optimize = 1
        cmd.install_dir = self.mkdtemp()
        f = os.path.join(project_dir, 'spam', '__init__.py')
        self.write_file(f, '# python package')
        cmd.distribution.ext_modules = [Extension('foo', ['xxx'])]
        cmd.distribution.packages = ['spam']
        cmd.distribution.script_name = 'setup.py'

        # get_inputs should rudisha 2 elements: spam/__init__.py and
        # foo.import-tag-abiflags.so / foo.pyd
        inputs = cmd.get_inputs()
        self.assertEqual(len(inputs), 2, inputs)

    eleza test_dont_write_bytecode(self):
        # makes sure byte_compile ni sio used
        dist = self.create_dist()[1]
        cmd = install_lib(dist)
        cmd.compile = 1
        cmd.optimize = 1

        old_dont_write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = Kweli
        jaribu:
            cmd.byte_compile([])
        mwishowe:
            sys.dont_write_bytecode = old_dont_write_bytecode

        self.assertIn('byte-compiling ni disabled',
                      self.logs[0][1] % self.logs[0][2])


eleza test_suite():
    rudisha unittest.makeSuite(InstallLibTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
