"""Core implementation of agiza.

This module is NOT meant to be directly imported! It has been designed such
that it can be bootstrapped into Python as the implementation of agiza. As
such it requires the injection of specific modules and attributes in order to
work. One should use importlib as the public-facing version of this module.

"""
#
# IMPORTANT: Whenever making changes to this module, be sure to run a top-level
# `make regen-importlib` followed by `make` in order to get the frozen version
# of the module updated. Not doing so will result in the Makefile to fail for
# all others who don't have a ./python around to freeze the module
# in the early stages of compilation.
#

# See importlib._setup() for what is injected into the global namespace.

# When editing this code be aware that code executed at agiza time CANNOT
# reference any injected objects! This includes not only global code but also
# anything specified at the kundi level.

# Bootstrap-related code ######################################################

_bootstrap_external = None

eleza _wrap(new, old):
    """Simple substitute for functools.update_wrapper."""
    for replace in ['__module__', '__name__', '__qualname__', '__doc__']:
        ikiwa hasattr(old, replace):
            setattr(new, replace, getattr(old, replace))
    new.__dict__.update(old.__dict__)


eleza _new_module(name):
    rudisha type(sys)(name)


# Module-level locking ########################################################

# A dict mapping module names to weakrefs of _ModuleLock instances
# Dictionary protected by the global agiza lock
_module_locks = {}
# A dict mapping thread ids to _ModuleLock instances
_blocking_on = {}


kundi _DeadlockError(RuntimeError):
    pass


kundi _ModuleLock:
    """A recursive lock implementation which is able to detect deadlocks
    (e.g. thread 1 trying to take locks A then B, and thread 2 trying to
    take locks B then A).
    """

    eleza __init__(self, name):
        self.lock = _thread.allocate_lock()
        self.wakeup = _thread.allocate_lock()
        self.name = name
        self.owner = None
        self.count = 0
        self.waiters = 0

    eleza has_deadlock(self):
        # Deadlock avoidance for concurrent circular agizas.
        me = _thread.get_ident()
        tid = self.owner
        while True:
            lock = _blocking_on.get(tid)
            ikiwa lock is None:
                rudisha False
            tid = lock.owner
            ikiwa tid == me:
                rudisha True

    eleza acquire(self):
        """
        Acquire the module lock.  If a potential deadlock is detected,
        a _DeadlockError is raised.
        Otherwise, the lock is always acquired and True is returned.
        """
        tid = _thread.get_ident()
        _blocking_on[tid] = self
        try:
            while True:
                with self.lock:
                    ikiwa self.count == 0 or self.owner == tid:
                        self.owner = tid
                        self.count += 1
                        rudisha True
                    ikiwa self.has_deadlock():
                        raise _DeadlockError('deadlock detected by %r' % self)
                    ikiwa self.wakeup.acquire(False):
                        self.waiters += 1
                # Wait for a release() call
                self.wakeup.acquire()
                self.wakeup.release()
        finally:
            del _blocking_on[tid]

    eleza release(self):
        tid = _thread.get_ident()
        with self.lock:
            ikiwa self.owner != tid:
                raise RuntimeError('cannot release un-acquired lock')
            assert self.count > 0
            self.count -= 1
            ikiwa self.count == 0:
                self.owner = None
                ikiwa self.waiters:
                    self.waiters -= 1
                    self.wakeup.release()

    eleza __repr__(self):
        rudisha '_ModuleLock({!r}) at {}'.format(self.name, id(self))


kundi _DummyModuleLock:
    """A simple _ModuleLock equivalent for Python builds without
    multi-threading support."""

    eleza __init__(self, name):
        self.name = name
        self.count = 0

    eleza acquire(self):
        self.count += 1
        rudisha True

    eleza release(self):
        ikiwa self.count == 0:
            raise RuntimeError('cannot release un-acquired lock')
        self.count -= 1

    eleza __repr__(self):
        rudisha '_DummyModuleLock({!r}) at {}'.format(self.name, id(self))


kundi _ModuleLockManager:

    eleza __init__(self, name):
        self._name = name
        self._lock = None

    eleza __enter__(self):
        self._lock = _get_module_lock(self._name)
        self._lock.acquire()

    eleza __exit__(self, *args, **kwargs):
        self._lock.release()


# The following two functions are for consumption by Python/agiza.c.

