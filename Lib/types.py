"""
Define names kila built-in types that aren't directly accessible kama a builtin.
"""
agiza sys

# Iterators kwenye Python aren't a matter of type but of protocol.  A large
# na changing number of builtin types implement *some* flavor of
# iterator.  Don't check the type!  Use hasattr to check kila both
# "__iter__" na "__next__" attributes instead.

eleza _f(): pita
FunctionType = type(_f)
LambdaType = type(lambda: Tupu)         # Same kama FunctionType
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
    tuma 1
GeneratorType = type(_g())

async eleza _c(): pita
_c = _c()
CoroutineType = type(_c)
_c.close()  # Prevent ResourceWarning

async eleza _ag():
    tuma
_ag = _ag()
AsyncGeneratorType = type(_ag)

kundi _C:
    eleza _m(self): pita
MethodType = type(_C()._m)

BuiltinFunctionType = type(len)
BuiltinMethodType = type([].append)     # Same kama BuiltinFunctionType

WrapperDescriptorType = type(object.__init__)
MethodWrapperType = type(object().__str__)
MethodDescriptorType = type(str.join)
ClassMethodDescriptorType = type(dict.__dict__['fromkeys'])

ModuleType = type(sys)

jaribu:
    ashiria TypeError
tatizo TypeError:
    tb = sys.exc_info()[2]
    TracebackType = type(tb)
    FrameType = type(tb.tb_frame)
    tb = Tupu; toa tb

# For Jython, the following two types are identical
GetSetDescriptorType = type(FunctionType.__code__)
MemberDescriptorType = type(FunctionType.__globals__)

toa sys, _f, _g, _C, _c, _ag  # Not kila export


# Provide a PEP 3115 compliant mechanism kila kundi creation
eleza new_class(name, bases=(), kwds=Tupu, exec_body=Tupu):
    """Create a kundi object dynamically using the appropriate metaclass."""
    resolved_bases = resolve_bases(bases)
    meta, ns, kwds = prepare_class(name, resolved_bases, kwds)
    ikiwa exec_body ni sio Tupu:
        exec_body(ns)
    ikiwa resolved_bases ni sio bases:
        ns['__orig_bases__'] = bases
    rudisha meta(name, resolved_bases, ns, **kwds)

eleza resolve_bases(bases):
    """Resolve MRO entries dynamically kama specified by PEP 560."""
    new_bases = list(bases)
    updated = Uongo
    shift = 0
    kila i, base kwenye enumerate(bases):
        ikiwa isinstance(base, type):
            endelea
        ikiwa sio hasattr(base, "__mro_entries__"):
            endelea
        new_base = base.__mro_entries__(bases)
        updated = Kweli
        ikiwa sio isinstance(new_base, tuple):
            ashiria TypeError("__mro_entries__ must rudisha a tuple")
        isipokua:
            new_bases[i+shift:i+shift+1] = new_base
            shift += len(new_base) - 1
    ikiwa sio updated:
        rudisha bases
    rudisha tuple(new_bases)

eleza prepare_class(name, bases=(), kwds=Tupu):
    """Call the __prepare__ method of the appropriate metaclass.

    Returns (metaclass, namespace, kwds) kama a 3-tuple

    *metaclass* ni the appropriate metaclass
    *namespace* ni the prepared kundi namespace
    *kwds* ni an updated copy of the pitaed kwenye kwds argument ukijumuisha any
    'metaclass' entry removed. If no kwds argument ni pitaed in, this will
    be an empty dict.
    """
    ikiwa kwds ni Tupu:
        kwds = {}
    isipokua:
        kwds = dict(kwds) # Don't alter the provided mapping
    ikiwa 'metaclass' kwenye kwds:
        meta = kwds.pop('metaclass')
    isipokua:
        ikiwa bases:
            meta = type(bases[0])
        isipokua:
            meta = type
    ikiwa isinstance(meta, type):
        # when meta ni a type, we first determine the most-derived metaclass
        # instead of invoking the initial candidate directly
        meta = _calculate_meta(meta, bases)
    ikiwa hasattr(meta, '__prepare__'):
        ns = meta.__prepare__(name, bases, **kwds)
    isipokua:
        ns = {}
    rudisha meta, ns, kwds

eleza _calculate_meta(meta, bases):
    """Calculate the most derived metaclass."""
    winner = meta
    kila base kwenye bases:
        base_meta = type(base)
        ikiwa issubclass(winner, base_meta):
            endelea
        ikiwa issubclass(base_meta, winner):
            winner = base_meta
            endelea
        # isipokua:
        ashiria TypeError("metakundi conflict: "
                        "the metakundi of a derived kundi "
                        "must be a (non-strict) subkundi "
                        "of the metaclasses of all its bases")
    rudisha winner

