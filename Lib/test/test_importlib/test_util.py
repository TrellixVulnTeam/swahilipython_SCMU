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
                pass
        spec = self.machinery.ModuleSpec('test', Loader())
        with self.assertRaises(ImportError):
            module = self.util.module_kutoka_spec(spec)

    eleza test_create_module_returns_None(self):
        kundi Loader(self.abc.Loader):
            eleza create_module(self, spec):
                rudisha None
        spec = self.machinery.ModuleSpec('test', Loader())
        module = self.util.module_kutoka_spec(spec)
        self.assertIsInstance(module, types.ModuleType)
        self.assertEqual(module.__name__, spec.name)

    eleza test_create_module(self):
        name = 'already set'
        kundi CustomModule(types.ModuleType):
            pass
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
        spec = self.machinery.ModuleSpec('test', object(), is_package=True)
        module = self.util.module_kutoka_spec(spec)
        self.assertEqual(module.__path__, spec.submodule_search_locations)

    eleza test___file__(self):
        spec = self.machinery.ModuleSpec('test', object(), origin='some/path')
        spec.has_location = True
        module = self.util.module_kutoka_spec(spec)
        self.assertEqual(module.__file__, spec.origin)

    eleza test___cached__(self):
        spec = self.machinery.ModuleSpec('test', object())
        spec.cached = 'some/path'
        spec.has_location = True
        module = self.util.module_kutoka_spec(spec)
        self.assertEqual(module.__cached__, spec.cached)

(Frozen_ModuleFromSpecTests,
 Source_ModuleFromSpecTests
) = util.test_both(ModuleFromSpecTests, abc=abc, machinery=machinery,
                   util=importlib_util)


kundi ModuleForLoaderTests:

    """Tests for importlib.util.module_for_loader."""

    @classmethod
    eleza module_for_loader(cls, func):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            rudisha cls.util.module_for_loader(func)

    eleza test_warning(self):
        # Should raise a PendingDeprecationWarning when used.
        with warnings.catch_warnings():
            warnings.simplefilter('error', DeprecationWarning)
            with self.assertRaises(DeprecationWarning):
                func = self.util.module_for_loader(lambda x: x)

    eleza return_module(self, name):
        fxn = self.module_for_loader(lambda self, module: module)
        rudisha fxn(self, name)

    eleza raise_exception(self, name):
        eleza to_wrap(self, module):
            raise ImportError
        fxn = self.module_for_loader(to_wrap)
        try:
            fxn(self, name)
        except ImportError:
            pass

    eleza test_new_module(self):
        # Test that when no module exists in sys.modules a new module is
        # created.
        module_name = 'a.b.c'
        with util.uncache(module_name):
            module = self.return_module(module_name)
            self.assertIn(module_name, sys.modules)
        self.assertIsInstance(module, types.ModuleType)
        self.assertEqual(module.__name__, module_name)

    eleza test_reload(self):
        # Test that a module is reused ikiwa already in sys.modules.
        kundi FakeLoader:
            eleza is_package(self, name):
                rudisha True
            @self.module_for_loader
            eleza load_module(self, module):
                rudisha module
        name = 'a.b.c'
        module = types.ModuleType('a.b.c')
        module.__loader__ = 42
        module.__package__ = 42
        with util.uncache(name):
            sys.modules[name] = module
            loader = FakeLoader()
            returned_module = loader.load_module(name)
            self.assertIs(returned_module, sys.modules[name])
            self.assertEqual(module.__loader__, loader)
            self.assertEqual(module.__package__, name)

    eleza test_new_module_failure(self):
        # Test that a module is removed kutoka sys.modules ikiwa added but an
        # exception is raised.
        name = 'a.b.c'
        with util.uncache(name):
            self.raise_exception(name)
            self.assertNotIn(name, sys.modules)

    eleza test_reload_failure(self):
        # Test that a failure on reload leaves the module in-place.
        name = 'a.b.c'
        module = types.ModuleType(name)
        with util.uncache(name):
            sys.modules[name] = module
            self.raise_exception(name)
            self.assertIs(module, sys.modules[name])

    eleza test_decorator_attrs(self):
        eleza fxn(self, module): pass
        wrapped = self.module_for_loader(fxn)
        self.assertEqual(wrapped.__name__, fxn.__name__)
        self.assertEqual(wrapped.__qualname__, fxn.__qualname__)

    eleza test_false_module(self):
        # If for some odd reason a module is considered false, still rudisha it
        # kutoka sys.modules.
        kundi FalseModule(types.ModuleType):
            eleza __bool__(self): rudisha False

        name = 'mod'
        module = FalseModule(name)
        with util.uncache(name):
            self.assertFalse(module)
            sys.modules[name] = module
            given = self.return_module(name)
            self.assertIs(given, module)

    eleza test_attributes_set(self):
        # __name__, __loader__, and __package__ should be set (when
        # is_package() is defined; undefined implicitly tested elsewhere).
        kundi FakeLoader:
            eleza __init__(self, is_package):
                self._pkg = is_package
            eleza is_package(self, name):
                rudisha self._pkg
            @self.module_for_loader
            eleza load_module(self, module):
                rudisha module

        name = 'pkg.mod'
        with util.uncache(name):
            loader = FakeLoader(False)
            module = loader.load_module(name)
            self.assertEqual(module.__name__, name)
            self.assertIs(module.__loader__, loader)
            self.assertEqual(module.__package__, 'pkg')

        name = 'pkg.sub'
        with util.uncache(name):
            loader = FakeLoader(True)
            module = loader.load_module(name)
            self.assertEqual(module.__name__, name)
            self.assertIs(module.__loader__, loader)
            self.assertEqual(module.__package__, name)