eleza _get_module_lock(name):
    """Get or create the module lock for a given module name.

    Acquire/release internally the global agiza lock to protect
    _module_locks."""

    _imp.acquire_lock()
    try:
        try:
            lock = _module_locks[name]()
        except KeyError:
            lock = None

        ikiwa lock is None:
            ikiwa _thread is None:
                lock = _DummyModuleLock(name)
            else:
                lock = _ModuleLock(name)

            eleza cb(ref, name=name):
                _imp.acquire_lock()
                try:
                    # bpo-31070: Check ikiwa another thread created a new lock
                    # after the previous lock was destroyed
                    # but before the weakref callback was called.
                    ikiwa _module_locks.get(name) is ref:
                        del _module_locks[name]
                finally:
                    _imp.release_lock()

            _module_locks[name] = _weakref.ref(lock, cb)
    finally:
        _imp.release_lock()

    rudisha lock


eleza _lock_unlock_module(name):
    """Acquires then releases the module lock for a given module name.

    This is used to ensure a module is completely initialized, in the
    event it is being imported by another thread.
    """
    lock = _get_module_lock(name)
    try:
        lock.acquire()
    except _DeadlockError:
        # Concurrent circular agiza, we'll accept a partially initialized
        # module object.
        pass
    else:
        lock.release()

# Frame stripping magic ###############################################
eleza _call_with_frames_removed(f, *args, **kwds):
    """remove_importlib_frames in agiza.c will always remove sequences
    of importlib frames that end with a call to this function

    Use it instead of a normal call in places where including the importlib
    frames introduces unwanted noise into the traceback (e.g. when executing
    module code)
    """
    rudisha f(*args, **kwds)


eleza _verbose_message(message, *args, verbosity=1):
    """Print the message to stderr ikiwa -v/PYTHONVERBOSE is turned on."""
    ikiwa sys.flags.verbose >= verbosity:
        ikiwa not message.startswith(('#', 'agiza ')):
            message = '# ' + message
        andika(message.format(*args), file=sys.stderr)


eleza _requires_builtin(fxn):
    """Decorator to verify the named module is built-in."""
    eleza _requires_builtin_wrapper(self, fullname):
        ikiwa fullname not in sys.builtin_module_names:
            raise ImportError('{!r} is not a built-in module'.format(fullname),
                              name=fullname)
        rudisha fxn(self, fullname)
    _wrap(_requires_builtin_wrapper, fxn)
    rudisha _requires_builtin_wrapper


eleza _requires_frozen(fxn):
    """Decorator to verify the named module is frozen."""
    eleza _requires_frozen_wrapper(self, fullname):
        ikiwa not _imp.is_frozen(fullname):
            raise ImportError('{!r} is not a frozen module'.format(fullname),
                              name=fullname)
        rudisha fxn(self, fullname)
    _wrap(_requires_frozen_wrapper, fxn)
    rudisha _requires_frozen_wrapper


# Typically used by loader classes as a method replacement.
eleza _load_module_shim(self, fullname):
    """Load the specified module into sys.modules and rudisha it.

    This method is deprecated.  Use loader.exec_module instead.

    """
    spec = spec_kutoka_loader(fullname, self)
    ikiwa fullname in sys.modules:
        module = sys.modules[fullname]
        _exec(spec, module)
        rudisha sys.modules[fullname]
    else:
        rudisha _load(spec)

# Module specifications #######################################################

eleza _module_repr(module):
    # The implementation of ModuleType.__repr__().
    loader = getattr(module, '__loader__', None)
    ikiwa hasattr(loader, 'module_repr'):
        # As soon as BuiltinImporter, FrozenImporter, and NamespaceLoader
        # drop their implementations for module_repr. we can add a
        # deprecation warning here.
        try:
            rudisha loader.module_repr(module)
        except Exception:
            pass
    try:
        spec = module.__spec__
    except AttributeError:
        pass
    else:
        ikiwa spec is not None:
            rudisha _module_repr_kutoka_spec(spec)

    # We could use module.__class__.__name__ instead of 'module' in the
    # various repr permutations.
    try:
        name = module.__name__
    except AttributeError:
        name = '?'
    try:
        filename = module.__file__
    except AttributeError:
        ikiwa loader is None:
            rudisha '<module {!r}>'.format(name)
        else:
            rudisha '<module {!r} ({!r})>'.format(name, loader)
    else:
        rudisha '<module {!r} kutoka {!r}>'.format(name, filename)


