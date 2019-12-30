"""Core implementation of import.

This module ni NOT meant to be directly imported! It has been designed such
that it can be bootstrapped into Python as the implementation of import. As
such it requires the injection of specific modules na attributes kwenye order to
work. One should use importlib as the public-facing version of this module.

"""
#
# IMPORTANT: Whenever making changes to this module, be sure to run a top-level
# `make regen-importlib` followed by `make` kwenye order to get the frozen version
# of the module updated. Not doing so will result kwenye the Makefile to fail for
# all others who don't have a ./python around to freeze the module
# kwenye the early stages of compilation.
#

# See importlib._setup() kila what ni injected into the global namespace.

# When editing this code be aware that code executed at agiza time CANNOT
# reference any injected objects! This includes sio only global code but also
# anything specified at the kundi level.

# Bootstrap-related code ######################################################

_bootstrap_external = Tupu

eleza _wrap(new, old):
    """Simple substitute kila functools.update_wrapper."""
    kila replace kwenye ['__module__', '__name__', '__qualname__', '__doc__']:
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
    """A recursive lock implementation which ni able to detect deadlocks
    (e.g. thread 1 trying to take locks A then B, na thread 2 trying to
    take locks B then A).
    """

    eleza __init__(self, name):
        self.lock = _thread.allocate_lock()
        self.wakeup = _thread.allocate_lock()
        self.name = name
        self.owner = Tupu
        self.count = 0
        self.waiters = 0

    eleza has_deadlock(self):
        # Deadlock avoidance kila concurrent circular imports.
        me = _thread.get_ident()
        tid = self.owner
        wakati Kweli:
            lock = _blocking_on.get(tid)
            ikiwa lock ni Tupu:
                rudisha Uongo
            tid = lock.owner
            ikiwa tid == me:
                rudisha Kweli

    eleza acquire(self):
        """
        Acquire the module lock.  If a potential deadlock ni detected,
        a _DeadlockError ni raised.
        Otherwise, the lock ni always acquired na Kweli ni returned.
        """
        tid = _thread.get_ident()
        _blocking_on[tid] = self
        jaribu:
            wakati Kweli:
                ukijumuisha self.lock:
                    ikiwa self.count == 0 ama self.owner == tid:
                        self.owner = tid
                        self.count += 1
                        rudisha Kweli
                    ikiwa self.has_deadlock():
                         ashiria _DeadlockError('deadlock detected by %r' % self)
                    ikiwa self.wakeup.acquire(Uongo):
                        self.waiters += 1
                # Wait kila a release() call
                self.wakeup.acquire()
                self.wakeup.release()
        mwishowe:
            toa _blocking_on[tid]

    eleza release(self):
        tid = _thread.get_ident()
        ukijumuisha self.lock:
            ikiwa self.owner != tid:
                 ashiria RuntimeError('cannot release un-acquired lock')
            assert self.count > 0
            self.count -= 1
            ikiwa self.count == 0:
                self.owner = Tupu
                ikiwa self.waiters:
                    self.waiters -= 1
                    self.wakeup.release()

    eleza __repr__(self):
        rudisha '_ModuleLock({!r}) at {}'.format(self.name, id(self))


kundi _DummyModuleLock:
    """A simple _ModuleLock equivalent kila Python builds without
    multi-threading support."""

    eleza __init__(self, name):
        self.name = name
        self.count = 0

    eleza acquire(self):
        self.count += 1
        rudisha Kweli

    eleza release(self):
        ikiwa self.count == 0:
             ashiria RuntimeError('cannot release un-acquired lock')
        self.count -= 1

    eleza __repr__(self):
        rudisha '_DummyModuleLock({!r}) at {}'.format(self.name, id(self))


kundi _ModuleLockManager:

    eleza __init__(self, name):
        self._name = name
        self._lock = Tupu

    eleza __enter__(self):
        self._lock = _get_module_lock(self._name)
        self._lock.acquire()

    eleza __exit__(self, *args, **kwargs):
        self._lock.release()


# The following two functions are kila consumption by Python/import.c.

eleza _get_module_lock(name):
    """Get ama create the module lock kila a given module name.

    Acquire/release internally the global agiza lock to protect
    _module_locks."""

    _imp.acquire_lock()
    jaribu:
        jaribu:
            lock = _module_locks[name]()
        except KeyError:
            lock = Tupu

        ikiwa lock ni Tupu:
            ikiwa _thread ni Tupu:
                lock = _DummyModuleLock(name)
            isipokua:
                lock = _ModuleLock(name)

            eleza cb(ref, name=name):
                _imp.acquire_lock()
                jaribu:
                    # bpo-31070: Check ikiwa another thread created a new lock
                    # after the previous lock was destroyed
                    # but before the weakref callback was called.
                    ikiwa _module_locks.get(name) ni ref:
                        toa _module_locks[name]
                mwishowe:
                    _imp.release_lock()

            _module_locks[name] = _weakref.ref(lock, cb)
    mwishowe:
        _imp.release_lock()

    rudisha lock


