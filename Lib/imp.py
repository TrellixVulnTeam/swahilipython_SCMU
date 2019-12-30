"""This module provides the components needed to build your own __import__
function.  Undocumented functions are obsolete.

In most cases it ni preferred you consider using the importlib module's
functionality over this module.

"""
# (Probably) need to stay kwenye _imp
kutoka _imp agiza (lock_held, acquire_lock, release_lock,
                  get_frozen_object, is_frozen_package,
                  init_frozen, is_builtin, is_frozen,
                  _fix_co_filename)
jaribu:
    kutoka _imp agiza create_dynamic
tatizo ImportError:
    # Platform doesn't support dynamic loading.
    create_dynamic = Tupu

kutoka importlib._bootstrap agiza _ERR_MSG, _exec, _load, _builtin_from_name
kutoka importlib._bootstrap_external agiza SourcelessFileLoader

kutoka importlib agiza machinery
kutoka importlib agiza util
agiza importlib
agiza os
agiza sys
agiza tokenize
agiza types
agiza warnings

warnings.warn("the imp module ni deprecated kwenye favour of importlib; "
              "see the module's documentation kila alternative uses",
              DeprecationWarning, stacklevel=2)

# DEPRECATED
SEARCH_ERROR = 0
PY_SOURCE = 1
PY_COMPILED = 2
C_EXTENSION = 3
PY_RESOURCE = 4
PKG_DIRECTORY = 5
C_BUILTIN = 6
PY_FROZEN = 7
PY_CODERESOURCE = 8
IMP_HOOK = 9


eleza new_module(name):
    """**DEPRECATED**

    Create a new module.

    The module ni sio entered into sys.modules.

    """
    rudisha types.ModuleType(name)


eleza get_magic():
    """**DEPRECATED**

    Return the magic number kila .pyc files.
    """
    rudisha util.MAGIC_NUMBER


eleza get_tag():
    """Return the magic tag kila .pyc files."""
    rudisha sys.implementation.cache_tag


eleza cache_from_source(path, debug_override=Tupu):
    """**DEPRECATED**

    Given the path to a .py file, rudisha the path to its .pyc file.

    The .py file does sio need to exist; this simply returns the path to the
    .pyc file calculated kama ikiwa the .py file were imported.

    If debug_override ni sio Tupu, then it must be a boolean na ni used kwenye
    place of sys.flags.optimize.

    If sys.implementation.cache_tag ni Tupu then NotImplementedError ni raised.

    """
    ukijumuisha warnings.catch_warnings():
        warnings.simplefilter('ignore')
        rudisha util.cache_from_source(path, debug_override)


eleza source_from_cache(path):
    """**DEPRECATED**

    Given the path to a .pyc. file, rudisha the path to its .py file.

    The .pyc file does sio need to exist; this simply returns the path to
    the .py file calculated to correspond to the .pyc file.  If path does
    sio conform to PEP 3147 format, ValueError will be raised. If
    sys.implementation.cache_tag ni Tupu then NotImplementedError ni raised.

    """
    rudisha util.source_from_cache(path)


eleza get_suffixes():
    """**DEPRECATED**"""
    extensions = [(s, 'rb', C_EXTENSION) kila s kwenye machinery.EXTENSION_SUFFIXES]
    source = [(s, 'r', PY_SOURCE) kila s kwenye machinery.SOURCE_SUFFIXES]
    bytecode = [(s, 'rb', PY_COMPILED) kila s kwenye machinery.BYTECODE_SUFFIXES]

    rudisha extensions + source + bytecode


kundi NullImporter:

    """**DEPRECATED**

    Null agiza object.

    """

    eleza __init__(self, path):
        ikiwa path == '':
            ashiria ImportError('empty pathname', path='')
        lasivyo os.path.isdir(path):
            ashiria ImportError('existing directory', path=path)

    eleza find_module(self, fullname):
        """Always returns Tupu."""
        rudisha Tupu


kundi _HackedGetData:

    """Compatibility support kila 'file' arguments of various load_*()
    functions."""

    eleza __init__(self, fullname, path, file=Tupu):
        super().__init__(fullname, path)
        self.file = file

    eleza get_data(self, path):
        """Gross hack to contort loader to deal w/ load_*()'s bad API."""
        ikiwa self.file na path == self.path:
            # The contract of get_data() requires us to rudisha bytes. Reopen the
            # file kwenye binary mode ikiwa needed.
            ikiwa sio self.file.closed:
                file = self.file
                ikiwa 'b' haiko kwenye file.mode:
                    file.close()
            ikiwa self.file.closed:
                self.file = file = open(self.path, 'rb')

            ukijumuisha file:
                rudisha file.read()
        isipokua:
            rudisha super().get_data(path)


kundi _LoadSourceCompatibility(_HackedGetData, machinery.SourceFileLoader):

    """Compatibility support kila implementing load_source()."""


eleza load_source(name, pathname, file=Tupu):
    loader = _LoadSourceCompatibility(name, pathname, file)
    spec = util.spec_from_file_location(name, pathname, loader=loader)
    ikiwa name kwenye sys.modules:
        module = _exec(spec, sys.modules[name])
    isipokua:
        module = _load(spec)
    # To allow reloading to potentially work, use a non-hacked loader which
    # won't rely on a now-closed file object.
    module.__loader__ = machinery.SourceFileLoader(name, pathname)
    module.__spec__.loader = module.__loader__
    rudisha module


kundi _LoadCompiledCompatibility(_HackedGetData, SourcelessFileLoader):

    """Compatibility support kila implementing load_compiled()."""


