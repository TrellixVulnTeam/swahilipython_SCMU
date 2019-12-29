'''This module implements specialized container datatypes providing
alternatives to Python's general purpose built-in containers, dict,
list, set, na tuple.

* namedtuple   factory function kila creating tuple subclasses ukijumuisha named fields
* deque        list-like container ukijumuisha fast appends na pops on either end
* ChainMap     dict-like kundi kila creating a single view of multiple mappings
* Counter      dict subkundi kila counting hashable objects
* OrderedDict  dict subkundi that remembers the order entries were added
* defaultdict  dict subkundi that calls a factory function to supply missing values
* UserDict     wrapper around dictionary objects kila easier dict subclassing
* UserList     wrapper around list objects kila easier list subclassing
* UserString   wrapper around string objects kila easier string subclassing

'''

__all__ = ['deque', 'defaultdict', 'namedtuple', 'UserDict', 'UserList',
            'UserString', 'Counter', 'OrderedDict', 'ChainMap']

agiza _collections_abc
kutoka operator agiza itemgetter kama _itemgetter, eq kama _eq
kutoka keyword agiza iskeyword kama _iskeyword
agiza sys kama _sys
agiza heapq kama _heapq
kutoka _weakref agiza proxy kama _proxy
kutoka itertools agiza repeat kama _repeat, chain kama _chain, starmap kama _starmap
kutoka reprlib agiza recursive_repr kama _recursive_repr

jaribu:
    kutoka _collections agiza deque
tatizo ImportError:
    pita
isipokua:
    _collections_abc.MutableSequence.register(deque)

jaribu:
    kutoka _collections agiza defaultdict
tatizo ImportError:
    pita


eleza __getattr__(name):
    # For backwards compatibility, endelea to make the collections ABCs
    # through Python 3.6 available through the collections module.
    # Note, no new collections ABCs were added kwenye Python 3.7
    ikiwa name kwenye _collections_abc.__all__:
        obj = getattr(_collections_abc, name)
        agiza warnings
        warnings.warn("Using ama agizaing the ABCs kutoka 'collections' instead "
                      "of kutoka 'collections.abc' ni deprecated since Python 3.3, "
                      "and kwenye 3.9 it will stop working",
                      DeprecationWarning, stacklevel=2)
        globals()[name] = obj
        rudisha obj
    ashiria AttributeError(f'module {__name__!r} has no attribute {name!r}')

################################################################################
### OrderedDict
################################################################################

kundi _OrderedDictKeysView(_collections_abc.KeysView):

    eleza __reversed__(self):
        tuma kutoka reversed(self._mapping)

kundi _OrderedDictItemsView(_collections_abc.ItemsView):

    eleza __reversed__(self):
        kila key kwenye reversed(self._mapping):
            tuma (key, self._mapping[key])

kundi _OrderedDictValuesView(_collections_abc.ValuesView):

    eleza __reversed__(self):
        kila key kwenye reversed(self._mapping):
            tuma self._mapping[key]

kundi _Link(object):
    __slots__ = 'prev', 'next', 'key', '__weakref__'

