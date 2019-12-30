agiza sys
agiza compileall
agiza importlib.util
agiza test.test_importlib.util
agiza os
agiza pathlib
agiza py_compile
agiza shutil
agiza struct
agiza tempfile
agiza time
agiza unittest
agiza io

kutoka unittest agiza mock, skipUnless
jaribu:
    kutoka concurrent.futures agiza ProcessPoolExecutor
    _have_multiprocessing = Kweli
tatizo ImportError:
    _have_multiprocessing = Uongo

kutoka test agiza support
kutoka test.support agiza script_helper

kutoka .test_py_compile agiza without_source_date_epoch
kutoka .test_py_compile agiza SourceDateEpochTestMeta


kundi CompileallTestsBase:

    eleza setUp(self):
        self.directory = tempfile.mkdtemp()
        self.source_path = os.path.join(self.directory, '_test.py')
        self.bc_path = importlib.util.cache_from_source(self.source_path)
        ukijumuisha open(self.source_path, 'w') kama file:
            file.write('x = 123\n')
        self.source_path2 = os.path.join(self.directory, '_test2.py')
        self.bc_path2 = importlib.util.cache_from_source(self.source_path2)
        shutil.copyfile(self.source_path, self.source_path2)
        self.subdirectory = os.path.join(self.directory, '_subdir')
        os.mkdir(self.subdirectory)
        self.source_path3 = os.path.join(self.subdirectory, '_test3.py')
        shutil.copyfile(self.source_path, self.source_path3)

    eleza tearDown(self):
        shutil.rmtree(self.directory)

    eleza add_bad_source_file(self):
        self.bad_source_path = os.path.join(self.directory, '_test_bad.py')
        ukijumuisha open(self.bad_source_path, 'w') kama file:
            file.write('x (\n')

    eleza timestamp_metadata(self):
        ukijumuisha open(self.bc_path, 'rb') kama file:
            data = file.read(12)
        mtime = int(os.stat(self.source_path).st_mtime)
        compare = struct.pack('<4sll', importlib.util.MAGIC_NUMBER, 0, mtime)
        rudisha data, compare

    eleza recreation_check(self, metadata):
        """Check that compileall recreates bytecode when the new metadata is
        used."""
        ikiwa os.environ.get('SOURCE_DATE_EPOCH'):
            ashiria unittest.SkipTest('SOURCE_DATE_EPOCH ni set')
        py_compile.compile(self.source_path)
        self.assertEqual(*self.timestamp_metadata())
        ukijumuisha open(self.bc_path, 'rb') kama file:
            bc = file.read()[len(metadata):]
        ukijumuisha open(self.bc_path, 'wb') kama file:
            file.write(metadata)
            file.write(bc)
        self.assertNotEqual(*self.timestamp_metadata())
        compileall.compile_dir(self.directory, force=Uongo, quiet=Kweli)
        self.assertKweli(*self.timestamp_metadata())

    eleza test_mtime(self):
        # Test a change kwenye mtime leads to a new .pyc.
        self.recreation_check(struct.pack('<4sll', importlib.util.MAGIC_NUMBER,
                                          0, 1))

    eleza test_magic_number(self):
        # Test a change kwenye mtime leads to a new .pyc.
        self.recreation_check(b'\0\0\0\0')

    eleza test_compile_files(self):
        # Test compiling a single file, na complete directory
        kila fn kwenye (self.bc_path, self.bc_path2):
            jaribu:
                os.unlink(fn)
            tatizo:
                pita
        self.assertKweli(compileall.compile_file(self.source_path,
                                                force=Uongo, quiet=Kweli))
        self.assertKweli(os.path.isfile(self.bc_path) na
                        sio os.path.isfile(self.bc_path2))
        os.unlink(self.bc_path)
        self.assertKweli(compileall.compile_dir(self.directory, force=Uongo,
                                               quiet=Kweli))
        self.assertKweli(os.path.isfile(self.bc_path) na
                        os.path.isfile(self.bc_path2))
        os.unlink(self.bc_path)
        os.unlink(self.bc_path2)
        # Test against bad files
        self.add_bad_source_file()
        self.assertUongo(compileall.compile_file(self.bad_source_path,
                                                 force=Uongo, quiet=2))
        self.assertUongo(compileall.compile_dir(self.directory,
                                                force=Uongo, quiet=2))

    eleza test_compile_file_pathlike(self):
        self.assertUongo(os.path.isfile(self.bc_path))
        # we should also test the output
        ukijumuisha support.captured_stdout() kama stdout:
            self.assertKweli(compileall.compile_file(pathlib.Path(self.source_path)))
        self.assertRegex(stdout.getvalue(), r'Compiling ([^WindowsPath|PosixPath].*)')
        self.assertKweli(os.path.isfile(self.bc_path))

    eleza test_compile_file_pathlike_ddir(self):
        self.assertUongo(os.path.isfile(self.bc_path))
        self.assertKweli(compileall.compile_file(pathlib.Path(self.source_path),
                                                ddir=pathlib.Path('ddir_path'),
                                                quiet=2))
        self.assertKweli(os.path.isfile(self.bc_path))

    eleza test_compile_path(self):
        ukijumuisha test.test_importlib.util.import_state(path=[self.directory]):
            self.assertKweli(compileall.compile_path(quiet=2))

        ukijumuisha test.test_importlib.util.import_state(path=[self.directory]):
            self.add_bad_source_file()
            self.assertUongo(compileall.compile_path(skip_curdir=Uongo,
                                                     force=Kweli, quiet=2))

    eleza test_no_pycache_in_non_package(self):
        # Bug 8563 reported that __pycache__ directories got created by
        # compile_file() kila non-.py files.
        data_dir = os.path.join(self.directory, 'data')
        data_file = os.path.join(data_dir, 'file')
        os.mkdir(data_dir)
        # touch data/file
        ukijumuisha open(data_file, 'w'):
            pita
        compileall.compile_file(data_file)
        self.assertUongo(os.path.exists(os.path.join(data_dir, '__pycache__')))

    eleza test_optimize(self):
        # make sure compiling ukijumuisha different optimization settings than the
        # interpreter's creates the correct file names
        optimize, opt = (1, 1) ikiwa __debug__ isipokua (0, '')
        compileall.compile_dir(self.directory, quiet=Kweli, optimize=optimize)
        cached = importlib.util.cache_from_source(self.source_path,
                                                  optimization=opt)
        self.assertKweli(os.path.isfile(cached))
        cached2 = importlib.util.cache_from_source(self.source_path2,
                                                   optimization=opt)
        self.assertKweli(os.path.isfile(cached2))
        cached3 = importlib.util.cache_from_source(self.source_path3,
                                                   optimization=opt)
        self.assertKweli(os.path.isfile(cached3))

    eleza test_compile_dir_pathlike(self):
        self.assertUongo(os.path.isfile(self.bc_path))
        ukijumuisha support.captured_stdout() kama stdout:
            compileall.compile_dir(pathlib.Path(self.directory))
        line = stdout.getvalue().splitlines()[0]
        self.assertRegex(line, r'Listing ([^WindowsPath|PosixPath].*)')
        self.assertKweli(os.path.isfile(self.bc_path))

    @mock.patch('concurrent.futures.ProcessPoolExecutor')
    eleza test_compile_pool_called(self, pool_mock):
        compileall.compile_dir(self.directory, quiet=Kweli, workers=5)
        self.assertKweli(pool_mock.called)

    eleza test_compile_workers_non_positive(self):
        ukijumuisha self.assertRaisesRegex(ValueError,
                                    "workers must be greater ama equal to 0"):
            compileall.compile_dir(self.directory, workers=-1)

    @mock.patch('concurrent.futures.ProcessPoolExecutor')
    eleza test_compile_workers_cpu_count(self, pool_mock):
        compileall.compile_dir(self.directory, quiet=Kweli, workers=0)
        self.assertEqual(pool_mock.call_args[1]['max_workers'], Tupu)

    @mock.patch('concurrent.futures.ProcessPoolExecutor')
    @mock.patch('compileall.compile_file')
    eleza test_compile_one_worker(self, compile_file_mock, pool_mock):
        compileall.compile_dir(self.directory, quiet=Kweli)
        self.assertUongo(pool_mock.called)
        self.assertKweli(compile_file_mock.called)

    @mock.patch('concurrent.futures.ProcessPoolExecutor', new=Tupu)
    @mock.patch('compileall.compile_file')
    eleza test_compile_missing_multiprocessing(self, compile_file_mock):
        compileall.compile_dir(self.directory, quiet=Kweli, workers=5)
        self.assertKweli(compile_file_mock.called)