eleza _lock_unlock_module(name):
    """Acquires then releases the module lock kila a given module name.

    This ni used to ensure a module ni completely initialized, kwenye the
    event it ni being imported by another thread.
    """
    lock = _get_module_lock(name)
    jaribu:
        lock.acquire()
    except _DeadlockError:
        # Concurrent circular import, we'll accept a partially initialized
        # module object.
        pass
    isipokua:
        lock.release()

# Frame stripping magic ###############################################
eleza _call_with_frames_removed(f, *args, **kwds):
    """remove_importlib_frames kwenye import.c will always remove sequences
    of importlib frames that end ukijumuisha a call to this function

    Use it instead of a normal call kwenye places where including the importlib
    frames introduces unwanted noise into the traceback (e.g. when executing
    module code)
    """
    rudisha f(*args, **kwds)


eleza _verbose_message(message, *args, verbosity=1):
    """Print the message to stderr ikiwa -v/PYTHONVERBOSE ni turned on."""
    ikiwa sys.flags.verbose >= verbosity:
        ikiwa sio message.startswith(('#', 'agiza ')):
            message = '# ' + message
        andika(message.format(*args), file=sys.stderr)


eleza _requires_builtin(fxn):
    """Decorator to verify the named module ni built-in."""
    eleza _requires_builtin_wrapper(self, fullname):
        ikiwa fullname sio kwenye sys.builtin_module_names:
             ashiria ImportError('{!r} ni sio a built-in module'.format(fullname),
                              name=fullname)
        rudisha fxn(self, fullname)
    _wrap(_requires_builtin_wrapper, fxn)
    rudisha _requires_builtin_wrapper


eleza _requires_frozen(fxn):
    """Decorator to verify the named module ni frozen."""
    eleza _requires_frozen_wrapper(self, fullname):
        ikiwa sio _imp.is_frozen(fullname):
             ashiria ImportError('{!r} ni sio a frozen module'.format(fullname),
                              name=fullname)
        rudisha fxn(self, fullname)
    _wrap(_requires_frozen_wrapper, fxn)
    rudisha _requires_frozen_wrapper


# Typically used by loader classes as a method replacement.
eleza _load_module_shim(self, fullname):
    """Load the specified module into sys.modules na rudisha it.

    This method ni deprecated.  Use loader.exec_module instead.

    """
    spec = spec_from_loader(fullname, self)
    ikiwa fullname kwenye sys.modules:
        module = sys.modules[fullname]
        _exec(spec, module)
        rudisha sys.modules[fullname]
    isipokua:
        rudisha _load(spec)

# Module specifications #######################################################

eleza _module_repr(module):
    # The implementation of ModuleType.__repr__().
    loader = getattr(module, '__loader__', Tupu)
    ikiwa hasattr(loader, 'module_repr'):
        # As soon as BuiltinImporter, FrozenImporter, na NamespaceLoader
        # drop their implementations kila module_repr. we can add a
        # deprecation warning here.
        jaribu:
            rudisha loader.module_repr(module)
        except Exception:
            pass
    jaribu:
        spec = module.__spec__
    except AttributeError:
        pass
    isipokua:
        ikiwa spec ni sio Tupu:
            rudisha _module_repr_from_spec(spec)

    # We could use module.__class__.__name__ instead of 'module' kwenye the
    # various repr permutations.
    jaribu:
        name = module.__name__
    except AttributeError:
        name = '?'
    jaribu:
        filename = module.__file__
    except AttributeError:
        ikiwa loader ni Tupu:
            rudisha '<module {!r}>'.format(name)
        isipokua:
            rudisha '<module {!r} ({!r})>'.format(name, loader)
    isipokua:
        rudisha '<module {!r} kutoka {!r}>'.format(name, filename)


