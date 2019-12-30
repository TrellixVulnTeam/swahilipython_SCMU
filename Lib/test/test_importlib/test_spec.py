kutoka . agiza util as test_util

init = test_util.import_importlib('importlib')
machinery = test_util.import_importlib('importlib.machinery')
util = test_util.import_importlib('importlib.util')

agiza os.path
agiza pathlib
kutoka test.support agiza CleanImport
agiza unittest
agiza sys
agiza warnings



kundi TestLoader:

    eleza __init__(self, path=Tupu, is_package=Tupu):
        self.path = path
        self.package = is_package

    eleza __repr__(self):
        rudisha '<TestLoader object>'

    eleza __getattr__(self, name):
        ikiwa name == 'get_filename' na self.path ni sio Tupu:
            rudisha self._get_filename
        ikiwa name == 'is_package':
            rudisha self._is_package
         ashiria AttributeError(name)

    eleza _get_filename(self, name):
        rudisha self.path

    eleza _is_package(self, name):
        rudisha self.package

    eleza create_module(self, spec):
        rudisha Tupu


kundi NewLoader(TestLoader):

    EGGS = 1

    eleza exec_module(self, module):
        module.eggs = self.EGGS


kundi LegacyLoader(TestLoader):

    HAM = -1

    ukijumuisha warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)

        frozen_util = util['Frozen']

        @frozen_util.module_for_loader
        eleza load_module(self, module):
            module.ham = self.HAM
            rudisha module


kundi ModuleSpecTests:

    eleza setUp(self):
        self.name = 'spam'
        self.path = 'spam.py'
        self.cached = self.util.cache_from_source(self.path)
        self.loader = TestLoader()
        self.spec = self.machinery.ModuleSpec(self.name, self.loader)
        self.loc_spec = self.machinery.ModuleSpec(self.name, self.loader,
                                                  origin=self.path)
        self.loc_spec._set_fileattr = Kweli

    eleza test_default(self):
        spec = self.machinery.ModuleSpec(self.name, self.loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, Tupu)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertIs(spec.cached, Tupu)
        self.assertUongo(spec.has_location)

    eleza test_default_no_loader(self):
        spec = self.machinery.ModuleSpec(self.name, Tupu)

        self.assertEqual(spec.name, self.name)
        self.assertIs(spec.loader, Tupu)
        self.assertIs(spec.origin, Tupu)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertIs(spec.cached, Tupu)
        self.assertUongo(spec.has_location)

    eleza test_default_is_package_false(self):
        spec = self.machinery.ModuleSpec(self.name, self.loader,
                                         is_package=Uongo)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, Tupu)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertIs(spec.cached, Tupu)
        self.assertUongo(spec.has_location)

    eleza test_default_is_package_true(self):
        spec = self.machinery.ModuleSpec(self.name, self.loader,
                                         is_package=Kweli)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, Tupu)
        self.assertIs(spec.loader_state, Tupu)
        self.assertEqual(spec.submodule_search_locations, [])
        self.assertIs(spec.cached, Tupu)
        self.assertUongo(spec.has_location)

    eleza test_has_location_setter(self):
        spec = self.machinery.ModuleSpec(self.name, self.loader,
                                         origin='somewhere')
        self.assertUongo(spec.has_location)
        spec.has_location = Kweli
        self.assertKweli(spec.has_location)

    eleza test_equality(self):
        other = type(sys.implementation)(name=self.name,
                                         loader=self.loader,
                                         origin=Tupu,
                                         submodule_search_locations=Tupu,
                                         has_location=Uongo,
                                         cached=Tupu,
                                         )

        self.assertKweli(self.spec == other)

    eleza test_equality_location(self):
        other = type(sys.implementation)(name=self.name,
                                         loader=self.loader,
                                         origin=self.path,
                                         submodule_search_locations=Tupu,
                                         has_location=Kweli,
                                         cached=self.cached,
                                         )

        self.assertEqual(self.loc_spec, other)

    eleza test_inequality(self):
        other = type(sys.implementation)(name='ham',
                                         loader=self.loader,
                                         origin=Tupu,
                                         submodule_search_locations=Tupu,
                                         has_location=Uongo,
                                         cached=Tupu,
                                         )

        self.assertNotEqual(self.spec, other)

    eleza test_inequality_incomplete(self):
        other = type(sys.implementation)(name=self.name,
                                         loader=self.loader,
                                         )

        self.assertNotEqual(self.spec, other)

    eleza test_package(self):
        spec = self.machinery.ModuleSpec('spam.eggs', self.loader)

        self.assertEqual(spec.parent, 'spam')

    eleza test_package_is_package(self):
        spec = self.machinery.ModuleSpec('spam.eggs', self.loader,
                                         is_package=Kweli)

        self.assertEqual(spec.parent, 'spam.eggs')

    # cached

    eleza test_cached_set(self):
        before = self.spec.cached
        self.spec.cached = 'there'
        after = self.spec.cached

        self.assertIs(before, Tupu)
        self.assertEqual(after, 'there')

    eleza test_cached_no_origin(self):
        spec = self.machinery.ModuleSpec(self.name, self.loader)

        self.assertIs(spec.cached, Tupu)

    eleza test_cached_with_origin_not_location(self):
        spec = self.machinery.ModuleSpec(self.name, self.loader,
                                         origin=self.path)

        self.assertIs(spec.cached, Tupu)

    eleza test_cached_source(self):
        expected = self.util.cache_from_source(self.path)

        self.assertEqual(self.loc_spec.cached, expected)

    eleza test_cached_source_unknown_suffix(self):
        self.loc_spec.origin = 'spam.spamspamspam'

        self.assertIs(self.loc_spec.cached, Tupu)

    eleza test_cached_source_missing_cache_tag(self):
        original = sys.implementation.cache_tag
        sys.implementation.cache_tag = Tupu
        jaribu:
            cached = self.loc_spec.cached
        mwishowe:
            sys.implementation.cache_tag = original

        self.assertIs(cached, Tupu)

    eleza test_cached_sourceless(self):
        self.loc_spec.origin = 'spam.pyc'

        self.assertEqual(self.loc_spec.cached, 'spam.pyc')


