"""Utility code for constructing importers, etc."""
kutoka . agiza abc
kutoka ._bootstrap agiza module_kutoka_spec
kutoka ._bootstrap agiza _resolve_name
kutoka ._bootstrap agiza spec_kutoka_loader
kutoka ._bootstrap agiza _find_spec
kutoka ._bootstrap_external agiza MAGIC_NUMBER
kutoka ._bootstrap_external agiza _RAW_MAGIC_NUMBER
kutoka ._bootstrap_external agiza cache_kutoka_source
kutoka ._bootstrap_external agiza decode_source
kutoka ._bootstrap_external agiza source_kutoka_cache
kutoka ._bootstrap_external agiza spec_kutoka_file_location

kutoka contextlib agiza contextmanager
agiza _imp
agiza functools
agiza sys
agiza types
agiza warnings


eleza source_hash(source_bytes):
    "Return the hash of *source_bytes* as used in hash-based pyc files."
    rudisha _imp.source_hash(_RAW_MAGIC_NUMBER, source_bytes)


eleza resolve_name(name, package):
    """Resolve a relative module name to an absolute one."""
    ikiwa not name.startswith('.'):
        rudisha name
    elikiwa not package:
        raise ValueError(f'no package specified for {repr(name)} '
                         '(required for relative module names)')
    level = 0
    for character in name:
        ikiwa character != '.':
            break
        level += 1
    rudisha _resolve_name(name[level:], package, level)


eleza _find_spec_kutoka_path(name, path=None):
    """Return the spec for the specified module.

    First, sys.modules is checked to see ikiwa the module was already imported. If
    so, then sys.modules[name].__spec__ is returned. If that happens to be
    set to None, then ValueError is raised. If the module is not in
    sys.modules, then sys.meta_path is searched for a suitable spec with the
    value of 'path' given to the finders. None is returned ikiwa no spec could
    be found.

    Dotted names do not have their parent packages implicitly imported. You will
    most likely need to explicitly agiza all parent packages in the proper
    order for a submodule to get the correct spec.

    """
    ikiwa name not in sys.modules:
        rudisha _find_spec(name, path)
    else:
        module = sys.modules[name]
        ikiwa module is None:
            rudisha None
        try:
            spec = module.__spec__
        except AttributeError:
            raise ValueError('{}.__spec__ is not set'.format(name)) kutoka None
        else:
            ikiwa spec is None:
                raise ValueError('{}.__spec__ is None'.format(name))
            rudisha spec


eleza find_spec(name, package=None):
    """Return the spec for the specified module.

    First, sys.modules is checked to see ikiwa the module was already imported. If
    so, then sys.modules[name].__spec__ is returned. If that happens to be
    set to None, then ValueError is raised. If the module is not in
    sys.modules, then sys.meta_path is searched for a suitable spec with the
    value of 'path' given to the finders. None is returned ikiwa no spec could
    be found.

    If the name is for submodule (contains a dot), the parent module is
    automatically imported.

    The name and package arguments work the same as importlib.import_module().
    In other words, relative module names (with leading dots) work.

    """
    fullname = resolve_name(name, package) ikiwa name.startswith('.') else name
    ikiwa fullname not in sys.modules:
        parent_name = fullname.rpartition('.')[0]
        ikiwa parent_name:
            parent = __import__(parent_name, kutokalist=['__path__'])
            try:
                parent_path = parent.__path__
            except AttributeError as e:
                raise ModuleNotFoundError(
                    f"__path__ attribute not found on {parent_name!r} "
                    f"while trying to find {fullname!r}", name=fullname) kutoka e
        else:
            parent_path = None
        rudisha _find_spec(fullname, parent_path)
    else:
        module = sys.modules[fullname]
        ikiwa module is None:
            rudisha None
        try:
            spec = module.__spec__
        except AttributeError:
            raise ValueError('{}.__spec__ is not set'.format(name)) kutoka None
        else:
            ikiwa spec is None:
                raise ValueError('{}.__spec__ is None'.format(name))
            rudisha spec


@contextmanager
eleza _module_to_load(name):
    is_reload = name in sys.modules

    module = sys.modules.get(name)
    ikiwa not is_reload:
        # This must be done before open() is called as the 'io' module
        # implicitly agizas 'locale' and would otherwise trigger an
        # infinite loop.
        module = type(sys)(name)
        # This must be done before putting the module in sys.modules
        # (otherwise an optimization shortcut in agiza.c becomes wrong)
        module.__initializing__ = True
        sys.modules[name] = module
    try:
        yield module
    except Exception:
        ikiwa not is_reload:
            try:
                del sys.modules[name]
            except KeyError:
                pass
    finally:
        module.__initializing__ = False


