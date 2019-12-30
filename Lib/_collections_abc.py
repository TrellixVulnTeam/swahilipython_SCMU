# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Abstract Base Classes (ABCs) kila collections, according to PEP 3119.

Unit tests are kwenye test_collections.
"""

kutoka abc agiza ABCMeta, abstractmethod
agiza sys

__all__ = ["Awaitable", "Coroutine",
           "AsyncIterable", "AsyncIterator", "AsyncGenerator",
           "Hashable", "Iterable", "Iterator", "Generator", "Reversible",
           "Sized", "Container", "Callable", "Collection",
           "Set", "MutableSet",
           "Mapping", "MutableMapping",
           "MappingView", "KeysView", "ItemsView", "ValuesView",
           "Sequence", "MutableSequence",
           "ByteString",
           ]

# This module has been renamed kutoka collections.abc to _collections_abc to
# speed up interpreter startup. Some of the types such kama MutableMapping are
# required early but collections module imports a lot of other modules.
# See issue #19218
__name__ = "collections.abc"

# Private list of types that we want to register ukijumuisha the various ABCs
# so that they will pita tests like:
#       it = iter(somebytearray)
#       assert isinstance(it, Iterable)
# Note:  kwenye other implementations, these types might sio be distinct
# na they may have their own implementation specific types that
# are sio included on this list.
bytes_iterator = type(iter(b''))
bytearray_iterator = type(iter(bytearray()))
#callable_iterator = ???
dict_keyiterator = type(iter({}.keys()))
dict_valueiterator = type(iter({}.values()))
dict_itemiterator = type(iter({}.items()))
list_iterator = type(iter([]))
list_reverseiterator = type(iter(reversed([])))
range_iterator = type(iter(range(0)))
longrange_iterator = type(iter(range(1 << 1000)))
set_iterator = type(iter(set()))
str_iterator = type(iter(""))
tuple_iterator = type(iter(()))
zip_iterator = type(iter(zip()))
## views ##
dict_keys = type({}.keys())
dict_values = type({}.values())
dict_items = type({}.items())
## misc ##
mappingproxy = type(type.__dict__)
generator = type((lambda: (tuma))())
## coroutine ##
async eleza _coro(): pita
_coro = _coro()
coroutine = type(_coro)
_coro.close()  # Prevent ResourceWarning
toa _coro
## asynchronous generator ##
async eleza _ag(): tuma
_ag = _ag()
async_generator = type(_ag)
toa _ag


### ONE-TRICK PONIES ###

eleza _check_methods(C, *methods):
    mro = C.__mro__
    kila method kwenye methods:
        kila B kwenye mro:
            ikiwa method kwenye B.__dict__:
                ikiwa B.__dict__[method] ni Tupu:
                    rudisha NotImplemented
                koma
        isipokua:
            rudisha NotImplemented
    rudisha Kweli

kundi Hashable(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    eleza __hash__(self):
        rudisha 0

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni Hashable:
            rudisha _check_methods(C, "__hash__")
        rudisha NotImplemented


kundi Awaitable(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    eleza __await__(self):
        tuma

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni Awaitable:
            rudisha _check_methods(C, "__await__")
        rudisha NotImplemented


kundi Coroutine(Awaitable):

    __slots__ = ()

    @abstractmethod
    eleza send(self, value):
        """Send a value into the coroutine.
        Return next tumaed value ama ashiria StopIteration.
        """
        ashiria StopIteration

    @abstractmethod
    eleza throw(self, typ, val=Tupu, tb=Tupu):
        """Raise an exception kwenye the coroutine.
        Return next tumaed value ama ashiria StopIteration.
        """
        ikiwa val ni Tupu:
            ikiwa tb ni Tupu:
                ashiria typ
            val = typ()
        ikiwa tb ni sio Tupu:
            val = val.with_traceback(tb)
        ashiria val

    eleza close(self):
        """Raise GeneratorExit inside coroutine.
        """
        jaribu:
            self.throw(GeneratorExit)
        tatizo (GeneratorExit, StopIteration):
            pita
        isipokua:
            ashiria RuntimeError("coroutine ignored GeneratorExit")

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni Coroutine:
            rudisha _check_methods(C, '__await__', 'send', 'throw', 'close')
        rudisha NotImplemented


Coroutine.register(coroutine)


kundi AsyncIterable(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    eleza __aiter__(self):
        rudisha AsyncIterator()

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni AsyncIterable:
            rudisha _check_methods(C, "__aiter__")
        rudisha NotImplemented


kundi AsyncIterator(AsyncIterable):

    __slots__ = ()

    @abstractmethod
    async eleza __anext__(self):
        """Return the next item ama ashiria StopAsyncIteration when exhausted."""
        ashiria StopAsyncIteration

    eleza __aiter__(self):
        rudisha self

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni AsyncIterator:
            rudisha _check_methods(C, "__anext__", "__aiter__")
        rudisha NotImplemented


kundi AsyncGenerator(AsyncIterator):

    __slots__ = ()

    async eleza __anext__(self):
        """Return the next item kutoka the asynchronous generator.
        When exhausted, ashiria StopAsyncIteration.
        """
        rudisha await self.asend(Tupu)

    @abstractmethod
    async eleza asend(self, value):
        """Send a value into the asynchronous generator.
        Return next tumaed value ama ashiria StopAsyncIteration.
        """
        ashiria StopAsyncIteration

    @abstractmethod
    async eleza athrow(self, typ, val=Tupu, tb=Tupu):
        """Raise an exception kwenye the asynchronous generator.
        Return next tumaed value ama ashiria StopAsyncIteration.
        """
        ikiwa val ni Tupu:
            ikiwa tb ni Tupu:
                ashiria typ
            val = typ()
        ikiwa tb ni sio Tupu:
            val = val.with_traceback(tb)
        ashiria val

    async eleza aclose(self):
        """Raise GeneratorExit inside coroutine.
        """
        jaribu:
            await self.athrow(GeneratorExit)
        tatizo (GeneratorExit, StopAsyncIteration):
            pita
        isipokua:
            ashiria RuntimeError("asynchronous generator ignored GeneratorExit")

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni AsyncGenerator:
            rudisha _check_methods(C, '__aiter__', '__anext__',
                                  'asend', 'athrow', 'aclose')
        rudisha NotImplemented


AsyncGenerator.register(async_generator)


kundi Iterable(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    eleza __iter__(self):
        wakati Uongo:
            tuma Tupu

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni Iterable:
            rudisha _check_methods(C, "__iter__")
        rudisha NotImplemented


kundi Iterator(Iterable):

    __slots__ = ()

    @abstractmethod
    eleza __next__(self):
        'Return the next item kutoka the iterator. When exhausted, ashiria StopIteration'
        ashiria StopIteration

    eleza __iter__(self):
        rudisha self

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni Iterator:
            rudisha _check_methods(C, '__iter__', '__next__')
        rudisha NotImplemented

Iterator.register(bytes_iterator)
Iterator.register(bytearray_iterator)
#Iterator.register(callable_iterator)
Iterator.register(dict_keyiterator)
Iterator.register(dict_valueiterator)
Iterator.register(dict_itemiterator)
Iterator.register(list_iterator)
Iterator.register(list_reverseiterator)
Iterator.register(range_iterator)
Iterator.register(longrange_iterator)
Iterator.register(set_iterator)
Iterator.register(str_iterator)
Iterator.register(tuple_iterator)
Iterator.register(zip_iterator)


kundi Reversible(Iterable):

    __slots__ = ()

    @abstractmethod
    eleza __reversed__(self):
        wakati Uongo:
            tuma Tupu

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni Reversible:
            rudisha _check_methods(C, "__reversed__", "__iter__")
        rudisha NotImplemented


kundi Generator(Iterator):

    __slots__ = ()

    eleza __next__(self):
        """Return the next item kutoka the generator.
        When exhausted, ashiria StopIteration.
        """
        rudisha self.send(Tupu)

    @abstractmethod
    eleza send(self, value):
        """Send a value into the generator.
        Return next tumaed value ama ashiria StopIteration.
        """
        ashiria StopIteration

    @abstractmethod
    eleza throw(self, typ, val=Tupu, tb=Tupu):
        """Raise an exception kwenye the generator.
        Return next tumaed value ama ashiria StopIteration.
        """
        ikiwa val ni Tupu:
            ikiwa tb ni Tupu:
                ashiria typ
            val = typ()
        ikiwa tb ni sio Tupu:
            val = val.with_traceback(tb)
        ashiria val

    eleza close(self):
        """Raise GeneratorExit inside generator.
        """
        jaribu:
            self.throw(GeneratorExit)
        tatizo (GeneratorExit, StopIteration):
            pita
        isipokua:
            ashiria RuntimeError("generator ignored GeneratorExit")

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni Generator:
            rudisha _check_methods(C, '__iter__', '__next__',
                                  'send', 'throw', 'close')
        rudisha NotImplemented

Generator.register(generator)


kundi Sized(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    eleza __len__(self):
        rudisha 0

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni Sized:
            rudisha _check_methods(C, "__len__")
        rudisha NotImplemented


kundi Container(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    eleza __contains__(self, x):
        rudisha Uongo

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni Container:
            rudisha _check_methods(C, "__contains__")
        rudisha NotImplemented

kundi Collection(Sized, Iterable, Container):

    __slots__ = ()

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni Collection:
            rudisha _check_methods(C,  "__len__", "__iter__", "__contains__")
        rudisha NotImplemented

kundi Callable(metaclass=ABCMeta):

    __slots__ = ()

    @abstractmethod
    eleza __call__(self, *args, **kwds):
        rudisha Uongo

    @classmethod
    eleza __subclasshook__(cls, C):
        ikiwa cls ni Callable:
            rudisha _check_methods(C, "__call__")
        rudisha NotImplemented


### SETS ###


kundi Set(Collection):

    """A set ni a finite, iterable container.

    This kundi provides concrete generic implementations of all
    methods tatizo kila __contains__, __iter__ na __len__.

    To override the comparisons (presumably kila speed, kama the
    semantics are fixed), redefine __le__ na __ge__,
    then the other operations will automatically follow suit.
    """

    __slots__ = ()

    eleza __le__(self, other):
        ikiwa sio isinstance(other, Set):
            rudisha NotImplemented
        ikiwa len(self) > len(other):
            rudisha Uongo
        kila elem kwenye self:
            ikiwa elem haiko kwenye other:
                rudisha Uongo
        rudisha Kweli

    eleza __lt__(self, other):
        ikiwa sio isinstance(other, Set):
            rudisha NotImplemented
        rudisha len(self) < len(other) na self.__le__(other)

    eleza __gt__(self, other):
        ikiwa sio isinstance(other, Set):
            rudisha NotImplemented
        rudisha len(self) > len(other) na self.__ge__(other)

    eleza __ge__(self, other):
        ikiwa sio isinstance(other, Set):
            rudisha NotImplemented
        ikiwa len(self) < len(other):
            rudisha Uongo
        kila elem kwenye other:
            ikiwa elem haiko kwenye self:
                rudisha Uongo
        rudisha Kweli

    eleza __eq__(self, other):
        ikiwa sio isinstance(other, Set):
            rudisha NotImplemented
        rudisha len(self) == len(other) na self.__le__(other)

    @classmethod
    eleza _from_iterable(cls, it):
        '''Construct an instance of the kundi kutoka any iterable input.

        Must override this method ikiwa the kundi constructor signature
        does sio accept an iterable kila an input.
        '''
        rudisha cls(it)

    eleza __and__(self, other):
        ikiwa sio isinstance(other, Iterable):
            rudisha NotImplemented
        rudisha self._from_iterable(value kila value kwenye other ikiwa value kwenye self)

    __rand__ = __and__

    eleza isdisjoint(self, other):
        'Return Kweli ikiwa two sets have a null intersection.'
        kila value kwenye other:
            ikiwa value kwenye self:
                rudisha Uongo
        rudisha Kweli

    eleza __or__(self, other):
        ikiwa sio isinstance(other, Iterable):
            rudisha NotImplemented
        chain = (e kila s kwenye (self, other) kila e kwenye s)
        rudisha self._from_iterable(chain)

    __ror__ = __or__

    eleza __sub__(self, other):
        ikiwa sio isinstance(other, Set):
            ikiwa sio isinstance(other, Iterable):
                rudisha NotImplemented
            other = self._from_iterable(other)
        rudisha self._from_iterable(value kila value kwenye self
                                   ikiwa value haiko kwenye other)

    eleza __rsub__(self, other):
        ikiwa sio isinstance(other, Set):
            ikiwa sio isinstance(other, Iterable):
                rudisha NotImplemented
            other = self._from_iterable(other)
        rudisha self._from_iterable(value kila value kwenye other
                                   ikiwa value haiko kwenye self)

    eleza __xor__(self, other):
        ikiwa sio isinstance(other, Set):
            ikiwa sio isinstance(other, Iterable):
                rudisha NotImplemented
            other = self._from_iterable(other)
        rudisha (self - other) | (other - self)

    __rxor__ = __xor__

    eleza _hash(self):
        """Compute the hash value of a set.

        Note that we don't define __hash__: sio all sets are hashable.
        But ikiwa you define a hashable set type, its __hash__ should
        call this function.

        This must be compatible __eq__.

        All sets ought to compare equal ikiwa they contain the same
        elements, regardless of how they are implemented, na
        regardless of the order of the elements; so there's sio much
        freedom kila __eq__ ama __hash__.  We match the algorithm used
        by the built-in frozenset type.
        """
        MAX = sys.maxsize
        MASK = 2 * MAX + 1
        n = len(self)
        h = 1927868237 * (n + 1)
        h &= MASK
        kila x kwenye self:
            hx = hash(x)
            h ^= (hx ^ (hx << 16) ^ 89869747)  * 3644798167
            h &= MASK
        h = h * 69069 + 907133923
        h &= MASK
        ikiwa h > MAX:
            h -= MASK + 1
        ikiwa h == -1:
            h = 590923713
        rudisha h

Set.register(frozenset)


kundi MutableSet(Set):
    """A mutable set ni a finite, iterable container.

    This kundi provides concrete generic implementations of all
    methods tatizo kila __contains__, __iter__, __len__,
    add(), na discard().

    To override the comparisons (presumably kila speed, kama the
    semantics are fixed), all you have to do ni redefine __le__ na
    then the other operations will automatically follow suit.
    """

    __slots__ = ()

    @abstractmethod
    eleza add(self, value):
        """Add an element."""
        ashiria NotImplementedError

    @abstractmethod
    eleza discard(self, value):
        """Remove an element.  Do sio ashiria an exception ikiwa absent."""
        ashiria NotImplementedError

    eleza remove(self, value):
        """Remove an element. If sio a member, ashiria a KeyError."""
        ikiwa value haiko kwenye self:
            ashiria KeyError(value)
        self.discard(value)

    eleza pop(self):
        """Return the popped value.  Raise KeyError ikiwa empty."""
        it = iter(self)
        jaribu:
            value = next(it)
        tatizo StopIteration:
            ashiria KeyError kutoka Tupu
        self.discard(value)
        rudisha value

    eleza clear(self):
        """This ni slow (creates N new iterators!) but effective."""
        jaribu:
            wakati Kweli:
                self.pop()
        tatizo KeyError:
            pita

    eleza __ior__(self, it):
        kila value kwenye it:
            self.add(value)
        rudisha self

    eleza __iand__(self, it):
        kila value kwenye (self - it):
            self.discard(value)
        rudisha self

    eleza __ixor__(self, it):
        ikiwa it ni self:
            self.clear()
        isipokua:
            ikiwa sio isinstance(it, Set):
                it = self._from_iterable(it)
            kila value kwenye it:
                ikiwa value kwenye self:
                    self.discard(value)
                isipokua:
                    self.add(value)
        rudisha self

    eleza __isub__(self, it):
        ikiwa it ni self:
            self.clear()
        isipokua:
            kila value kwenye it:
                self.discard(value)
        rudisha self

MutableSet.register(set)


### MAPPINGS ###


kundi Mapping(Collection):

    __slots__ = ()

    """A Mapping ni a generic container kila associating key/value
    pairs.

    This kundi provides concrete generic implementations of all
    methods tatizo kila __getitem__, __iter__, na __len__.

    """

    @abstractmethod
    eleza __getitem__(self, key):
        ashiria KeyError

    eleza get(self, key, default=Tupu):
        'D.get(k[,d]) -> D[k] ikiwa k kwenye D, isipokua d.  d defaults to Tupu.'
        jaribu:
            rudisha self[key]
        tatizo KeyError:
            rudisha default

    eleza __contains__(self, key):
        jaribu:
            self[key]
        tatizo KeyError:
            rudisha Uongo
        isipokua:
            rudisha Kweli

    eleza keys(self):
        "D.keys() -> a set-like object providing a view on D's keys"
        rudisha KeysView(self)

    eleza items(self):
        "D.items() -> a set-like object providing a view on D's items"
        rudisha ItemsView(self)

    eleza values(self):
        "D.values() -> an object providing a view on D's values"
        rudisha ValuesView(self)

    eleza __eq__(self, other):
        ikiwa sio isinstance(other, Mapping):
            rudisha NotImplemented
        rudisha dict(self.items()) == dict(other.items())

    __reversed__ = Tupu

Mapping.register(mappingproxy)


kundi MappingView(Sized):

    __slots__ = '_mapping',

    eleza __init__(self, mapping):
        self._mapping = mapping

    eleza __len__(self):
        rudisha len(self._mapping)

    eleza __repr__(self):
        rudisha '{0.__class__.__name__}({0._mapping!r})'.format(self)


kundi KeysView(MappingView, Set):

    __slots__ = ()

    @classmethod
    eleza _from_iterable(self, it):
        rudisha set(it)

    eleza __contains__(self, key):
        rudisha key kwenye self._mapping

    eleza __iter__(self):
        tuma kutoka self._mapping

KeysView.register(dict_keys)


kundi ItemsView(MappingView, Set):

    __slots__ = ()

    @classmethod
    eleza _from_iterable(self, it):
        rudisha set(it)

    eleza __contains__(self, item):
        key, value = item
        jaribu:
            v = self._mapping[key]
        tatizo KeyError:
            rudisha Uongo
        isipokua:
            rudisha v ni value ama v == value

    eleza __iter__(self):
        kila key kwenye self._mapping:
            tuma (key, self._mapping[key])

ItemsView.register(dict_items)


kundi ValuesView(MappingView, Collection):

    __slots__ = ()

    eleza __contains__(self, value):
        kila key kwenye self._mapping:
            v = self._mapping[key]
            ikiwa v ni value ama v == value:
                rudisha Kweli
        rudisha Uongo

    eleza __iter__(self):
        kila key kwenye self._mapping:
            tuma self._mapping[key]

ValuesView.register(dict_values)


kundi MutableMapping(Mapping):

    __slots__ = ()

    """A MutableMapping ni a generic container kila associating
    key/value pairs.

    This kundi provides concrete generic implementations of all
    methods tatizo kila __getitem__, __setitem__, __delitem__,
    __iter__, na __len__.

    """

    @abstractmethod
    eleza __setitem__(self, key, value):
        ashiria KeyError

    @abstractmethod
    eleza __delitem__(self, key):
        ashiria KeyError

    __marker = object()

    eleza pop(self, key, default=__marker):
        '''D.pop(k[,d]) -> v, remove specified key na rudisha the corresponding value.
          If key ni sio found, d ni returned ikiwa given, otherwise KeyError ni raised.
        '''
        jaribu:
            value = self[key]
        tatizo KeyError:
            ikiwa default ni self.__marker:
                raise
            rudisha default
        isipokua:
            toa self[key]
            rudisha value

    eleza popitem(self):
        '''D.popitem() -> (k, v), remove na rudisha some (key, value) pair
           kama a 2-tuple; but ashiria KeyError ikiwa D ni empty.
        '''
        jaribu:
            key = next(iter(self))
        tatizo StopIteration:
            ashiria KeyError kutoka Tupu
        value = self[key]
        toa self[key]
        rudisha key, value

    eleza clear(self):
        'D.clear() -> Tupu.  Remove all items kutoka D.'
        jaribu:
            wakati Kweli:
                self.popitem()
        tatizo KeyError:
            pita

    eleza update(self, other=(), /, **kwds):
        ''' D.update([E, ]**F) -> Tupu.  Update D kutoka mapping/iterable E na F.
            If E present na has a .keys() method, does:     kila k kwenye E: D[k] = E[k]
            If E present na lacks .keys() method, does:     kila (k, v) kwenye E: D[k] = v
            In either case, this ni followed by: kila k, v kwenye F.items(): D[k] = v
        '''
        ikiwa isinstance(other, Mapping):
            kila key kwenye other:
                self[key] = other[key]
        lasivyo hasattr(other, "keys"):
            kila key kwenye other.keys():
                self[key] = other[key]
        isipokua:
            kila key, value kwenye other:
                self[key] = value
        kila key, value kwenye kwds.items():
            self[key] = value

    eleza setdefault(self, key, default=Tupu):
        'D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d ikiwa k haiko kwenye D'
        jaribu:
            rudisha self[key]
        tatizo KeyError:
            self[key] = default
        rudisha default

MutableMapping.register(dict)


### SEQUENCES ###


kundi Sequence(Reversible, Collection):

    """All the operations on a read-only sequence.

    Concrete subclasses must override __new__ ama __init__,
    __getitem__, na __len__.
    """

    __slots__ = ()

    @abstractmethod
    eleza __getitem__(self, index):
        ashiria IndexError

    eleza __iter__(self):
        i = 0
        jaribu:
            wakati Kweli:
                v = self[i]
                tuma v
                i += 1
        tatizo IndexError:
            return

    eleza __contains__(self, value):
        kila v kwenye self:
            ikiwa v ni value ama v == value:
                rudisha Kweli
        rudisha Uongo

    eleza __reversed__(self):
        kila i kwenye reversed(range(len(self))):
            tuma self[i]

    eleza index(self, value, start=0, stop=Tupu):
        '''S.index(value, [start, [stop]]) -> integer -- rudisha first index of value.
           Raises ValueError ikiwa the value ni sio present.

           Supporting start na stop arguments ni optional, but
           recommended.
        '''
        ikiwa start ni sio Tupu na start < 0:
            start = max(len(self) + start, 0)
        ikiwa stop ni sio Tupu na stop < 0:
            stop += len(self)

        i = start
        wakati stop ni Tupu ama i < stop:
            jaribu:
                v = self[i]
                ikiwa v ni value ama v == value:
                    rudisha i
            tatizo IndexError:
                koma
            i += 1
        ashiria ValueError

    eleza count(self, value):
        'S.count(value) -> integer -- rudisha number of occurrences of value'
        rudisha sum(1 kila v kwenye self ikiwa v ni value ama v == value)

Sequence.register(tuple)
Sequence.register(str)
Sequence.register(range)
Sequence.register(memoryview)


kundi ByteString(Sequence):

    """This unifies bytes na bytearray.

    XXX Should add all their methods.
    """

    __slots__ = ()

ByteString.register(bytes)
ByteString.register(bytearray)


kundi MutableSequence(Sequence):

    __slots__ = ()

    """All the operations on a read-write sequence.

    Concrete subclasses must provide __new__ ama __init__,
    __getitem__, __setitem__, __delitem__, __len__, na insert().

    """

    @abstractmethod
    eleza __setitem__(self, index, value):
        ashiria IndexError

    @abstractmethod
    eleza __delitem__(self, index):
        ashiria IndexError

    @abstractmethod
    eleza insert(self, index, value):
        'S.insert(index, value) -- insert value before index'
        ashiria IndexError

    eleza append(self, value):
        'S.append(value) -- append value to the end of the sequence'
        self.insert(len(self), value)

    eleza clear(self):
        'S.clear() -> Tupu -- remove all items kutoka S'
        jaribu:
            wakati Kweli:
                self.pop()
        tatizo IndexError:
            pita

    eleza reverse(self):
        'S.reverse() -- reverse *IN PLACE*'
        n = len(self)
        kila i kwenye range(n//2):
            self[i], self[n-i-1] = self[n-i-1], self[i]

    eleza extend(self, values):
        'S.extend(iterable) -- extend sequence by appending elements kutoka the iterable'
        ikiwa values ni self:
            values = list(values)
        kila v kwenye values:
            self.append(v)

    eleza pop(self, index=-1):
        '''S.pop([index]) -> item -- remove na rudisha item at index (default last).
           Raise IndexError ikiwa list ni empty ama index ni out of range.
        '''
        v = self[index]
        toa self[index]
        rudisha v

    eleza remove(self, value):
        '''S.remove(value) -- remove first occurrence of value.
           Raise ValueError ikiwa the value ni sio present.
        '''
        toa self[self.index(value)]

    eleza __iadd__(self, values):
        self.extend(values)
        rudisha self

MutableSequence.register(list)
MutableSequence.register(bytearray)  # Multiply inheriting, see ByteString
