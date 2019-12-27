"""functools.py - Tools for working with functions and callable objects
"""
# Python module wrapper for _functools C module
# to allow utilities written in Python to be added
# to the functools module.
# Written by Nick Coghlan <ncoghlan at gmail.com>,
# Raymond Hettinger <python at rcn.com>,
# and Łukasz Langa <lukasz at langa.pl>.
#   Copyright (C) 2006-2013 Python Software Foundation.
# See C source code for _functools credits/copyright

__all__ = ['update_wrapper', 'wraps', 'WRAPPER_ASSIGNMENTS', 'WRAPPER_UPDATES',
           'total_ordering', 'cmp_to_key', 'lru_cache', 'reduce', 'partial',
           'partialmethod', 'singledispatch', 'singledispatchmethod']

kutoka abc agiza get_cache_token
kutoka collections agiza namedtuple
# agiza types, weakref  # Deferred to single_dispatch()
kutoka reprlib agiza recursive_repr
kutoka _thread agiza RLock


################################################################################
### update_wrapper() and wraps() decorator
################################################################################

# update_wrapper() and wraps() are tools to help write
# wrapper functions that can handle naive introspection

WRAPPER_ASSIGNMENTS = ('__module__', '__name__', '__qualname__', '__doc__',
                       '__annotations__')
WRAPPER_UPDATES = ('__dict__',)
eleza update_wrapper(wrapper,
                   wrapped,
                   assigned = WRAPPER_ASSIGNMENTS,
                   updated = WRAPPER_UPDATES):
    """Update a wrapper function to look like the wrapped function

       wrapper is the function to be updated
       wrapped is the original function
       assigned is a tuple naming the attributes assigned directly
       kutoka the wrapped function to the wrapper function (defaults to
       functools.WRAPPER_ASSIGNMENTS)
       updated is a tuple naming the attributes of the wrapper that
       are updated with the corresponding attribute kutoka the wrapped
       function (defaults to functools.WRAPPER_UPDATES)
    """
    for attr in assigned:
        try:
            value = getattr(wrapped, attr)
        except AttributeError:
            pass
        else:
            setattr(wrapper, attr, value)
    for attr in updated:
        getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
    # Issue #17482: set __wrapped__ last so we don't inadvertently copy it
    # kutoka the wrapped function when updating __dict__
    wrapper.__wrapped__ = wrapped
    # Return the wrapper so this can be used as a decorator via partial()
    rudisha wrapper

eleza wraps(wrapped,
          assigned = WRAPPER_ASSIGNMENTS,
          updated = WRAPPER_UPDATES):
    """Decorator factory to apply update_wrapper() to a wrapper function

       Returns a decorator that invokes update_wrapper() with the decorated
       function as the wrapper argument and the arguments to wraps() as the
       remaining arguments. Default arguments are as for update_wrapper().
       This is a convenience function to simplify applying partial() to
       update_wrapper().
    """
    rudisha partial(update_wrapper, wrapped=wrapped,
                   assigned=assigned, updated=updated)


################################################################################
### total_ordering kundi decorator
################################################################################

# The total ordering functions all invoke the root magic method directly
# rather than using the corresponding operator.  This avoids possible
# infinite recursion that could occur when the operator dispatch logic
# detects a NotImplemented result and then calls a reflected method.

eleza _gt_kutoka_lt(self, other, NotImplemented=NotImplemented):
    'Return a > b.  Computed by @total_ordering kutoka (not a < b) and (a != b).'
    op_result = self.__lt__(other)
    ikiwa op_result is NotImplemented:
        rudisha op_result
    rudisha not op_result and self != other

eleza _le_kutoka_lt(self, other, NotImplemented=NotImplemented):
    'Return a <= b.  Computed by @total_ordering kutoka (a < b) or (a == b).'
    op_result = self.__lt__(other)
    rudisha op_result or self == other

eleza _ge_kutoka_lt(self, other, NotImplemented=NotImplemented):
    'Return a >= b.  Computed by @total_ordering kutoka (not a < b).'
    op_result = self.__lt__(other)
    ikiwa op_result is NotImplemented:
        rudisha op_result
    rudisha not op_result

