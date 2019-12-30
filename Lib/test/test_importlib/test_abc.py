agiza io
agiza marshal
agiza os
agiza sys
kutoka test agiza support
agiza types
agiza unittest
kutoka unittest agiza mock
agiza warnings

kutoka . agiza util kama test_util

init = test_util.import_importlib('importlib')
abc = test_util.import_importlib('importlib.abc')
machinery = test_util.import_importlib('importlib.machinery')
util = test_util.import_importlib('importlib.util')


##### Inheritance ##############################################################
kundi InheritanceTests:

    """Test that the specified kundi ni a subclass/superkundi of the expected
    classes."""

    subclasses = []
    superclasses = []

    eleza setUp(self):
        self.superclasses = [getattr(self.abc, class_name)
                             kila class_name kwenye self.superclass_names]
        ikiwa hasattr(self, 'subclass_names'):
            # Because test.support.import_fresh_module() creates a new
            # importlib._bootstrap per module, inheritance checks fail when
            # checking across module boundaries (i.e. the _bootstrap kwenye abc is
            # sio the same kama the one kwenye machinery). That means stealing one of
            # the modules kutoka the other to make sure the same instance ni used.
            machinery = self.abc.machinery
            self.subclasses = [getattr(machinery, class_name)
                               kila class_name kwenye self.subclass_names]
        assert self.subclasses ama self.superclasses, self.__class__
        self.__test = getattr(self.abc, self._NAME)

    eleza test_subclasses(self):
        # Test that the expected subclasses inherit.
        kila subkundi kwenye self.subclasses:
            self.assertKweli(issubclass(subclass, self.__test),
                "{0} ni sio a subkundi of {1}".format(subclass, self.__test))

    eleza test_superclasses(self):
        # Test that the kundi inherits kutoka the expected superclasses.
        kila superkundi kwenye self.superclasses:
            self.assertKweli(issubclass(self.__test, superclass),
               "{0} ni sio a superkundi of {1}".format(superclass, self.__test))


kundi MetaPathFinder(InheritanceTests):
    superclass_names = ['Finder']
    subclass_names = ['BuiltinImporter', 'FrozenImporter', 'PathFinder',
                      'WindowsRegistryFinder']


(Frozen_MetaPathFinderInheritanceTests,
 Source_MetaPathFinderInheritanceTests
 ) = test_util.test_both(MetaPathFinder, abc=abc)


kundi PathEntryFinder(InheritanceTests):
    superclass_names = ['Finder']
    subclass_names = ['FileFinder']


(Frozen_PathEntryFinderInheritanceTests,
 Source_PathEntryFinderInheritanceTests
 ) = test_util.test_both(PathEntryFinder, abc=abc)


kundi ResourceLoader(InheritanceTests):
    superclass_names = ['Loader']


(Frozen_ResourceLoaderInheritanceTests,
 Source_ResourceLoaderInheritanceTests
 ) = test_util.test_both(ResourceLoader, abc=abc)


kundi InspectLoader(InheritanceTests):
    superclass_names = ['Loader']
    subclass_names = ['BuiltinImporter', 'FrozenImporter', 'ExtensionFileLoader']


(Frozen_InspectLoaderInheritanceTests,
 Source_InspectLoaderInheritanceTests
 ) = test_util.test_both(InspectLoader, abc=abc)


kundi ExecutionLoader(InheritanceTests):
    superclass_names = ['InspectLoader']
    subclass_names = ['ExtensionFileLoader']


(Frozen_ExecutionLoaderInheritanceTests,
 Source_ExecutionLoaderInheritanceTests
 ) = test_util.test_both(ExecutionLoader, abc=abc)


kundi FileLoader(InheritanceTests):
    superclass_names = ['ResourceLoader', 'ExecutionLoader']
    subclass_names = ['SourceFileLoader', 'SourcelessFileLoader']


(Frozen_FileLoaderInheritanceTests,
 Source_FileLoaderInheritanceTests
 ) = test_util.test_both(FileLoader, abc=abc)


kundi SourceLoader(InheritanceTests):
    superclass_names = ['ResourceLoader', 'ExecutionLoader']
    subclass_names = ['SourceFileLoader']


(Frozen_SourceLoaderInheritanceTests,
 Source_SourceLoaderInheritanceTests
 ) = test_util.test_both(SourceLoader, abc=abc)


