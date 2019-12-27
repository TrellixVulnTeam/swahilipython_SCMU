"""
Define names for built-in types that aren't directly accessible as a builtin.
"""
agiza sys

# Iterators in Python aren't a matter of type but of protocol.  A large
# and changing number of builtin types implement *some* flavor of
# iterator.  Don't check the type!  Use hasattr to check for both
# "__iter__" and "__next__" attributes instead.

eleza _f(): pass
FunctionType = type(_f)
LambdaType = type(lambda: None)         # Same as FunctionType
CodeType = type(_f.__code__)
MappingProxyType = type(type.__dict__)
SimpleNamespace = type(sys.implementation)

eleza _cell_factory():
    a = 1
    eleza f():
        nonlocal a
    rudisha f.__closure__[0]
CellType = type(_cell_factory())

eleza _g():
    yield 1
GeneratorType = type(_g())

async eleza _c(): pass
_c = _c()
CoroutineType = type(_c)
_c.close()  # Prevent ResourceWarning

async eleza _ag():
    yield
_ag = _ag()
AsyncGeneratorType = type(_ag)

kundi _C:
    eleza _m(self): pass
MethodType = type(_C()._m)

BuiltinFunctionType = type(len)
BuiltinMethodType = type([].append)     # Same as BuiltinFunctionType

WrapperDescriptorType = type(object.__init__)
MethodWrapperType = type(object().__str__)
MethodDescriptorType = type(str.join)
ClassMethodDescriptorType = type(dict.__dict__['kutokakeys'])

ModuleType = type(sys)

try:
    raise TypeError
except TypeError:
    tb = sys.exc_info()[2]
    TracebackType = type(tb)
    FrameType = type(tb.tb_frame)
    tb = None; del tb

# For Jython, the following two types are identical
GetSetDescriptorType = type(FunctionType.__code__)
MemberDescriptorType = type(FunctionType.__globals__)

del sys, _f, _g, _C, _c, _ag  # Not for export


# Provide a PEP 3115 compliant mechanism for kundi creation
eleza new_class(name, bases=(), kwds=None, exec_body=None):
    """Create a kundi object dynamically using the appropriate metaclass."""
    resolved_bases = resolve_bases(bases)
    meta, ns, kwds = prepare_class(name, resolved_bases, kwds)
    ikiwa exec_body is not None:
        exec_body(ns)
    ikiwa resolved_bases is not bases:
        ns['__orig_bases__'] = bases
    rudisha meta(name, resolved_bases, ns, **kwds)

eleza resolve_bases(bases):
    """Resolve MRO entries dynamically as specified by PEP 560."""
    new_bases = list(bases)
    updated = False
    shift = 0
    for i, base in enumerate(bases):
        ikiwa isinstance(base, type):
            continue
        ikiwa not hasattr(base, "__mro_entries__"):
            continue
        new_base = base.__mro_entries__(bases)
        updated = True
        ikiwa not isinstance(new_base, tuple):
            raise TypeError("__mro_entries__ must rudisha a tuple")
        else:
            new_bases[i+shift:i+shift+1] = new_base
            shift += len(new_base) - 1
    ikiwa not updated:
        rudisha bases
    rudisha tuple(new_bases)

eleza prepare_class(name, bases=(), kwds=None):
    """Call the __prepare__ method of the appropriate metaclass.

    Returns (metaclass, namespace, kwds) as a 3-tuple

    *metaclass* is the appropriate metaclass
    *namespace* is the prepared kundi namespace
    *kwds* is an updated copy of the passed in kwds argument with any
    'metaclass' entry removed. If no kwds argument is passed in, this will
    be an empty dict.
    """
    ikiwa kwds is None:
        kwds = {}
    else:
        kwds = dict(kwds) # Don't alter the provided mapping
    ikiwa 'metaclass' in kwds:
        meta = kwds.pop('metaclass')
    else:
        ikiwa bases:
            meta = type(bases[0])
        else:
            meta = type
    ikiwa isinstance(meta, type):
        # when meta is a type, we first determine the most-derived metaclass
        # instead of invoking the initial candidate directly
        meta = _calculate_meta(meta, bases)
    ikiwa hasattr(meta, '__prepare__'):
        ns = meta.__prepare__(name, bases, **kwds)
    else:
        ns = {}
    rudisha meta, ns, kwds

eleza _calculate_meta(meta, bases):
    """Calculate the most derived metaclass."""
    winner = meta
    for base in bases:
        base_meta = type(base)
        ikiwa issubclass(winner, base_meta):
            continue
        ikiwa issubclass(base_meta, winner):
            winner = base_meta
            continue
        # else:
        raise TypeError("metakundi conflict: "
                        "the metakundi of a derived kundi "
                        "must be a (non-strict) subkundi "
                        "of the metaclasses of all its bases")
    rudisha winner