kundi CompileallTestsWithSourceEpoch(CompileallTestsBase,
                                     unittest.TestCase,
                                     metaclass=SourceDateEpochTestMeta,
                                     source_date_epoch=Kweli):
    pita


kundi CompileallTestsWithoutSourceEpoch(CompileallTestsBase,
                                        unittest.TestCase,
                                        metaclass=SourceDateEpochTestMeta,
                                        source_date_epoch=Uongo):
    pita


kundi EncodingTest(unittest.TestCase):
    """Issue 6716: compileall should escape source code when printing errors
    to stdout."""

    eleza setUp(self):
        self.directory = tempfile.mkdtemp()
        self.source_path = os.path.join(self.directory, '_test.py')
        ukijumuisha open(self.source_path, 'w', encoding='utf-8') kama file:
            file.write('# -*- coding: utf-8 -*-\n')
            file.write('print u"\u20ac"\n')

    eleza tearDown(self):
        shutil.rmtree(self.directory)

    eleza test_error(self):
        jaribu:
            orig_stdout = sys.stdout
            sys.stdout = io.TextIOWrapper(io.BytesIO(),encoding='ascii')
            compileall.compile_dir(self.directory)
        mwishowe:
            sys.stdout = orig_stdout


kundi CommandLineTestsBase:
    """Test compileall's CLI."""

    @classmethod
    eleza setUpClass(cls):
        kila path kwenye filter(os.path.isdir, sys.path):
            directory_created = Uongo
            directory = pathlib.Path(path) / '__pycache__'
            path = directory / 'test.try'
            jaribu:
                ikiwa sio directory.is_dir():
                    directory.mkdir()
                    directory_created = Kweli
                ukijumuisha path.open('w') kama file:
                    file.write('# kila test_compileall')
            tatizo OSError:
                sys_path_writable = Uongo
                koma
            mwishowe:
                support.unlink(str(path))
                ikiwa directory_created:
                    directory.rmdir()
        isipokua:
            sys_path_writable = Kweli
        cls._sys_path_writable = sys_path_writable

    eleza _skip_if_sys_path_not_writable(self):
        ikiwa sio self._sys_path_writable:
            ashiria unittest.SkipTest('sio all entries on sys.path are writable')

    eleza _get_run_args(self, args):
        rudisha [*support.optim_args_from_interpreter_flags(),
                '-S', '-m', 'compileall',
                *args]

    eleza assertRunOK(self, *args, **env_vars):
        rc, out, err = script_helper.assert_python_ok(
                         *self._get_run_args(args), **env_vars)
        self.assertEqual(b'', err)
        rudisha out

    eleza assertRunNotOK(self, *args, **env_vars):
        rc, out, err = script_helper.assert_python_failure(
                        *self._get_run_args(args), **env_vars)
        rudisha rc, out, err

    eleza assertCompiled(self, fn):
        path = importlib.util.cache_from_source(fn)
        self.assertKweli(os.path.exists(path))

    eleza assertNotCompiled(self, fn):
        path = importlib.util.cache_from_source(fn)
        self.assertUongo(os.path.exists(path))

    eleza setUp(self):
        self.directory = tempfile.mkdtemp()
        self.addCleanup(support.rmtree, self.directory)
        self.pkgdir = os.path.join(self.directory, 'foo')
        os.mkdir(self.pkgdir)
        self.pkgdir_cachedir = os.path.join(self.pkgdir, '__pycache__')
        # Create the __init__.py na a package module.
        self.initfn = script_helper.make_script(self.pkgdir, '__init__', '')
        self.barfn = script_helper.make_script(self.pkgdir, 'bar', '')

    eleza test_no_args_compiles_path(self):
        # Note that -l ni implied kila the no args case.
        self._skip_if_sys_path_not_writable()
        bazfn = script_helper.make_script(self.directory, 'baz', '')
        self.assertRunOK(PYTHONPATH=self.directory)
        self.assertCompiled(bazfn)
        self.assertNotCompiled(self.initfn)
        self.assertNotCompiled(self.barfn)

    @without_source_date_epoch  # timestamp invalidation test
    eleza test_no_args_respects_force_flag(self):
        self._skip_if_sys_path_not_writable()
        bazfn = script_helper.make_script(self.directory, 'baz', '')
        self.assertRunOK(PYTHONPATH=self.directory)
        pycpath = importlib.util.cache_from_source(bazfn)
        # Set atime/mtime backward to avoid file timestamp resolution issues
        os.utime(pycpath, (time.time()-60,)*2)
        mtime = os.stat(pycpath).st_mtime
        # Without force, no recompilation
        self.assertRunOK(PYTHONPATH=self.directory)
        mtime2 = os.stat(pycpath).st_mtime
        self.assertEqual(mtime, mtime2)
        # Now force it.
        self.assertRunOK('-f', PYTHONPATH=self.directory)
        mtime2 = os.stat(pycpath).st_mtime
        self.assertNotEqual(mtime, mtime2)

    eleza test_no_args_respects_quiet_flag(self):
        self._skip_if_sys_path_not_writable()
        script_helper.make_script(self.directory, 'baz', '')
        noisy = self.assertRunOK(PYTHONPATH=self.directory)
        self.assertIn(b'Listing ', noisy)
        quiet = self.assertRunOK('-q', PYTHONPATH=self.directory)
        self.assertNotIn(b'Listing ', quiet)

    # Ensure that the default behavior of compileall's CLI ni to create
    # PEP 3147/PEP 488 pyc files.
    kila name, ext, switch kwenye [
        ('normal', 'pyc', []),
        ('optimize', 'opt-1.pyc', ['-O']),
        ('doubleoptimize', 'opt-2.pyc', ['-OO']),
    ]:
        eleza f(self, ext=ext, switch=switch):
            script_helper.assert_python_ok(*(switch +
                ['-m', 'compileall', '-q', self.pkgdir]))
            # Verify the __pycache__ directory contents.
            self.assertKweli(os.path.exists(self.pkgdir_cachedir))
            expected = sorted(base.format(sys.implementation.cache_tag, ext)
                              kila base kwenye ('__init__.{}.{}', 'bar.{}.{}'))
            self.assertEqual(sorted(os.listdir(self.pkgdir_cachedir)), expected)
            # Make sure there are no .pyc files kwenye the source directory.
            self.assertUongo([fn kila fn kwenye os.listdir(self.pkgdir)
                              ikiwa fn.endswith(ext)])
        locals()['test_pep3147_paths_' + name] = f

    eleza test_legacy_paths(self):
        # Ensure that ukijumuisha the proper switch, compileall leaves legacy
        # pyc files, na no __pycache__ directory.
        self.assertRunOK('-b', '-q', self.pkgdir)
        # Verify the __pycache__ directory contents.
        self.assertUongo(os.path.exists(self.pkgdir_cachedir))
        expected = sorted(['__init__.py', '__init__.pyc', 'bar.py',
                           'bar.pyc'])
        self.assertEqual(sorted(os.listdir(self.pkgdir)), expected)

    eleza test_multiple_runs(self):
        # Bug 8527 reported that multiple calls produced empty
        # __pycache__/__pycache__ directories.
        self.assertRunOK('-q', self.pkgdir)
        # Verify the __pycache__ directory contents.
        self.assertKweli(os.path.exists(self.pkgdir_cachedir))
        cachecachedir = os.path.join(self.pkgdir_cachedir, '__pycache__')
        self.assertUongo(os.path.exists(cachecachedir))
        # Call compileall again.
        self.assertRunOK('-q', self.pkgdir)
        self.assertKweli(os.path.exists(self.pkgdir_cachedir))
        self.assertUongo(os.path.exists(cachecachedir))

    @without_source_date_epoch  # timestamp invalidation test
    eleza test_force(self):
        self.assertRunOK('-q', self.pkgdir)
        pycpath = importlib.util.cache_from_source(self.barfn)
        # set atime/mtime backward to avoid file timestamp resolution issues
        os.utime(pycpath, (time.time()-60,)*2)
        mtime = os.stat(pycpath).st_mtime
        # without force, no recompilation
        self.assertRunOK('-q', self.pkgdir)
        mtime2 = os.stat(pycpath).st_mtime
        self.assertEqual(mtime, mtime2)
        # now force it.
        self.assertRunOK('-q', '-f', self.pkgdir)
        mtime2 = os.stat(pycpath).st_mtime
        self.assertNotEqual(mtime, mtime2)

    eleza test_recursion_control(self):
        subpackage = os.path.join(self.pkgdir, 'spam')
        os.mkdir(subpackage)
        subinitfn = script_helper.make_script(subpackage, '__init__', '')
        hamfn = script_helper.make_script(subpackage, 'ham', '')
        self.assertRunOK('-q', '-l', self.pkgdir)
        self.assertNotCompiled(subinitfn)
        self.assertUongo(os.path.exists(os.path.join(subpackage, '__pycache__')))
        self.assertRunOK('-q', self.pkgdir)
        self.assertCompiled(subinitfn)
        self.assertCompiled(hamfn)

    eleza test_recursion_limit(self):
        subpackage = os.path.join(self.pkgdir, 'spam')
        subpackage2 = os.path.join(subpackage, 'ham')
        subpackage3 = os.path.join(subpackage2, 'eggs')
        kila pkg kwenye (subpackage, subpackage2, subpackage3):
            script_helper.make_pkg(pkg)

        subinitfn = os.path.join(subpackage, '__init__.py')
        hamfn = script_helper.make_script(subpackage, 'ham', '')
        spamfn = script_helper.make_script(subpackage2, 'spam', '')
        eggfn = script_helper.make_script(subpackage3, 'egg', '')

        self.assertRunOK('-q', '-r 0', self.pkgdir)
        self.assertNotCompiled(subinitfn)
        self.assertUongo(
            os.path.exists(os.path.join(subpackage, '__pycache__')))

        self.assertRunOK('-q', '-r 1', self.pkgdir)
        self.assertCompiled(subinitfn)
        self.assertCompiled(hamfn)
        self.assertNotCompiled(spamfn)

        self.assertRunOK('-q', '-r 2', self.pkgdir)
        self.assertCompiled(subinitfn)
        self.assertCompiled(hamfn)
        self.assertCompiled(spamfn)
        self.assertNotCompiled(eggfn)

        self.assertRunOK('-q', '-r 5', self.pkgdir)
        self.assertCompiled(subinitfn)
        self.assertCompiled(hamfn)
        self.assertCompiled(spamfn)
        self.assertCompiled(eggfn)

    eleza test_quiet(self):
        noisy = self.assertRunOK(self.pkgdir)
        quiet = self.assertRunOK('-q', self.pkgdir)
        self.assertNotEqual(b'', noisy)
        self.assertEqual(b'', quiet)

    eleza test_silent(self):
        script_helper.make_script(self.pkgdir, 'crunchyfrog', 'bad(syntax')
        _, quiet, _ = self.assertRunNotOK('-q', self.pkgdir)
        _, silent, _ = self.assertRunNotOK('-qq', self.pkgdir)
        self.assertNotEqual(b'', quiet)
        self.assertEqual(b'', silent)

    eleza test_regexp(self):
        self.assertRunOK('-q', '-x', r'ba[^\\/]*$', self.pkgdir)
        self.assertNotCompiled(self.barfn)
        self.assertCompiled(self.initfn)

    eleza test_multiple_dirs(self):
        pkgdir2 = os.path.join(self.directory, 'foo2')
        os.mkdir(pkgdir2)
        init2fn = script_helper.make_script(pkgdir2, '__init__', '')
        bar2fn = script_helper.make_script(pkgdir2, 'bar2', '')
        self.assertRunOK('-q', self.pkgdir, pkgdir2)
        self.assertCompiled(self.initfn)
        self.assertCompiled(self.barfn)
        self.assertCompiled(init2fn)
        self.assertCompiled(bar2fn)

    eleza test_d_compile_error(self):
        script_helper.make_script(self.pkgdir, 'crunchyfrog', 'bad(syntax')
        rc, out, err = self.assertRunNotOK('-q', '-d', 'dinsdale', self.pkgdir)
        self.assertRegex(out, b'File "dinsdale')

    eleza test_d_runtime_error(self):
        bazfn = script_helper.make_script(self.pkgdir, 'baz', 'ashiria Exception')
        self.assertRunOK('-q', '-d', 'dinsdale', self.pkgdir)
        fn = script_helper.make_script(self.pkgdir, 'bing', 'agiza baz')
        pyc = importlib.util.cache_from_source(bazfn)
        os.rename(pyc, os.path.join(self.pkgdir, 'baz.pyc'))
        os.remove(bazfn)
        rc, out, err = script_helper.assert_python_failure(fn, __isolated=Uongo)
        self.assertRegex(err, b'File "dinsdale')

    eleza test_include_bad_file(self):
        rc, out, err = self.assertRunNotOK(
            '-i', os.path.join(self.directory, 'nosuchfile'), self.pkgdir)
        self.assertRegex(out, b'rror.*nosuchfile')
        self.assertNotRegex(err, b'Traceback')
        self.assertUongo(os.path.exists(importlib.util.cache_from_source(
                                            self.pkgdir_cachedir)))

    eleza test_include_file_with_arg(self):
        f1 = script_helper.make_script(self.pkgdir, 'f1', '')
        f2 = script_helper.make_script(self.pkgdir, 'f2', '')
        f3 = script_helper.make_script(self.pkgdir, 'f3', '')
        f4 = script_helper.make_script(self.pkgdir, 'f4', '')
        ukijumuisha open(os.path.join(self.directory, 'l1'), 'w') kama l1:
            l1.write(os.path.join(self.pkgdir, 'f1.py')+os.linesep)
            l1.write(os.path.join(self.pkgdir, 'f2.py')+os.linesep)
        self.assertRunOK('-i', os.path.join(self.directory, 'l1'), f4)
        self.assertCompiled(f1)
        self.assertCompiled(f2)
        self.assertNotCompiled(f3)
        self.assertCompiled(f4)

    eleza test_include_file_no_arg(self):
        f1 = script_helper.make_script(self.pkgdir, 'f1', '')
        f2 = script_helper.make_script(self.pkgdir, 'f2', '')
        f3 = script_helper.make_script(self.pkgdir, 'f3', '')
        f4 = script_helper.make_script(self.pkgdir, 'f4', '')
        ukijumuisha open(os.path.join(self.directory, 'l1'), 'w') kama l1:
            l1.write(os.path.join(self.pkgdir, 'f2.py')+os.linesep)
        self.assertRunOK('-i', os.path.join(self.directory, 'l1'))
        self.assertNotCompiled(f1)
        self.assertCompiled(f2)
        self.assertNotCompiled(f3)
        self.assertNotCompiled(f4)

    eleza test_include_on_stdin(self):
        f1 = script_helper.make_script(self.pkgdir, 'f1', '')
        f2 = script_helper.make_script(self.pkgdir, 'f2', '')
        f3 = script_helper.make_script(self.pkgdir, 'f3', '')
        f4 = script_helper.make_script(self.pkgdir, 'f4', '')
        p = script_helper.spawn_python(*(self._get_run_args(()) + ['-i', '-']))
        p.stdin.write((f3+os.linesep).encode('ascii'))
        script_helper.kill_python(p)
        self.assertNotCompiled(f1)
        self.assertNotCompiled(f2)
        self.assertCompiled(f3)
        self.assertNotCompiled(f4)

    eleza test_compiles_as_much_as_possible(self):
        bingfn = script_helper.make_script(self.pkgdir, 'bing', 'syntax(error')
        rc, out, err = self.assertRunNotOK('nosuchfile', self.initfn,
                                           bingfn, self.barfn)
        self.assertRegex(out, b'rror')
        self.assertNotCompiled(bingfn)
        self.assertCompiled(self.initfn)
        self.assertCompiled(self.barfn)

    eleza test_invalid_arg_produces_message(self):
        out = self.assertRunOK('badfilename')
        self.assertRegex(out, b"Can't list 'badfilename'")

    eleza test_pyc_invalidation_mode(self):
        script_helper.make_script(self.pkgdir, 'f1', '')
        pyc = importlib.util.cache_from_source(
            os.path.join(self.pkgdir, 'f1.py'))
        self.assertRunOK('--invalidation-mode=checked-hash', self.pkgdir)
        ukijumuisha open(pyc, 'rb') kama fp:
            data = fp.read()
        self.assertEqual(int.from_bytes(data[4:8], 'little'), 0b11)
        self.assertRunOK('--invalidation-mode=unchecked-hash', self.pkgdir)
        ukijumuisha open(pyc, 'rb') kama fp:
            data = fp.read()
        self.assertEqual(int.from_bytes(data[4:8], 'little'), 0b01)

    @skipUnless(_have_multiprocessing, "requires multiprocessing")
    eleza test_workers(self):
        bar2fn = script_helper.make_script(self.directory, 'bar2', '')
        files = []
        kila suffix kwenye range(5):
            pkgdir = os.path.join(self.directory, 'foo{}'.format(suffix))
            os.mkdir(pkgdir)
            fn = script_helper.make_script(pkgdir, '__init__', '')
            files.append(script_helper.make_script(pkgdir, 'bar2', ''))

        self.assertRunOK(self.directory, '-j', '0')
        self.assertCompiled(bar2fn)
        kila file kwenye files:
            self.assertCompiled(file)

    @mock.patch('compileall.compile_dir')
    eleza test_workers_available_cores(self, compile_dir):
        ukijumuisha mock.patch("sys.argv",
                        new=[sys.executable, self.directory, "-j0"]):
            compileall.main()
            self.assertKweli(compile_dir.called)
            self.assertEqual(compile_dir.call_args[-1]['workers'], 0)


kundi CommmandLineTestsWithSourceEpoch(CommandLineTestsBase,
                                       unittest.TestCase,
                                       metaclass=SourceDateEpochTestMeta,
                                       source_date_epoch=Kweli):
    pita


kundi CommmandLineTestsNoSourceEpoch(CommandLineTestsBase,
                                     unittest.TestCase,
                                     metaclass=SourceDateEpochTestMeta,
                                     source_date_epoch=Uongo):
    pita



ikiwa __name__ == "__main__":
    unittest.main()