##### Default rudisha values ####################################################

eleza make_abc_subclasses(base_class, name=Tupu, inst=Uongo, **kwargs):
    ikiwa name ni Tupu:
        name = base_class.__name__
    base = {kind: getattr(splitabc, name)
            kila kind, splitabc kwenye abc.items()}
    rudisha {cls._KIND: cls() ikiwa inst isipokua cls
            kila cls kwenye test_util.split_frozen(base_class, base, **kwargs)}


kundi ABCTestHarness:

    @property
    eleza ins(self):
        # Lazily set ins on the class.
        cls = self.SPLIT[self._KIND]
        ins = cls()
        self.__class__.ins = ins
        rudisha ins


kundi MetaPathFinder:

    eleza find_module(self, fullname, path):
        rudisha super().find_module(fullname, path)


kundi MetaPathFinderDefaultsTests(ABCTestHarness):

    SPLIT = make_abc_subclasses(MetaPathFinder)

    eleza test_find_module(self):
        # Default should rudisha Tupu.
        ukijumuisha self.assertWarns(DeprecationWarning):
            found = self.ins.find_module('something', Tupu)
        self.assertIsTupu(found)

    eleza test_invalidate_caches(self):
        # Calling the method ni a no-op.
        self.ins.invalidate_caches()


(Frozen_MPFDefaultTests,
 Source_MPFDefaultTests
 ) = test_util.test_both(MetaPathFinderDefaultsTests)


kundi PathEntryFinder:

    eleza find_loader(self, fullname):
        rudisha super().find_loader(fullname)


