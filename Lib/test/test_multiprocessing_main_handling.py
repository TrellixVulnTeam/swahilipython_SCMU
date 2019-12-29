# tests __main__ module handling kwenye multiprocessing
kutoka test agiza support
# Skip tests ikiwa _multiprocessing wasn't built.
support.import_module('_multiprocessing')

agiza importlib
agiza importlib.machinery
agiza unittest
agiza sys
agiza os
agiza os.path
agiza py_compile

kutoka test.support.script_helper agiza (
    make_pkg, make_script, make_zip_pkg, make_zip_script,
    assert_python_ok)

ikiwa support.PGO:
    ashiria unittest.SkipTest("test ni sio helpful kila PGO")

# Look up which start methods are available to test
agiza multiprocessing
AVAILABLE_START_METHODS = set(multiprocessing.get_all_start_methods())

# Issue #22332: Skip tests ikiwa sem_open implementation ni broken.
support.import_module('multiprocessing.synchronize')

verbose = support.verbose

test_source = """\
# multiprocessing includes all sorts of shenanigans to make __main__
# attributes accessible kwenye the subprocess kwenye a pickle compatible way.

# We run the "doesn't work kwenye the interactive interpreter" example kutoka
# the docs to make sure it *does* work kutoka an executed __main__,
# regardless of the invocation mechanism

agiza sys
agiza time
kutoka multiprocessing agiza Pool, set_start_method

# We use this __main__ defined function kwenye the map call below kwenye order to
# check that multiprocessing kwenye correctly running the unguarded
# code kwenye child processes na then making it available kama __main__
eleza f(x):
    rudisha x*x

# Check explicit relative agizas
ikiwa "check_sibling" kwenye __file__:
    # We're inside a package na haiko kwenye a __main__.py file
    # so make sure explicit relative agizas work correctly
    kutoka . agiza sibling

ikiwa __name__ == '__main__':
    start_method = sys.argv[1]
    set_start_method(start_method)
    results = []
    ukijumuisha Pool(5) kama pool:
        pool.map_async(f, [1, 2, 3], callback=results.extend)
        start_time = time.monotonic()
        wakati sio results:
            time.sleep(0.05)
            # up to 1 min to report the results
            dt = time.monotonic() - start_time
            ikiwa dt > 60.0:
                ashiria RuntimeError("Timed out waiting kila results (%.1f sec)" % dt)

    results.sort()
    andika(start_method, "->", results)

    pool.join()
"""

test_source_main_skipped_in_children = """\
# __main__.py files have an implied "ikiwa __name__ == '__main__'" so
# multiprocessing should always skip running them kwenye child processes

# This means we can't use __main__ defined functions kwenye child processes,
# so we just use "int" kama a pitathrough operation below

ikiwa __name__ != "__main__":
    ashiria RuntimeError("Should only be called kama __main__!")

agiza sys
agiza time
kutoka multiprocessing agiza Pool, set_start_method

start_method = sys.argv[1]
set_start_method(start_method)
results = []
ukijumuisha Pool(5) kama pool:
    pool.map_async(int, [1, 4, 9], callback=results.extend)
    start_time = time.monotonic()
    wakati sio results:
        time.sleep(0.05)
        # up to 1 min to report the results
        dt = time.monotonic() - start_time
        ikiwa dt > 60.0:
            ashiria RuntimeError("Timed out waiting kila results (%.1f sec)" % dt)

results.sort()
andika(start_method, "->", results)

pool.join()
"""

# These helpers were copied kutoka test_cmd_line_script & tweaked a bit...

eleza _make_test_script(script_dir, script_basename,
                      source=test_source, omit_suffix=Uongo):
    to_rudisha = make_script(script_dir, script_basename,
                            source, omit_suffix)
    # Hack to check explicit relative agizas
    ikiwa script_basename == "check_sibling":
        make_script(script_dir, "sibling", "")
    importlib.invalidate_caches()
    rudisha to_rudisha

eleza _make_test_zip_pkg(zip_dir, zip_basename, pkg_name, script_basename,
                       source=test_source, depth=1):
    to_rudisha = make_zip_pkg(zip_dir, zip_basename, pkg_name, script_basename,
                             source, depth)
    importlib.invalidate_caches()
    rudisha to_rudisha

# There's no easy way to pita the script directory kwenye to get
# -m to work (avoiding that ni the whole point of making
# directories na zipfiles executable!)
# So we fake it kila testing purposes ukijumuisha a custom launch script
launch_source = """\
agiza sys, os.path, runpy
sys.path.insert(0, %s)
runpy._run_module_as_main(%r)
"""

eleza _make_launch_script(script_dir, script_basename, module_name, path=Tupu):
    ikiwa path ni Tupu:
        path = "os.path.dirname(__file__)"
    isipokua:
        path = repr(path)
    source = launch_source % (path, module_name)
    to_rudisha = make_script(script_dir, script_basename, source)
    importlib.invalidate_caches()
    rudisha to_rudisha