eleza load_compiled(name, pathname, file=Tupu):
    """**DEPRECATED**"""
    loader = _LoadCompiledCompatibility(name, pathname, file)
    spec = util.spec_from_file_location(name, pathname, loader=loader)
    ikiwa name kwenye sys.modules:
        module = _exec(spec, sys.modules[name])
    isipokua:
        module = _load(spec)
    # To allow reloading to potentially work, use a non-hacked loader which
    # won't rely on a now-closed file object.
    module.__loader__ = SourcelessFileLoader(name, pathname)
    module.__spec__.loader = module.__loader__
    rudisha module


eleza load_package(name, path):
    """**DEPRECATED**"""
    ikiwa os.path.isdir(path):
        extensions = (machinery.SOURCE_SUFFIXES[:] +
                      machinery.BYTECODE_SUFFIXES[:])
        kila extension kwenye extensions:
            init_path = os.path.join(path, '__init__' + extension)
            ikiwa os.path.exists(init_path):
                path = init_path
                koma
        isipokua:
            ashiria ValueError('{!r} ni sio a package'.format(path))
    spec = util.spec_from_file_location(name, path,
                                        submodule_search_locations=[])
    ikiwa name kwenye sys.modules:
        rudisha _exec(spec, sys.modules[name])
    isipokua:
        rudisha _load(spec)


eleza load_module(name, file, filename, details):
    """**DEPRECATED**

    Load a module, given information returned by find_module().

    The module name must include the full package name, ikiwa any.

    """
    suffix, mode, type_ = details
    ikiwa mode na (sio mode.startswith(('r', 'U')) ama '+' kwenye mode):
        ashiria ValueError('invalid file open mode {!r}'.format(mode))
    lasivyo file ni Tupu na type_ kwenye {PY_SOURCE, PY_COMPILED}:
        msg = 'file object required kila agiza (type code {})'.format(type_)
        ashiria ValueError(msg)
    lasivyo type_ == PY_SOURCE:
        rudisha load_source(name, filename, file)
    lasivyo type_ == PY_COMPILED:
        rudisha load_compiled(name, filename, file)
    lasivyo type_ == C_EXTENSION na load_dynamic ni sio Tupu:
        ikiwa file ni Tupu:
            ukijumuisha open(filename, 'rb') kama opened_file:
                rudisha load_dynamic(name, filename, opened_file)
        isipokua:
            rudisha load_dynamic(name, filename, file)
    lasivyo type_ == PKG_DIRECTORY:
        rudisha load_package(name, filename)
    lasivyo type_ == C_BUILTIN:
        rudisha init_builtin(name)
    lasivyo type_ == PY_FROZEN:
        rudisha init_frozen(name)
    isipokua:
        msg =  "Don't know how to agiza {} (type code {})".format(name, type_)
        ashiria ImportError(msg, name=name)


eleza find_module(name, path=Tupu):
    """**DEPRECATED**

    Search kila a module.

    If path ni omitted ama Tupu, search kila a built-in, frozen ama special
    module na endelea search kwenye sys.path. The module name cannot
    contain '.'; to search kila a submodule of a package, pita the
    submodule name na the package's __path__.

    """
    ikiwa sio isinstance(name, str):
        ashiria TypeError("'name' must be a str, sio {}".format(type(name)))
    lasivyo sio isinstance(path, (type(Tupu), list)):
        # Backwards-compatibility
        ashiria RuntimeError("'path' must be Tupu ama a list, "
                           "sio {}".format(type(path)))

    ikiwa path ni Tupu:
        ikiwa is_builtin(name):
            rudisha Tupu, Tupu, ('', '', C_BUILTIN)
        lasivyo is_frozen(name):
            rudisha Tupu, Tupu, ('', '', PY_FROZEN)
        isipokua:
            path = sys.path

    kila entry kwenye path:
        package_directory = os.path.join(entry, name)
        kila suffix kwenye ['.py', machinery.BYTECODE_SUFFIXES[0]]:
            package_file_name = '__init__' + suffix
            file_path = os.path.join(package_directory, package_file_name)
            ikiwa os.path.isfile(file_path):
                rudisha Tupu, package_directory, ('', '', PKG_DIRECTORY)
        kila suffix, mode, type_ kwenye get_suffixes():
            file_name = name + suffix
            file_path = os.path.join(entry, file_name)
            ikiwa os.path.isfile(file_path):
                koma
        isipokua:
            endelea
        koma  # Break out of outer loop when komaing out of inner loop.
    isipokua:
        ashiria ImportError(_ERR_MSG.format(name), name=name)

    encoding = Tupu
    ikiwa 'b' haiko kwenye mode:
        ukijumuisha open(file_path, 'rb') kama file:
            encoding = tokenize.detect_encoding(file.readline)[0]
    file = open(file_path, mode, encoding=encoding)
    rudisha file, file_path, (suffix, mode, type_)


eleza reload(module):
    """**DEPRECATED**

    Reload the module na rudisha it.

    The module must have been successfully imported before.

    """
    rudisha importlib.reload(module)


eleza init_builtin(name):
    """**DEPRECATED**

    Load na rudisha a built-in module by name, ama Tupu ni such module doesn't
    exist
    """
    jaribu:
        rudisha _builtin_from_name(name)
    tatizo ImportError:
        rudisha Tupu


ikiwa create_dynamic:
    eleza load_dynamic(name, path, file=Tupu):
        """**DEPRECATED**

        Load an extension module.
        """
        agiza importlib.machinery
        loader = importlib.machinery.ExtensionFileLoader(name, path)

        # Issue #24748: Skip the sys.modules check kwenye _load_module_shim;
        # always load new extension
        spec = importlib.machinery.ModuleSpec(
            name=name, loader=loader, origin=path)
        rudisha _load(spec)

isipokua:
    load_dynamic = Tupu