eleza set_package(fxn):
    """Set __package__ on the returned module.

    This function is deprecated.

    """
    @functools.wraps(fxn)
    eleza set_package_wrapper(*args, **kwargs):
        warnings.warn('The agiza system now takes care of this automatically.',
                      DeprecationWarning, stacklevel=2)
        module = fxn(*args, **kwargs)
        ikiwa getattr(module, '__package__', None) is None:
            module.__package__ = module.__name__
            ikiwa not hasattr(module, '__path__'):
                module.__package__ = module.__package__.rpartition('.')[0]
        rudisha module
    rudisha set_package_wrapper


eleza set_loader(fxn):
    """Set __loader__ on the returned module.

    This function is deprecated.

    """
    @functools.wraps(fxn)
    eleza set_loader_wrapper(self, *args, **kwargs):
        warnings.warn('The agiza system now takes care of this automatically.',
                      DeprecationWarning, stacklevel=2)
        module = fxn(self, *args, **kwargs)
        ikiwa getattr(module, '__loader__', None) is None:
            module.__loader__ = self
        rudisha module
    rudisha set_loader_wrapper


eleza module_for_loader(fxn):
    """Decorator to handle selecting the proper module for loaders.

    The decorated function is passed the module to use instead of the module
    name. The module passed in to the function is either kutoka sys.modules if
    it already exists or is a new module. If the module is new, then __name__
    is set the first argument to the method, __loader__ is set to self, and
    __package__ is set accordingly (ikiwa self.is_package() is defined) will be set
    before it is passed to the decorated function (ikiwa self.is_package() does
    not work for the module it will be set post-load).

    If an exception is raised and the decorator created the module it is
    subsequently removed kutoka sys.modules.

    The decorator assumes that the decorated function takes the module name as
    the second argument.

    """
    warnings.warn('The agiza system now takes care of this automatically.',
                  DeprecationWarning, stacklevel=2)
    @functools.wraps(fxn)
    eleza module_for_loader_wrapper(self, fullname, *args, **kwargs):
        with _module_to_load(fullname) as module:
            module.__loader__ = self
            try:
                is_package = self.is_package(fullname)
            except (ImportError, AttributeError):
                pass
            else:
                ikiwa is_package:
                    module.__package__ = fullname
                else:
                    module.__package__ = fullname.rpartition('.')[0]
            # If __package__ was not set above, __import__() will do it later.
            rudisha fxn(self, module, *args, **kwargs)

    rudisha module_for_loader_wrapper


kundi _LazyModule(types.ModuleType):

    """A subkundi of the module type which triggers loading upon attribute access."""

    eleza __getattribute__(self, attr):
        """Trigger the load of the module and rudisha the attribute."""
        # All module metadata must be garnered kutoka __spec__ in order to avoid
        # using mutated values.
        # Stop triggering this method.
        self.__class__ = types.ModuleType
        # Get the original name to make sure no object substitution occurred
        # in sys.modules.
        original_name = self.__spec__.name
        # Figure out exactly what attributes were mutated between the creation
        # of the module and now.
        attrs_then = self.__spec__.loader_state['__dict__']
        original_type = self.__spec__.loader_state['__class__']
        attrs_now = self.__dict__
        attrs_updated = {}
        for key, value in attrs_now.items():
            # Code that set the attribute may have kept a reference to the
            # assigned object, making identity more agizaant than equality.
            ikiwa key not in attrs_then:
                attrs_updated[key] = value
            elikiwa id(attrs_now[key]) != id(attrs_then[key]):
                attrs_updated[key] = value
        self.__spec__.loader.exec_module(self)
        # If exec_module() was used directly there is no guarantee the module
        # object was put into sys.modules.
        ikiwa original_name in sys.modules:
            ikiwa id(self) != id(sys.modules[original_name]):
                raise ValueError(f"module object for {original_name!r} "
                                  "substituted in sys.modules during a lazy "
                                  "load")
        # Update after loading since that's what would happen in an eager
        # loading situation.
        self.__dict__.update(attrs_updated)
        rudisha getattr(self, attr)

    eleza __delattr__(self, attr):
        """Trigger the load and then perform the deletion."""
        # To trigger the load and raise an exception ikiwa the attribute
        # doesn't exist.
        self.__getattribute__(attr)
        delattr(self, attr)


kundi LazyLoader(abc.Loader):

    """A loader that creates a module which defers loading until attribute access."""

    @staticmethod
    eleza __check_eager_loader(loader):
        ikiwa not hasattr(loader, 'exec_module'):
            raise TypeError('loader must define exec_module()')

    @classmethod
    eleza factory(cls, loader):
        """Construct a callable which returns the eager loader made lazy."""
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
        # Don't need to worry about deep-copying as trying to set an attribute
        # on an object would have triggered the load,
        # e.g. ``module.__spec__.loader = None`` would trigger a load kutoka
        # trying to access module.__spec__.
        loader_state = {}
        loader_state['__dict__'] = module.__dict__.copy()
        loader_state['__class__'] = module.__class__
        module.__spec__.loader_state = loader_state
        module.__class__ = _LazyModule
