agiza abc
agiza builtins
agiza contextlib
agiza errno
agiza functools
agiza importlib
kutoka importlib agiza machinery, util, invalidate_caches
kutoka importlib.abc agiza ResourceReader
agiza io
agiza os
agiza os.path
kutoka pathlib agiza Path, PurePath
kutoka test agiza support
agiza unittest
agiza sys
agiza tempfile
agiza types

kutoka . agiza data01
kutoka . agiza zipdata01


BUILTINS = types.SimpleNamespace()
BUILTINS.good_name = Tupu
BUILTINS.bad_name = Tupu
ikiwa 'errno' kwenye sys.builtin_module_names:
    BUILTINS.good_name = 'errno'
ikiwa 'importlib' sio kwenye sys.builtin_module_names:
    BUILTINS.bad_name = 'importlib'

EXTENSIONS = types.SimpleNamespace()
EXTENSIONS.path = Tupu
EXTENSIONS.ext = Tupu
EXTENSIONS.filename = Tupu
EXTENSIONS.file_path = Tupu
EXTENSIONS.name = '_testcapi'

eleza _extension_details():
    global EXTENSIONS
    kila path kwenye sys.path:
        kila ext kwenye machinery.EXTENSION_SUFFIXES:
            filename = EXTENSIONS.name + ext
            file_path = os.path.join(path, filename)
            ikiwa os.path.exists(file_path):
                EXTENSIONS.path = path
                EXTENSIONS.ext = ext
                EXTENSIONS.filename = filename
                EXTENSIONS.file_path = file_path
                return

_extension_details()


eleza import_importlib(module_name):
    """Import a module kutoka importlib both w/ na w/o _frozen_importlib."""
    fresh = ('importlib',) ikiwa '.' kwenye module_name isipokua ()
    frozen = support.import_fresh_module(module_name)
    source = support.import_fresh_module(module_name, fresh=fresh,
                                         blocked=('_frozen_importlib', '_frozen_importlib_external'))
    rudisha {'Frozen': frozen, 'Source': source}


eleza specialize_class(cls, kind, base=Tupu, **kwargs):
    # XXX Support passing kwenye submodule names--load (and cache) them?
    # That would clean up the test modules a bit more.
    ikiwa base ni Tupu:
        base = unittest.TestCase
    elikiwa sio isinstance(base, type):
        base = base[kind]
    name = '{}_{}'.format(kind, cls.__name__)
    bases = (cls, base)
    specialized = types.new_class(name, bases)
    specialized.__module__ = cls.__module__
    specialized._NAME = cls.__name__
    specialized._KIND = kind
    kila attr, values kwenye kwargs.items():
        value = values[kind]
        setattr(specialized, attr, value)
    rudisha specialized


eleza split_frozen(cls, base=Tupu, **kwargs):
    frozen = specialize_class(cls, 'Frozen', base, **kwargs)
    source = specialize_class(cls, 'Source', base, **kwargs)
    rudisha frozen, source


eleza test_both(test_class, base=Tupu, **kwargs):
    rudisha split_frozen(test_class, base, **kwargs)


CASE_INSENSITIVE_FS = Kweli
# Windows ni the only OS that ni *always* case-insensitive
# (OS X *can* be case-sensitive).
ikiwa sys.platform sio kwenye ('win32', 'cygwin'):
    changed_name = __file__.upper()
    ikiwa changed_name == __file__:
        changed_name = __file__.lower()
    ikiwa sio os.path.exists(changed_name):
        CASE_INSENSITIVE_FS = Uongo

source_importlib = import_importlib('importlib')['Source']
__import__ = {'Frozen': staticmethod(builtins.__import__),
              'Source': staticmethod(source_importlib.__import__)}


eleza case_insensitive_tests(test):
    """Class decorator that nullifies tests requiring a case-insensitive
    file system."""
    rudisha unittest.skipIf(not CASE_INSENSITIVE_FS,
                            "requires a case-insensitive filesystem")(test)


eleza submodule(parent, name, pkg_dir, content=''):
    path = os.path.join(pkg_dir, name + '.py')
    ukijumuisha open(path, 'w') as subfile:
        subfile.write(content)
    rudisha '{}.{}'.format(parent, name), path


@contextlib.contextmanager
eleza uncache(*names):
    """Uncache a module kutoka sys.modules.

    A basic sanity check ni performed to prevent uncaching modules that either
    cannot/shouldn't be uncached.

    """
    kila name kwenye names:
        ikiwa name kwenye ('sys', 'marshal', 'imp'):
             ashiria ValueError(
                "cannot uncache {0}".format(name))
        jaribu:
            toa sys.modules[name]
        except KeyError:
            pass
    jaribu:
        yield
    mwishowe:
        kila name kwenye names:
            jaribu:
                toa sys.modules[name]
            except KeyError:
                pass


