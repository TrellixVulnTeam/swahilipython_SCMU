"""Weak reference support for Python.

This module is an implementation of PEP 205:

http://www.python.org/dev/peps/pep-0205/
"""

# Naming convention: Variables named "wr" are weak reference objects;
# they are called this instead of "ref" to avoid name collisions with
# the module-global ref() function imported kutoka _weakref.

kutoka _weakref agiza (
     getweakrefcount,
     getweakrefs,
     ref,
     proxy,
     CallableProxyType,
     ProxyType,
     ReferenceType,
     _remove_dead_weakref)

kutoka _weakrefset agiza WeakSet, _IterationGuard

agiza _collections_abc  # Import after _weakref to avoid circular agiza.
agiza sys
agiza itertools

ProxyTypes = (ProxyType, CallableProxyType)

__all__ = ["ref", "proxy", "getweakrefcount", "getweakrefs",
           "WeakKeyDictionary", "ReferenceType", "ProxyType",
           "CallableProxyType", "ProxyTypes", "WeakValueDictionary",
           "WeakSet", "WeakMethod", "finalize"]


kundi WeakMethod(ref):
    """
    A custom `weakref.ref` subkundi which simulates a weak reference to
    a bound method, working around the lifetime problem of bound methods.
    """

    __slots__ = "_func_ref", "_meth_type", "_alive", "__weakref__"

    eleza __new__(cls, meth, callback=None):
        try:
            obj = meth.__self__
            func = meth.__func__
        except AttributeError:
            raise TypeError("argument should be a bound method, not {}"
                            .format(type(meth))) kutoka None
        eleza _cb(arg):
            # The self-weakref trick is needed to avoid creating a reference
            # cycle.
            self = self_wr()
            ikiwa self._alive:
                self._alive = False
                ikiwa callback is not None:
                    callback(self)
        self = ref.__new__(cls, obj, _cb)
        self._func_ref = ref(func, _cb)
        self._meth_type = type(meth)
        self._alive = True
        self_wr = ref(self)
        rudisha self

    eleza __call__(self):
        obj = super().__call__()
        func = self._func_ref()
        ikiwa obj is None or func is None:
            rudisha None
        rudisha self._meth_type(func, obj)

    eleza __eq__(self, other):
        ikiwa isinstance(other, WeakMethod):
            ikiwa not self._alive or not other._alive:
                rudisha self is other
            rudisha ref.__eq__(self, other) and self._func_ref == other._func_ref
        rudisha False

    eleza __ne__(self, other):
        ikiwa isinstance(other, WeakMethod):
            ikiwa not self._alive or not other._alive:
                rudisha self is not other
            rudisha ref.__ne__(self, other) or self._func_ref != other._func_ref
        rudisha True

    __hash__ = ref.__hash__


