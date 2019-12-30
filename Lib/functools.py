"""functools.py - Tools kila working ukijumuisha functions na callable objects
"""
# Python module wrapper kila _functools C module
# to allow utilities written kwenye Python to be added
# to the functools module.
# Written by Nick Coghlan <ncoghlan at gmail.com>,
# Raymond Hettinger <python at rcn.com>,
# na Łukasz Langa <lukasz at langa.pl>.
#   Copyright (C) 2006-2013 Python Software Foundation.
# See C source code kila _functools credits/copyright

__all__ = ['update_wrapper', 'wraps', 'WRAPPER_ASSIGNMENTS', 'WRAPPER_UPDATES',
           'total_ordering', 'cmp_to_key', 'lru_cache', 'reduce', 'partial',
           'partialmethod', 'singledispatch', 'singledispatchmethod']

kutoka abc agiza get_cache_token
kutoka collections agiza namedtuple
# agiza types, weakref  # Deferred to single_dispatch()
kutoka reprlib agiza recursive_repr
kutoka _thread agiza RLock


################################################################################
### update_wrapper() na wraps() decorator
################################################################################

# update_wrapper() na wraps() are tools to help write
# wrapper functions that can handle naive introspection

WRAPPER_ASSIGNMENTS = ('__module__', '__name__', '__qualname__', '__doc__',
                       '__annotations__')
WRAPPER_UPDATES = ('__dict__',)
eleza update_wrapper(wrapper,
                   wrapped,
                   assigned = WRAPPER_ASSIGNMENTS,
                   updated = WRAPPER_UPDATES):
    """Update a wrapper function to look like the wrapped function

       wrapper ni the function to be updated
       wrapped ni the original function
       assigned ni a tuple naming the attributes assigned directly
       kutoka the wrapped function to the wrapper function (defaults to
       functools.WRAPPER_ASSIGNMENTS)
       updated ni a tuple naming the attributes of the wrapper that
       are updated ukijumuisha the corresponding attribute kutoka the wrapped
       function (defaults to functools.WRAPPER_UPDATES)
    """
    kila attr kwenye assigned:
        jaribu:
            value = getattr(wrapped, attr)
        tatizo AttributeError:
            pita
        isipokua:
            setattr(wrapper, attr, value)
    kila attr kwenye updated:
        getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
    # Issue #17482: set __wrapped__ last so we don't inadvertently copy it
    # kutoka the wrapped function when updating __dict__
    wrapper.__wrapped__ = wrapped
    # Return the wrapper so this can be used kama a decorator via partial()
    rudisha wrapper

