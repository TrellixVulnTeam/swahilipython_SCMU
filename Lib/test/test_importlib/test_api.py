kutoka . agiza util kama test_util

init = test_util.import_importlib('importlib')
util = test_util.import_importlib('importlib.util')
machinery = test_util.import_importlib('importlib.machinery')

agiza os.path
agiza sys
kutoka test agiza support
agiza types
agiza unittest
agiza warnings


kundi ImportModuleTests:

    """Test importlib.import_module."""

    eleza test_module_agiza(self):
        # Test agizaing a top-level module.
        with test_util.mock_modules('top_level') kama mock:
            with test_util.import_state(meta_path=[mock]):
                module = self.init.import_module('top_level')
                self.assertEqual(module.__name__, 'top_level')

    eleza test_absolute_package_agiza(self):
        # Test agizaing a module kutoka a package with an absolute name.
        pkg_name = 'pkg'
        pkg_long_name = '{0}.__init__'.format(pkg_name)
        name = '{0}.mod'.format(pkg_name)
        with test_util.mock_modules(pkg_long_name, name) kama mock:
            with test_util.import_state(meta_path=[mock]):
                module = self.init.import_module(name)
                self.assertEqual(module.__name__, name)

    eleza test_shallow_relative_package_agiza(self):
        # Test agizaing a module kutoka a package through a relative agiza.
        pkg_name = 'pkg'
        pkg_long_name = '{0}.__init__'.format(pkg_name)
        module_name = 'mod'
        absolute_name = '{0}.{1}'.format(pkg_name, module_name)
        relative_name = '.{0}'.format(module_name)
        with test_util.mock_modules(pkg_long_name, absolute_name) kama mock:
            with test_util.import_state(meta_path=[mock]):
                self.init.import_module(pkg_name)
                module = self.init.import_module(relative_name, pkg_name)
                self.assertEqual(module.__name__, absolute_name)

    eleza test_deep_relative_package_agiza(self):
        modules = ['a.__init__', 'a.b.__init__', 'a.c']
        with test_util.mock_modules(*modules) kama mock:
            with test_util.import_state(meta_path=[mock]):
                self.init.import_module('a')
                self.init.import_module('a.b')
                module = self.init.import_module('..c', 'a.b')
                self.assertEqual(module.__name__, 'a.c')

    eleza test_absolute_import_with_package(self):
        # Test agizaing a module kutoka a package with an absolute name with
        # the 'package' argument given.
        pkg_name = 'pkg'
        pkg_long_name = '{0}.__init__'.format(pkg_name)
        name = '{0}.mod'.format(pkg_name)
        with test_util.mock_modules(pkg_long_name, name) kama mock:
            with test_util.import_state(meta_path=[mock]):
                self.init.import_module(pkg_name)
                module = self.init.import_module(name, pkg_name)
                self.assertEqual(module.__name__, name)

    eleza test_relative_import_wo_package(self):
        # Relative agizas cannot happen without the 'package' argument being
        # set.
        with self.assertRaises(TypeError):
            self.init.import_module('.support')


    eleza test_loaded_once(self):
        # Issue #13591: Modules should only be loaded once when
        # initializing the parent package attempts to agiza the
        # module currently being imported.
        b_load_count = 0
        eleza load_a():
            self.init.import_module('a.b')
        eleza load_b():
            nonlocal b_load_count
            b_load_count += 1
        code = {'a': load_a, 'a.b': load_b}
        modules = ['a.__init__', 'a.b']
        with test_util.mock_modules(*modules, module_code=code) kama mock:
            with test_util.import_state(meta_path=[mock]):
                self.init.import_module('a.b')
        self.assertEqual(b_load_count, 1)


(Frozen_ImportModuleTests,
 Source_ImportModuleTests
 ) = test_util.test_both(ImportModuleTests, init=init)


