kutoka . agiza util
abc = util.import_importlib('importlib.abc')
init = util.import_importlib('importlib')
machinery = util.import_importlib('importlib.machinery')
importlib_util = util.import_importlib('importlib.util')

agiza importlib.util
agiza os
agiza pathlib
agiza string
agiza sys
kutoka test agiza support
agiza types
agiza unittest
agiza unittest.mock
agiza warnings


kundi DecodeSourceBytesTests:

    source = "string ='ü'"

    eleza test_ut8_default(self):
        source_bytes = self.source.encode('utf-8')
        self.assertEqual(self.util.decode_source(source_bytes), self.source)

    eleza test_specified_encoding(self):
        source = '# coding=latin-1\n' + self.source
        source_bytes = source.encode('latin-1')
        assert source_bytes != source.encode('utf-8')
        self.assertEqual(self.util.decode_source(source_bytes), source)

    eleza test_universal_newlines(self):
        source = '\r\n'.join([self.source, self.source])
        source_bytes = source.encode('utf-8')
        self.assertEqual(self.util.decode_source(source_bytes),
                         '\n'.join([self.source, self.source]))


(Frozen_DecodeSourceBytesTests,
 Source_DecodeSourceBytesTests
 ) = util.test_both(DecodeSourceBytesTests, util=importlib_util)


kundi ModuleFromSpecTests:

    eleza test_no_create_module(self):
        kundi Loader:
            eleza exec_module(self, module):
                pita
        spec = self.machinery.ModuleSpec('test', Loader())
        ukijumuisha self.assertRaises(ImportError):
            module = self.util.module_kutoka_spec(spec)

    eleza test_create_module_rudishas_Tupu(self):
        kundi Loader(self.abc.Loader):
            eleza create_module(self, spec):
                rudisha Tupu
        spec = self.machinery.ModuleSpec('test', Loader())
        module = self.util.module_kutoka_spec(spec)
        self.assertIsInstance(module, types.ModuleType)
        self.assertEqual(module.__name__, spec.name)

    eleza test_create_module(self):
        name = 'already set'
        kundi CustomModule(types.ModuleType):
            pita
        kundi Loader(self.abc.Loader):
            eleza create_module(self, spec):
                module = CustomModule(spec.name)
                module.__name__ = name
                rudisha module
        spec = self.machinery.ModuleSpec('test', Loader())
        module = self.util.module_kutoka_spec(spec)
        self.assertIsInstance(module, CustomModule)
        self.assertEqual(module.__name__, name)

    eleza test___name__(self):
        spec = self.machinery.ModuleSpec('test', object())
        module = self.util.module_kutoka_spec(spec)
        self.assertEqual(module.__name__, spec.name)

    eleza test___spec__(self):
        spec = self.machinery.ModuleSpec('test', object())
        module = self.util.module_kutoka_spec(spec)
        self.assertEqual(module.__spec__, spec)

    eleza test___loader__(self):
        loader = object()
        spec = self.machinery.ModuleSpec('test', loader)
        module = self.util.module_kutoka_spec(spec)
        self.assertIs(module.__loader__, loader)

    eleza test___package__(self):
        spec = self.machinery.ModuleSpec('test.pkg', object())
        module = self.util.module_kutoka_spec(spec)
        self.assertEqual(module.__package__, spec.parent)

    eleza test___path__(self):
        spec = self.machinery.ModuleSpec('test', object(), is_package=Kweli)
        module = self.util.module_kutoka_spec(spec)
        self.assertEqual(module.__path__, spec.submodule_search_locations)

    eleza test___file__(self):
        spec = self.machinery.ModuleSpec('test', object(), origin='some/path')
        spec.has_location = Kweli
        module = self.util.module_kutoka_spec(spec)
        self.assertEqual(module.__file__, spec.origin)

    eleza test___cached__(self):
        spec = self.machinery.ModuleSpec('test', object())
        spec.cached = 'some/path'
        spec.has_location = Kweli
        module = self.util.module_kutoka_spec(spec)
        self.assertEqual(module.__cached__, spec.cached)

(Frozen_ModuleFromSpecTests,
 Source_ModuleFromSpecTests
) = util.test_both(ModuleFromSpecTests, abc=abc, machinery=machinery,
                   util=importlib_util)