eleza wraps(wrapped,
          assigned = WRAPPER_ASSIGNMENTS,
          updated = WRAPPER_UPDATES):
    """Decorator factory to apply update_wrapper() to a wrapper function

       Returns a decorator that invokes update_wrapper() ukijumuisha the decorated
       function kama the wrapper argument na the arguments to wraps() kama the
       remaining arguments. Default arguments are kama kila update_wrapper().
       This ni a convenience function to simplify applying partial() to
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
# detects a NotImplemented result na then calls a reflected method.

eleza _gt_from_lt(self, other, NotImplemented=NotImplemented):
    'Return a > b.  Computed by @total_ordering kutoka (sio a < b) na (a != b).'
    op_result = self.__lt__(other)
    ikiwa op_result ni NotImplemented:
        rudisha op_result
    rudisha sio op_result na self != other

eleza _le_from_lt(self, other, NotImplemented=NotImplemented):
    'Return a <= b.  Computed by @total_ordering kutoka (a < b) ama (a == b).'
    op_result = self.__lt__(other)
    rudisha op_result ama self == other

eleza _ge_from_lt(self, other, NotImplemented=NotImplemented):
    'Return a >= b.  Computed by @total_ordering kutoka (sio a < b).'
    op_result = self.__lt__(other)
    ikiwa op_result ni NotImplemented:
        rudisha op_result
    rudisha sio op_result

eleza _ge_from_le(self, other, NotImplemented=NotImplemented):
    'Return a >= b.  Computed by @total_ordering kutoka (sio a <= b) ama (a == b).'
    op_result = self.__le__(other)
    ikiwa op_result ni NotImplemented:
        rudisha op_result
    rudisha sio op_result ama self == other

eleza _lt_from_le(self, other, NotImplemented=NotImplemented):
    'Return a < b.  Computed by @total_ordering kutoka (a <= b) na (a != b).'
    op_result = self.__le__(other)
    ikiwa op_result ni NotImplemented:
        rudisha op_result
    rudisha op_result na self != other

eleza _gt_from_le(self, other, NotImplemented=NotImplemented):
    'Return a > b.  Computed by @total_ordering kutoka (sio a <= b).'
    op_result = self.__le__(other)
    ikiwa op_result ni NotImplemented:
        rudisha op_result
    rudisha sio op_result

eleza _lt_from_gt(self, other, NotImplemented=NotImplemented):
    'Return a < b.  Computed by @total_ordering kutoka (sio a > b) na (a != b).'
    op_result = self.__gt__(other)
    ikiwa op_result ni NotImplemented:
        rudisha op_result
    rudisha sio op_result na self != other

eleza _ge_from_gt(self, other, NotImplemented=NotImplemented):
    'Return a >= b.  Computed by @total_ordering kutoka (a > b) ama (a == b).'
    op_result = self.__gt__(other)
    rudisha op_result ama self == other

eleza _le_from_gt(self, other, NotImplemented=NotImplemented):
    'Return a <= b.  Computed by @total_ordering kutoka (sio a > b).'
    op_result = self.__gt__(other)
    ikiwa op_result ni NotImplemented:
        rudisha op_result
    rudisha sio op_result

eleza _le_from_ge(self, other, NotImplemented=NotImplemented):
    'Return a <= b.  Computed by @total_ordering kutoka (sio a >= b) ama (a == b).'
    op_result = self.__ge__(other)
    ikiwa op_result ni NotImplemented:
        rudisha op_result
    rudisha sio op_result ama self == other

eleza _gt_from_ge(self, other, NotImplemented=NotImplemented):
    'Return a > b.  Computed by @total_ordering kutoka (a >= b) na (a != b).'
    op_result = self.__ge__(other)
    ikiwa op_result ni NotImplemented:
        rudisha op_result
    rudisha op_result na self != other

eleza _lt_from_ge(self, other, NotImplemented=NotImplemented):
    'Return a < b.  Computed by @total_ordering kutoka (sio a >= b).'
    op_result = self.__ge__(other)
    ikiwa op_result ni NotImplemented:
        rudisha op_result
    rudisha sio op_result

_convert = {
    '__lt__': [('__gt__', _gt_from_lt),
               ('__le__', _le_from_lt),
               ('__ge__', _ge_from_lt)],
    '__le__': [('__ge__', _ge_from_le),
               ('__lt__', _lt_from_le),
               ('__gt__', _gt_from_le)],
    '__gt__': [('__lt__', _lt_from_gt),
               ('__ge__', _ge_from_gt),
               ('__le__', _le_from_gt)],
    '__ge__': [('__le__', _le_from_ge),
               ('__gt__', _gt_from_ge),
               ('__lt__', _lt_from_ge)]
}

eleza total_ordering(cls):
    """Class decorator that fills kwenye missing ordering methods"""
    # Find user-defined comparisons (sio those inherited kutoka object).
    roots = {op kila op kwenye _convert ikiwa getattr(cls, op, Tupu) ni sio getattr(object, op, Tupu)}
    ikiwa sio roots:
        ashiria ValueError('must define at least one ordering operation: < > <= >=')
    root = max(roots)       # prefer __lt__ to __le__ to __gt__ to __ge__
    kila opname, opfunc kwenye _convert[root]:
        ikiwa opname haiko kwenye roots:
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
        __hash__ = Tupu
    rudisha K

jaribu:
    kutoka _functools agiza cmp_to_key
tatizo ImportError:
    pita


################################################################################
### reduce() sequence to a single item
################################################################################

_initial_missing = object()

eleza reduce(function, sequence, initial=_initial_missing):
    """
    reduce(function, sequence[, initial]) -> value

    Apply a function of two arguments cumulatively to the items of a sequence,
    kutoka left to right, so kama to reduce the sequence to a single value.
    For example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5]) calculates
    ((((1+2)+3)+4)+5).  If initial ni present, it ni placed before the items
    of the sequence kwenye the calculation, na serves kama a default when the
    sequence ni empty.
    """

    it = iter(sequence)

    ikiwa initial ni _initial_missing:
        jaribu:
            value = next(it)
        tatizo StopIteration:
            ashiria TypeError("reduce() of empty sequence ukijumuisha no initial value") kutoka Tupu
    isipokua:
        value = initial

    kila element kwenye it:
        value = function(value, element)

    rudisha value

jaribu:
    kutoka _functools agiza reduce
tatizo ImportError:
    pita


################################################################################
### partial() argument application
################################################################################

# Purely functional, no descriptor behaviour
kundi partial:
    """New function ukijumuisha partial application of the given arguments
    na keywords.
    """

    __slots__ = "func", "args", "keywords", "__dict__", "__weakref__"

    eleza __new__(cls, func, /, *args, **keywords):
        ikiwa sio callable(func):
            ashiria TypeError("the first argument must be callable")

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
        args.extend(repr(x) kila x kwenye self.args)
        args.extend(f"{k}={v!r}" kila (k, v) kwenye self.keywords.items())
        ikiwa type(self).__module__ == "functools":
            rudisha f"functools.{qualname}({', '.join(args)})"
        rudisha f"{qualname}({', '.join(args)})"

    eleza __reduce__(self):
        rudisha type(self), (self.func,), (self.func, self.args,
               self.keywords ama Tupu, self.__dict__ ama Tupu)

    eleza __setstate__(self, state):
        ikiwa sio isinstance(state, tuple):
            ashiria TypeError("argument to __setstate__ must be a tuple")
        ikiwa len(state) != 4:
            ashiria TypeError(f"expected 4 items kwenye state, got {len(state)}")
        func, args, kwds, namespace = state
        ikiwa (sio callable(func) ama sio isinstance(args, tuple) ama
           (kwds ni sio Tupu na sio isinstance(kwds, dict)) ama
           (namespace ni sio Tupu na sio isinstance(namespace, dict))):
            ashiria TypeError("invalid partial state")

        args = tuple(args) # just kwenye case it's a subclass
        ikiwa kwds ni Tupu:
            kwds = {}
        lasivyo type(kwds) ni sio dict: # XXX does it need to be *exactly* dict?
            kwds = dict(kwds)
        ikiwa namespace ni Tupu:
            namespace = {}

        self.__dict__ = namespace
        self.func = func
        self.args = args
        self.keywords = kwds

jaribu:
    kutoka _functools agiza partial
tatizo ImportError:
    pita

# Descriptor version
kundi partialmethod(object):
    """Method descriptor ukijumuisha partial application of the given arguments
    na keywords.

    Supports wrapping existing descriptors na handles non-descriptor
    callables kama instance methods.
    """

    eleza __init__(*args, **keywords):
        ikiwa len(args) >= 2:
            self, func, *args = args
        lasivyo sio args:
            ashiria TypeError("descriptor '__init__' of partialmethod "
                            "needs an argument")
        lasivyo 'func' kwenye keywords:
            func = keywords.pop('func')
            self, *args = args
            agiza warnings
            warnings.warn("Passing 'func' kama keyword argument ni deprecated",
                          DeprecationWarning, stacklevel=2)
        isipokua:
            ashiria TypeError("type 'partialmethod' takes at least one argument, "
                            "got %d" % (len(args)-1))
        args = tuple(args)

        ikiwa sio callable(func) na sio hasattr(func, "__get__"):
            ashiria TypeError("{!r} ni sio callable ama a descriptor"
                                 .format(func))

        # func could be a descriptor like classmethod which isn't callable,
        # so we can't inherit kutoka partial (it verifies func ni callable)
        ikiwa isinstance(func, partialmethod):
            # flattening ni mandatory kwenye order to place cls/self before all
            # other arguments
            # it's also more efficient since only one function will be called
            self.func = func.func
            self.args = func.args + args
            self.keywords = {**func.keywords, **keywords}
        isipokua:
            self.func = func
            self.args = args
            self.keywords = keywords
    __init__.__text_signature__ = '($self, func, /, *args, **keywords)'

    eleza __repr__(self):
        args = ", ".join(map(repr, self.args))
        keywords = ", ".join("{}={!r}".format(k, v)
                                 kila k, v kwenye self.keywords.items())
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

    eleza __get__(self, obj, cls=Tupu):
        get = getattr(self.func, "__get__", Tupu)
        result = Tupu
        ikiwa get ni sio Tupu:
            new_func = get(obj, cls)
            ikiwa new_func ni sio self.func:
                # Assume __get__ rudishaing something new indicates the
                # creation of an appropriate callable
                result = partial(new_func, *self.args, **self.keywords)
                jaribu:
                    result.__self__ = new_func.__self__
                tatizo AttributeError:
                    pita
        ikiwa result ni Tupu:
            # If the underlying descriptor didn't do anything, treat this
            # like an instance method
            result = self._make_unbound_method().__get__(obj, cls)
        rudisha result

    @property
    eleza __isabstractmethod__(self):
        rudisha getattr(self.func, "__isabstractmethod__", Uongo)

# Helper functions

eleza _unwrap_partial(func):
    wakati isinstance(func, partial):
        func = func.func
    rudisha func

################################################################################
### LRU Cache function decorator
################################################################################

_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])

kundi _HashedSeq(list):
    """ This kundi guarantees that hash() will be called no more than once
        per element.  This ni agizaant because the lru_cache() will hash
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
    """Make a cache key kutoka optionally typed positional na keyword arguments

    The key ni constructed kwenye a way that ni flat kama possible rather than
    kama a nested structure that would take more memory.

    If there ni only a single argument na its data type ni known to cache
    its hash value, then that argument ni rudishaed without a wrapper.  This
    saves space na improves lookup speed.

    """
    # All of code below relies on kwds preserving the order input by the user.
    # Formerly, we sorted() the kwds before looping.  The new way ni *much*
    # faster; however, it means that f(x=1, y=2) will now be treated kama a
    # distinct call kutoka f(y=2, x=1) which will be cached separately.
    key = args
    ikiwa kwds:
        key += kwd_mark
        kila item kwenye kwds.items():
            key += item
    ikiwa typed:
        key += tuple(type(v) kila v kwenye args)
        ikiwa kwds:
            key += tuple(type(v) kila v kwenye kwds.values())
    lasivyo len(key) == 1 na type(key[0]) kwenye fasttypes:
        rudisha key[0]
    rudisha _HashedSeq(key)