kundi OrderedDict(dict):
    'Dictionary that remembers insertion order'
    # An inherited dict maps keys to values.
    # The inherited dict provides __getitem__, __len__, __contains__, na get.
    # The remaining methods are order-aware.
    # Big-O running times kila all methods are the same kama regular dictionaries.

    # The internal self.__map dict maps keys to links kwenye a doubly linked list.
    # The circular doubly linked list starts na ends ukijumuisha a sentinel element.
    # The sentinel element never gets deleted (this simplifies the algorithm).
    # The sentinel ni kwenye self.__hardroot ukijumuisha a weakref proxy kwenye self.__root.
    # The prev links are weakref proxies (to prevent circular references).
    # Individual links are kept alive by the hard reference kwenye self.__map.
    # Those hard references disappear when a key ni deleted kutoka an OrderedDict.

    eleza __init__(self, other=(), /, **kwds):
        '''Initialize an ordered dictionary.  The signature ni the same as
        regular dictionaries.  Keyword argument order ni preserved.
        '''
        jaribu:
            self.__root
        tatizo AttributeError:
            self.__hardroot = _Link()
            self.__root = root = _proxy(self.__hardroot)
            root.prev = root.next = root
            self.__map = {}
        self.__update(other, **kwds)

    eleza __setitem__(self, key, value,
                    dict_setitem=dict.__setitem__, proxy=_proxy, Link=_Link):
        'od.__setitem__(i, y) <==> od[i]=y'
        # Setting a new item creates a new link at the end of the linked list,
        # na the inherited dictionary ni updated ukijumuisha the new key/value pair.
        ikiwa key haiko kwenye self:
            self.__map[key] = link = Link()
            root = self.__root
            last = root.prev
            link.prev, link.next, link.key = last, root, key
            last.next = link
            root.prev = proxy(link)
        dict_setitem(self, key, value)

    eleza __delitem__(self, key, dict_delitem=dict.__delitem__):
        'od.__delitem__(y) <==> toa od[y]'
        # Deleting an existing item uses self.__map to find the link which gets
        # removed by updating the links kwenye the predecessor na successor nodes.
        dict_delitem(self, key)
        link = self.__map.pop(key)
        link_prev = link.prev
        link_next = link.next
        link_prev.next = link_next
        link_next.prev = link_prev
        link.prev = Tupu
        link.next = Tupu

    eleza __iter__(self):
        'od.__iter__() <==> iter(od)'
        # Traverse the linked list kwenye order.
        root = self.__root
        curr = root.next
        wakati curr ni sio root:
            tuma curr.key
            curr = curr.next

    eleza __reversed__(self):
        'od.__reversed__() <==> reversed(od)'
        # Traverse the linked list kwenye reverse order.
        root = self.__root
        curr = root.prev
        wakati curr ni sio root:
            tuma curr.key
            curr = curr.prev

    eleza clear(self):
        'od.clear() -> Tupu.  Remove all items kutoka od.'
        root = self.__root
        root.prev = root.next = root
        self.__map.clear()
        dict.clear(self)

    eleza popitem(self, last=Kweli):
        '''Remove na rudisha a (key, value) pair kutoka the dictionary.

        Pairs are rudishaed kwenye LIFO order ikiwa last ni true ama FIFO order ikiwa false.
        '''
        ikiwa sio self:
            ashiria KeyError('dictionary ni empty')
        root = self.__root
        ikiwa last:
            link = root.prev
            link_prev = link.prev
            link_prev.next = root
            root.prev = link_prev
        isipokua:
            link = root.next
            link_next = link.next
            root.next = link_next
            link_next.prev = root
        key = link.key
        toa self.__map[key]
        value = dict.pop(self, key)
        rudisha key, value

    eleza move_to_end(self, key, last=Kweli):
        '''Move an existing element to the end (or beginning ikiwa last ni false).

        Raise KeyError ikiwa the element does sio exist.
        '''
        link = self.__map[key]
        link_prev = link.prev
        link_next = link.next
        soft_link = link_next.prev
        link_prev.next = link_next
        link_next.prev = link_prev
        root = self.__root
        ikiwa last:
            last = root.prev
            link.prev = last
            link.next = root
            root.prev = soft_link
            last.next = link
        isipokua:
            first = root.next
            link.prev = root
            link.next = first
            first.prev = soft_link
            root.next = link

    eleza __sizeof__(self):
        sizeof = _sys.getsizeof
        n = len(self) + 1                       # number of links including root
        size = sizeof(self.__dict__)            # instance dictionary
        size += sizeof(self.__map) * 2          # internal dict na inherited dict
        size += sizeof(self.__hardroot) * n     # link objects
        size += sizeof(self.__root) * n         # proxy objects
        rudisha size

    update = __update = _collections_abc.MutableMapping.update

    eleza keys(self):
        "D.keys() -> a set-like object providing a view on D's keys"
        rudisha _OrderedDictKeysView(self)

    eleza items(self):
        "D.items() -> a set-like object providing a view on D's items"
        rudisha _OrderedDictItemsView(self)

    eleza values(self):
        "D.values() -> an object providing a view on D's values"
        rudisha _OrderedDictValuesView(self)

    __ne__ = _collections_abc.MutableMapping.__ne__

    __marker = object()

    eleza pop(self, key, default=__marker):
        '''od.pop(k[,d]) -> v, remove specified key na rudisha the corresponding
        value.  If key ni sio found, d ni rudishaed ikiwa given, otherwise KeyError
        ni ashiriad.

        '''
        ikiwa key kwenye self:
            result = self[key]
            toa self[key]
            rudisha result
        ikiwa default ni self.__marker:
            ashiria KeyError(key)
        rudisha default

    eleza setdefault(self, key, default=Tupu):
        '''Insert key ukijumuisha a value of default ikiwa key ni haiko kwenye the dictionary.

        Return the value kila key ikiwa key ni kwenye the dictionary, isipokua default.
        '''
        ikiwa key kwenye self:
            rudisha self[key]
        self[key] = default
        rudisha default

    @_recursive_repr()
    eleza __repr__(self):
        'od.__repr__() <==> repr(od)'
        ikiwa sio self:
            rudisha '%s()' % (self.__class__.__name__,)
        rudisha '%s(%r)' % (self.__class__.__name__, list(self.items()))

    eleza __reduce__(self):
        'Return state information kila pickling'
        inst_dict = vars(self).copy()
        kila k kwenye vars(OrderedDict()):
            inst_dict.pop(k, Tupu)
        rudisha self.__class__, (), inst_dict ama Tupu, Tupu, iter(self.items())

    eleza copy(self):
        'od.copy() -> a shallow copy of od'
        rudisha self.__class__(self)

    @classmethod
    eleza kutokakeys(cls, iterable, value=Tupu):
        '''Create a new ordered dictionary ukijumuisha keys kutoka iterable na values set to value.
        '''
        self = cls()
        kila key kwenye iterable:
            self[key] = value
        rudisha self

    eleza __eq__(self, other):
        '''od.__eq__(y) <==> od==y.  Comparison to another OD ni order-sensitive
        wakati comparison to a regular mapping ni order-insensitive.

        '''
        ikiwa isinstance(other, OrderedDict):
            rudisha dict.__eq__(self, other) na all(map(_eq, self, other))
        rudisha dict.__eq__(self, other)


jaribu:
    kutoka _collections agiza OrderedDict
tatizo ImportError:
    # Leave the pure Python version kwenye place.
    pita


################################################################################
### namedtuple
################################################################################

jaribu:
    kutoka _collections agiza _tuplegetter
tatizo ImportError:
    _tuplegetter = lambda index, doc: property(_itemgetter(index), doc=doc)

