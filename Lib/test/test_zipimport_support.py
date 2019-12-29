# This test module covers support kwenye various parts of the standard library
# kila working with modules located inside zipfiles
# The tests are centralised kwenye this fashion to make it easy to drop them
# ikiwa a platform doesn't support zipagiza
agiza test.support
agiza os
agiza os.path
agiza sys
agiza textwrap
agiza zipfile
agiza zipagiza
agiza doctest
agiza inspect
agiza linecache
agiza unittest
kutoka test.support.script_helper agiza (spawn_python, kill_python, assert_python_ok,
                                        make_script, make_zip_script)

verbose = test.support.verbose

# Library modules covered by this test set
#  pdb (Issue 4201)
#  inspect (Issue 4223)
#  doctest (Issue 4197)

# Other test modules with zipagiza related tests
#  test_zipagiza (of course!)
#  test_cmd_line_script (covers the zipagiza support kwenye runpy)

# Retrieve some helpers kutoka other test cases
kutoka test agiza (test_doctest, sample_doctest, sample_doctest_no_doctests,
                  sample_doctest_no_docstrings)


eleza _run_object_doctest(obj, module):
    finder = doctest.DocTestFinder(verbose=verbose, recurse=Uongo)
    runner = doctest.DocTestRunner(verbose=verbose)
    # Use the object's fully qualified name ikiwa it has one
    # Otherwise, use the module's name
    jaribu:
        name = "%s.%s" % (obj.__module__, obj.__qualname__)
    tatizo AttributeError:
        name = module.__name__
    kila example kwenye finder.find(obj, name, module):
        runner.run(example)
    f, t = runner.failures, runner.tries
    ikiwa f:
        ashiria test.support.TestFailed("%d of %d doctests failed" % (f, t))
    ikiwa verbose:
        print ('doctest (%s) ... %d tests with zero failures' % (module.__name__, t))
    rudisha f, t