kundi ModuleSpec:
    """The specification for a module, used for loading.

    A module's spec is the source for information about the module.  For
    data associated with the module, including source, use the spec's
    loader.

    `name` is the absolute name of the module.  `loader` is the loader
    to use when loading the module.  `parent` is the name of the
    package the module is in.  The parent is derived kutoka the name.

    `is_package` determines ikiwa the module is considered a package or
    not.  On modules this is reflected by the `__path__` attribute.

    `origin` is the specific location used by the loader kutoka which to
    load the module, ikiwa that information is available.  When filename is
    set, origin will match.

    `has_location` indicates that a spec's "origin" reflects a location.
    When this is True, `__file__` attribute of the module is set.

    `cached` is the location of the cached bytecode file, ikiwa any.  It
    corresponds to the `__cached__` attribute.

    `submodule_search_locations` is the sequence of path entries to
    search when agizaing submodules.  If set, is_package should be
    True--and False otherwise.

    Packages are simply modules that (may) have submodules.  If a spec
    has a non-None value in `submodule_search_locations`, the agiza
    system will consider modules loaded kutoka the spec as packages.

    Only finders (see importlib.abc.MetaPathFinder and
    importlib.abc.PathEntryFinder) should modify ModuleSpec instances.

    """

    eleza __init__(self, name, loader, *, origin=None, loader_state=None,
                 is_package=None):
        self.name = name
        self.loader = loader
        self.origin = origin
        self.loader_state = loader_state
        self.submodule_search_locations = [] ikiwa is_package else None

        # file-location attributes
        self._set_fileattr = False
        self._cached = None

    eleza __repr__(self):
        args = ['name={!r}'.format(self.name),
                'loader={!r}'.format(self.loader)]
        ikiwa self.origin is not None:
            args.append('origin={!r}'.format(self.origin))
        ikiwa self.submodule_search_locations is not None:
            args.append('submodule_search_locations={}'
                        .format(self.submodule_search_locations))
        rudisha '{}({})'.format(self.__class__.__name__, ', '.join(args))

    eleza __eq__(self, other):
        smsl = self.submodule_search_locations
        try:
            rudisha (self.name == other.name and
                    self.loader == other.loader and
                    self.origin == other.origin and
                    smsl == other.submodule_search_locations and
                    self.cached == other.cached and
                    self.has_location == other.has_location)
        except AttributeError:
            rudisha False

    @property
    eleza cached(self):
        ikiwa self._cached is None:
            ikiwa self.origin is not None and self._set_fileattr:
                ikiwa _bootstrap_external is None:
                    raise NotImplementedError
                self._cached = _bootstrap_external._get_cached(self.origin)
        rudisha self._cached

    @cached.setter
    eleza cached(self, cached):
        self._cached = cached

    @property
    eleza parent(self):
        """The name of the module's parent."""
        ikiwa self.submodule_search_locations is None:
            rudisha self.name.rpartition('.')[0]
        else:
            rudisha self.name

    @property
    eleza has_location(self):
        rudisha self._set_fileattr

    @has_location.setter
    eleza has_location(self, value):
        self._set_fileattr = bool(value)


eleza spec_kutoka_loader(name, loader, *, origin=None, is_package=None):
    """Return a module spec based on various loader methods."""
    ikiwa hasattr(loader, 'get_filename'):
        ikiwa _bootstrap_external is None:
            raise NotImplementedError
        spec_kutoka_file_location = _bootstrap_external.spec_kutoka_file_location

        ikiwa is_package is None:
            rudisha spec_kutoka_file_location(name, loader=loader)
        search = [] ikiwa is_package else None
        rudisha spec_kutoka_file_location(name, loader=loader,
                                       submodule_search_locations=search)

    ikiwa is_package is None:
        ikiwa hasattr(loader, 'is_package'):
            try:
                is_package = loader.is_package(name)
            except ImportError:
                is_package = None  # aka, undefined
        else:
            # the default
            is_package = False

    rudisha ModuleSpec(name, loader, origin=origin, is_package=is_package)


eleza _spec_kutoka_module(module, loader=None, origin=None):
    # This function is meant for use in _setup().
    try:
        spec = module.__spec__
    except AttributeError:
        pass
    else:
        ikiwa spec is not None:
            rudisha spec

    name = module.__name__
    ikiwa loader is None:
        try:
            loader = module.__loader__
        except AttributeError:
            # loader will stay None.
            pass
    try:
        location = module.__file__
    except AttributeError:
        location = None
    ikiwa origin is None:
        ikiwa location is None:
            try:
                origin = loader._ORIGIN
            except AttributeError:
                origin = None
        else:
            origin = location
    try:
        cached = module.__cached__
    except AttributeError:
        cached = None
    try:
        submodule_search_locations = list(module.__path__)
    except AttributeError:
        submodule_search_locations = None

    spec = ModuleSpec(name, loader, origin=origin)
    spec._set_fileattr = False ikiwa location is None else True
    spec.cached = cached
    spec.submodule_search_locations = submodule_search_locations
    rudisha spec