eleza namedtuple(typename, field_names, *, rename=Uongo, defaults=Tupu, module=Tupu):
    """Returns a new subkundi of tuple ukijumuisha named fields.

    >>> Point = namedtuple('Point', ['x', 'y'])
    >>> Point.__doc__                   # docstring kila the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate ukijumuisha positional args ama keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    33
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessible by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d['x']
    11
    >>> Point(**d)                      # convert kutoka a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)               # _replace() ni like str.replace() but targets named fields
    Point(x=100, y=22)

    """

    # Validate the field names.  At the user's option, either generate an error
    # message ama automatically replace the field name ukijumuisha a valid name.
    ikiwa isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split()
    field_names = list(map(str, field_names))
    typename = _sys.intern(str(typename))

    ikiwa rename:
        seen = set()
        kila index, name kwenye enumerate(field_names):
            ikiwa (not name.isidentifier()
                ama _iskeyword(name)
                ama name.startswith('_')
                ama name kwenye seen):
                field_names[index] = f'_{index}'
            seen.add(name)

    kila name kwenye [typename] + field_names:
        ikiwa type(name) ni sio str:
            ashiria TypeError('Type names na field names must be strings')
        ikiwa sio name.isidentifier():
            ashiria ValueError('Type names na field names must be valid '
                             f'identifiers: {name!r}')
        ikiwa _iskeyword(name):
            ashiria ValueError('Type names na field names cannot be a '
                             f'keyword: {name!r}')

    seen = set()
    kila name kwenye field_names:
        ikiwa name.startswith('_') na sio rename:
            ashiria ValueError('Field names cannot start ukijumuisha an underscore: '
                             f'{name!r}')
        ikiwa name kwenye seen:
            ashiria ValueError(f'Encountered duplicate field name: {name!r}')
        seen.add(name)

    field_defaults = {}
    ikiwa defaults ni sio Tupu:
        defaults = tuple(defaults)
        ikiwa len(defaults) > len(field_names):
            ashiria TypeError('Got more default values than field names')
        field_defaults = dict(reversed(list(zip(reversed(field_names),
                                                reversed(defaults)))))

    # Variables used kwenye the methods na docstrings
    field_names = tuple(map(_sys.intern, field_names))
    num_fields = len(field_names)
    arg_list = repr(field_names).replace("'", "")[1:-1]
    repr_fmt = '(' + ', '.join(f'{name}=%r' kila name kwenye field_names) + ')'
    tuple_new = tuple.__new__
    _dict, _tuple, _len, _map, _zip = dict, tuple, len, map, zip

    # Create all the named tuple methods to be added to the kundi namespace

    s = f'eleza __new__(_cls, {arg_list}): rudisha _tuple_new(_cls, ({arg_list}))'
    namespace = {'_tuple_new': tuple_new, '__name__': f'namedtuple_{typename}'}
    # Note: exec() has the side-effect of interning the field names
    exec(s, namespace)
    __new__ = namespace['__new__']
    __new__.__doc__ = f'Create new instance of {typename}({arg_list})'
    ikiwa defaults ni sio Tupu:
        __new__.__defaults__ = defaults

    @classmethod
    eleza _make(cls, iterable):
        result = tuple_new(cls, iterable)
        ikiwa _len(result) != num_fields:
            ashiria TypeError(f'Expected {num_fields} arguments, got {len(result)}')
        rudisha result

    _make.__func__.__doc__ = (f'Make a new {typename} object kutoka a sequence '
                              'or iterable')

    eleza _replace(self, /, **kwds):
        result = self._make(_map(kwds.pop, field_names, self))
        ikiwa kwds:
            ashiria ValueError(f'Got unexpected field names: {list(kwds)!r}')
        rudisha result

    _replace.__doc__ = (f'Return a new {typename} object replacing specified '
                        'fields ukijumuisha new values')

    eleza __repr__(self):
        'Return a nicely formatted representation string'
        rudisha self.__class__.__name__ + repr_fmt % self

    eleza _asdict(self):
        'Return a new dict which maps field names to their values.'
        rudisha _dict(_zip(self._fields, self))

    eleza __getnewargs__(self):
        'Return self kama a plain tuple.  Used by copy na pickle.'
        rudisha _tuple(self)

    # Modify function metadata to help ukijumuisha introspection na debugging
    kila method kwenye (__new__, _make.__func__, _replace,
                   __repr__, _asdict, __getnewargs__):
        method.__qualname__ = f'{typename}.{method.__name__}'

    # Build-up the kundi namespace dictionary
    # na use type() to build the result class
    class_namespace = {
        '__doc__': f'{typename}({arg_list})',
        '__slots__': (),
        '_fields': field_names,
        '_field_defaults': field_defaults,
        # alternate spelling kila backward compatibility
        '_fields_defaults': field_defaults,
        '__new__': __new__,
        '_make': _make,
        '_replace': _replace,
        '__repr__': __repr__,
        '_asdict': _asdict,
        '__getnewargs__': __getnewargs__,
    }
    kila index, name kwenye enumerate(field_names):
        doc = _sys.intern(f'Alias kila field number {index}')
        class_namespace[name] = _tuplegetter(index, doc)

    result = type(typename, (tuple,), class_namespace)

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple ni created.  Bypita this step kwenye environments where
    # sys._getframe ni sio defined (Jython kila example) ama sys._getframe ni not
    # defined kila arguments greater than 0 (IronPython), ama where the user has
    # specified a particular module.
    ikiwa module ni Tupu:
        jaribu:
            module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        tatizo (AttributeError, ValueError):
            pita
    ikiwa module ni sio Tupu:
        result.__module__ = module

    rudisha result


########################################################################
###  Counter
########################################################################

eleza _count_elements(mapping, iterable):
    'Tally elements kutoka the iterable.'
    mapping_get = mapping.get
    kila elem kwenye iterable:
        mapping[elem] = mapping_get(elem, 0) + 1

jaribu:                                    # Load C helper function ikiwa available
    kutoka _collections agiza _count_elements
tatizo ImportError:
    pita