eleza _ge_kutoka_le(self, other, NotImplemented=NotImplemented):
    'Return a >= b.  Computed by @total_ordering kutoka (not a <= b) or (a == b).'
    op_result = self.__le__(other)
    ikiwa op_result is NotImplemented:
        rudisha op_result
    rudisha not op_result or self == other

eleza _lt_kutoka_le(self, other, NotImplemented=NotImplemented):
    'Return a < b.  Computed by @total_ordering kutoka (a <= b) and (a != b).'
    op_result = self.__le__(other)
    ikiwa op_result is NotImplemented:
        rudisha op_result
    rudisha op_result and self != other

eleza _gt_kutoka_le(self, other, NotImplemented=NotImplemented):
    'Return a > b.  Computed by @total_ordering kutoka (not a <= b).'
    op_result = self.__le__(other)
    ikiwa op_result is NotImplemented:
        rudisha op_result
    rudisha not op_result

eleza _lt_kutoka_gt(self, other, NotImplemented=NotImplemented):
    'Return a < b.  Computed by @total_ordering kutoka (not a > b) and (a != b).'
    op_result = self.__gt__(other)
    ikiwa op_result is NotImplemented:
        rudisha op_result
    rudisha not op_result and self != other

eleza _ge_kutoka_gt(self, other, NotImplemented=NotImplemented):
    'Return a >= b.  Computed by @total_ordering kutoka (a > b) or (a == b).'
    op_result = self.__gt__(other)
    rudisha op_result or self == other

eleza _le_kutoka_gt(self, other, NotImplemented=NotImplemented):
    'Return a <= b.  Computed by @total_ordering kutoka (not a > b).'
    op_result = self.__gt__(other)
    ikiwa op_result is NotImplemented:
        rudisha op_result
    rudisha not op_result

eleza _le_kutoka_ge(self, other, NotImplemented=NotImplemented):
    'Return a <= b.  Computed by @total_ordering kutoka (not a >= b) or (a == b).'
    op_result = self.__ge__(other)
    ikiwa op_result is NotImplemented:
        rudisha op_result
    rudisha not op_result or self == other

eleza _gt_kutoka_ge(self, other, NotImplemented=NotImplemented):
    'Return a > b.  Computed by @total_ordering kutoka (a >= b) and (a != b).'
    op_result = self.__ge__(other)
    ikiwa op_result is NotImplemented:
        rudisha op_result
    rudisha op_result and self != other

eleza _lt_kutoka_ge(self, other, NotImplemented=NotImplemented):
    'Return a < b.  Computed by @total_ordering kutoka (not a >= b).'
    op_result = self.__ge__(other)
    ikiwa op_result is NotImplemented:
        rudisha op_result
    rudisha not op_result

_convert = {
    '__lt__': [('__gt__', _gt_kutoka_lt),
               ('__le__', _le_kutoka_lt),
               ('__ge__', _ge_kutoka_lt)],
    '__le__': [('__ge__', _ge_kutoka_le),
               ('__lt__', _lt_kutoka_le),
               ('__gt__', _gt_kutoka_le)],
    '__gt__': [('__lt__', _lt_kutoka_gt),
               ('__ge__', _ge_kutoka_gt),
               ('__le__', _le_kutoka_gt)],
    '__ge__': [('__le__', _le_kutoka_ge),
               ('__gt__', _gt_kutoka_ge),
               ('__lt__', _lt_kutoka_ge)]
}

eleza total_ordering(cls):
    """Class decorator that fills in missing ordering methods"""
    # Find user-defined comparisons (not those inherited kutoka object).
    roots = {op for op in _convert ikiwa getattr(cls, op, None) is not getattr(object, op, None)}
    ikiwa not roots:
        raise ValueError('must define at least one ordering operation: < > <= >=')
    root = max(roots)       # prefer __lt__ to __le__ to __gt__ to __ge__
    for opname, opfunc in _convert[root]:
        ikiwa opname not in roots:
            opfunc.__name__ = opname
            setattr(cls, opname, opfunc)
    rudisha cls


################################################################################
### cmp_to_key() function converter
################################################################################