eleza _init_module_attrs(spec, module, *, override=False):
    # The passed-in module may be not support attribute assignment,
    # in which case we simply don't set the attributes.
    # __name__
    ikiwa (override or getattr(module, '__name__', None) is None):
        try:
            module.__name__ = spec.name
        except AttributeError:
            pass
    # __loader__
    ikiwa override or getattr(module, '__loader__', None) is None:
        loader = spec.loader
        ikiwa loader is None:
            # A backward compatibility hack.
            ikiwa spec.submodule_search_locations is not None:
                ikiwa _bootstrap_external is None:
                    raise NotImplementedError
                _NamespaceLoader = _bootstrap_external._NamespaceLoader

                loader = _NamespaceLoader.__new__(_NamespaceLoader)
                loader._path = spec.submodule_search_locations
                spec.loader = loader
                # While the docs say that module.__file__ is not set for
                # built-in modules, and the code below will avoid setting it if
                # spec.has_location is false, this is incorrect for namespace
                # packages.  Namespace packages have no location, but their
                # __spec__.origin is None, and thus their module.__file__
                # should also be None for consistency.  While a bit of a hack,
                # this is the best place to ensure this consistency.
                #
                # See # https://docs.python.org/3/library/importlib.html#importlib.abc.Loader.load_module
                # and bpo-32305
                module.__file__ = None
        try:
            module.__loader__ = loader
        except AttributeError:
            pass
    # __package__
    ikiwa override or getattr(module, '__package__', None) is None:
        try:
            module.__package__ = spec.parent
        except AttributeError:
            pass
    # __spec__
    try:
        module.__spec__ = spec
    except AttributeError:
        pass
    # __path__
    ikiwa override or getattr(module, '__path__', None) is None:
        ikiwa spec.submodule_search_locations is not None:
            try:
                module.__path__ = spec.submodule_search_locations
            except AttributeError:
                pass
    # __file__/__cached__
    ikiwa spec.has_location:
        ikiwa override or getattr(module, '__file__', None) is None:
            try:
                module.__file__ = spec.origin
            except AttributeError:
                pass

        ikiwa override or getattr(module, '__cached__', None) is None:
            ikiwa spec.cached is not None:
                try:
                    module.__cached__ = spec.cached
                except AttributeError:
                    pass
    rudisha module


eleza module_kutoka_spec(spec):
    """Create a module based on the provided spec."""
    # Typically loaders will not implement create_module().
    module = None
    ikiwa hasattr(spec.loader, 'create_module'):
        # If create_module() returns `None` then it means default
        # module creation should be used.
        module = spec.loader.create_module(spec)
    elikiwa hasattr(spec.loader, 'exec_module'):
        raise ImportError('loaders that define exec_module() '
                          'must also define create_module()')
    ikiwa module is None:
        module = _new_module(spec.name)
    _init_module_attrs(spec, module)
    rudisha module


eleza _module_repr_kutoka_spec(spec):
    """Return the repr to use for the module."""
    # We mostly replicate _module_repr() using the spec attributes.
    name = '?' ikiwa spec.name is None else spec.name
    ikiwa spec.origin is None:
        ikiwa spec.loader is None:
            rudisha '<module {!r}>'.format(name)
        else:
            rudisha '<module {!r} ({!r})>'.format(name, spec.loader)
    else:
        ikiwa spec.has_location:
            rudisha '<module {!r} kutoka {!r}>'.format(name, spec.origin)
        else:
            rudisha '<module {!r} ({})>'.format(spec.name, spec.origin)


# Used by importlib.reload() and _load_module_shim().
eleza _exec(spec, module):
    """Execute the spec's specified module in an existing module's namespace."""
    name = spec.name
    with _ModuleLockManager(name):
        ikiwa sys.modules.get(name) is not module:
            msg = 'module {!r} not in sys.modules'.format(name)
            raise ImportError(msg, name=name)
        try:
            ikiwa spec.loader is None:
                ikiwa spec.submodule_search_locations is None:
                    raise ImportError('missing loader', name=spec.name)
                # Namespace package.
                _init_module_attrs(spec, module, override=True)
            else:
                _init_module_attrs(spec, module, override=True)
                ikiwa not hasattr(spec.loader, 'exec_module'):
                    # (issue19713) Once BuiltinImporter and ExtensionFileLoader
                    # have exec_module() implemented, we can add a deprecation
                    # warning here.
                    spec.loader.load_module(name)
                else:
                    spec.loader.exec_module(module)
        finally:
            # Update the order of insertion into sys.modules for module
            # clean-up at shutdown.
            module = sys.modules.pop(spec.name)
            sys.modules[spec.name] = module
    rudisha module


