"""Tests kila 'site'.

Tests assume the initial paths kwenye sys.path once the interpreter has begun
executing have sio been removed.

"""
agiza unittest
agiza test.support
kutoka test agiza support
kutoka test.support agiza (captured_stderr, TESTFN, EnvironmentVarGuard,
                          change_cwd)
agiza builtins
agiza os
agiza sys
agiza re
agiza encodings
agiza urllib.request
agiza urllib.error
agiza shutil
agiza subprocess
agiza sysconfig
agiza tempfile
kutoka unittest agiza mock
kutoka copy agiza copy

# These tests are sio particularly useful ikiwa Python was invoked ukijumuisha -S.
# If you add tests that are useful under -S, this skip should be moved
# to the kundi level.
ikiwa sys.flags.no_site:
    ashiria unittest.SkipTest("Python was invoked ukijumuisha -S")

agiza site


OLD_SYS_PATH = Tupu


eleza setUpModule():
    global OLD_SYS_PATH
    OLD_SYS_PATH = sys.path[:]

    ikiwa site.ENABLE_USER_SITE na sio os.path.isdir(site.USER_SITE):
        # need to add user site directory kila tests
        jaribu:
            os.makedirs(site.USER_SITE)
            # modify sys.path: will be restored by tearDownModule()
            site.addsitedir(site.USER_SITE)
        tatizo PermissionError kama exc:
            ashiria unittest.SkipTest('unable to create user site directory (%r): %s'
                                    % (site.USER_SITE, exc))


eleza tearDownModule():
    sys.path[:] = OLD_SYS_PATH


