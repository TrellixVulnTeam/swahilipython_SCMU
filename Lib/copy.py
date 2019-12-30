"""Generic (shallow na deep) copying operations.

Interface summary:

        agiza copy

        x = copy.copy(y)        # make a shallow copy of y
        x = copy.deepcopy(y)    # make a deep copy of y

For module specific errors, copy.Error ni raised.

The difference between shallow na deep copying ni only relevant for
compound objects (objects that contain other objects, like lists ama
kundi instances).

- A shallow copy constructs a new compound object na then (to the
  extent possible) inserts *the same objects* into it that the
  original contains.

- A deep copy constructs a new compound object na then, recursively,
  inserts *copies* into it of the objects found kwenye the original.

Two problems often exist ukijumuisha deep copy operations that don't exist
ukijumuisha shallow copy operations:

 a) recursive objects (compound objects that, directly ama indirectly,
    contain a reference to themselves) may cause a recursive loop

 b) because deep copy copies *everything* it may copy too much, e.g.
    administrative data structures that should be shared even between
    copies

Python's deep copy operation avoids these problems by:

 a) keeping a table of objects already copied during the current
    copying pita

 b) letting user-defined classes override the copying operation ama the
    set of components copied

This version does sio copy types like module, class, function, method,
nor stack trace, stack frame, nor file, socket, window, nor array, nor
any similar types.

Classes can use the same interfaces to control copying that they use
to control pickling: they can define methods called __getinitargs__(),
__getstate__() na __setstate__().  See the documentation kila module
"pickle" kila information on these methods.
"""

agiza types
agiza weakref
kutoka copyreg agiza dispatch_table

kundi Error(Exception):
    pita
error = Error   # backward compatibility

jaribu:
    kutoka org.python.core agiza PyStringMap
tatizo ImportError:
    PyStringMap = Tupu

__all__ = ["Error", "copy", "deepcopy"]

eleza copy(x):
    """Shallow copy operation on arbitrary Python objects.

    See the module's __doc__ string kila more info.
    """

    cls = type(x)

    copier = _copy_dispatch.get(cls)
    ikiwa copier:
        rudisha copier(x)

    ikiwa issubclass(cls, type):
        # treat it kama a regular class:
        rudisha _copy_immutable(x)

    copier = getattr(cls, "__copy__", Tupu)
    ikiwa copier ni sio Tupu:
        rudisha copier(x)

    reductor = dispatch_table.get(cls)
    ikiwa reductor ni sio Tupu:
        rv = reductor(x)
    isipokua:
        reductor = getattr(x, "__reduce_ex__", Tupu)
        ikiwa reductor ni sio Tupu:
            rv = reductor(4)
        isipokua:
            reductor = getattr(x, "__reduce__", Tupu)
            ikiwa reductor:
                rv = reductor()
            isipokua:
                ashiria Error("un(shallow)copyable object of type %s" % cls)

    ikiwa isinstance(rv, str):
        rudisha x
    rudisha _reconstruct(x, Tupu, *rv)


_copy_dispatch = d = {}

eleza _copy_immutable(x):
    rudisha x
kila t kwenye (type(Tupu), int, float, bool, complex, str, tuple,
          bytes, frozenset, type, range, slice,
          types.BuiltinFunctionType, type(Ellipsis), type(NotImplemented),
          types.FunctionType, weakref.ref):
    d[t] = _copy_immutable
t = getattr(types, "CodeType", Tupu)
ikiwa t ni sio Tupu:
    d[t] = _copy_immutable

d[list] = list.copy
d[dict] = dict.copy
d[set] = set.copy
d[bytearray] = bytearray.copy

ikiwa PyStringMap ni sio Tupu:
    d[PyStringMap] = PyStringMap.copy

toa d, t

eleza deepcopy(x, memo=Tupu, _nil=[]):
    """Deep copy operation on arbitrary Python objects.

    See the module's __doc__ string kila more info.
    """

    ikiwa memo ni Tupu:
        memo = {}

    d = id(x)
    y = memo.get(d, _nil)
    ikiwa y ni sio _nil:
        rudisha y

    cls = type(x)

    copier = _deepcopy_dispatch.get(cls)
    ikiwa copier ni sio Tupu:
        y = copier(x, memo)
    isipokua:
        ikiwa issubclass(cls, type):
            y = _deepcopy_atomic(x, memo)
        isipokua:
            copier = getattr(x, "__deepcopy__", Tupu)
            ikiwa copier ni sio Tupu:
                y = copier(memo)
            isipokua:
                reductor = dispatch_table.get(cls)
                ikiwa reductor:
                    rv = reductor(x)
                isipokua:
                    reductor = getattr(x, "__reduce_ex__", Tupu)
                    ikiwa reductor ni sio Tupu:
                        rv = reductor(4)
                    isipokua:
                        reductor = getattr(x, "__reduce__", Tupu)
                        ikiwa reductor:
                            rv = reductor()
                        isipokua:
                            ashiria Error(
                                "un(deep)copyable object of type %s" % cls)
                ikiwa isinstance(rv, str):
                    y = x
                isipokua:
                    y = _reconstruct(x, memo, *rv)

    # If ni its own copy, don't memoize.
    ikiwa y ni sio x:
        memo[d] = y
        _keep_alive(x, memo) # Make sure x lives at least kama long kama d
    rudisha y