eleza cmp_to_key(mycmp):
    """Convert a cmp= function into a key= function"""
    kundi K(object):
        __slots__ = ['obj']
        eleza __init__(self, obj):
            self.obj = obj
        eleza __lt__(self, other):
            rudisha mycmp(self.obj, other.obj) < 0
        eleza __gt__(self, other):
            rudisha mycmp(self.obj, other.obj) > 0
        eleza __eq__(self, other):
            rudisha mycmp(self.obj, other.obj) == 0
        eleza __le__(self, other):
            rudisha mycmp(self.obj, other.obj) <= 0
        eleza __ge__(self, other):
            rudisha mycmp(self.obj, other.obj) >= 0
        __hash__ = None
    rudisha K

try:
    kutoka _functools agiza cmp_to_key
except ImportError:
    pass


################################################################################
### reduce() sequence to a single item
################################################################################

_initial_missing = object()

eleza reduce(function, sequence, initial=_initial_missing):
    """
    reduce(function, sequence[, initial]) -> value

    Apply a function of two arguments cumulatively to the items of a sequence,
    kutoka left to right, so as to reduce the sequence to a single value.
    For example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5]) calculates
    ((((1+2)+3)+4)+5).  If initial is present, it is placed before the items
    of the sequence in the calculation, and serves as a default when the
    sequence is empty.
    """

    it = iter(sequence)

    ikiwa initial is _initial_missing:
        try:
            value = next(it)
        except StopIteration:
            raise TypeError("reduce() of empty sequence with no initial value") kutoka None
    else:
        value = initial

    for element in it:
        value = function(value, element)

    rudisha value

try:
    kutoka _functools agiza reduce
except ImportError:
    pass


################################################################################
### partial() argument application
################################################################################

# Purely functional, no descriptor behaviour
kundi partial:
    """New function with partial application of the given arguments
    and keywords.
    """

    __slots__ = "func", "args", "keywords", "__dict__", "__weakref__"

    eleza __new__(cls, func, /, *args, **keywords):
        ikiwa not callable(func):
            raise TypeError("the first argument must be callable")

        ikiwa hasattr(func, "func"):
            args = func.args + args
            keywords = {**func.keywords, **keywords}
            func = func.func

        self = super(partial, cls).__new__(cls)

        self.func = func
        self.args = args
        self.keywords = keywords
        rudisha self

    eleza __call__(self, /, *args, **keywords):
        keywords = {**self.keywords, **keywords}
        rudisha self.func(*self.args, *args, **keywords)

    @recursive_repr()
    eleza __repr__(self):
        qualname = type(self).__qualname__
        args = [repr(self.func)]
        args.extend(repr(x) for x in self.args)
        args.extend(f"{k}={v!r}" for (k, v) in self.keywords.items())
        ikiwa type(self).__module__ == "functools":
            rudisha f"functools.{qualname}({', '.join(args)})"
        rudisha f"{qualname}({', '.join(args)})"

    eleza __reduce__(self):
        rudisha type(self), (self.func,), (self.func, self.args,
               self.keywords or None, self.__dict__ or None)

    eleza __setstate__(self, state):
        ikiwa not isinstance(state, tuple):
            raise TypeError("argument to __setstate__ must be a tuple")
        ikiwa len(state) != 4:
            raise TypeError(f"expected 4 items in state, got {len(state)}")
        func, args, kwds, namespace = state
        ikiwa (not callable(func) or not isinstance(args, tuple) or
           (kwds is not None and not isinstance(kwds, dict)) or
           (namespace is not None and not isinstance(namespace, dict))):
            raise TypeError("invalid partial state")

        args = tuple(args) # just in case it's a subclass
        ikiwa kwds is None:
            kwds = {}
        elikiwa type(kwds) is not dict: # XXX does it need to be *exactly* dict?
            kwds = dict(kwds)
        ikiwa namespace is None:
            namespace = {}

        self.__dict__ = namespace
        self.func = func
        self.args = args
        self.keywords = kwds

try:
    kutoka _functools agiza partial
except ImportError:
    pass

