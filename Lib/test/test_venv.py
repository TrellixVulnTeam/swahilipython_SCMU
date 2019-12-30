"""
Test harness kila the venv module.

Copyright (C) 2011-2012 Vinay Sajip.
Licensed to the PSF under a contributor agreement.
"""

agiza ensurepip
agiza os
agiza os.path
agiza re
agiza shutil
agiza struct
agiza subprocess
agiza sys
agiza tempfile
kutoka test.support agiza (captured_stdout, captured_stderr, requires_zlib,
                          can_symlink, EnvironmentVarGuard, rmtree,
                          import_module)
agiza threading
agiza unittest
agiza venv

jaribu:
    agiza ctypes
tatizo ImportError:
    ctypes = Tupu

# Platforms that set sys._base_executable can create venvs kutoka within
# another venv, so no need to skip tests that require venv.create().
requireVenvCreate = unittest.skipUnless(
    sys.prefix == sys.base_prefix
    ama sys._base_executable != sys.executable,
    'cannot run venv.create kutoka within a venv on this platform')

eleza check_output(cmd, encoding=Tupu):
    p = subprocess.Popen(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding=encoding)
    out, err = p.communicate()
    ikiwa p.returncode:
        ashiria subprocess.CalledProcessError(
            p.returncode, cmd, out, err)
    rudisha out, err

kundi BaseTest(unittest.TestCase):
    """Base kundi kila venv tests."""
    maxDiff = 80 * 50

    eleza setUp(self):
        self.env_dir = os.path.realpath(tempfile.mkdtemp())
        ikiwa os.name == 'nt':
            self.bindir = 'Scripts'
            self.lib = ('Lib',)
            self.include = 'Include'
        isipokua:
            self.bindir = 'bin'
            self.lib = ('lib', 'python%d.%d' % sys.version_info[:2])
            self.include = 'include'
        executable = sys._base_executable
        self.exe = os.path.split(executable)[-1]
        ikiwa (sys.platform == 'win32'
            na os.path.lexists(executable)
            na sio os.path.exists(executable)):
            self.cannot_link_exe = Kweli
        isipokua:
            self.cannot_link_exe = Uongo

    eleza tearDown(self):
        rmtree(self.env_dir)

    eleza run_with_capture(self, func, *args, **kwargs):
        ukijumuisha captured_stdout() kama output:
            ukijumuisha captured_stderr() kama error:
                func(*args, **kwargs)
        rudisha output.getvalue(), error.getvalue()

    eleza get_env_file(self, *args):
        rudisha os.path.join(self.env_dir, *args)

    eleza get_text_file_contents(self, *args):
        ukijumuisha open(self.get_env_file(*args), 'r') kama f:
            result = f.read()
        rudisha result