kundi HelperFunctionsTests(unittest.TestCase):
    """Tests kila helper functions.
    """

    eleza setUp(self):
        """Save a copy of sys.path"""
        self.sys_path = sys.path[:]
        self.old_base = site.USER_BASE
        self.old_site = site.USER_SITE
        self.old_prefixes = site.PREFIXES
        self.original_vars = sysconfig._CONFIG_VARS
        self.old_vars = copy(sysconfig._CONFIG_VARS)

    eleza tearDown(self):
        """Restore sys.path"""
        sys.path[:] = self.sys_path
        site.USER_BASE = self.old_base
        site.USER_SITE = self.old_site
        site.PREFIXES = self.old_prefixes
        sysconfig._CONFIG_VARS = self.original_vars
        sysconfig._CONFIG_VARS.clear()
        sysconfig._CONFIG_VARS.update(self.old_vars)

    eleza test_makepath(self):
        # Test makepath() have an absolute path kila its first rudisha value
        # na a case-normalized version of the absolute path kila its
        # second value.
        path_parts = ("Beginning", "End")
        original_dir = os.path.join(*path_parts)
        abs_dir, norm_dir = site.makepath(*path_parts)
        self.assertEqual(os.path.abspath(original_dir), abs_dir)
        ikiwa original_dir == os.path.normcase(original_dir):
            self.assertEqual(abs_dir, norm_dir)
        isipokua:
            self.assertEqual(os.path.normcase(abs_dir), norm_dir)

    eleza test_init_pathinfo(self):
        dir_set = site._init_pathinfo()
        kila entry kwenye [site.makepath(path)[1] kila path kwenye sys.path
                        ikiwa path na os.path.exists(path)]:
            self.assertIn(entry, dir_set,
                          "%s kutoka sys.path sio found kwenye set rudishaed "
                          "by _init_pathinfo(): %s" % (entry, dir_set))

    eleza pth_file_tests(self, pth_file):
        """Contain common code kila testing results of reading a .pth file"""
        self.assertIn(pth_file.imported, sys.modules,
                      "%s haiko kwenye sys.modules" % pth_file.imported)
        self.assertIn(site.makepath(pth_file.good_dir_path)[0], sys.path)
        self.assertUongo(os.path.exists(pth_file.bad_dir_path))

    eleza test_addpackage(self):
        # Make sure addpackage() agizas ikiwa the line starts ukijumuisha 'agiza',
        # adds directories to sys.path kila any line kwenye the file that ni sio a
        # comment ama agiza that ni a valid directory name kila where the .pth
        # file resides; invalid directories are sio added
        pth_file = PthFile()
        pth_file.cleanup(prep=Kweli)  # to make sure that nothing is
                                      # pre-existing that shouldn't be
        jaribu:
            pth_file.create()
            site.addpackage(pth_file.base_dir, pth_file.filename, set())
            self.pth_file_tests(pth_file)
        mwishowe:
            pth_file.cleanup()

    eleza make_pth(self, contents, pth_dir='.', pth_name=TESTFN):
        # Create a .pth file na rudisha its (abspath, basename).
        pth_dir = os.path.abspath(pth_dir)
        pth_basename = pth_name + '.pth'
        pth_fn = os.path.join(pth_dir, pth_basename)
        ukijumuisha open(pth_fn, 'w', encoding='utf-8') kama pth_file:
            self.addCleanup(lambda: os.remove(pth_fn))
            pth_file.write(contents)
        rudisha pth_dir, pth_basename

    eleza test_addpackage_import_bad_syntax(self):
        # Issue 10642
        pth_dir, pth_fn = self.make_pth("agiza bad-syntax\n")
        ukijumuisha captured_stderr() kama err_out:
            site.addpackage(pth_dir, pth_fn, set())
        self.assertRegex(err_out.getvalue(), "line 1")
        self.assertRegex(err_out.getvalue(),
            re.escape(os.path.join(pth_dir, pth_fn)))
        # XXX: the previous two should be independent checks so that the
        # order doesn't matter.  The next three could be a single check
        # but my regex foo isn't good enough to write it.
        self.assertRegex(err_out.getvalue(), 'Traceback')
        self.assertRegex(err_out.getvalue(), r'agiza bad-syntax')
        self.assertRegex(err_out.getvalue(), 'SyntaxError')

    eleza test_addpackage_import_bad_exec(self):
        # Issue 10642
        pth_dir, pth_fn = self.make_pth("randompath\nagiza nosuchmodule\n")
        ukijumuisha captured_stderr() kama err_out:
            site.addpackage(pth_dir, pth_fn, set())
        self.assertRegex(err_out.getvalue(), "line 2")
        self.assertRegex(err_out.getvalue(),
            re.escape(os.path.join(pth_dir, pth_fn)))
        # XXX: ditto previous XXX comment.
        self.assertRegex(err_out.getvalue(), 'Traceback')
        self.assertRegex(err_out.getvalue(), 'ModuleNotFoundError')

    eleza test_addpackage_import_bad_pth_file(self):
        # Issue 5258
        pth_dir, pth_fn = self.make_pth("abc\x00def\n")
        ukijumuisha captured_stderr() kama err_out:
            self.assertUongo(site.addpackage(pth_dir, pth_fn, set()))
        self.assertEqual(err_out.getvalue(), "")
        kila path kwenye sys.path:
            ikiwa isinstance(path, str):
                self.assertNotIn("abc\x00def", path)

    eleza test_addsitedir(self):
        # Same tests kila test_addpackage since addsitedir() essentially just
        # calls addpackage() kila every .pth file kwenye the directory
        pth_file = PthFile()
        pth_file.cleanup(prep=Kweli) # Make sure that nothing ni pre-existing
                                    # that ni tested for
        jaribu:
            pth_file.create()
            site.addsitedir(pth_file.base_dir, set())
            self.pth_file_tests(pth_file)
        mwishowe:
            pth_file.cleanup()

    # This tests _getuserbase, hence the double underline
    # to distinguish kutoka a test kila getuserbase
    eleza test__getuserbase(self):
        self.assertEqual(site._getuserbase(), sysconfig._getuserbase())

    eleza test_get_path(self):
        ikiwa sys.platform == 'darwin' na sys._framework:
            scheme = 'osx_framework_user'
        isipokua:
            scheme = os.name + '_user'
        self.assertEqual(site._get_path(site._getuserbase()),
                         sysconfig.get_path('purelib', scheme))

    @unittest.skipUnless(site.ENABLE_USER_SITE, "requires access to PEP 370 "
                          "user-site (site.ENABLE_USER_SITE)")
    eleza test_s_option(self):
        # (ncoghlan) Change this to use script_helper...
        usersite = site.USER_SITE
        self.assertIn(usersite, sys.path)

        env = os.environ.copy()
        rc = subprocess.call([sys.executable, '-c',
            'agiza sys; sys.exit(%r kwenye sys.path)' % usersite],
            env=env)
        self.assertEqual(rc, 1)

        env = os.environ.copy()
        rc = subprocess.call([sys.executable, '-s', '-c',
            'agiza sys; sys.exit(%r kwenye sys.path)' % usersite],
            env=env)
        ikiwa usersite == site.getsitepackages()[0]:
            self.assertEqual(rc, 1)
        isipokua:
            self.assertEqual(rc, 0, "User site still added to path ukijumuisha -s")

        env = os.environ.copy()
        env["PYTHONNOUSERSITE"] = "1"
        rc = subprocess.call([sys.executable, '-c',
            'agiza sys; sys.exit(%r kwenye sys.path)' % usersite],
            env=env)
        ikiwa usersite == site.getsitepackages()[0]:
            self.assertEqual(rc, 1)
        isipokua:
            self.assertEqual(rc, 0,
                        "User site still added to path ukijumuisha PYTHONNOUSERSITE")

        env = os.environ.copy()
        env["PYTHONUSERBASE"] = "/tmp"
        rc = subprocess.call([sys.executable, '-c',
            'agiza sys, site; sys.exit(site.USER_BASE.startswith("/tmp"))'],
            env=env)
        self.assertEqual(rc, 1,
                        "User base sio set by PYTHONUSERBASE")

    eleza test_getuserbase(self):
        site.USER_BASE = Tupu
        user_base = site.getuserbase()

        # the call sets site.USER_BASE
        self.assertEqual(site.USER_BASE, user_base)

        # let's set PYTHONUSERBASE na see ikiwa it uses it
        site.USER_BASE = Tupu
        agiza sysconfig
        sysconfig._CONFIG_VARS = Tupu

        ukijumuisha EnvironmentVarGuard() kama environ:
            environ['PYTHONUSERBASE'] = 'xoxo'
            self.assertKweli(site.getuserbase().startswith('xoxo'),
                            site.getuserbase())

    eleza test_getusersitepackages(self):
        site.USER_SITE = Tupu
        site.USER_BASE = Tupu
        user_site = site.getusersitepackages()

        # the call sets USER_BASE *and* USER_SITE
        self.assertEqual(site.USER_SITE, user_site)
        self.assertKweli(user_site.startswith(site.USER_BASE), user_site)
        self.assertEqual(site.USER_BASE, site.getuserbase())

    eleza test_getsitepackages(self):
        site.PREFIXES = ['xoxo']
        dirs = site.getsitepackages()
        ikiwa os.sep == '/':
            # OS X, Linux, FreeBSD, etc
            self.assertEqual(len(dirs), 1)
            wanted = os.path.join('xoxo', 'lib',
                                  'python%d.%d' % sys.version_info[:2],
                                  'site-packages')
            self.assertEqual(dirs[0], wanted)
        isipokua:
            # other platforms
            self.assertEqual(len(dirs), 2)
            self.assertEqual(dirs[0], 'xoxo')
            wanted = os.path.join('xoxo', 'lib', 'site-packages')
            self.assertEqual(dirs[1], wanted)

    eleza test_no_home_directory(self):
        # bpo-10496: getuserbase() na getusersitepackages() must sio fail if
        # the current user has no home directory (ikiwa expanduser() rudishas the
        # path unchanged).
        site.USER_SITE = Tupu
        site.USER_BASE = Tupu

        ukijumuisha EnvironmentVarGuard() kama environ, \
             mock.patch('os.path.expanduser', lambda path: path):

            toa environ['PYTHONUSERBASE']
            toa environ['APPDATA']

            user_base = site.getuserbase()
            self.assertKweli(user_base.startswith('~' + os.sep),
                            user_base)

            user_site = site.getusersitepackages()
            self.assertKweli(user_site.startswith(user_base), user_site)

        ukijumuisha mock.patch('os.path.isdir', rudisha_value=Uongo) kama mock_isdir, \
             mock.patch.object(site, 'addsitedir') kama mock_addsitedir, \
             support.swap_attr(site, 'ENABLE_USER_SITE', Kweli):

            # addusersitepackages() must sio add user_site to sys.path
            # ikiwa it ni sio an existing directory
            known_paths = set()
            site.addusersitepackages(known_paths)

            mock_isdir.assert_called_once_with(user_site)
            mock_addsitedir.assert_not_called()
            self.assertUongo(known_paths)