kundi WeakValueDictionary(_collections_abc.MutableMapping):
    """Mapping kundi that references values weakly.

    Entries in the dictionary will be discarded when no strong
    reference to the value exists anymore
    """
    # We inherit the constructor without worrying about the input
    # dictionary; since it uses our .update() method, we get the right
    # checks (ikiwa the other dictionary is a WeakValueDictionary,
    # objects are unwrapped on the way out, and we always wrap on the
    # way in).

    eleza __init__(self, other=(), /, **kw):
        eleza remove(wr, selfref=ref(self), _atomic_removal=_remove_dead_weakref):
            self = selfref()
            ikiwa self is not None:
                ikiwa self._iterating:
                    self._pending_removals.append(wr.key)
                else:
                    # Atomic removal is necessary since this function
                    # can be called asynchronously by the GC
                    _atomic_removal(self.data, wr.key)
        self._remove = remove
        # A list of keys to be removed
        self._pending_removals = []
        self._iterating = set()
        self.data = {}
        self.update(other, **kw)

    eleza _commit_removals(self):
        l = self._pending_removals
        d = self.data
        # We shouldn't encounter any KeyError, because this method should
        # always be called *before* mutating the dict.
        while l:
            key = l.pop()
            _remove_dead_weakref(d, key)

    eleza __getitem__(self, key):
        ikiwa self._pending_removals:
            self._commit_removals()
        o = self.data[key]()
        ikiwa o is None:
            raise KeyError(key)
        else:
            rudisha o

    eleza __delitem__(self, key):
        ikiwa self._pending_removals:
            self._commit_removals()
        del self.data[key]

    eleza __len__(self):
        ikiwa self._pending_removals:
            self._commit_removals()
        rudisha len(self.data)

    eleza __contains__(self, key):
        ikiwa self._pending_removals:
            self._commit_removals()
        try:
            o = self.data[key]()
        except KeyError:
            rudisha False
        rudisha o is not None

    eleza __repr__(self):
        rudisha "<%s at %#x>" % (self.__class__.__name__, id(self))

    eleza __setitem__(self, key, value):
        ikiwa self._pending_removals:
            self._commit_removals()
        self.data[key] = KeyedRef(value, self._remove, key)

    eleza copy(self):
        ikiwa self._pending_removals:
            self._commit_removals()
        new = WeakValueDictionary()
        with _IterationGuard(self):
            for key, wr in self.data.items():
                o = wr()
                ikiwa o is not None:
                    new[key] = o
        rudisha new

    __copy__ = copy

    eleza __deepcopy__(self, memo):
        kutoka copy agiza deepcopy
        ikiwa self._pending_removals:
            self._commit_removals()
        new = self.__class__()
        with _IterationGuard(self):
            for key, wr in self.data.items():
                o = wr()
                ikiwa o is not None:
                    new[deepcopy(key, memo)] = o
        rudisha new

    eleza get(self, key, default=None):
        ikiwa self._pending_removals:
            self._commit_removals()
        try:
            wr = self.data[key]
        except KeyError:
            rudisha default
        else:
            o = wr()
            ikiwa o is None:
                # This should only happen
                rudisha default
            else:
                rudisha o

    eleza items(self):
        ikiwa self._pending_removals:
            self._commit_removals()
        with _IterationGuard(self):
            for k, wr in self.data.items():
                v = wr()
                ikiwa v is not None:
                    yield k, v

    eleza keys(self):
        ikiwa self._pending_removals:
            self._commit_removals()
        with _IterationGuard(self):
            for k, wr in self.data.items():
                ikiwa wr() is not None:
                    yield k

    __iter__ = keys

    eleza itervaluerefs(self):
        """Return an iterator that yields the weak references to the values.

        The references are not guaranteed to be 'live' at the time
        they are used, so the result of calling the references needs
        to be checked before being used.  This can be used to avoid
        creating references that will cause the garbage collector to
        keep the values around longer than needed.

        """
        ikiwa self._pending_removals:
            self._commit_removals()
        with _IterationGuard(self):
            yield kutoka self.data.values()

    eleza values(self):
        ikiwa self._pending_removals:
            self._commit_removals()
        with _IterationGuard(self):
            for wr in self.data.values():
                obj = wr()
                ikiwa obj is not None:
                    yield obj

    eleza popitem(self):
        ikiwa self._pending_removals:
            self._commit_removals()
        while True:
            key, wr = self.data.popitem()
            o = wr()
            ikiwa o is not None:
                rudisha key, o

    eleza pop(self, key, *args):
        ikiwa self._pending_removals:
            self._commit_removals()
        try:
            o = self.data.pop(key)()
        except KeyError:
            o = None
        ikiwa o is None:
            ikiwa args:
                rudisha args[0]
            else:
                raise KeyError(key)
        else:
            rudisha o

    eleza setdefault(self, key, default=None):
        try:
            o = self.data[key]()
        except KeyError:
            o = None
        ikiwa o is None:
            ikiwa self._pending_removals:
                self._commit_removals()
            self.data[key] = KeyedRef(default, self._remove, key)
            rudisha default
        else:
            rudisha o

    eleza update(self, other=None, /, **kwargs):
        ikiwa self._pending_removals:
            self._commit_removals()
        d = self.data
        ikiwa other is not None:
            ikiwa not hasattr(other, "items"):
                other = dict(other)
            for key, o in other.items():
                d[key] = KeyedRef(o, self._remove, key)
        for key, o in kwargs.items():
            d[key] = KeyedRef(o, self._remove, key)

    eleza valuerefs(self):
        """Return a list of weak references to the values.

        The references are not guaranteed to be 'live' at the time
        they are used, so the result of calling the references needs
        to be checked before being used.  This can be used to avoid
        creating references that will cause the garbage collector to
        keep the values around longer than needed.

        """
        ikiwa self._pending_removals:
            self._commit_removals()
        rudisha list(self.data.values())


kundi KeyedRef(ref):
    """Specialized reference that includes a key corresponding to the value.

    This is used in the WeakValueDictionary to avoid having to create
    a function object for each key stored in the mapping.  A shared
    callback object can use the 'key' attribute of a KeyedRef instead
    of getting a reference to the key kutoka an enclosing scope.

    """

    __slots__ = "key",

    eleza __new__(type, ob, callback, key):
        self = ref.__new__(type, ob, callback)
        self.key = key
        rudisha self

    eleza __init__(self, ob, callback, key):
        super().__init__(ob, callback)


