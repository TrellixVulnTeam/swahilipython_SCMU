kutoka .. agiza util

importlib = util.import_importlib('importlib')
machinery = util.import_importlib('importlib.machinery')

agiza os
agiza sys
agiza tempfile
kutoka types agiza ModuleType
agiza unittest
agiza warnings
agiza zipagiza


kundi FinderTests:

    """Tests for PathFinder."""

    find = None
    check_found = None

    eleza test_failure(self):
        # Test None returned upon not finding a suitable loader.
        module = '<test module>'
        with util.import_state():
            self.assertIsNone(self.find(module))

    eleza test_sys_path(self):
        # Test that sys.path is used when 'path' is None.
        # Implicitly tests that sys.path_importer_cache is used.
        module = '<test module>'
        path = '<test path>'
        importer = util.mock_spec(module)
        with util.import_state(path_importer_cache={path: importer},
                               path=[path]):
            found = self.find(module)
            self.check_found(found, importer)

    eleza test_path(self):
        # Test that 'path' is used when set.
        # Implicitly tests that sys.path_importer_cache is used.
        module = '<test module>'
        path = '<test path>'
        importer = util.mock_spec(module)
        with util.import_state(path_importer_cache={path: importer}):
            found = self.find(module, [path])
            self.check_found(found, importer)

    eleza test_empty_list(self):
        # An empty list should not count as asking for sys.path.
        module = 'module'
        path = '<test path>'
        importer = util.mock_spec(module)
        with util.import_state(path_importer_cache={path: importer},
                               path=[path]):
            self.assertIsNone(self.find('module', []))

    eleza test_path_hooks(self):
        # Test that sys.path_hooks is used.
        # Test that sys.path_importer_cache is set.
        module = '<test module>'
        path = '<test path>'
        importer = util.mock_spec(module)
        hook = util.mock_path_hook(path, importer=importer)
        with util.import_state(path_hooks=[hook]):
            found = self.find(module, [path])
            self.check_found(found, importer)
            self.assertIn(path, sys.path_importer_cache)
            self.assertIs(sys.path_importer_cache[path], importer)

    eleza test_empty_path_hooks(self):
        # Test that ikiwa sys.path_hooks is empty a warning is raised,
        # sys.path_importer_cache gets None set, and PathFinder returns None.
        path_entry = 'bogus_path'
        with util.import_state(path_importer_cache={}, path_hooks=[],
                               path=[path_entry]):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always')
                self.assertIsNone(self.find('os'))
                self.assertIsNone(sys.path_importer_cache[path_entry])
                self.assertEqual(len(w), 1)
                self.assertTrue(issubclass(w[-1].category, ImportWarning))

    eleza test_path_importer_cache_empty_string(self):
        # The empty string should create a finder using the cwd.
        path = ''
        module = '<test module>'
        importer = util.mock_spec(module)
        hook = util.mock_path_hook(os.getcwd(), importer=importer)
        with util.import_state(path=[path], path_hooks=[hook]):
            found = self.find(module)
            self.check_found(found, importer)
            self.assertIn(os.getcwd(), sys.path_importer_cache)

    eleza test_None_on_sys_path(self):
        # Putting None in sys.path[0] caused an agiza regression kutoka Python
        # 3.2: http://bugs.python.org/issue16514
        new_path = sys.path[:]
        new_path.insert(0, None)
        new_path_importer_cache = sys.path_importer_cache.copy()
        new_path_importer_cache.pop(None, None)
        new_path_hooks = [zipagiza.zipimporter,
                          self.machinery.FileFinder.path_hook(
                              *self.importlib._bootstrap_external._get_supported_file_loaders())]
        missing = object()
        email = sys.modules.pop('email', missing)
        try:
            with util.import_state(meta_path=sys.meta_path[:],
                                   path=new_path,
                                   path_importer_cache=new_path_importer_cache,
                                   path_hooks=new_path_hooks):
                module = self.importlib.import_module('email')
                self.assertIsInstance(module, ModuleType)
        finally:
            ikiwa email is not missing:
                sys.modules['email'] = email

    eleza test_finder_with_find_module(self):
        kundi TestFinder:
            eleza find_module(self, fullname):
                rudisha self.to_return
        failing_finder = TestFinder()
        failing_finder.to_rudisha = None
        path = 'testing path'
        with util.import_state(path_importer_cache={path: failing_finder}):
            self.assertIsNone(
                    self.machinery.PathFinder.find_spec('whatever', [path]))
        success_finder = TestFinder()
        success_finder.to_rudisha = __loader__
        with util.import_state(path_importer_cache={path: success_finder}):
            spec = self.machinery.PathFinder.find_spec('whatever', [path])
        self.assertEqual(spec.loader, __loader__)

    eleza test_finder_with_find_loader(self):
        kundi TestFinder:
            loader = None
            portions = []
            eleza find_loader(self, fullname):
                rudisha self.loader, self.portions
        path = 'testing path'
        with util.import_state(path_importer_cache={path: TestFinder()}):
            self.assertIsNone(
                    self.machinery.PathFinder.find_spec('whatever', [path]))
        success_finder = TestFinder()
        success_finder.loader = __loader__
        with util.import_state(path_importer_cache={path: success_finder}):
            spec = self.machinery.PathFinder.find_spec('whatever', [path])
        self.assertEqual(spec.loader, __loader__)

    eleza test_finder_with_find_spec(self):
        kundi TestFinder:
            spec = None
            eleza find_spec(self, fullname, target=None):
                rudisha self.spec
        path = 'testing path'
        with util.import_state(path_importer_cache={path: TestFinder()}):
            self.assertIsNone(
                    self.machinery.PathFinder.find_spec('whatever', [path]))
        success_finder = TestFinder()
        success_finder.spec = self.machinery.ModuleSpec('whatever', __loader__)
        with util.import_state(path_importer_cache={path: success_finder}):
            got = self.machinery.PathFinder.find_spec('whatever', [path])
        self.assertEqual(got, success_finder.spec)

    eleza test_deleted_cwd(self):
        # Issue #22834
        old_dir = os.getcwd()
        self.addCleanup(os.chdir, old_dir)
        new_dir = tempfile.mkdtemp()
        try:
            os.chdir(new_dir)
            try:
                os.rmdir(new_dir)
            except OSError:
                # EINVAL on Solaris, EBUSY on AIX, ENOTEMPTY on Windows
                self.skipTest("platform does not allow "
                              "the deletion of the cwd")
        except:
            os.chdir(old_dir)
            os.rmdir(new_dir)
            raise

        with util.import_state(path=['']):
            # Do not want FileNotFoundError raised.
            self.assertIsNone(self.machinery.PathFinder.find_spec('whatever'))

    eleza test_invalidate_caches_finders(self):
        # Finders with an invalidate_caches() method have it called.
        kundi FakeFinder:
            eleza __init__(self):
                self.called = False

            eleza invalidate_caches(self):
                self.called = True

        cache = {'leave_alone': object(), 'finder_to_invalidate': FakeFinder()}
        with util.import_state(path_importer_cache=cache):
            self.machinery.PathFinder.invalidate_caches()
        self.assertTrue(cache['finder_to_invalidate'].called)

    eleza test_invalidate_caches_clear_out_None(self):
        # Clear out None in sys.path_importer_cache() when invalidating caches.
        cache = {'clear_out': None}
        with util.import_state(path_importer_cache=cache):
            self.machinery.PathFinder.invalidate_caches()
        self.assertEqual(len(cache), 0)