kundi ModuleSpec:
    """The specification kila a module, used kila loading.

    A module's spec ni the source kila information about the module.  For
    data associated ukijumuisha the module, including source, use the spec's
    loader.

    `name` ni the absolute name of the module.  `loader` ni the loader
    to use when loading the module.  `parent` ni the name of the
    package the module ni in.  The parent ni derived kutoka the name.

    `is_package` determines ikiwa the module ni considered a package or
    not.  On modules this ni reflected by the `__path__` attribute.

    `origin` ni the specific location used by the loader kutoka which to
    load the module, ikiwa that information ni available.  When filename is
    set, origin will match.

    `has_location` indicates that a spec's "origin" reflects a location.
    When this ni Kweli, `__file__` attribute of the module ni set.

    `cached` ni the location of the cached bytecode file, ikiwa any.  It
    corresponds to the `__cached__` attribute.

    `submodule_search_locations` ni the sequence of path entries to
    search when importing submodules.  If set, is_package should be
    Kweli--and Uongo otherwise.

    Packages are simply modules that (may) have submodules.  If a spec
    has a non-Tupu value kwenye `submodule_search_locations`, the import
    system will consider modules loaded kutoka the spec as packages.

    Only finders (see importlib.abc.MetaPathFinder and
    importlib.abc.PathEntryFinder) should modify ModuleSpec instances.

    """

    eleza __init__(self, name, loader, *, origin=Tupu, loader_state=Tupu,
                 is_package=Tupu):
        self.name = name
        self.loader = loader
        self.origin = origin
        self.loader_state = loader_state
        self.submodule_search_locations = [] ikiwa is_package isipokua Tupu

        # file-location attributes
        self._set_fileattr = Uongo
        self._cached = Tupu

    eleza __repr__(self):
        args = ['name={!r}'.format(self.name),
                'loader={!r}'.format(self.loader)]
        ikiwa self.origin ni sio Tupu:
            args.append('origin={!r}'.format(self.origin))
        ikiwa self.submodule_search_locations ni sio Tupu:
            args.append('submodule_search_locations={}'
                        .format(self.submodule_search_locations))
        rudisha '{}({})'.format(self.__class__.__name__, ', '.join(args))

    eleza __eq__(self, other):
        smsl = self.submodule_search_locations
        jaribu:
            rudisha (self.name == other.name and
                    self.loader == other.loader and
                    self.origin == other.origin and
                    smsl == other.submodule_search_locations and
                    self.cached == other.cached and
                    self.has_location == other.has_location)
        except AttributeError:
            rudisha Uongo

    @property
    eleza cached(self):
        ikiwa self._cached ni Tupu:
            ikiwa self.origin ni sio Tupu na self._set_fileattr:
                ikiwa _bootstrap_external ni Tupu:
                     ashiria NotImplementedError
                self._cached = _bootstrap_external._get_cached(self.origin)
        rudisha self._cached

    @cached.setter
    eleza cached(self, cached):
        self._cached = cached

    @property
    eleza parent(self):
        """The name of the module's parent."""
        ikiwa self.submodule_search_locations ni Tupu:
            rudisha self.name.rpartition('.')[0]
        isipokua:
            rudisha self.name

    @property
    eleza has_location(self):
        rudisha self._set_fileattr

    @has_location.setter
    eleza has_location(self, value):
        self._set_fileattr = bool(value)


eleza spec_from_loader(name, loader, *, origin=Tupu, is_package=Tupu):
    """Return a module spec based on various loader methods."""
    ikiwa hasattr(loader, 'get_filename'):
        ikiwa _bootstrap_external ni Tupu:
             ashiria NotImplementedError
        spec_from_file_location = _bootstrap_external.spec_from_file_location

        ikiwa is_package ni Tupu:
            rudisha spec_from_file_location(name, loader=loader)
        search = [] ikiwa is_package isipokua Tupu
        rudisha spec_from_file_location(name, loader=loader,
                                       submodule_search_locations=search)

    ikiwa is_package ni Tupu:
        ikiwa hasattr(loader, 'is_package'):
            jaribu:
                is_package = loader.is_package(name)
            except ImportError:
                is_package = Tupu  # aka, undefined
        isipokua:
            # the default
            is_package = Uongo

    rudisha ModuleSpec(name, loader, origin=origin, is_package=is_package)


eleza _spec_from_module(module, loader=Tupu, origin=Tupu):
    # This function ni meant kila use kwenye _setup().
    jaribu:
        spec = module.__spec__
    except AttributeError:
        pass
    isipokua:
        ikiwa spec ni sio Tupu:
            rudisha spec

    name = module.__name__
    ikiwa loader ni Tupu:
        jaribu:
            loader = module.__loader__
        except AttributeError:
            # loader will stay Tupu.
            pass
    jaribu:
        location = module.__file__
    except AttributeError:
        location = Tupu
    ikiwa origin ni Tupu:
        ikiwa location ni Tupu:
            jaribu:
                origin = loader._ORIGIN
            except AttributeError:
                origin = Tupu
        isipokua:
            origin = location
    jaribu:
        cached = module.__cached__
    except AttributeError:
        cached = Tupu
    jaribu:
        submodule_search_locations = list(module.__path__)
    except AttributeError:
        submodule_search_locations = Tupu

    spec = ModuleSpec(name, loader, origin=origin)
    spec._set_fileattr = Uongo ikiwa location ni Tupu isipokua Kweli
    spec.cached = cached
    spec.submodule_search_locations = submodule_search_locations
    rudisha spec


