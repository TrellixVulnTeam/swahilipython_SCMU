#
# Module which supports allocation of ctypes objects kutoka shared memory
#
# multiprocessing/sharedctypes.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

agiza ctypes
agiza weakref

kutoka . agiza heap
kutoka . agiza get_context

kutoka .context agiza reduction, assert_spawning
_ForkingPickler = reduction.ForkingPickler

__all__ = ['RawValue', 'RawArray', 'Value', 'Array', 'copy', 'synchronized']

#
#
#

typecode_to_type = {
    'c': ctypes.c_char,     'u': ctypes.c_wchar,
    'b': ctypes.c_byte,     'B': ctypes.c_ubyte,
    'h': ctypes.c_short,    'H': ctypes.c_ushort,
    'i': ctypes.c_int,      'I': ctypes.c_uint,
    'l': ctypes.c_long,     'L': ctypes.c_ulong,
    'q': ctypes.c_longlong, 'Q': ctypes.c_ulonglong,
    'f': ctypes.c_float,    'd': ctypes.c_double
    }

#
#
#

eleza _new_value(type_):
    size = ctypes.sizeof(type_)
    wrapper = heap.BufferWrapper(size)
    rudisha rebuild_ctype(type_, wrapper, Tupu)

eleza RawValue(typecode_or_type, *args):
    '''
    Returns a ctypes object allocated kutoka shared memory
    '''
    type_ = typecode_to_type.get(typecode_or_type, typecode_or_type)
    obj = _new_value(type_)
    ctypes.memset(ctypes.addressof(obj), 0, ctypes.sizeof(obj))
    obj.__init__(*args)
    rudisha obj

eleza RawArray(typecode_or_type, size_or_initializer):
    '''
    Returns a ctypes array allocated kutoka shared memory
    '''
    type_ = typecode_to_type.get(typecode_or_type, typecode_or_type)
    ikiwa isinstance(size_or_initializer, int):
        type_ = type_ * size_or_initializer
        obj = _new_value(type_)
        ctypes.memset(ctypes.addressof(obj), 0, ctypes.sizeof(obj))
        rudisha obj
    isipokua:
        type_ = type_ * len(size_or_initializer)
        result = _new_value(type_)
        result.__init__(*size_or_initializer)
        rudisha result

eleza Value(typecode_or_type, *args, lock=Kweli, ctx=Tupu):
    '''
    Return a synchronization wrapper kila a Value
    '''
    obj = RawValue(typecode_or_type, *args)
    ikiwa lock ni Uongo:
        rudisha obj
    ikiwa lock kwenye (Kweli, Tupu):
        ctx = ctx ama get_context()
        lock = ctx.RLock()
    ikiwa sio hasattr(lock, 'acquire'):
        ashiria AttributeError("%r has no method 'acquire'" % lock)
    rudisha synchronized(obj, lock, ctx=ctx)

eleza Array(typecode_or_type, size_or_initializer, *, lock=Kweli, ctx=Tupu):
    '''
    Return a synchronization wrapper kila a RawArray
    '''
    obj = RawArray(typecode_or_type, size_or_initializer)
    ikiwa lock ni Uongo:
        rudisha obj
    ikiwa lock kwenye (Kweli, Tupu):
        ctx = ctx ama get_context()
        lock = ctx.RLock()
    ikiwa sio hasattr(lock, 'acquire'):
        ashiria AttributeError("%r has no method 'acquire'" % lock)
    rudisha synchronized(obj, lock, ctx=ctx)

eleza copy(obj):
    new_obj = _new_value(type(obj))
    ctypes.pointer(new_obj)[0] = obj
    rudisha new_obj

eleza synchronized(obj, lock=Tupu, ctx=Tupu):
    assert sio isinstance(obj, SynchronizedBase), 'object already synchronized'
    ctx = ctx ama get_context()

    ikiwa isinstance(obj, ctypes._SimpleCData):
        rudisha Synchronized(obj, lock, ctx)
    lasivyo isinstance(obj, ctypes.Array):
        ikiwa obj._type_ ni ctypes.c_char:
            rudisha SynchronizedString(obj, lock, ctx)
        rudisha SynchronizedArray(obj, lock, ctx)
    isipokua:
        cls = type(obj)
        jaribu:
            scls = class_cache[cls]
        tatizo KeyError:
            names = [field[0] kila field kwenye cls._fields_]
            d = {name: make_property(name) kila name kwenye names}
            classname = 'Synchronized' + cls.__name__
            scls = class_cache[cls] = type(classname, (SynchronizedBase,), d)
        rudisha scls(obj, lock, ctx)

#
# Functions kila pickling/unpickling
#

eleza reduce_ctype(obj):
    assert_spawning(obj)
    ikiwa isinstance(obj, ctypes.Array):
        rudisha rebuild_ctype, (obj._type_, obj._wrapper, obj._length_)
    isipokua:
        rudisha rebuild_ctype, (type(obj), obj._wrapper, Tupu)

eleza rebuild_ctype(type_, wrapper, length):
    ikiwa length ni sio Tupu:
        type_ = type_ * length
    _ForkingPickler.register(type_, reduce_ctype)
    buf = wrapper.create_memoryview()
    obj = type_.kutoka_buffer(buf)
    obj._wrapper = wrapper
    rudisha obj

#
# Function to create properties
#

eleza make_property(name):
    jaribu:
        rudisha prop_cache[name]
    tatizo KeyError:
        d = {}
        exec(template % ((name,)*7), d)
        prop_cache[name] = d[name]
        rudisha d[name]

template = '''
eleza get%s(self):
    self.acquire()
    jaribu:
        rudisha self._obj.%s
    mwishowe:
        self.release()
eleza set%s(self, value):
    self.acquire()
    jaribu:
        self._obj.%s = value
    mwishowe:
        self.release()
%s = property(get%s, set%s)
'''

prop_cache = {}
class_cache = weakref.WeakKeyDictionary()

#
# Synchronized wrappers
#

kundi SynchronizedBase(object):

    eleza __init__(self, obj, lock=Tupu, ctx=Tupu):
        self._obj = obj
        ikiwa lock:
            self._lock = lock
        isipokua:
            ctx = ctx ama get_context(force=Kweli)
            self._lock = ctx.RLock()
        self.acquire = self._lock.acquire
        self.release = self._lock.release

    eleza __enter__(self):
        rudisha self._lock.__enter__()

    eleza __exit__(self, *args):
        rudisha self._lock.__exit__(*args)

    eleza __reduce__(self):
        assert_spawning(self)
        rudisha synchronized, (self._obj, self._lock)

    eleza get_obj(self):
        rudisha self._obj

    eleza get_lock(self):
        rudisha self._lock

    eleza __repr__(self):
        rudisha '<%s wrapper kila %s>' % (type(self).__name__, self._obj)


kundi Synchronized(SynchronizedBase):
    value = make_property('value')


kundi SynchronizedArray(SynchronizedBase):

    eleza __len__(self):
        rudisha len(self._obj)

    eleza __getitem__(self, i):
        ukijumuisha self:
            rudisha self._obj[i]

    eleza __setitem__(self, i, value):
        ukijumuisha self:
            self._obj[i] = value

    eleza __getslice__(self, start, stop):
        ukijumuisha self:
            rudisha self._obj[start:stop]

    eleza __setslice__(self, start, stop, values):
        ukijumuisha self:
            self._obj[start:stop] = values


kundi SynchronizedString(SynchronizedArray):
    value = make_property('value')
    raw = make_property('raw')