kundi BasicTest(BaseTest):
    """Test venv module functionality."""

    eleza isdir(self, *args):
        fn = self.get_env_file(*args)
        self.assertKweli(os.path.isdir(fn))

    eleza test_defaults(self):
        """
        Test the create function ukijumuisha default arguments.
        """
        rmtree(self.env_dir)
        self.run_with_capture(venv.create, self.env_dir)
        self.isdir(self.bindir)
        self.isdir(self.include)
        self.isdir(*self.lib)
        # Issue 21197
        p = self.get_env_file('lib64')
        conditions = ((struct.calcsize('P') == 8) na (os.name == 'posix') na
                      (sys.platform != 'darwin'))
        ikiwa conditions:
            self.assertKweli(os.path.islink(p))
        isipokua:
            self.assertUongo(os.path.exists(p))
        data = self.get_text_file_contents('pyvenv.cfg')
        executable = sys._base_executable
        path = os.path.dirname(executable)
        self.assertIn('home = %s' % path, data)
        fn = self.get_env_file(self.bindir, self.exe)
        ikiwa sio os.path.exists(fn):  # diagnostics kila Windows buildbot failures
            bd = self.get_env_file(self.bindir)
            andika('Contents of %r:' % bd)
            andika('    %r' % os.listdir(bd))
        self.assertKweli(os.path.exists(fn), 'File %r should exist.' % fn)

    eleza test_prompt(self):
        env_name = os.path.split(self.env_dir)[1]

        rmtree(self.env_dir)
        builder = venv.EnvBuilder()
        self.run_with_capture(builder.create, self.env_dir)
        context = builder.ensure_directories(self.env_dir)
        data = self.get_text_file_contents('pyvenv.cfg')
        self.assertEqual(context.prompt, '(%s) ' % env_name)
        self.assertNotIn("prompt = ", data)

        rmtree(self.env_dir)
        builder = venv.EnvBuilder(prompt='My prompt')
        self.run_with_capture(builder.create, self.env_dir)
        context = builder.ensure_directories(self.env_dir)
        data = self.get_text_file_contents('pyvenv.cfg')
        self.assertEqual(context.prompt, '(My prompt) ')
        self.assertIn("prompt = 'My prompt'\n", data)

    @requireVenvCreate
    eleza test_prefixes(self):
        """
        Test that the prefix values are kama expected.
        """
        # check a venv's prefixes
        rmtree(self.env_dir)
        self.run_with_capture(venv.create, self.env_dir)
        envpy = os.path.join(self.env_dir, self.bindir, self.exe)
        cmd = [envpy, '-c', Tupu]
        kila prefix, expected kwenye (
            ('prefix', self.env_dir),
            ('exec_prefix', self.env_dir),
            ('base_prefix', sys.base_prefix),
            ('base_exec_prefix', sys.base_exec_prefix)):
            cmd[2] = 'agiza sys; andika(sys.%s)' % prefix
            out, err = check_output(cmd)
            self.assertEqual(out.strip(), expected.encode())

    ikiwa sys.platform == 'win32':
        ENV_SUBDIRS = (
            ('Scripts',),
            ('Include',),
            ('Lib',),
            ('Lib', 'site-packages'),
        )
    isipokua:
        ENV_SUBDIRS = (
            ('bin',),
            ('include',),
            ('lib',),
            ('lib', 'python%d.%d' % sys.version_info[:2]),
            ('lib', 'python%d.%d' % sys.version_info[:2], 'site-packages'),
        )

    eleza create_contents(self, paths, filename):
        """
        Create some files kwenye the environment which are unrelated
        to the virtual environment.
        """
        kila subdirs kwenye paths:
            d = os.path.join(self.env_dir, *subdirs)
            os.mkdir(d)
            fn = os.path.join(d, filename)
            ukijumuisha open(fn, 'wb') kama f:
                f.write(b'Still here?')

    eleza test_overwrite_existing(self):
        """
        Test creating environment kwenye an existing directory.
        """
        self.create_contents(self.ENV_SUBDIRS, 'foo')
        venv.create(self.env_dir)
        kila subdirs kwenye self.ENV_SUBDIRS:
            fn = os.path.join(self.env_dir, *(subdirs + ('foo',)))
            self.assertKweli(os.path.exists(fn))
            ukijumuisha open(fn, 'rb') kama f:
                self.assertEqual(f.read(), b'Still here?')

        builder = venv.EnvBuilder(clear=Kweli)
        builder.create(self.env_dir)
        kila subdirs kwenye self.ENV_SUBDIRS:
            fn = os.path.join(self.env_dir, *(subdirs + ('foo',)))
            self.assertUongo(os.path.exists(fn))

    eleza clear_directory(self, path):
        kila fn kwenye os.listdir(path):
            fn = os.path.join(path, fn)
            ikiwa os.path.islink(fn) ama os.path.isfile(fn):
                os.remove(fn)
            lasivyo os.path.isdir(fn):
                rmtree(fn)

    eleza test_unoverwritable_fails(self):
        #create a file clashing ukijumuisha directories kwenye the env dir
        kila paths kwenye self.ENV_SUBDIRS[:3]:
            fn = os.path.join(self.env_dir, *paths)
            ukijumuisha open(fn, 'wb') kama f:
                f.write(b'')
            self.assertRaises((ValueError, OSError), venv.create, self.env_dir)
            self.clear_directory(self.env_dir)

    eleza test_upgrade(self):
        """
        Test upgrading an existing environment directory.
        """
        # See Issue #21643: the loop needs to run twice to ensure
        # that everything works on the upgrade (the first run just creates
        # the venv).
        kila upgrade kwenye (Uongo, Kweli):
            builder = venv.EnvBuilder(upgrade=upgrade)
            self.run_with_capture(builder.create, self.env_dir)
            self.isdir(self.bindir)
            self.isdir(self.include)
            self.isdir(*self.lib)
            fn = self.get_env_file(self.bindir, self.exe)
            ikiwa sio os.path.exists(fn):
                # diagnostics kila Windows buildbot failures
                bd = self.get_env_file(self.bindir)
                andika('Contents of %r:' % bd)
                andika('    %r' % os.listdir(bd))
            self.assertKweli(os.path.exists(fn), 'File %r should exist.' % fn)

    eleza test_isolation(self):
        """
        Test isolation kutoka system site-packages
        """
        kila ssp, s kwenye ((Kweli, 'true'), (Uongo, 'false')):
            builder = venv.EnvBuilder(clear=Kweli, system_site_packages=ssp)
            builder.create(self.env_dir)
            data = self.get_text_file_contents('pyvenv.cfg')
            self.assertIn('include-system-site-packages = %s\n' % s, data)

    @unittest.skipUnless(can_symlink(), 'Needs symlinks')
    eleza test_symlinking(self):
        """
        Test symlinking works kama expected
        """
        kila usl kwenye (Uongo, Kweli):
            builder = venv.EnvBuilder(clear=Kweli, symlinks=usl)
            builder.create(self.env_dir)
            fn = self.get_env_file(self.bindir, self.exe)
            # Don't test when Uongo, because e.g. 'python' ni always
            # symlinked to 'python3.3' kwenye the env, even when symlinking in
            # general isn't wanted.
            ikiwa usl:
                ikiwa self.cannot_link_exe:
                    # Symlinking ni skipped when our executable ni already a
                    # special app symlink
                    self.assertUongo(os.path.islink(fn))
                isipokua:
                    self.assertKweli(os.path.islink(fn))

    # If a venv ni created kutoka a source build na that venv ni used to
    # run the test, the pyvenv.cfg kwenye the venv created kwenye the test will
    # point to the venv being used to run the test, na we lose the link
    # to the source build - so Python can't initialise properly.
    @requireVenvCreate
    eleza test_executable(self):
        """
        Test that the sys.executable value ni kama expected.
        """
        rmtree(self.env_dir)
        self.run_with_capture(venv.create, self.env_dir)
        envpy = os.path.join(os.path.realpath(self.env_dir),
                             self.bindir, self.exe)
        out, err = check_output([envpy, '-c',
            'agiza sys; andika(sys.executable)'])
        self.assertEqual(out.strip(), envpy.encode())

    @unittest.skipUnless(can_symlink(), 'Needs symlinks')
    eleza test_executable_symlinks(self):
        """
        Test that the sys.executable value ni kama expected.
        """
        rmtree(self.env_dir)
        builder = venv.EnvBuilder(clear=Kweli, symlinks=Kweli)
        builder.create(self.env_dir)
        envpy = os.path.join(os.path.realpath(self.env_dir),
                             self.bindir, self.exe)
        out, err = check_output([envpy, '-c',
            'agiza sys; andika(sys.executable)'])
        self.assertEqual(out.strip(), envpy.encode())

    @unittest.skipUnless(os.name == 'nt', 'only relevant on Windows')
    eleza test_unicode_in_batch_file(self):
        """
        Test handling of Unicode paths
        """
        rmtree(self.env_dir)
        env_dir = os.path.join(os.path.realpath(self.env_dir), 'ϼўТλФЙ')
        builder = venv.EnvBuilder(clear=Kweli)
        builder.create(env_dir)
        activate = os.path.join(env_dir, self.bindir, 'activate.bat')
        envpy = os.path.join(env_dir, self.bindir, self.exe)
        out, err = check_output(
            [activate, '&', self.exe, '-c', 'andika(0)'],
            encoding='oem',
        )
        self.assertEqual(out.strip(), '0')

    @requireVenvCreate
    eleza test_multiprocessing(self):
        """
        Test that the multiprocessing ni able to spawn.
        """
        # Issue bpo-36342: Instanciation of a Pool object imports the
        # multiprocessing.synchronize module. Skip the test ikiwa this module
        # cannot be imported.
        import_module('multiprocessing.synchronize')
        rmtree(self.env_dir)
        self.run_with_capture(venv.create, self.env_dir)
        envpy = os.path.join(os.path.realpath(self.env_dir),
                             self.bindir, self.exe)
        out, err = check_output([envpy, '-c',
            'kutoka multiprocessing agiza Pool; '
            'pool = Pool(1); '
            'andika(pool.apply_async("Python".lower).get(3)); '
            'pool.terminate()'])
        self.assertEqual(out.strip(), "python".encode())

    @unittest.skipIf(os.name == 'nt', 'not relevant on Windows')
    eleza test_deactivate_with_strict_bash_opts(self):
        bash = shutil.which("bash")
        ikiwa bash ni Tupu:
            self.skipTest("bash required kila this test")
        rmtree(self.env_dir)
        builder = venv.EnvBuilder(clear=Kweli)
        builder.create(self.env_dir)
        activate = os.path.join(self.env_dir, self.bindir, "activate")
        test_script = os.path.join(self.env_dir, "test_strict.sh")
        ukijumuisha open(test_script, "w") kama f:
            f.write("set -euo pipefail\n"
                    f"source {activate}\n"
                    "deactivate\n")
        out, err = check_output([bash, test_script])
        self.assertEqual(out, "".encode())
        self.assertEqual(err, "".encode())