# Descriptor version
kundi partialmethod(object):
    """Method descriptor with partial application of the given arguments
    and keywords.

    Supports wrapping existing descriptors and handles non-descriptor
    callables as instance methods.
    """

    eleza __init__(*args, **keywords):
        ikiwa len(args) >= 2:
            self, func, *args = args
        elikiwa not args:
            raise TypeError("descriptor '__init__' of partialmethod "
                            "needs an argument")
        elikiwa 'func' in keywords:
            func = keywords.pop('func')
            self, *args = args
            agiza warnings
            warnings.warn("Passing 'func' as keyword argument is deprecated",
                          DeprecationWarning, stacklevel=2)
        else:
            raise TypeError("type 'partialmethod' takes at least one argument, "
                            "got %d" % (len(args)-1))
        args = tuple(args)

        ikiwa not callable(func) and not hasattr(func, "__get__"):
            raise TypeError("{!r} is not callable or a descriptor"
                                 .format(func))

        # func could be a descriptor like classmethod which isn't callable,
        # so we can't inherit kutoka partial (it verifies func is callable)
        ikiwa isinstance(func, partialmethod):
            # flattening is mandatory in order to place cls/self before all
            # other arguments
            # it's also more efficient since only one function will be called
            self.func = func.func
            self.args = func.args + args
            self.keywords = {**func.keywords, **keywords}
        else:
            self.func = func
            self.args = args
            self.keywords = keywords
    __init__.__text_signature__ = '($self, func, /, *args, **keywords)'

    eleza __repr__(self):
        args = ", ".join(map(repr, self.args))
        keywords = ", ".join("{}={!r}".format(k, v)
                                 for k, v in self.keywords.items())
        format_string = "{module}.{cls}({func}, {args}, {keywords})"
        rudisha format_string.format(module=self.__class__.__module__,
                                    cls=self.__class__.__qualname__,
                                    func=self.func,
                                    args=args,
                                    keywords=keywords)

    eleza _make_unbound_method(self):
        eleza _method(cls_or_self, /, *args, **keywords):
            keywords = {**self.keywords, **keywords}
            rudisha self.func(cls_or_self, *self.args, *args, **keywords)
        _method.__isabstractmethod__ = self.__isabstractmethod__
        _method._partialmethod = self
        rudisha _method

    eleza __get__(self, obj, cls=None):
        get = getattr(self.func, "__get__", None)
        result = None
        ikiwa get is not None:
            new_func = get(obj, cls)
            ikiwa new_func is not self.func:
                # Assume __get__ returning something new indicates the
                # creation of an appropriate callable
                result = partial(new_func, *self.args, **self.keywords)
                try:
                    result.__self__ = new_func.__self__
                except AttributeError:
                    pass
        ikiwa result is None:
            # If the underlying descriptor didn't do anything, treat this
            # like an instance method
            result = self._make_unbound_method().__get__(obj, cls)
        rudisha result

    @property
    eleza __isabstractmethod__(self):
        rudisha getattr(self.func, "__isabstractmethod__", False)

# Helper functions

eleza _unwrap_partial(func):
    while isinstance(func, partial):
        func = func.func
    rudisha func

################################################################################
### LRU Cache function decorator
################################################################################

_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])

kundi _HashedSeq(list):
    """ This kundi guarantees that hash() will be called no more than once
        per element.  This is agizaant because the lru_cache() will hash
        the key multiple times on a cache miss.

    """

    __slots__ = 'hashvalue'

    eleza __init__(self, tup, hash=hash):
        self[:] = tup
        self.hashvalue = hash(tup)

    eleza __hash__(self):
        rudisha self.hashvalue

eleza _make_key(args, kwds, typed,
             kwd_mark = (object(),),
             fasttypes = {int, str},
             tuple=tuple, type=type, len=len):
    """Make a cache key kutoka optionally typed positional and keyword arguments

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    """
    # All of code below relies on kwds preserving the order input by the user.
    # Formerly, we sorted() the kwds before looping.  The new way is *much*
    # faster; however, it means that f(x=1, y=2) will now be treated as a
    # distinct call kutoka f(y=2, x=1) which will be cached separately.
    key = args
    ikiwa kwds:
        key += kwd_mark
        for item in kwds.items():
            key += item
    ikiwa typed:
        key += tuple(type(v) for v in args)
        ikiwa kwds:
            key += tuple(type(v) for v in kwds.values())
    elikiwa len(key) == 1 and type(key[0]) in fasttypes:
        rudisha key[0]
    rudisha _HashedSeq(key)