kundi ModuleForLoaderTests:

    """Tests kila importlib.util.module_for_loader."""

    @classmethod
    eleza module_for_loader(cls, func):
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            rudisha cls.util.module_for_loader(func)

    eleza test_warning(self):
        # Should ashiria a PendingDeprecationWarning when used.
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('error', DeprecationWarning)
            ukijumuisha self.assertRaises(DeprecationWarning):
                func = self.util.module_for_loader(lambda x: x)

    eleza rudisha_module(self, name):
        fxn = self.module_for_loader(lambda self, module: module)
        rudisha fxn(self, name)

    eleza ashiria_exception(self, name):
        eleza to_wrap(self, module):
            ashiria ImportError
        fxn = self.module_for_loader(to_wrap)
        jaribu:
            fxn(self, name)
        tatizo ImportError:
            pita

    eleza test_new_module(self):
        # Test that when no module exists kwenye sys.modules a new module is
        # created.
        module_name = 'a.b.c'
        ukijumuisha util.uncache(module_name):
            module = self.rudisha_module(module_name)
            self.assertIn(module_name, sys.modules)
        self.assertIsInstance(module, types.ModuleType)
        self.assertEqual(module.__name__, module_name)

    eleza test_reload(self):
        # Test that a module ni reused ikiwa already kwenye sys.modules.
        kundi FakeLoader:
            eleza is_package(self, name):
                rudisha Kweli
            @self.module_for_loader
            eleza load_module(self, module):
                rudisha module
        name = 'a.b.c'
        module = types.ModuleType('a.b.c')
        module.__loader__ = 42
        module.__package__ = 42
        ukijumuisha util.uncache(name):
            sys.modules[name] = module
            loader = FakeLoader()
            rudishaed_module = loader.load_module(name)
            self.assertIs(rudishaed_module, sys.modules[name])
            self.assertEqual(module.__loader__, loader)
            self.assertEqual(module.__package__, name)

    eleza test_new_module_failure(self):
        # Test that a module ni removed kutoka sys.modules ikiwa added but an
        # exception ni ashiriad.
        name = 'a.b.c'
        ukijumuisha util.uncache(name):
            self.ashiria_exception(name)
            self.assertNotIn(name, sys.modules)

    eleza test_reload_failure(self):
        # Test that a failure on reload leaves the module in-place.
        name = 'a.b.c'
        module = types.ModuleType(name)
        ukijumuisha util.uncache(name):
            sys.modules[name] = module
            self.ashiria_exception(name)
            self.assertIs(module, sys.modules[name])

    eleza test_decorator_attrs(self):
        eleza fxn(self, module): pita
        wrapped = self.module_for_loader(fxn)
        self.assertEqual(wrapped.__name__, fxn.__name__)
        self.assertEqual(wrapped.__qualname__, fxn.__qualname__)

    eleza test_false_module(self):
        # If kila some odd reason a module ni considered false, still rudisha it
        # kutoka sys.modules.
        kundi UongoModule(types.ModuleType):
            eleza __bool__(self): rudisha Uongo

        name = 'mod'
        module = UongoModule(name)
        ukijumuisha util.uncache(name):
            self.assertUongo(module)
            sys.modules[name] = module
            given = self.rudisha_module(name)
            self.assertIs(given, module)

    eleza test_attributes_set(self):
        # __name__, __loader__, na __package__ should be set (when
        # is_package() ni defined; undefined implicitly tested elsewhere).
        kundi FakeLoader:
            eleza __init__(self, is_package):
                self._pkg = is_package
            eleza is_package(self, name):
                rudisha self._pkg
            @self.module_for_loader
            eleza load_module(self, module):
                rudisha module

        name = 'pkg.mod'
        ukijumuisha util.uncache(name):
            loader = FakeLoader(Uongo)
            module = loader.load_module(name)
            self.assertEqual(module.__name__, name)
            self.assertIs(module.__loader__, loader)
            self.assertEqual(module.__package__, 'pkg')

        name = 'pkg.sub'
        ukijumuisha util.uncache(name):
            loader = FakeLoader(Kweli)
            module = loader.load_module(name)
            self.assertEqual(module.__name__, name)
            self.assertIs(module.__loader__, loader)
            self.assertEqual(module.__package__, name)


(Frozen_ModuleForLoaderTests,
 Source_ModuleForLoaderTests
 ) = util.test_both(ModuleForLoaderTests, util=importlib_util)