eleza _init_module_attrs(spec, module, *, override=Uongo):
    # The passed-in module may be sio support attribute assignment,
    # kwenye which case we simply don't set the attributes.
    # __name__
    ikiwa (override ama getattr(module, '__name__', Tupu) ni Tupu):
        jaribu:
            module.__name__ = spec.name
        except AttributeError:
            pass
    # __loader__
    ikiwa override ama getattr(module, '__loader__', Tupu) ni Tupu:
        loader = spec.loader
        ikiwa loader ni Tupu:
            # A backward compatibility hack.
            ikiwa spec.submodule_search_locations ni sio Tupu:
                ikiwa _bootstrap_external ni Tupu:
                     ashiria NotImplementedError
                _NamespaceLoader = _bootstrap_external._NamespaceLoader

                loader = _NamespaceLoader.__new__(_NamespaceLoader)
                loader._path = spec.submodule_search_locations
                spec.loader = loader
                # While the docs say that module.__file__ ni sio set for
                # built-in modules, na the code below will avoid setting it if
                # spec.has_location ni false, this ni incorrect kila namespace
                # packages.  Namespace packages have no location, but their
                # __spec__.origin ni Tupu, na thus their module.__file__
                # should also be Tupu kila consistency.  While a bit of a hack,
                # this ni the best place to ensure this consistency.
                #
                # See # https://docs.python.org/3/library/importlib.html#importlib.abc.Loader.load_module
                # na bpo-32305
                module.__file__ = Tupu
        jaribu:
            module.__loader__ = loader
        except AttributeError:
            pass
    # __package__
    ikiwa override ama getattr(module, '__package__', Tupu) ni Tupu:
        jaribu:
            module.__package__ = spec.parent
        except AttributeError:
            pass
    # __spec__
    jaribu:
        module.__spec__ = spec
    except AttributeError:
        pass
    # __path__
    ikiwa override ama getattr(module, '__path__', Tupu) ni Tupu:
        ikiwa spec.submodule_search_locations ni sio Tupu:
            jaribu:
                module.__path__ = spec.submodule_search_locations
            except AttributeError:
                pass
    # __file__/__cached__
    ikiwa spec.has_location:
        ikiwa override ama getattr(module, '__file__', Tupu) ni Tupu:
            jaribu:
                module.__file__ = spec.origin
            except AttributeError:
                pass

        ikiwa override ama getattr(module, '__cached__', Tupu) ni Tupu:
            ikiwa spec.cached ni sio Tupu:
                jaribu:
                    module.__cached__ = spec.cached
                except AttributeError:
                    pass
    rudisha module


eleza module_from_spec(spec):
    """Create a module based on the provided spec."""
    # Typically loaders will sio implement create_module().
    module = Tupu
    ikiwa hasattr(spec.loader, 'create_module'):
        # If create_module() returns `Tupu` then it means default
        # module creation should be used.
        module = spec.loader.create_module(spec)
    elikiwa hasattr(spec.loader, 'exec_module'):
         ashiria ImportError('loaders that define exec_module() '
                          'must also define create_module()')
    ikiwa module ni Tupu:
        module = _new_module(spec.name)
    _init_module_attrs(spec, module)
    rudisha module


eleza _module_repr_from_spec(spec):
    """Return the repr to use kila the module."""
    # We mostly replicate _module_repr() using the spec attributes.
    name = '?' ikiwa spec.name ni Tupu isipokua spec.name
    ikiwa spec.origin ni Tupu:
        ikiwa spec.loader ni Tupu:
            rudisha '<module {!r}>'.format(name)
        isipokua:
            rudisha '<module {!r} ({!r})>'.format(name, spec.loader)
    isipokua:
        ikiwa spec.has_location:
            rudisha '<module {!r} kutoka {!r}>'.format(name, spec.origin)
        isipokua:
            rudisha '<module {!r} ({})>'.format(spec.name, spec.origin)


