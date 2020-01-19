"""Weak reference support kila Python.

This module ni an implementation of PEP 205:

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

agiza _collections_abc  # Import after _weakref to avoid circular import.
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

    eleza __new__(cls, meth, callback=Tupu):
        jaribu:
            obj = meth.__self__
            func = meth.__func__
        tatizo AttributeError:
            ashiria TypeError("argument should be a bound method, sio {}"
                            .format(type(meth))) kutoka Tupu
        eleza _cb(arg):
            # The self-weakref trick ni needed to avoid creating a reference
            # cycle.
            self = self_wr()
            ikiwa self._alive:
                self._alive = Uongo
                ikiwa callback ni sio Tupu:
                    callback(self)
        self = ref.__new__(cls, obj, _cb)
        self._func_ref = ref(func, _cb)
        self._meth_type = type(meth)
        self._alive = Kweli
        self_wr = ref(self)
        rudisha self

    eleza __call__(self):
        obj = super().__call__()
        func = self._func_ref()
        ikiwa obj ni Tupu ama func ni Tupu:
            rudisha Tupu
        rudisha self._meth_type(func, obj)

    eleza __eq__(self, other):
        ikiwa isinstance(other, WeakMethod):
            ikiwa sio self._alive ama sio other._alive:
                rudisha self ni other
            rudisha ref.__eq__(self, other) na self._func_ref == other._func_ref
        rudisha Uongo

    eleza __ne__(self, other):
        ikiwa isinstance(other, WeakMethod):
            ikiwa sio self._alive ama sio other._alive:
                rudisha self ni sio other
            rudisha ref.__ne__(self, other) ama self._func_ref != other._func_ref
        rudisha Kweli

    __hash__ = ref.__hash__


kundi WeakValueDictionary(_collections_abc.MutableMapping):
    """Mapping kundi that references values weakly.

    Entries kwenye the dictionary will be discarded when no strong
    reference to the value exists anymore
    """
    # We inherit the constructor without worrying about the input
    # dictionary; since it uses our .update() method, we get the right
    # checks (ikiwa the other dictionary ni a WeakValueDictionary,
    # objects are unwrapped on the way out, na we always wrap on the
    # way in).

    eleza __init__(self, other=(), /, **kw):
        eleza remove(wr, selfref=ref(self), _atomic_removal=_remove_dead_weakref):
            self = selfref()
            ikiwa self ni sio Tupu:
                ikiwa self._iterating:
                    self._pending_removals.append(wr.key)
                isipokua:
                    # Atomic removal ni necessary since this function
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
        wakati l:
            key = l.pop()
            _remove_dead_weakref(d, key)

    eleza __getitem__(self, key):
        ikiwa self._pending_removals:
            self._commit_removals()
        o = self.data[key]()
        ikiwa o ni Tupu:
            ashiria KeyError(key)
        isipokua:
            rudisha o

    eleza __delitem__(self, key):
        ikiwa self._pending_removals:
            self._commit_removals()
        toa self.data[key]

    eleza __len__(self):
        ikiwa self._pending_removals:
            self._commit_removals()
        rudisha len(self.data)

    eleza __contains__(self, key):
        ikiwa self._pending_removals:
            self._commit_removals()
        jaribu:
            o = self.data[key]()
        tatizo KeyError:
            rudisha Uongo
        rudisha o ni sio Tupu

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
        ukijumuisha _IterationGuard(self):
            kila key, wr kwenye self.data.items():
                o = wr()
                ikiwa o ni sio Tupu:
                    new[key] = o
        rudisha new

    __copy__ = copy

    eleza __deepcopy__(self, memo):
        kutoka copy agiza deepcopy
        ikiwa self._pending_removals:
            self._commit_removals()
        new = self.__class__()
        ukijumuisha _IterationGuard(self):
            kila key, wr kwenye self.data.items():
                o = wr()
                ikiwa o ni sio Tupu:
                    new[deepcopy(key, memo)] = o
        rudisha new

    eleza get(self, key, default=Tupu):
        ikiwa self._pending_removals:
            self._commit_removals()
        jaribu:
            wr = self.data[key]
        tatizo KeyError:
            rudisha default
        isipokua:
            o = wr()
            ikiwa o ni Tupu:
                # This should only happen
                rudisha default
            isipokua:
                rudisha o

    eleza items(self):
        ikiwa self._pending_removals:
            self._commit_removals()
        ukijumuisha _IterationGuard(self):
            kila k, wr kwenye self.data.items():
                v = wr()
                ikiwa v ni sio Tupu:
                    tuma k, v

    eleza keys(self):
        ikiwa self._pending_removals:
            self._commit_removals()
        ukijumuisha _IterationGuard(self):
            kila k, wr kwenye self.data.items():
                ikiwa wr() ni sio Tupu:
                    tuma k

    __iter__ = keys

    eleza itervaluerefs(self):
        """Return an iterator that tumas the weak references to the values.

        The references are sio guaranteed to be 'live' at the time
        they are used, so the result of calling the references needs
        to be checked before being used.  This can be used to avoid
        creating references that will cause the garbage collector to
        keep the values around longer than needed.

        """
        ikiwa self._pending_removals:
            self._commit_removals()
        ukijumuisha _IterationGuard(self):
            tuma kutoka self.data.values()

    eleza values(self):
        ikiwa self._pending_removals:
            self._commit_removals()
        ukijumuisha _IterationGuard(self):
            kila wr kwenye self.data.values():
                obj = wr()
                ikiwa obj ni sio Tupu:
                    tuma obj

    eleza popitem(self):
        ikiwa self._pending_removals:
            self._commit_removals()
        wakati Kweli:
            key, wr = self.data.popitem()
            o = wr()
            ikiwa o ni sio Tupu:
                rudisha key, o

    eleza pop(self, key, *args):
        ikiwa self._pending_removals:
            self._commit_removals()
        jaribu:
            o = self.data.pop(key)()
        tatizo KeyError:
            o = Tupu
        ikiwa o ni Tupu:
            ikiwa args:
                rudisha args[0]
            isipokua:
                ashiria KeyError(key)
        isipokua:
            rudisha o

    eleza setdefault(self, key, default=Tupu):
        jaribu:
            o = self.data[key]()
        tatizo KeyError:
            o = Tupu
        ikiwa o ni Tupu:
            ikiwa self._pending_removals:
                self._commit_removals()
            self.data[key] = KeyedRef(default, self._remove, key)
            rudisha default
        isipokua:
            rudisha o

    eleza update(self, other=Tupu, /, **kwargs):
        ikiwa self._pending_removals:
            self._commit_removals()
        d = self.data
        ikiwa other ni sio Tupu:
            ikiwa sio hasattr(other, "items"):
                other = dict(other)
            kila key, o kwenye other.items():
                d[key] = KeyedRef(o, self._remove, key)
        kila key, o kwenye kwargs.items():
            d[key] = KeyedRef(o, self._remove, key)

    eleza valuerefs(self):
        """Return a list of weak references to the values.

        The references are sio guaranteed to be 'live' at the time
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

    This ni used kwenye the WeakValueDictionary to avoid having to create
    a function object kila each key stored kwenye the mapping.  A shared
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

    Entries kwenye the dictionary will be discarded when there ni no
    longer a strong reference to the key. This can be used to
    associate additional data ukijumuisha an object owned by other parts of
    an application without adding attributes to those objects. This
    can be especially useful ukijumuisha objects that override attribute
    accesses.
    """

    eleza __init__(self, dict=Tupu):
        self.data = {}
        eleza remove(k, selfref=ref(self)):
            self = selfref()
            ikiwa self ni sio Tupu:
                ikiwa self._iterating:
                    self._pending_removals.append(k)
                isipokua:
                    toa self.data[k]
        self._remove = remove
        # A list of dead weakrefs (keys to be removed)
        self._pending_removals = []
        self._iterating = set()
        self._dirty_len = Uongo
        ikiwa dict ni sio Tupu:
            self.update(dict)

    eleza _commit_removals(self):
        # NOTE: We don't need to call this method before mutating the dict,
        # because a dead weakref never compares equal to a live weakref,
        # even ikiwa they happened to refer to equal objects.
        # However, it means keys may already have been removed.
        l = self._pending_removals
        d = self.data
        wakati l:
            jaribu:
                toa d[l.pop()]
            tatizo KeyError:
                pita

    eleza _scrub_removals(self):
        d = self.data
        self._pending_removals = [k kila k kwenye self._pending_removals ikiwa k kwenye d]
        self._dirty_len = Uongo

    eleza __delitem__(self, key):
        self._dirty_len = Kweli
        toa self.data[ref(key)]

    eleza __getitem__(self, key):
        rudisha self.data[ref(key)]

    eleza __len__(self):
        ikiwa self._dirty_len na self._pending_removals:
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
        ukijumuisha _IterationGuard(self):
            kila key, value kwenye self.data.items():
                o = key()
                ikiwa o ni sio Tupu:
                    new[o] = value
        rudisha new

    __copy__ = copy

    eleza __deepcopy__(self, memo):
        kutoka copy agiza deepcopy
        new = self.__class__()
        ukijumuisha _IterationGuard(self):
            kila key, value kwenye self.data.items():
                o = key()
                ikiwa o ni sio Tupu:
                    new[o] = deepcopy(value, memo)
        rudisha new

    eleza get(self, key, default=Tupu):
        rudisha self.data.get(ref(key),default)

    eleza __contains__(self, key):
        jaribu:
            wr = ref(key)
        tatizo TypeError:
            rudisha Uongo
        rudisha wr kwenye self.data

    eleza items(self):
        ukijumuisha _IterationGuard(self):
            kila wr, value kwenye self.data.items():
                key = wr()
                ikiwa key ni sio Tupu:
                    tuma key, value

    eleza keys(self):
        ukijumuisha _IterationGuard(self):
            kila wr kwenye self.data:
                obj = wr()
                ikiwa obj ni sio Tupu:
                    tuma obj

    __iter__ = keys

    eleza values(self):
        ukijumuisha _IterationGuard(self):
            kila wr, value kwenye self.data.items():
                ikiwa wr() ni sio Tupu:
                    tuma value

    eleza keyrefs(self):
        """Return a list of weak references to the keys.

        The references are sio guaranteed to be 'live' at the time
        they are used, so the result of calling the references needs
        to be checked before being used.  This can be used to avoid
        creating references that will cause the garbage collector to
        keep the keys around longer than needed.

        """
        rudisha list(self.data)

    eleza popitem(self):
        self._dirty_len = Kweli
        wakati Kweli:
            key, value = self.data.popitem()
            o = key()
            ikiwa o ni sio Tupu:
                rudisha o, value

    eleza pop(self, key, *args):
        self._dirty_len = Kweli
        rudisha self.data.pop(ref(key), *args)

    eleza setdefault(self, key, default=Tupu):
        rudisha self.data.setdefault(ref(key, self._remove),default)

    eleza update(self, dict=Tupu, /, **kwargs):
        d = self.data
        ikiwa dict ni sio Tupu:
            ikiwa sio hasattr(dict, "items"):
                dict = type({})(dict)
            kila key, value kwenye dict.items():
                d[ref(key, self._remove)] = value
        ikiwa len(kwargs):
            self.update(kwargs)


kundi finalize:
    """Class kila finalization of weakrefable objects

    finalize(obj, func, *args, **kwargs) returns a callable finalizer
    object which will be called when obj ni garbage collected. The
    first time the finalizer ni called it evaluates func(*arg, **kwargs)
    na returns the result. After this the finalizer ni dead, na
    calling it just returns Tupu.

    When the program exits any remaining finalizers kila which the
    atexit attribute ni true will be run kwenye reverse order of creation.
    By default atexit ni true.
    """

    # Finalizer objects don't have any state of their own.  They are
    # just used kama keys to lookup _Info objects kwenye the registry.  This
    # ensures that they cannot be part of a ref-cycle.

    __slots__ = ()
    _registry = {}
    _shutdown = Uongo
    _index_iter = itertools.count()
    _dirty = Uongo
    _registered_with_atexit = Uongo

    kundi _Info:
        __slots__ = ("weakref", "func", "args", "kwargs", "atexit", "index")

    eleza __init__(*args, **kwargs):
        ikiwa len(args) >= 3:
            self, obj, func, *args = args
        lasivyo sio args:
            ashiria TypeError("descriptor '__init__' of 'finalize' object "
                            "needs an argument")
        isipokua:
            ikiwa 'func' haiko kwenye kwargs:
                ashiria TypeError('finalize expected at least 2 positional '
                                'arguments, got %d' % (len(args)-1))
            func = kwargs.pop('func')
            ikiwa len(args) >= 2:
                self, obj, *args = args
                agiza warnings
                warnings.warn("Passing 'func' kama keyword argument ni deprecated",
                              DeprecationWarning, stacklevel=2)
            isipokua:
                ikiwa 'obj' haiko kwenye kwargs:
                    ashiria TypeError('finalize expected at least 2 positional '
                                    'arguments, got %d' % (len(args)-1))
                obj = kwargs.pop('obj')
                self, *args = args
                agiza warnings
                warnings.warn("Passing 'obj' kama keyword argument ni deprecated",
                              DeprecationWarning, stacklevel=2)
        args = tuple(args)

        ikiwa sio self._registered_with_atexit:
            # We may register the exit function more than once because
            # of a thread race, but that ni harmless
            agiza atexit
            atexit.register(self._exitfunc)
            finalize._registered_with_atexit = Kweli
        info = self._Info()
        info.weakref = ref(obj, self)
        info.func = func
        info.args = args
        info.kwargs = kwargs ama Tupu
        info.atexit = Kweli
        info.index = next(self._index_iter)
        self._registry[self] = info
        finalize._dirty = Kweli
    __init__.__text_signature__ = '($self, obj, func, /, *args, **kwargs)'

    eleza __call__(self, _=Tupu):
        """If alive then mark kama dead na rudisha func(*args, **kwargs);
        otherwise rudisha Tupu"""
        info = self._registry.pop(self, Tupu)
        ikiwa info na sio self._shutdown:
            rudisha info.func(*info.args, **(info.kwargs ama {}))

    eleza detach(self):
        """If alive then mark kama dead na rudisha (obj, func, args, kwargs);
        otherwise rudisha Tupu"""
        info = self._registry.get(self)
        obj = info na info.weakref()
        ikiwa obj ni sio Tupu na self._registry.pop(self, Tupu):
            rudisha (obj, info.func, info.args, info.kwargs ama {})

    eleza peek(self):
        """If alive then rudisha (obj, func, args, kwargs);
        otherwise rudisha Tupu"""
        info = self._registry.get(self)
        obj = info na info.weakref()
        ikiwa obj ni sio Tupu:
            rudisha (obj, info.func, info.args, info.kwargs ama {})

    @property
    eleza alive(self):
        """Whether finalizer ni alive"""
        rudisha self kwenye self._registry

    @property
    eleza atexit(self):
        """Whether finalizer should be called at exit"""
        info = self._registry.get(self)
        rudisha bool(info) na info.atexit

    @atexit.setter
    eleza atexit(self, value):
        info = self._registry.get(self)
        ikiwa info:
            info.atexit = bool(value)

    eleza __repr__(self):
        info = self._registry.get(self)
        obj = info na info.weakref()
        ikiwa obj ni Tupu:
            rudisha '<%s object at %#x; dead>' % (type(self).__name__, id(self))
        isipokua:
            rudisha '<%s object at %#x; kila %r at %#x>' % \
                (type(self).__name__, id(self), type(obj).__name__, id(obj))

    @classmethod
    eleza _select_for_exit(cls):
        # Return live finalizers marked kila exit, oldest first
        L = [(f,i) kila (f,i) kwenye cls._registry.items() ikiwa i.atexit]
        L.sort(key=lambda item:item[1].index)
        rudisha [f kila (f,i) kwenye L]

    @classmethod
    eleza _exitfunc(cls):
        # At shutdown invoke finalizers kila which atexit ni true.
        # This ni called once all other non-daemonic threads have been
        # joined.
        reenable_gc = Uongo
        jaribu:
            ikiwa cls._regisjaribu:
                agiza gc
                ikiwa gc.isenabled():
                    reenable_gc = Kweli
                    gc.disable()
                pending = Tupu
                wakati Kweli:
                    ikiwa pending ni Tupu ama finalize._dirty:
                        pending = cls._select_for_exit()
                        finalize._dirty = Uongo
                    ikiwa sio pending:
                        koma
                    f = pending.pop()
                    jaribu:
                        # gc ni disabled, so (assuming no daemonic
                        # threads) the following ni the only line kwenye
                        # this function which might trigger creation
                        # of a new finalizer
                        f()
                    tatizo Exception:
                        sys.excepthook(*sys.exc_info())
                    assert f haiko kwenye cls._registry
        mwishowe:
            # prevent any more finalizers kutoka executing during shutdown
            finalize._shutdown = Kweli
            ikiwa reenable_gc:
                gc.enable()