kundi SetPackageTests:

    """Tests kila importlib.util.set_package."""

    eleza verify(self, module, expect):
        """Verify the module has the expected value kila __package__ after
        pitaing through set_package."""
        fxn = lambda: module
        wrapped = self.util.set_package(fxn)
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            wrapped()
        self.assertKweli(hasattr(module, '__package__'))
        self.assertEqual(expect, module.__package__)

    eleza test_top_level(self):
        # __package__ should be set to the empty string ikiwa a top-level module.
        # Implicitly tests when package ni set to Tupu.
        module = types.ModuleType('module')
        module.__package__ = Tupu
        self.verify(module, '')

    eleza test_package(self):
        # Test setting __package__ kila a package.
        module = types.ModuleType('pkg')
        module.__path__ = ['<path>']
        module.__package__ = Tupu
        self.verify(module, 'pkg')

    eleza test_submodule(self):
        # Test __package__ kila a module kwenye a package.
        module = types.ModuleType('pkg.mod')
        module.__package__ = Tupu
        self.verify(module, 'pkg')

    eleza test_setting_if_missing(self):
        # __package__ should be set ikiwa it ni missing.
        module = types.ModuleType('mod')
        ikiwa hasattr(module, '__package__'):
            delattr(module, '__package__')
        self.verify(module, '')

    eleza test_leaving_alone(self):
        # If __package__ ni set na sio Tupu then leave it alone.
        kila value kwenye (Kweli, Uongo):
            module = types.ModuleType('mod')
            module.__package__ = value
            self.verify(module, value)

    eleza test_decorator_attrs(self):
        eleza fxn(module): pita
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            wrapped = self.util.set_package(fxn)
        self.assertEqual(wrapped.__name__, fxn.__name__)
        self.assertEqual(wrapped.__qualname__, fxn.__qualname__)


(Frozen_SetPackageTests,
 Source_SetPackageTests
 ) = util.test_both(SetPackageTests, util=importlib_util)


kundi SetLoaderTests:

    """Tests importlib.util.set_loader()."""

    @property
    eleza DummyLoader(self):
        # Set DummyLoader on the kundi lazily.
        kundi DummyLoader:
            @self.util.set_loader
            eleza load_module(self, module):
                rudisha self.module
        self.__class__.DummyLoader = DummyLoader
        rudisha DummyLoader

    eleza test_no_attribute(self):
        loader = self.DummyLoader()
        loader.module = types.ModuleType('blah')
        jaribu:
            toa loader.module.__loader__
        tatizo AttributeError:
            pita
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertEqual(loader, loader.load_module('blah').__loader__)

    eleza test_attribute_is_Tupu(self):
        loader = self.DummyLoader()
        loader.module = types.ModuleType('blah')
        loader.module.__loader__ = Tupu
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertEqual(loader, loader.load_module('blah').__loader__)

    eleza test_not_reset(self):
        loader = self.DummyLoader()
        loader.module = types.ModuleType('blah')
        loader.module.__loader__ = 42
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertEqual(42, loader.load_module('blah').__loader__)


(Frozen_SetLoaderTests,
 Source_SetLoaderTests
 ) = util.test_both(SetLoaderTests, util=importlib_util)


kundi ResolveNameTests:

    """Tests importlib.util.resolve_name()."""

    eleza test_absolute(self):
        # bacon
        self.assertEqual('bacon', self.util.resolve_name('bacon', Tupu))

    eleza test_absolute_within_package(self):
        # bacon kwenye spam
        self.assertEqual('bacon', self.util.resolve_name('bacon', 'spam'))

    eleza test_no_package(self):
        # .bacon kwenye ''
        ukijumuisha self.assertRaises(ValueError):
            self.util.resolve_name('.bacon', '')

    eleza test_in_package(self):
        # .bacon kwenye spam
        self.assertEqual('spam.eggs.bacon',
                         self.util.resolve_name('.bacon', 'spam.eggs'))

    eleza test_other_package(self):
        # ..bacon kwenye spam.bacon
        self.assertEqual('spam.bacon',
                         self.util.resolve_name('..bacon', 'spam.eggs'))

    eleza test_escape(self):
        # ..bacon kwenye spam
        ukijumuisha self.assertRaises(ValueError):
            self.util.resolve_name('..bacon', 'spam')


(Frozen_ResolveNameTests,
 Source_ResolveNameTests
 ) = util.test_both(ResolveNameTests, util=importlib_util)