kundi Counter(dict):
    '''Dict subkundi kila counting hashable items.  Sometimes called a bag
    ama multiset.  Elements are stored kama dictionary keys na their counts
    are stored kama dictionary values.

    >>> c = Counter('abcdeabcdabcaba')  # count elements kutoka a string

    >>> c.most_common(3)                # three most common elements
    [('a', 5), ('b', 4), ('c', 3)]
    >>> sorted(c)                       # list all unique elements
    ['a', 'b', 'c', 'd', 'e']
    >>> ''.join(sorted(c.elements()))   # list elements ukijumuisha repetitions
    'aaaaabbbbcccdde'
    >>> sum(c.values())                 # total of all counts
    15

    >>> c['a']                          # count of letter 'a'
    5
    >>> kila elem kwenye 'shazam':           # update counts kutoka an iterable
    ...     c[elem] += 1                # by adding 1 to each element's count
    >>> c['a']                          # now there are seven 'a'
    7
    >>> toa c['b']                      # remove all 'b'
    >>> c['b']                          # now there are zero 'b'
    0

    >>> d = Counter('simsalabim')       # make another counter
    >>> c.update(d)                     # add kwenye the second counter
    >>> c['a']                          # now there are nine 'a'
    9

    >>> c.clear()                       # empty the counter
    >>> c
    Counter()

    Note:  If a count ni set to zero ama reduced to zero, it will remain
    kwenye the counter until the entry ni deleted ama the counter ni cleared:

    >>> c = Counter('aaabbc')
    >>> c['b'] -= 2                     # reduce the count of 'b' by two
    >>> c.most_common()                 # 'b' ni still in, but its count ni zero
    [('a', 3), ('c', 1), ('b', 0)]

    '''
    # References:
    #   http://en.wikipedia.org/wiki/Multiset
    #   http://www.gnu.org/software/smalltalk/manual-base/html_node/Bag.html
    #   http://www.demo2s.com/Tutorial/Cpp/0380__set-multiset/Catalog0380__set-multiset.htm
    #   http://code.activestate.com/recipes/259174/
    #   Knuth, TAOCP Vol. II section 4.6.3

    eleza __init__(self, iterable=Tupu, /, **kwds):
        '''Create a new, empty Counter object.  And ikiwa given, count elements
        kutoka an input iterable.  Or, initialize the count kutoka another mapping
        of elements to their counts.

        >>> c = Counter()                           # a new, empty counter
        >>> c = Counter('gallahad')                 # a new counter kutoka an iterable
        >>> c = Counter({'a': 4, 'b': 2})           # a new counter kutoka a mapping
        >>> c = Counter(a=4, b=2)                   # a new counter kutoka keyword args

        '''
        super(Counter, self).__init__()
        self.update(iterable, **kwds)

    eleza __missing__(self, key):
        'The count of elements haiko kwenye the Counter ni zero.'
        # Needed so that self[missing_item] does sio ashiria KeyError
        rudisha 0

    eleza most_common(self, n=Tupu):
        '''List the n most common elements na their counts kutoka the most
        common to the least.  If n ni Tupu, then list all element counts.

        >>> Counter('abracadabra').most_common(3)
        [('a', 5), ('b', 2), ('r', 2)]

        '''
        # Emulate Bag.sortedByCount kutoka Smalltalk
        ikiwa n ni Tupu:
            rudisha sorted(self.items(), key=_itemgetter(1), reverse=Kweli)
        rudisha _heapq.nlargest(n, self.items(), key=_itemgetter(1))

    eleza elements(self):
        '''Iterator over elements repeating each kama many times kama its count.

        >>> c = Counter('ABCABC')
        >>> sorted(c.elements())
        ['A', 'A', 'B', 'B', 'C', 'C']

        # Knuth's example kila prime factors of 1836:  2**2 * 3**3 * 17**1
        >>> prime_factors = Counter({2: 2, 3: 3, 17: 1})
        >>> product = 1
        >>> kila factor kwenye prime_factors.elements():     # loop over factors
        ...     product *= factor                       # na multiply them
        >>> product
        1836

        Note, ikiwa an element's count has been set to zero ama ni a negative
        number, elements() will ignore it.

        '''
        # Emulate Bag.do kutoka Smalltalk na Multiset.begin kutoka C++.
        rudisha _chain.kutoka_iterable(_starmap(_repeat, self.items()))

    # Override dict methods where necessary

    @classmethod
    eleza kutokakeys(cls, iterable, v=Tupu):
        # There ni no equivalent method kila counters because the semantics
        # would be ambiguous kwenye cases such kama Counter.kutokakeys('aaabbc', v=2).
        # Initializing counters to zero values isn't necessary because zero
        # ni already the default value kila counter lookups.  Initializing
        # to one ni easily accomplished ukijumuisha Counter(set(iterable)).  For
        # more exotic cases, create a dictionary first using a dictionary
        # comprehension ama dict.kutokakeys().
        ashiria NotImplementedError(
            'Counter.kutokakeys() ni undefined.  Use Counter(iterable) instead.')

    eleza update(self, iterable=Tupu, /, **kwds):
        '''Like dict.update() but add counts instead of replacing them.

        Source can be an iterable, a dictionary, ama another Counter instance.

        >>> c = Counter('which')
        >>> c.update('witch')           # add elements kutoka another iterable
        >>> d = Counter('watch')
        >>> c.update(d)                 # add elements kutoka another counter
        >>> c['h']                      # four 'h' kwenye which, witch, na watch
        4

        '''
        # The regular dict.update() operation makes no sense here because the
        # replace behavior results kwenye the some of original untouched counts
        # being mixed-in ukijumuisha all of the other counts kila a mismash that
        # doesn't have a straight-forward interpretation kwenye most counting
        # contexts.  Instead, we implement straight-addition.  Both the inputs
        # na outputs are allowed to contain zero na negative counts.

        ikiwa iterable ni sio Tupu:
            ikiwa isinstance(iterable, _collections_abc.Mapping):
                ikiwa self:
                    self_get = self.get
                    kila elem, count kwenye iterable.items():
                        self[elem] = count + self_get(elem, 0)
                isipokua:
                    super(Counter, self).update(iterable) # fast path when counter ni empty
            isipokua:
                _count_elements(self, iterable)
        ikiwa kwds:
            self.update(kwds)

    eleza subtract(self, iterable=Tupu, /, **kwds):
        '''Like dict.update() but subtracts counts instead of replacing them.
        Counts can be reduced below zero.  Both the inputs na outputs are
        allowed to contain zero na negative counts.

        Source can be an iterable, a dictionary, ama another Counter instance.

        >>> c = Counter('which')
        >>> c.subtract('witch')             # subtract elements kutoka another iterable
        >>> c.subtract(Counter('watch'))    # subtract elements kutoka another counter
        >>> c['h']                          # 2 kwenye which, minus 1 kwenye witch, minus 1 kwenye watch
        0
        >>> c['w']                          # 1 kwenye which, minus 1 kwenye witch, minus 1 kwenye watch
        -1

        '''
        ikiwa iterable ni sio Tupu:
            self_get = self.get
            ikiwa isinstance(iterable, _collections_abc.Mapping):
                kila elem, count kwenye iterable.items():
                    self[elem] = self_get(elem, 0) - count
            isipokua:
                kila elem kwenye iterable:
                    self[elem] = self_get(elem, 0) - 1
        ikiwa kwds:
            self.subtract(kwds)

    eleza copy(self):
        'Return a shallow copy.'
        rudisha self.__class__(self)

    eleza __reduce__(self):
        rudisha self.__class__, (dict(self),)

    eleza __delitem__(self, elem):
        'Like dict.__delitem__() but does sio ashiria KeyError kila missing values.'
        ikiwa elem kwenye self:
            super().__delitem__(elem)

    eleza __repr__(self):
        ikiwa sio self:
            rudisha '%s()' % self.__class__.__name__
        jaribu:
            items = ', '.join(map('%r: %r'.__mod__, self.most_common()))
            rudisha '%s({%s})' % (self.__class__.__name__, items)
        tatizo TypeError:
            # handle case where values are sio orderable
            rudisha '{0}({1!r})'.format(self.__class__.__name__, dict(self))

    # Multiset-style mathematical operations discussed in:
    #       Knuth TAOCP Volume II section 4.6.3 exercise 19
    #       na at http://en.wikipedia.org/wiki/Multiset
    #
    # Outputs guaranteed to only include positive counts.
    #
    # To strip negative na zero counts, add-in an empty counter:
    #       c += Counter()

    eleza __add__(self, other):
        '''Add counts kutoka two counters.

        >>> Counter('abbb') + Counter('bcc')
        Counter({'b': 4, 'c': 2, 'a': 1})

        '''
        ikiwa sio isinstance(other, Counter):
            rudisha NotImplemented
        result = Counter()
        kila elem, count kwenye self.items():
            newcount = count + other[elem]
            ikiwa newcount > 0:
                result[elem] = newcount
        kila elem, count kwenye other.items():
            ikiwa elem haiko kwenye self na count > 0:
                result[elem] = count
        rudisha result

    eleza __sub__(self, other):
        ''' Subtract count, but keep only results ukijumuisha positive counts.

        >>> Counter('abbbc') - Counter('bccd')
        Counter({'b': 2, 'a': 1})

        '''
        ikiwa sio isinstance(other, Counter):
            rudisha NotImplemented
        result = Counter()
        kila elem, count kwenye self.items():
            newcount = count - other[elem]
            ikiwa newcount > 0:
                result[elem] = newcount
        kila elem, count kwenye other.items():
            ikiwa elem haiko kwenye self na count < 0:
                result[elem] = 0 - count
        rudisha result

    eleza __or__(self, other):
        '''Union ni the maximum of value kwenye either of the input counters.

        >>> Counter('abbb') | Counter('bcc')
        Counter({'b': 3, 'c': 2, 'a': 1})

        '''
        ikiwa sio isinstance(other, Counter):
            rudisha NotImplemented
        result = Counter()
        kila elem, count kwenye self.items():
            other_count = other[elem]
            newcount = other_count ikiwa count < other_count isipokua count
            ikiwa newcount > 0:
                result[elem] = newcount
        kila elem, count kwenye other.items():
            ikiwa elem haiko kwenye self na count > 0:
                result[elem] = count
        rudisha result

    eleza __and__(self, other):
        ''' Intersection ni the minimum of corresponding counts.

        >>> Counter('abbb') & Counter('bcc')
        Counter({'b': 1})

        '''
        ikiwa sio isinstance(other, Counter):
            rudisha NotImplemented
        result = Counter()
        kila elem, count kwenye self.items():
            other_count = other[elem]
            newcount = count ikiwa count < other_count isipokua other_count
            ikiwa newcount > 0:
                result[elem] = newcount
        rudisha result

    eleza __pos__(self):
        'Adds an empty counter, effectively stripping negative na zero counts'
        result = Counter()
        kila elem, count kwenye self.items():
            ikiwa count > 0:
                result[elem] = count
        rudisha result

    eleza __neg__(self):
        '''Subtracts kutoka an empty counter.  Strips positive na zero counts,
        na flips the sign on negative counts.

        '''
        result = Counter()
        kila elem, count kwenye self.items():
            ikiwa count < 0:
                result[elem] = 0 - count
        rudisha result

    eleza _keep_positive(self):
        '''Internal method to strip elements ukijumuisha a negative ama zero count'''
        nonpositive = [elem kila elem, count kwenye self.items() ikiwa sio count > 0]
        kila elem kwenye nonpositive:
            toa self[elem]
        rudisha self

    eleza __iadd__(self, other):
        '''Inplace add kutoka another counter, keeping only positive counts.

        >>> c = Counter('abbb')
        >>> c += Counter('bcc')
        >>> c
        Counter({'b': 4, 'c': 2, 'a': 1})

        '''
        kila elem, count kwenye other.items():
            self[elem] += count
        rudisha self._keep_positive()

    eleza __isub__(self, other):
        '''Inplace subtract counter, but keep only results ukijumuisha positive counts.

        >>> c = Counter('abbbc')
        >>> c -= Counter('bccd')
        >>> c
        Counter({'b': 2, 'a': 1})

        '''
        kila elem, count kwenye other.items():
            self[elem] -= count
        rudisha self._keep_positive()

    eleza __ior__(self, other):
        '''Inplace union ni the maximum of value kutoka either counter.

        >>> c = Counter('abbb')
        >>> c |= Counter('bcc')
        >>> c
        Counter({'b': 3, 'c': 2, 'a': 1})

        '''
        kila elem, other_count kwenye other.items():
            count = self[elem]
            ikiwa other_count > count:
                self[elem] = other_count
        rudisha self._keep_positive()

    eleza __iand__(self, other):
        '''Inplace intersection ni the minimum of corresponding counts.

        >>> c = Counter('abbb')
        >>> c &= Counter('bcc')
        >>> c
        Counter({'b': 1})

        '''
        kila elem, count kwenye self.items():
            other_count = other[elem]
            ikiwa other_count < count:
                self[elem] = other_count
        rudisha self._keep_positive()