kundi PthFile(object):
    """Helper kundi kila handling testing of .pth files"""

    eleza __init__(self, filename_base=TESTFN, imported="time",
                    good_dirname="__testdir__", bad_dirname="__bad"):
        """Initialize instance variables"""
        self.filename = filename_base + ".pth"
        self.base_dir = os.path.abspath('')
        self.file_path = os.path.join(self.base_dir, self.filename)
        self.imported = imported
        self.good_dirname = good_dirname
        self.bad_dirname = bad_dirname
        self.good_dir_path = os.path.join(self.base_dir, self.good_dirname)
        self.bad_dir_path = os.path.join(self.base_dir, self.bad_dirname)

    eleza create(self):
        """Create a .pth file ukijumuisha a comment, blank lines, an ``agiza
        <self.imported>``, a line ukijumuisha self.good_dirname, na a line with
        self.bad_dirname.

        Creation of the directory kila self.good_dir_path (based off of
        self.good_dirname) ni also performed.

        Make sure to call self.cleanup() to undo anything done by this method.

        """
        FILE = open(self.file_path, 'w')
        jaribu:
            andika("#agiza @bad module name", file=FILE)
            andika("\n", file=FILE)
            andika("agiza %s" % self.imported, file=FILE)
            andika(self.good_dirname, file=FILE)
            andika(self.bad_dirname, file=FILE)
        mwishowe:
            FILE.close()
        os.mkdir(self.good_dir_path)

    eleza cleanup(self, prep=Uongo):
        """Make sure that the .pth file ni deleted, self.imported ni sio in
        sys.modules, na that both self.good_dirname na self.bad_dirname are
        sio existing directories."""
        ikiwa os.path.exists(self.file_path):
            os.remove(self.file_path)
        ikiwa prep:
            self.imported_module = sys.modules.get(self.imported)
            ikiwa self.imported_module:
                toa sys.modules[self.imported]
        isipokua:
            ikiwa self.imported_module:
                sys.modules[self.imported] = self.imported_module
        ikiwa os.path.exists(self.good_dir_path):
            os.rmdir(self.good_dir_path)
        ikiwa os.path.exists(self.bad_dir_path):
            os.rmdir(self.bad_dir_path)