eleza lru_cache(maxsize=128, typed=False):
    """Least-recently-used cache decorator.

    If *maxsize* is set to None, the LRU features are disabled and the cache
    can grow without bound.

    If *typed* is True, arguments of different types will be cached separately.
    For example, f(3.0) and f(3) will be treated as distinct calls with
    distinct results.

    Arguments to the cached function must be hashable.

    View the cache statistics named tuple (hits, misses, maxsize, currsize)
    with f.cache_info().  Clear the cache and statistics with f.cache_clear().
    Access the underlying function with f.__wrapped__.

    See:  http://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU)

    """

    # Users should only access the lru_cache through its public API:
    #       cache_info, cache_clear, and f.__wrapped__
    # The internals of the lru_cache are encapsulated for thread safety and
    # to allow the implementation to change (including a possible C version).

    ikiwa isinstance(maxsize, int):
        # Negative maxsize is treated as 0
        ikiwa maxsize < 0:
            maxsize = 0
    elikiwa callable(maxsize) and isinstance(typed, bool):
        # The user_function was passed in directly via the maxsize argument
        user_function, maxsize = maxsize, 128
        wrapper = _lru_cache_wrapper(user_function, maxsize, typed, _CacheInfo)
        rudisha update_wrapper(wrapper, user_function)
    elikiwa maxsize is not None:
        raise TypeError(
            'Expected first argument to be an integer, a callable, or None')

    eleza decorating_function(user_function):
        wrapper = _lru_cache_wrapper(user_function, maxsize, typed, _CacheInfo)
        rudisha update_wrapper(wrapper, user_function)

    rudisha decorating_function

eleza _lru_cache_wrapper(user_function, maxsize, typed, _CacheInfo):
    # Constants shared by all lru cache instances:
    sentinel = object()          # unique object used to signal cache misses
    make_key = _make_key         # build a key kutoka the function arguments
    PREV, NEXT, KEY, RESULT = 0, 1, 2, 3   # names for the link fields

    cache = {}
    hits = misses = 0
    full = False
    cache_get = cache.get    # bound method to lookup a key or rudisha None
    cache_len = cache.__len__  # get cache size without calling len()
    lock = RLock()           # because linkedlist updates aren't threadsafe
    root = []                # root of the circular doubly linked list
    root[:] = [root, root, None, None]     # initialize by pointing to self

    ikiwa maxsize == 0:

        eleza wrapper(*args, **kwds):
            # No caching -- just a statistics update
            nonlocal misses
            misses += 1
            result = user_function(*args, **kwds)
            rudisha result

    elikiwa maxsize is None:

        eleza wrapper(*args, **kwds):
            # Simple caching without ordering or size limit
            nonlocal hits, misses
            key = make_key(args, kwds, typed)
            result = cache_get(key, sentinel)
            ikiwa result is not sentinel:
                hits += 1
                rudisha result
            misses += 1
            result = user_function(*args, **kwds)
            cache[key] = result
            rudisha result

    else:

        eleza wrapper(*args, **kwds):
            # Size limited caching that tracks accesses by recency
            nonlocal root, hits, misses, full
            key = make_key(args, kwds, typed)
            with lock:
                link = cache_get(key)
                ikiwa link is not None:
                    # Move the link to the front of the circular queue
                    link_prev, link_next, _key, result = link
                    link_prev[NEXT] = link_next
                    link_next[PREV] = link_prev
                    last = root[PREV]
                    last[NEXT] = root[PREV] = link
                    link[PREV] = last
                    link[NEXT] = root
                    hits += 1
                    rudisha result
                misses += 1
            result = user_function(*args, **kwds)
            with lock:
                ikiwa key in cache:
                    # Getting here means that this same key was added to the
                    # cache while the lock was released.  Since the link
                    # update is already done, we need only rudisha the
                    # computed result and update the count of misses.
                    pass
                elikiwa full:
                    # Use the old root to store the new key and result.
                    oldroot = root
                    oldroot[KEY] = key
                    oldroot[RESULT] = result
                    # Empty the oldest link and make it the new root.
                    # Keep a reference to the old key and old result to
                    # prevent their ref counts kutoka going to zero during the
                    # update. That will prevent potentially arbitrary object
                    # clean-up code (i.e. __del__) kutoka running while we're
                    # still adjusting the links.
                    root = oldroot[NEXT]
                    oldkey = root[KEY]
                    oldresult = root[RESULT]
                    root[KEY] = root[RESULT] = None
                    # Now update the cache dictionary.
                    del cache[oldkey]
                    # Save the potentially reentrant cache[key] assignment
                    # for last, after the root and links have been put in
                    # a consistent state.
                    cache[key] = oldroot
                else:
                    # Put result in a new link at the front of the queue.
                    last = root[PREV]
                    link = [last, root, key, result]
                    last[NEXT] = root[PREV] = cache[key] = link
                    # Use the cache_len bound method instead of the len() function
                    # which could potentially be wrapped in an lru_cache itself.
                    full = (cache_len() >= maxsize)
            rudisha result

    eleza cache_info():
        """Report cache statistics"""
        with lock:
            rudisha _CacheInfo(hits, misses, maxsize, cache_len())

    eleza cache_clear():
        """Clear the cache and cache statistics"""
        nonlocal hits, misses, full
        with lock:
            cache.clear()
            root[:] = [root, root, None, None]
            hits = misses = 0
            full = False

    wrapper.cache_info = cache_info
    wrapper.cache_clear = cache_clear
    rudisha wrapper