########################################################################
###  ChainMap
########################################################################

kundi ChainMap(_collections_abc.MutableMapping):
    ''' A ChainMap groups multiple dicts (or other mappings) together
    to create a single, updateable view.

    The underlying mappings are stored kwenye a list.  That list ni public na can
    be accessed ama updated using the *maps* attribute.  There ni no other
    state.

    Lookups search the underlying mappings successively until a key ni found.
    In contrast, writes, updates, na deletions only operate on the first
    mapping.

    '''

    eleza __init__(self, *maps):
        '''Initialize a ChainMap by setting *maps* to the given mappings.
        If no mappings are provided, a single empty dictionary ni used.

        '''
        self.maps = list(maps) ama [{}]          # always at least one map

    eleza __missing__(self, key):
        ashiria KeyError(key)

    eleza __getitem__(self, key):
        kila mapping kwenye self.maps:
            jaribu:
                rudisha mapping[key]             # can't use 'key kwenye mapping' ukijumuisha defaultdict
            tatizo KeyError:
                pita
        rudisha self.__missing__(key)            # support subclasses that define __missing__

    eleza get(self, key, default=Tupu):
        rudisha self[key] ikiwa key kwenye self isipokua default

    eleza __len__(self):
        rudisha len(set().union(*self.maps))     # reuses stored hash values ikiwa possible

    eleza __iter__(self):
        d = {}
        kila mapping kwenye reversed(self.maps):
            d.update(mapping)                   # reuses stored hash values ikiwa possible
        rudisha iter(d)

    eleza __contains__(self, key):
        rudisha any(key kwenye m kila m kwenye self.maps)

    eleza __bool__(self):
        rudisha any(self.maps)

    @_recursive_repr()
    eleza __repr__(self):
        rudisha f'{self.__class__.__name__}({", ".join(map(repr, self.maps))})'

    @classmethod
    eleza kutokakeys(cls, iterable, *args):
        'Create a ChainMap ukijumuisha a single dict created kutoka the iterable.'
        rudisha cls(dict.kutokakeys(iterable, *args))

    eleza copy(self):
        'New ChainMap ama subkundi ukijumuisha a new copy of maps[0] na refs to maps[1:]'
        rudisha self.__class__(self.maps[0].copy(), *self.maps[1:])

    __copy__ = copy

    eleza new_child(self, m=Tupu):                # like Django's Context.push()
        '''New ChainMap ukijumuisha a new map followed by all previous maps.
        If no map ni provided, an empty dict ni used.
        '''
        ikiwa m ni Tupu:
            m = {}
        rudisha self.__class__(m, *self.maps)

    @property
    eleza parents(self):                          # like Django's Context.pop()
        'New ChainMap kutoka maps[1:].'
        rudisha self.__class__(*self.maps[1:])

    eleza __setitem__(self, key, value):
        self.maps[0][key] = value

    eleza __delitem__(self, key):
        jaribu:
            toa self.maps[0][key]
        tatizo KeyError:
            ashiria KeyError('Key sio found kwenye the first mapping: {!r}'.format(key))

    eleza popitem(self):
        'Remove na rudisha an item pair kutoka maps[0]. Raise KeyError ni maps[0] ni empty.'
        jaribu:
            rudisha self.maps[0].popitem()
        tatizo KeyError:
            ashiria KeyError('No keys found kwenye the first mapping.')

    eleza pop(self, key, *args):
        'Remove *key* kutoka maps[0] na rudisha its value. Raise KeyError ikiwa *key* haiko kwenye maps[0].'
        jaribu:
            rudisha self.maps[0].pop(key, *args)
        tatizo KeyError:
            ashiria KeyError('Key sio found kwenye the first mapping: {!r}'.format(key))

    eleza clear(self):
        'Clear maps[0], leaving maps[1:] intact.'
        self.maps[0].clear()