@contextlib.contextmanager
eleza temp_module(name, content='', *, pkg=Uongo):
    conflicts = [n kila n kwenye sys.modules ikiwa n.partition('.')[0] == name]
    ukijumuisha support.temp_cwd(Tupu) as cwd:
        ukijumuisha uncache(name, *conflicts):
            ukijumuisha support.DirsOnSysPath(cwd):
                invalidate_caches()

                location = os.path.join(cwd, name)
                ikiwa pkg:
                    modpath = os.path.join(location, '__init__.py')
                    os.mkdir(name)
                isipokua:
                    modpath = location + '.py'
                    ikiwa content ni Tupu:
                        # Make sure the module file gets created.
                        content = ''
                ikiwa content ni sio Tupu:
                    # sio a namespace package
                    ukijumuisha open(modpath, 'w') as modfile:
                        modfile.write(content)
                tuma location


@contextlib.contextmanager
eleza import_state(**kwargs):
    """Context manager to manage the various importers na stored state kwenye the
    sys module.

    The 'modules' attribute ni sio supported as the interpreter state stores a
    pointer to the dict that the interpreter uses internally;
    reassigning to sys.modules does sio have the desired effect.

    """
    originals = {}
    jaribu:
        kila attr, default kwenye (('meta_path', []), ('path', []),
                              ('path_hooks', []),
                              ('path_importer_cache', {})):
            originals[attr] = getattr(sys, attr)
            ikiwa attr kwenye kwargs:
                new_value = kwargs[attr]
                toa kwargs[attr]
            isipokua:
                new_value = default
            setattr(sys, attr, new_value)
        ikiwa len(kwargs):
             ashiria ValueError(
                    'unrecognized arguments: {0}'.format(kwargs.keys()))
        yield
    mwishowe:
        kila attr, value kwenye originals.items():
            setattr(sys, attr, value)


kundi _ImporterMock:

    """Base kundi to help ukijumuisha creating importer mocks."""

    eleza __init__(self, *names, module_code={}):
        self.modules = {}
        self.module_code = {}
        kila name kwenye names:
            ikiwa sio name.endswith('.__init__'):
                import_name = name
            isipokua:
                import_name = name[:-len('.__init__')]
            ikiwa '.' sio kwenye name:
                package = Tupu
            elikiwa import_name == name:
                package = name.rsplit('.', 1)[0]
            isipokua:
                package = import_name
            module = types.ModuleType(import_name)
            module.__loader__ = self
            module.__file__ = '<mock __file__>'
            module.__package__ = package
            module.attr = name
            ikiwa import_name != name:
                module.__path__ = ['<mock __path__>']
            self.modules[import_name] = module
            ikiwa import_name kwenye module_code:
                self.module_code[import_name] = module_code[import_name]

    eleza __getitem__(self, name):
        rudisha self.modules[name]

    eleza __enter__(self):
        self._uncache = uncache(*self.modules.keys())
        self._uncache.__enter__()
        rudisha self

    eleza __exit__(self, *exc_info):
        self._uncache.__exit__(Tupu, Tupu, Tupu)


kundi mock_modules(_ImporterMock):

    """Importer mock using PEP 302 APIs."""

    eleza find_module(self, fullname, path=Tupu):
        ikiwa fullname sio kwenye self.modules:
            rudisha Tupu
        isipokua:
            rudisha self

    eleza load_module(self, fullname):
        ikiwa fullname sio kwenye self.modules:
             ashiria ImportError
        isipokua:
            sys.modules[fullname] = self.modules[fullname]
            ikiwa fullname kwenye self.module_code:
                jaribu:
                    self.module_code[fullname]()
                except Exception:
                    toa sys.modules[fullname]
                    raise
            rudisha self.modules[fullname]


kundi mock_spec(_ImporterMock):

    """Importer mock using PEP 451 APIs."""

    eleza find_spec(self, fullname, path=Tupu, parent=Tupu):
        jaribu:
            module = self.modules[fullname]
        except KeyError:
            rudisha Tupu
        spec = util.spec_from_file_location(
                fullname, module.__file__, loader=self,
                submodule_search_locations=getattr(module, '__path__', Tupu))
        rudisha spec

    eleza create_module(self, spec):
        ikiwa spec.name sio kwenye self.modules:
             ashiria ImportError
        rudisha self.modules[spec.name]

    eleza exec_module(self, module):
        jaribu:
            self.module_code[module.__spec__.name]()
        except KeyError:
            pass


