'''This module implements specialized container datatypes providing
alternatives to Python's general purpose built-in containers, dict,
list, set, and tuple.

* namedtuple   factory function for creating tuple subclasses with named fields
* deque        list-like container with fast appends and pops on either end
* ChainMap     dict-like kundi for creating a single view of multiple mappings
* Counter      dict subkundi for counting hashable objects
* OrderedDict  dict subkundi that remembers the order entries were added
* defaultdict  dict subkundi that calls a factory function to supply missing values
* UserDict     wrapper around dictionary objects for easier dict subclassing
* UserList     wrapper around list objects for easier list subclassing
* UserString   wrapper around string objects for easier string subclassing

'''

__all__ = ['deque', 'defaultdict', 'namedtuple', 'UserDict', 'UserList',
            'UserString', 'Counter', 'OrderedDict', 'ChainMap']

agiza _collections_abc
kutoka operator agiza itemgetter as _itemgetter, eq as _eq
kutoka keyword agiza iskeyword as _iskeyword
agiza sys as _sys
agiza heapq as _heapq
kutoka _weakref agiza proxy as _proxy
kutoka itertools agiza repeat as _repeat, chain as _chain, starmap as _starmap
kutoka reprlib agiza recursive_repr as _recursive_repr

try:
    kutoka _collections agiza deque
except ImportError:
    pass
else:
    _collections_abc.MutableSequence.register(deque)

try:
    kutoka _collections agiza defaultdict
except ImportError:
    pass


eleza __getattr__(name):
    # For backwards compatibility, continue to make the collections ABCs
    # through Python 3.6 available through the collections module.
    # Note, no new collections ABCs were added in Python 3.7
    ikiwa name in _collections_abc.__all__:
        obj = getattr(_collections_abc, name)
        agiza warnings
        warnings.warn("Using or agizaing the ABCs kutoka 'collections' instead "
                      "of kutoka 'collections.abc' is deprecated since Python 3.3, "
                      "and in 3.9 it will stop working",
                      DeprecationWarning, stacklevel=2)
        globals()[name] = obj
        rudisha obj
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

################################################################################
### OrderedDict
################################################################################

kundi _OrderedDictKeysView(_collections_abc.KeysView):

    eleza __reversed__(self):
        yield kutoka reversed(self._mapping)

kundi _OrderedDictItemsView(_collections_abc.ItemsView):

    eleza __reversed__(self):
        for key in reversed(self._mapping):
            yield (key, self._mapping[key])

kundi _OrderedDictValuesView(_collections_abc.ValuesView):

    eleza __reversed__(self):
        for key in reversed(self._mapping):
            yield self._mapping[key]

kundi _Link(object):
    __slots__ = 'prev', 'next', 'key', '__weakref__'