(Frozen_ModuleForLoaderTests,
 Source_ModuleForLoaderTests
 ) = util.test_both(ModuleForLoaderTests, util=importlib_util)


kundi SetPackageTests:

    """Tests for importlib.util.set_package."""

    eleza verify(self, module, expect):
        """Verify the module has the expected value for __package__ after
        passing through set_package."""
        fxn = lambda: module
        wrapped = self.util.set_package(fxn)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            wrapped()
        self.assertTrue(hasattr(module, '__package__'))
        self.assertEqual(expect, module.__package__)

    eleza test_top_level(self):
        # __package__ should be set to the empty string ikiwa a top-level module.
        # Implicitly tests when package is set to None.
        module = types.ModuleType('module')
        module.__package__ = None
        self.verify(module, '')

    eleza test_package(self):
        # Test setting __package__ for a package.
        module = types.ModuleType('pkg')
        module.__path__ = ['<path>']
        module.__package__ = None
        self.verify(module, 'pkg')

    eleza test_submodule(self):
        # Test __package__ for a module in a package.
        module = types.ModuleType('pkg.mod')
        module.__package__ = None
        self.verify(module, 'pkg')

    eleza test_setting_if_missing(self):
        # __package__ should be set ikiwa it is missing.
        module = types.ModuleType('mod')
        ikiwa hasattr(module, '__package__'):
            delattr(module, '__package__')
        self.verify(module, '')

    eleza test_leaving_alone(self):
        # If __package__ is set and not None then leave it alone.
        for value in (True, False):
            module = types.ModuleType('mod')
            module.__package__ = value
            self.verify(module, value)

    eleza test_decorator_attrs(self):
        eleza fxn(module): pass
        with warnings.catch_warnings():
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
        try:
            del loader.module.__loader__
        except AttributeError:
            pass
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertEqual(loader, loader.load_module('blah').__loader__)

    eleza test_attribute_is_None(self):
        loader = self.DummyLoader()
        loader.module = types.ModuleType('blah')
        loader.module.__loader__ = None
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertEqual(loader, loader.load_module('blah').__loader__)

    eleza test_not_reset(self):
        loader = self.DummyLoader()
        loader.module = types.ModuleType('blah')
        loader.module.__loader__ = 42
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertEqual(42, loader.load_module('blah').__loader__)


(Frozen_SetLoaderTests,
 Source_SetLoaderTests
 ) = util.test_both(SetLoaderTests, util=importlib_util)