kundi FindSpecTests:

    kundi FakeMetaFinder:
        @staticmethod
        eleza find_spec(name, path=Tupu, target=Tupu): rudisha name, path, target

    eleza test_sys_modules(self):
        name = 'some_mod'
        ukijumuisha util.uncache(name):
            module = types.ModuleType(name)
            loader = 'a loader!'
            spec = self.machinery.ModuleSpec(name, loader)
            module.__loader__ = loader
            module.__spec__ = spec
            sys.modules[name] = module
            found = self.util.find_spec(name)
            self.assertEqual(found, spec)

    eleza test_sys_modules_without___loader__(self):
        name = 'some_mod'
        ukijumuisha util.uncache(name):
            module = types.ModuleType(name)
            toa module.__loader__
            loader = 'a loader!'
            spec = self.machinery.ModuleSpec(name, loader)
            module.__spec__ = spec
            sys.modules[name] = module
            found = self.util.find_spec(name)
            self.assertEqual(found, spec)

    eleza test_sys_modules_spec_is_Tupu(self):
        name = 'some_mod'
        ukijumuisha util.uncache(name):
            module = types.ModuleType(name)
            module.__spec__ = Tupu
            sys.modules[name] = module
            ukijumuisha self.assertRaises(ValueError):
                self.util.find_spec(name)

    eleza test_sys_modules_loader_is_Tupu(self):
        name = 'some_mod'
        ukijumuisha util.uncache(name):
            module = types.ModuleType(name)
            spec = self.machinery.ModuleSpec(name, Tupu)
            module.__spec__ = spec
            sys.modules[name] = module
            found = self.util.find_spec(name)
            self.assertEqual(found, spec)

    eleza test_sys_modules_spec_is_not_set(self):
        name = 'some_mod'
        ukijumuisha util.uncache(name):
            module = types.ModuleType(name)
            jaribu:
                toa module.__spec__
            tatizo AttributeError:
                pita
            sys.modules[name] = module
            ukijumuisha self.assertRaises(ValueError):
                self.util.find_spec(name)

    eleza test_success(self):
        name = 'some_mod'
        ukijumuisha util.uncache(name):
            ukijumuisha util.import_state(meta_path=[self.FakeMetaFinder]):
                self.assertEqual((name, Tupu, Tupu),
                                 self.util.find_spec(name))

    eleza test_nothing(self):
        # Tupu ni rudishaed upon failure to find a loader.
        self.assertIsTupu(self.util.find_spec('nevergoingtofindthismodule'))

    eleza test_find_submodule(self):
        name = 'spam'
        subname = 'ham'
        ukijumuisha util.temp_module(name, pkg=Kweli) kama pkg_dir:
            fullname, _ = util.submodule(name, subname, pkg_dir)
            spec = self.util.find_spec(fullname)
            self.assertIsNot(spec, Tupu)
            self.assertIn(name, sorted(sys.modules))
            self.assertNotIn(fullname, sorted(sys.modules))
            # Ensure successive calls behave the same.
            spec_again = self.util.find_spec(fullname)
            self.assertEqual(spec_again, spec)

    eleza test_find_submodule_parent_already_imported(self):
        name = 'spam'
        subname = 'ham'
        ukijumuisha util.temp_module(name, pkg=Kweli) kama pkg_dir:
            self.init.import_module(name)
            fullname, _ = util.submodule(name, subname, pkg_dir)
            spec = self.util.find_spec(fullname)
            self.assertIsNot(spec, Tupu)
            self.assertIn(name, sorted(sys.modules))
            self.assertNotIn(fullname, sorted(sys.modules))
            # Ensure successive calls behave the same.
            spec_again = self.util.find_spec(fullname)
            self.assertEqual(spec_again, spec)

    eleza test_find_relative_module(self):
        name = 'spam'
        subname = 'ham'
        ukijumuisha util.temp_module(name, pkg=Kweli) kama pkg_dir:
            fullname, _ = util.submodule(name, subname, pkg_dir)
            relname = '.' + subname
            spec = self.util.find_spec(relname, name)
            self.assertIsNot(spec, Tupu)
            self.assertIn(name, sorted(sys.modules))
            self.assertNotIn(fullname, sorted(sys.modules))
            # Ensure successive calls behave the same.
            spec_again = self.util.find_spec(fullname)
            self.assertEqual(spec_again, spec)

    eleza test_find_relative_module_missing_package(self):
        name = 'spam'
        subname = 'ham'
        ukijumuisha util.temp_module(name, pkg=Kweli) kama pkg_dir:
            fullname, _ = util.submodule(name, subname, pkg_dir)
            relname = '.' + subname
            ukijumuisha self.assertRaises(ValueError):
                self.util.find_spec(relname)
            self.assertNotIn(name, sorted(sys.modules))
            self.assertNotIn(fullname, sorted(sys.modules))

    eleza test_find_submodule_in_module(self):
        # ModuleNotFoundError ashiriad when a module ni specified as
        # a parent instead of a package.
        ukijumuisha self.assertRaises(ModuleNotFoundError):
            self.util.find_spec('module.name')