eleza lru_cache(maxsize=128, typed=Uongo):
    """Least-recently-used cache decorator.

    If *maxsize* ni set to Tupu, the LRU features are disabled na the cache
    can grow without bound.

    If *typed* ni Kweli, arguments of different types will be cached separately.
    For example, f(3.0) na f(3) will be treated kama distinct calls with
    distinct results.

    Arguments to the cached function must be hashable.

    View the cache statistics named tuple (hits, misses, maxsize, currsize)
    ukijumuisha f.cache_info().  Clear the cache na statistics ukijumuisha f.cache_clear().
    Access the underlying function ukijumuisha f.__wrapped__.

    See:  http://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU)

    """

    # Users should only access the lru_cache through its public API:
    #       cache_info, cache_clear, na f.__wrapped__
    # The internals of the lru_cache are encapsulated kila thread safety na
    # to allow the implementation to change (including a possible C version).

    ikiwa isinstance(maxsize, int):
        # Negative maxsize ni treated kama 0
        ikiwa maxsize < 0:
            maxsize = 0
    lasivyo callable(maxsize) na isinstance(typed, bool):
        # The user_function was pitaed kwenye directly via the maxsize argument
        user_function, maxsize = maxsize, 128
        wrapper = _lru_cache_wrapper(user_function, maxsize, typed, _CacheInfo)
        rudisha update_wrapper(wrapper, user_function)
    lasivyo maxsize ni sio Tupu:
        ashiria TypeError(
            'Expected first argument to be an integer, a callable, ama Tupu')

    eleza decorating_function(user_function):
        wrapper = _lru_cache_wrapper(user_function, maxsize, typed, _CacheInfo)
        rudisha update_wrapper(wrapper, user_function)

    rudisha decorating_function