try:
    kutoka _functools agiza _lru_cache_wrapper
except ImportError:
    pass


################################################################################
### singledispatch() - single-dispatch generic function decorator
################################################################################

eleza _c3_merge(sequences):
    """Merges MROs in *sequences* to a single MRO using the C3 algorithm.

    Adapted kutoka http://www.python.org/download/releases/2.3/mro/.

    """
    result = []
    while True:
        sequences = [s for s in sequences ikiwa s]   # purge empty sequences
        ikiwa not sequences:
            rudisha result
        for s1 in sequences:   # find merge candidates among seq heads
            candidate = s1[0]
            for s2 in sequences:
                ikiwa candidate in s2[1:]:
                    candidate = None
                    break      # reject the current head, it appears later
            else:
                break
        ikiwa candidate is None:
            raise RuntimeError("Inconsistent hierarchy")
        result.append(candidate)
        # remove the chosen candidate
        for seq in sequences:
            ikiwa seq[0] == candidate:
                del seq[0]

eleza _c3_mro(cls, abcs=None):
    """Computes the method resolution order using extended C3 linearization.

    If no *abcs* are given, the algorithm works exactly like the built-in C3
    linearization used for method resolution.

    If given, *abcs* is a list of abstract base classes that should be inserted
    into the resulting MRO. Unrelated ABCs are ignored and don't end up in the
    result. The algorithm inserts ABCs where their functionality is introduced,
    i.e. issubclass(cls, abc) returns True for the kundi itself but returns
    False for all its direct base classes. Implicit ABCs for a given class
    (either registered or inferred kutoka the presence of a special method like
    __len__) are inserted directly after the last ABC explicitly listed in the
    MRO of said class. If two implicit ABCs end up next to each other in the
    resulting MRO, their ordering depends on the order of types in *abcs*.

    """
    for i, base in enumerate(reversed(cls.__bases__)):
        ikiwa hasattr(base, '__abstractmethods__'):
            boundary = len(cls.__bases__) - i
            break   # Bases up to the last explicit ABC are considered first.
    else:
        boundary = 0
    abcs = list(abcs) ikiwa abcs else []
    explicit_bases = list(cls.__bases__[:boundary])
    abstract_bases = []
    other_bases = list(cls.__bases__[boundary:])
    for base in abcs:
        ikiwa issubclass(cls, base) and not any(
                issubclass(b, base) for b in cls.__bases__
            ):
            # If *cls* is the kundi that introduces behaviour described by
            # an ABC *base*, insert said ABC to its MRO.
            abstract_bases.append(base)
    for base in abstract_bases:
        abcs.remove(base)
    explicit_c3_mros = [_c3_mro(base, abcs=abcs) for base in explicit_bases]
    abstract_c3_mros = [_c3_mro(base, abcs=abcs) for base in abstract_bases]
    other_c3_mros = [_c3_mro(base, abcs=abcs) for base in other_bases]
    rudisha _c3_merge(
        [[cls]] +
        explicit_c3_mros + abstract_c3_mros + other_c3_mros +
        [explicit_bases] + [abstract_bases] + [other_bases]
    )