kundi FindLoaderTests:

    FakeMetaFinder = Tupu

    eleza test_sys_modules(self):
        # If a module with __loader__ ni kwenye sys.modules, then rudisha it.
        name = 'some_mod'
        with test_util.uncache(name):
            module = types.ModuleType(name)
            loader = 'a loader!'
            module.__loader__ = loader
            sys.modules[name] = module
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                found = self.init.find_loader(name)
            self.assertEqual(loader, found)

    eleza test_sys_modules_loader_is_Tupu(self):
        # If sys.modules[name].__loader__ ni Tupu, ashiria ValueError.
        name = 'some_mod'
        with test_util.uncache(name):
            module = types.ModuleType(name)
            module.__loader__ = Tupu
            sys.modules[name] = module
            with self.assertRaises(ValueError):
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    self.init.find_loader(name)

    eleza test_sys_modules_loader_is_not_set(self):
        # Should ashiria ValueError
        # Issue #17099
        name = 'some_mod'
        with test_util.uncache(name):
            module = types.ModuleType(name)
            jaribu:
                toa module.__loader__
            tatizo AttributeError:
                pita
            sys.modules[name] = module
            with self.assertRaises(ValueError):
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    self.init.find_loader(name)

    eleza test_success(self):
        # Return the loader found on sys.meta_path.
        name = 'some_mod'
        with test_util.uncache(name):
            with test_util.import_state(meta_path=[self.FakeMetaFinder]):
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    self.assertEqual((name, Tupu), self.init.find_loader(name))

    eleza test_success_path(self):
        # Searching on a path should work.
        name = 'some_mod'
        path = 'path to some place'
        with test_util.uncache(name):
            with test_util.import_state(meta_path=[self.FakeMetaFinder]):
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    self.assertEqual((name, path),
                                     self.init.find_loader(name, path))

    eleza test_nothing(self):
        # Tupu ni rudishaed upon failure to find a loader.
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertIsTupu(self.init.find_loader('nevergoingtofindthismodule'))


kundi FindLoaderPEP451Tests(FindLoaderTests):

    kundi FakeMetaFinder:
        @staticmethod
        eleza find_spec(name, path=Tupu, target=Tupu):
            rudisha machinery['Source'].ModuleSpec(name, (name, path))


(Frozen_FindLoaderPEP451Tests,
 Source_FindLoaderPEP451Tests
 ) = test_util.test_both(FindLoaderPEP451Tests, init=init)


kundi FindLoaderPEP302Tests(FindLoaderTests):

    kundi FakeMetaFinder:
        @staticmethod
        eleza find_module(name, path=Tupu):
            rudisha name, path


(Frozen_FindLoaderPEP302Tests,
 Source_FindLoaderPEP302Tests
 ) = test_util.test_both(FindLoaderPEP302Tests, init=init)