_deepcopy_dispatch = d = {}

eleza _deepcopy_atomic(x, memo):
    rudisha x
d[type(Tupu)] = _deepcopy_atomic
d[type(Ellipsis)] = _deepcopy_atomic
d[type(NotImplemented)] = _deepcopy_atomic
d[int] = _deepcopy_atomic
d[float] = _deepcopy_atomic
d[bool] = _deepcopy_atomic
d[complex] = _deepcopy_atomic
d[bytes] = _deepcopy_atomic
d[str] = _deepcopy_atomic
d[types.CodeType] = _deepcopy_atomic
d[type] = _deepcopy_atomic
d[types.BuiltinFunctionType] = _deepcopy_atomic
d[types.FunctionType] = _deepcopy_atomic
d[weakref.ref] = _deepcopy_atomic

eleza _deepcopy_list(x, memo, deepcopy=deepcopy):
    y = []
    memo[id(x)] = y
    append = y.append
    kila a kwenye x:
        append(deepcopy(a, memo))
    rudisha y
d[list] = _deepcopy_list

eleza _deepcopy_tuple(x, memo, deepcopy=deepcopy):
    y = [deepcopy(a, memo) kila a kwenye x]
    # We're sio going to put the tuple kwenye the memo, but it's still important we
    # check kila it, kwenye case the tuple contains recursive mutable structures.
    jaribu:
        rudisha memo[id(x)]
    tatizo KeyError:
        pita
    kila k, j kwenye zip(x, y):
        ikiwa k ni sio j:
            y = tuple(y)
            koma
    isipokua:
        y = x
    rudisha y
d[tuple] = _deepcopy_tuple

eleza _deepcopy_dict(x, memo, deepcopy=deepcopy):
    y = {}
    memo[id(x)] = y
    kila key, value kwenye x.items():
        y[deepcopy(key, memo)] = deepcopy(value, memo)
    rudisha y
d[dict] = _deepcopy_dict
ikiwa PyStringMap ni sio Tupu:
    d[PyStringMap] = _deepcopy_dict

eleza _deepcopy_method(x, memo): # Copy instance methods
    rudisha type(x)(x.__func__, deepcopy(x.__self__, memo))
d[types.MethodType] = _deepcopy_method

toa d

eleza _keep_alive(x, memo):
    """Keeps a reference to the object x kwenye the memo.

    Because we remember objects by their id, we have
    to assure that possibly temporary objects are kept
    alive by referencing them.
    We store a reference at the id of the memo, which should
    normally sio be used unless someone tries to deepcopy
    the memo itself...
    """
    jaribu:
        memo[id(memo)].append(x)
    tatizo KeyError:
        # aha, this ni the first one :-)
        memo[id(memo)]=[x]

eleza _reconstruct(x, memo, func, args,
                 state=Tupu, listiter=Tupu, dictiter=Tupu,
                 deepcopy=deepcopy):
    deep = memo ni sio Tupu
    ikiwa deep na args:
        args = (deepcopy(arg, memo) kila arg kwenye args)
    y = func(*args)
    ikiwa deep:
        memo[id(x)] = y

    ikiwa state ni sio Tupu:
        ikiwa deep:
            state = deepcopy(state, memo)
        ikiwa hasattr(y, '__setstate__'):
            y.__setstate__(state)
        isipokua:
            ikiwa isinstance(state, tuple) na len(state) == 2:
                state, slotstate = state
            isipokua:
                slotstate = Tupu
            ikiwa state ni sio Tupu:
                y.__dict__.update(state)
            ikiwa slotstate ni sio Tupu:
                kila key, value kwenye slotstate.items():
                    setattr(y, key, value)

    ikiwa listiter ni sio Tupu:
        ikiwa deep:
            kila item kwenye listiter:
                item = deepcopy(item, memo)
                y.append(item)
        isipokua:
            kila item kwenye listiter:
                y.append(item)
    ikiwa dictiter ni sio Tupu:
        ikiwa deep:
            kila key, value kwenye dictiter:
                key = deepcopy(key, memo)
                value = deepcopy(value, memo)
                y[key] = value
        isipokua:
            kila key, value kwenye dictiter:
                y[key] = value
    rudisha y

toa types, weakref, PyStringMap