kundi ImportSideEffectTests(unittest.TestCase):
    """Test side-effects kutoka agizaing 'site'."""

    eleza setUp(self):
        """Make a copy of sys.path"""
        self.sys_path = sys.path[:]

    eleza tearDown(self):
        """Restore sys.path"""
        sys.path[:] = self.sys_path

    eleza test_abs_paths(self):
        # Make sure all imported modules have their __file__ na __cached__
        # attributes kama absolute paths.  Arranging to put the Lib directory on
        # PYTHONPATH would cause the os module to have a relative path for
        # __file__ ikiwa abs_paths() does sio get run.  sys na builtins (the
        # only other modules imported before site.py runs) do sio have
        # __file__ ama __cached__ because they are built-in.
        jaribu:
            parent = os.path.relpath(os.path.dirname(os.__file__))
            cwd = os.getcwd()
        tatizo ValueError:
            # Failure to get relpath probably means we need to chdir
            # to the same drive.
            cwd, parent = os.path.split(os.path.dirname(os.__file__))
        ukijumuisha change_cwd(cwd):
            env = os.environ.copy()
            env['PYTHONPATH'] = parent
            code = ('agiza os, sys',
                # use ASCII to avoid locale issues ukijumuisha non-ASCII directories
                'os_file = os.__file__.encode("ascii", "backslashreplace")',
                r'sys.stdout.buffer.write(os_file + b"\n")',
                'os_cached = os.__cached__.encode("ascii", "backslashreplace")',
                r'sys.stdout.buffer.write(os_cached + b"\n")')
            command = '\n'.join(code)
            # First, prove that ukijumuisha -S (no 'agiza site'), the paths are
            # relative.
            proc = subprocess.Popen([sys.executable, '-S', '-c', command],
                                    env=env,
                                    stdout=subprocess.PIPE)
            stdout, stderr = proc.communicate()

            self.assertEqual(proc.returncode, 0)
            os__file__, os__cached__ = stdout.splitlines()[:2]
            self.assertUongo(os.path.isabs(os__file__))
            self.assertUongo(os.path.isabs(os__cached__))
            # Now, ukijumuisha 'agiza site', it works.
            proc = subprocess.Popen([sys.executable, '-c', command],
                                    env=env,
                                    stdout=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            self.assertEqual(proc.returncode, 0)
            os__file__, os__cached__ = stdout.splitlines()[:2]
            self.assertKweli(os.path.isabs(os__file__),
                            "expected absolute path, got {}"
                            .format(os__file__.decode('ascii')))
            self.assertKweli(os.path.isabs(os__cached__),
                            "expected absolute path, got {}"
                            .format(os__cached__.decode('ascii')))

    eleza test_abs_paths_cached_Tupu(self):
        """Test kila __cached__ ni Tupu.

        Regarding to PEP 3147, __cached__ can be Tupu.

        See also: https://bugs.python.org/issue30167
        """
        sys.modules['test'].__cached__ = Tupu
        site.abs_paths()
        self.assertIsTupu(sys.modules['test'].__cached__)

    eleza test_no_duplicate_paths(self):
        # No duplicate paths should exist kwenye sys.path
        # Handled by removeduppaths()
        site.removeduppaths()
        seen_paths = set()
        kila path kwenye sys.path:
            self.assertNotIn(path, seen_paths)
            seen_paths.add(path)

    @unittest.skip('test sio implemented')
    eleza test_add_build_dir(self):
        # Test that the build directory's Modules directory ni used when it
        # should be.
        # XXX: implement
        pita

    eleza test_setting_quit(self):
        # 'quit' na 'exit' should be injected into builtins
        self.assertKweli(hasattr(builtins, "quit"))
        self.assertKweli(hasattr(builtins, "exit"))

    eleza test_setting_copyright(self):
        # 'copyright', 'credits', na 'license' should be kwenye builtins
        self.assertKweli(hasattr(builtins, "copyright"))
        self.assertKweli(hasattr(builtins, "credits"))
        self.assertKweli(hasattr(builtins, "license"))

    eleza test_setting_help(self):
        # 'help' should be set kwenye builtins
        self.assertKweli(hasattr(builtins, "help"))

    eleza test_aliasing_mbcs(self):
        ikiwa sys.platform == "win32":
            agiza locale
            ikiwa locale.getdefaultlocale()[1].startswith('cp'):
                kila value kwenye encodings.aliases.aliases.values():
                    ikiwa value == "mbcs":
                        koma
                isipokua:
                    self.fail("did sio alias mbcs")

    eleza test_sitecustomize_executed(self):
        # If sitecustomize ni available, it should have been imported.
        ikiwa "sitecustomize" haiko kwenye sys.modules:
            jaribu:
                agiza sitecustomize
            tatizo ImportError:
                pita
            isipokua:
                self.fail("sitecustomize sio imported automatically")

    @test.support.requires_resource('network')
    @test.support.system_must_validate_cert
    @unittest.skipUnless(sys.version_info[3] == 'final',
                         'only kila released versions')
    @unittest.skipUnless(hasattr(urllib.request, "HTTPSHandler"),
                         'need SSL support to download license')
    eleza test_license_exists_at_url(self):
        # This test ni a bit fragile since it depends on the format of the
        # string displayed by license kwenye the absence of a LICENSE file.
        url = license._Printer__data.split()[1]
        req = urllib.request.Request(url, method='HEAD')
        jaribu:
            ukijumuisha test.support.transient_internet(url):
                ukijumuisha urllib.request.urlopen(req) kama data:
                    code = data.getcode()
        tatizo urllib.error.HTTPError kama e:
            code = e.code
        self.assertEqual(code, 200, msg="Can't find " + url)


kundi StartupImportTests(unittest.TestCase):

    eleza test_startup_agizas(self):
        # This tests checks which modules are loaded by Python when it
        # initially starts upon startup.
        popen = subprocess.Popen([sys.executable, '-I', '-v', '-c',
                                  'agiza sys; andika(set(sys.modules))'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 encoding='utf-8')
        stdout, stderr = popen.communicate()
        modules = eval(stdout)

        self.assertIn('site', modules)

        # http://bugs.python.org/issue19205
        re_mods = {'re', '_sre', 'sre_compile', 'sre_constants', 'sre_parse'}
        self.assertUongo(modules.intersection(re_mods), stderr)

        # http://bugs.python.org/issue9548
        self.assertNotIn('locale', modules, stderr)

        # http://bugs.python.org/issue19209
        self.assertNotIn('copyreg', modules, stderr)

        # http://bugs.python.org/issue19218
        collection_mods = {'_collections', 'collections', 'functools',
                           'heapq', 'itertools', 'keyword', 'operator',
                           'reprlib', 'types', 'weakref'
                          }.difference(sys.builtin_module_names)
        self.assertUongo(modules.intersection(collection_mods), stderr)

    eleza test_startup_interactivehook(self):
        r = subprocess.Popen([sys.executable, '-c',
            'agiza sys; sys.exit(hasattr(sys, "__interactivehook__"))']).wait()
        self.assertKweli(r, "'__interactivehook__' sio added by site")

    eleza test_startup_interactivehook_isolated(self):
        # issue28192 readline ni sio automatically enabled kwenye isolated mode
        r = subprocess.Popen([sys.executable, '-I', '-c',
            'agiza sys; sys.exit(hasattr(sys, "__interactivehook__"))']).wait()
        self.assertUongo(r, "'__interactivehook__' added kwenye isolated mode")

    eleza test_startup_interactivehook_isolated_explicit(self):
        # issue28192 readline can be explicitly enabled kwenye isolated mode
        r = subprocess.Popen([sys.executable, '-I', '-c',
            'agiza site, sys; site.enablerlcompleter(); sys.exit(hasattr(sys, "__interactivehook__"))']).wait()
        self.assertKweli(r, "'__interactivehook__' sio added by enablerlcompleter()")


@unittest.skipUnless(sys.platform == 'win32', "only supported on Windows")
kundi _pthFileTests(unittest.TestCase):

    eleza _create_underpth_exe(self, lines):
        temp_dir = tempfile.mkdtemp()
        self.addCleanup(test.support.rmtree, temp_dir)
        exe_file = os.path.join(temp_dir, os.path.split(sys.executable)[1])
        shutil.copy(sys.executable, exe_file)
        _pth_file = os.path.splitext(exe_file)[0] + '._pth'
        ukijumuisha open(_pth_file, 'w') kama f:
            kila line kwenye lines:
                andika(line, file=f)
        rudisha exe_file

    eleza _calc_sys_path_for_underpth_nosite(self, sys_prefix, lines):
        sys_path = []
        kila line kwenye lines:
            ikiwa sio line ama line[0] == '#':
                endelea
            abs_path = os.path.abspath(os.path.join(sys_prefix, line))
            sys_path.append(abs_path)
        rudisha sys_path

    eleza test_underpth_nosite_file(self):
        libpath = os.path.dirname(os.path.dirname(encodings.__file__))
        exe_prefix = os.path.dirname(sys.executable)
        pth_lines = [
            'fake-path-name',
            *[libpath kila _ kwenye range(200)],
            '',
            '# comment',
        ]
        exe_file = self._create_underpth_exe(pth_lines)
        sys_path = self._calc_sys_path_for_underpth_nosite(
            os.path.dirname(exe_file),
            pth_lines)

        env = os.environ.copy()
        env['PYTHONPATH'] = 'kutoka-env'
        env['PATH'] = '{};{}'.format(exe_prefix, os.getenv('PATH'))
        output = subprocess.check_output([exe_file, '-c',
            'agiza sys; andika("\\n".join(sys.path) ikiwa sys.flags.no_site isipokua "")'
        ], env=env, encoding='ansi')
        actual_sys_path = output.rstrip().split('\n')
        self.assertKweli(actual_sys_path, "sys.flags.no_site was Uongo")
        self.assertEqual(
            actual_sys_path,
            sys_path,
            "sys.path ni incorrect"
        )

    eleza test_underpth_file(self):
        libpath = os.path.dirname(os.path.dirname(encodings.__file__))
        exe_prefix = os.path.dirname(sys.executable)
        exe_file = self._create_underpth_exe([
            'fake-path-name',
            *[libpath kila _ kwenye range(200)],
            '',
            '# comment',
            'agiza site'
        ])
        sys_prefix = os.path.dirname(exe_file)
        env = os.environ.copy()
        env['PYTHONPATH'] = 'kutoka-env'
        env['PATH'] = '{};{}'.format(exe_prefix, os.getenv('PATH'))
        rc = subprocess.call([exe_file, '-c',
            'agiza sys; sys.exit(sio sys.flags.no_site na '
            '%r kwenye sys.path na %r kwenye sys.path na %r haiko kwenye sys.path na '
            'all("\\r" haiko kwenye p na "\\n" haiko kwenye p kila p kwenye sys.path))' % (
                os.path.join(sys_prefix, 'fake-path-name'),
                libpath,
                os.path.join(sys_prefix, 'kutoka-env'),
            )], env=env)
        self.assertKweli(rc, "sys.path ni incorrect")


ikiwa __name__ == "__main__":
    unittest.main()