eleza _load_backward_compatible(spec):
    # (issue19713) Once BuiltinImporter and ExtensionFileLoader
    # have exec_module() implemented, we can add a deprecation
    # warning here.
    try:
        spec.loader.load_module(spec.name)
    except:
        ikiwa spec.name in sys.modules:
            module = sys.modules.pop(spec.name)
            sys.modules[spec.name] = module
        raise
    # The module must be in sys.modules at this point!
    # Move it to the end of sys.modules.
    module = sys.modules.pop(spec.name)
    sys.modules[spec.name] = module
    ikiwa getattr(module, '__loader__', None) is None:
        try:
            module.__loader__ = spec.loader
        except AttributeError:
            pass
    ikiwa getattr(module, '__package__', None) is None:
        try:
            # Since module.__path__ may not line up with
            # spec.submodule_search_paths, we can't necessarily rely
            # on spec.parent here.
            module.__package__ = module.__name__
            ikiwa not hasattr(module, '__path__'):
                module.__package__ = spec.name.rpartition('.')[0]
        except AttributeError:
            pass
    ikiwa getattr(module, '__spec__', None) is None:
        try:
            module.__spec__ = spec
        except AttributeError:
            pass
    rudisha module

eleza _load_unlocked(spec):
    # A helper for direct use by the agiza system.
    ikiwa spec.loader is not None:
        # Not a namespace package.
        ikiwa not hasattr(spec.loader, 'exec_module'):
            rudisha _load_backward_compatible(spec)

    module = module_kutoka_spec(spec)

    # This must be done before putting the module in sys.modules
    # (otherwise an optimization shortcut in agiza.c becomes
    # wrong).
    spec._initializing = True
    try:
        sys.modules[spec.name] = module
        try:
            ikiwa spec.loader is None:
                ikiwa spec.submodule_search_locations is None:
                    raise ImportError('missing loader', name=spec.name)
                # A namespace package so do nothing.
            else:
                spec.loader.exec_module(module)
        except:
            try:
                del sys.modules[spec.name]
            except KeyError:
                pass
            raise
        # Move the module to the end of sys.modules.
        # We don't ensure that the agiza-related module attributes get
        # set in the sys.modules replacement case.  Such modules are on
        # their own.
        module = sys.modules.pop(spec.name)
        sys.modules[spec.name] = module
        _verbose_message('agiza {!r} # {!r}', spec.name, spec.loader)
    finally:
        spec._initializing = False

    rudisha module

# A method used during testing of _load_unlocked() and by
# _load_module_shim().
eleza _load(spec):
    """Return a new module object, loaded by the spec's loader.

    The module is not added to its parent.

    If a module is already in sys.modules, that existing module gets
    clobbered.

    """
    with _ModuleLockManager(spec.name):
        rudisha _load_unlocked(spec)


# Loaders #####################################################################

kundi BuiltinImporter:

    """Meta path agiza for built-in modules.

    All methods are either kundi or static methods to avoid the need to
    instantiate the class.

    """

    @staticmethod
    eleza module_repr(module):
        """Return repr for the module.

        The method is deprecated.  The agiza machinery does the job itself.

        """
        rudisha '<module {!r} (built-in)>'.format(module.__name__)

    @classmethod
    eleza find_spec(cls, fullname, path=None, target=None):
        ikiwa path is not None:
            rudisha None
        ikiwa _imp.is_builtin(fullname):
            rudisha spec_kutoka_loader(fullname, cls, origin='built-in')
        else:
            rudisha None

    @classmethod
    eleza find_module(cls, fullname, path=None):
        """Find the built-in module.

        If 'path' is ever specified then the search is considered a failure.

        This method is deprecated.  Use find_spec() instead.

        """
        spec = cls.find_spec(fullname, path)
        rudisha spec.loader ikiwa spec is not None else None

    @classmethod
    eleza create_module(self, spec):
        """Create a built-in module"""
        ikiwa spec.name not in sys.builtin_module_names:
            raise ImportError('{!r} is not a built-in module'.format(spec.name),
                              name=spec.name)
        rudisha _call_with_frames_removed(_imp.create_builtin, spec)

    @classmethod
    eleza exec_module(self, module):
        """Exec a built-in module"""
        _call_with_frames_removed(_imp.exec_builtin, module)

    @classmethod
    @_requires_builtin
    eleza get_code(cls, fullname):
        """Return None as built-in modules do not have code objects."""
        rudisha None

    @classmethod
    @_requires_builtin
    eleza get_source(cls, fullname):
        """Return None as built-in modules do not have source code."""
        rudisha None

    @classmethod
    @_requires_builtin
    eleza is_package(cls, fullname):
        """Return False as built-in modules are never packages."""
        rudisha False

    load_module = classmethod(_load_module_shim)