# Used by importlib.reload() na _load_module_shim().
eleza _exec(spec, module):
    """Execute the spec's specified module kwenye an existing module's namespace."""
    name = spec.name
    ukijumuisha _ModuleLockManager(name):
        ikiwa sys.modules.get(name) ni sio module:
            msg = 'module {!r} sio kwenye sys.modules'.format(name)
             ashiria ImportError(msg, name=name)
        jaribu:
            ikiwa spec.loader ni Tupu:
                ikiwa spec.submodule_search_locations ni Tupu:
                     ashiria ImportError('missing loader', name=spec.name)
                # Namespace package.
                _init_module_attrs(spec, module, override=Kweli)
            isipokua:
                _init_module_attrs(spec, module, override=Kweli)
                ikiwa sio hasattr(spec.loader, 'exec_module'):
                    # (issue19713) Once BuiltinImporter na ExtensionFileLoader
                    # have exec_module() implemented, we can add a deprecation
                    # warning here.
                    spec.loader.load_module(name)
                isipokua:
                    spec.loader.exec_module(module)
        mwishowe:
            # Update the order of insertion into sys.modules kila module
            # clean-up at shutdown.
            module = sys.modules.pop(spec.name)
            sys.modules[spec.name] = module
    rudisha module


eleza _load_backward_compatible(spec):
    # (issue19713) Once BuiltinImporter na ExtensionFileLoader
    # have exec_module() implemented, we can add a deprecation
    # warning here.
    jaribu:
        spec.loader.load_module(spec.name)
    tatizo:
        ikiwa spec.name kwenye sys.modules:
            module = sys.modules.pop(spec.name)
            sys.modules[spec.name] = module
        raise
    # The module must be kwenye sys.modules at this point!
    # Move it to the end of sys.modules.
    module = sys.modules.pop(spec.name)
    sys.modules[spec.name] = module
    ikiwa getattr(module, '__loader__', Tupu) ni Tupu:
        jaribu:
            module.__loader__ = spec.loader
        except AttributeError:
            pass
    ikiwa getattr(module, '__package__', Tupu) ni Tupu:
        jaribu:
            # Since module.__path__ may sio line up with
            # spec.submodule_search_paths, we can't necessarily rely
            # on spec.parent here.
            module.__package__ = module.__name__
            ikiwa sio hasattr(module, '__path__'):
                module.__package__ = spec.name.rpartition('.')[0]
        except AttributeError:
            pass
    ikiwa getattr(module, '__spec__', Tupu) ni Tupu:
        jaribu:
            module.__spec__ = spec
        except AttributeError:
            pass
    rudisha module

eleza _load_unlocked(spec):
    # A helper kila direct use by the agiza system.
    ikiwa spec.loader ni sio Tupu:
        # Not a namespace package.
        ikiwa sio hasattr(spec.loader, 'exec_module'):
            rudisha _load_backward_compatible(spec)

    module = module_from_spec(spec)

    # This must be done before putting the module kwenye sys.modules
    # (otherwise an optimization shortcut kwenye import.c becomes
    # wrong).
    spec._initializing = Kweli
    jaribu:
        sys.modules[spec.name] = module
        jaribu:
            ikiwa spec.loader ni Tupu:
                ikiwa spec.submodule_search_locations ni Tupu:
                     ashiria ImportError('missing loader', name=spec.name)
                # A namespace package so do nothing.
            isipokua:
                spec.loader.exec_module(module)
        tatizo:
            jaribu:
                toa sys.modules[spec.name]
            except KeyError:
                pass
            raise
        # Move the module to the end of sys.modules.
        # We don't ensure that the import-related module attributes get
        # set kwenye the sys.modules replacement case.  Such modules are on
        # their own.
        module = sys.modules.pop(spec.name)
        sys.modules[spec.name] = module
        _verbose_message('agiza {!r} # {!r}', spec.name, spec.loader)
    mwishowe:
        spec._initializing = Uongo

    rudisha module

# A method used during testing of _load_unlocked() na by
# _load_module_shim().
eleza _load(spec):
    """Return a new module object, loaded by the spec's loader.

    The module ni sio added to its parent.

    If a module ni already kwenye sys.modules, that existing module gets
    clobbered.

    """
    ukijumuisha _ModuleLockManager(spec.name):
        rudisha _load_unlocked(spec)


# Loaders #####################################################################