(Frozen_ModuleSpecTests,
 Source_ModuleSpecTests
 ) = test_util.test_both(ModuleSpecTests, util=util, machinery=machinery)


kundi ModuleSpecMethodsTests:

    @property
    eleza bootstrap(self):
        rudisha self.init._bootstrap

    eleza setUp(self):
        self.name = 'spam'
        self.path = 'spam.py'
        self.cached = self.util.cache_from_source(self.path)
        self.loader = TestLoader()
        self.spec = self.machinery.ModuleSpec(self.name, self.loader)
        self.loc_spec = self.machinery.ModuleSpec(self.name, self.loader,
                                                  origin=self.path)
        self.loc_spec._set_fileattr = Kweli

    # exec()

    eleza test_exec(self):
        self.spec.loader = NewLoader()
        module = self.util.module_from_spec(self.spec)
        sys.modules[self.name] = module
        self.assertUongo(hasattr(module, 'eggs'))
        self.bootstrap._exec(self.spec, module)

        self.assertEqual(module.eggs, 1)

    # load()

    eleza test_load(self):
        self.spec.loader = NewLoader()
        ukijumuisha CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            installed = sys.modules[self.spec.name]

        self.assertEqual(loaded.eggs, 1)
        self.assertIs(loaded, installed)

    eleza test_load_replaced(self):
        replacement = object()
        kundi ReplacingLoader(TestLoader):
            eleza exec_module(self, module):
                sys.modules[module.__name__] = replacement
        self.spec.loader = ReplacingLoader()
        ukijumuisha CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            installed = sys.modules[self.spec.name]

        self.assertIs(loaded, replacement)
        self.assertIs(installed, replacement)

    eleza test_load_failed(self):
        kundi FailedLoader(TestLoader):
            eleza exec_module(self, module):
                 ashiria RuntimeError
        self.spec.loader = FailedLoader()
        ukijumuisha CleanImport(self.spec.name):
            ukijumuisha self.assertRaises(RuntimeError):
                loaded = self.bootstrap._load(self.spec)
            self.assertNotIn(self.spec.name, sys.modules)

    eleza test_load_failed_removed(self):
        kundi FailedLoader(TestLoader):
            eleza exec_module(self, module):
                toa sys.modules[module.__name__]
                 ashiria RuntimeError
        self.spec.loader = FailedLoader()
        ukijumuisha CleanImport(self.spec.name):
            ukijumuisha self.assertRaises(RuntimeError):
                loaded = self.bootstrap._load(self.spec)
            self.assertNotIn(self.spec.name, sys.modules)

    eleza test_load_legacy(self):
        self.spec.loader = LegacyLoader()
        ukijumuisha CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)

        self.assertEqual(loaded.ham, -1)

    eleza test_load_legacy_attributes(self):
        self.spec.loader = LegacyLoader()
        ukijumuisha CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)

        self.assertIs(loaded.__loader__, self.spec.loader)
        self.assertEqual(loaded.__package__, self.spec.parent)
        self.assertIs(loaded.__spec__, self.spec)

    eleza test_load_legacy_attributes_immutable(self):
        module = object()
        kundi ImmutableLoader(TestLoader):
            eleza load_module(self, name):
                sys.modules[name] = module
                rudisha module
        self.spec.loader = ImmutableLoader()
        ukijumuisha CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)

            self.assertIs(sys.modules[self.spec.name], module)

    # reload()

    eleza test_reload(self):
        self.spec.loader = NewLoader()
        ukijumuisha CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            reloaded = self.bootstrap._exec(self.spec, loaded)
            installed = sys.modules[self.spec.name]

        self.assertEqual(loaded.eggs, 1)
        self.assertIs(reloaded, loaded)
        self.assertIs(installed, loaded)

    eleza test_reload_modified(self):
        self.spec.loader = NewLoader()
        ukijumuisha CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            loaded.eggs = 2
            reloaded = self.bootstrap._exec(self.spec, loaded)

        self.assertEqual(loaded.eggs, 1)
        self.assertIs(reloaded, loaded)

    eleza test_reload_extra_attributes(self):
        self.spec.loader = NewLoader()
        ukijumuisha CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            loaded.available = Uongo
            reloaded = self.bootstrap._exec(self.spec, loaded)

        self.assertUongo(loaded.available)
        self.assertIs(reloaded, loaded)

    eleza test_reload_init_module_attrs(self):
        self.spec.loader = NewLoader()
        ukijumuisha CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            loaded.__name__ = 'ham'
            toa loaded.__loader__
            toa loaded.__package__
            toa loaded.__spec__
            self.bootstrap._exec(self.spec, loaded)

        self.assertEqual(loaded.__name__, self.spec.name)
        self.assertIs(loaded.__loader__, self.spec.loader)
        self.assertEqual(loaded.__package__, self.spec.parent)
        self.assertIs(loaded.__spec__, self.spec)
        self.assertUongo(hasattr(loaded, '__path__'))
        self.assertUongo(hasattr(loaded, '__file__'))
        self.assertUongo(hasattr(loaded, '__cached__'))

    eleza test_reload_legacy(self):
        self.spec.loader = LegacyLoader()
        ukijumuisha CleanImport(self.spec.name):
            loaded = self.bootstrap._load(self.spec)
            reloaded = self.bootstrap._exec(self.spec, loaded)
            installed = sys.modules[self.spec.name]

        self.assertEqual(loaded.ham, -1)
        self.assertIs(reloaded, loaded)
        self.assertIs(installed, loaded)


