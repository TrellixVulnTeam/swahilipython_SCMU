"""Utility code kila constructing importers, etc."""
kutoka . agiza abc
kutoka ._bootstrap agiza module_from_spec
kutoka ._bootstrap agiza _resolve_name
kutoka ._bootstrap agiza spec_from_loader
kutoka ._bootstrap agiza _find_spec
kutoka ._bootstrap_external agiza MAGIC_NUMBER
kutoka ._bootstrap_external agiza _RAW_MAGIC_NUMBER
kutoka ._bootstrap_external agiza cache_from_source
kutoka ._bootstrap_external agiza decode_source
kutoka ._bootstrap_external agiza source_from_cache
kutoka ._bootstrap_external agiza spec_from_file_location

kutoka contextlib agiza contextmanager
agiza _imp
agiza functools
agiza sys
agiza types
agiza warnings


eleza source_hash(source_bytes):
    "Return the hash of *source_bytes* kama used kwenye hash-based pyc files."
    rudisha _imp.source_hash(_RAW_MAGIC_NUMBER, source_bytes)


eleza resolve_name(name, package):
    """Resolve a relative module name to an absolute one."""
    ikiwa sio name.startswith('.'):
        rudisha name
    lasivyo sio package:
        ashiria ValueError(f'no package specified kila {repr(name)} '
                         '(required kila relative module names)')
    level = 0
    kila character kwenye name:
        ikiwa character != '.':
            koma
        level += 1
    rudisha _resolve_name(name[level:], package, level)


eleza _find_spec_from_path(name, path=Tupu):
    """Return the spec kila the specified module.

    First, sys.modules ni checked to see ikiwa the module was already imported. If
    so, then sys.modules[name].__spec__ ni rudishaed. If that happens to be
    set to Tupu, then ValueError ni ashiriad. If the module ni sio in
    sys.modules, then sys.meta_path ni searched kila a suitable spec ukijumuisha the
    value of 'path' given to the finders. Tupu ni rudishaed ikiwa no spec could
    be found.

    Dotted names do sio have their parent packages implicitly imported. You will
    most likely need to explicitly agiza all parent packages kwenye the proper
    order kila a submodule to get the correct spec.

    """
    ikiwa name haiko kwenye sys.modules:
        rudisha _find_spec(name, path)
    isipokua:
        module = sys.modules[name]
        ikiwa module ni Tupu:
            rudisha Tupu
        jaribu:
            spec = module.__spec__
        tatizo AttributeError:
            ashiria ValueError('{}.__spec__ ni sio set'.format(name)) kutoka Tupu
        isipokua:
            ikiwa spec ni Tupu:
                ashiria ValueError('{}.__spec__ ni Tupu'.format(name))
            rudisha spec


eleza find_spec(name, package=Tupu):
    """Return the spec kila the specified module.

    First, sys.modules ni checked to see ikiwa the module was already imported. If
    so, then sys.modules[name].__spec__ ni rudishaed. If that happens to be
    set to Tupu, then ValueError ni ashiriad. If the module ni sio in
    sys.modules, then sys.meta_path ni searched kila a suitable spec ukijumuisha the
    value of 'path' given to the finders. Tupu ni rudishaed ikiwa no spec could
    be found.

    If the name ni kila submodule (contains a dot), the parent module is
    automatically imported.

    The name na package arguments work the same kama importlib.import_module().
    In other words, relative module names (ukijumuisha leading dots) work.

    """
    fullname = resolve_name(name, package) ikiwa name.startswith('.') isipokua name
    ikiwa fullname haiko kwenye sys.modules:
        parent_name = fullname.rpartition('.')[0]
        ikiwa parent_name:
            parent = __import__(parent_name, kutokalist=['__path__'])
            jaribu:
                parent_path = parent.__path__
            tatizo AttributeError kama e:
                ashiria ModuleNotFoundError(
                    f"__path__ attribute sio found on {parent_name!r} "
                    f"wakati trying to find {fullname!r}", name=fullname) kutoka e
        isipokua:
            parent_path = Tupu
        rudisha _find_spec(fullname, parent_path)
    isipokua:
        module = sys.modules[fullname]
        ikiwa module ni Tupu:
            rudisha Tupu
        jaribu:
            spec = module.__spec__
        tatizo AttributeError:
            ashiria ValueError('{}.__spec__ ni sio set'.format(name)) kutoka Tupu
        isipokua:
            ikiwa spec ni Tupu:
                ashiria ValueError('{}.__spec__ ni Tupu'.format(name))
            rudisha spec


@contextmanager
eleza _module_to_load(name):
    is_reload = name kwenye sys.modules

    module = sys.modules.get(name)
    ikiwa sio is_reload:
        # This must be done before open() ni called kama the 'io' module
        # implicitly agizas 'locale' na would otherwise trigger an
        # infinite loop.
        module = type(sys)(name)
        # This must be done before putting the module kwenye sys.modules
        # (otherwise an optimization shortcut kwenye agiza.c becomes wrong)
        module.__initializing__ = Kweli
        sys.modules[name] = module
    jaribu:
        tuma module
    tatizo Exception:
        ikiwa sio is_reload:
            jaribu:
                toa sys.modules[name]
            tatizo KeyError:
                pita
    mwishowe:
        module.__initializing__ = Uongo