kundi FrozenImporter:

    """Meta path agiza for frozen modules.

    All methods are either kundi or static methods to avoid the need to
    instantiate the class.

    """

    _ORIGIN = "frozen"

    @staticmethod
    eleza module_repr(m):
        """Return repr for the module.

        The method is deprecated.  The agiza machinery does the job itself.

        """
        rudisha '<module {!r} ({})>'.format(m.__name__, FrozenImporter._ORIGIN)

    @classmethod
    eleza find_spec(cls, fullname, path=None, target=None):
        ikiwa _imp.is_frozen(fullname):
            rudisha spec_kutoka_loader(fullname, cls, origin=cls._ORIGIN)
        else:
            rudisha None

    @classmethod
    eleza find_module(cls, fullname, path=None):
        """Find a frozen module.

        This method is deprecated.  Use find_spec() instead.

        """
        rudisha cls ikiwa _imp.is_frozen(fullname) else None

    @classmethod
    eleza create_module(cls, spec):
        """Use default semantics for module creation."""

    @staticmethod
    eleza exec_module(module):
        name = module.__spec__.name
        ikiwa not _imp.is_frozen(name):
            raise ImportError('{!r} is not a frozen module'.format(name),
                              name=name)
        code = _call_with_frames_removed(_imp.get_frozen_object, name)
        exec(code, module.__dict__)

    @classmethod
    eleza load_module(cls, fullname):
        """Load a frozen module.

        This method is deprecated.  Use exec_module() instead.

        """
        rudisha _load_module_shim(cls, fullname)

    @classmethod
    @_requires_frozen
    eleza get_code(cls, fullname):
        """Return the code object for the frozen module."""
        rudisha _imp.get_frozen_object(fullname)

    @classmethod
    @_requires_frozen
    eleza get_source(cls, fullname):
        """Return None as frozen modules do not have source code."""
        rudisha None

    @classmethod
    @_requires_frozen
    eleza is_package(cls, fullname):
        """Return True ikiwa the frozen module is a package."""
        rudisha _imp.is_frozen_package(fullname)


# Import itself ###############################################################

kundi _ImportLockContext:

    """Context manager for the agiza lock."""

    eleza __enter__(self):
        """Acquire the agiza lock."""
        _imp.acquire_lock()

    eleza __exit__(self, exc_type, exc_value, exc_traceback):
        """Release the agiza lock regardless of any raised exceptions."""
        _imp.release_lock()


eleza _resolve_name(name, package, level):
    """Resolve a relative module name to an absolute one."""
    bits = package.rsplit('.', level - 1)
    ikiwa len(bits) < level:
        raise ValueError('attempted relative agiza beyond top-level package')
    base = bits[0]
    rudisha '{}.{}'.format(base, name) ikiwa name else base


eleza _find_spec_legacy(finder, name, path):
    # This would be a good place for a DeprecationWarning if
    # we ended up going that route.
    loader = finder.find_module(name, path)
    ikiwa loader is None:
        rudisha None
    rudisha spec_kutoka_loader(name, loader)