(Frozen_ModuleSpecMethodsTests,
 Source_ModuleSpecMethodsTests
 ) = test_util.test_both(ModuleSpecMethodsTests, init=init, util=util,
                         machinery=machinery)


kundi ModuleReprTests:

    @property
    eleza bootstrap(self):
        rudisha self.init._bootstrap

    eleza setUp(self):
        self.module = type(os)('spam')
        self.spec = self.machinery.ModuleSpec('spam', TestLoader())

    eleza test_module___loader___module_repr(self):
        kundi Loader:
            eleza module_repr(self, module):
                rudisha '<delicious {}>'.format(module.__name__)
        self.module.__loader__ = Loader()
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr, '<delicious spam>')

    eleza test_module___loader___module_repr_bad(self):
        kundi Loader(TestLoader):
            eleza module_repr(self, module):
                 ashiria Exception
        self.module.__loader__ = Loader()
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr,
                         '<module {!r} (<TestLoader object>)>'.format('spam'))

    eleza test_module___spec__(self):
        origin = 'in a hole, kwenye the ground'
        self.spec.origin = origin
        self.module.__spec__ = self.spec
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr, '<module {!r} ({})>'.format('spam', origin))

    eleza test_module___spec___location(self):
        location = 'in_a_galaxy_far_far_away.py'
        self.spec.origin = location
        self.spec._set_fileattr = Kweli
        self.module.__spec__ = self.spec
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr,
                         '<module {!r} kutoka {!r}>'.format('spam', location))

    eleza test_module___spec___no_origin(self):
        self.spec.loader = TestLoader()
        self.module.__spec__ = self.spec
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr,
                         '<module {!r} (<TestLoader object>)>'.format('spam'))

    eleza test_module___spec___no_origin_no_loader(self):
        self.spec.loader = Tupu
        self.module.__spec__ = self.spec
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr, '<module {!r}>'.format('spam'))

    eleza test_module_no_name(self):
        toa self.module.__name__
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr, '<module {!r}>'.format('?'))

    eleza test_module_with_file(self):
        filename = 'e/i/e/i/o/spam.py'
        self.module.__file__ = filename
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr,
                         '<module {!r} kutoka {!r}>'.format('spam', filename))

    eleza test_module_no_file(self):
        self.module.__loader__ = TestLoader()
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr,
                         '<module {!r} (<TestLoader object>)>'.format('spam'))

    eleza test_module_no_file_no_loader(self):
        modrepr = self.bootstrap._module_repr(self.module)

        self.assertEqual(modrepr, '<module {!r}>'.format('spam'))