kundi DynamicClassAttribute:
    """Route attribute access on a kundi to __getattr__.

    This is a descriptor, used to define attributes that act differently when
    accessed through an instance and through a class.  Instance access remains
    normal, but access to an attribute through a kundi will be routed to the
    class's __getattr__ method; this is done by raising AttributeError.

    This allows one to have properties active on an instance, and have virtual
    attributes on the kundi with the same name (see Enum for an example).

    """
    eleza __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        # next two lines make DynamicClassAttribute act the same as property
        self.__doc__ = doc or fget.__doc__
        self.overwrite_doc = doc is None
        # support for abstract methods
        self.__isabstractmethod__ = bool(getattr(fget, '__isabstractmethod__', False))

    eleza __get__(self, instance, ownerclass=None):
        ikiwa instance is None:
            ikiwa self.__isabstractmethod__:
                rudisha self
            raise AttributeError()
        elikiwa self.fget is None:
            raise AttributeError("unreadable attribute")
        rudisha self.fget(instance)

    eleza __set__(self, instance, value):
        ikiwa self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(instance, value)

    eleza __delete__(self, instance):
        ikiwa self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(instance)

    eleza getter(self, fget):
        fdoc = fget.__doc__ ikiwa self.overwrite_doc else None
        result = type(self)(fget, self.fset, self.fdel, fdoc or self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        rudisha result

    eleza setter(self, fset):
        result = type(self)(self.fget, fset, self.fdel, self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        rudisha result

    eleza deleter(self, fdel):
        result = type(self)(self.fget, self.fset, fdel, self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        rudisha result


kundi _GeneratorWrapper:
    # TODO: Implement this in C.
    eleza __init__(self, gen):
        self.__wrapped = gen
        self.__isgen = gen.__class__ is GeneratorType
        self.__name__ = getattr(gen, '__name__', None)
        self.__qualname__ = getattr(gen, '__qualname__', None)
    eleza send(self, val):
        rudisha self.__wrapped.send(val)
    eleza throw(self, tp, *rest):
        rudisha self.__wrapped.throw(tp, *rest)
    eleza close(self):
        rudisha self.__wrapped.close()
    @property
    eleza gi_code(self):
        rudisha self.__wrapped.gi_code
    @property
    eleza gi_frame(self):
        rudisha self.__wrapped.gi_frame
    @property
    eleza gi_running(self):
        rudisha self.__wrapped.gi_running
    @property
    eleza gi_yieldkutoka(self):
        rudisha self.__wrapped.gi_yieldkutoka
    cr_code = gi_code
    cr_frame = gi_frame
    cr_running = gi_running
    cr_await = gi_yieldkutoka
    eleza __next__(self):
        rudisha next(self.__wrapped)
    eleza __iter__(self):
        ikiwa self.__isgen:
            rudisha self.__wrapped
        rudisha self
    __await__ = __iter__

eleza coroutine(func):
    """Convert regular generator function to a coroutine."""

    ikiwa not callable(func):
        raise TypeError('types.coroutine() expects a callable')

    ikiwa (func.__class__ is FunctionType and
        getattr(func, '__code__', None).__class__ is CodeType):

        co_flags = func.__code__.co_flags

        # Check ikiwa 'func' is a coroutine function.
        # (0x180 == CO_COROUTINE | CO_ITERABLE_COROUTINE)
        ikiwa co_flags & 0x180:
            rudisha func

        # Check ikiwa 'func' is a generator function.
        # (0x20 == CO_GENERATOR)
        ikiwa co_flags & 0x20:
            # TODO: Implement this in C.
            co = func.__code__
            # 0x100 == CO_ITERABLE_COROUTINE
            func.__code__ = co.replace(co_flags=co.co_flags | 0x100)
            rudisha func

    # The following code is primarily to support functions that
    # rudisha generator-like objects (for instance generators
    # compiled with Cython).

    # Delay functools and _collections_abc agiza for speeding up types agiza.
    agiza functools
    agiza _collections_abc
    @functools.wraps(func)
    eleza wrapped(*args, **kwargs):
        coro = func(*args, **kwargs)
        ikiwa (coro.__class__ is CoroutineType or
            coro.__class__ is GeneratorType and coro.gi_code.co_flags & 0x100):
            # 'coro' is a native coroutine object or an iterable coroutine
            rudisha coro
        ikiwa (isinstance(coro, _collections_abc.Generator) and
            not isinstance(coro, _collections_abc.Coroutine)):
            # 'coro' is either a pure Python generator iterator, or it
            # implements collections.abc.Generator (and does not implement
            # collections.abc.Coroutine).
            rudisha _GeneratorWrapper(coro)
        # 'coro' is either an instance of collections.abc.Coroutine or
        # some other object -- pass it through.
        rudisha coro

    rudisha wrapped


__all__ = [n for n in globals() ikiwa n[:1] != '_']