kundi OrderedDict(dict):
    'Dictionary that remembers insertion order'
    # An inherited dict maps keys to values.
    # The inherited dict provides __getitem__, __len__, __contains__, and get.
    # The remaining methods are order-aware.
    # Big-O running times for all methods are the same as regular dictionaries.

    # The internal self.__map dict maps keys to links in a doubly linked list.
    # The circular doubly linked list starts and ends with a sentinel element.
    # The sentinel element never gets deleted (this simplifies the algorithm).
    # The sentinel is in self.__hardroot with a weakref proxy in self.__root.
    # The prev links are weakref proxies (to prevent circular references).
    # Individual links are kept alive by the hard reference in self.__map.
    # Those hard references disappear when a key is deleted kutoka an OrderedDict.

    eleza __init__(self, other=(), /, **kwds):
        '''Initialize an ordered dictionary.  The signature is the same as
        regular dictionaries.  Keyword argument order is preserved.
        '''
        try:
            self.__root
        except AttributeError:
            self.__hardroot = _Link()
            self.__root = root = _proxy(self.__hardroot)
            root.prev = root.next = root
            self.__map = {}
        self.__update(other, **kwds)

    eleza __setitem__(self, key, value,
                    dict_setitem=dict.__setitem__, proxy=_proxy, Link=_Link):
        'od.__setitem__(i, y) <==> od[i]=y'
        # Setting a new item creates a new link at the end of the linked list,
        # and the inherited dictionary is updated with the new key/value pair.
        ikiwa key not in self:
            self.__map[key] = link = Link()
            root = self.__root
            last = root.prev
            link.prev, link.next, link.key = last, root, key
            last.next = link
            root.prev = proxy(link)
        dict_setitem(self, key, value)

    eleza __delitem__(self, key, dict_delitem=dict.__delitem__):
        'od.__delitem__(y) <==> del od[y]'
        # Deleting an existing item uses self.__map to find the link which gets
        # removed by updating the links in the predecessor and successor nodes.
        dict_delitem(self, key)
        link = self.__map.pop(key)
        link_prev = link.prev
        link_next = link.next
        link_prev.next = link_next
        link_next.prev = link_prev
        link.prev = None
        link.next = None

    eleza __iter__(self):
        'od.__iter__() <==> iter(od)'
        # Traverse the linked list in order.
        root = self.__root
        curr = root.next
        while curr is not root:
            yield curr.key
            curr = curr.next

    eleza __reversed__(self):
        'od.__reversed__() <==> reversed(od)'
        # Traverse the linked list in reverse order.
        root = self.__root
        curr = root.prev
        while curr is not root:
            yield curr.key
            curr = curr.prev

    eleza clear(self):
        'od.clear() -> None.  Remove all items kutoka od.'
        root = self.__root
        root.prev = root.next = root
        self.__map.clear()
        dict.clear(self)

    eleza popitem(self, last=True):
        '''Remove and rudisha a (key, value) pair kutoka the dictionary.

        Pairs are returned in LIFO order ikiwa last is true or FIFO order ikiwa false.
        '''
        ikiwa not self:
            raise KeyError('dictionary is empty')
        root = self.__root
        ikiwa last:
            link = root.prev
            link_prev = link.prev
            link_prev.next = root
            root.prev = link_prev
        else:
            link = root.next
            link_next = link.next
            root.next = link_next
            link_next.prev = root
        key = link.key
        del self.__map[key]
        value = dict.pop(self, key)
        rudisha key, value

    eleza move_to_end(self, key, last=True):
        '''Move an existing element to the end (or beginning ikiwa last is false).

        Raise KeyError ikiwa the element does not exist.
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
        else:
            first = root.next
            link.prev = root
            link.next = first
            first.prev = soft_link
            root.next = link

    eleza __sizeof__(self):
        sizeof = _sys.getsizeof
        n = len(self) + 1                       # number of links including root
        size = sizeof(self.__dict__)            # instance dictionary
        size += sizeof(self.__map) * 2          # internal dict and inherited dict
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
        '''od.pop(k[,d]) -> v, remove specified key and rudisha the corresponding
        value.  If key is not found, d is returned ikiwa given, otherwise KeyError
        is raised.

        '''
        ikiwa key in self:
            result = self[key]
            del self[key]
            rudisha result
        ikiwa default is self.__marker:
            raise KeyError(key)
        rudisha default

    eleza setdefault(self, key, default=None):
        '''Insert key with a value of default ikiwa key is not in the dictionary.

        Return the value for key ikiwa key is in the dictionary, else default.
        '''
        ikiwa key in self:
            rudisha self[key]
        self[key] = default
        rudisha default

    @_recursive_repr()
    eleza __repr__(self):
        'od.__repr__() <==> repr(od)'
        ikiwa not self:
            rudisha '%s()' % (self.__class__.__name__,)
        rudisha '%s(%r)' % (self.__class__.__name__, list(self.items()))

    eleza __reduce__(self):
        'Return state information for pickling'
        inst_dict = vars(self).copy()
        for k in vars(OrderedDict()):
            inst_dict.pop(k, None)
        rudisha self.__class__, (), inst_dict or None, None, iter(self.items())

    eleza copy(self):
        'od.copy() -> a shallow copy of od'
        rudisha self.__class__(self)

    @classmethod
    eleza kutokakeys(cls, iterable, value=None):
        '''Create a new ordered dictionary with keys kutoka iterable and values set to value.
        '''
        self = cls()
        for key in iterable:
            self[key] = value
        rudisha self

    eleza __eq__(self, other):
        '''od.__eq__(y) <==> od==y.  Comparison to another OD is order-sensitive
        while comparison to a regular mapping is order-insensitive.

        '''
        ikiwa isinstance(other, OrderedDict):
            rudisha dict.__eq__(self, other) and all(map(_eq, self, other))
        rudisha dict.__eq__(self, other)


try:
    kutoka _collections agiza OrderedDict
except ImportError:
    # Leave the pure Python version in place.
    pass


################################################################################
### namedtuple
################################################################################

try:
    kutoka _collections agiza _tuplegetter
except ImportError:
    _tuplegetter = lambda index, doc: property(_itemgetter(index), doc=doc)

eleza namedtuple(typename, field_names, *, rename=False, defaults=None, module=None):
    """Returns a new subkundi of tuple with named fields.

    >>> Point = namedtuple('Point', ['x', 'y'])
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate with positional args or keywords
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
    >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields
    Point(x=100, y=22)

    """

    # Validate the field names.  At the user's option, either generate an error
    # message or automatically replace the field name with a valid name.
    ikiwa isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split()
    field_names = list(map(str, field_names))
    typename = _sys.intern(str(typename))

    ikiwa rename:
        seen = set()
        for index, name in enumerate(field_names):
            ikiwa (not name.isidentifier()
                or _iskeyword(name)
                or name.startswith('_')
                or name in seen):
                field_names[index] = f'_{index}'
            seen.add(name)

    for name in [typename] + field_names:
        ikiwa type(name) is not str:
            raise TypeError('Type names and field names must be strings')
        ikiwa not name.isidentifier():
            raise ValueError('Type names and field names must be valid '
                             f'identifiers: {name!r}')
        ikiwa _iskeyword(name):
            raise ValueError('Type names and field names cannot be a '
                             f'keyword: {name!r}')

    seen = set()
    for name in field_names:
        ikiwa name.startswith('_') and not rename:
            raise ValueError('Field names cannot start with an underscore: '
                             f'{name!r}')
        ikiwa name in seen:
            raise ValueError(f'Encountered duplicate field name: {name!r}')
        seen.add(name)

    field_defaults = {}
    ikiwa defaults is not None:
        defaults = tuple(defaults)
        ikiwa len(defaults) > len(field_names):
            raise TypeError('Got more default values than field names')
        field_defaults = dict(reversed(list(zip(reversed(field_names),
                                                reversed(defaults)))))

    # Variables used in the methods and docstrings
    field_names = tuple(map(_sys.intern, field_names))
    num_fields = len(field_names)
    arg_list = repr(field_names).replace("'", "")[1:-1]
    repr_fmt = '(' + ', '.join(f'{name}=%r' for name in field_names) + ')'
    tuple_new = tuple.__new__
    _dict, _tuple, _len, _map, _zip = dict, tuple, len, map, zip

    # Create all the named tuple methods to be added to the kundi namespace

    s = f'eleza __new__(_cls, {arg_list}): rudisha _tuple_new(_cls, ({arg_list}))'
    namespace = {'_tuple_new': tuple_new, '__name__': f'namedtuple_{typename}'}
    # Note: exec() has the side-effect of interning the field names
    exec(s, namespace)
    __new__ = namespace['__new__']
    __new__.__doc__ = f'Create new instance of {typename}({arg_list})'
    ikiwa defaults is not None:
        __new__.__defaults__ = defaults

    @classmethod
    eleza _make(cls, iterable):
        result = tuple_new(cls, iterable)
        ikiwa _len(result) != num_fields:
            raise TypeError(f'Expected {num_fields} arguments, got {len(result)}')
        rudisha result

    _make.__func__.__doc__ = (f'Make a new {typename} object kutoka a sequence '
                              'or iterable')

    eleza _replace(self, /, **kwds):
        result = self._make(_map(kwds.pop, field_names, self))
        ikiwa kwds:
            raise ValueError(f'Got unexpected field names: {list(kwds)!r}')
        rudisha result

    _replace.__doc__ = (f'Return a new {typename} object replacing specified '
                        'fields with new values')

    eleza __repr__(self):
        'Return a nicely formatted representation string'
        rudisha self.__class__.__name__ + repr_fmt % self

    eleza _asdict(self):
        'Return a new dict which maps field names to their values.'
        rudisha _dict(_zip(self._fields, self))

    eleza __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        rudisha _tuple(self)

    # Modify function metadata to help with introspection and debugging
    for method in (__new__, _make.__func__, _replace,
                   __repr__, _asdict, __getnewargs__):
        method.__qualname__ = f'{typename}.{method.__name__}'

    # Build-up the kundi namespace dictionary
    # and use type() to build the result class
    class_namespace = {
        '__doc__': f'{typename}({arg_list})',
        '__slots__': (),
        '_fields': field_names,
        '_field_defaults': field_defaults,
        # alternate spelling for backward compatibility
        '_fields_defaults': field_defaults,
        '__new__': __new__,
        '_make': _make,
        '_replace': _replace,
        '__repr__': __repr__,
        '_asdict': _asdict,
        '__getnewargs__': __getnewargs__,
    }
    for index, name in enumerate(field_names):
        doc = _sys.intern(f'Alias for field number {index}')
        class_namespace[name] = _tuplegetter(index, doc)

    result = type(typename, (tuple,), class_namespace)

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in environments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython), or where the user has
    # specified a particular module.
    ikiwa module is None:
        try:
            module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass
    ikiwa module is not None:
        result.__module__ = module

    rudisha result


########################################################################
###  Counter
########################################################################

eleza _count_elements(mapping, iterable):
    'Tally elements kutoka the iterable.'
    mapping_get = mapping.get
    for elem in iterable:
        mapping[elem] = mapping_get(elem, 0) + 1

try:                                    # Load C helper function ikiwa available
    kutoka _collections agiza _count_elements
except ImportError:
    pass

kundi Counter(dict):
    '''Dict subkundi for counting hashable items.  Sometimes called a bag
    or multiset.  Elements are stored as dictionary keys and their counts
    are stored as dictionary values.

    >>> c = Counter('abcdeabcdabcaba')  # count elements kutoka a string

    >>> c.most_common(3)                # three most common elements
    [('a', 5), ('b', 4), ('c', 3)]
    >>> sorted(c)                       # list all unique elements
    ['a', 'b', 'c', 'd', 'e']
    >>> ''.join(sorted(c.elements()))   # list elements with repetitions
    'aaaaabbbbcccdde'
    >>> sum(c.values())                 # total of all counts
    15

    >>> c['a']                          # count of letter 'a'
    5
    >>> for elem in 'shazam':           # update counts kutoka an iterable
    ...     c[elem] += 1                # by adding 1 to each element's count
    >>> c['a']                          # now there are seven 'a'
    7
    >>> del c['b']                      # remove all 'b'
    >>> c['b']                          # now there are zero 'b'
    0

    >>> d = Counter('simsalabim')       # make another counter
    >>> c.update(d)                     # add in the second counter
    >>> c['a']                          # now there are nine 'a'
    9

    >>> c.clear()                       # empty the counter
    >>> c
    Counter()

    Note:  If a count is set to zero or reduced to zero, it will remain
    in the counter until the entry is deleted or the counter is cleared:

    >>> c = Counter('aaabbc')
    >>> c['b'] -= 2                     # reduce the count of 'b' by two
    >>> c.most_common()                 # 'b' is still in, but its count is zero
    [('a', 3), ('c', 1), ('b', 0)]

    '''
    # References:
    #   http://en.wikipedia.org/wiki/Multiset
    #   http://www.gnu.org/software/smalltalk/manual-base/html_node/Bag.html
    #   http://www.demo2s.com/Tutorial/Cpp/0380__set-multiset/Catalog0380__set-multiset.htm
    #   http://code.activestate.com/recipes/259174/
    #   Knuth, TAOCP Vol. II section 4.6.3

    eleza __init__(self, iterable=None, /, **kwds):
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
        'The count of elements not in the Counter is zero.'
        # Needed so that self[missing_item] does not raise KeyError
        rudisha 0

    eleza most_common(self, n=None):
        '''List the n most common elements and their counts kutoka the most
        common to the least.  If n is None, then list all element counts.

        >>> Counter('abracadabra').most_common(3)
        [('a', 5), ('b', 2), ('r', 2)]

        '''
        # Emulate Bag.sortedByCount kutoka Smalltalk
        ikiwa n is None:
            rudisha sorted(self.items(), key=_itemgetter(1), reverse=True)
        rudisha _heapq.nlargest(n, self.items(), key=_itemgetter(1))

    eleza elements(self):
        '''Iterator over elements repeating each as many times as its count.

        >>> c = Counter('ABCABC')
        >>> sorted(c.elements())
        ['A', 'A', 'B', 'B', 'C', 'C']

        # Knuth's example for prime factors of 1836:  2**2 * 3**3 * 17**1
        >>> prime_factors = Counter({2: 2, 3: 3, 17: 1})
        >>> product = 1
        >>> for factor in prime_factors.elements():     # loop over factors
        ...     product *= factor                       # and multiply them
        >>> product
        1836

        Note, ikiwa an element's count has been set to zero or is a negative
        number, elements() will ignore it.

        '''
        # Emulate Bag.do kutoka Smalltalk and Multiset.begin kutoka C++.
        rudisha _chain.kutoka_iterable(_starmap(_repeat, self.items()))

    # Override dict methods where necessary

    @classmethod
    eleza kutokakeys(cls, iterable, v=None):
        # There is no equivalent method for counters because the semantics
        # would be ambiguous in cases such as Counter.kutokakeys('aaabbc', v=2).
        # Initializing counters to zero values isn't necessary because zero
        # is already the default value for counter lookups.  Initializing
        # to one is easily accomplished with Counter(set(iterable)).  For
        # more exotic cases, create a dictionary first using a dictionary
        # comprehension or dict.kutokakeys().
        raise NotImplementedError(
            'Counter.kutokakeys() is undefined.  Use Counter(iterable) instead.')

    eleza update(self, iterable=None, /, **kwds):
        '''Like dict.update() but add counts instead of replacing them.

        Source can be an iterable, a dictionary, or another Counter instance.

        >>> c = Counter('which')
        >>> c.update('witch')           # add elements kutoka another iterable
        >>> d = Counter('watch')
        >>> c.update(d)                 # add elements kutoka another counter
        >>> c['h']                      # four 'h' in which, witch, and watch
        4

        '''
        # The regular dict.update() operation makes no sense here because the
        # replace behavior results in the some of original untouched counts
        # being mixed-in with all of the other counts for a mismash that
        # doesn't have a straight-forward interpretation in most counting
        # contexts.  Instead, we implement straight-addition.  Both the inputs
        # and outputs are allowed to contain zero and negative counts.

        ikiwa iterable is not None:
            ikiwa isinstance(iterable, _collections_abc.Mapping):
                ikiwa self:
                    self_get = self.get
                    for elem, count in iterable.items():
                        self[elem] = count + self_get(elem, 0)
                else:
                    super(Counter, self).update(iterable) # fast path when counter is empty
            else:
                _count_elements(self, iterable)
        ikiwa kwds:
            self.update(kwds)

    eleza subtract(self, iterable=None, /, **kwds):
        '''Like dict.update() but subtracts counts instead of replacing them.
        Counts can be reduced below zero.  Both the inputs and outputs are
        allowed to contain zero and negative counts.

        Source can be an iterable, a dictionary, or another Counter instance.

        >>> c = Counter('which')
        >>> c.subtract('witch')             # subtract elements kutoka another iterable
        >>> c.subtract(Counter('watch'))    # subtract elements kutoka another counter
        >>> c['h']                          # 2 in which, minus 1 in witch, minus 1 in watch
        0
        >>> c['w']                          # 1 in which, minus 1 in witch, minus 1 in watch
        -1

        '''
        ikiwa iterable is not None:
            self_get = self.get
            ikiwa isinstance(iterable, _collections_abc.Mapping):
                for elem, count in iterable.items():
                    self[elem] = self_get(elem, 0) - count
            else:
                for elem in iterable:
                    self[elem] = self_get(elem, 0) - 1
        ikiwa kwds:
            self.subtract(kwds)

    eleza copy(self):
        'Return a shallow copy.'
        rudisha self.__class__(self)

    eleza __reduce__(self):
        rudisha self.__class__, (dict(self),)

    eleza __delitem__(self, elem):
        'Like dict.__delitem__() but does not raise KeyError for missing values.'
        ikiwa elem in self:
            super().__delitem__(elem)

    eleza __repr__(self):
        ikiwa not self:
            rudisha '%s()' % self.__class__.__name__
        try:
            items = ', '.join(map('%r: %r'.__mod__, self.most_common()))
            rudisha '%s({%s})' % (self.__class__.__name__, items)
        except TypeError:
            # handle case where values are not orderable
            rudisha '{0}({1!r})'.format(self.__class__.__name__, dict(self))

    # Multiset-style mathematical operations discussed in:
    #       Knuth TAOCP Volume II section 4.6.3 exercise 19
    #       and at http://en.wikipedia.org/wiki/Multiset
    #
    # Outputs guaranteed to only include positive counts.
    #
    # To strip negative and zero counts, add-in an empty counter:
    #       c += Counter()

    eleza __add__(self, other):
        '''Add counts kutoka two counters.

        >>> Counter('abbb') + Counter('bcc')
        Counter({'b': 4, 'c': 2, 'a': 1})

        '''
        ikiwa not isinstance(other, Counter):
            rudisha NotImplemented
        result = Counter()
        for elem, count in self.items():
            newcount = count + other[elem]
            ikiwa newcount > 0:
                result[elem] = newcount
        for elem, count in other.items():
            ikiwa elem not in self and count > 0:
                result[elem] = count
        rudisha result

    eleza __sub__(self, other):
        ''' Subtract count, but keep only results with positive counts.

        >>> Counter('abbbc') - Counter('bccd')
        Counter({'b': 2, 'a': 1})

        '''
        ikiwa not isinstance(other, Counter):
            rudisha NotImplemented
        result = Counter()
        for elem, count in self.items():
            newcount = count - other[elem]
            ikiwa newcount > 0:
                result[elem] = newcount
        for elem, count in other.items():
            ikiwa elem not in self and count < 0:
                result[elem] = 0 - count
        rudisha result

    eleza __or__(self, other):
        '''Union is the maximum of value in either of the input counters.

        >>> Counter('abbb') | Counter('bcc')
        Counter({'b': 3, 'c': 2, 'a': 1})

        '''
        ikiwa not isinstance(other, Counter):
            rudisha NotImplemented
        result = Counter()
        for elem, count in self.items():
            other_count = other[elem]
            newcount = other_count ikiwa count < other_count else count
            ikiwa newcount > 0:
                result[elem] = newcount
        for elem, count in other.items():
            ikiwa elem not in self and count > 0:
                result[elem] = count
        rudisha result

    eleza __and__(self, other):
        ''' Intersection is the minimum of corresponding counts.

        >>> Counter('abbb') & Counter('bcc')
        Counter({'b': 1})

        '''
        ikiwa not isinstance(other, Counter):
            rudisha NotImplemented
        result = Counter()
        for elem, count in self.items():
            other_count = other[elem]
            newcount = count ikiwa count < other_count else other_count
            ikiwa newcount > 0:
                result[elem] = newcount
        rudisha result

    eleza __pos__(self):
        'Adds an empty counter, effectively stripping negative and zero counts'
        result = Counter()
        for elem, count in self.items():
            ikiwa count > 0:
                result[elem] = count
        rudisha result

    eleza __neg__(self):
        '''Subtracts kutoka an empty counter.  Strips positive and zero counts,
        and flips the sign on negative counts.

        '''
        result = Counter()
        for elem, count in self.items():
            ikiwa count < 0:
                result[elem] = 0 - count
        rudisha result

    eleza _keep_positive(self):
        '''Internal method to strip elements with a negative or zero count'''
        nonpositive = [elem for elem, count in self.items() ikiwa not count > 0]
        for elem in nonpositive:
            del self[elem]
        rudisha self

    eleza __iadd__(self, other):
        '''Inplace add kutoka another counter, keeping only positive counts.

        >>> c = Counter('abbb')
        >>> c += Counter('bcc')
        >>> c
        Counter({'b': 4, 'c': 2, 'a': 1})

        '''
        for elem, count in other.items():
            self[elem] += count
        rudisha self._keep_positive()

    eleza __isub__(self, other):
        '''Inplace subtract counter, but keep only results with positive counts.

        >>> c = Counter('abbbc')
        >>> c -= Counter('bccd')
        >>> c
        Counter({'b': 2, 'a': 1})

        '''
        for elem, count in other.items():
            self[elem] -= count
        rudisha self._keep_positive()

    eleza __ior__(self, other):
        '''Inplace union is the maximum of value kutoka either counter.

        >>> c = Counter('abbb')
        >>> c |= Counter('bcc')
        >>> c
        Counter({'b': 3, 'c': 2, 'a': 1})

        '''
        for elem, other_count in other.items():
            count = self[elem]
            ikiwa other_count > count:
                self[elem] = other_count
        rudisha self._keep_positive()

    eleza __iand__(self, other):
        '''Inplace intersection is the minimum of corresponding counts.

        >>> c = Counter('abbb')
        >>> c &= Counter('bcc')
        >>> c
        Counter({'b': 1})

        '''
        for elem, count in self.items():
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

    The underlying mappings are stored in a list.  That list is public and can
    be accessed or updated using the *maps* attribute.  There is no other
    state.

    Lookups search the underlying mappings successively until a key is found.
    In contrast, writes, updates, and deletions only operate on the first
    mapping.

    '''

    eleza __init__(self, *maps):
        '''Initialize a ChainMap by setting *maps* to the given mappings.
        If no mappings are provided, a single empty dictionary is used.

        '''
        self.maps = list(maps) or [{}]          # always at least one map

    eleza __missing__(self, key):
        raise KeyError(key)

    eleza __getitem__(self, key):
        for mapping in self.maps:
            try:
                rudisha mapping[key]             # can't use 'key in mapping' with defaultdict
            except KeyError:
                pass
        rudisha self.__missing__(key)            # support subclasses that define __missing__

    eleza get(self, key, default=None):
        rudisha self[key] ikiwa key in self else default

    eleza __len__(self):
        rudisha len(set().union(*self.maps))     # reuses stored hash values ikiwa possible

    eleza __iter__(self):
        d = {}
        for mapping in reversed(self.maps):
            d.update(mapping)                   # reuses stored hash values ikiwa possible
        rudisha iter(d)

    eleza __contains__(self, key):
        rudisha any(key in m for m in self.maps)

    eleza __bool__(self):
        rudisha any(self.maps)

    @_recursive_repr()
    eleza __repr__(self):
        rudisha f'{self.__class__.__name__}({", ".join(map(repr, self.maps))})'

    @classmethod
    eleza kutokakeys(cls, iterable, *args):
        'Create a ChainMap with a single dict created kutoka the iterable.'
        rudisha cls(dict.kutokakeys(iterable, *args))

    eleza copy(self):
        'New ChainMap or subkundi with a new copy of maps[0] and refs to maps[1:]'
        rudisha self.__class__(self.maps[0].copy(), *self.maps[1:])

    __copy__ = copy

    eleza new_child(self, m=None):                # like Django's Context.push()
        '''New ChainMap with a new map followed by all previous maps.
        If no map is provided, an empty dict is used.
        '''
        ikiwa m is None:
            m = {}
        rudisha self.__class__(m, *self.maps)

    @property
    eleza parents(self):                          # like Django's Context.pop()
        'New ChainMap kutoka maps[1:].'
        rudisha self.__class__(*self.maps[1:])

    eleza __setitem__(self, key, value):
        self.maps[0][key] = value

    eleza __delitem__(self, key):
        try:
            del self.maps[0][key]
        except KeyError:
            raise KeyError('Key not found in the first mapping: {!r}'.format(key))

    eleza popitem(self):
        'Remove and rudisha an item pair kutoka maps[0]. Raise KeyError is maps[0] is empty.'
        try:
            rudisha self.maps[0].popitem()
        except KeyError:
            raise KeyError('No keys found in the first mapping.')

    eleza pop(self, key, *args):
        'Remove *key* kutoka maps[0] and rudisha its value. Raise KeyError ikiwa *key* not in maps[0].'
        try:
            rudisha self.maps[0].pop(key, *args)
        except KeyError:
            raise KeyError('Key not found in the first mapping: {!r}'.format(key))

    eleza clear(self):
        'Clear maps[0], leaving maps[1:] intact.'
        self.maps[0].clear()


