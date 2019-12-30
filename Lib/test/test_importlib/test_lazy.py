agiza importlib
kutoka importlib agiza abc
kutoka importlib agiza util
agiza sys
agiza types
agiza unittest

kutoka . agiza util kama test_util


kundi CollectInit:

    eleza __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    eleza exec_module(self, module):
        rudisha self


kundi LazyLoaderFactoryTests(unittest.TestCase):

    eleza test_init(self):
        factory = util.LazyLoader.factory(CollectInit)
        # E.g. what importlib.machinery.FileFinder instantiates loaders with
        # plus keyword arguments.
        lazy_loader = factory('module name', 'module path', kw='kw')
        loader = lazy_loader.loader
        self.assertEqual(('module name', 'module path'), loader.args)
        self.assertEqual({'kw': 'kw'}, loader.kwargs)

    eleza test_validation(self):
        # No exec_module(), no lazy loading.
        ukijumuisha self.assertRaises(TypeError):
            util.LazyLoader.factory(object)


kundi TestingImporter(abc.MetaPathFinder, abc.Loader):

    module_name = 'lazy_loader_test'
    mutated_name = 'changed'
    loaded = Tupu
    source_code = 'attr = 42; __name__ = {!r}'.format(mutated_name)

    eleza find_spec(self, name, path, target=Tupu):
        ikiwa name != self.module_name:
            rudisha Tupu
        rudisha util.spec_from_loader(name, util.LazyLoader(self))

    eleza exec_module(self, module):
        exec(self.source_code, module.__dict__)
        self.loaded = module


kundi LazyLoaderTests(unittest.TestCase):

    eleza test_init(self):
        ukijumuisha self.assertRaises(TypeError):
            # Classes that don't define exec_module() trigger TypeError.
            util.LazyLoader(object)

    eleza new_module(self, source_code=Tupu):
        loader = TestingImporter()
        ikiwa source_code ni sio Tupu:
            loader.source_code = source_code
        spec = util.spec_from_loader(TestingImporter.module_name,
                                     util.LazyLoader(loader))
        module = spec.loader.create_module(spec)
        ikiwa module ni Tupu:
            module = types.ModuleType(TestingImporter.module_name)
        module.__spec__ = spec
        module.__loader__ = spec.loader
        spec.loader.exec_module(module)
        # Module ni now lazy.
        self.assertIsTupu(loader.loaded)
        rudisha module

    eleza test_e2e(self):
        # End-to-end test to verify the load ni kwenye fact lazy.
        importer = TestingImporter()
        assert importer.loaded ni Tupu
        ukijumuisha test_util.uncache(importer.module_name):
            ukijumuisha test_util.import_state(meta_path=[importer]):
                module = importlib.import_module(importer.module_name)
        self.assertIsTupu(importer.loaded)
        # Trigger load.
        self.assertEqual(module.__loader__, importer)
        self.assertIsNotTupu(importer.loaded)
        self.assertEqual(module, importer.loaded)

    eleza test_attr_unchanged(self):
        # An attribute only mutated kama a side-effect of agiza should sio be
        # changed needlessly.
        module = self.new_module()
        self.assertEqual(TestingImporter.mutated_name, module.__name__)

    eleza test_new_attr(self):
        # A new attribute should persist.
        module = self.new_module()
        module.new_attr = 42
        self.assertEqual(42, module.new_attr)

    eleza test_mutated_preexisting_attr(self):
        # Changing an attribute that already existed on the module --
        # e.g. __name__ -- should persist.
        module = self.new_module()
        module.__name__ = 'bogus'
        self.assertEqual('bogus', module.__name__)

    eleza test_mutated_attr(self):
        # Changing an attribute that comes into existence after an agiza
        # should persist.
        module = self.new_module()
        module.attr = 6
        self.assertEqual(6, module.attr)

    eleza test_delete_eventual_attr(self):
        # Deleting an attribute should stay deleted.
        module = self.new_module()
        toa module.attr
        self.assertUongo(hasattr(module, 'attr'))

    eleza test_delete_preexisting_attr(self):
        module = self.new_module()
        toa module.__name__
        self.assertUongo(hasattr(module, '__name__'))

    eleza test_module_substitution_error(self):
        ukijumuisha test_util.uncache(TestingImporter.module_name):
            fresh_module = types.ModuleType(TestingImporter.module_name)
            sys.modules[TestingImporter.module_name] = fresh_module
            module = self.new_module()
            ukijumuisha self.assertRaisesRegex(ValueError, "substituted"):
                module.__name__

    eleza test_module_already_in_sys(self):
        ukijumuisha test_util.uncache(TestingImporter.module_name):
            module = self.new_module()
            sys.modules[TestingImporter.module_name] = module
            # Force the load; just care that no exception ni ashiriad.
            module.__name__


ikiwa __name__ == '__main__':
    unittest.main()