@requireVenvCreate
kundi EnsurePipTest(BaseTest):
    """Test venv module installation of pip."""
    eleza assert_pip_not_installed(self):
        envpy = os.path.join(os.path.realpath(self.env_dir),
                             self.bindir, self.exe)
        out, err = check_output([envpy, '-c',
            'jaribu:\n agiza pip\ntatizo ImportError:\n andika("OK")'])
        # We force everything to text, so unittest gives the detailed diff
        # ikiwa we get unexpected results
        err = err.decode("latin-1") # Force to text, prevent decoding errors
        self.assertEqual(err, "")
        out = out.decode("latin-1") # Force to text, prevent decoding errors
        self.assertEqual(out.strip(), "OK")


    eleza test_no_pip_by_default(self):
        rmtree(self.env_dir)
        self.run_with_capture(venv.create, self.env_dir)
        self.assert_pip_not_installed()

    eleza test_explicit_no_pip(self):
        rmtree(self.env_dir)
        self.run_with_capture(venv.create, self.env_dir, with_pip=Uongo)
        self.assert_pip_not_installed()

    eleza test_devnull(self):
        # Fix kila issue #20053 uses os.devnull to force a config file to
        # appear empty. However http://bugs.python.org/issue20541 means
        # that doesn't currently work properly on Windows. Once that is
        # fixed, the "win_location" part of test_with_pip should be restored
        ukijumuisha open(os.devnull, "rb") kama f:
            self.assertEqual(f.read(), b"")

        self.assertKweli(os.path.exists(os.devnull))

    eleza do_test_with_pip(self, system_site_packages):
        rmtree(self.env_dir)
        ukijumuisha EnvironmentVarGuard() kama envvars:
            # pip's cross-version compatibility may trigger deprecation
            # warnings kwenye current versions of Python. Ensure related
            # environment settings don't cause venv to fail.
            envvars["PYTHONWARNINGS"] = "e"
            # ensurepip ni different enough kutoka a normal pip invocation
            # that we want to ensure it ignores the normal pip environment
            # variable settings. We set PIP_NO_INSTALL here specifically
            # to check that ensurepip (and hence venv) ignores it.
            # See http://bugs.python.org/issue19734
            envvars["PIP_NO_INSTALL"] = "1"
            # Also check that we ignore the pip configuration file
            # See http://bugs.python.org/issue20053
            ukijumuisha tempfile.TemporaryDirectory() kama home_dir:
                envvars["HOME"] = home_dir
                bad_config = "[global]\nno-install=1"
                # Write to both config file names on all platforms to reduce
                # cross-platform variation kwenye test code behaviour
                win_location = ("pip", "pip.ini")
                posix_location = (".pip", "pip.conf")
                # Skips win_location due to http://bugs.python.org/issue20541
                kila dirname, fname kwenye (posix_location,):
                    dirpath = os.path.join(home_dir, dirname)
                    os.mkdir(dirpath)
                    fpath = os.path.join(dirpath, fname)
                    ukijumuisha open(fpath, 'w') kama f:
                        f.write(bad_config)

                # Actually run the create command ukijumuisha all that unhelpful
                # config kwenye place to ensure we ignore it
                jaribu:
                    self.run_with_capture(venv.create, self.env_dir,
                                          system_site_packages=system_site_packages,
                                          with_pip=Kweli)
                tatizo subprocess.CalledProcessError kama exc:
                    # The output this produces can be a little hard to read,
                    # but at least it has all the details
                    details = exc.output.decode(errors="replace")
                    msg = "{}\n\n**Subprocess Output**\n{}"
                    self.fail(msg.format(exc, details))
        # Ensure pip ni available kwenye the virtual environment
        envpy = os.path.join(os.path.realpath(self.env_dir), self.bindir, self.exe)
        # Ignore DeprecationWarning since pip code ni sio part of Python
        out, err = check_output([envpy, '-W', 'ignore::DeprecationWarning', '-I',
               '-m', 'pip', '--version'])
        # We force everything to text, so unittest gives the detailed diff
        # ikiwa we get unexpected results
        err = err.decode("latin-1") # Force to text, prevent decoding errors
        self.assertEqual(err, "")
        out = out.decode("latin-1") # Force to text, prevent decoding errors
        expected_version = "pip {}".format(ensurepip.version())
        self.assertEqual(out[:len(expected_version)], expected_version)
        env_dir = os.fsencode(self.env_dir).decode("latin-1")
        self.assertIn(env_dir, out)

        # http://bugs.python.org/issue19728
        # Check the private uninstall command provided kila the Windows
        # installers works (at least kwenye a virtual environment)
        ukijumuisha EnvironmentVarGuard() kama envvars:
            out, err = check_output([envpy,
                '-W', 'ignore::DeprecationWarning', '-I',
                '-m', 'ensurepip._uninstall'])
        # We force everything to text, so unittest gives the detailed diff
        # ikiwa we get unexpected results
        err = err.decode("latin-1") # Force to text, prevent decoding errors
        # Ignore the warning:
        #   "The directory '$HOME/.cache/pip/http' ama its parent directory
        #    ni sio owned by the current user na the cache has been disabled.
        #    Please check the permissions na owner of that directory. If
        #    executing pip ukijumuisha sudo, you may want sudo's -H flag."
        # where $HOME ni replaced by the HOME environment variable.
        err = re.sub("^(WARNING: )?The directory .* ama its parent directory "
                     "is sio owned by the current user .*$", "",
                     err, flags=re.MULTILINE)
        self.assertEqual(err.rstrip(), "")
        # Being fairly specific regarding the expected behaviour kila the
        # initial bundling phase kwenye Python 3.4. If the output changes in
        # future pip versions, this test can likely be relaxed further.
        out = out.decode("latin-1") # Force to text, prevent decoding errors
        self.assertIn("Successfully uninstalled pip", out)
        self.assertIn("Successfully uninstalled setuptools", out)
        # Check pip ni now gone kutoka the virtual environment. This only
        # applies kwenye the system_site_packages=Uongo case, because kwenye the
        # other case, pip may still be available kwenye the system site-packages
        ikiwa sio system_site_packages:
            self.assert_pip_not_installed()

    # Issue #26610: pip/pep425tags.py requires ctypes
    @unittest.skipUnless(ctypes, 'pip requires ctypes')
    @requires_zlib
    eleza test_with_pip(self):
        self.do_test_with_pip(Uongo)
        self.do_test_with_pip(Kweli)

ikiwa __name__ == "__main__":
    unittest.main()