eleza writes_bytecode_files(fxn):
    """Decorator to protect sys.dont_write_bytecode kutoka mutation na to skip
    tests that require it to be set to Uongo."""
    ikiwa sys.dont_write_bytecode:
        rudisha lambda *args, **kwargs: Tupu
    @functools.wraps(fxn)
    eleza wrapper(*args, **kwargs):
        original = sys.dont_write_bytecode
        sys.dont_write_bytecode = Uongo
        jaribu:
            to_rudisha = fxn(*args, **kwargs)
        mwishowe:
            sys.dont_write_bytecode = original
        rudisha to_return
    rudisha wrapper


eleza ensure_bytecode_path(bytecode_path):
    """Ensure that the __pycache__ directory kila PEP 3147 pyc file exists.

    :param bytecode_path: File system path to PEP 3147 pyc file.
    """
    jaribu:
        os.mkdir(os.path.dirname(bytecode_path))
    except OSError as error:
        ikiwa error.errno != errno.EEXIST:
            raise


@contextlib.contextmanager
eleza temporary_pycache_prefix(prefix):
    """Adjust na restore sys.pycache_prefix."""
    _orig_prefix = sys.pycache_prefix
    sys.pycache_prefix = prefix
    jaribu:
        yield
    mwishowe:
        sys.pycache_prefix = _orig_prefix


@contextlib.contextmanager
eleza create_modules(*names):
    """Temporarily create each named module ukijumuisha an attribute (named 'attr')
    that contains the name passed into the context manager that caused the
    creation of the module.

    All files are created kwenye a temporary directory returned by
    tempfile.mkdtemp(). This directory ni inserted at the beginning of
    sys.path. When the context manager exits all created files (source and
    bytecode) are explicitly deleted.

    No magic ni performed when creating packages! This means that ikiwa you create
    a module within a package you must also create the package's __init__ as
    well.

    """
    source = 'attr = {0!r}'
    created_paths = []
    mapping = {}
    state_manager = Tupu
    uncache_manager = Tupu
    jaribu:
        temp_dir = tempfile.mkdtemp()
        mapping['.root'] = temp_dir
        import_names = set()
        kila name kwenye names:
            ikiwa sio name.endswith('__init__'):
                import_name = name
            isipokua:
                import_name = name[:-len('.__init__')]
            import_names.add(import_name)
            ikiwa import_name kwenye sys.modules:
                toa sys.modules[import_name]
            name_parts = name.split('.')
            file_path = temp_dir
            kila directory kwenye name_parts[:-1]:
                file_path = os.path.join(file_path, directory)
                ikiwa sio os.path.exists(file_path):
                    os.mkdir(file_path)
                    created_paths.append(file_path)
            file_path = os.path.join(file_path, name_parts[-1] + '.py')
            ukijumuisha open(file_path, 'w') as file:
                file.write(source.format(name))
            created_paths.append(file_path)
            mapping[name] = file_path
        uncache_manager = uncache(*import_names)
        uncache_manager.__enter__()
        state_manager = import_state(path=[temp_dir])
        state_manager.__enter__()
        tuma mapping
    mwishowe:
        ikiwa state_manager ni sio Tupu:
            state_manager.__exit__(Tupu, Tupu, Tupu)
        ikiwa uncache_manager ni sio Tupu:
            uncache_manager.__exit__(Tupu, Tupu, Tupu)
        support.rmtree(temp_dir)


eleza mock_path_hook(*entries, importer):
    """A mock sys.path_hooks entry."""
    eleza hook(entry):
        ikiwa entry sio kwenye entries:
             ashiria ImportError
        rudisha importer
    rudisha hook


kundi CASEOKTestBase:

    eleza caseok_env_changed(self, *, should_exist):
        possibilities = b'PYTHONCASEOK', 'PYTHONCASEOK'
        ikiwa any(x kwenye self.importlib._bootstrap_external._os.environ
                    kila x kwenye possibilities) != should_exist:
            self.skipTest('os.environ changes sio reflected kwenye _os.environ')