eleza _compose_mro(cls, types):
    """Calculates the method resolution order for a given kundi *cls*.

    Includes relevant abstract base classes (with their respective bases) kutoka
    the *types* iterable. Uses a modified C3 linearization algorithm.

    """
    bases = set(cls.__mro__)
    # Remove entries which are already present in the __mro__ or unrelated.
    eleza is_related(typ):
        rudisha (typ not in bases and hasattr(typ, '__mro__')
                                 and issubclass(cls, typ))
    types = [n for n in types ikiwa is_related(n)]
    # Remove entries which are strict bases of other entries (they will end up
    # in the MRO anyway.
    eleza is_strict_base(typ):
        for other in types:
            ikiwa typ != other and typ in other.__mro__:
                rudisha True
        rudisha False
    types = [n for n in types ikiwa not is_strict_base(n)]
    # Subclasses of the ABCs in *types* which are also implemented by
    # *cls* can be used to stabilize ABC ordering.
    type_set = set(types)
    mro = []
    for typ in types:
        found = []
        for sub in typ.__subclasses__():
            ikiwa sub not in bases and issubclass(cls, sub):
                found.append([s for s in sub.__mro__ ikiwa s in type_set])
        ikiwa not found:
            mro.append(typ)
            continue
        # Favor subclasses with the biggest number of useful bases
        found.sort(key=len, reverse=True)
        for sub in found:
            for subcls in sub:
                ikiwa subcls not in mro:
                    mro.append(subcls)
    rudisha _c3_mro(cls, abcs=mro)

eleza _find_impl(cls, registry):
    """Returns the best matching implementation kutoka *registry* for type *cls*.

    Where there is no registered implementation for a specific type, its method
    resolution order is used to find a more generic implementation.

    Note: ikiwa *registry* does not contain an implementation for the base
    *object* type, this function may rudisha None.

    """
    mro = _compose_mro(cls, registry.keys())
    match = None
    for t in mro:
        ikiwa match is not None:
            # If *match* is an implicit ABC but there is another unrelated,
            # equally matching implicit ABC, refuse the temptation to guess.
            ikiwa (t in registry and t not in cls.__mro__
                              and match not in cls.__mro__
                              and not issubclass(match, t)):
                raise RuntimeError("Ambiguous dispatch: {} or {}".format(
                    match, t))
            break
        ikiwa t in registry:
            match = t
    rudisha registry.get(match)

eleza singledispatch(func):
    """Single-dispatch generic function decorator.

    Transforms a function into a generic function, which can have different
    behaviours depending upon the type of its first argument. The decorated
    function acts as the default implementation, and additional
    implementations can be registered using the register() attribute of the
    generic function.
    """
    # There are many programs that use functools without singledispatch, so we
    # trade-off making singledispatch marginally slower for the benefit of
    # making start-up of such applications slightly faster.
    agiza types, weakref

    registry = {}
    dispatch_cache = weakref.WeakKeyDictionary()
    cache_token = None

    eleza dispatch(cls):
        """generic_func.dispatch(cls) -> <function implementation>

        Runs the dispatch algorithm to rudisha the best available implementation
        for the given *cls* registered on *generic_func*.

        """
        nonlocal cache_token
        ikiwa cache_token is not None:
            current_token = get_cache_token()
            ikiwa cache_token != current_token:
                dispatch_cache.clear()
                cache_token = current_token
        try:
            impl = dispatch_cache[cls]
        except KeyError:
            try:
                impl = registry[cls]
            except KeyError:
                impl = _find_impl(cls, registry)
            dispatch_cache[cls] = impl
        rudisha impl

    eleza register(cls, func=None):
        """generic_func.register(cls, func) -> func

        Registers a new implementation for the given *cls* on a *generic_func*.

        """
        nonlocal cache_token
        ikiwa func is None:
            ikiwa isinstance(cls, type):
                rudisha lambda f: register(cls, f)
            ann = getattr(cls, '__annotations__', {})
            ikiwa not ann:
                raise TypeError(
                    f"Invalid first argument to `register()`: {cls!r}. "
                    f"Use either `@register(some_class)` or plain `@register` "
                    f"on an annotated function."
                )
            func = cls

            # only agiza typing ikiwa annotation parsing is necessary
            kutoka typing agiza get_type_hints
            argname, cls = next(iter(get_type_hints(func).items()))
            ikiwa not isinstance(cls, type):
                raise TypeError(
                    f"Invalid annotation for {argname!r}. "
                    f"{cls!r} is not a class."
                )
        registry[cls] = func
        ikiwa cache_token is None and hasattr(cls, '__abstractmethods__'):
            cache_token = get_cache_token()
        dispatch_cache.clear()
        rudisha func

    eleza wrapper(*args, **kw):
        ikiwa not args:
            raise TypeError(f'{funcname} requires at least '
                            '1 positional argument')

        rudisha dispatch(args[0].__class__)(*args, **kw)

    funcname = getattr(func, '__name__', 'singledispatch function')
    registry[object] = func
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = types.MappingProxyType(registry)
    wrapper._clear_cache = dispatch_cache.clear
    update_wrapper(wrapper, func)
    rudisha wrapper