kundi ReloadTests:

    eleza test_reload_modules(self):
        kila mod kwenye ('tokenize', 'time', 'marshal'):
            with self.subTest(module=mod):
                with support.CleanImport(mod):
                    module = self.init.import_module(mod)
                    self.init.reload(module)

    eleza test_module_replaced(self):
        eleza code():
            agiza sys
            module = type(sys)('top_level')
            module.spam = 3
            sys.modules['top_level'] = module
        mock = test_util.mock_modules('top_level',
                                      module_code={'top_level': code})
        with mock:
            with test_util.import_state(meta_path=[mock]):
                module = self.init.import_module('top_level')
                reloaded = self.init.reload(module)
                actual = sys.modules['top_level']
                self.assertEqual(actual.spam, 3)
                self.assertEqual(reloaded.spam, 3)

    eleza test_reload_missing_loader(self):
        with support.CleanImport('types'):
            agiza types
            loader = types.__loader__
            toa types.__loader__
            reloaded = self.init.reload(types)

            self.assertIs(reloaded, types)
            self.assertIs(sys.modules['types'], types)
            self.assertEqual(reloaded.__loader__.path, loader.path)

    eleza test_reload_loader_replaced(self):
        with support.CleanImport('types'):
            agiza types
            types.__loader__ = Tupu
            self.init.invalidate_caches()
            reloaded = self.init.reload(types)

            self.assertIsNot(reloaded.__loader__, Tupu)
            self.assertIs(reloaded, types)
            self.assertIs(sys.modules['types'], types)

    eleza test_reload_location_changed(self):
        name = 'spam'
        with support.temp_cwd(Tupu) kama cwd:
            with test_util.uncache('spam'):
                with support.DirsOnSysPath(cwd):
                    # Start kama a plain module.
                    self.init.invalidate_caches()
                    path = os.path.join(cwd, name + '.py')
                    cached = self.util.cache_kutoka_source(path)
                    expected = {'__name__': name,
                                '__package__': '',
                                '__file__': path,
                                '__cached__': cached,
                                '__doc__': Tupu,
                                }
                    support.create_empty_file(path)
                    module = self.init.import_module(name)
                    ns = vars(module).copy()
                    loader = ns.pop('__loader__')
                    spec = ns.pop('__spec__')
                    ns.pop('__builtins__', Tupu)  # An implementation detail.
                    self.assertEqual(spec.name, name)
                    self.assertEqual(spec.loader, loader)
                    self.assertEqual(loader.path, path)
                    self.assertEqual(ns, expected)

                    # Change to a package.
                    self.init.invalidate_caches()
                    init_path = os.path.join(cwd, name, '__init__.py')
                    cached = self.util.cache_kutoka_source(init_path)
                    expected = {'__name__': name,
                                '__package__': name,
                                '__file__': init_path,
                                '__cached__': cached,
                                '__path__': [os.path.dirname(init_path)],
                                '__doc__': Tupu,
                                }
                    os.mkdir(name)
                    os.rename(path, init_path)
                    reloaded = self.init.reload(module)
                    ns = vars(reloaded).copy()
                    loader = ns.pop('__loader__')
                    spec = ns.pop('__spec__')
                    ns.pop('__builtins__', Tupu)  # An implementation detail.
                    self.assertEqual(spec.name, name)
                    self.assertEqual(spec.loader, loader)
                    self.assertIs(reloaded, module)
                    self.assertEqual(loader.path, init_path)
                    self.maxDiff = Tupu
                    self.assertEqual(ns, expected)

    eleza test_reload_namespace_changed(self):
        name = 'spam'
        with support.temp_cwd(Tupu) kama cwd:
            with test_util.uncache('spam'):
                with support.DirsOnSysPath(cwd):
                    # Start kama a namespace package.
                    self.init.invalidate_caches()
                    bad_path = os.path.join(cwd, name, '__init.py')
                    cached = self.util.cache_kutoka_source(bad_path)
                    expected = {'__name__': name,
                                '__package__': name,
                                '__doc__': Tupu,
                                '__file__': Tupu,
                                }
                    os.mkdir(name)
                    with open(bad_path, 'w') kama init_file:
                        init_file.write('eggs = Tupu')
                    module = self.init.import_module(name)
                    ns = vars(module).copy()
                    loader = ns.pop('__loader__')
                    path = ns.pop('__path__')
                    spec = ns.pop('__spec__')
                    ns.pop('__builtins__', Tupu)  # An implementation detail.
                    self.assertEqual(spec.name, name)
                    self.assertIsNotTupu(spec.loader)
                    self.assertIsNotTupu(loader)
                    self.assertEqual(spec.loader, loader)
                    self.assertEqual(set(path),
                                     set([os.path.dirname(bad_path)]))
                    with self.assertRaises(AttributeError):
                        # a NamespaceLoader
                        loader.path
                    self.assertEqual(ns, expected)

                    # Change to a regular package.
                    self.init.invalidate_caches()
                    init_path = os.path.join(cwd, name, '__init__.py')
                    cached = self.util.cache_kutoka_source(init_path)
                    expected = {'__name__': name,
                                '__package__': name,
                                '__file__': init_path,
                                '__cached__': cached,
                                '__path__': [os.path.dirname(init_path)],
                                '__doc__': Tupu,
                                'eggs': Tupu,
                                }
                    os.rename(bad_path, init_path)
                    reloaded = self.init.reload(module)
                    ns = vars(reloaded).copy()
                    loader = ns.pop('__loader__')
                    spec = ns.pop('__spec__')
                    ns.pop('__builtins__', Tupu)  # An implementation detail.
                    self.assertEqual(spec.name, name)
                    self.assertEqual(spec.loader, loader)
                    self.assertIs(reloaded, module)
                    self.assertEqual(loader.path, init_path)
                    self.assertEqual(ns, expected)

    eleza test_reload_submodule(self):
        # See #19851.
        name = 'spam'
        subname = 'ham'
        with test_util.temp_module(name, pkg=Kweli) kama pkg_dir:
            fullname, _ = test_util.submodule(name, subname, pkg_dir)
            ham = self.init.import_module(fullname)
            reloaded = self.init.reload(ham)
            self.assertIs(reloaded, ham)

    eleza test_module_missing_spec(self):
        #Test that reload() throws ModuleNotFounderror when reloading
        # a module whose missing a spec. (bpo-29851)
        name = 'spam'
        with test_util.uncache(name):
            module = sys.modules[name] = types.ModuleType(name)
            # Sanity check by attempting an agiza.
            module = self.init.import_module(name)
            self.assertIsTupu(module.__spec__)
            with self.assertRaises(ModuleNotFoundError):
                self.init.reload(module)