eleza _lru_cache_wrapper(user_function, maxsize, typed, _CacheInfo):
    # Constants shared by all lru cache instances:
    sentinel = object()          # unique object used to signal cache misses
    make_key = _make_key         # build a key kutoka the function arguments
    PREV, NEXT, KEY, RESULT = 0, 1, 2, 3   # names kila the link fields

    cache = {}
    hits = misses = 0
    full = Uongo
    cache_get = cache.get    # bound method to lookup a key ama rudisha Tupu
    cache_len = cache.__len__  # get cache size without calling len()
    lock = RLock()           # because linkedlist updates aren't threadsafe
    root = []                # root of the circular doubly linked list
    root[:] = [root, root, Tupu, Tupu]     # initialize by pointing to self

    ikiwa maxsize == 0:

        eleza wrapper(*args, **kwds):
            # No caching -- just a statistics update
            nonlocal misses
            misses += 1
            result = user_function(*args, **kwds)
            rudisha result

    lasivyo maxsize ni Tupu:

        eleza wrapper(*args, **kwds):
            # Simple caching without ordering ama size limit
            nonlocal hits, misses
            key = make_key(args, kwds, typed)
            result = cache_get(key, sentinel)
            ikiwa result ni sio sentinel:
                hits += 1
                rudisha result
            misses += 1
            result = user_function(*args, **kwds)
            cache[key] = result
            rudisha result

    isipokua:

        eleza wrapper(*args, **kwds):
            # Size limited caching that tracks accesses by recency
            nonlocal root, hits, misses, full
            key = make_key(args, kwds, typed)
            ukijumuisha lock:
                link = cache_get(key)
                ikiwa link ni sio Tupu:
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
            ukijumuisha lock:
                ikiwa key kwenye cache:
                    # Getting here means that this same key was added to the
                    # cache wakati the lock was released.  Since the link
                    # update ni already done, we need only rudisha the
                    # computed result na update the count of misses.
                    pita
                lasivyo full:
                    # Use the old root to store the new key na result.
                    oldroot = root
                    oldroot[KEY] = key
                    oldroot[RESULT] = result
                    # Empty the oldest link na make it the new root.
                    # Keep a reference to the old key na old result to
                    # prevent their ref counts kutoka going to zero during the
                    # update. That will prevent potentially arbitrary object
                    # clean-up code (i.e. __del__) kutoka running wakati we're
                    # still adjusting the links.
                    root = oldroot[NEXT]
                    oldkey = root[KEY]
                    oldresult = root[RESULT]
                    root[KEY] = root[RESULT] = Tupu
                    # Now update the cache dictionary.
                    toa cache[oldkey]
                    # Save the potentially reentrant cache[key] assignment
                    # kila last, after the root na links have been put in
                    # a consistent state.
                    cache[key] = oldroot
                isipokua:
                    # Put result kwenye a new link at the front of the queue.
                    last = root[PREV]
                    link = [last, root, key, result]
                    last[NEXT] = root[PREV] = cache[key] = link
                    # Use the cache_len bound method instead of the len() function
                    # which could potentially be wrapped kwenye an lru_cache itself.
                    full = (cache_len() >= maxsize)
            rudisha result

    eleza cache_info():
        """Report cache statistics"""
        ukijumuisha lock:
            rudisha _CacheInfo(hits, misses, maxsize, cache_len())

    eleza cache_clear():
        """Clear the cache na cache statistics"""
        nonlocal hits, misses, full
        ukijumuisha lock:
            cache.clear()
            root[:] = [root, root, Tupu, Tupu]
            hits = misses = 0
            full = Uongo

    wrapper.cache_info = cache_info
    wrapper.cache_clear = cache_clear
    rudisha wrapper