################################################################################
### UserDict
################################################################################

kundi UserDict(_collections_abc.MutableMapping):

    # Start by filling-out the abstract methods
    eleza __init__(*args, **kwargs):
        ikiwa sio args:
            ashiria TypeError("descriptor '__init__' of 'UserDict' object "
                            "needs an argument")
        self, *args = args
        ikiwa len(args) > 1:
            ashiria TypeError('expected at most 1 arguments, got %d' % len(args))
        ikiwa args:
            dict = args[0]
        lasivyo 'dict' kwenye kwargs:
            dict = kwargs.pop('dict')
            agiza warnings
            warnings.warn("Passing 'dict' kama keyword argument ni deprecated",
                          DeprecationWarning, stacklevel=2)
        isipokua:
            dict = Tupu
        self.data = {}
        ikiwa dict ni sio Tupu:
            self.update(dict)
        ikiwa kwargs:
            self.update(kwargs)
    __init__.__text_signature__ = '($self, dict=Tupu, /, **kwargs)'

    eleza __len__(self): rudisha len(self.data)
    eleza __getitem__(self, key):
        ikiwa key kwenye self.data:
            rudisha self.data[key]
        ikiwa hasattr(self.__class__, "__missing__"):
            rudisha self.__class__.__missing__(self, key)
        ashiria KeyError(key)
    eleza __setitem__(self, key, item): self.data[key] = item
    eleza __delitem__(self, key): toa self.data[key]
    eleza __iter__(self):
        rudisha iter(self.data)

    # Modify __contains__ to work correctly when __missing__ ni present
    eleza __contains__(self, key):
        rudisha key kwenye self.data

    # Now, add the methods kwenye dicts but haiko kwenye MutableMapping
    eleza __repr__(self): rudisha repr(self.data)
    eleza __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy na avoid triggering descriptors
        inst.__dict__["data"] = self.__dict__["data"].copy()
        rudisha inst

    eleza copy(self):
        ikiwa self.__class__ ni UserDict:
            rudisha UserDict(self.data.copy())
        agiza copy
        data = self.data
        jaribu:
            self.data = {}
            c = copy.copy(self)
        mwishowe:
            self.data = data
        c.update(self)
        rudisha c

    @classmethod
    eleza kutokakeys(cls, iterable, value=Tupu):
        d = cls()
        kila key kwenye iterable:
            d[key] = value
        rudisha d