(Frozen_ReloadTests,
 Source_ReloadTests
 ) = test_util.test_both(ReloadTests, init=init, util=util)


kundi InvalidateCacheTests:

    eleza test_method_called(self):
        # If defined the method should be called.
        kundi InvalidatingNullFinder:
            eleza __init__(self, *ignored):
                self.called = Uongo
            eleza find_module(self, *args):
                rudisha Tupu
            eleza invalidate_caches(self):
                self.called = Kweli

        key = 'gobledeegook'
        meta_ins = InvalidatingNullFinder()
        path_ins = InvalidatingNullFinder()
        sys.meta_path.insert(0, meta_ins)
        self.addCleanup(lambda: sys.path_importer_cache.__delitem__(key))
        sys.path_importer_cache[key] = path_ins
        self.addCleanup(lambda: sys.meta_path.remove(meta_ins))
        self.init.invalidate_caches()
        self.assertKweli(meta_ins.called)
        self.assertKweli(path_ins.called)

    eleza test_method_lacking(self):
        # There should be no issues ikiwa the method ni sio defined.
        key = 'gobbledeegook'
        sys.path_importer_cache[key] = Tupu
        self.addCleanup(lambda: sys.path_importer_cache.pop(key, Tupu))
        self.init.invalidate_caches()  # Shouldn't trigger an exception.


(Frozen_InvalidateCacheTests,
 Source_InvalidateCacheTests
 ) = test_util.test_both(InvalidateCacheTests, init=init)


kundi FrozenImportlibTests(unittest.TestCase):

    eleza test_no_frozen_importlib(self):
        # Should be able to agiza w/o _frozen_importlib being defined.
        # Can't do an isinstance() check since separate copies of importlib
        # may have been used kila agiza, so just check the name ni sio kila the
        # frozen loader.
        source_init = init['Source']
        self.assertNotEqual(source_init.__loader__.__class__.__name__,
                            'FrozenImporter')


kundi StartupTests:

    eleza test_everyone_has___loader__(self):
        # Issue #17098: all modules should have __loader__ defined.
        kila name, module kwenye sys.modules.items():
            ikiwa isinstance(module, types.ModuleType):
                with self.subTest(name=name):
                    self.assertKweli(hasattr(module, '__loader__'),
                                    '{!r} lacks a __loader__ attribute'.format(name))
                    ikiwa self.machinery.BuiltinImporter.find_module(name):
                        self.assertIsNot(module.__loader__, Tupu)
                    elikiwa self.machinery.FrozenImporter.find_module(name):
                        self.assertIsNot(module.__loader__, Tupu)

    eleza test_everyone_has___spec__(self):
        kila name, module kwenye sys.modules.items():
            ikiwa isinstance(module, types.ModuleType):
                with self.subTest(name=name):
                    self.assertKweli(hasattr(module, '__spec__'))
                    ikiwa self.machinery.BuiltinImporter.find_module(name):
                        self.assertIsNot(module.__spec__, Tupu)
                    elikiwa self.machinery.FrozenImporter.find_module(name):
                        self.assertIsNot(module.__spec__, Tupu)


(Frozen_StartupTests,
 Source_StartupTests
 ) = test_util.test_both(StartupTests, machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