jaribu:
    kutoka _functools agiza _lru_cache_wrapper
tatizo ImportError:
    pita


################################################################################
### singledispatch() - single-dispatch generic function decorator
################################################################################

eleza _c3_merge(sequences):
    """Merges MROs kwenye *sequences* to a single MRO using the C3 algorithm.

    Adapted kutoka http://www.python.org/download/releases/2.3/mro/.

    """
    result = []
    wakati Kweli:
        sequences = [s kila s kwenye sequences ikiwa s]   # purge empty sequences
        ikiwa sio sequences:
            rudisha result
        kila s1 kwenye sequences:   # find merge candidates among seq heads
            candidate = s1[0]
            kila s2 kwenye sequences:
                ikiwa candidate kwenye s2[1:]:
                    candidate = Tupu
                    koma      # reject the current head, it appears later
            isipokua:
                koma
        ikiwa candidate ni Tupu:
            ashiria RuntimeError("Inconsistent hierarchy")
        result.append(candidate)
        # remove the chosen candidate
        kila seq kwenye sequences:
            ikiwa seq[0] == candidate:
                toa seq[0]

eleza _c3_mro(cls, abcs=Tupu):
    """Computes the method resolution order using extended C3 linearization.

    If no *abcs* are given, the algorithm works exactly like the built-in C3
    linearization used kila method resolution.

    If given, *abcs* ni a list of abstract base classes that should be inserted
    into the resulting MRO. Unrelated ABCs are ignored na don't end up kwenye the
    result. The algorithm inserts ABCs where their functionality ni introduced,
    i.e. issubclass(cls, abc) rudishas Kweli kila the kundi itself but rudishas
    Uongo kila all its direct base classes. Implicit ABCs kila a given class
    (either registered ama inferred kutoka the presence of a special method like
    __len__) are inserted directly after the last ABC explicitly listed kwenye the
    MRO of said class. If two implicit ABCs end up next to each other kwenye the
    resulting MRO, their ordering depends on the order of types kwenye *abcs*.

    """
    kila i, base kwenye enumerate(reversed(cls.__bases__)):
        ikiwa hasattr(base, '__abstractmethods__'):
            boundary = len(cls.__bases__) - i
            koma   # Bases up to the last explicit ABC are considered first.
    isipokua:
        boundary = 0
    abcs = list(abcs) ikiwa abcs isipokua []
    explicit_bases = list(cls.__bases__[:boundary])
    abstract_bases = []
    other_bases = list(cls.__bases__[boundary:])
    kila base kwenye abcs:
        ikiwa issubclass(cls, base) na sio any(
                issubclass(b, base) kila b kwenye cls.__bases__
            ):
            # If *cls* ni the kundi that introduces behaviour described by
            # an ABC *base*, insert said ABC to its MRO.
            abstract_bases.append(base)
    kila base kwenye abstract_bases:
        abcs.remove(base)
    explicit_c3_mros = [_c3_mro(base, abcs=abcs) kila base kwenye explicit_bases]
    abstract_c3_mros = [_c3_mro(base, abcs=abcs) kila base kwenye abstract_bases]
    other_c3_mros = [_c3_mro(base, abcs=abcs) kila base kwenye other_bases]
    rudisha _c3_merge(
        [[cls]] +
        explicit_c3_mros + abstract_c3_mros + other_c3_mros +
        [explicit_bases] + [abstract_bases] + [other_bases]
    )