################################################################################
### UserDict
################################################################################

kundi UserDict(_collections_abc.MutableMapping):

    # Start by filling-out the abstract methods
    eleza __init__(*args, **kwargs):
        ikiwa not args:
            raise TypeError("descriptor '__init__' of 'UserDict' object "
                            "needs an argument")
        self, *args = args
        ikiwa len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        ikiwa args:
            dict = args[0]
        elikiwa 'dict' in kwargs:
            dict = kwargs.pop('dict')
            agiza warnings
            warnings.warn("Passing 'dict' as keyword argument is deprecated",
                          DeprecationWarning, stacklevel=2)
        else:
            dict = None
        self.data = {}
        ikiwa dict is not None:
            self.update(dict)
        ikiwa kwargs:
            self.update(kwargs)
    __init__.__text_signature__ = '($self, dict=None, /, **kwargs)'

    eleza __len__(self): rudisha len(self.data)
    eleza __getitem__(self, key):
        ikiwa key in self.data:
            rudisha self.data[key]
        ikiwa hasattr(self.__class__, "__missing__"):
            rudisha self.__class__.__missing__(self, key)
        raise KeyError(key)
    eleza __setitem__(self, key, item): self.data[key] = item
    eleza __delitem__(self, key): del self.data[key]
    eleza __iter__(self):
        rudisha iter(self.data)

    # Modify __contains__ to work correctly when __missing__ is present
    eleza __contains__(self, key):
        rudisha key in self.data

    # Now, add the methods in dicts but not in MutableMapping
    eleza __repr__(self): rudisha repr(self.data)
    eleza __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["data"] = self.__dict__["data"].copy()
        rudisha inst

    eleza copy(self):
        ikiwa self.__class__ is UserDict:
            rudisha UserDict(self.data.copy())
        agiza copy
        data = self.data
        try:
            self.data = {}
            c = copy.copy(self)
        finally:
            self.data = data
        c.update(self)
        rudisha c

    @classmethod
    eleza kutokakeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        rudisha d