kundi BuiltinImporter:

    """Meta path agiza kila built-in modules.

    All methods are either kundi ama static methods to avoid the need to
    instantiate the class.

    """

    @staticmethod
    eleza module_repr(module):
        """Return repr kila the module.

        The method ni deprecated.  The agiza machinery does the job itself.

        """
        rudisha '<module {!r} (built-in)>'.format(module.__name__)

    @classmethod
    eleza find_spec(cls, fullname, path=Tupu, target=Tupu):
        ikiwa path ni sio Tupu:
            rudisha Tupu
        ikiwa _imp.is_builtin(fullname):
            rudisha spec_from_loader(fullname, cls, origin='built-in')
        isipokua:
            rudisha Tupu

    @classmethod
    eleza find_module(cls, fullname, path=Tupu):
        """Find the built-in module.

        If 'path' ni ever specified then the search ni considered a failure.

        This method ni deprecated.  Use find_spec() instead.

        """
        spec = cls.find_spec(fullname, path)
        rudisha spec.loader ikiwa spec ni sio Tupu isipokua Tupu

    @classmethod
    eleza create_module(self, spec):
        """Create a built-in module"""
        ikiwa spec.name sio kwenye sys.builtin_module_names:
             ashiria ImportError('{!r} ni sio a built-in module'.format(spec.name),
                              name=spec.name)
        rudisha _call_with_frames_removed(_imp.create_builtin, spec)

    @classmethod
    eleza exec_module(self, module):
        """Exec a built-in module"""
        _call_with_frames_removed(_imp.exec_builtin, module)

    @classmethod
    @_requires_builtin
    eleza get_code(cls, fullname):
        """Return Tupu as built-in modules do sio have code objects."""
        rudisha Tupu

    @classmethod
    @_requires_builtin
    eleza get_source(cls, fullname):
        """Return Tupu as built-in modules do sio have source code."""
        rudisha Tupu

    @classmethod
    @_requires_builtin
    eleza is_package(cls, fullname):
        """Return Uongo as built-in modules are never packages."""
        rudisha Uongo

    load_module = classmethod(_load_module_shim)


kundi FrozenImporter:

    """Meta path agiza kila frozen modules.

    All methods are either kundi ama static methods to avoid the need to
    instantiate the class.

    """

    _ORIGIN = "frozen"

    @staticmethod
    eleza module_repr(m):
        """Return repr kila the module.

        The method ni deprecated.  The agiza machinery does the job itself.

        """
        rudisha '<module {!r} ({})>'.format(m.__name__, FrozenImporter._ORIGIN)

    @classmethod
    eleza find_spec(cls, fullname, path=Tupu, target=Tupu):
        ikiwa _imp.is_frozen(fullname):
            rudisha spec_from_loader(fullname, cls, origin=cls._ORIGIN)
        isipokua:
            rudisha Tupu

    @classmethod
    eleza find_module(cls, fullname, path=Tupu):
        """Find a frozen module.

        This method ni deprecated.  Use find_spec() instead.

        """
        rudisha cls ikiwa _imp.is_frozen(fullname) isipokua Tupu

    @classmethod
    eleza create_module(cls, spec):
        """Use default semantics kila module creation."""

    @staticmethod
    eleza exec_module(module):
        name = module.__spec__.name
        ikiwa sio _imp.is_frozen(name):
             ashiria ImportError('{!r} ni sio a frozen module'.format(name),
                              name=name)
        code = _call_with_frames_removed(_imp.get_frozen_object, name)
        exec(code, module.__dict__)

    @classmethod
    eleza load_module(cls, fullname):
        """Load a frozen module.

        This method ni deprecated.  Use exec_module() instead.

        """
        rudisha _load_module_shim(cls, fullname)

    @classmethod
    @_requires_frozen
    eleza get_code(cls, fullname):
        """Return the code object kila the frozen module."""
        rudisha _imp.get_frozen_object(fullname)

    @classmethod
    @_requires_frozen
    eleza get_source(cls, fullname):
        """Return Tupu as frozen modules do sio have source code."""
        rudisha Tupu

    @classmethod
    @_requires_frozen
    eleza is_package(cls, fullname):
        """Return Kweli ikiwa the frozen module ni a package."""
        rudisha _imp.is_frozen_package(fullname)


# Import itself ###############################################################

kundi _ImportLockContext:

    """Context manager kila the agiza lock."""

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
         ashiria ValueError('attempted relative agiza beyond top-level package')
    base = bits[0]
    rudisha '{}.{}'.format(base, name) ikiwa name isipokua base


eleza _find_spec_legacy(finder, name, path):
    # This would be a good place kila a DeprecationWarning if
    # we ended up going that route.
    loader = finder.find_module(name, path)
    ikiwa loader ni Tupu:
        rudisha Tupu
    rudisha spec_from_loader(name, loader)


eleza _find_spec(name, path, target=Tupu):
    """Find a module's spec."""
    meta_path = sys.meta_path
    ikiwa meta_path ni Tupu:
        # PyImport_Cleanup() ni running ama has been called.
         ashiria ImportError("sys.meta_path ni Tupu, Python ni likely "
                          "shutting down")

    ikiwa sio meta_path:
        _warnings.warn('sys.meta_path ni empty', ImportWarning)

    # We check sys.modules here kila the reload case.  While a passed-in
    # target will usually indicate a reload there ni no guarantee, whereas
    # sys.modules provides one.
    is_reload = name kwenye sys.modules
    kila finder kwenye meta_path:
        ukijumuisha _ImportLockContext():
            jaribu:
                find_spec = finder.find_spec
            except AttributeError:
                spec = _find_spec_legacy(finder, name, path)
                ikiwa spec ni Tupu:
                    endelea
            isipokua:
                spec = find_spec(name, path, target)
        ikiwa spec ni sio Tupu:
            # The parent agiza may have already imported this module.
            ikiwa sio is_reload na name kwenye sys.modules:
                module = sys.modules[name]
                jaribu:
                    __spec__ = module.__spec__
                except AttributeError:
                    # We use the found spec since that ni the one that
                    # we would have used ikiwa the parent module hadn't
                    # beaten us to the punch.
                    rudisha spec
                isipokua:
                    ikiwa __spec__ ni Tupu:
                        rudisha spec
                    isipokua:
                        rudisha __spec__
            isipokua:
                rudisha spec
    isipokua:
        rudisha Tupu


