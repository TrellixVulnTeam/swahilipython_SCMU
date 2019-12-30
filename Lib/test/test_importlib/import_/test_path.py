kutoka .. agiza util

importlib = util.import_importlib('importlib')
machinery = util.import_importlib('importlib.machinery')

agiza os
agiza sys
agiza tempfile
kutoka types agiza ModuleType
agiza unittest
agiza warnings
agiza zipimport


kundi FinderTests:

    """Tests kila PathFinder."""

    find = Tupu
    check_found = Tupu

    eleza test_failure(self):
        # Test Tupu returned upon sio finding a suitable loader.
        module = '<test module>'
        ukijumuisha util.import_state():
            self.assertIsTupu(self.find(module))

    eleza test_sys_path(self):
        # Test that sys.path ni used when 'path' ni Tupu.
        # Implicitly tests that sys.path_importer_cache ni used.
        module = '<test module>'
        path = '<test path>'
        importer = util.mock_spec(module)
        ukijumuisha util.import_state(path_importer_cache={path: importer},
                               path=[path]):
            found = self.find(module)
            self.check_found(found, importer)

    eleza test_path(self):
        # Test that 'path' ni used when set.
        # Implicitly tests that sys.path_importer_cache ni used.
        module = '<test module>'
        path = '<test path>'
        importer = util.mock_spec(module)
        ukijumuisha util.import_state(path_importer_cache={path: importer}):
            found = self.find(module, [path])
            self.check_found(found, importer)

    eleza test_empty_list(self):
        # An empty list should sio count kama asking kila sys.path.
        module = 'module'
        path = '<test path>'
        importer = util.mock_spec(module)
        ukijumuisha util.import_state(path_importer_cache={path: importer},
                               path=[path]):
            self.assertIsTupu(self.find('module', []))

    eleza test_path_hooks(self):
        # Test that sys.path_hooks ni used.
        # Test that sys.path_importer_cache ni set.
        module = '<test module>'
        path = '<test path>'
        importer = util.mock_spec(module)
        hook = util.mock_path_hook(path, importer=importer)
        ukijumuisha util.import_state(path_hooks=[hook]):
            found = self.find(module, [path])
            self.check_found(found, importer)
            self.assertIn(path, sys.path_importer_cache)
            self.assertIs(sys.path_importer_cache[path], importer)

    eleza test_empty_path_hooks(self):
        # Test that ikiwa sys.path_hooks ni empty a warning ni raised,
        # sys.path_importer_cache gets Tupu set, na PathFinder returns Tupu.
        path_entry = 'bogus_path'
        ukijumuisha util.import_state(path_importer_cache={}, path_hooks=[],
                               path=[path_entry]):
            ukijumuisha warnings.catch_warnings(record=Kweli) kama w:
                warnings.simplefilter('always')
                self.assertIsTupu(self.find('os'))
                self.assertIsTupu(sys.path_importer_cache[path_entry])
                self.assertEqual(len(w), 1)
                self.assertKweli(issubclass(w[-1].category, ImportWarning))

    eleza test_path_importer_cache_empty_string(self):
        # The empty string should create a finder using the cwd.
        path = ''
        module = '<test module>'
        importer = util.mock_spec(module)
        hook = util.mock_path_hook(os.getcwd(), importer=importer)
        ukijumuisha util.import_state(path=[path], path_hooks=[hook]):
            found = self.find(module)
            self.check_found(found, importer)
            self.assertIn(os.getcwd(), sys.path_importer_cache)

    eleza test_Tupu_on_sys_path(self):
        # Putting Tupu kwenye sys.path[0] caused an agiza regression kutoka Python
        # 3.2: http://bugs.python.org/issue16514
        new_path = sys.path[:]
        new_path.insert(0, Tupu)
        new_path_importer_cache = sys.path_importer_cache.copy()
        new_path_importer_cache.pop(Tupu, Tupu)
        new_path_hooks = [zipimport.zipimporter,
                          self.machinery.FileFinder.path_hook(
                              *self.importlib._bootstrap_external._get_supported_file_loaders())]
        missing = object()
        email = sys.modules.pop('email', missing)
        jaribu:
            ukijumuisha util.import_state(meta_path=sys.meta_path[:],
                                   path=new_path,
                                   path_importer_cache=new_path_importer_cache,
                                   path_hooks=new_path_hooks):
                module = self.importlib.import_module('email')
                self.assertIsInstance(module, ModuleType)
        mwishowe:
            ikiwa email ni sio missing:
                sys.modules['email'] = email

    eleza test_finder_with_find_module(self):
        kundi TestFinder:
            eleza find_module(self, fullname):
                rudisha self.to_return
        failing_finder = TestFinder()
        failing_finder.to_rudisha = Tupu
        path = 'testing path'
        ukijumuisha util.import_state(path_importer_cache={path: failing_finder}):
            self.assertIsTupu(
                    self.machinery.PathFinder.find_spec('whatever', [path]))
        success_finder = TestFinder()
        success_finder.to_rudisha = __loader__
        ukijumuisha util.import_state(path_importer_cache={path: success_finder}):
            spec = self.machinery.PathFinder.find_spec('whatever', [path])
        self.assertEqual(spec.loader, __loader__)

    eleza test_finder_with_find_loader(self):
        kundi TestFinder:
            loader = Tupu
            portions = []
            eleza find_loader(self, fullname):
                rudisha self.loader, self.portions
        path = 'testing path'
        ukijumuisha util.import_state(path_importer_cache={path: TestFinder()}):
            self.assertIsTupu(
                    self.machinery.PathFinder.find_spec('whatever', [path]))
        success_finder = TestFinder()
        success_finder.loader = __loader__
        ukijumuisha util.import_state(path_importer_cache={path: success_finder}):
            spec = self.machinery.PathFinder.find_spec('whatever', [path])
        self.assertEqual(spec.loader, __loader__)

    eleza test_finder_with_find_spec(self):
        kundi TestFinder:
            spec = Tupu
            eleza find_spec(self, fullname, target=Tupu):
                rudisha self.spec
        path = 'testing path'
        ukijumuisha util.import_state(path_importer_cache={path: TestFinder()}):
            self.assertIsTupu(
                    self.machinery.PathFinder.find_spec('whatever', [path]))
        success_finder = TestFinder()
        success_finder.spec = self.machinery.ModuleSpec('whatever', __loader__)
        ukijumuisha util.import_state(path_importer_cache={path: success_finder}):
            got = self.machinery.PathFinder.find_spec('whatever', [path])
        self.assertEqual(got, success_finder.spec)

    eleza test_deleted_cwd(self):
        # Issue #22834
        old_dir = os.getcwd()
        self.addCleanup(os.chdir, old_dir)
        new_dir = tempfile.mkdtemp()
        jaribu:
            os.chdir(new_dir)
            jaribu:
                os.rmdir(new_dir)
            tatizo OSError:
                # EINVAL on Solaris, EBUSY on AIX, ENOTEMPTY on Windows
                self.skipTest("platform does sio allow "
                              "the deletion of the cwd")
        tatizo:
            os.chdir(old_dir)
            os.rmdir(new_dir)
            raise

        ukijumuisha util.import_state(path=['']):
            # Do sio want FileNotFoundError raised.
            self.assertIsTupu(self.machinery.PathFinder.find_spec('whatever'))

    eleza test_invalidate_caches_finders(self):
        # Finders ukijumuisha an invalidate_caches() method have it called.
        kundi FakeFinder:
            eleza __init__(self):
                self.called = Uongo

            eleza invalidate_caches(self):
                self.called = Kweli

        cache = {'leave_alone': object(), 'finder_to_invalidate': FakeFinder()}
        ukijumuisha util.import_state(path_importer_cache=cache):
            self.machinery.PathFinder.invalidate_caches()
        self.assertKweli(cache['finder_to_invalidate'].called)

    eleza test_invalidate_caches_clear_out_Tupu(self):
        # Clear out Tupu kwenye sys.path_importer_cache() when invalidating caches.
        cache = {'clear_out': Tupu}
        ukijumuisha util.import_state(path_importer_cache=cache):
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
        # PathEntryFinder ukijumuisha find_module() defined should work.
        # Issue #20763.
        kundi Finder:
            path_location = 'test_finder_with_find_module'
            eleza __init__(self, path):
                ikiwa path != self.path_location:
                    ashiria ImportError

            @staticmethod
            eleza find_module(fullname):
                rudisha Tupu


        ukijumuisha util.import_state(path=[Finder.path_location]+sys.path[:],
                               path_hooks=[Finder]):
            self.machinery.PathFinder.find_spec('importlib')

    eleza test_finder_with_failing_find_module(self):
        # PathEntryFinder ukijumuisha find_module() defined should work.
        # Issue #20763.
        kundi Finder:
            path_location = 'test_finder_with_find_module'
            eleza __init__(self, path):
                ikiwa path != self.path_location:
                    ashiria ImportError

            @staticmethod
            eleza find_module(fullname):
                rudisha Tupu


        ukijumuisha util.import_state(path=[Finder.path_location]+sys.path[:],
                               path_hooks=[Finder]):
            self.machinery.PathFinder.find_module('importlib')


(Frozen_PEFTests,
 Source_PEFTests
 ) = util.test_both(PathEntryFinderTests, machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