################################################################################
### UserList
################################################################################

kundi UserList(_collections_abc.MutableSequence):
    """A more ama less complete user-defined wrapper around list objects."""
    eleza __init__(self, initlist=Tupu):
        self.data = []
        ikiwa initlist ni sio Tupu:
            # XXX should this accept an arbitrary sequence?
            ikiwa type(initlist) == type(self.data):
                self.data[:] = initlist
            lasivyo isinstance(initlist, UserList):
                self.data[:] = initlist.data[:]
            isipokua:
                self.data = list(initlist)
    eleza __repr__(self): rudisha repr(self.data)
    eleza __lt__(self, other): rudisha self.data <  self.__cast(other)
    eleza __le__(self, other): rudisha self.data <= self.__cast(other)
    eleza __eq__(self, other): rudisha self.data == self.__cast(other)
    eleza __gt__(self, other): rudisha self.data >  self.__cast(other)
    eleza __ge__(self, other): rudisha self.data >= self.__cast(other)
    eleza __cast(self, other):
        rudisha other.data ikiwa isinstance(other, UserList) isipokua other
    eleza __contains__(self, item): rudisha item kwenye self.data
    eleza __len__(self): rudisha len(self.data)
    eleza __getitem__(self, i):
        ikiwa isinstance(i, slice):
            rudisha self.__class__(self.data[i])
        isipokua:
            rudisha self.data[i]
    eleza __setitem__(self, i, item): self.data[i] = item
    eleza __delitem__(self, i): toa self.data[i]
    eleza __add__(self, other):
        ikiwa isinstance(other, UserList):
            rudisha self.__class__(self.data + other.data)
        lasivyo isinstance(other, type(self.data)):
            rudisha self.__class__(self.data + other)
        rudisha self.__class__(self.data + list(other))
    eleza __radd__(self, other):
        ikiwa isinstance(other, UserList):
            rudisha self.__class__(other.data + self.data)
        lasivyo isinstance(other, type(self.data)):
            rudisha self.__class__(other + self.data)
        rudisha self.__class__(list(other) + self.data)
    eleza __iadd__(self, other):
        ikiwa isinstance(other, UserList):
            self.data += other.data
        lasivyo isinstance(other, type(self.data)):
            self.data += other
        isipokua:
            self.data += list(other)
        rudisha self
    eleza __mul__(self, n):
        rudisha self.__class__(self.data*n)
    __rmul__ = __mul__
    eleza __imul__(self, n):
        self.data *= n
        rudisha self
    eleza __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy na avoid triggering descriptors
        inst.__dict__["data"] = self.__dict__["data"][:]
        rudisha inst
    eleza append(self, item): self.data.append(item)
    eleza insert(self, i, item): self.data.insert(i, item)
    eleza pop(self, i=-1): rudisha self.data.pop(i)
    eleza remove(self, item): self.data.remove(item)
    eleza clear(self): self.data.clear()
    eleza copy(self): rudisha self.__class__(self)
    eleza count(self, item): rudisha self.data.count(item)
    eleza index(self, item, *args): rudisha self.data.index(item, *args)
    eleza reverse(self): self.data.reverse()
    eleza sort(self, /, *args, **kwds): self.data.sort(*args, **kwds)
    eleza extend(self, other):
        ikiwa isinstance(other, UserList):
            self.data.extend(other.data)
        isipokua:
            self.data.extend(other)



################################################################################
### UserString
################################################################################