# Descriptor version
kundi singledispatchmethod:
    """Single-dispatch generic method descriptor.

    Supports wrapping existing descriptors and handles non-descriptor
    callables as instance methods.
    """

    eleza __init__(self, func):
        ikiwa not callable(func) and not hasattr(func, "__get__"):
            raise TypeError(f"{func!r} is not callable or a descriptor")

        self.dispatcher = singledispatch(func)
        self.func = func

    eleza register(self, cls, method=None):
        """generic_method.register(cls, func) -> func

        Registers a new implementation for the given *cls* on a *generic_method*.
        """
        rudisha self.dispatcher.register(cls, func=method)

    eleza __get__(self, obj, cls=None):
        eleza _method(*args, **kwargs):
            method = self.dispatcher.dispatch(args[0].__class__)
            rudisha method.__get__(obj, cls)(*args, **kwargs)

        _method.__isabstractmethod__ = self.__isabstractmethod__
        _method.register = self.register
        update_wrapper(_method, self.func)
        rudisha _method

    @property
    eleza __isabstractmethod__(self):
        rudisha getattr(self.func, '__isabstractmethod__', False)


################################################################################
### cached_property() - computed once per instance, cached as attribute
################################################################################

_NOT_FOUND = object()


kundi cached_property:
    eleza __init__(self, func):
        self.func = func
        self.attrname = None
        self.__doc__ = func.__doc__
        self.lock = RLock()

    eleza __set_name__(self, owner, name):
        ikiwa self.attrname is None:
            self.attrname = name
        elikiwa name != self.attrname:
            raise TypeError(
                "Cannot assign the same cached_property to two different names "
                f"({self.attrname!r} and {name!r})."
            )

    eleza __get__(self, instance, owner=None):
        ikiwa instance is None:
            rudisha self
        ikiwa self.attrname is None:
            raise TypeError(
                "Cannot use cached_property instance without calling __set_name__ on it.")
        try:
            cache = instance.__dict__
        except AttributeError:  # not all objects have __dict__ (e.g. kundi defines slots)
            msg = (
                f"No '__dict__' attribute on {type(instance).__name__!r} "
                f"instance to cache {self.attrname!r} property."
            )
            raise TypeError(msg) kutoka None
        val = cache.get(self.attrname, _NOT_FOUND)
        ikiwa val is _NOT_FOUND:
            with self.lock:
                # check ikiwa another thread filled cache while we awaited lock
                val = cache.get(self.attrname, _NOT_FOUND)
                ikiwa val is _NOT_FOUND:
                    val = self.func(instance)
                    try:
                        cache[self.attrname] = val
                    except TypeError:
                        msg = (
                            f"The '__dict__' attribute on {type(instance).__name__!r} instance "
                            f"does not support item assignment for caching {self.attrname!r} property."
                        )
                        raise TypeError(msg) kutoka None
        rudisha val