eleza _sanity_check(name, package, level):
    """Verify arguments are "sane"."""
    ikiwa sio isinstance(name, str):
         ashiria TypeError('module name must be str, sio {}'.format(type(name)))
    ikiwa level < 0:
         ashiria ValueError('level must be >= 0')
    ikiwa level > 0:
        ikiwa sio isinstance(package, str):
             ashiria TypeError('__package__ sio set to a string')
        elikiwa sio package:
             ashiria ImportError('attempted relative agiza ukijumuisha no known parent '
                              'package')
    ikiwa sio name na level == 0:
         ashiria ValueError('Empty module name')


_ERR_MSG_PREFIX = 'No module named '
_ERR_MSG = _ERR_MSG_PREFIX + '{!r}'

eleza _find_and_load_unlocked(name, import_):
    path = Tupu
    parent = name.rpartition('.')[0]
    ikiwa parent:
        ikiwa parent sio kwenye sys.modules:
            _call_with_frames_removed(import_, parent)
        # Crazy side-effects!
        ikiwa name kwenye sys.modules:
            rudisha sys.modules[name]
        parent_module = sys.modules[parent]
        jaribu:
            path = parent_module.__path__
        except AttributeError:
            msg = (_ERR_MSG + '; {!r} ni sio a package').format(name, parent)
             ashiria ModuleNotFoundError(msg, name=name) kutoka Tupu
    spec = _find_spec(name, path)
    ikiwa spec ni Tupu:
         ashiria ModuleNotFoundError(_ERR_MSG.format(name), name=name)
    isipokua:
        module = _load_unlocked(spec)
    ikiwa parent:
        # Set the module as an attribute on its parent.
        parent_module = sys.modules[parent]
        setattr(parent_module, name.rpartition('.')[2], module)
    rudisha module


_NEEDS_LOADING = object()


eleza _find_and_load(name, import_):
    """Find na load the module."""
    ukijumuisha _ModuleLockManager(name):
        module = sys.modules.get(name, _NEEDS_LOADING)
        ikiwa module ni _NEEDS_LOADING:
            rudisha _find_and_load_unlocked(name, import_)

    ikiwa module ni Tupu:
        message = ('agiza of {} halted; '
                   'Tupu kwenye sys.modules'.format(name))
         ashiria ModuleNotFoundError(message, name=name)

    _lock_unlock_module(name)
    rudisha module


eleza _gcd_import(name, package=Tupu, level=0):
    """Import na rudisha the module based on its name, the package the call is
    being made from, na the level adjustment.

    This function represents the greatest common denominator of functionality
    between import_module na __import__. This includes setting __package__ if
    the loader did not.

    """
    _sanity_check(name, package, level)
    ikiwa level > 0:
        name = _resolve_name(name, package, level)
    rudisha _find_and_load(name, _gcd_import)


eleza _handle_fromlist(module, fromlist, import_, *, recursive=Uongo):
    """Figure out what __import__ should return.

    The import_ parameter ni a callable which takes the name of module to
    import. It ni required to decouple the function kutoka assuming importlib's
    agiza implementation ni desired.

    """
    # The hell that ni fromlist ...
    # If a package was imported, try to agiza stuff kutoka fromlist.
    kila x kwenye fromlist:
        ikiwa sio isinstance(x, str):
            ikiwa recursive:
                where = module.__name__ + '.__all__'
            isipokua:
                where = "``kutoka list''"
             ashiria TypeError(f"Item kwenye {where} must be str, "
                            f"not {type(x).__name__}")
        elikiwa x == '*':
            ikiwa sio recursive na hasattr(module, '__all__'):
                _handle_fromlist(module, module.__all__, import_,
                                 recursive=Kweli)
        elikiwa sio hasattr(module, x):
            from_name = '{}.{}'.format(module.__name__, x)
            jaribu:
                _call_with_frames_removed(import_, from_name)
            except ModuleNotFoundError as exc:
                # Backwards-compatibility dictates we ignore failed
                # imports triggered by fromlist kila modules that don't
                # exist.
                ikiwa (exc.name == from_name and
                    sys.modules.get(from_name, _NEEDS_LOADING) ni sio Tupu):
                    endelea
                raise
    rudisha module