kundi FindModuleTests(FinderTests):
    eleza find(self, *args, **kwargs):
        rudisha self.machinery.PathFinder.find_module(*args, **kwargs)
    eleza check_found(self, found, importer):
        self.assertIs(found, importer)


(Frozen_FindModuleTests,
 Source_FindModuleTests
) = util.test_both(FindModuleTests, importlib=importlib, machinery=machinery)


kundi FindSpecTests(FinderTests):
    eleza find(self, *args, **kwargs):
        rudisha self.machinery.PathFinder.find_spec(*args, **kwargs)
    eleza check_found(self, found, importer):
        self.assertIs(found.loader, importer)


(Frozen_FindSpecTests,
 Source_FindSpecTests
 ) = util.test_both(FindSpecTests, importlib=importlib, machinery=machinery)


kundi PathEntryFinderTests:

    eleza test_finder_with_failing_find_spec(self):
        # PathEntryFinder with find_module() defined should work.
        # Issue #20763.
        kundi Finder:
            path_location = 'test_finder_with_find_module'
            eleza __init__(self, path):
                ikiwa path != self.path_location:
                    raise ImportError

            @staticmethod
            eleza find_module(fullname):
                rudisha None


        with util.import_state(path=[Finder.path_location]+sys.path[:],
                               path_hooks=[Finder]):
            self.machinery.PathFinder.find_spec('importlib')

    eleza test_finder_with_failing_find_module(self):
        # PathEntryFinder with find_module() defined should work.
        # Issue #20763.
        kundi Finder:
            path_location = 'test_finder_with_find_module'
            eleza __init__(self, path):
                ikiwa path != self.path_location:
                    raise ImportError

            @staticmethod
            eleza find_module(fullname):
                rudisha None


        with util.import_state(path=[Finder.path_location]+sys.path[:],
                               path_hooks=[Finder]):
            self.machinery.PathFinder.find_module('importlib')


(Frozen_PEFTests,
 Source_PEFTests
 ) = util.test_both(PathEntryFinderTests, machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