kundi ResolveNameTests:

    """Tests importlib.util.resolve_name()."""

    eleza test_absolute(self):
        # bacon
        self.assertEqual('bacon', self.util.resolve_name('bacon', None))

    eleza test_absolute_within_package(self):
        # bacon in spam
        self.assertEqual('bacon', self.util.resolve_name('bacon', 'spam'))

    eleza test_no_package(self):
        # .bacon in ''
        with self.assertRaises(ValueError):
            self.util.resolve_name('.bacon', '')

    eleza test_in_package(self):
        # .bacon in spam
        self.assertEqual('spam.eggs.bacon',
                         self.util.resolve_name('.bacon', 'spam.eggs'))

    eleza test_other_package(self):
        # ..bacon in spam.bacon
        self.assertEqual('spam.bacon',
                         self.util.resolve_name('..bacon', 'spam.eggs'))

    eleza test_escape(self):
        # ..bacon in spam
        with self.assertRaises(ValueError):
            self.util.resolve_name('..bacon', 'spam')


(Frozen_ResolveNameTests,
 Source_ResolveNameTests
 ) = util.test_both(ResolveNameTests, util=importlib_util)


kundi FindSpecTests:

    kundi FakeMetaFinder:
        @staticmethod
        eleza find_spec(name, path=None, target=None): rudisha name, path, target

    eleza test_sys_modules(self):
        name = 'some_mod'
        with util.uncache(name):
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
        with util.uncache(name):
            module = types.ModuleType(name)
            del module.__loader__
            loader = 'a loader!'
            spec = self.machinery.ModuleSpec(name, loader)
            module.__spec__ = spec
            sys.modules[name] = module
            found = self.util.find_spec(name)
            self.assertEqual(found, spec)

    eleza test_sys_modules_spec_is_None(self):
        name = 'some_mod'
        with util.uncache(name):
            module = types.ModuleType(name)
            module.__spec__ = None
            sys.modules[name] = module
            with self.assertRaises(ValueError):
                self.util.find_spec(name)

    eleza test_sys_modules_loader_is_None(self):
        name = 'some_mod'
        with util.uncache(name):
            module = types.ModuleType(name)
            spec = self.machinery.ModuleSpec(name, None)
            module.__spec__ = spec
            sys.modules[name] = module
            found = self.util.find_spec(name)
            self.assertEqual(found, spec)

    eleza test_sys_modules_spec_is_not_set(self):
        name = 'some_mod'
        with util.uncache(name):
            module = types.ModuleType(name)
            try:
                del module.__spec__
            except AttributeError:
                pass
            sys.modules[name] = module
            with self.assertRaises(ValueError):
                self.util.find_spec(name)

    eleza test_success(self):
        name = 'some_mod'
        with util.uncache(name):
            with util.import_state(meta_path=[self.FakeMetaFinder]):
                self.assertEqual((name, None, None),
                                 self.util.find_spec(name))

    eleza test_nothing(self):
        # None is returned upon failure to find a loader.
        self.assertIsNone(self.util.find_spec('nevergoingtofindthismodule'))

    eleza test_find_submodule(self):
        name = 'spam'
        subname = 'ham'
        with util.temp_module(name, pkg=True) as pkg_dir:
            fullname, _ = util.submodule(name, subname, pkg_dir)
            spec = self.util.find_spec(fullname)
            self.assertIsNot(spec, None)
            self.assertIn(name, sorted(sys.modules))
            self.assertNotIn(fullname, sorted(sys.modules))
            # Ensure successive calls behave the same.
            spec_again = self.util.find_spec(fullname)
            self.assertEqual(spec_again, spec)

    eleza test_find_submodule_parent_already_imported(self):
        name = 'spam'
        subname = 'ham'
        with util.temp_module(name, pkg=True) as pkg_dir:
            self.init.import_module(name)
            fullname, _ = util.submodule(name, subname, pkg_dir)
            spec = self.util.find_spec(fullname)
            self.assertIsNot(spec, None)
            self.assertIn(name, sorted(sys.modules))
            self.assertNotIn(fullname, sorted(sys.modules))
            # Ensure successive calls behave the same.
            spec_again = self.util.find_spec(fullname)
            self.assertEqual(spec_again, spec)

    eleza test_find_relative_module(self):
        name = 'spam'
        subname = 'ham'
        with util.temp_module(name, pkg=True) as pkg_dir:
            fullname, _ = util.submodule(name, subname, pkg_dir)
            relname = '.' + subname
            spec = self.util.find_spec(relname, name)
            self.assertIsNot(spec, None)
            self.assertIn(name, sorted(sys.modules))
            self.assertNotIn(fullname, sorted(sys.modules))
            # Ensure successive calls behave the same.
            spec_again = self.util.find_spec(fullname)
            self.assertEqual(spec_again, spec)

    eleza test_find_relative_module_missing_package(self):
        name = 'spam'
        subname = 'ham'
        with util.temp_module(name, pkg=True) as pkg_dir:
            fullname, _ = util.submodule(name, subname, pkg_dir)
            relname = '.' + subname
            with self.assertRaises(ValueError):
                self.util.find_spec(relname)
            self.assertNotIn(name, sorted(sys.modules))
            self.assertNotIn(fullname, sorted(sys.modules))

    eleza test_find_submodule_in_module(self):
        # ModuleNotFoundError raised when a module is specified as
        # a parent instead of a package.
        with self.assertRaises(ModuleNotFoundError):
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
        self.assertTrue(self.util.MAGIC_NUMBER.endswith(b'\r\n'))