eleza create_package(file, path, is_package=Kweli, contents=()):
    kundi Reader(ResourceReader):
        eleza get_resource_reader(self, package):
            rudisha self

        eleza open_resource(self, path):
            self._path = path
            ikiwa isinstance(file, Exception):
                 ashiria file
            isipokua:
                rudisha file

        eleza resource_path(self, path_):
            self._path = path_
            ikiwa isinstance(path, Exception):
                 ashiria path
            isipokua:
                rudisha path

        eleza is_resource(self, path_):
            self._path = path_
            ikiwa isinstance(path, Exception):
                 ashiria path
            kila entry kwenye contents:
                parts = entry.split('/')
                ikiwa len(parts) == 1 na parts[0] == path_:
                    rudisha Kweli
            rudisha Uongo

        eleza contents(self):
            ikiwa isinstance(path, Exception):
                 ashiria path
            # There's no tuma kutoka kwenye baseball, er, Python 2.
            kila entry kwenye contents:
                tuma entry

    name = 'testingpackage'
    # Unfortunately importlib.util.module_from_spec() was sio introduced until
    # Python 3.5.
    module = types.ModuleType(name)
    loader = Reader()
    spec = machinery.ModuleSpec(
        name, loader,
        origin='does-not-exist',
        is_package=is_package)
    module.__spec__ = spec
    module.__loader__ = loader
    rudisha module


kundi CommonResourceTests(abc.ABC):
    @abc.abstractmethod
    eleza execute(self, package, path):
         ashiria NotImplementedError

    eleza test_package_name(self):
        # Passing kwenye the package name should succeed.
        self.execute(data01.__name__, 'utf-8.file')

    eleza test_package_object(self):
        # Passing kwenye the package itself should succeed.
        self.execute(data01, 'utf-8.file')

    eleza test_string_path(self):
        # Passing kwenye a string kila the path should succeed.
        path = 'utf-8.file'
        self.execute(data01, path)

    @unittest.skipIf(sys.version_info < (3, 6), 'requires os.PathLike support')
    eleza test_pathlib_path(self):
        # Passing kwenye a pathlib.PurePath object kila the path should succeed.
        path = PurePath('utf-8.file')
        self.execute(data01, path)

    eleza test_absolute_path(self):
        # An absolute path ni a ValueError.
        path = Path(__file__)
        full_path = path.parent/'utf-8.file'
        ukijumuisha self.assertRaises(ValueError):
            self.execute(data01, full_path)

    eleza test_relative_path(self):
        # A reative path ni a ValueError.
        ukijumuisha self.assertRaises(ValueError):
            self.execute(data01, '../data01/utf-8.file')

    eleza test_importing_module_as_side_effect(self):
        # The anchor package can already be imported.
        toa sys.modules[data01.__name__]
        self.execute(data01.__name__, 'utf-8.file')

    eleza test_non_package_by_name(self):
        # The anchor package cannot be a module.
        ukijumuisha self.assertRaises(TypeError):
            self.execute(__name__, 'utf-8.file')

    eleza test_non_package_by_package(self):
        # The anchor package cannot be a module.
        ukijumuisha self.assertRaises(TypeError):
            module = sys.modules['test.test_importlib.util']
            self.execute(module, 'utf-8.file')

    @unittest.skipIf(sys.version_info < (3,), 'No ResourceReader kwenye Python 2')
    eleza test_resource_opener(self):
        bytes_data = io.BytesIO(b'Hello, world!')
        package = create_package(file=bytes_data, path=FileNotFoundError())
        self.execute(package, 'utf-8.file')
        self.assertEqual(package.__loader__._path, 'utf-8.file')

    @unittest.skipIf(sys.version_info < (3,), 'No ResourceReader kwenye Python 2')
    eleza test_resource_path(self):
        bytes_data = io.BytesIO(b'Hello, world!')
        path = __file__
        package = create_package(file=bytes_data, path=path)
        self.execute(package, 'utf-8.file')
        self.assertEqual(package.__loader__._path, 'utf-8.file')

    eleza test_useless_loader(self):
        package = create_package(file=FileNotFoundError(),
                                 path=FileNotFoundError())
        ukijumuisha self.assertRaises(FileNotFoundError):
            self.execute(package, 'utf-8.file')


kundi ZipSetupBase:
    ZIP_MODULE = Tupu

    @classmethod
    eleza setUpClass(cls):
        data_path = Path(cls.ZIP_MODULE.__file__)
        data_dir = data_path.parent
        cls._zip_path = str(data_dir / 'ziptestdata.zip')
        sys.path.append(cls._zip_path)
        cls.data = importlib.import_module('ziptestdata')

    @classmethod
    eleza tearDownClass(cls):
        jaribu:
            sys.path.remove(cls._zip_path)
        except ValueError:
            pass

        jaribu:
            toa sys.path_importer_cache[cls._zip_path]
            toa sys.modules[cls.data.__name__]
        except KeyError:
            pass

        jaribu:
            toa cls.data
            toa cls._zip_path
        except AttributeError:
            pass

    eleza setUp(self):
        modules = support.modules_setup()
        self.addCleanup(support.modules_cleanup, *modules)


kundi ZipSetup(ZipSetupBase):
    ZIP_MODULE = zipdata01                          # type: ignore