################################################################################
### UserList
################################################################################

kundi UserList(_collections_abc.MutableSequence):
    """A more or less complete user-defined wrapper around list objects."""
    eleza __init__(self, initlist=None):
        self.data = []
        ikiwa initlist is not None:
            # XXX should this accept an arbitrary sequence?
            ikiwa type(initlist) == type(self.data):
                self.data[:] = initlist
            elikiwa isinstance(initlist, UserList):
                self.data[:] = initlist.data[:]
            else:
                self.data = list(initlist)
    eleza __repr__(self): rudisha repr(self.data)
    eleza __lt__(self, other): rudisha self.data <  self.__cast(other)
    eleza __le__(self, other): rudisha self.data <= self.__cast(other)
    eleza __eq__(self, other): rudisha self.data == self.__cast(other)
    eleza __gt__(self, other): rudisha self.data >  self.__cast(other)
    eleza __ge__(self, other): rudisha self.data >= self.__cast(other)
    eleza __cast(self, other):
        rudisha other.data ikiwa isinstance(other, UserList) else other
    eleza __contains__(self, item): rudisha item in self.data
    eleza __len__(self): rudisha len(self.data)
    eleza __getitem__(self, i):
        ikiwa isinstance(i, slice):
            rudisha self.__class__(self.data[i])
        else:
            rudisha self.data[i]
    eleza __setitem__(self, i, item): self.data[i] = item
    eleza __delitem__(self, i): del self.data[i]
    eleza __add__(self, other):
        ikiwa isinstance(other, UserList):
            rudisha self.__class__(self.data + other.data)
        elikiwa isinstance(other, type(self.data)):
            rudisha self.__class__(self.data + other)
        rudisha self.__class__(self.data + list(other))
    eleza __radd__(self, other):
        ikiwa isinstance(other, UserList):
            rudisha self.__class__(other.data + self.data)
        elikiwa isinstance(other, type(self.data)):
            rudisha self.__class__(other + self.data)
        rudisha self.__class__(list(other) + self.data)
    eleza __iadd__(self, other):
        ikiwa isinstance(other, UserList):
            self.data += other.data
        elikiwa isinstance(other, type(self.data)):
            self.data += other
        else:
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
        # Create a copy and avoid triggering descriptors
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
        else:
            self.data.extend(other)