kundi UserString(_collections_abc.Sequence):
    eleza __init__(self, seq):
        ikiwa isinstance(seq, str):
            self.data = seq
        lasivyo isinstance(seq, UserString):
            self.data = seq.data[:]
        isipokua:
            self.data = str(seq)
    eleza __str__(self): rudisha str(self.data)
    eleza __repr__(self): rudisha repr(self.data)
    eleza __int__(self): rudisha int(self.data)
    eleza __float__(self): rudisha float(self.data)
    eleza __complex__(self): rudisha complex(self.data)
    eleza __hash__(self): rudisha hash(self.data)
    eleza __getnewargs__(self):
        rudisha (self.data[:],)

    eleza __eq__(self, string):
        ikiwa isinstance(string, UserString):
            rudisha self.data == string.data
        rudisha self.data == string
    eleza __lt__(self, string):
        ikiwa isinstance(string, UserString):
            rudisha self.data < string.data
        rudisha self.data < string
    eleza __le__(self, string):
        ikiwa isinstance(string, UserString):
            rudisha self.data <= string.data
        rudisha self.data <= string
    eleza __gt__(self, string):
        ikiwa isinstance(string, UserString):
            rudisha self.data > string.data
        rudisha self.data > string
    eleza __ge__(self, string):
        ikiwa isinstance(string, UserString):
            rudisha self.data >= string.data
        rudisha self.data >= string

    eleza __contains__(self, char):
        ikiwa isinstance(char, UserString):
            char = char.data
        rudisha char kwenye self.data

    eleza __len__(self): rudisha len(self.data)
    eleza __getitem__(self, index): rudisha self.__class__(self.data[index])
    eleza __add__(self, other):
        ikiwa isinstance(other, UserString):
            rudisha self.__class__(self.data + other.data)
        lasivyo isinstance(other, str):
            rudisha self.__class__(self.data + other)
        rudisha self.__class__(self.data + str(other))
    eleza __radd__(self, other):
        ikiwa isinstance(other, str):
            rudisha self.__class__(other + self.data)
        rudisha self.__class__(str(other) + self.data)
    eleza __mul__(self, n):
        rudisha self.__class__(self.data*n)
    __rmul__ = __mul__
    eleza __mod__(self, args):
        rudisha self.__class__(self.data % args)
    eleza __rmod__(self, template):
        rudisha self.__class__(str(template) % self)
    # the following methods are defined kwenye alphabetical order:
    eleza capitalize(self): rudisha self.__class__(self.data.capitalize())
    eleza casefold(self):
        rudisha self.__class__(self.data.casefold())
    eleza center(self, width, *args):
        rudisha self.__class__(self.data.center(width, *args))
    eleza count(self, sub, start=0, end=_sys.maxsize):
        ikiwa isinstance(sub, UserString):
            sub = sub.data
        rudisha self.data.count(sub, start, end)
    eleza encode(self, encoding='utf-8', errors='strict'):
        encoding = 'utf-8' ikiwa encoding ni Tupu isipokua encoding
        errors = 'strict' ikiwa errors ni Tupu isipokua errors
        rudisha self.data.encode(encoding, errors)
    eleza endswith(self, suffix, start=0, end=_sys.maxsize):
        rudisha self.data.endswith(suffix, start, end)
    eleza expandtabs(self, tabsize=8):
        rudisha self.__class__(self.data.expandtabs(tabsize))
    eleza find(self, sub, start=0, end=_sys.maxsize):
        ikiwa isinstance(sub, UserString):
            sub = sub.data
        rudisha self.data.find(sub, start, end)
    eleza format(self, /, *args, **kwds):
        rudisha self.data.format(*args, **kwds)
    eleza format_map(self, mapping):
        rudisha self.data.format_map(mapping)
    eleza index(self, sub, start=0, end=_sys.maxsize):
        rudisha self.data.index(sub, start, end)
    eleza isalpha(self): rudisha self.data.isalpha()
    eleza isalnum(self): rudisha self.data.isalnum()
    eleza isascii(self): rudisha self.data.isascii()
    eleza isdecimal(self): rudisha self.data.isdecimal()
    eleza isdigit(self): rudisha self.data.isdigit()
    eleza isidentifier(self): rudisha self.data.isidentifier()
    eleza islower(self): rudisha self.data.islower()
    eleza isnumeric(self): rudisha self.data.isnumeric()
    eleza isprintable(self): rudisha self.data.isprintable()
    eleza isspace(self): rudisha self.data.isspace()
    eleza istitle(self): rudisha self.data.istitle()
    eleza isupper(self): rudisha self.data.isupper()
    eleza join(self, seq): rudisha self.data.join(seq)
    eleza ljust(self, width, *args):
        rudisha self.__class__(self.data.ljust(width, *args))
    eleza lower(self): rudisha self.__class__(self.data.lower())
    eleza lstrip(self, chars=Tupu): rudisha self.__class__(self.data.lstrip(chars))
    maketrans = str.maketrans
    eleza partition(self, sep):
        rudisha self.data.partition(sep)
    eleza replace(self, old, new, maxsplit=-1):
        ikiwa isinstance(old, UserString):
            old = old.data
        ikiwa isinstance(new, UserString):
            new = new.data
        rudisha self.__class__(self.data.replace(old, new, maxsplit))
    eleza rfind(self, sub, start=0, end=_sys.maxsize):
        ikiwa isinstance(sub, UserString):
            sub = sub.data
        rudisha self.data.rfind(sub, start, end)
    eleza rindex(self, sub, start=0, end=_sys.maxsize):
        rudisha self.data.rindex(sub, start, end)
    eleza rjust(self, width, *args):
        rudisha self.__class__(self.data.rjust(width, *args))
    eleza rpartition(self, sep):
        rudisha self.data.rpartition(sep)
    eleza rstrip(self, chars=Tupu):
        rudisha self.__class__(self.data.rstrip(chars))
    eleza split(self, sep=Tupu, maxsplit=-1):
        rudisha self.data.split(sep, maxsplit)
    eleza rsplit(self, sep=Tupu, maxsplit=-1):
        rudisha self.data.rsplit(sep, maxsplit)
    eleza splitlines(self, keepends=Uongo): rudisha self.data.splitlines(keepends)
    eleza startswith(self, prefix, start=0, end=_sys.maxsize):
        rudisha self.data.startswith(prefix, start, end)
    eleza strip(self, chars=Tupu): rudisha self.__class__(self.data.strip(chars))
    eleza swapcase(self): rudisha self.__class__(self.data.swapcase())
    eleza title(self): rudisha self.__class__(self.data.title())
    eleza translate(self, *args):
        rudisha self.__class__(self.data.translate(*args))
    eleza upper(self): rudisha self.__class__(self.data.upper())
    eleza zfill(self, width): rudisha self.__class__(self.data.zfill(width))
