"""A pure Python implementation of agiza."""
__all__ = ['__import__', 'import_module', 'invalidate_caches', 'reload']

# Bootstrap help #####################################################

# Until bootstrapping is complete, DO NOT agiza any modules that attempt
# to agiza importlib._bootstrap (directly or indirectly). Since this
# partially initialised package would be present in sys.modules, those
# modules would get an uninitialised copy of the source version, instead
# of a fully initialised version (either the frozen one or the one
# initialised below ikiwa the frozen one is not available).
agiza _imp  # Just the builtin component, NOT the full Python module
agiza sys

try:
    agiza _frozen_importlib as _bootstrap
except ImportError:
    kutoka . agiza _bootstrap
    _bootstrap._setup(sys, _imp)
else:
    # importlib._bootstrap is the built-in agiza, ensure we don't create
    # a second copy of the module.
    _bootstrap.__name__ = 'importlib._bootstrap'
    _bootstrap.__package__ = 'importlib'
    try:
        _bootstrap.__file__ = __file__.replace('__init__.py', '_bootstrap.py')
    except NameError:
        # __file__ is not guaranteed to be defined, e.g. ikiwa this code gets
        # frozen by a tool like cx_Freeze.
        pass
    sys.modules['importlib._bootstrap'] = _bootstrap

try:
    agiza _frozen_importlib_external as _bootstrap_external
except ImportError:
    kutoka . agiza _bootstrap_external
    _bootstrap_external._setup(_bootstrap)
    _bootstrap._bootstrap_external = _bootstrap_external
else:
    _bootstrap_external.__name__ = 'importlib._bootstrap_external'
    _bootstrap_external.__package__ = 'importlib'
    try:
        _bootstrap_external.__file__ = __file__.replace('__init__.py', '_bootstrap_external.py')
    except NameError:
        # __file__ is not guaranteed to be defined, e.g. ikiwa this code gets
        # frozen by a tool like cx_Freeze.
        pass
    sys.modules['importlib._bootstrap_external'] = _bootstrap_external

# To simplify agizas in test code
_pack_uint32 = _bootstrap_external._pack_uint32
_unpack_uint32 = _bootstrap_external._unpack_uint32

# Fully bootstrapped at this point, agiza whatever you like, circular
# dependencies and startup overhead minimisation permitting :)

agiza types
agiza warnings


# Public API #########################################################

kutoka ._bootstrap agiza __import__


eleza invalidate_caches():
    """Call the invalidate_caches() method on all meta path finders stored in
    sys.meta_path (where implemented)."""
    for finder in sys.meta_path:
        ikiwa hasattr(finder, 'invalidate_caches'):
            finder.invalidate_caches()


eleza find_loader(name, path=None):
    """Return the loader for the specified module.

    This is a backward-compatible wrapper around find_spec().

    This function is deprecated in favor of importlib.util.find_spec().

    """
    warnings.warn('Deprecated since Python 3.4. '
                  'Use importlib.util.find_spec() instead.',
                  DeprecationWarning, stacklevel=2)
    try:
        loader = sys.modules[name].__loader__
        ikiwa loader is None:
            raise ValueError('{}.__loader__ is None'.format(name))
        else:
            rudisha loader
    except KeyError:
        pass
    except AttributeError:
        raise ValueError('{}.__loader__ is not set'.format(name)) kutoka None

    spec = _bootstrap._find_spec(name, path)
    # We won't worry about malformed specs (missing attributes).
    ikiwa spec is None:
        rudisha None
    ikiwa spec.loader is None:
        ikiwa spec.submodule_search_locations is None:
            raise ImportError('spec for {} missing loader'.format(name),
                              name=name)
        raise ImportError('namespace packages do not have loaders',
                          name=name)
    rudisha spec.loader


eleza import_module(name, package=None):
    """Import a module.

    The 'package' argument is required when performing a relative agiza. It
    specifies the package to use as the anchor point kutoka which to resolve the
    relative agiza to an absolute agiza.

    """
    level = 0
    ikiwa name.startswith('.'):
        ikiwa not package:
            msg = ("the 'package' argument is required to perform a relative "
                   "agiza for {!r}")
            raise TypeError(msg.format(name))
        for character in name:
            ikiwa character != '.':
                break
            level += 1
    rudisha _bootstrap._gcd_agiza(name[level:], package, level)


_RELOADING = {}


eleza reload(module):
    """Reload the module and rudisha it.

    The module must have been successfully imported before.

    """
    ikiwa not module or not isinstance(module, types.ModuleType):
        raise TypeError("reload() argument must be a module")
    try:
        name = module.__spec__.name
    except AttributeError:
        name = module.__name__

    ikiwa sys.modules.get(name) is not module:
        msg = "module {} not in sys.modules"
        raise ImportError(msg.format(name), name=name)
    ikiwa name in _RELOADING:
        rudisha _RELOADING[name]
    _RELOADING[name] = module
    try:
        parent_name = name.rpartition('.')[0]
        ikiwa parent_name:
            try:
                parent = sys.modules[parent_name]
            except KeyError:
                msg = "parent {!r} not in sys.modules"
                raise ImportError(msg.format(parent_name),
                                  name=parent_name) kutoka None
            else:
                pkgpath = parent.__path__
        else:
            pkgpath = None
        target = module
        spec = module.__spec__ = _bootstrap._find_spec(name, pkgpath, target)
        ikiwa spec is None:
            raise ModuleNotFoundError(f"spec not found for the module {name!r}", name=name)
        _bootstrap._exec(spec, module)
        # The module may have replaced itself in sys.modules!
        rudisha sys.modules[name]
    finally:
        try:
            del _RELOADING[name]
        except KeyError:
            pass