eleza _find_spec(name, path, target=None):
    """Find a module's spec."""
    meta_path = sys.meta_path
    ikiwa meta_path is None:
        # PyImport_Cleanup() is running or has been called.
        raise ImportError("sys.meta_path is None, Python is likely "
                          "shutting down")

    ikiwa not meta_path:
        _warnings.warn('sys.meta_path is empty', ImportWarning)

    # We check sys.modules here for the reload case.  While a passed-in
    # target will usually indicate a reload there is no guarantee, whereas
    # sys.modules provides one.
    is_reload = name in sys.modules
    for finder in meta_path:
        with _ImportLockContext():
            try:
                find_spec = finder.find_spec
            except AttributeError:
                spec = _find_spec_legacy(finder, name, path)
                ikiwa spec is None:
                    continue
            else:
                spec = find_spec(name, path, target)
        ikiwa spec is not None:
            # The parent agiza may have already imported this module.
            ikiwa not is_reload and name in sys.modules:
                module = sys.modules[name]
                try:
                    __spec__ = module.__spec__
                except AttributeError:
                    # We use the found spec since that is the one that
                    # we would have used ikiwa the parent module hadn't
                    # beaten us to the punch.
                    rudisha spec
                else:
                    ikiwa __spec__ is None:
                        rudisha spec
                    else:
                        rudisha __spec__
            else:
                rudisha spec
    else:
        rudisha None


eleza _sanity_check(name, package, level):
    """Verify arguments are "sane"."""
    ikiwa not isinstance(name, str):
        raise TypeError('module name must be str, not {}'.format(type(name)))
    ikiwa level < 0:
        raise ValueError('level must be >= 0')
    ikiwa level > 0:
        ikiwa not isinstance(package, str):
            raise TypeError('__package__ not set to a string')
        elikiwa not package:
            raise ImportError('attempted relative agiza with no known parent '
                              'package')
    ikiwa not name and level == 0:
        raise ValueError('Empty module name')


_ERR_MSG_PREFIX = 'No module named '
_ERR_MSG = _ERR_MSG_PREFIX + '{!r}'

eleza _find_and_load_unlocked(name, import_):
    path = None
    parent = name.rpartition('.')[0]
    ikiwa parent:
        ikiwa parent not in sys.modules:
            _call_with_frames_removed(import_, parent)
        # Crazy side-effects!
        ikiwa name in sys.modules:
            rudisha sys.modules[name]
        parent_module = sys.modules[parent]
        try:
            path = parent_module.__path__
        except AttributeError:
            msg = (_ERR_MSG + '; {!r} is not a package').format(name, parent)
            raise ModuleNotFoundError(msg, name=name) kutoka None
    spec = _find_spec(name, path)
    ikiwa spec is None:
        raise ModuleNotFoundError(_ERR_MSG.format(name), name=name)
    else:
        module = _load_unlocked(spec)
    ikiwa parent:
        # Set the module as an attribute on its parent.
        parent_module = sys.modules[parent]
        setattr(parent_module, name.rpartition('.')[2], module)
    rudisha module


_NEEDS_LOADING = object()


eleza _find_and_load(name, import_):
    """Find and load the module."""
    with _ModuleLockManager(name):
        module = sys.modules.get(name, _NEEDS_LOADING)
        ikiwa module is _NEEDS_LOADING:
            rudisha _find_and_load_unlocked(name, import_)

    ikiwa module is None:
        message = ('agiza of {} halted; '
                   'None in sys.modules'.format(name))
        raise ModuleNotFoundError(message, name=name)

    _lock_unlock_module(name)
    rudisha module


eleza _gcd_agiza(name, package=None, level=0):
    """Import and rudisha the module based on its name, the package the call is
    being made kutoka, and the level adjustment.

    This function represents the greatest common denominator of functionality
    between import_module and __import__. This includes setting __package__ if
    the loader did not.

    """
    _sanity_check(name, package, level)
    ikiwa level > 0:
        name = _resolve_name(name, package, level)
    rudisha _find_and_load(name, _gcd_agiza)


eleza _handle_kutokalist(module, kutokalist, import_, *, recursive=False):
    """Figure out what __import__ should return.

    The import_ parameter is a callable which takes the name of module to
    agiza. It is required to decouple the function kutoka assuming importlib's
    agiza implementation is desired.

    """
    # The hell that is kutokalist ...
    # If a package was imported, try to agiza stuff kutoka kutokalist.
    for x in kutokalist:
        ikiwa not isinstance(x, str):
            ikiwa recursive:
                where = module.__name__ + '.__all__'
            else:
                where = "``kutoka list''"
            raise TypeError(f"Item in {where} must be str, "
                            f"not {type(x).__name__}")
        elikiwa x == '*':
            ikiwa not recursive and hasattr(module, '__all__'):
                _handle_kutokalist(module, module.__all__, import_,
                                 recursive=True)
        elikiwa not hasattr(module, x):
            kutoka_name = '{}.{}'.format(module.__name__, x)
            try:
                _call_with_frames_removed(import_, kutoka_name)
            except ModuleNotFoundError as exc:
                # Backwards-compatibility dictates we ignore failed
                # agizas triggered by kutokalist for modules that don't
                # exist.
                ikiwa (exc.name == kutoka_name and
                    sys.modules.get(kutoka_name, _NEEDS_LOADING) is not None):
                    continue
                raise
    rudisha module