kundi PathEntryFinderDefaultsTests(ABCTestHarness):

    SPLIT = make_abc_subclasses(PathEntryFinder)

    eleza test_find_loader(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            found = self.ins.find_loader('something')
        self.assertEqual(found, (Tupu, []))

    eleza find_module(self):
        self.assertEqual(Tupu, self.ins.find_module('something'))

    eleza test_invalidate_caches(self):
        # Should be a no-op.
        self.ins.invalidate_caches()


(Frozen_PEFDefaultTests,
 Source_PEFDefaultTests
 ) = test_util.test_both(PathEntryFinderDefaultsTests)


kundi Loader:

    eleza load_module(self, fullname):
        rudisha super().load_module(fullname)


kundi LoaderDefaultsTests(ABCTestHarness):

    SPLIT = make_abc_subclasses(Loader)

    eleza test_create_module(self):
        spec = 'a spec'
        self.assertIsTupu(self.ins.create_module(spec))

    eleza test_load_module(self):
        ukijumuisha self.assertRaises(ImportError):
            self.ins.load_module('something')

    eleza test_module_repr(self):
        mod = types.ModuleType('blah')
        ukijumuisha self.assertRaises(NotImplementedError):
            self.ins.module_repr(mod)
        original_repr = repr(mod)
        mod.__loader__ = self.ins
        # Should still rudisha a proper repr.
        self.assertKweli(repr(mod))


(Frozen_LDefaultTests,
 SourceLDefaultTests
 ) = test_util.test_both(LoaderDefaultsTests)


kundi ResourceLoader(Loader):

    eleza get_data(self, path):
        rudisha super().get_data(path)


kundi ResourceLoaderDefaultsTests(ABCTestHarness):

    SPLIT = make_abc_subclasses(ResourceLoader)

    eleza test_get_data(self):
        ukijumuisha self.assertRaises(IOError):
            self.ins.get_data('/some/path')


(Frozen_RLDefaultTests,
 Source_RLDefaultTests
 ) = test_util.test_both(ResourceLoaderDefaultsTests)


kundi InspectLoader(Loader):

    eleza is_package(self, fullname):
        rudisha super().is_package(fullname)

    eleza get_source(self, fullname):
        rudisha super().get_source(fullname)


SPLIT_IL = make_abc_subclasses(InspectLoader)


kundi InspectLoaderDefaultsTests(ABCTestHarness):

    SPLIT = SPLIT_IL

    eleza test_is_package(self):
        ukijumuisha self.assertRaises(ImportError):
            self.ins.is_package('blah')

    eleza test_get_source(self):
        ukijumuisha self.assertRaises(ImportError):
            self.ins.get_source('blah')


(Frozen_ILDefaultTests,
 Source_ILDefaultTests
 ) = test_util.test_both(InspectLoaderDefaultsTests)


kundi ExecutionLoader(InspectLoader):

    eleza get_filename(self, fullname):
        rudisha super().get_filename(fullname)


SPLIT_EL = make_abc_subclasses(ExecutionLoader)


kundi ExecutionLoaderDefaultsTests(ABCTestHarness):

    SPLIT = SPLIT_EL

    eleza test_get_filename(self):
        ukijumuisha self.assertRaises(ImportError):
            self.ins.get_filename('blah')


(Frozen_ELDefaultTests,
 Source_ELDefaultsTests
 ) = test_util.test_both(InspectLoaderDefaultsTests)


kundi ResourceReader:

    eleza open_resource(self, *args, **kwargs):
        rudisha super().open_resource(*args, **kwargs)

    eleza resource_path(self, *args, **kwargs):
        rudisha super().resource_path(*args, **kwargs)

    eleza is_resource(self, *args, **kwargs):
        rudisha super().is_resource(*args, **kwargs)

    eleza contents(self, *args, **kwargs):
        rudisha super().contents(*args, **kwargs)


kundi ResourceReaderDefaultsTests(ABCTestHarness):

    SPLIT = make_abc_subclasses(ResourceReader)

    eleza test_open_resource(self):
        ukijumuisha self.assertRaises(FileNotFoundError):
            self.ins.open_resource('dummy_file')

    eleza test_resource_path(self):
        ukijumuisha self.assertRaises(FileNotFoundError):
            self.ins.resource_path('dummy_file')

    eleza test_is_resource(self):
        ukijumuisha self.assertRaises(FileNotFoundError):
            self.ins.is_resource('dummy_file')

    eleza test_contents(self):
        self.assertEqual([], list(self.ins.contents()))

(Frozen_RRDefaultTests,
 Source_RRDefaultsTests
 ) = test_util.test_both(ResourceReaderDefaultsTests)


##### MetaPathFinder concrete methods ##########################################
kundi MetaPathFinderFindModuleTests:

    @classmethod
    eleza finder(cls, spec):
        kundi MetaPathSpecFinder(cls.abc.MetaPathFinder):

            eleza find_spec(self, fullname, path, target=Tupu):
                self.called_kila = fullname, path
                rudisha spec

        rudisha MetaPathSpecFinder()

    eleza test_no_spec(self):
        finder = self.finder(Tupu)
        path = ['a', 'b', 'c']
        name = 'blah'
        ukijumuisha self.assertWarns(DeprecationWarning):
            found = finder.find_module(name, path)
        self.assertIsTupu(found)
        self.assertEqual(name, finder.called_for[0])
        self.assertEqual(path, finder.called_for[1])

    eleza test_spec(self):
        loader = object()
        spec = self.util.spec_from_loader('blah', loader)
        finder = self.finder(spec)
        ukijumuisha self.assertWarns(DeprecationWarning):
            found = finder.find_module('blah', Tupu)
        self.assertIs(found, spec.loader)


(Frozen_MPFFindModuleTests,
 Source_MPFFindModuleTests
 ) = test_util.test_both(MetaPathFinderFindModuleTests, abc=abc, util=util)


##### PathEntryFinder concrete methods #########################################
kundi PathEntryFinderFindLoaderTests:

    @classmethod
    eleza finder(cls, spec):
        kundi PathEntrySpecFinder(cls.abc.PathEntryFinder):

            eleza find_spec(self, fullname, target=Tupu):
                self.called_kila = fullname
                rudisha spec

        rudisha PathEntrySpecFinder()

    eleza test_no_spec(self):
        finder = self.finder(Tupu)
        name = 'blah'
        ukijumuisha self.assertWarns(DeprecationWarning):
            found = finder.find_loader(name)
        self.assertIsTupu(found[0])
        self.assertEqual([], found[1])
        self.assertEqual(name, finder.called_for)

    eleza test_spec_with_loader(self):
        loader = object()
        spec = self.util.spec_from_loader('blah', loader)
        finder = self.finder(spec)
        ukijumuisha self.assertWarns(DeprecationWarning):
            found = finder.find_loader('blah')
        self.assertIs(found[0], spec.loader)

    eleza test_spec_with_portions(self):
        spec = self.machinery.ModuleSpec('blah', Tupu)
        paths = ['a', 'b', 'c']
        spec.submodule_search_locations = paths
        finder = self.finder(spec)
        ukijumuisha self.assertWarns(DeprecationWarning):
            found = finder.find_loader('blah')
        self.assertIsTupu(found[0])
        self.assertEqual(paths, found[1])


(Frozen_PEFFindLoaderTests,
 Source_PEFFindLoaderTests
 ) = test_util.test_both(PathEntryFinderFindLoaderTests, abc=abc, util=util,
                         machinery=machinery)


##### Loader concrete methods ##################################################
kundi LoaderLoadModuleTests:

    eleza loader(self):
        kundi SpecLoader(self.abc.Loader):
            found = Tupu
            eleza exec_module(self, module):
                self.found = module

            eleza is_package(self, fullname):
                """Force some non-default module state to be set."""
                rudisha Kweli

        rudisha SpecLoader()

    eleza test_fresh(self):
        loader = self.loader()
        name = 'blah'
        ukijumuisha test_util.uncache(name):
            loader.load_module(name)
            module = loader.found
            self.assertIs(sys.modules[name], module)
        self.assertEqual(loader, module.__loader__)
        self.assertEqual(loader, module.__spec__.loader)
        self.assertEqual(name, module.__name__)
        self.assertEqual(name, module.__spec__.name)
        self.assertIsNotTupu(module.__path__)
        self.assertIsNotTupu(module.__path__,
                             module.__spec__.submodule_search_locations)

    eleza test_reload(self):
        name = 'blah'
        loader = self.loader()
        module = types.ModuleType(name)
        module.__spec__ = self.util.spec_from_loader(name, loader)
        module.__loader__ = loader
        ukijumuisha test_util.uncache(name):
            sys.modules[name] = module
            loader.load_module(name)
            found = loader.found
            self.assertIs(found, sys.modules[name])
            self.assertIs(module, sys.modules[name])


(Frozen_LoaderLoadModuleTests,
 Source_LoaderLoadModuleTests
 ) = test_util.test_both(LoaderLoadModuleTests, abc=abc, util=util)


##### InspectLoader concrete methods ###########################################
kundi InspectLoaderSourceToCodeTests:

    eleza source_to_module(self, data, path=Tupu):
        """Help ukijumuisha source_to_code() tests."""
        module = types.ModuleType('blah')
        loader = self.InspectLoaderSubclass()
        ikiwa path ni Tupu:
            code = loader.source_to_code(data)
        isipokua:
            code = loader.source_to_code(data, path)
        exec(code, module.__dict__)
        rudisha module

    eleza test_source_to_code_source(self):
        # Since compile() can handle strings, so should source_to_code().
        source = 'attr = 42'
        module = self.source_to_module(source)
        self.assertKweli(hasattr(module, 'attr'))
        self.assertEqual(module.attr, 42)

    eleza test_source_to_code_bytes(self):
        # Since compile() can handle bytes, so should source_to_code().
        source = b'attr = 42'
        module = self.source_to_module(source)
        self.assertKweli(hasattr(module, 'attr'))
        self.assertEqual(module.attr, 42)

    eleza test_source_to_code_path(self):
        # Specifying a path should set it kila the code object.
        path = 'path/to/somewhere'
        loader = self.InspectLoaderSubclass()
        code = loader.source_to_code('', path)
        self.assertEqual(code.co_filename, path)

    eleza test_source_to_code_no_path(self):
        # Not setting a path should still work na be set to <string> since that
        # ni a pre-existing practice kama a default to compile().
        loader = self.InspectLoaderSubclass()
        code = loader.source_to_code('')
        self.assertEqual(code.co_filename, '<string>')


(Frozen_ILSourceToCodeTests,
 Source_ILSourceToCodeTests
 ) = test_util.test_both(InspectLoaderSourceToCodeTests,
                         InspectLoaderSubclass=SPLIT_IL)


kundi InspectLoaderGetCodeTests:

    eleza test_get_code(self):
        # Test success.
        module = types.ModuleType('blah')
        ukijumuisha mock.patch.object(self.InspectLoaderSubclass, 'get_source') kama mocked:
            mocked.return_value = 'attr = 42'
            loader = self.InspectLoaderSubclass()
            code = loader.get_code('blah')
        exec(code, module.__dict__)
        self.assertEqual(module.attr, 42)

    eleza test_get_code_source_is_Tupu(self):
        # If get_source() ni Tupu then this should be Tupu.
        ukijumuisha mock.patch.object(self.InspectLoaderSubclass, 'get_source') kama mocked:
            mocked.return_value = Tupu
            loader = self.InspectLoaderSubclass()
            code = loader.get_code('blah')
        self.assertIsTupu(code)

    eleza test_get_code_source_not_found(self):
        # If there ni no source then there ni no code object.
        loader = self.InspectLoaderSubclass()
        ukijumuisha self.assertRaises(ImportError):
            loader.get_code('blah')


(Frozen_ILGetCodeTests,
 Source_ILGetCodeTests
 ) = test_util.test_both(InspectLoaderGetCodeTests,
                         InspectLoaderSubclass=SPLIT_IL)


kundi InspectLoaderLoadModuleTests:

    """Test InspectLoader.load_module()."""

    module_name = 'blah'

    eleza setUp(self):
        support.unload(self.module_name)
        self.addCleanup(support.unload, self.module_name)

    eleza load(self, loader):
        spec = self.util.spec_from_loader(self.module_name, loader)
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            rudisha self.init._bootstrap._load_unlocked(spec)

    eleza mock_get_code(self):
        rudisha mock.patch.object(self.InspectLoaderSubclass, 'get_code')

    eleza test_get_code_ImportError(self):
        # If get_code() raises ImportError, it should propagate.
        ukijumuisha self.mock_get_code() kama mocked_get_code:
            mocked_get_code.side_effect = ImportError
            ukijumuisha self.assertRaises(ImportError):
                loader = self.InspectLoaderSubclass()
                self.load(loader)

    eleza test_get_code_Tupu(self):
        # If get_code() returns Tupu, ashiria ImportError.
        ukijumuisha self.mock_get_code() kama mocked_get_code:
            mocked_get_code.return_value = Tupu
            ukijumuisha self.assertRaises(ImportError):
                loader = self.InspectLoaderSubclass()
                self.load(loader)

    eleza test_module_returned(self):
        # The loaded module should be returned.
        code = compile('attr = 42', '<string>', 'exec')
        ukijumuisha self.mock_get_code() kama mocked_get_code:
            mocked_get_code.return_value = code
            loader = self.InspectLoaderSubclass()
            module = self.load(loader)
            self.assertEqual(module, sys.modules[self.module_name])


(Frozen_ILLoadModuleTests,
 Source_ILLoadModuleTests
 ) = test_util.test_both(InspectLoaderLoadModuleTests,
                         InspectLoaderSubclass=SPLIT_IL,
                         init=init,
                         util=util)


##### ExecutionLoader concrete methods #########################################
kundi ExecutionLoaderGetCodeTests:

    eleza mock_methods(self, *, get_source=Uongo, get_filename=Uongo):
        source_mock_context, filename_mock_context = Tupu, Tupu
        ikiwa get_source:
            source_mock_context = mock.patch.object(self.ExecutionLoaderSubclass,
                                                    'get_source')
        ikiwa get_filename:
            filename_mock_context = mock.patch.object(self.ExecutionLoaderSubclass,
                                                      'get_filename')
        rudisha source_mock_context, filename_mock_context

    eleza test_get_code(self):
        path = 'blah.py'
        source_mock_context, filename_mock_context = self.mock_methods(
                get_source=Kweli, get_filename=Kweli)
        ukijumuisha source_mock_context kama source_mock, filename_mock_context kama name_mock:
            source_mock.return_value = 'attr = 42'
            name_mock.return_value = path
            loader = self.ExecutionLoaderSubclass()
            code = loader.get_code('blah')
        self.assertEqual(code.co_filename, path)
        module = types.ModuleType('blah')
        exec(code, module.__dict__)
        self.assertEqual(module.attr, 42)

    eleza test_get_code_source_is_Tupu(self):
        # If get_source() ni Tupu then this should be Tupu.
        source_mock_context, _ = self.mock_methods(get_source=Kweli)
        ukijumuisha source_mock_context kama mocked:
            mocked.return_value = Tupu
            loader = self.ExecutionLoaderSubclass()
            code = loader.get_code('blah')
        self.assertIsTupu(code)

    eleza test_get_code_source_not_found(self):
        # If there ni no source then there ni no code object.
        loader = self.ExecutionLoaderSubclass()
        ukijumuisha self.assertRaises(ImportError):
            loader.get_code('blah')

    eleza test_get_code_no_path(self):
        # If get_filename() raises ImportError then simply skip setting the path
        # on the code object.
        source_mock_context, filename_mock_context = self.mock_methods(
                get_source=Kweli, get_filename=Kweli)
        ukijumuisha source_mock_context kama source_mock, filename_mock_context kama name_mock:
            source_mock.return_value = 'attr = 42'
            name_mock.side_effect = ImportError
            loader = self.ExecutionLoaderSubclass()
            code = loader.get_code('blah')
        self.assertEqual(code.co_filename, '<string>')
        module = types.ModuleType('blah')
        exec(code, module.__dict__)
        self.assertEqual(module.attr, 42)


(Frozen_ELGetCodeTests,
 Source_ELGetCodeTests
 ) = test_util.test_both(ExecutionLoaderGetCodeTests,
                         ExecutionLoaderSubclass=SPLIT_EL)


##### SourceLoader concrete methods ############################################
kundi SourceOnlyLoader:

    # Globals that should be defined kila all modules.
    source = (b"_ = '::'.join([__name__, __file__, __cached__, __package__, "
              b"repr(__loader__)])")

    eleza __init__(self, path):
        self.path = path

    eleza get_data(self, path):
        ikiwa path != self.path:
            ashiria IOError
        rudisha self.source

    eleza get_filename(self, fullname):
        rudisha self.path

    eleza module_repr(self, module):
        rudisha '<module>'


SPLIT_SOL = make_abc_subclasses(SourceOnlyLoader, 'SourceLoader')


kundi SourceLoader(SourceOnlyLoader):

    source_mtime = 1

    eleza __init__(self, path, magic=Tupu):
        super().__init__(path)
        self.bytecode_path = self.util.cache_from_source(self.path)
        self.source_size = len(self.source)
        ikiwa magic ni Tupu:
            magic = self.util.MAGIC_NUMBER
        data = bytearray(magic)
        data.extend(self.init._pack_uint32(0))
        data.extend(self.init._pack_uint32(self.source_mtime))
        data.extend(self.init._pack_uint32(self.source_size))
        code_object = compile(self.source, self.path, 'exec',
                                dont_inherit=Kweli)
        data.extend(marshal.dumps(code_object))
        self.bytecode = bytes(data)
        self.written = {}

    eleza get_data(self, path):
        ikiwa path == self.path:
            rudisha super().get_data(path)
        lasivyo path == self.bytecode_path:
            rudisha self.bytecode
        isipokua:
            ashiria OSError

    eleza path_stats(self, path):
        ikiwa path != self.path:
            ashiria IOError
        rudisha {'mtime': self.source_mtime, 'size': self.source_size}

    eleza set_data(self, path, data):
        self.written[path] = bytes(data)
        rudisha path == self.bytecode_path


SPLIT_SL = make_abc_subclasses(SourceLoader, util=util, init=init)


kundi SourceLoaderTestHarness:

    eleza setUp(self, *, is_package=Kweli, **kwargs):
        self.package = 'pkg'
        ikiwa is_package:
            self.path = os.path.join(self.package, '__init__.py')
            self.name = self.package
        isipokua:
            module_name = 'mod'
            self.path = os.path.join(self.package, '.'.join(['mod', 'py']))
            self.name = '.'.join([self.package, module_name])
        self.cached = self.util.cache_from_source(self.path)
        self.loader = self.loader_mock(self.path, **kwargs)

    eleza verify_module(self, module):
        self.assertEqual(module.__name__, self.name)
        self.assertEqual(module.__file__, self.path)
        self.assertEqual(module.__cached__, self.cached)
        self.assertEqual(module.__package__, self.package)
        self.assertEqual(module.__loader__, self.loader)
        values = module._.split('::')
        self.assertEqual(values[0], self.name)
        self.assertEqual(values[1], self.path)
        self.assertEqual(values[2], self.cached)
        self.assertEqual(values[3], self.package)
        self.assertEqual(values[4], repr(self.loader))

    eleza verify_code(self, code_object):
        module = types.ModuleType(self.name)
        module.__file__ = self.path
        module.__cached__ = self.cached
        module.__package__ = self.package
        module.__loader__ = self.loader
        module.__path__ = []
        exec(code_object, module.__dict__)
        self.verify_module(module)


kundi SourceOnlyLoaderTests(SourceLoaderTestHarness):

    """Test importlib.abc.SourceLoader kila source-only loading.

    Reload testing ni subsumed by the tests for
    importlib.util.module_for_loader.

    """

    eleza test_get_source(self):
        # Verify the source code ni returned kama a string.
        # If an OSError ni raised by get_data then ashiria ImportError.
        expected_source = self.loader.source.decode('utf-8')
        self.assertEqual(self.loader.get_source(self.name), expected_source)
        eleza raise_OSError(path):
            ashiria OSError
        self.loader.get_data = raise_OSError
        ukijumuisha self.assertRaises(ImportError) kama cm:
            self.loader.get_source(self.name)
        self.assertEqual(cm.exception.name, self.name)

    eleza test_is_package(self):
        # Properly detect when loading a package.
        self.setUp(is_package=Uongo)
        self.assertUongo(self.loader.is_package(self.name))
        self.setUp(is_package=Kweli)
        self.assertKweli(self.loader.is_package(self.name))
        self.assertUongo(self.loader.is_package(self.name + '.__init__'))

    eleza test_get_code(self):
        # Verify the code object ni created.
        code_object = self.loader.get_code(self.name)
        self.verify_code(code_object)

    eleza test_source_to_code(self):
        # Verify the compiled code object.
        code = self.loader.source_to_code(self.loader.source, self.path)
        self.verify_code(code)

    eleza test_load_module(self):
        # Loading a module should set __name__, __loader__, __package__,
        # __path__ (kila packages), __file__, na __cached__.
        # The module should also be put into sys.modules.
        ukijumuisha test_util.uncache(self.name):
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = self.loader.load_module(self.name)
            self.verify_module(module)
            self.assertEqual(module.__path__, [os.path.dirname(self.path)])
            self.assertIn(self.name, sys.modules)

    eleza test_package_settings(self):
        # __package__ needs to be set, wakati __path__ ni set on ikiwa the module
        # ni a package.
        # Testing the values kila a package are covered by test_load_module.
        self.setUp(is_package=Uongo)
        ukijumuisha test_util.uncache(self.name):
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = self.loader.load_module(self.name)
            self.verify_module(module)
            self.assertUongo(hasattr(module, '__path__'))

    eleza test_get_source_encoding(self):
        # Source ni considered encoded kwenye UTF-8 by default unless otherwise
        # specified by an encoding line.
        source = "_ = 'ü'"
        self.loader.source = source.encode('utf-8')
        returned_source = self.loader.get_source(self.name)
        self.assertEqual(returned_source, source)
        source = "# coding: latin-1\n_ = ü"
        self.loader.source = source.encode('latin-1')
        returned_source = self.loader.get_source(self.name)
        self.assertEqual(returned_source, source)


(Frozen_SourceOnlyLoaderTests,
 Source_SourceOnlyLoaderTests
 ) = test_util.test_both(SourceOnlyLoaderTests, util=util,
                         loader_mock=SPLIT_SOL)


@unittest.skipIf(sys.dont_write_bytecode, "sys.dont_write_bytecode ni true")
kundi SourceLoaderBytecodeTests(SourceLoaderTestHarness):

    """Test importlib.abc.SourceLoader's use of bytecode.

    Source-only testing handled by SourceOnlyLoaderTests.

    """

    eleza verify_code(self, code_object, *, bytecode_written=Uongo):
        super().verify_code(code_object)
        ikiwa bytecode_written:
            self.assertIn(self.cached, self.loader.written)
            data = bytearray(self.util.MAGIC_NUMBER)
            data.extend(self.init._pack_uint32(0))
            data.extend(self.init._pack_uint32(self.loader.source_mtime))
            data.extend(self.init._pack_uint32(self.loader.source_size))
            data.extend(marshal.dumps(code_object))
            self.assertEqual(self.loader.written[self.cached], bytes(data))

    eleza test_code_with_everything(self):
        # When everything should work.
        code_object = self.loader.get_code(self.name)
        self.verify_code(code_object)

    eleza test_no_bytecode(self):
        # If no bytecode exists then move on to the source.
        self.loader.bytecode_path = "<does sio exist>"
        # Sanity check
        ukijumuisha self.assertRaises(OSError):
            bytecode_path = self.util.cache_from_source(self.path)
            self.loader.get_data(bytecode_path)
        code_object = self.loader.get_code(self.name)
        self.verify_code(code_object, bytecode_written=Kweli)

    eleza test_code_bad_timestamp(self):
        # Bytecode ni only used when the timestamp matches the source EXACTLY.
        kila source_mtime kwenye (0, 2):
            assert source_mtime != self.loader.source_mtime
            original = self.loader.source_mtime
            self.loader.source_mtime = source_mtime
            # If bytecode ni used then EOFError would be raised by marshal.
            self.loader.bytecode = self.loader.bytecode[8:]
            code_object = self.loader.get_code(self.name)
            self.verify_code(code_object, bytecode_written=Kweli)
            self.loader.source_mtime = original

    eleza test_code_bad_magic(self):
        # Skip over bytecode ukijumuisha a bad magic number.
        self.setUp(magic=b'0000')
        # If bytecode ni used then EOFError would be raised by marshal.
        self.loader.bytecode = self.loader.bytecode[8:]
        code_object = self.loader.get_code(self.name)
        self.verify_code(code_object, bytecode_written=Kweli)

    eleza test_dont_write_bytecode(self):
        # Bytecode ni sio written ikiwa sys.dont_write_bytecode ni true.
        # Can assume it ni false already thanks to the skipIf kundi decorator.
        jaribu:
            sys.dont_write_bytecode = Kweli
            self.loader.bytecode_path = "<does sio exist>"
            code_object = self.loader.get_code(self.name)
            self.assertNotIn(self.cached, self.loader.written)
        mwishowe:
            sys.dont_write_bytecode = Uongo

    eleza test_no_set_data(self):
        # If set_data ni sio defined, one can still read bytecode.
        self.setUp(magic=b'0000')
        original_set_data = self.loader.__class__.mro()[1].set_data
        jaribu:
            toa self.loader.__class__.mro()[1].set_data
            code_object = self.loader.get_code(self.name)
            self.verify_code(code_object)
        mwishowe:
            self.loader.__class__.mro()[1].set_data = original_set_data

    eleza test_set_data_raises_exceptions(self):
        # Raising NotImplementedError ama OSError ni okay kila set_data.
        eleza raise_exception(exc):
            eleza closure(*args, **kwargs):
                ashiria exc
            rudisha closure

        self.setUp(magic=b'0000')
        self.loader.set_data = raise_exception(NotImplementedError)
        code_object = self.loader.get_code(self.name)
        self.verify_code(code_object)


(Frozen_SLBytecodeTests,
 SourceSLBytecodeTests
 ) = test_util.test_both(SourceLoaderBytecodeTests, init=init, util=util,
                         loader_mock=SPLIT_SL)


kundi SourceLoaderGetSourceTests:

    """Tests kila importlib.abc.SourceLoader.get_source()."""

    eleza test_default_encoding(self):
        # Should have no problems ukijumuisha UTF-8 text.
        name = 'mod'
        mock = self.SourceOnlyLoaderMock('mod.file')
        source = 'x = "ü"'
        mock.source = source.encode('utf-8')
        returned_source = mock.get_source(name)
        self.assertEqual(returned_source, source)

    eleza test_decoded_source(self):
        # Decoding should work.
        name = 'mod'
        mock = self.SourceOnlyLoaderMock("mod.file")
        source = "# coding: Latin-1\nx='ü'"
        assert source.encode('latin-1') != source.encode('utf-8')
        mock.source = source.encode('latin-1')
        returned_source = mock.get_source(name)
        self.assertEqual(returned_source, source)

    eleza test_universal_newlines(self):
        # PEP 302 says universal newlines should be used.
        name = 'mod'
        mock = self.SourceOnlyLoaderMock('mod.file')
        source = "x = 42\r\ny = -13\r\n"
        mock.source = source.encode('utf-8')
        expect = io.IncrementalNewlineDecoder(Tupu, Kweli).decode(source)
        self.assertEqual(mock.get_source(name), expect)


(Frozen_SourceOnlyLoaderGetSourceTests,
 Source_SourceOnlyLoaderGetSourceTests
 ) = test_util.test_both(SourceLoaderGetSourceTests,
                         SourceOnlyLoaderMock=SPLIT_SOL)


ikiwa __name__ == '__main__':
    unittest.main()
