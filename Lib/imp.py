"""This module provides the components needed to build your own __import__
function.  Undocumented functions are obsolete.

In most cases it is preferred you consider using the importlib module's
functionality over this module.

"""
# (Probably) need to stay in _imp
kutoka _imp agiza (lock_held, acquire_lock, release_lock,
                  get_frozen_object, is_frozen_package,
                  init_frozen, is_builtin, is_frozen,
                  _fix_co_filename)
try:
    kutoka _imp agiza create_dynamic
except ImportError:
    # Platform doesn't support dynamic loading.
    create_dynamic = None

kutoka importlib._bootstrap agiza _ERR_MSG, _exec, _load, _builtin_kutoka_name
kutoka importlib._bootstrap_external agiza SourcelessFileLoader

kutoka importlib agiza machinery
kutoka importlib agiza util
agiza importlib
agiza os
agiza sys
agiza tokenize
agiza types
agiza warnings

warnings.warn("the imp module is deprecated in favour of importlib; "
              "see the module's documentation for alternative uses",
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

    The module is not entered into sys.modules.

    """
    rudisha types.ModuleType(name)


eleza get_magic():
    """**DEPRECATED**

    Return the magic number for .pyc files.
    """
    rudisha util.MAGIC_NUMBER


eleza get_tag():
    """Return the magic tag for .pyc files."""
    rudisha sys.implementation.cache_tag


eleza cache_kutoka_source(path, debug_override=None):
    """**DEPRECATED**

    Given the path to a .py file, rudisha the path to its .pyc file.

    The .py file does not need to exist; this simply returns the path to the
    .pyc file calculated as ikiwa the .py file were imported.

    If debug_override is not None, then it must be a boolean and is used in
    place of sys.flags.optimize.

    If sys.implementation.cache_tag is None then NotImplementedError is raised.

    """
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        rudisha util.cache_kutoka_source(path, debug_override)


eleza source_kutoka_cache(path):
    """**DEPRECATED**

    Given the path to a .pyc. file, rudisha the path to its .py file.

    The .pyc file does not need to exist; this simply returns the path to
    the .py file calculated to correspond to the .pyc file.  If path does
    not conform to PEP 3147 format, ValueError will be raised. If
    sys.implementation.cache_tag is None then NotImplementedError is raised.

    """
    rudisha util.source_kutoka_cache(path)


eleza get_suffixes():
    """**DEPRECATED**"""
    extensions = [(s, 'rb', C_EXTENSION) for s in machinery.EXTENSION_SUFFIXES]
    source = [(s, 'r', PY_SOURCE) for s in machinery.SOURCE_SUFFIXES]
    bytecode = [(s, 'rb', PY_COMPILED) for s in machinery.BYTECODE_SUFFIXES]

    rudisha extensions + source + bytecode


kundi NullImporter:

    """**DEPRECATED**

    Null agiza object.

    """

    eleza __init__(self, path):
        ikiwa path == '':
            raise ImportError('empty pathname', path='')
        elikiwa os.path.isdir(path):
            raise ImportError('existing directory', path=path)

    eleza find_module(self, fullname):
        """Always returns None."""
        rudisha None


kundi _HackedGetData:

    """Compatibility support for 'file' arguments of various load_*()
    functions."""

    eleza __init__(self, fullname, path, file=None):
        super().__init__(fullname, path)
        self.file = file

    eleza get_data(self, path):
        """Gross hack to contort loader to deal w/ load_*()'s bad API."""
        ikiwa self.file and path == self.path:
            # The contract of get_data() requires us to rudisha bytes. Reopen the
            # file in binary mode ikiwa needed.
            ikiwa not self.file.closed:
                file = self.file
                ikiwa 'b' not in file.mode:
                    file.close()
            ikiwa self.file.closed:
                self.file = file = open(self.path, 'rb')

            with file:
                rudisha file.read()
        else:
            rudisha super().get_data(path)


kundi _LoadSourceCompatibility(_HackedGetData, machinery.SourceFileLoader):

    """Compatibility support for implementing load_source()."""


eleza load_source(name, pathname, file=None):
    loader = _LoadSourceCompatibility(name, pathname, file)
    spec = util.spec_kutoka_file_location(name, pathname, loader=loader)
    ikiwa name in sys.modules:
        module = _exec(spec, sys.modules[name])
    else:
        module = _load(spec)
    # To allow reloading to potentially work, use a non-hacked loader which
    # won't rely on a now-closed file object.
    module.__loader__ = machinery.SourceFileLoader(name, pathname)
    module.__spec__.loader = module.__loader__
    rudisha module


kundi _LoadCompiledCompatibility(_HackedGetData, SourcelessFileLoader):

    """Compatibility support for implementing load_compiled()."""


eleza load_compiled(name, pathname, file=None):
    """**DEPRECATED**"""
    loader = _LoadCompiledCompatibility(name, pathname, file)
    spec = util.spec_kutoka_file_location(name, pathname, loader=loader)
    ikiwa name in sys.modules:
        module = _exec(spec, sys.modules[name])
    else:
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
        for extension in extensions:
            init_path = os.path.join(path, '__init__' + extension)
            ikiwa os.path.exists(init_path):
                path = init_path
                break
        else:
            raise ValueError('{!r} is not a package'.format(path))
    spec = util.spec_kutoka_file_location(name, path,
                                        submodule_search_locations=[])
    ikiwa name in sys.modules:
        rudisha _exec(spec, sys.modules[name])
    else:
        rudisha _load(spec)


eleza load_module(name, file, filename, details):
    """**DEPRECATED**

    Load a module, given information returned by find_module().

    The module name must include the full package name, ikiwa any.

    """
    suffix, mode, type_ = details
    ikiwa mode and (not mode.startswith(('r', 'U')) or '+' in mode):
        raise ValueError('invalid file open mode {!r}'.format(mode))
    elikiwa file is None and type_ in {PY_SOURCE, PY_COMPILED}:
        msg = 'file object required for agiza (type code {})'.format(type_)
        raise ValueError(msg)
    elikiwa type_ == PY_SOURCE:
        rudisha load_source(name, filename, file)
    elikiwa type_ == PY_COMPILED:
        rudisha load_compiled(name, filename, file)
    elikiwa type_ == C_EXTENSION and load_dynamic is not None:
        ikiwa file is None:
            with open(filename, 'rb') as opened_file:
                rudisha load_dynamic(name, filename, opened_file)
        else:
            rudisha load_dynamic(name, filename, file)
    elikiwa type_ == PKG_DIRECTORY:
        rudisha load_package(name, filename)
    elikiwa type_ == C_BUILTIN:
        rudisha init_builtin(name)
    elikiwa type_ == PY_FROZEN:
        rudisha init_frozen(name)
    else:
        msg =  "Don't know how to agiza {} (type code {})".format(name, type_)
        raise ImportError(msg, name=name)


eleza find_module(name, path=None):
    """**DEPRECATED**

    Search for a module.

    If path is omitted or None, search for a built-in, frozen or special
    module and continue search in sys.path. The module name cannot
    contain '.'; to search for a submodule of a package, pass the
    submodule name and the package's __path__.

    """
    ikiwa not isinstance(name, str):
        raise TypeError("'name' must be a str, not {}".format(type(name)))
    elikiwa not isinstance(path, (type(None), list)):
        # Backwards-compatibility
        raise RuntimeError("'path' must be None or a list, "
                           "not {}".format(type(path)))

    ikiwa path is None:
        ikiwa is_builtin(name):
            rudisha None, None, ('', '', C_BUILTIN)
        elikiwa is_frozen(name):
            rudisha None, None, ('', '', PY_FROZEN)
        else:
            path = sys.path

    for entry in path:
        package_directory = os.path.join(entry, name)
        for suffix in ['.py', machinery.BYTECODE_SUFFIXES[0]]:
            package_file_name = '__init__' + suffix
            file_path = os.path.join(package_directory, package_file_name)
            ikiwa os.path.isfile(file_path):
                rudisha None, package_directory, ('', '', PKG_DIRECTORY)
        for suffix, mode, type_ in get_suffixes():
            file_name = name + suffix
            file_path = os.path.join(entry, file_name)
            ikiwa os.path.isfile(file_path):
                break
        else:
            continue
        break  # Break out of outer loop when breaking out of inner loop.
    else:
        raise ImportError(_ERR_MSG.format(name), name=name)

    encoding = None
    ikiwa 'b' not in mode:
        with open(file_path, 'rb') as file:
            encoding = tokenize.detect_encoding(file.readline)[0]
    file = open(file_path, mode, encoding=encoding)
    rudisha file, file_path, (suffix, mode, type_)


eleza reload(module):
    """**DEPRECATED**

    Reload the module and rudisha it.

    The module must have been successfully imported before.

    """
    rudisha importlib.reload(module)


eleza init_builtin(name):
    """**DEPRECATED**

    Load and rudisha a built-in module by name, or None is such module doesn't
    exist
    """
    try:
        rudisha _builtin_kutoka_name(name)
    except ImportError:
        rudisha None


ikiwa create_dynamic:
    eleza load_dynamic(name, path, file=None):
        """**DEPRECATED**

        Load an extension module.
        """
        agiza importlib.machinery
        loader = importlib.machinery.ExtensionFileLoader(name, path)

        # Issue #24748: Skip the sys.modules check in _load_module_shim;
        # always load new extension
        spec = importlib.machinery.ModuleSpec(
            name=name, loader=loader, origin=path)
        rudisha _load(spec)

else:
    load_dynamic = None