eleza _calc___package__(globals):
    """Calculate what __package__ should be.

    __package__ is not guaranteed to be defined or could be set to None
    to represent that its proper value is unknown.

    """
    package = globals.get('__package__')
    spec = globals.get('__spec__')
    ikiwa package is not None:
        ikiwa spec is not None and package != spec.parent:
            _warnings.warn("__package__ != __spec__.parent "
                           f"({package!r} != {spec.parent!r})",
                           ImportWarning, stacklevel=3)
        rudisha package
    elikiwa spec is not None:
        rudisha spec.parent
    else:
        _warnings.warn("can't resolve package kutoka __spec__ or __package__, "
                       "falling back on __name__ and __path__",
                       ImportWarning, stacklevel=3)
        package = globals['__name__']
        ikiwa '__path__' not in globals:
            package = package.rpartition('.')[0]
    rudisha package


eleza __import__(name, globals=None, locals=None, kutokalist=(), level=0):
    """Import a module.

    The 'globals' argument is used to infer where the agiza is occurring kutoka
    to handle relative agizas. The 'locals' argument is ignored. The
    'kutokalist' argument specifies what should exist as attributes on the module
    being imported (e.g. ``kutoka module agiza <kutokalist>``).  The 'level'
    argument represents the package location to agiza kutoka in a relative
    agiza (e.g. ``kutoka ..pkg agiza mod`` would have a 'level' of 2).

    """
    ikiwa level == 0:
        module = _gcd_agiza(name)
    else:
        globals_ = globals ikiwa globals is not None else {}
        package = _calc___package__(globals_)
        module = _gcd_agiza(name, package, level)
    ikiwa not kutokalist:
        # Return up to the first dot in 'name'. This is complicated by the fact
        # that 'name' may be relative.
        ikiwa level == 0:
            rudisha _gcd_agiza(name.partition('.')[0])
        elikiwa not name:
            rudisha module
        else:
            # Figure out where to slice the module's name up to the first dot
            # in 'name'.
            cut_off = len(name) - len(name.partition('.')[0])
            # Slice end needs to be positive to alleviate need to special-case
            # when ``'.' not in name``.
            rudisha sys.modules[module.__name__[:len(module.__name__)-cut_off]]
    elikiwa hasattr(module, '__path__'):
        rudisha _handle_kutokalist(module, kutokalist, _gcd_agiza)
    else:
        rudisha module


eleza _builtin_kutoka_name(name):
    spec = BuiltinImporter.find_spec(name)
    ikiwa spec is None:
        raise ImportError('no built-in module named ' + name)
    rudisha _load_unlocked(spec)


eleza _setup(sys_module, _imp_module):
    """Setup importlib by agizaing needed built-in modules and injecting them
    into the global namespace.

    As sys is needed for sys.modules access and _imp is needed to load built-in
    modules, those two modules must be explicitly passed in.

    """
    global _imp, sys
    _imp = _imp_module
    sys = sys_module

    # Set up the spec for existing builtin/frozen modules.
    module_type = type(sys)
    for name, module in sys.modules.items():
        ikiwa isinstance(module, module_type):
            ikiwa name in sys.builtin_module_names:
                loader = BuiltinImporter
            elikiwa _imp.is_frozen(name):
                loader = FrozenImporter
            else:
                continue
            spec = _spec_kutoka_module(module, loader)
            _init_module_attrs(spec, module)

    # Directly load built-in modules needed during bootstrap.
    self_module = sys.modules[__name__]
    for builtin_name in ('_thread', '_warnings', '_weakref'):
        ikiwa builtin_name not in sys.modules:
            builtin_module = _builtin_kutoka_name(builtin_name)
        else:
            builtin_module = sys.modules[builtin_name]
        setattr(self_module, builtin_name, builtin_module)


eleza _install(sys_module, _imp_module):
    """Install importers for builtin and frozen modules"""
    _setup(sys_module, _imp_module)

    sys.meta_path.append(BuiltinImporter)
    sys.meta_path.append(FrozenImporter)


eleza _install_external_importers():
    """Install importers that require external filesystem access"""
    global _bootstrap_external
    agiza _frozen_importlib_external
    _bootstrap_external = _frozen_importlib_external
    _frozen_importlib_external._install(sys.modules[__name__])