eleza _compose_mro(cls, types):
    """Calculates the method resolution order kila a given kundi *cls*.

    Includes relevant abstract base classes (ukijumuisha their respective bases) kutoka
    the *types* iterable. Uses a modified C3 linearization algorithm.

    """
    bases = set(cls.__mro__)
    # Remove entries which are already present kwenye the __mro__ ama unrelated.
    eleza is_related(typ):
        rudisha (typ haiko kwenye bases na hasattr(typ, '__mro__')
                                 na issubclass(cls, typ))
    types = [n kila n kwenye types ikiwa is_related(n)]
    # Remove entries which are strict bases of other entries (they will end up
    # kwenye the MRO anyway.
    eleza is_strict_base(typ):
        kila other kwenye types:
            ikiwa typ != other na typ kwenye other.__mro__:
                rudisha Kweli
        rudisha Uongo
    types = [n kila n kwenye types ikiwa sio is_strict_base(n)]
    # Subclasses of the ABCs kwenye *types* which are also implemented by
    # *cls* can be used to stabilize ABC ordering.
    type_set = set(types)
    mro = []
    kila typ kwenye types:
        found = []
        kila sub kwenye typ.__subclasses__():
            ikiwa sub haiko kwenye bases na issubclass(cls, sub):
                found.append([s kila s kwenye sub.__mro__ ikiwa s kwenye type_set])
        ikiwa sio found:
            mro.append(typ)
            endelea
        # Favor subclasses ukijumuisha the biggest number of useful bases
        found.sort(key=len, reverse=Kweli)
        kila sub kwenye found:
            kila subcls kwenye sub:
                ikiwa subcls haiko kwenye mro:
                    mro.append(subcls)
    rudisha _c3_mro(cls, abcs=mro)