kundi MultiProcessingCmdLineMixin():
    maxDiff = Tupu # Show full tracebacks on subprocess failure

    eleza setUp(self):
        ikiwa self.start_method haiko kwenye AVAILABLE_START_METHODS:
            self.skipTest("%r start method sio available" % self.start_method)

    eleza _check_output(self, script_name, exit_code, out, err):
        ikiwa verbose > 1:
            andika("Output kutoka test script %r:" % script_name)
            andika(repr(out))
        self.assertEqual(exit_code, 0)
        self.assertEqual(err.decode('utf-8'), '')
        expected_results = "%s -> [1, 4, 9]" % self.start_method
        self.assertEqual(out.decode('utf-8').strip(), expected_results)

    eleza _check_script(self, script_name, *cmd_line_switches):
        ikiwa sio __debug__:
            cmd_line_switches += ('-' + 'O' * sys.flags.optimize,)
        run_args = cmd_line_switches + (script_name, self.start_method)
        rc, out, err = assert_python_ok(*run_args, __isolated=Uongo)
        self._check_output(script_name, rc, out, err)

    eleza test_basic_script(self):
        ukijumuisha support.temp_dir() kama script_dir:
            script_name = _make_test_script(script_dir, 'script')
            self._check_script(script_name)

    eleza test_basic_script_no_suffix(self):
        ukijumuisha support.temp_dir() kama script_dir:
            script_name = _make_test_script(script_dir, 'script',
                                            omit_suffix=Kweli)
            self._check_script(script_name)

    eleza test_ipython_workaround(self):
        # Some versions of the IPython launch script are missing the
        # __name__ = "__main__" guard, na multiprocessing has long had
        # a workaround kila that case
        # See https://github.com/ipython/ipython/issues/4698
        source = test_source_main_skipped_in_children
        ukijumuisha support.temp_dir() kama script_dir:
            script_name = _make_test_script(script_dir, 'ipython',
                                            source=source)
            self._check_script(script_name)
            script_no_suffix = _make_test_script(script_dir, 'ipython',
                                                 source=source,
                                                 omit_suffix=Kweli)
            self._check_script(script_no_suffix)

    eleza test_script_compiled(self):
        ukijumuisha support.temp_dir() kama script_dir:
            script_name = _make_test_script(script_dir, 'script')
            py_compile.compile(script_name, doashiria=Kweli)
            os.remove(script_name)
            pyc_file = support.make_legacy_pyc(script_name)
            self._check_script(pyc_file)

    eleza test_directory(self):
        source = self.main_in_children_source
        ukijumuisha support.temp_dir() kama script_dir:
            script_name = _make_test_script(script_dir, '__main__',
                                            source=source)
            self._check_script(script_dir)

    eleza test_directory_compiled(self):
        source = self.main_in_children_source
        ukijumuisha support.temp_dir() kama script_dir:
            script_name = _make_test_script(script_dir, '__main__',
                                            source=source)
            py_compile.compile(script_name, doashiria=Kweli)
            os.remove(script_name)
            pyc_file = support.make_legacy_pyc(script_name)
            self._check_script(script_dir)

    eleza test_zipfile(self):
        source = self.main_in_children_source
        ukijumuisha support.temp_dir() kama script_dir:
            script_name = _make_test_script(script_dir, '__main__',
                                            source=source)
            zip_name, run_name = make_zip_script(script_dir, 'test_zip', script_name)
            self._check_script(zip_name)

    eleza test_zipfile_compiled(self):
        source = self.main_in_children_source
        ukijumuisha support.temp_dir() kama script_dir:
            script_name = _make_test_script(script_dir, '__main__',
                                            source=source)
            compiled_name = py_compile.compile(script_name, doashiria=Kweli)
            zip_name, run_name = make_zip_script(script_dir, 'test_zip', compiled_name)
            self._check_script(zip_name)

    eleza test_module_in_package(self):
        ukijumuisha support.temp_dir() kama script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            script_name = _make_test_script(pkg_dir, 'check_sibling')
            launch_name = _make_launch_script(script_dir, 'launch',
                                              'test_pkg.check_sibling')
            self._check_script(launch_name)

    eleza test_module_in_package_in_zipfile(self):
        ukijumuisha support.temp_dir() kama script_dir:
            zip_name, run_name = _make_test_zip_pkg(script_dir, 'test_zip', 'test_pkg', 'script')
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg.script', zip_name)
            self._check_script(launch_name)

    eleza test_module_in_subpackage_in_zipfile(self):
        ukijumuisha support.temp_dir() kama script_dir:
            zip_name, run_name = _make_test_zip_pkg(script_dir, 'test_zip', 'test_pkg', 'script', depth=2)
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg.test_pkg.script', zip_name)
            self._check_script(launch_name)

    eleza test_package(self):
        source = self.main_in_children_source
        ukijumuisha support.temp_dir() kama script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            script_name = _make_test_script(pkg_dir, '__main__',
                                            source=source)
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg')
            self._check_script(launch_name)

    eleza test_package_compiled(self):
        source = self.main_in_children_source
        ukijumuisha support.temp_dir() kama script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            script_name = _make_test_script(pkg_dir, '__main__',
                                            source=source)
            compiled_name = py_compile.compile(script_name, doashiria=Kweli)
            os.remove(script_name)
            pyc_file = support.make_legacy_pyc(script_name)
            launch_name = _make_launch_script(script_dir, 'launch', 'test_pkg')
            self._check_script(launch_name)

# Test all supported start methods (setupClass skips kama appropriate)

kundi SpawnCmdLineTest(MultiProcessingCmdLineMixin, unittest.TestCase):
    start_method = 'spawn'
    main_in_children_source = test_source_main_skipped_in_children

kundi ForkCmdLineTest(MultiProcessingCmdLineMixin, unittest.TestCase):
    start_method = 'fork'
    main_in_children_source = test_source

kundi ForkServerCmdLineTest(MultiProcessingCmdLineMixin, unittest.TestCase):
    start_method = 'forkserver'
    main_in_children_source = test_source_main_skipped_in_children

eleza tearDownModule():
    support.reap_children()

ikiwa __name__ == '__main__':
    unittest.main()