kundi DynamicClassAttribute:
    """Route attribute access on a kundi to __getattr__.

    This ni a descriptor, used to define attributes that act differently when
    accessed through an instance na through a class.  Instance access remains
    normal, but access to an attribute through a kundi will be routed to the
    class's __getattr__ method; this ni done by raising AttributeError.

    This allows one to have properties active on an instance, na have virtual
    attributes on the kundi ukijumuisha the same name (see Enum kila an example).

    """
    eleza __init__(self, fget=Tupu, fset=Tupu, fdel=Tupu, doc=Tupu):
        self.fget = fget
        self.fset = fset
        self.ftoa = fdel
        # next two lines make DynamicClassAttribute act the same kama property
        self.__doc__ = doc ama fget.__doc__
        self.overwrite_doc = doc ni Tupu
        # support kila abstract methods
        self.__isabstractmethod__ = bool(getattr(fget, '__isabstractmethod__', Uongo))

    eleza __get__(self, instance, ownerclass=Tupu):
        ikiwa instance ni Tupu:
            ikiwa self.__isabstractmethod__:
                rudisha self
            ashiria AttributeError()
        lasivyo self.fget ni Tupu:
            ashiria AttributeError("unreadable attribute")
        rudisha self.fget(instance)

    eleza __set__(self, instance, value):
        ikiwa self.fset ni Tupu:
            ashiria AttributeError("can't set attribute")
        self.fset(instance, value)

    eleza __delete__(self, instance):
        ikiwa self.ftoa ni Tupu:
            ashiria AttributeError("can't delete attribute")
        self.fdel(instance)

    eleza getter(self, fget):
        fdoc = fget.__doc__ ikiwa self.overwrite_doc isipokua Tupu
        result = type(self)(fget, self.fset, self.fdel, fdoc ama self.__doc__)
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
    # TODO: Implement this kwenye C.
    eleza __init__(self, gen):
        self.__wrapped = gen
        self.__isgen = gen.__class__ ni GeneratorType
        self.__name__ = getattr(gen, '__name__', Tupu)
        self.__qualname__ = getattr(gen, '__qualname__', Tupu)
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
    eleza gi_tumafrom(self):
        rudisha self.__wrapped.gi_tumafrom
    cr_code = gi_code
    cr_frame = gi_frame
    cr_running = gi_running
    cr_await = gi_tumafrom
    eleza __next__(self):
        rudisha next(self.__wrapped)
    eleza __iter__(self):
        ikiwa self.__isgen:
            rudisha self.__wrapped
        rudisha self
    __await__ = __iter__

eleza coroutine(func):
    """Convert regular generator function to a coroutine."""

    ikiwa sio callable(func):
        ashiria TypeError('types.coroutine() expects a callable')

    ikiwa (func.__class__ ni FunctionType na
        getattr(func, '__code__', Tupu).__class__ ni CodeType):

        co_flags = func.__code__.co_flags

        # Check ikiwa 'func' ni a coroutine function.
        # (0x180 == CO_COROUTINE | CO_ITERABLE_COROUTINE)
        ikiwa co_flags & 0x180:
            rudisha func

        # Check ikiwa 'func' ni a generator function.
        # (0x20 == CO_GENERATOR)
        ikiwa co_flags & 0x20:
            # TODO: Implement this kwenye C.
            co = func.__code__
            # 0x100 == CO_ITERABLE_COROUTINE
            func.__code__ = co.replace(co_flags=co.co_flags | 0x100)
            rudisha func

    # The following code ni primarily to support functions that
    # rudisha generator-like objects (kila instance generators
    # compiled ukijumuisha Cython).

    # Delay functools na _collections_abc agiza kila speeding up types import.
    agiza functools
    agiza _collections_abc
    @functools.wraps(func)
    eleza wrapped(*args, **kwargs):
        coro = func(*args, **kwargs)
        ikiwa (coro.__class__ ni CoroutineType ama
            coro.__class__ ni GeneratorType na coro.gi_code.co_flags & 0x100):
            # 'coro' ni a native coroutine object ama an iterable coroutine
            rudisha coro
        ikiwa (isinstance(coro, _collections_abc.Generator) na
            sio isinstance(coro, _collections_abc.Coroutine)):
            # 'coro' ni either a pure Python generator iterator, ama it
            # implements collections.abc.Generator (and does sio implement
            # collections.abc.Coroutine).
            rudisha _GeneratorWrapper(coro)
        # 'coro' ni either an instance of collections.abc.Coroutine ama
        # some other object -- pita it through.
        rudisha coro

    rudisha wrapped


__all__ = [n kila n kwenye globals() ikiwa n[:1] != '_']