kundi WeakKeyDictionary(_collections_abc.MutableMapping):
    """ Mapping kundi that references keys weakly.

    Entries in the dictionary will be discarded when there is no
    longer a strong reference to the key. This can be used to
    associate additional data with an object owned by other parts of
    an application without adding attributes to those objects. This
    can be especially useful with objects that override attribute
    accesses.
    """

    eleza __init__(self, dict=None):
        self.data = {}
        eleza remove(k, selfref=ref(self)):
            self = selfref()
            ikiwa self is not None:
                ikiwa self._iterating:
                    self._pending_removals.append(k)
                else:
                    del self.data[k]
        self._remove = remove
        # A list of dead weakrefs (keys to be removed)
        self._pending_removals = []
        self._iterating = set()
        self._dirty_len = False
        ikiwa dict is not None:
            self.update(dict)

    eleza _commit_removals(self):
        # NOTE: We don't need to call this method before mutating the dict,
        # because a dead weakref never compares equal to a live weakref,
        # even ikiwa they happened to refer to equal objects.
        # However, it means keys may already have been removed.
        l = self._pending_removals
        d = self.data
        while l:
            try:
                del d[l.pop()]
            except KeyError:
                pass

    eleza _scrub_removals(self):
        d = self.data
        self._pending_removals = [k for k in self._pending_removals ikiwa k in d]
        self._dirty_len = False

    eleza __delitem__(self, key):
        self._dirty_len = True
        del self.data[ref(key)]

    eleza __getitem__(self, key):
        rudisha self.data[ref(key)]

    eleza __len__(self):
        ikiwa self._dirty_len and self._pending_removals:
            # self._pending_removals may still contain keys which were
            # explicitly removed, we have to scrub them (see issue #21173).
            self._scrub_removals()
        rudisha len(self.data) - len(self._pending_removals)

    eleza __repr__(self):
        rudisha "<%s at %#x>" % (self.__class__.__name__, id(self))

    eleza __setitem__(self, key, value):
        self.data[ref(key, self._remove)] = value

    eleza copy(self):
        new = WeakKeyDictionary()
        with _IterationGuard(self):
            for key, value in self.data.items():
                o = key()
                ikiwa o is not None:
                    new[o] = value
        rudisha new

    __copy__ = copy

    eleza __deepcopy__(self, memo):
        kutoka copy agiza deepcopy
        new = self.__class__()
        with _IterationGuard(self):
            for key, value in self.data.items():
                o = key()
                ikiwa o is not None:
                    new[o] = deepcopy(value, memo)
        rudisha new

    eleza get(self, key, default=None):
        rudisha self.data.get(ref(key),default)

    eleza __contains__(self, key):
        try:
            wr = ref(key)
        except TypeError:
            rudisha False
        rudisha wr in self.data

    eleza items(self):
        with _IterationGuard(self):
            for wr, value in self.data.items():
                key = wr()
                ikiwa key is not None:
                    yield key, value

    eleza keys(self):
        with _IterationGuard(self):
            for wr in self.data:
                obj = wr()
                ikiwa obj is not None:
                    yield obj

    __iter__ = keys

    eleza values(self):
        with _IterationGuard(self):
            for wr, value in self.data.items():
                ikiwa wr() is not None:
                    yield value

    eleza keyrefs(self):
        """Return a list of weak references to the keys.

        The references are not guaranteed to be 'live' at the time
        they are used, so the result of calling the references needs
        to be checked before being used.  This can be used to avoid
        creating references that will cause the garbage collector to
        keep the keys around longer than needed.

        """
        rudisha list(self.data)

    eleza popitem(self):
        self._dirty_len = True
        while True:
            key, value = self.data.popitem()
            o = key()
            ikiwa o is not None:
                rudisha o, value

    eleza pop(self, key, *args):
        self._dirty_len = True
        rudisha self.data.pop(ref(key), *args)

    eleza setdefault(self, key, default=None):
        rudisha self.data.setdefault(ref(key, self._remove),default)

    eleza update(self, dict=None, /, **kwargs):
        d = self.data
        ikiwa dict is not None:
            ikiwa not hasattr(dict, "items"):
                dict = type({})(dict)
            for key, value in dict.items():
                d[ref(key, self._remove)] = value
        ikiwa len(kwargs):
            self.update(kwargs)