################################################################################
### UserString
################################################################################

kundi UserString(_collections_abc.Sequence):
    eleza __init__(self, seq):
        ikiwa isinstance(seq, str):
            self.data = seq
        elikiwa isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
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
        rudisha char in self.data

    eleza __len__(self): rudisha len(self.data)
    eleza __getitem__(self, index): rudisha self.__class__(self.data[index])
    eleza __add__(self, other):
        ikiwa isinstance(other, UserString):
            rudisha self.__class__(self.data + other.data)
        elikiwa isinstance(other, str):
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
    # the following methods are defined in alphabetical order:
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
        encoding = 'utf-8' ikiwa encoding is None else encoding
        errors = 'strict' ikiwa errors is None else errors
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
    eleza lstrip(self, chars=None): rudisha self.__class__(self.data.lstrip(chars))
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
    eleza rstrip(self, chars=None):
        rudisha self.__class__(self.data.rstrip(chars))
    eleza split(self, sep=None, maxsplit=-1):
        rudisha self.data.split(sep, maxsplit)
    eleza rsplit(self, sep=None, maxsplit=-1):
        rudisha self.data.rsplit(sep, maxsplit)
    eleza splitlines(self, keepends=False): rudisha self.data.splitlines(keepends)
    eleza startswith(self, prefix, start=0, end=_sys.maxsize):
        rudisha self.data.startswith(prefix, start, end)
    eleza strip(self, chars=None): rudisha self.__class__(self.data.strip(chars))
    eleza swapcase(self): rudisha self.__class__(self.data.swapcase())
    eleza title(self): rudisha self.__class__(self.data.title())
    eleza translate(self, *args):
        rudisha self.__class__(self.data.translate(*args))
    eleza upper(self): rudisha self.__class__(self.data.upper())
    eleza zfill(self, width): rudisha self.__class__(self.data.zfill(width))