(Frozen_ModuleReprTests,
 Source_ModuleReprTests
 ) = test_util.test_both(ModuleReprTests, init=init, util=util,
                         machinery=machinery)


kundi FactoryTests:

    eleza setUp(self):
        self.name = 'spam'
        self.path = 'spam.py'
        self.cached = self.util.cache_from_source(self.path)
        self.loader = TestLoader()
        self.fileloader = TestLoader(self.path)
        self.pkgloader = TestLoader(self.path, Kweli)

    # spec_from_loader()

    eleza test_spec_from_loader_default(self):
        spec = self.util.spec_from_loader(self.name, self.loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, Tupu)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertIs(spec.cached, Tupu)
        self.assertUongo(spec.has_location)

    eleza test_spec_from_loader_default_with_bad_is_package(self):
        kundi Loader:
            eleza is_package(self, name):
                 ashiria ImportError
        loader = Loader()
        spec = self.util.spec_from_loader(self.name, loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, loader)
        self.assertIs(spec.origin, Tupu)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertIs(spec.cached, Tupu)
        self.assertUongo(spec.has_location)

    eleza test_spec_from_loader_origin(self):
        origin = 'somewhere over the rainbow'
        spec = self.util.spec_from_loader(self.name, self.loader,
                                          origin=origin)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, origin)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertIs(spec.cached, Tupu)
        self.assertUongo(spec.has_location)

    eleza test_spec_from_loader_is_package_false(self):
        spec = self.util.spec_from_loader(self.name, self.loader,
                                          is_package=Uongo)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, Tupu)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertIs(spec.cached, Tupu)
        self.assertUongo(spec.has_location)

    eleza test_spec_from_loader_is_package_true(self):
        spec = self.util.spec_from_loader(self.name, self.loader,
                                          is_package=Kweli)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, Tupu)
        self.assertIs(spec.loader_state, Tupu)
        self.assertEqual(spec.submodule_search_locations, [])
        self.assertIs(spec.cached, Tupu)
        self.assertUongo(spec.has_location)

    eleza test_spec_from_loader_origin_and_is_package(self):
        origin = 'where the streets have no name'
        spec = self.util.spec_from_loader(self.name, self.loader,
                                          origin=origin, is_package=Kweli)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertIs(spec.origin, origin)
        self.assertIs(spec.loader_state, Tupu)
        self.assertEqual(spec.submodule_search_locations, [])
        self.assertIs(spec.cached, Tupu)
        self.assertUongo(spec.has_location)

    eleza test_spec_from_loader_is_package_with_loader_false(self):
        loader = TestLoader(is_package=Uongo)
        spec = self.util.spec_from_loader(self.name, loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, loader)
        self.assertIs(spec.origin, Tupu)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertIs(spec.cached, Tupu)
        self.assertUongo(spec.has_location)

    eleza test_spec_from_loader_is_package_with_loader_true(self):
        loader = TestLoader(is_package=Kweli)
        spec = self.util.spec_from_loader(self.name, loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, loader)
        self.assertIs(spec.origin, Tupu)
        self.assertIs(spec.loader_state, Tupu)
        self.assertEqual(spec.submodule_search_locations, [])
        self.assertIs(spec.cached, Tupu)
        self.assertUongo(spec.has_location)

    eleza test_spec_from_loader_default_with_file_loader(self):
        spec = self.util.spec_from_loader(self.name, self.fileloader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertEqual(spec.cached, self.cached)
        self.assertKweli(spec.has_location)

    eleza test_spec_from_loader_is_package_false_with_fileloader(self):
        spec = self.util.spec_from_loader(self.name, self.fileloader,
                                          is_package=Uongo)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertEqual(spec.cached, self.cached)
        self.assertKweli(spec.has_location)

    eleza test_spec_from_loader_is_package_true_with_fileloader(self):
        spec = self.util.spec_from_loader(self.name, self.fileloader,
                                          is_package=Kweli)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Tupu)
        self.assertEqual(spec.submodule_search_locations, [''])
        self.assertEqual(spec.cached, self.cached)
        self.assertKweli(spec.has_location)

    # spec_from_file_location()

    eleza test_spec_from_file_location_default(self):
        spec = self.util.spec_from_file_location(self.name, self.path)

        self.assertEqual(spec.name, self.name)
        # Need to use a circuitous route to get at importlib.machinery to make
        # sure the same kundi object ni used kwenye the isinstance() check as
        # would have been used to create the loader.
        self.assertIsInstance(spec.loader,
                              self.util.abc.machinery.SourceFileLoader)
        self.assertEqual(spec.loader.name, self.name)
        self.assertEqual(spec.loader.path, self.path)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertEqual(spec.cached, self.cached)
        self.assertKweli(spec.has_location)

    eleza test_spec_from_file_location_path_like_arg(self):
        spec = self.util.spec_from_file_location(self.name,
                                                 pathlib.PurePath(self.path))
        self.assertEqual(spec.origin, self.path)

    eleza test_spec_from_file_location_default_without_location(self):
        spec = self.util.spec_from_file_location(self.name)

        self.assertIs(spec, Tupu)

    eleza test_spec_from_file_location_default_bad_suffix(self):
        spec = self.util.spec_from_file_location(self.name, 'spam.eggs')

        self.assertIs(spec, Tupu)

    eleza test_spec_from_file_location_loader_no_location(self):
        spec = self.util.spec_from_file_location(self.name,
                                                 loader=self.fileloader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertEqual(spec.cached, self.cached)
        self.assertKweli(spec.has_location)

    eleza test_spec_from_file_location_loader_no_location_no_get_filename(self):
        spec = self.util.spec_from_file_location(self.name,
                                                 loader=self.loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.loader)
        self.assertEqual(spec.origin, '<unknown>')
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertIs(spec.cached, Tupu)
        self.assertKweli(spec.has_location)

    eleza test_spec_from_file_location_loader_no_location_bad_get_filename(self):
        kundi Loader:
            eleza get_filename(self, name):
                 ashiria ImportError
        loader = Loader()
        spec = self.util.spec_from_file_location(self.name, loader=loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, loader)
        self.assertEqual(spec.origin, '<unknown>')
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertIs(spec.cached, Tupu)
        self.assertKweli(spec.has_location)

    eleza test_spec_from_file_location_smsl_none(self):
        spec = self.util.spec_from_file_location(self.name, self.path,
                                       loader=self.fileloader,
                                       submodule_search_locations=Tupu)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertEqual(spec.cached, self.cached)
        self.assertKweli(spec.has_location)

    eleza test_spec_from_file_location_smsl_empty(self):
        spec = self.util.spec_from_file_location(self.name, self.path,
                                       loader=self.fileloader,
                                       submodule_search_locations=[])

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Tupu)
        self.assertEqual(spec.submodule_search_locations, [''])
        self.assertEqual(spec.cached, self.cached)
        self.assertKweli(spec.has_location)

    eleza test_spec_from_file_location_smsl_not_empty(self):
        spec = self.util.spec_from_file_location(self.name, self.path,
                                       loader=self.fileloader,
                                       submodule_search_locations=['eggs'])

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Tupu)
        self.assertEqual(spec.submodule_search_locations, ['eggs'])
        self.assertEqual(spec.cached, self.cached)
        self.assertKweli(spec.has_location)

    eleza test_spec_from_file_location_smsl_default(self):
        spec = self.util.spec_from_file_location(self.name, self.path,
                                       loader=self.pkgloader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.pkgloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Tupu)
        self.assertEqual(spec.submodule_search_locations, [''])
        self.assertEqual(spec.cached, self.cached)
        self.assertKweli(spec.has_location)

    eleza test_spec_from_file_location_smsl_default_not_package(self):
        kundi Loader:
            eleza is_package(self, name):
                rudisha Uongo
        loader = Loader()
        spec = self.util.spec_from_file_location(self.name, self.path,
                                                 loader=loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, loader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertEqual(spec.cached, self.cached)
        self.assertKweli(spec.has_location)

    eleza test_spec_from_file_location_smsl_default_no_is_package(self):
        spec = self.util.spec_from_file_location(self.name, self.path,
                                       loader=self.fileloader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, self.fileloader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertEqual(spec.cached, self.cached)
        self.assertKweli(spec.has_location)

    eleza test_spec_from_file_location_smsl_default_bad_is_package(self):
        kundi Loader:
            eleza is_package(self, name):
                 ashiria ImportError
        loader = Loader()
        spec = self.util.spec_from_file_location(self.name, self.path,
                                                 loader=loader)

        self.assertEqual(spec.name, self.name)
        self.assertEqual(spec.loader, loader)
        self.assertEqual(spec.origin, self.path)
        self.assertIs(spec.loader_state, Tupu)
        self.assertIs(spec.submodule_search_locations, Tupu)
        self.assertEqual(spec.cached, self.cached)
        self.assertKweli(spec.has_location)


(Frozen_FactoryTests,
 Source_FactoryTests
 ) = test_util.test_both(FactoryTests, util=util, machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
