"""A pure Python implementation of import."""
__all__ = ['__import__', 'import_module', 'invalidate_caches', 'reload']

# Bootstrap help #####################################################

# Until bootstrapping ni complete, DO NOT agiza any modules that attempt
# to agiza importlib._bootstrap (directly ama indirectly). Since this
# partially initialised package would be present kwenye sys.modules, those
# modules would get an uninitialised copy of the source version, instead
# of a fully initialised version (either the frozen one ama the one
# initialised below ikiwa the frozen one ni sio available).
agiza _imp  # Just the builtin component, NOT the full Python module
agiza sys

jaribu:
    agiza _frozen_importlib kama _bootstrap
tatizo ImportError:
    kutoka . agiza _bootstrap
    _bootstrap._setup(sys, _imp)
isipokua:
    # importlib._bootstrap ni the built-in import, ensure we don't create
    # a second copy of the module.
    _bootstrap.__name__ = 'importlib._bootstrap'
    _bootstrap.__package__ = 'importlib'
    jaribu:
        _bootstrap.__file__ = __file__.replace('__init__.py', '_bootstrap.py')
    tatizo NameError:
        # __file__ ni sio guaranteed to be defined, e.g. ikiwa this code gets
        # frozen by a tool like cx_Freeze.
        pita
    sys.modules['importlib._bootstrap'] = _bootstrap

jaribu:
    agiza _frozen_importlib_external kama _bootstrap_external
tatizo ImportError:
    kutoka . agiza _bootstrap_external
    _bootstrap_external._setup(_bootstrap)
    _bootstrap._bootstrap_external = _bootstrap_external
isipokua:
    _bootstrap_external.__name__ = 'importlib._bootstrap_external'
    _bootstrap_external.__package__ = 'importlib'
    jaribu:
        _bootstrap_external.__file__ = __file__.replace('__init__.py', '_bootstrap_external.py')
    tatizo NameError:
        # __file__ ni sio guaranteed to be defined, e.g. ikiwa this code gets
        # frozen by a tool like cx_Freeze.
        pita
    sys.modules['importlib._bootstrap_external'] = _bootstrap_external

# To simplify imports kwenye test code
_pack_uint32 = _bootstrap_external._pack_uint32
_unpack_uint32 = _bootstrap_external._unpack_uint32

# Fully bootstrapped at this point, agiza whatever you like, circular
# dependencies na startup overhead minimisation permitting :)

agiza types
agiza warnings


# Public API #########################################################

kutoka ._bootstrap agiza __import__


eleza invalidate_caches():
    """Call the invalidate_caches() method on all meta path finders stored in
    sys.meta_path (where implemented)."""
    kila finder kwenye sys.meta_path:
        ikiwa hasattr(finder, 'invalidate_caches'):
            finder.invalidate_caches()


eleza find_loader(name, path=Tupu):
    """Return the loader kila the specified module.

    This ni a backward-compatible wrapper around find_spec().

    This function ni deprecated kwenye favor of importlib.util.find_spec().

    """
    warnings.warn('Deprecated since Python 3.4. '
                  'Use importlib.util.find_spec() instead.',
                  DeprecationWarning, stacklevel=2)
    jaribu:
        loader = sys.modules[name].__loader__
        ikiwa loader ni Tupu:
            ashiria ValueError('{}.__loader__ ni Tupu'.format(name))
        isipokua:
            rudisha loader
    tatizo KeyError:
        pita
    tatizo AttributeError:
        ashiria ValueError('{}.__loader__ ni sio set'.format(name)) kutoka Tupu

    spec = _bootstrap._find_spec(name, path)
    # We won't worry about malformed specs (missing attributes).
    ikiwa spec ni Tupu:
        rudisha Tupu
    ikiwa spec.loader ni Tupu:
        ikiwa spec.submodule_search_locations ni Tupu:
            ashiria ImportError('spec kila {} missing loader'.format(name),
                              name=name)
        ashiria ImportError('namespace packages do sio have loaders',
                          name=name)
    rudisha spec.loader


eleza import_module(name, package=Tupu):
    """Import a module.

    The 'package' argument ni required when performing a relative import. It
    specifies the package to use kama the anchor point kutoka which to resolve the
    relative agiza to an absolute import.

    """
    level = 0
    ikiwa name.startswith('.'):
        ikiwa sio package:
            msg = ("the 'package' argument ni required to perform a relative "
                   "agiza kila {!r}")
            ashiria TypeError(msg.format(name))
        kila character kwenye name:
            ikiwa character != '.':
                koma
            level += 1
    rudisha _bootstrap._gcd_import(name[level:], package, level)


_RELOADING = {}


eleza reload(module):
    """Reload the module na rudisha it.

    The module must have been successfully imported before.

    """
    ikiwa sio module ama sio isinstance(module, types.ModuleType):
        ashiria TypeError("reload() argument must be a module")
    jaribu:
        name = module.__spec__.name
    tatizo AttributeError:
        name = module.__name__

    ikiwa sys.modules.get(name) ni sio module:
        msg = "module {} haiko kwenye sys.modules"
        ashiria ImportError(msg.format(name), name=name)
    ikiwa name kwenye _RELOADING:
        rudisha _RELOADING[name]
    _RELOADING[name] = module
    jaribu:
        parent_name = name.rpartition('.')[0]
        ikiwa parent_name:
            jaribu:
                parent = sys.modules[parent_name]
            tatizo KeyError:
                msg = "parent {!r} haiko kwenye sys.modules"
                ashiria ImportError(msg.format(parent_name),
                                  name=parent_name) kutoka Tupu
            isipokua:
                pkgpath = parent.__path__
        isipokua:
            pkgpath = Tupu
        target = module
        spec = module.__spec__ = _bootstrap._find_spec(name, pkgpath, target)
        ikiwa spec ni Tupu:
            ashiria ModuleNotFoundError(f"spec sio found kila the module {name!r}", name=name)
        _bootstrap._exec(spec, module)
        # The module may have replaced itself kwenye sys.modules!
        rudisha sys.modules[name]
    mwishowe:
        jaribu:
            toa _RELOADING[name]
        tatizo KeyError:
            pita