eleza _calc___package__(globals):
    """Calculate what __package__ should be.

    __package__ ni sio guaranteed to be defined ama could be set to Tupu
    to represent that its proper value ni unknown.

    """
    package = globals.get('__package__')
    spec = globals.get('__spec__')
    ikiwa package ni sio Tupu:
        ikiwa spec ni sio Tupu na package != spec.parent:
            _warnings.warn("__package__ != __spec__.parent "
                           f"({package!r} != {spec.parent!r})",
                           ImportWarning, stacklevel=3)
        rudisha package
    elikiwa spec ni sio Tupu:
        rudisha spec.parent
    isipokua:
        _warnings.warn("can't resolve package kutoka __spec__ ama __package__, "
                       "falling back on __name__ na __path__",
                       ImportWarning, stacklevel=3)
        package = globals['__name__']
        ikiwa '__path__' sio kwenye globals:
            package = package.rpartition('.')[0]
    rudisha package


eleza __import__(name, globals=Tupu, locals=Tupu, fromlist=(), level=0):
    """Import a module.

    The 'globals' argument ni used to infer where the agiza ni occurring from
    to handle relative imports. The 'locals' argument ni ignored. The
    'fromlist' argument specifies what should exist as attributes on the module
    being imported (e.g. ``kutoka module agiza <fromlist>``).  The 'level'
    argument represents the package location to agiza kutoka kwenye a relative
    agiza (e.g. ``kutoka ..pkg agiza mod`` would have a 'level' of 2).

    """
    ikiwa level == 0:
        module = _gcd_import(name)
    isipokua:
        globals_ = globals ikiwa globals ni sio Tupu isipokua {}
        package = _calc___package__(globals_)
        module = _gcd_import(name, package, level)
    ikiwa sio fromlist:
        # Return up to the first dot kwenye 'name'. This ni complicated by the fact
        # that 'name' may be relative.
        ikiwa level == 0:
            rudisha _gcd_import(name.partition('.')[0])
        elikiwa sio name:
            rudisha module
        isipokua:
            # Figure out where to slice the module's name up to the first dot
            # kwenye 'name'.
            cut_off = len(name) - len(name.partition('.')[0])
            # Slice end needs to be positive to alleviate need to special-case
            # when ``'.' sio kwenye name``.
            rudisha sys.modules[module.__name__[:len(module.__name__)-cut_off]]
    elikiwa hasattr(module, '__path__'):
        rudisha _handle_fromlist(module, fromlist, _gcd_import)
    isipokua:
        rudisha module


eleza _builtin_from_name(name):
    spec = BuiltinImporter.find_spec(name)
    ikiwa spec ni Tupu:
         ashiria ImportError('no built-in module named ' + name)
    rudisha _load_unlocked(spec)


eleza _setup(sys_module, _imp_module):
    """Setup importlib by importing needed built-in modules na injecting them
    into the global namespace.

    As sys ni needed kila sys.modules access na _imp ni needed to load built-in
    modules, those two modules must be explicitly passed in.

    """
    global _imp, sys
    _imp = _imp_module
    sys = sys_module

    # Set up the spec kila existing builtin/frozen modules.
    module_type = type(sys)
    kila name, module kwenye sys.modules.items():
        ikiwa isinstance(module, module_type):
            ikiwa name kwenye sys.builtin_module_names:
                loader = BuiltinImporter
            elikiwa _imp.is_frozen(name):
                loader = FrozenImporter
            isipokua:
                endelea
            spec = _spec_from_module(module, loader)
            _init_module_attrs(spec, module)

    # Directly load built-in modules needed during bootstrap.
    self_module = sys.modules[__name__]
    kila builtin_name kwenye ('_thread', '_warnings', '_weakref'):
        ikiwa builtin_name sio kwenye sys.modules:
            builtin_module = _builtin_from_name(builtin_name)
        isipokua:
            builtin_module = sys.modules[builtin_name]
        setattr(self_module, builtin_name, builtin_module)


eleza _install(sys_module, _imp_module):
    """Install importers kila builtin na frozen modules"""
    _setup(sys_module, _imp_module)

    sys.meta_path.append(BuiltinImporter)
    sys.meta_path.append(FrozenImporter)


eleza _install_external_importers():
    """Install importers that require external filesystem access"""
    global _bootstrap_external
    agiza _frozen_importlib_external
    _bootstrap_external = _frozen_importlib_external
    _frozen_importlib_external._install(sys.modules[__name__])