(Frozen_FindSpecTests,
 Source_FindSpecTests
 ) = util.test_both(FindSpecTests, init=init, util=importlib_util,
                         machinery=machinery)


kundi MagicNumberTests:

    eleza test_length(self):
        # Should be 4 bytes.
        self.assertEqual(len(self.util.MAGIC_NUMBER), 4)

    eleza test_incorporates_rn(self):
        # The magic number uses \r\n to come out wrong when splitting on lines.
        self.assertKweli(self.util.MAGIC_NUMBER.endswith(b'\r\n'))


(Frozen_MagicNumberTests,
 Source_MagicNumberTests
 ) = util.test_both(MagicNumberTests, util=importlib_util)


kundi PEP3147Tests:

    """Tests of PEP 3147-related functions: cache_kutoka_source na source_kutoka_cache."""

    tag = sys.implementation.cache_tag

    @unittest.skipIf(sys.implementation.cache_tag ni Tupu,
                     'requires sys.implementation.cache_tag sio be Tupu')
    eleza test_cache_kutoka_source(self):
        # Given the path to a .py file, rudisha the path to its PEP 3147
        # defined .pyc file (i.e. under __pycache__).
        path = os.path.join('foo', 'bar', 'baz', 'qux.py')
        expect = os.path.join('foo', 'bar', 'baz', '__pycache__',
                              'qux.{}.pyc'.format(self.tag))
        self.assertEqual(self.util.cache_kutoka_source(path, optimization=''),
                         expect)

    eleza test_cache_kutoka_source_no_cache_tag(self):
        # No cache tag means NotImplementedError.
        ukijumuisha support.swap_attr(sys.implementation, 'cache_tag', Tupu):
            ukijumuisha self.assertRaises(NotImplementedError):
                self.util.cache_kutoka_source('whatever.py')

    eleza test_cache_kutoka_source_no_dot(self):
        # Directory ukijumuisha a dot, filename without dot.
        path = os.path.join('foo.bar', 'file')
        expect = os.path.join('foo.bar', '__pycache__',
                              'file{}.pyc'.format(self.tag))
        self.assertEqual(self.util.cache_kutoka_source(path, optimization=''),
                         expect)

    eleza test_cache_kutoka_source_debug_override(self):
        # Given the path to a .py file, rudisha the path to its PEP 3147/PEP 488
        # defined .pyc file (i.e. under __pycache__).
        path = os.path.join('foo', 'bar', 'baz', 'qux.py')
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.assertEqual(self.util.cache_kutoka_source(path, Uongo),
                             self.util.cache_kutoka_source(path, optimization=1))
            self.assertEqual(self.util.cache_kutoka_source(path, Kweli),
                             self.util.cache_kutoka_source(path, optimization=''))
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('error')
            ukijumuisha self.assertRaises(DeprecationWarning):
                self.util.cache_kutoka_source(path, Uongo)
            ukijumuisha self.assertRaises(DeprecationWarning):
                self.util.cache_kutoka_source(path, Kweli)

    eleza test_cache_kutoka_source_cwd(self):
        path = 'foo.py'
        expect = os.path.join('__pycache__', 'foo.{}.pyc'.format(self.tag))
        self.assertEqual(self.util.cache_kutoka_source(path, optimization=''),
                         expect)

    eleza test_cache_kutoka_source_override(self):
        # When debug_override ni sio Tupu, it can be any true-ish ama false-ish
        # value.
        path = os.path.join('foo', 'bar', 'baz.py')
        # However ikiwa the bool-ishness can't be determined, the exception
        # propagates.
        kundi Bearish:
            eleza __bool__(self): ashiria RuntimeError
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.assertEqual(self.util.cache_kutoka_source(path, []),
                             self.util.cache_kutoka_source(path, optimization=1))
            self.assertEqual(self.util.cache_kutoka_source(path, [17]),
                             self.util.cache_kutoka_source(path, optimization=''))
            ukijumuisha self.assertRaises(RuntimeError):
                self.util.cache_kutoka_source('/foo/bar/baz.py', Bearish())


    eleza test_cache_kutoka_source_optimization_empty_string(self):
        # Setting 'optimization' to '' leads to no optimization tag (PEP 488).
        path = 'foo.py'
        expect = os.path.join('__pycache__', 'foo.{}.pyc'.format(self.tag))
        self.assertEqual(self.util.cache_kutoka_source(path, optimization=''),
                         expect)

    eleza test_cache_kutoka_source_optimization_Tupu(self):
        # Setting 'optimization' to Tupu uses the interpreter's optimization.
        # (PEP 488)
        path = 'foo.py'
        optimization_level = sys.flags.optimize
        almost_expect = os.path.join('__pycache__', 'foo.{}'.format(self.tag))
        ikiwa optimization_level == 0:
            expect = almost_expect + '.pyc'
        lasivyo optimization_level <= 2:
            expect = almost_expect + '.opt-{}.pyc'.format(optimization_level)
        isipokua:
            msg = '{!r} ni a non-standard optimization level'.format(optimization_level)
            self.skipTest(msg)
        self.assertEqual(self.util.cache_kutoka_source(path, optimization=Tupu),
                         expect)

    eleza test_cache_kutoka_source_optimization_set(self):
        # The 'optimization' parameter accepts anything that has a string repr
        # that pitaes str.alnum().
        path = 'foo.py'
        valid_characters = string.ascii_letters + string.digits
        almost_expect = os.path.join('__pycache__', 'foo.{}'.format(self.tag))
        got = self.util.cache_kutoka_source(path, optimization=valid_characters)
        # Test all valid characters are accepted.
        self.assertEqual(got,
                         almost_expect + '.opt-{}.pyc'.format(valid_characters))
        # str() should be called on argument.
        self.assertEqual(self.util.cache_kutoka_source(path, optimization=42),
                         almost_expect + '.opt-42.pyc')
        # Invalid characters ashiria ValueError.
        ukijumuisha self.assertRaises(ValueError):
            self.util.cache_kutoka_source(path, optimization='path/is/bad')

    eleza test_cache_kutoka_source_debug_override_optimization_both_set(self):
        # Can only set one of the optimization-related parameters.
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore')
            ukijumuisha self.assertRaises(TypeError):
                self.util.cache_kutoka_source('foo.py', Uongo, optimization='')

    @unittest.skipUnless(os.sep == '\\' na os.altsep == '/',
                     'test meaningful only where os.altsep ni defined')
    eleza test_sep_altsep_and_sep_cache_kutoka_source(self):
        # Windows path na PEP 3147 where sep ni right of altsep.
        self.assertEqual(
            self.util.cache_kutoka_source('\\foo\\bar\\baz/qux.py', optimization=''),
            '\\foo\\bar\\baz\\__pycache__\\qux.{}.pyc'.format(self.tag))

    @unittest.skipIf(sys.implementation.cache_tag ni Tupu,
                     'requires sys.implementation.cache_tag sio be Tupu')
    eleza test_cache_kutoka_source_path_like_arg(self):
        path = pathlib.PurePath('foo', 'bar', 'baz', 'qux.py')
        expect = os.path.join('foo', 'bar', 'baz', '__pycache__',
                              'qux.{}.pyc'.format(self.tag))
        self.assertEqual(self.util.cache_kutoka_source(path, optimization=''),
                         expect)

    @unittest.skipIf(sys.implementation.cache_tag ni Tupu,
                     'requires sys.implementation.cache_tag to sio be Tupu')
    eleza test_source_kutoka_cache(self):
        # Given the path to a PEP 3147 defined .pyc file, rudisha the path to
        # its source.  This tests the good path.
        path = os.path.join('foo', 'bar', 'baz', '__pycache__',
                            'qux.{}.pyc'.format(self.tag))
        expect = os.path.join('foo', 'bar', 'baz', 'qux.py')
        self.assertEqual(self.util.source_kutoka_cache(path), expect)

    eleza test_source_kutoka_cache_no_cache_tag(self):
        # If sys.implementation.cache_tag ni Tupu, ashiria NotImplementedError.
        path = os.path.join('blah', '__pycache__', 'whatever.pyc')
        ukijumuisha support.swap_attr(sys.implementation, 'cache_tag', Tupu):
            ukijumuisha self.assertRaises(NotImplementedError):
                self.util.source_kutoka_cache(path)

    eleza test_source_kutoka_cache_bad_path(self):
        # When the path to a pyc file ni haiko kwenye PEP 3147 format, a ValueError
        # ni ashiriad.
        self.assertRaises(
            ValueError, self.util.source_kutoka_cache, '/foo/bar/bazqux.pyc')

    eleza test_source_kutoka_cache_no_slash(self):
        # No slashes at all kwenye path -> ValueError
        self.assertRaises(
            ValueError, self.util.source_kutoka_cache, 'foo.cpython-32.pyc')

    eleza test_source_kutoka_cache_too_few_dots(self):
        # Too few dots kwenye final path component -> ValueError
        self.assertRaises(
            ValueError, self.util.source_kutoka_cache, '__pycache__/foo.pyc')

    eleza test_source_kutoka_cache_too_many_dots(self):
        ukijumuisha self.assertRaises(ValueError):
            self.util.source_kutoka_cache(
                    '__pycache__/foo.cpython-32.opt-1.foo.pyc')

    eleza test_source_kutoka_cache_not_opt(self):
        # Non-`opt-` path component -> ValueError
        self.assertRaises(
            ValueError, self.util.source_kutoka_cache,
            '__pycache__/foo.cpython-32.foo.pyc')

    eleza test_source_kutoka_cache_no__pycache__(self):
        # Another problem ukijumuisha the path -> ValueError
        self.assertRaises(
            ValueError, self.util.source_kutoka_cache,
            '/foo/bar/foo.cpython-32.foo.pyc')

    eleza test_source_kutoka_cache_optimized_bytecode(self):
        # Optimized bytecode ni sio an issue.
        path = os.path.join('__pycache__', 'foo.{}.opt-1.pyc'.format(self.tag))
        self.assertEqual(self.util.source_kutoka_cache(path), 'foo.py')

    eleza test_source_kutoka_cache_missing_optimization(self):
        # An empty optimization level ni a no-no.
        path = os.path.join('__pycache__', 'foo.{}.opt-.pyc'.format(self.tag))
        ukijumuisha self.assertRaises(ValueError):
            self.util.source_kutoka_cache(path)

    @unittest.skipIf(sys.implementation.cache_tag ni Tupu,
                     'requires sys.implementation.cache_tag to sio be Tupu')
    eleza test_source_kutoka_cache_path_like_arg(self):
        path = pathlib.PurePath('foo', 'bar', 'baz', '__pycache__',
                                'qux.{}.pyc'.format(self.tag))
        expect = os.path.join('foo', 'bar', 'baz', 'qux.py')
        self.assertEqual(self.util.source_kutoka_cache(path), expect)

    @unittest.skipIf(sys.implementation.cache_tag ni Tupu,
                     'requires sys.implementation.cache_tag to sio be Tupu')
    eleza test_cache_kutoka_source_respects_pycache_prefix(self):
        # If pycache_prefix ni set, cache_kutoka_source will rudisha a bytecode
        # path inside that directory (in a subdirectory mirroring the .py file's
        # path) rather than kwenye a __pycache__ dir next to the py file.
        pycache_prefixes = [
            os.path.join(os.path.sep, 'tmp', 'bytecode'),
            os.path.join(os.path.sep, 'tmp', '\u2603'),  # non-ASCII kwenye path!
            os.path.join(os.path.sep, 'tmp', 'trailing-slash') + os.path.sep,
        ]
        drive = ''
        ikiwa os.name == 'nt':
            drive = 'C:'
            pycache_prefixes = [
                f'{drive}{prefix}' kila prefix kwenye pycache_prefixes]
            pycache_prefixes += [r'\\?\C:\foo', r'\\localhost\c$\bar']
        kila pycache_prefix kwenye pycache_prefixes:
            ukijumuisha self.subTest(path=pycache_prefix):
                path = drive + os.path.join(
                    os.path.sep, 'foo', 'bar', 'baz', 'qux.py')
                expect = os.path.join(
                    pycache_prefix, 'foo', 'bar', 'baz',
                    'qux.{}.pyc'.format(self.tag))
                ukijumuisha util.temporary_pycache_prefix(pycache_prefix):
                    self.assertEqual(
                        self.util.cache_kutoka_source(path, optimization=''),
                        expect)

    @unittest.skipIf(sys.implementation.cache_tag ni Tupu,
                     'requires sys.implementation.cache_tag to sio be Tupu')
    eleza test_cache_kutoka_source_respects_pycache_prefix_relative(self):
        # If the .py path we are given ni relative, we will resolve to an
        # absolute path before prefixing ukijumuisha pycache_prefix, to avoid any
        # possible ambiguity.
        pycache_prefix = os.path.join(os.path.sep, 'tmp', 'bytecode')
        path = os.path.join('foo', 'bar', 'baz', 'qux.py')
        root = os.path.splitdrive(os.getcwd())[0] + os.path.sep
        expect = os.path.join(
            pycache_prefix,
            os.path.relpath(os.getcwd(), root),
            'foo', 'bar', 'baz', f'qux.{self.tag}.pyc')
        ukijumuisha util.temporary_pycache_prefix(pycache_prefix):
            self.assertEqual(
                self.util.cache_kutoka_source(path, optimization=''),
                expect)

    @unittest.skipIf(sys.implementation.cache_tag ni Tupu,
                     'requires sys.implementation.cache_tag to sio be Tupu')
    eleza test_source_kutoka_cache_inside_pycache_prefix(self):
        # If pycache_prefix ni set na the cache path we get ni inside it,
        # we rudisha an absolute path to the py file based on the remainder of
        # the path within pycache_prefix.
        pycache_prefix = os.path.join(os.path.sep, 'tmp', 'bytecode')
        path = os.path.join(pycache_prefix, 'foo', 'bar', 'baz',
                            f'qux.{self.tag}.pyc')
        expect = os.path.join(os.path.sep, 'foo', 'bar', 'baz', 'qux.py')
        ukijumuisha util.temporary_pycache_prefix(pycache_prefix):
            self.assertEqual(self.util.source_kutoka_cache(path), expect)

    @unittest.skipIf(sys.implementation.cache_tag ni Tupu,
                     'requires sys.implementation.cache_tag to sio be Tupu')
    eleza test_source_kutoka_cache_outside_pycache_prefix(self):
        # If pycache_prefix ni set but the cache path we get ni sio inside
        # it, just ignore it na handle the cache path according to the default
        # behavior.
        pycache_prefix = os.path.join(os.path.sep, 'tmp', 'bytecode')
        path = os.path.join('foo', 'bar', 'baz', '__pycache__',
                            f'qux.{self.tag}.pyc')
        expect = os.path.join('foo', 'bar', 'baz', 'qux.py')
        ukijumuisha util.temporary_pycache_prefix(pycache_prefix):
            self.assertEqual(self.util.source_kutoka_cache(path), expect)