eleza set_package(fxn):
    """Set __package__ on the rudishaed module.

    This function ni deprecated.

    """
    @functools.wraps(fxn)
    eleza set_package_wrapper(*args, **kwargs):
        warnings.warn('The agiza system now takes care of this automatically.',
                      DeprecationWarning, stacklevel=2)
        module = fxn(*args, **kwargs)
        ikiwa getattr(module, '__package__', Tupu) ni Tupu:
            module.__package__ = module.__name__
            ikiwa sio hasattr(module, '__path__'):
                module.__package__ = module.__package__.rpartition('.')[0]
        rudisha module
    rudisha set_package_wrapper


eleza set_loader(fxn):
    """Set __loader__ on the rudishaed module.

    This function ni deprecated.

    """
    @functools.wraps(fxn)
    eleza set_loader_wrapper(self, *args, **kwargs):
        warnings.warn('The agiza system now takes care of this automatically.',
                      DeprecationWarning, stacklevel=2)
        module = fxn(self, *args, **kwargs)
        ikiwa getattr(module, '__loader__', Tupu) ni Tupu:
            module.__loader__ = self
        rudisha module
    rudisha set_loader_wrapper


eleza module_for_loader(fxn):
    """Decorator to handle selecting the proper module kila loaders.

    The decorated function ni pitaed the module to use instead of the module
    name. The module pitaed kwenye to the function ni either kutoka sys.modules if
    it already exists ama ni a new module. If the module ni new, then __name__
    ni set the first argument to the method, __loader__ ni set to self, na
    __package__ ni set accordingly (ikiwa self.is_package() ni defined) will be set
    before it ni pitaed to the decorated function (ikiwa self.is_package() does
    sio work kila the module it will be set post-load).

    If an exception ni ashiriad na the decorator created the module it is
    subsequently removed kutoka sys.modules.

    The decorator assumes that the decorated function takes the module name as
    the second argument.

    """
    warnings.warn('The agiza system now takes care of this automatically.',
                  DeprecationWarning, stacklevel=2)
    @functools.wraps(fxn)
    eleza module_for_loader_wrapper(self, fullname, *args, **kwargs):
        ukijumuisha _module_to_load(fullname) kama module:
            module.__loader__ = self
            jaribu:
                is_package = self.is_package(fullname)
            tatizo (ImportError, AttributeError):
                pita
            isipokua:
                ikiwa is_package:
                    module.__package__ = fullname
                isipokua:
                    module.__package__ = fullname.rpartition('.')[0]
            # If __package__ was sio set above, __import__() will do it later.
            rudisha fxn(self, module, *args, **kwargs)

    rudisha module_for_loader_wrapper


kundi _LazyModule(types.ModuleType):

    """A subkundi of the module type which triggers loading upon attribute access."""

    eleza __getattribute__(self, attr):
        """Trigger the load of the module na rudisha the attribute."""
        # All module metadata must be garnered kutoka __spec__ kwenye order to avoid
        # using mutated values.
        # Stop triggering this method.
        self.__class__ = types.ModuleType
        # Get the original name to make sure no object substitution occurred
        # kwenye sys.modules.
        original_name = self.__spec__.name
        # Figure out exactly what attributes were mutated between the creation
        # of the module na now.
        attrs_then = self.__spec__.loader_state['__dict__']
        original_type = self.__spec__.loader_state['__class__']
        attrs_now = self.__dict__
        attrs_updated = {}
        kila key, value kwenye attrs_now.items():
            # Code that set the attribute may have kept a reference to the
            # assigned object, making identity more agizaant than equality.
            ikiwa key haiko kwenye attrs_then:
                attrs_updated[key] = value
            lasivyo id(attrs_now[key]) != id(attrs_then[key]):
                attrs_updated[key] = value
        self.__spec__.loader.exec_module(self)
        # If exec_module() was used directly there ni no guarantee the module
        # object was put into sys.modules.
        ikiwa original_name kwenye sys.modules:
            ikiwa id(self) != id(sys.modules[original_name]):
                ashiria ValueError(f"module object kila {original_name!r} "
                                  "substituted kwenye sys.modules during a lazy "
                                  "load")
        # Update after loading since that's what would happen kwenye an eager
        # loading situation.
        self.__dict__.update(attrs_updated)
        rudisha getattr(self, attr)

    eleza __delattr__(self, attr):
        """Trigger the load na then perform the deletion."""
        # To trigger the load na ashiria an exception ikiwa the attribute
        # doesn't exist.
        self.__getattribute__(attr)
        delattr(self, attr)


kundi LazyLoader(abc.Loader):

    """A loader that creates a module which defers loading until attribute access."""

    @staticmethod
    eleza __check_eager_loader(loader):
        ikiwa sio hasattr(loader, 'exec_module'):
            ashiria TypeError('loader must define exec_module()')

    @classmethod
    eleza factory(cls, loader):
        """Construct a callable which rudishas the eager loader made lazy."""
        cls.__check_eager_loader(loader)
        rudisha lambda *args, **kwargs: cls(loader(*args, **kwargs))

    eleza __init__(self, loader):
        self.__check_eager_loader(loader)
        self.loader = loader

    eleza create_module(self, spec):
        rudisha self.loader.create_module(spec)

    eleza exec_module(self, module):
        """Make the module load lazily."""
        module.__spec__.loader = self.loader
        module.__loader__ = self.loader
        # Don't need to worry about deep-copying kama trying to set an attribute
        # on an object would have triggered the load,
        # e.g. ``module.__spec__.loader = Tupu`` would trigger a load kutoka
        # trying to access module.__spec__.
        loader_state = {}
        loader_state['__dict__'] = module.__dict__.copy()
        loader_state['__class__'] = module.__class__
        module.__spec__.loader_state = loader_state
        module.__class__ = _LazyModule
