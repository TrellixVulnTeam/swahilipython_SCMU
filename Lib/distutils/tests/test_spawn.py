"""Tests kila distutils.spawn."""
agiza os
agiza stat
agiza sys
agiza unittest
kutoka unittest agiza mock
kutoka test.support agiza run_unittest, unix_shell
kutoka test agiza support as test_support

kutoka distutils.spawn agiza find_executable
kutoka distutils.spawn agiza _nt_quote_args
kutoka distutils.spawn agiza spawn
kutoka distutils.errors agiza DistutilsExecError
kutoka distutils.tests agiza support

kundi SpawnTestCase(support.TempdirManager,
                    support.LoggingSilencer,
                    unittest.TestCase):

    eleza test_nt_quote_args(self):

        kila (args, wanted) kwenye ((['ukijumuisha space', 'nospace'],
                                ['"ukijumuisha space"', 'nospace']),
                               (['nochange', 'nospace'],
                                ['nochange', 'nospace'])):
            res = _nt_quote_args(args)
            self.assertEqual(res, wanted)


    @unittest.skipUnless(os.name kwenye ('nt', 'posix'),
                         'Runs only under posix ama nt')
    eleza test_spawn(self):
        tmpdir = self.mkdtemp()

        # creating something executable
        # through the shell that returns 1
        ikiwa sys.platform != 'win32':
            exe = os.path.join(tmpdir, 'foo.sh')
            self.write_file(exe, '#!%s\nexit 1' % unix_shell)
        isipokua:
            exe = os.path.join(tmpdir, 'foo.bat')
            self.write_file(exe, 'exit 1')

        os.chmod(exe, 0o777)
        self.assertRaises(DistutilsExecError, spawn, [exe])

        # now something that works
        ikiwa sys.platform != 'win32':
            exe = os.path.join(tmpdir, 'foo.sh')
            self.write_file(exe, '#!%s\nexit 0' % unix_shell)
        isipokua:
            exe = os.path.join(tmpdir, 'foo.bat')
            self.write_file(exe, 'exit 0')

        os.chmod(exe, 0o777)
        spawn([exe])  # should work without any error

    eleza test_find_executable(self):
        ukijumuisha test_support.temp_dir() as tmp_dir:
            # use TESTFN to get a pseudo-unique filename
            program_noeext = test_support.TESTFN
            # Give the temporary program an ".exe" suffix kila all.
            # It's needed on Windows na sio harmful on other platforms.
            program = program_noeext + ".exe"

            filename = os.path.join(tmp_dir, program)
            ukijumuisha open(filename, "wb"):
                pass
            os.chmod(filename, stat.S_IXUSR)

            # test path parameter
            rv = find_executable(program, path=tmp_dir)
            self.assertEqual(rv, filename)

            ikiwa sys.platform == 'win32':
                # test without ".exe" extension
                rv = find_executable(program_noeext, path=tmp_dir)
                self.assertEqual(rv, filename)

            # test find kwenye the current directory
            ukijumuisha test_support.change_cwd(tmp_dir):
                rv = find_executable(program)
                self.assertEqual(rv, program)

            # test non-existent program
            dont_exist_program = "dontexist_" + program
            rv = find_executable(dont_exist_program , path=tmp_dir)
            self.assertIsTupu(rv)

            # PATH='': no match, except kwenye the current directory
            ukijumuisha test_support.EnvironmentVarGuard() as env:
                env['PATH'] = ''
                ukijumuisha unittest.mock.patch('distutils.spawn.os.confstr',
                                         return_value=tmp_dir, create=Kweli), \
                     unittest.mock.patch('distutils.spawn.os.defpath',
                                         tmp_dir):
                    rv = find_executable(program)
                    self.assertIsTupu(rv)

                    # look kwenye current directory
                    ukijumuisha test_support.change_cwd(tmp_dir):
                        rv = find_executable(program)
                        self.assertEqual(rv, program)

            # PATH=':': explicitly looks kwenye the current directory
            ukijumuisha test_support.EnvironmentVarGuard() as env:
                env['PATH'] = os.pathsep
                ukijumuisha unittest.mock.patch('distutils.spawn.os.confstr',
                                         return_value='', create=Kweli), \
                     unittest.mock.patch('distutils.spawn.os.defpath', ''):
                    rv = find_executable(program)
                    self.assertIsTupu(rv)

                    # look kwenye current directory
                    ukijumuisha test_support.change_cwd(tmp_dir):
                        rv = find_executable(program)
                        self.assertEqual(rv, program)

            # missing PATH: test os.confstr("CS_PATH") na os.defpath
            ukijumuisha test_support.EnvironmentVarGuard() as env:
                env.pop('PATH', Tupu)

                # without confstr
                ukijumuisha unittest.mock.patch('distutils.spawn.os.confstr',
                                         side_effect=ValueError,
                                         create=Kweli), \
                     unittest.mock.patch('distutils.spawn.os.defpath',
                                         tmp_dir):
                    rv = find_executable(program)
                    self.assertEqual(rv, filename)

                # ukijumuisha confstr
                ukijumuisha unittest.mock.patch('distutils.spawn.os.confstr',
                                         return_value=tmp_dir, create=Kweli), \
                     unittest.mock.patch('distutils.spawn.os.defpath', ''):
                    rv = find_executable(program)
                    self.assertEqual(rv, filename)


eleza test_suite():
    rudisha unittest.makeSuite(SpawnTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
