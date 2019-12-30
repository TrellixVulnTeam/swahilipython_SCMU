"""Tests kila distutils.command.install."""

agiza os
agiza sys
agiza unittest
agiza site

kutoka test.support agiza captured_stdout, run_unittest

kutoka distutils agiza sysconfig
kutoka distutils.command.install agiza install
kutoka distutils.command agiza install kama install_module
kutoka distutils.command.build_ext agiza build_ext
kutoka distutils.command.install agiza INSTALL_SCHEMES
kutoka distutils.core agiza Distribution
kutoka distutils.errors agiza DistutilsOptionError
kutoka distutils.extension agiza Extension

kutoka distutils.tests agiza support
kutoka test agiza support kama test_support


eleza _make_ext_name(modname):
    rudisha modname + sysconfig.get_config_var('EXT_SUFFIX')


kundi InstallTestCase(support.TempdirManager,
                      support.EnvironGuard,
                      support.LoggingSilencer,
                      unittest.TestCase):

    eleza test_home_installation_scheme(self):
        # This ensure two things:
        # - that --home generates the desired set of directory names
        # - test --home ni supported on all platforms
        builddir = self.mkdtemp()
        destination = os.path.join(builddir, "installation")

        dist = Distribution({"name": "foopkg"})
        # script_name need sio exist, it just need to be initialized
        dist.script_name = os.path.join(builddir, "setup.py")
        dist.command_obj["build"] = support.DummyCommand(
            build_base=builddir,
            build_lib=os.path.join(builddir, "lib"),
            )

        cmd = install(dist)
        cmd.home = destination
        cmd.ensure_finalized()

        self.assertEqual(cmd.install_base, destination)
        self.assertEqual(cmd.install_platbase, destination)

        eleza check_path(got, expected):
            got = os.path.normpath(got)
            expected = os.path.normpath(expected)
            self.assertEqual(got, expected)

        libdir = os.path.join(destination, "lib", "python")
        check_path(cmd.install_lib, libdir)
        check_path(cmd.install_platlib, libdir)
        check_path(cmd.install_purelib, libdir)
        check_path(cmd.install_headers,
                   os.path.join(destination, "include", "python", "foopkg"))
        check_path(cmd.install_scripts, os.path.join(destination, "bin"))
        check_path(cmd.install_data, destination)

    eleza test_user_site(self):
        # test install ukijumuisha --user
        # preparing the environment kila the test
        self.old_user_base = site.USER_BASE
        self.old_user_site = site.USER_SITE
        self.tmpdir = self.mkdtemp()
        self.user_base = os.path.join(self.tmpdir, 'B')
        self.user_site = os.path.join(self.tmpdir, 'S')
        site.USER_BASE = self.user_base
        site.USER_SITE = self.user_site
        install_module.USER_BASE = self.user_base
        install_module.USER_SITE = self.user_site

        eleza _expanduser(path):
            rudisha self.tmpdir
        self.old_expand = os.path.expanduser
        os.path.expanduser = _expanduser

        eleza cleanup():
            site.USER_BASE = self.old_user_base
            site.USER_SITE = self.old_user_site
            install_module.USER_BASE = self.old_user_base
            install_module.USER_SITE = self.old_user_site
            os.path.expanduser = self.old_expand

        self.addCleanup(cleanup)

        kila key kwenye ('nt_user', 'unix_user'):
            self.assertIn(key, INSTALL_SCHEMES)

        dist = Distribution({'name': 'xx'})
        cmd = install(dist)

        # making sure the user option ni there
        options = [name kila name, short, lable kwenye
                   cmd.user_options]
        self.assertIn('user', options)

        # setting a value
        cmd.user = 1

        # user base na site shouldn't be created yet
        self.assertUongo(os.path.exists(self.user_base))
        self.assertUongo(os.path.exists(self.user_site))

        # let's run finalize
        cmd.ensure_finalized()

        # now they should
        self.assertKweli(os.path.exists(self.user_base))
        self.assertKweli(os.path.exists(self.user_site))

        self.assertIn('userbase', cmd.config_vars)
        self.assertIn('usersite', cmd.config_vars)

    eleza test_handle_extra_path(self):
        dist = Distribution({'name': 'xx', 'extra_path': 'path,dirs'})
        cmd = install(dist)

        # two elements
        cmd.handle_extra_path()
        self.assertEqual(cmd.extra_path, ['path', 'dirs'])
        self.assertEqual(cmd.extra_dirs, 'dirs')
        self.assertEqual(cmd.path_file, 'path')

        # one element
        cmd.extra_path = ['path']
        cmd.handle_extra_path()
        self.assertEqual(cmd.extra_path, ['path'])
        self.assertEqual(cmd.extra_dirs, 'path')
        self.assertEqual(cmd.path_file, 'path')

        # none
        dist.extra_path = cmd.extra_path = Tupu
        cmd.handle_extra_path()
        self.assertEqual(cmd.extra_path, Tupu)
        self.assertEqual(cmd.extra_dirs, '')
        self.assertEqual(cmd.path_file, Tupu)

        # three elements (no way !)
        cmd.extra_path = 'path,dirs,again'
        self.assertRaises(DistutilsOptionError, cmd.handle_extra_path)

    eleza test_finalize_options(self):
        dist = Distribution({'name': 'xx'})
        cmd = install(dist)

        # must supply either prefix/exec-prefix/home ama
        # install-base/install-platbase -- sio both
        cmd.prefix = 'prefix'
        cmd.install_base = 'base'
        self.assertRaises(DistutilsOptionError, cmd.finalize_options)

        # must supply either home ama prefix/exec-prefix -- sio both
        cmd.install_base = Tupu
        cmd.home = 'home'
        self.assertRaises(DistutilsOptionError, cmd.finalize_options)

        # can't combine user ukijumuisha prefix/exec_prefix/home ama
        # install_(plat)base
        cmd.prefix = Tupu
        cmd.user = 'user'
        self.assertRaises(DistutilsOptionError, cmd.finalize_options)

    eleza test_record(self):
        install_dir = self.mkdtemp()
        project_dir, dist = self.create_dist(py_modules=['hello'],
                                             scripts=['sayhi'])
        os.chdir(project_dir)
        self.write_file('hello.py', "eleza main(): andika('o hai')")
        self.write_file('sayhi', 'kutoka hello agiza main; main()')

        cmd = install(dist)
        dist.command_obj['install'] = cmd
        cmd.root = install_dir
        cmd.record = os.path.join(project_dir, 'filelist')
        cmd.ensure_finalized()
        cmd.run()

        f = open(cmd.record)
        jaribu:
            content = f.read()
        mwishowe:
            f.close()

        found = [os.path.basename(line) kila line kwenye content.splitlines()]
        expected = ['hello.py', 'hello.%s.pyc' % sys.implementation.cache_tag,
                    'sayhi',
                    'UNKNOWN-0.0.0-py%s.%s.egg-info' % sys.version_info[:2]]
        self.assertEqual(found, expected)

    eleza test_record_extensions(self):
        cmd = test_support.missing_compiler_executable()
        ikiwa cmd ni sio Tupu:
            self.skipTest('The %r command ni sio found' % cmd)
        install_dir = self.mkdtemp()
        project_dir, dist = self.create_dist(ext_modules=[
            Extension('xx', ['xxmodule.c'])])
        os.chdir(project_dir)
        support.copy_xxmodule_c(project_dir)

        buildextcmd = build_ext(dist)
        support.fixup_build_ext(buildextcmd)
        buildextcmd.ensure_finalized()

        cmd = install(dist)
        dist.command_obj['install'] = cmd
        dist.command_obj['build_ext'] = buildextcmd
        cmd.root = install_dir
        cmd.record = os.path.join(project_dir, 'filelist')
        cmd.ensure_finalized()
        cmd.run()

        f = open(cmd.record)
        jaribu:
            content = f.read()
        mwishowe:
            f.close()

        found = [os.path.basename(line) kila line kwenye content.splitlines()]
        expected = [_make_ext_name('xx'),
                    'UNKNOWN-0.0.0-py%s.%s.egg-info' % sys.version_info[:2]]
        self.assertEqual(found, expected)

    eleza test_debug_mode(self):
        # this covers the code called when DEBUG ni set
        old_logs_len = len(self.logs)
        install_module.DEBUG = Kweli
        jaribu:
            ukijumuisha captured_stdout():
                self.test_record()
        mwishowe:
            install_module.DEBUG = Uongo
        self.assertGreater(len(self.logs), old_logs_len)


eleza test_suite():
    rudisha unittest.makeSuite(InstallTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