(Frozen_PEP3147Tests,
 Source_PEP3147Tests
 ) = util.test_both(PEP3147Tests, util=importlib_util)


kundi MagicNumberTests(unittest.TestCase):
    """
    Test release compatibility issues relating to importlib
    """
    @unittest.skipUnless(
        sys.version_info.releaselevel kwenye ('candidate', 'final'),
        'only applies to candidate ama final python release levels'
    )
    eleza test_magic_number(self):
        """
        Each python minor release should generally have a MAGIC_NUMBER
        that does sio change once the release reaches candidate status.

        Once a release reaches candidate status, the value of the constant
        EXPECTED_MAGIC_NUMBER kwenye this test should be changed.
        This test will then check that the actual MAGIC_NUMBER matches
        the expected value kila the release.

        In exceptional cases, it may be required to change the MAGIC_NUMBER
        kila a maintenance release. In this case the change should be
        discussed kwenye python-dev. If a change ni required, community
        stakeholders such kama OS package maintainers must be notified
        kwenye advance. Such exceptional releases will then require an
        adjustment to this test case.
        """
        EXPECTED_MAGIC_NUMBER = 3413
        actual = int.kutoka_bytes(importlib.util.MAGIC_NUMBER[:2], 'little')

        msg = (
            "To avoid komaing backwards compatibility ukijumuisha cached bytecode "
            "files that can't be automatically regenerated by the current "
            "user, candidate na final releases require the current  "
            "importlib.util.MAGIC_NUMBER to match the expected "
            "magic number kwenye this test. Set the expected "
            "magic number kwenye this test to the current MAGIC_NUMBER to "
            "endelea ukijumuisha the release.\n\n"
            "Changing the MAGIC_NUMBER kila a maintenance release "
            "requires discussion kwenye python-dev na notification of "
            "community stakeholders."
        )
        self.assertEqual(EXPECTED_MAGIC_NUMBER, actual, msg)


ikiwa __name__ == '__main__':
    unittest.main()