(Frozen_MagicNumberTests,
 Source_MagicNumberTests
 ) = util.test_both(MagicNumberTests, util=importlib_util)


kundi PEP3147Tests:

    """Tests of PEP 3147-related functions: cache_kutoka_source and source_kutoka_cache."""

    tag = sys.implementation.cache_tag

    @unittest.skipIf(sys.implementation.cache_tag is None,
                     'requires sys.implementation.cache_tag not be None')
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
        with support.swap_attr(sys.implementation, 'cache_tag', None):
            with self.assertRaises(NotImplementedError):
                self.util.cache_kutoka_source('whatever.py')

    eleza test_cache_kutoka_source_no_dot(self):
        # Directory with a dot, filename without dot.
        path = os.path.join('foo.bar', 'file')
        expect = os.path.join('foo.bar', '__pycache__',
                              'file{}.pyc'.format(self.tag))
        self.assertEqual(self.util.cache_kutoka_source(path, optimization=''),
                         expect)

    eleza test_cache_kutoka_source_debug_override(self):
        # Given the path to a .py file, rudisha the path to its PEP 3147/PEP 488
        # defined .pyc file (i.e. under __pycache__).
        path = os.path.join('foo', 'bar', 'baz', 'qux.py')
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.assertEqual(self.util.cache_kutoka_source(path, False),
                             self.util.cache_kutoka_source(path, optimization=1))
            self.assertEqual(self.util.cache_kutoka_source(path, True),
                             self.util.cache_kutoka_source(path, optimization=''))
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            with self.assertRaises(DeprecationWarning):
                self.util.cache_kutoka_source(path, False)
            with self.assertRaises(DeprecationWarning):
                self.util.cache_kutoka_source(path, True)

    eleza test_cache_kutoka_source_cwd(self):
        path = 'foo.py'
        expect = os.path.join('__pycache__', 'foo.{}.pyc'.format(self.tag))
        self.assertEqual(self.util.cache_kutoka_source(path, optimization=''),
                         expect)

    eleza test_cache_kutoka_source_override(self):
        # When debug_override is not None, it can be any true-ish or false-ish
        # value.
        path = os.path.join('foo', 'bar', 'baz.py')
        # However ikiwa the bool-ishness can't be determined, the exception
        # propagates.
        kundi Bearish:
            eleza __bool__(self): raise RuntimeError
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.assertEqual(self.util.cache_kutoka_source(path, []),
                             self.util.cache_kutoka_source(path, optimization=1))
            self.assertEqual(self.util.cache_kutoka_source(path, [17]),
                             self.util.cache_kutoka_source(path, optimization=''))
            with self.assertRaises(RuntimeError):
                self.util.cache_kutoka_source('/foo/bar/baz.py', Bearish())


    eleza test_cache_kutoka_source_optimization_empty_string(self):
        # Setting 'optimization' to '' leads to no optimization tag (PEP 488).
        path = 'foo.py'
        expect = os.path.join('__pycache__', 'foo.{}.pyc'.format(self.tag))
        self.assertEqual(self.util.cache_kutoka_source(path, optimization=''),
                         expect)

    eleza test_cache_kutoka_source_optimization_None(self):
        # Setting 'optimization' to None uses the interpreter's optimization.
        # (PEP 488)
        path = 'foo.py'
        optimization_level = sys.flags.optimize
        almost_expect = os.path.join('__pycache__', 'foo.{}'.format(self.tag))
        ikiwa optimization_level == 0:
            expect = almost_expect + '.pyc'
        elikiwa optimization_level <= 2:
            expect = almost_expect + '.opt-{}.pyc'.format(optimization_level)
        else:
            msg = '{!r} is a non-standard optimization level'.format(optimization_level)
            self.skipTest(msg)
        self.assertEqual(self.util.cache_kutoka_source(path, optimization=None),
                         expect)

    eleza test_cache_kutoka_source_optimization_set(self):
        # The 'optimization' parameter accepts anything that has a string repr
        # that passes str.alnum().
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
        # Invalid characters raise ValueError.
        with self.assertRaises(ValueError):
            self.util.cache_kutoka_source(path, optimization='path/is/bad')

    eleza test_cache_kutoka_source_debug_override_optimization_both_set(self):
        # Can only set one of the optimization-related parameters.
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            with self.assertRaises(TypeError):
                self.util.cache_kutoka_source('foo.py', False, optimization='')

    @unittest.skipUnless(os.sep == '\\' and os.altsep == '/',
                     'test meaningful only where os.altsep is defined')
    eleza test_sep_altsep_and_sep_cache_kutoka_source(self):
        # Windows path and PEP 3147 where sep is right of altsep.
        self.assertEqual(
            self.util.cache_kutoka_source('\\foo\\bar\\baz/qux.py', optimization=''),
            '\\foo\\bar\\baz\\__pycache__\\qux.{}.pyc'.format(self.tag))

    @unittest.skipIf(sys.implementation.cache_tag is None,
                     'requires sys.implementation.cache_tag not be None')
    eleza test_cache_kutoka_source_path_like_arg(self):
        path = pathlib.PurePath('foo', 'bar', 'baz', 'qux.py')
        expect = os.path.join('foo', 'bar', 'baz', '__pycache__',
                              'qux.{}.pyc'.format(self.tag))
        self.assertEqual(self.util.cache_kutoka_source(path, optimization=''),
                         expect)

    @unittest.skipIf(sys.implementation.cache_tag is None,
                     'requires sys.implementation.cache_tag to not be None')
    eleza test_source_kutoka_cache(self):
        # Given the path to a PEP 3147 defined .pyc file, rudisha the path to
        # its source.  This tests the good path.
        path = os.path.join('foo', 'bar', 'baz', '__pycache__',
                            'qux.{}.pyc'.format(self.tag))
        expect = os.path.join('foo', 'bar', 'baz', 'qux.py')
        self.assertEqual(self.util.source_kutoka_cache(path), expect)

    eleza test_source_kutoka_cache_no_cache_tag(self):
        # If sys.implementation.cache_tag is None, raise NotImplementedError.
        path = os.path.join('blah', '__pycache__', 'whatever.pyc')
        with support.swap_attr(sys.implementation, 'cache_tag', None):
            with self.assertRaises(NotImplementedError):
                self.util.source_kutoka_cache(path)

    eleza test_source_kutoka_cache_bad_path(self):
        # When the path to a pyc file is not in PEP 3147 format, a ValueError
        # is raised.
        self.assertRaises(
            ValueError, self.util.source_kutoka_cache, '/foo/bar/bazqux.pyc')

    eleza test_source_kutoka_cache_no_slash(self):
        # No slashes at all in path -> ValueError
        self.assertRaises(
            ValueError, self.util.source_kutoka_cache, 'foo.cpython-32.pyc')

    eleza test_source_kutoka_cache_too_few_dots(self):
        # Too few dots in final path component -> ValueError
        self.assertRaises(
            ValueError, self.util.source_kutoka_cache, '__pycache__/foo.pyc')

    eleza test_source_kutoka_cache_too_many_dots(self):
        with self.assertRaises(ValueError):
            self.util.source_kutoka_cache(
                    '__pycache__/foo.cpython-32.opt-1.foo.pyc')

    eleza test_source_kutoka_cache_not_opt(self):
        # Non-`opt-` path component -> ValueError
        self.assertRaises(
            ValueError, self.util.source_kutoka_cache,
            '__pycache__/foo.cpython-32.foo.pyc')

    eleza test_source_kutoka_cache_no__pycache__(self):
        # Another problem with the path -> ValueError
        self.assertRaises(
            ValueError, self.util.source_kutoka_cache,
            '/foo/bar/foo.cpython-32.foo.pyc')

    eleza test_source_kutoka_cache_optimized_bytecode(self):
        # Optimized bytecode is not an issue.
        path = os.path.join('__pycache__', 'foo.{}.opt-1.pyc'.format(self.tag))
        self.assertEqual(self.util.source_kutoka_cache(path), 'foo.py')

    eleza test_source_kutoka_cache_missing_optimization(self):
        # An empty optimization level is a no-no.
        path = os.path.join('__pycache__', 'foo.{}.opt-.pyc'.format(self.tag))
        with self.assertRaises(ValueError):
            self.util.source_kutoka_cache(path)

    @unittest.skipIf(sys.implementation.cache_tag is None,
                     'requires sys.implementation.cache_tag to not be None')
    eleza test_source_kutoka_cache_path_like_arg(self):
        path = pathlib.PurePath('foo', 'bar', 'baz', '__pycache__',
                                'qux.{}.pyc'.format(self.tag))
        expect = os.path.join('foo', 'bar', 'baz', 'qux.py')
        self.assertEqual(self.util.source_kutoka_cache(path), expect)

    @unittest.skipIf(sys.implementation.cache_tag is None,
                     'requires sys.implementation.cache_tag to not be None')
    eleza test_cache_kutoka_source_respects_pycache_prefix(self):
        # If pycache_prefix is set, cache_kutoka_source will rudisha a bytecode
        # path inside that directory (in a subdirectory mirroring the .py file's
        # path) rather than in a __pycache__ dir next to the py file.
        pycache_prefixes = [
            os.path.join(os.path.sep, 'tmp', 'bytecode'),
            os.path.join(os.path.sep, 'tmp', '\u2603'),  # non-ASCII in path!
            os.path.join(os.path.sep, 'tmp', 'trailing-slash') + os.path.sep,
        ]
        drive = ''
        ikiwa os.name == 'nt':
            drive = 'C:'
            pycache_prefixes = [
                f'{drive}{prefix}' for prefix in pycache_prefixes]
            pycache_prefixes += [r'\\?\C:\foo', r'\\localhost\c$\bar']
        for pycache_prefix in pycache_prefixes:
            with self.subTest(path=pycache_prefix):
                path = drive + os.path.join(
                    os.path.sep, 'foo', 'bar', 'baz', 'qux.py')
                expect = os.path.join(
                    pycache_prefix, 'foo', 'bar', 'baz',
                    'qux.{}.pyc'.format(self.tag))
                with util.temporary_pycache_prefix(pycache_prefix):
                    self.assertEqual(
                        self.util.cache_kutoka_source(path, optimization=''),
                        expect)

    @unittest.skipIf(sys.implementation.cache_tag is None,
                     'requires sys.implementation.cache_tag to not be None')
    eleza test_cache_kutoka_source_respects_pycache_prefix_relative(self):
        # If the .py path we are given is relative, we will resolve to an
        # absolute path before prefixing with pycache_prefix, to avoid any
        # possible ambiguity.
        pycache_prefix = os.path.join(os.path.sep, 'tmp', 'bytecode')
        path = os.path.join('foo', 'bar', 'baz', 'qux.py')
        root = os.path.splitdrive(os.getcwd())[0] + os.path.sep
        expect = os.path.join(
            pycache_prefix,
            os.path.relpath(os.getcwd(), root),
            'foo', 'bar', 'baz', f'qux.{self.tag}.pyc')
        with util.temporary_pycache_prefix(pycache_prefix):
            self.assertEqual(
                self.util.cache_kutoka_source(path, optimization=''),
                expect)

    @unittest.skipIf(sys.implementation.cache_tag is None,
                     'requires sys.implementation.cache_tag to not be None')
    eleza test_source_kutoka_cache_inside_pycache_prefix(self):
        # If pycache_prefix is set and the cache path we get is inside it,
        # we rudisha an absolute path to the py file based on the remainder of
        # the path within pycache_prefix.
        pycache_prefix = os.path.join(os.path.sep, 'tmp', 'bytecode')
        path = os.path.join(pycache_prefix, 'foo', 'bar', 'baz',
                            f'qux.{self.tag}.pyc')
        expect = os.path.join(os.path.sep, 'foo', 'bar', 'baz', 'qux.py')
        with util.temporary_pycache_prefix(pycache_prefix):
            self.assertEqual(self.util.source_kutoka_cache(path), expect)

    @unittest.skipIf(sys.implementation.cache_tag is None,
                     'requires sys.implementation.cache_tag to not be None')
    eleza test_source_kutoka_cache_outside_pycache_prefix(self):
        # If pycache_prefix is set but the cache path we get is not inside
        # it, just ignore it and handle the cache path according to the default
        # behavior.
        pycache_prefix = os.path.join(os.path.sep, 'tmp', 'bytecode')
        path = os.path.join('foo', 'bar', 'baz', '__pycache__',
                            f'qux.{self.tag}.pyc')
        expect = os.path.join('foo', 'bar', 'baz', 'qux.py')
        with util.temporary_pycache_prefix(pycache_prefix):
            self.assertEqual(self.util.source_kutoka_cache(path), expect)