kundi finalize:
    """Class for finalization of weakrefable objects

    finalize(obj, func, *args, **kwargs) returns a callable finalizer
    object which will be called when obj is garbage collected. The
    first time the finalizer is called it evaluates func(*arg, **kwargs)
    and returns the result. After this the finalizer is dead, and
    calling it just returns None.

    When the program exits any remaining finalizers for which the
    atexit attribute is true will be run in reverse order of creation.
    By default atexit is true.
    """

    # Finalizer objects don't have any state of their own.  They are
    # just used as keys to lookup _Info objects in the registry.  This
    # ensures that they cannot be part of a ref-cycle.

    __slots__ = ()
    _registry = {}
    _shutdown = False
    _index_iter = itertools.count()
    _dirty = False
    _registered_with_atexit = False

    kundi _Info:
        __slots__ = ("weakref", "func", "args", "kwargs", "atexit", "index")

    eleza __init__(*args, **kwargs):
        ikiwa len(args) >= 3:
            self, obj, func, *args = args
        elikiwa not args:
            raise TypeError("descriptor '__init__' of 'finalize' object "
                            "needs an argument")
        else:
            ikiwa 'func' not in kwargs:
                raise TypeError('finalize expected at least 2 positional '
                                'arguments, got %d' % (len(args)-1))
            func = kwargs.pop('func')
            ikiwa len(args) >= 2:
                self, obj, *args = args
                agiza warnings
                warnings.warn("Passing 'func' as keyword argument is deprecated",
                              DeprecationWarning, stacklevel=2)
            else:
                ikiwa 'obj' not in kwargs:
                    raise TypeError('finalize expected at least 2 positional '
                                    'arguments, got %d' % (len(args)-1))
                obj = kwargs.pop('obj')
                self, *args = args
                agiza warnings
                warnings.warn("Passing 'obj' as keyword argument is deprecated",
                              DeprecationWarning, stacklevel=2)
        args = tuple(args)

        ikiwa not self._registered_with_atexit:
            # We may register the exit function more than once because
            # of a thread race, but that is harmless
            agiza atexit
            atexit.register(self._exitfunc)
            finalize._registered_with_atexit = True
        info = self._Info()
        info.weakref = ref(obj, self)
        info.func = func
        info.args = args
        info.kwargs = kwargs or None
        info.atexit = True
        info.index = next(self._index_iter)
        self._registry[self] = info
        finalize._dirty = True
    __init__.__text_signature__ = '($self, obj, func, /, *args, **kwargs)'

    eleza __call__(self, _=None):
        """If alive then mark as dead and rudisha func(*args, **kwargs);
        otherwise rudisha None"""
        info = self._registry.pop(self, None)
        ikiwa info and not self._shutdown:
            rudisha info.func(*info.args, **(info.kwargs or {}))

    eleza detach(self):
        """If alive then mark as dead and rudisha (obj, func, args, kwargs);
        otherwise rudisha None"""
        info = self._registry.get(self)
        obj = info and info.weakref()
        ikiwa obj is not None and self._registry.pop(self, None):
            rudisha (obj, info.func, info.args, info.kwargs or {})

    eleza peek(self):
        """If alive then rudisha (obj, func, args, kwargs);
        otherwise rudisha None"""
        info = self._registry.get(self)
        obj = info and info.weakref()
        ikiwa obj is not None:
            rudisha (obj, info.func, info.args, info.kwargs or {})

    @property
    eleza alive(self):
        """Whether finalizer is alive"""
        rudisha self in self._registry

    @property
    eleza atexit(self):
        """Whether finalizer should be called at exit"""
        info = self._registry.get(self)
        rudisha bool(info) and info.atexit

    @atexit.setter
    eleza atexit(self, value):
        info = self._registry.get(self)
        ikiwa info:
            info.atexit = bool(value)

    eleza __repr__(self):
        info = self._registry.get(self)
        obj = info and info.weakref()
        ikiwa obj is None:
            rudisha '<%s object at %#x; dead>' % (type(self).__name__, id(self))
        else:
            rudisha '<%s object at %#x; for %r at %#x>' % \
                (type(self).__name__, id(self), type(obj).__name__, id(obj))

    @classmethod
    eleza _select_for_exit(cls):
        # Return live finalizers marked for exit, oldest first
        L = [(f,i) for (f,i) in cls._registry.items() ikiwa i.atexit]
        L.sort(key=lambda item:item[1].index)
        rudisha [f for (f,i) in L]

    @classmethod
    eleza _exitfunc(cls):
        # At shutdown invoke finalizers for which atexit is true.
        # This is called once all other non-daemonic threads have been
        # joined.
        reenable_gc = False
        try:
            ikiwa cls._registry:
                agiza gc
                ikiwa gc.isenabled():
                    reenable_gc = True
                    gc.disable()
                pending = None
                while True:
                    ikiwa pending is None or finalize._dirty:
                        pending = cls._select_for_exit()
                        finalize._dirty = False
                    ikiwa not pending:
                        break
                    f = pending.pop()
                    try:
                        # gc is disabled, so (assuming no daemonic
                        # threads) the following is the only line in
                        # this function which might trigger creation
                        # of a new finalizer
                        f()
                    except Exception:
                        sys.excepthook(*sys.exc_info())
                    assert f not in cls._registry
        finally:
            # prevent any more finalizers kutoka executing during shutdown
            finalize._shutdown = True
            ikiwa reenable_gc:
                gc.enable()