kundi ZipSupportTests(unittest.TestCase):
    # This used to use the ImportHooksBaseTestCase to restore
    # the state of the agiza related information
    # kwenye the sys module after each test. However, that restores
    # *too much* information na komas kila the invocation
    # of test_doctest. So we do our own thing na leave
    # sys.modules alone.
    # We also clear the linecache na zipagiza cache
    # just to avoid any bogus errors due to name reuse kwenye the tests
    eleza setUp(self):
        linecache.clearcache()
        zipagiza._zip_directory_cache.clear()
        self.path = sys.path[:]
        self.meta_path = sys.meta_path[:]
        self.path_hooks = sys.path_hooks[:]
        sys.path_importer_cache.clear()

    eleza tearDown(self):
        sys.path[:] = self.path
        sys.meta_path[:] = self.meta_path
        sys.path_hooks[:] = self.path_hooks
        sys.path_importer_cache.clear()

    eleza test_inspect_getsource_issue4223(self):
        test_src = "eleza foo(): pita\n"
        with test.support.temp_dir() kama d:
            init_name = make_script(d, '__init__', test_src)
            name_in_zip = os.path.join('zip_pkg',
                                       os.path.basename(init_name))
            zip_name, run_name = make_zip_script(d, 'test_zip',
                                                init_name, name_in_zip)
            os.remove(init_name)
            sys.path.insert(0, zip_name)
            agiza zip_pkg
            jaribu:
                self.assertEqual(inspect.getsource(zip_pkg.foo), test_src)
            mwishowe:
                toa sys.modules["zip_pkg"]

    eleza test_doctest_issue4197(self):
        # To avoid having to keep two copies of the doctest module's
        # unit tests kwenye sync, this test works by taking the source of
        # test_doctest itself, rewriting it a bit to cope with a new
        # location, na then throwing it kwenye a zip file to make sure
        # everything still works correctly
        test_src = inspect.getsource(test_doctest)
        test_src = test_src.replace(
                         "kutoka test agiza test_doctest",
                         "agiza test_zipped_doctest kama test_doctest")
        test_src = test_src.replace("test.test_doctest",
                                    "test_zipped_doctest")
        test_src = test_src.replace("test.sample_doctest",
                                    "sample_zipped_doctest")
        # The sample doctest files rewritten to include kwenye the zipped version.
        sample_sources = {}
        kila mod kwenye [sample_doctest, sample_doctest_no_doctests,
                    sample_doctest_no_docstrings]:
            src = inspect.getsource(mod)
            src = src.replace("test.test_doctest", "test_zipped_doctest")
            # Rewrite the module name so that, kila example,
            # "test.sample_doctest" becomes "sample_zipped_doctest".
            mod_name = mod.__name__.split(".")[-1]
            mod_name = mod_name.replace("sample_", "sample_zipped_")
            sample_sources[mod_name] = src

        with test.support.temp_dir() kama d:
            script_name = make_script(d, 'test_zipped_doctest',
                                            test_src)
            zip_name, run_name = make_zip_script(d, 'test_zip',
                                                script_name)
            with zipfile.ZipFile(zip_name, 'a') kama z:
                kila mod_name, src kwenye sample_sources.items():
                    z.writestr(mod_name + ".py", src)
            ikiwa verbose:
                with zipfile.ZipFile(zip_name, 'r') kama zip_file:
                    print ('Contents of %r:' % zip_name)
                    zip_file.printdir()
            os.remove(script_name)
            sys.path.insert(0, zip_name)
            agiza test_zipped_doctest
            jaribu:
                # Some of the doc tests depend on the colocated text files
                # which aren't available to the zipped version (the doctest
                # module currently requires real filenames kila non-embedded
                # tests). So we're forced to be selective about which tests
                # to run.
                # doctest could really use some APIs which take a text
                # string ama a file object instead of a filename...
                known_good_tests = [
                    test_zipped_doctest.SampleClass,
                    test_zipped_doctest.SampleClass.NestedClass,
                    test_zipped_doctest.SampleClass.NestedClass.__init__,
                    test_zipped_doctest.SampleClass.__init__,
                    test_zipped_doctest.SampleClass.a_classmethod,
                    test_zipped_doctest.SampleClass.a_property,
                    test_zipped_doctest.SampleClass.a_staticmethod,
                    test_zipped_doctest.SampleClass.double,
                    test_zipped_doctest.SampleClass.get,
                    test_zipped_doctest.SampleNewStyleClass,
                    test_zipped_doctest.SampleNewStyleClass.__init__,
                    test_zipped_doctest.SampleNewStyleClass.double,
                    test_zipped_doctest.SampleNewStyleClass.get,
                    test_zipped_doctest.sample_func,
                    test_zipped_doctest.test_DocTest,
                    test_zipped_doctest.test_DocTestParser,
                    test_zipped_doctest.test_DocTestRunner.basics,
                    test_zipped_doctest.test_DocTestRunner.exceptions,
                    test_zipped_doctest.test_DocTestRunner.option_directives,
                    test_zipped_doctest.test_DocTestRunner.optionflags,
                    test_zipped_doctest.test_DocTestRunner.verbose_flag,
                    test_zipped_doctest.test_Example,
                    test_zipped_doctest.test_debug,
                    test_zipped_doctest.test_testsource,
                    test_zipped_doctest.test_trailing_space_in_test,
                    test_zipped_doctest.test_DocTestSuite,
                    test_zipped_doctest.test_DocTestFinder,
                ]
                # These tests are the ones which need access
                # to the data files, so we don't run them
                fail_due_to_missing_data_files = [
                    test_zipped_doctest.test_DocFileSuite,
                    test_zipped_doctest.test_testfile,
                    test_zipped_doctest.test_unittest_reportflags,
                ]

                kila obj kwenye known_good_tests:
                    _run_object_doctest(obj, test_zipped_doctest)
            mwishowe:
                toa sys.modules["test_zipped_doctest"]

    eleza test_doctest_main_issue4197(self):
        test_src = textwrap.dedent("""\
                    kundi Test:
                        ">>> 'line 2'"
                        pita

                    agiza doctest
                    doctest.testmod()
                    """)
        pattern = 'File "%s", line 2, kwenye %s'
        with test.support.temp_dir() kama d:
            script_name = make_script(d, 'script', test_src)
            rc, out, err = assert_python_ok(script_name)
            expected = pattern % (script_name, "__main__.Test")
            ikiwa verbose:
                print ("Expected line", expected)
                print ("Got stdout:")
                print (ascii(out))
            self.assertIn(expected.encode('utf-8'), out)
            zip_name, run_name = make_zip_script(d, "test_zip",
                                                script_name, '__main__.py')
            rc, out, err = assert_python_ok(zip_name)
            expected = pattern % (run_name, "__main__.Test")
            ikiwa verbose:
                print ("Expected line", expected)
                print ("Got stdout:")
                print (ascii(out))
            self.assertIn(expected.encode('utf-8'), out)

    eleza test_pdb_issue4201(self):
        test_src = textwrap.dedent("""\
                    eleza f():
                        pita

                    agiza pdb
                    pdb.Pdb(nosigint=Kweli).runcall(f)
                    """)
        with test.support.temp_dir() kama d:
            script_name = make_script(d, 'script', test_src)
            p = spawn_python(script_name)
            p.stdin.write(b'l\n')
            data = kill_python(p)
            # bdb/pdb applies normcase to its filename before displaying
            self.assertIn(os.path.normcase(script_name.encode('utf-8')), data)
            zip_name, run_name = make_zip_script(d, "test_zip",
                                                script_name, '__main__.py')
            p = spawn_python(zip_name)
            p.stdin.write(b'l\n')
            data = kill_python(p)
            # bdb/pdb applies normcase to its filename before displaying
            self.assertIn(os.path.normcase(run_name.encode('utf-8')), data)


eleza tearDownModule():
    test.support.reap_children()

ikiwa __name__ == '__main__':
    unittest.main()