(Frozen_PEP3147Tests,
 Source_PEP3147Tests
 ) = util.test_both(PEP3147Tests, util=importlib_util)


kundi MagicNumberTests(unittest.TestCase):
    """
    Test release compatibility issues relating to importlib
    """
    @unittest.skipUnless(
        sys.version_info.releaselevel in ('candidate', 'final'),
        'only applies to candidate or final python release levels'
    )
    eleza test_magic_number(self):
        """
        Each python minor release should generally have a MAGIC_NUMBER
        that does not change once the release reaches candidate status.

        Once a release reaches candidate status, the value of the constant
        EXPECTED_MAGIC_NUMBER in this test should be changed.
        This test will then check that the actual MAGIC_NUMBER matches
        the expected value for the release.

        In exceptional cases, it may be required to change the MAGIC_NUMBER
        for a maintenance release. In this case the change should be
        discussed in python-dev. If a change is required, community
        stakeholders such as OS package maintainers must be notified
        in advance. Such exceptional releases will then require an
        adjustment to this test case.
        """
        EXPECTED_MAGIC_NUMBER = 3413
        actual = int.kutoka_bytes(importlib.util.MAGIC_NUMBER[:2], 'little')

        msg = (
            "To avoid breaking backwards compatibility with cached bytecode "
            "files that can't be automatically regenerated by the current "
            "user, candidate and final releases require the current  "
            "importlib.util.MAGIC_NUMBER to match the expected "
            "magic number in this test. Set the expected "
            "magic number in this test to the current MAGIC_NUMBER to "
            "continue with the release.\n\n"
            "Changing the MAGIC_NUMBER for a maintenance release "
            "requires discussion in python-dev and notification of "
            "community stakeholders."
        )
        self.assertEqual(EXPECTED_MAGIC_NUMBER, actual, msg)


ikiwa __name__ == '__main__':
    unittest.main()