eleza _find_impl(cls, registry):
    """Returns the best matching implementation kutoka *registry* kila type *cls*.

    Where there ni no registered implementation kila a specific type, its method
    resolution order ni used to find a more generic implementation.

    Note: ikiwa *registry* does sio contain an implementation kila the base
    *object* type, this function may rudisha Tupu.

    """
    mro = _compose_mro(cls, registry.keys())
    match = Tupu
    kila t kwenye mro:
        ikiwa match ni sio Tupu:
            # If *match* ni an implicit ABC but there ni another unrelated,
            # equally matching implicit ABC, refuse the temptation to guess.
            ikiwa (t kwenye registry na t haiko kwenye cls.__mro__
                              na match haiko kwenye cls.__mro__
                              na sio issubclass(match, t)):
                ashiria RuntimeError("Ambiguous dispatch: {} ama {}".format(
                    match, t))
            koma
        ikiwa t kwenye regisjaribu:
            match = t
    rudisha registry.get(match)

eleza singledispatch(func):
    """Single-dispatch generic function decorator.

    Transforms a function into a generic function, which can have different
    behaviours depending upon the type of its first argument. The decorated
    function acts kama the default implementation, na additional
    implementations can be registered using the register() attribute of the
    generic function.
    """
    # There are many programs that use functools without singledispatch, so we
    # trade-off making singledispatch marginally slower kila the benefit of
    # making start-up of such applications slightly faster.
    agiza types, weakref

    registry = {}
    dispatch_cache = weakref.WeakKeyDictionary()
    cache_token = Tupu

    eleza dispatch(cls):
        """generic_func.dispatch(cls) -> <function implementation>

        Runs the dispatch algorithm to rudisha the best available implementation
        kila the given *cls* registered on *generic_func*.

        """
        nonlocal cache_token
        ikiwa cache_token ni sio Tupu:
            current_token = get_cache_token()
            ikiwa cache_token != current_token:
                dispatch_cache.clear()
                cache_token = current_token
        jaribu:
            impl = dispatch_cache[cls]
        tatizo KeyError:
            jaribu:
                impl = registry[cls]
            tatizo KeyError:
                impl = _find_impl(cls, registry)
            dispatch_cache[cls] = impl
        rudisha impl

    eleza register(cls, func=Tupu):
        """generic_func.register(cls, func) -> func

        Registers a new implementation kila the given *cls* on a *generic_func*.

        """
        nonlocal cache_token
        ikiwa func ni Tupu:
            ikiwa isinstance(cls, type):
                rudisha lambda f: register(cls, f)
            ann = getattr(cls, '__annotations__', {})
            ikiwa sio ann:
                ashiria TypeError(
                    f"Invalid first argument to `register()`: {cls!r}. "
                    f"Use either `@register(some_class)` ama plain `@register` "
                    f"on an annotated function."
                )
            func = cls

            # only agiza typing ikiwa annotation parsing ni necessary
            kutoka typing agiza get_type_hints
            argname, cls = next(iter(get_type_hints(func).items()))
            ikiwa sio isinstance(cls, type):
                ashiria TypeError(
                    f"Invalid annotation kila {argname!r}. "
                    f"{cls!r} ni sio a class."
                )
        registry[cls] = func
        ikiwa cache_token ni Tupu na hasattr(cls, '__abstractmethods__'):
            cache_token = get_cache_token()
        dispatch_cache.clear()
        rudisha func

    eleza wrapper(*args, **kw):
        ikiwa sio args:
            ashiria TypeError(f'{funcname} requires at least '
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

    Supports wrapping existing descriptors na handles non-descriptor
    callables kama instance methods.
    """

    eleza __init__(self, func):
        ikiwa sio callable(func) na sio hasattr(func, "__get__"):
            ashiria TypeError(f"{func!r} ni sio callable ama a descriptor")

        self.dispatcher = singledispatch(func)
        self.func = func

    eleza register(self, cls, method=Tupu):
        """generic_method.register(cls, func) -> func

        Registers a new implementation kila the given *cls* on a *generic_method*.
        """
        rudisha self.dispatcher.register(cls, func=method)

    eleza __get__(self, obj, cls=Tupu):
        eleza _method(*args, **kwargs):
            method = self.dispatcher.dispatch(args[0].__class__)
            rudisha method.__get__(obj, cls)(*args, **kwargs)

        _method.__isabstractmethod__ = self.__isabstractmethod__
        _method.register = self.register
        update_wrapper(_method, self.func)
        rudisha _method

    @property
    eleza __isabstractmethod__(self):
        rudisha getattr(self.func, '__isabstractmethod__', Uongo)


################################################################################
### cached_property() - computed once per instance, cached kama attribute
################################################################################

_NOT_FOUND = object()


kundi cached_property:
    eleza __init__(self, func):
        self.func = func
        self.attrname = Tupu
        self.__doc__ = func.__doc__
        self.lock = RLock()

    eleza __set_name__(self, owner, name):
        ikiwa self.attrname ni Tupu:
            self.attrname = name
        lasivyo name != self.attrname:
            ashiria TypeError(
                "Cannot assign the same cached_property to two different names "
                f"({self.attrname!r} na {name!r})."
            )

    eleza __get__(self, instance, owner=Tupu):
        ikiwa instance ni Tupu:
            rudisha self
        ikiwa self.attrname ni Tupu:
            ashiria TypeError(
                "Cannot use cached_property instance without calling __set_name__ on it.")
        jaribu:
            cache = instance.__dict__
        tatizo AttributeError:  # sio all objects have __dict__ (e.g. kundi defines slots)
            msg = (
                f"No '__dict__' attribute on {type(instance).__name__!r} "
                f"instance to cache {self.attrname!r} property."
            )
            ashiria TypeError(msg) kutoka Tupu
        val = cache.get(self.attrname, _NOT_FOUND)
        ikiwa val ni _NOT_FOUND:
            ukijumuisha self.lock:
                # check ikiwa another thread filled cache wakati we awaited lock
                val = cache.get(self.attrname, _NOT_FOUND)
                ikiwa val ni _NOT_FOUND:
                    val = self.func(instance)
                    jaribu:
                        cache[self.attrname] = val
                    tatizo TypeError:
                        msg = (
                            f"The '__dict__' attribute on {type(instance).__name__!r} instance "
                            f"does sio support item assignment kila caching {self.attrname!r} property."
                        )
                        ashiria TypeError(msg) kutoka Tupu
        rudisha val
