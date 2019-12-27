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
    rudisha rebuild_ctype(type_, wrapper, None)

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
    else:
        type_ = type_ * len(size_or_initializer)
        result = _new_value(type_)
        result.__init__(*size_or_initializer)
        rudisha result

eleza Value(typecode_or_type, *args, lock=True, ctx=None):
    '''
    Return a synchronization wrapper for a Value
    '''
    obj = RawValue(typecode_or_type, *args)
    ikiwa lock is False:
        rudisha obj
    ikiwa lock in (True, None):
        ctx = ctx or get_context()
        lock = ctx.RLock()
    ikiwa not hasattr(lock, 'acquire'):
        raise AttributeError("%r has no method 'acquire'" % lock)
    rudisha synchronized(obj, lock, ctx=ctx)

eleza Array(typecode_or_type, size_or_initializer, *, lock=True, ctx=None):
    '''
    Return a synchronization wrapper for a RawArray
    '''
    obj = RawArray(typecode_or_type, size_or_initializer)
    ikiwa lock is False:
        rudisha obj
    ikiwa lock in (True, None):
        ctx = ctx or get_context()
        lock = ctx.RLock()
    ikiwa not hasattr(lock, 'acquire'):
        raise AttributeError("%r has no method 'acquire'" % lock)
    rudisha synchronized(obj, lock, ctx=ctx)

eleza copy(obj):
    new_obj = _new_value(type(obj))
    ctypes.pointer(new_obj)[0] = obj
    rudisha new_obj

eleza synchronized(obj, lock=None, ctx=None):
    assert not isinstance(obj, SynchronizedBase), 'object already synchronized'
    ctx = ctx or get_context()

    ikiwa isinstance(obj, ctypes._SimpleCData):
        rudisha Synchronized(obj, lock, ctx)
    elikiwa isinstance(obj, ctypes.Array):
        ikiwa obj._type_ is ctypes.c_char:
            rudisha SynchronizedString(obj, lock, ctx)
        rudisha SynchronizedArray(obj, lock, ctx)
    else:
        cls = type(obj)
        try:
            scls = class_cache[cls]
        except KeyError:
            names = [field[0] for field in cls._fields_]
            d = {name: make_property(name) for name in names}
            classname = 'Synchronized' + cls.__name__
            scls = class_cache[cls] = type(classname, (SynchronizedBase,), d)
        rudisha scls(obj, lock, ctx)

#
# Functions for pickling/unpickling
#

eleza reduce_ctype(obj):
    assert_spawning(obj)
    ikiwa isinstance(obj, ctypes.Array):
        rudisha rebuild_ctype, (obj._type_, obj._wrapper, obj._length_)
    else:
        rudisha rebuild_ctype, (type(obj), obj._wrapper, None)

eleza rebuild_ctype(type_, wrapper, length):
    ikiwa length is not None:
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
    try:
        rudisha prop_cache[name]
    except KeyError:
        d = {}
        exec(template % ((name,)*7), d)
        prop_cache[name] = d[name]
        rudisha d[name]

template = '''
eleza get%s(self):
    self.acquire()
    try:
        rudisha self._obj.%s
    finally:
        self.release()
eleza set%s(self, value):
    self.acquire()
    try:
        self._obj.%s = value
    finally:
        self.release()
%s = property(get%s, set%s)
'''

prop_cache = {}
class_cache = weakref.WeakKeyDictionary()

#
# Synchronized wrappers
#

kundi SynchronizedBase(object):

    eleza __init__(self, obj, lock=None, ctx=None):
        self._obj = obj
        ikiwa lock:
            self._lock = lock
        else:
            ctx = ctx or get_context(force=True)
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
        rudisha '<%s wrapper for %s>' % (type(self).__name__, self._obj)


kundi Synchronized(SynchronizedBase):
    value = make_property('value')


kundi SynchronizedArray(SynchronizedBase):

    eleza __len__(self):
        rudisha len(self._obj)

    eleza __getitem__(self, i):
        with self:
            rudisha self._obj[i]

    eleza __setitem__(self, i, value):
        with self:
            self._obj[i] = value

    eleza __getslice__(self, start, stop):
        with self:
            rudisha self._obj[start:stop]

    eleza __setslice__(self, start, stop, values):
        with self:
            self._obj[start:stop] = values


kundi SynchronizedString(SynchronizedArray):
    value = make_property('value')
    raw = make_property('raw')
