"""
The typing module: Support kila gradual typing kama defined by PEP 484.

At large scale, the structure of the module ni following:
* Imports na exports, all public names should be explicitly added to __all__.
* Internal helper functions: these should never be used kwenye code outside this module.
* _SpecialForm na its instances (special forms): Any, NoReturn, ClassVar, Union, Optional
* Two classes whose instances can be type arguments kwenye addition to types: ForwardRef na TypeVar
* The core of internal generics API: _GenericAlias na _VariadicGenericAlias, the latter is
  currently only used by Tuple na Callable. All subscripted types like X[int], Union[int, str],
  etc., are instances of either of these classes.
* The public counterpart of the generics API consists of two classes: Generic na Protocol.
* Public helper functions: get_type_hints, overload, cast, no_type_check,
  no_type_check_decorator.
* Generic aliases kila collections.abc ABCs na few additional protocols.
* Special types: NewType, NamedTuple, TypedDict (may be added soon).
* Wrapper submodules kila re na io related types.
"""

kutoka abc agiza abstractmethod, ABCMeta
agiza collections
agiza collections.abc
agiza contextlib
agiza functools
agiza operator
agiza re kama stdlib_re  # Avoid confusion with the re we export.
agiza sys
agiza types
kutoka types agiza WrapperDescriptorType, MethodWrapperType, MethodDescriptorType

# Please keep __all__ alphabetized within each category.
__all__ = [
    # Super-special typing primitives.
    'Any',
    'Callable',
    'ClassVar',
    'Final',
    'ForwardRef',
    'Generic',
    'Literal',
    'Optional',
    'Protocol',
    'Tuple',
    'Type',
    'TypeVar',
    'Union',

    # ABCs (kutoka collections.abc).
    'AbstractSet',  # collections.abc.Set.
    'ByteString',
    'Container',
    'ContextManager',
    'Hashable',
    'ItemsView',
    'Iterable',
    'Iterator',
    'KeysView',
    'Mapping',
    'MappingView',
    'MutableMapping',
    'MutableSequence',
    'MutableSet',
    'Sequence',
    'Sized',
    'ValuesView',
    'Awaitable',
    'AsyncIterator',
    'AsyncIterable',
    'Coroutine',
    'Collection',
    'AsyncGenerator',
    'AsyncContextManager',

    # Structural checks, a.k.a. protocols.
    'Reversible',
    'SupportsAbs',
    'SupportsBytes',
    'SupportsComplex',
    'SupportsFloat',
    'SupportsIndex',
    'SupportsInt',
    'SupportsRound',

    # Concrete collection types.
    'ChainMap',
    'Counter',
    'Deque',
    'Dict',
    'DefaultDict',
    'List',
    'OrderedDict',
    'Set',
    'FrozenSet',
    'NamedTuple',  # Not really a type.
    'TypedDict',  # Not really a type.
    'Generator',

    # One-off things.
    'AnyStr',
    'cast',
    'final',
    'get_args',
    'get_origin',
    'get_type_hints',
    'NewType',
    'no_type_check',
    'no_type_check_decorator',
    'NoReturn',
    'overload',
    'runtime_checkable',
    'Text',
    'TYPE_CHECKING',
]

# The pseudo-submodules 're' na 'io' are part of the public
# namespace, but excluded kutoka __all__ because they might stomp on
# legitimate agizas of those modules.


eleza _type_check(arg, msg, is_argument=Kweli):
    """Check that the argument ni a type, na rudisha it (internal helper).

    As a special case, accept Tupu na rudisha type(Tupu) instead. Also wrap strings
    into ForwardRef instances. Consider several corner cases, kila example plain
    special forms like Union are sio valid, wakati Union[int, str] ni OK, etc.
    The msg argument ni a human-readable error message, e.g::

        "Union[arg, ...]: arg should be a type."

    We append the repr() of the actual value (truncated to 100 chars).
    """
    invalid_generic_forms = (Generic, Protocol)
    ikiwa is_argument:
        invalid_generic_forms = invalid_generic_forms + (ClassVar, Final)

    ikiwa arg ni Tupu:
        rudisha type(Tupu)
    ikiwa isinstance(arg, str):
        rudisha ForwardRef(arg)
    ikiwa (isinstance(arg, _GenericAlias) and
            arg.__origin__ kwenye invalid_generic_forms):
        ashiria TypeError(f"{arg} ni sio valid kama type argument")
    ikiwa (isinstance(arg, _SpecialForm) na arg haiko kwenye (Any, NoReturn) or
            arg kwenye (Generic, Protocol)):
        ashiria TypeError(f"Plain {arg} ni sio valid kama type argument")
    ikiwa isinstance(arg, (type, TypeVar, ForwardRef)):
        rudisha arg
    ikiwa sio callable(arg):
        ashiria TypeError(f"{msg} Got {arg!r:.100}.")
    rudisha arg


eleza _type_repr(obj):
    """Return the repr() of an object, special-casing types (internal helper).

    If obj ni a type, we rudisha a shorter version than the default
    type.__repr__, based on the module na qualified name, which is
    typically enough to uniquely identify a type.  For everything
    else, we fall back on repr(obj).
    """
    ikiwa isinstance(obj, type):
        ikiwa obj.__module__ == 'builtins':
            rudisha obj.__qualname__
        rudisha f'{obj.__module__}.{obj.__qualname__}'
    ikiwa obj ni ...:
        rudisha('...')
    ikiwa isinstance(obj, types.FunctionType):
        rudisha obj.__name__
    rudisha repr(obj)


eleza _collect_type_vars(types):
    """Collect all type variable contained kwenye types kwenye order of
    first appearance (lexicographic order). For example::

        _collect_type_vars((T, List[S, T])) == (T, S)
    """
    tvars = []
    kila t kwenye types:
        ikiwa isinstance(t, TypeVar) na t haiko kwenye tvars:
            tvars.append(t)
        ikiwa isinstance(t, _GenericAlias) na sio t._special:
            tvars.extend([t kila t kwenye t.__parameters__ ikiwa t haiko kwenye tvars])
    rudisha tuple(tvars)


eleza _subs_tvars(tp, tvars, subs):
    """Substitute type variables 'tvars' with substitutions 'subs'.
    These two must have the same length.
    """
    ikiwa sio isinstance(tp, _GenericAlias):
        rudisha tp
    new_args = list(tp.__args__)
    kila a, arg kwenye enumerate(tp.__args__):
        ikiwa isinstance(arg, TypeVar):
            kila i, tvar kwenye enumerate(tvars):
                ikiwa arg == tvar:
                    new_args[a] = subs[i]
        isipokua:
            new_args[a] = _subs_tvars(arg, tvars, subs)
    ikiwa tp.__origin__ ni Union:
        rudisha Union[tuple(new_args)]
    rudisha tp.copy_with(tuple(new_args))


eleza _check_generic(cls, parameters):
    """Check correct count kila parameters of a generic cls (internal helper).
    This gives a nice error message kwenye case of count mismatch.
    """
    ikiwa sio cls.__parameters__:
        ashiria TypeError(f"{cls} ni sio a generic class")
    alen = len(parameters)
    elen = len(cls.__parameters__)
    ikiwa alen != elen:
        ashiria TypeError(f"Too {'many' ikiwa alen > elen else 'few'} parameters kila {cls};"
                        f" actual {alen}, expected {elen}")


eleza _remove_dups_flatten(parameters):
    """An internal helper kila Union creation na substitution: flatten Unions
    among parameters, then remove duplicates.
    """
    # Flatten out Union[Union[...], ...].
    params = []
    kila p kwenye parameters:
        ikiwa isinstance(p, _GenericAlias) na p.__origin__ ni Union:
            params.extend(p.__args__)
        elikiwa isinstance(p, tuple) na len(p) > 0 na p[0] ni Union:
            params.extend(p[1:])
        isipokua:
            params.append(p)
    # Weed out strict duplicates, preserving the first of each occurrence.
    all_params = set(params)
    ikiwa len(all_params) < len(params):
        new_params = []
        kila t kwenye params:
            ikiwa t kwenye all_params:
                new_params.append(t)
                all_params.remove(t)
        params = new_params
        assert sio all_params, all_params
    rudisha tuple(params)


_cleanups = []


eleza _tp_cache(func):
    """Internal wrapper caching __getitem__ of generic types with a fallback to
    original function kila non-hashable arguments.
    """
    cached = functools.lru_cache()(func)
    _cleanups.append(cached.cache_clear)

    @functools.wraps(func)
    eleza inner(*args, **kwds):
        jaribu:
            rudisha cached(*args, **kwds)
        tatizo TypeError:
            pita  # All real errors (not unhashable args) are ashiriad below.
        rudisha func(*args, **kwds)
    rudisha inner


eleza _eval_type(t, globalns, localns):
    """Evaluate all forward reverences kwenye the given type t.
    For use of globalns na localns see the docstring kila get_type_hints().
    """
    ikiwa isinstance(t, ForwardRef):
        rudisha t._evaluate(globalns, localns)
    ikiwa isinstance(t, _GenericAlias):
        ev_args = tuple(_eval_type(a, globalns, localns) kila a kwenye t.__args__)
        ikiwa ev_args == t.__args__:
            rudisha t
        res = t.copy_with(ev_args)
        res._special = t._special
        rudisha res
    rudisha t


kundi _Final:
    """Mixin to prohibit subclassing"""

    __slots__ = ('__weakref__',)

    eleza __init_subclass__(self, /, *args, **kwds):
        ikiwa '_root' haiko kwenye kwds:
            ashiria TypeError("Cannot subkundi special typing classes")

kundi _Immutable:
    """Mixin to indicate that object should sio be copied."""

    eleza __copy__(self):
        rudisha self

    eleza __deepcopy__(self, memo):
        rudisha self


kundi _SpecialForm(_Final, _Immutable, _root=Kweli):
    """Internal indicator of special typing constructs.
    See _doc instance attribute kila specific docs.
    """

    __slots__ = ('_name', '_doc')

    eleza __new__(cls, *args, **kwds):
        """Constructor.

        This only exists to give a better error message kwenye case
        someone tries to subkundi a special typing object (not a good idea).
        """
        ikiwa (len(args) == 3 and
                isinstance(args[0], str) and
                isinstance(args[1], tuple)):
            # Close enough.
            ashiria TypeError(f"Cannot subkundi {cls!r}")
        rudisha super().__new__(cls)

    eleza __init__(self, name, doc):
        self._name = name
        self._doc = doc

    eleza __eq__(self, other):
        ikiwa sio isinstance(other, _SpecialForm):
            rudisha NotImplemented
        rudisha self._name == other._name

    eleza __hash__(self):
        rudisha hash((self._name,))

    eleza __repr__(self):
        rudisha 'typing.' + self._name

    eleza __reduce__(self):
        rudisha self._name

    eleza __call__(self, *args, **kwds):
        ashiria TypeError(f"Cannot instantiate {self!r}")

    eleza __instancecheck__(self, obj):
        ashiria TypeError(f"{self} cannot be used with isinstance()")

    eleza __subclasscheck__(self, cls):
        ashiria TypeError(f"{self} cannot be used with issubclass()")

    @_tp_cache
    eleza __getitem__(self, parameters):
        ikiwa self._name kwenye ('ClassVar', 'Final'):
            item = _type_check(parameters, f'{self._name} accepts only single type.')
            rudisha _GenericAlias(self, (item,))
        ikiwa self._name == 'Union':
            ikiwa parameters == ():
                ashiria TypeError("Cannot take a Union of no types.")
            ikiwa sio isinstance(parameters, tuple):
                parameters = (parameters,)
            msg = "Union[arg, ...]: each arg must be a type."
            parameters = tuple(_type_check(p, msg) kila p kwenye parameters)
            parameters = _remove_dups_flatten(parameters)
            ikiwa len(parameters) == 1:
                rudisha parameters[0]
            rudisha _GenericAlias(self, parameters)
        ikiwa self._name == 'Optional':
            arg = _type_check(parameters, "Optional[t] requires a single type.")
            rudisha Union[arg, type(Tupu)]
        ikiwa self._name == 'Literal':
            # There ni no '_type_check' call because arguments to Literal[...] are
            # values, sio types.
            rudisha _GenericAlias(self, parameters)
        ashiria TypeError(f"{self} ni sio subscriptable")


Any = _SpecialForm('Any', doc=
    """Special type indicating an unconstrained type.

    - Any ni compatible with every type.
    - Any assumed to have all methods.
    - All values assumed to be instances of Any.

    Note that all the above statements are true kutoka the point of view of
    static type checkers. At runtime, Any should sio be used with instance
    ama kundi checks.
    """)

NoReturn = _SpecialForm('NoReturn', doc=
    """Special type indicating functions that never rudisha.
    Example::

      kutoka typing agiza NoReturn

      eleza stop() -> NoReturn:
          ashiria Exception('no way')

    This type ni invalid kwenye other positions, e.g., ``List[NoReturn]``
    will fail kwenye static type checkers.
    """)

ClassVar = _SpecialForm('ClassVar', doc=
    """Special type construct to mark kundi variables.

    An annotation wrapped kwenye ClassVar indicates that a given
    attribute ni intended to be used kama a kundi variable and
    should sio be set on instances of that class. Usage::

      kundi Starship:
          stats: ClassVar[Dict[str, int]] = {} # kundi variable
          damage: int = 10                     # instance variable

    ClassVar accepts only types na cannot be further subscribed.

    Note that ClassVar ni sio a kundi itself, na should not
    be used with isinstance() ama issubclass().
    """)

Final = _SpecialForm('Final', doc=
    """Special typing construct to indicate final names to type checkers.

    A final name cannot be re-assigned ama overridden kwenye a subclass.
    For example:

      MAX_SIZE: Final = 9000
      MAX_SIZE += 1  # Error reported by type checker

      kundi Connection:
          TIMEOUT: Final[int] = 10

      kundi FastConnector(Connection):
          TIMEOUT = 1  # Error reported by type checker

    There ni no runtime checking of these properties.
    """)

Union = _SpecialForm('Union', doc=
    """Union type; Union[X, Y] means either X ama Y.

    To define a union, use e.g. Union[int, str].  Details:
    - The arguments must be types na there must be at least one.
    - Tupu kama an argument ni a special case na ni replaced by
      type(Tupu).
    - Unions of unions are flattened, e.g.::

        Union[Union[int, str], float] == Union[int, str, float]

    - Unions of a single argument vanish, e.g.::

        Union[int] == int  # The constructor actually rudishas int

    - Redundant arguments are skipped, e.g.::

        Union[int, str, int] == Union[int, str]

    - When comparing unions, the argument order ni ignored, e.g.::

        Union[int, str] == Union[str, int]

    - You cannot subkundi ama instantiate a union.
    - You can use Optional[X] kama a shorthand kila Union[X, Tupu].
    """)

Optional = _SpecialForm('Optional', doc=
    """Optional type.

    Optional[X] ni equivalent to Union[X, Tupu].
    """)

Literal = _SpecialForm('Literal', doc=
    """Special typing form to define literal types (a.k.a. value types).

    This form can be used to indicate to type checkers that the corresponding
    variable ama function parameter has a value equivalent to the provided
    literal (or one of several literals):

      eleza validate_simple(data: Any) -> Literal[Kweli]:  # always rudishas Kweli
          ...

      MODE = Literal['r', 'rb', 'w', 'wb']
      eleza open_helper(file: str, mode: MODE) -> str:
          ...

      open_helper('/some/path', 'r')  # Passes type check
      open_helper('/other/path', 'typo')  # Error kwenye type checker

   Literal[...] cannot be subclassed. At runtime, an arbitrary value
   ni allowed kama type argument to Literal[...], but type checkers may
   impose restrictions.
    """)


kundi ForwardRef(_Final, _root=Kweli):
    """Internal wrapper to hold a forward reference."""

    __slots__ = ('__forward_arg__', '__forward_code__',
                 '__forward_evaluated__', '__forward_value__',
                 '__forward_is_argument__')

    eleza __init__(self, arg, is_argument=Kweli):
        ikiwa sio isinstance(arg, str):
            ashiria TypeError(f"Forward reference must be a string -- got {arg!r}")
        jaribu:
            code = compile(arg, '<string>', 'eval')
        tatizo SyntaxError:
            ashiria SyntaxError(f"Forward reference must be an expression -- got {arg!r}")
        self.__forward_arg__ = arg
        self.__forward_code__ = code
        self.__forward_evaluated__ = Uongo
        self.__forward_value__ = Tupu
        self.__forward_is_argument__ = is_argument

    eleza _evaluate(self, globalns, localns):
        ikiwa sio self.__forward_evaluated__ ama localns ni sio globalns:
            ikiwa globalns ni Tupu na localns ni Tupu:
                globalns = localns = {}
            elikiwa globalns ni Tupu:
                globalns = localns
            elikiwa localns ni Tupu:
                localns = globalns
            self.__forward_value__ = _type_check(
                eval(self.__forward_code__, globalns, localns),
                "Forward references must evaluate to types.",
                is_argument=self.__forward_is_argument__)
            self.__forward_evaluated__ = Kweli
        rudisha self.__forward_value__

    eleza __eq__(self, other):
        ikiwa sio isinstance(other, ForwardRef):
            rudisha NotImplemented
        ikiwa self.__forward_evaluated__ na other.__forward_evaluated__:
            rudisha (self.__forward_arg__ == other.__forward_arg__ and
                    self.__forward_value__ == other.__forward_value__)
        rudisha self.__forward_arg__ == other.__forward_arg__

    eleza __hash__(self):
        rudisha hash(self.__forward_arg__)

    eleza __repr__(self):
        rudisha f'ForwardRef({self.__forward_arg__!r})'


kundi TypeVar(_Final, _Immutable, _root=Kweli):
    """Type variable.

    Usage::

      T = TypeVar('T')  # Can be anything
      A = TypeVar('A', str, bytes)  # Must be str ama bytes

    Type variables exist primarily kila the benefit of static type
    checkers.  They serve kama the parameters kila generic types kama well
    kama kila generic function definitions.  See kundi Generic kila more
    information on generic types.  Generic functions work kama follows:

      eleza repeat(x: T, n: int) -> List[T]:
          '''Return a list containing n references to x.'''
          rudisha [x]*n

      eleza longest(x: A, y: A) -> A:
          '''Return the longest of two strings.'''
          rudisha x ikiwa len(x) >= len(y) else y

    The latter example's signature ni essentially the overloading
    of (str, str) -> str na (bytes, bytes) -> bytes.  Also note
    that ikiwa the arguments are instances of some subkundi of str,
    the rudisha type ni still plain str.

    At runtime, isinstance(x, T) na issubclass(C, T) will ashiria TypeError.

    Type variables defined with covariant=Kweli ama contravariant=Kweli
    can be used to declare covariant ama contravariant generic types.
    See PEP 484 kila more details. By default generic types are invariant
    kwenye all type variables.

    Type variables can be introspected. e.g.:

      T.__name__ == 'T'
      T.__constraints__ == ()
      T.__covariant__ == Uongo
      T.__contravariant__ = Uongo
      A.__constraints__ == (str, bytes)

    Note that only type variables defined kwenye global scope can be pickled.
    """

    __slots__ = ('__name__', '__bound__', '__constraints__',
                 '__covariant__', '__contravariant__')

    eleza __init__(self, name, *constraints, bound=Tupu,
                 covariant=Uongo, contravariant=Uongo):
        self.__name__ = name
        ikiwa covariant na contravariant:
            ashiria ValueError("Bivariant types are sio supported.")
        self.__covariant__ = bool(covariant)
        self.__contravariant__ = bool(contravariant)
        ikiwa constraints na bound ni sio Tupu:
            ashiria TypeError("Constraints cannot be combined with bound=...")
        ikiwa constraints na len(constraints) == 1:
            ashiria TypeError("A single constraint ni sio allowed")
        msg = "TypeVar(name, constraint, ...): constraints must be types."
        self.__constraints__ = tuple(_type_check(t, msg) kila t kwenye constraints)
        ikiwa bound:
            self.__bound__ = _type_check(bound, "Bound must be a type.")
        isipokua:
            self.__bound__ = Tupu
        def_mod = sys._getframe(1).f_globals['__name__']  # kila pickling
        ikiwa def_mod != 'typing':
            self.__module__ = def_mod

    eleza __repr__(self):
        ikiwa self.__covariant__:
            prefix = '+'
        elikiwa self.__contravariant__:
            prefix = '-'
        isipokua:
            prefix = '~'
        rudisha prefix + self.__name__

    eleza __reduce__(self):
        rudisha self.__name__


# Special typing constructs Union, Optional, Generic, Callable na Tuple
# use three special attributes kila internal bookkeeping of generic types:
# * __parameters__ ni a tuple of unique free type parameters of a generic
#   type, kila example, Dict[T, T].__parameters__ == (T,);
# * __origin__ keeps a reference to a type that was subscripted,
#   e.g., Union[T, int].__origin__ == Union, ama the non-generic version of
#   the type.
# * __args__ ni a tuple of all arguments used kwenye subscripting,
#   e.g., Dict[T, int].__args__ == (T, int).


# Mapping kutoka non-generic type names that have a generic alias kwenye typing
# but with a different name.
_normalize_alias = {'list': 'List',
                    'tuple': 'Tuple',
                    'dict': 'Dict',
                    'set': 'Set',
                    'frozenset': 'FrozenSet',
                    'deque': 'Deque',
                    'defaultdict': 'DefaultDict',
                    'type': 'Type',
                    'Set': 'AbstractSet'}

eleza _is_dunder(attr):
    rudisha attr.startswith('__') na attr.endswith('__')


kundi _GenericAlias(_Final, _root=Kweli):
    """The central part of internal API.

    This represents a generic version of type 'origin' with type arguments 'params'.
    There are two kind of these aliases: user defined na special. The special ones
    are wrappers around builtin collections na ABCs kwenye collections.abc. These must
    have 'name' always set. If 'inst' ni Uongo, then the alias can't be instantiated,
    this ni used by e.g. typing.List na typing.Dict.
    """
    eleza __init__(self, origin, params, *, inst=Kweli, special=Uongo, name=Tupu):
        self._inst = inst
        self._special = special
        ikiwa special na name ni Tupu:
            orig_name = origin.__name__
            name = _normalize_alias.get(orig_name, orig_name)
        self._name = name
        ikiwa sio isinstance(params, tuple):
            params = (params,)
        self.__origin__ = origin
        self.__args__ = tuple(... ikiwa a ni _TypingEllipsis else
                              () ikiwa a ni _TypingEmpty else
                              a kila a kwenye params)
        self.__parameters__ = _collect_type_vars(params)
        self.__slots__ = Tupu  # This ni sio documented.
        ikiwa sio name:
            self.__module__ = origin.__module__

    @_tp_cache
    eleza __getitem__(self, params):
        ikiwa self.__origin__ kwenye (Generic, Protocol):
            # Can't subscript Generic[...] ama Protocol[...].
            ashiria TypeError(f"Cannot subscript already-subscripted {self}")
        ikiwa sio isinstance(params, tuple):
            params = (params,)
        msg = "Parameters to generic types must be types."
        params = tuple(_type_check(p, msg) kila p kwenye params)
        _check_generic(self, params)
        rudisha _subs_tvars(self, self.__parameters__, params)

    eleza copy_with(self, params):
        # We don't copy self._special.
        rudisha _GenericAlias(self.__origin__, params, name=self._name, inst=self._inst)

    eleza __repr__(self):
        ikiwa (self._name != 'Callable' or
                len(self.__args__) == 2 na self.__args__[0] ni Ellipsis):
            ikiwa self._name:
                name = 'typing.' + self._name
            isipokua:
                name = _type_repr(self.__origin__)
            ikiwa sio self._special:
                args = f'[{", ".join([_type_repr(a) kila a kwenye self.__args__])}]'
            isipokua:
                args = ''
            rudisha (f'{name}{args}')
        ikiwa self._special:
            rudisha 'typing.Callable'
        rudisha (f'typing.Callable'
                f'[[{", ".join([_type_repr(a) kila a kwenye self.__args__[:-1]])}], '
                f'{_type_repr(self.__args__[-1])}]')

    eleza __eq__(self, other):
        ikiwa sio isinstance(other, _GenericAlias):
            rudisha NotImplemented
        ikiwa self.__origin__ != other.__origin__:
            rudisha Uongo
        ikiwa self.__origin__ ni Union na other.__origin__ ni Union:
            rudisha frozenset(self.__args__) == frozenset(other.__args__)
        rudisha self.__args__ == other.__args__

    eleza __hash__(self):
        ikiwa self.__origin__ ni Union:
            rudisha hash((Union, frozenset(self.__args__)))
        rudisha hash((self.__origin__, self.__args__))

    eleza __call__(self, *args, **kwargs):
        ikiwa sio self._inst:
            ashiria TypeError(f"Type {self._name} cannot be instantiated; "
                            f"use {self._name.lower()}() instead")
        result = self.__origin__(*args, **kwargs)
        jaribu:
            result.__orig_class__ = self
        tatizo AttributeError:
            pita
        rudisha result

    eleza __mro_entries__(self, bases):
        ikiwa self._name:  # generic version of an ABC ama built-in class
            res = []
            ikiwa self.__origin__ haiko kwenye bases:
                res.append(self.__origin__)
            i = bases.index(self)
            ikiwa sio any(isinstance(b, _GenericAlias) ama issubclass(b, Generic)
                       kila b kwenye bases[i+1:]):
                res.append(Generic)
            rudisha tuple(res)
        ikiwa self.__origin__ ni Generic:
            ikiwa Protocol kwenye bases:
                rudisha ()
            i = bases.index(self)
            kila b kwenye bases[i+1:]:
                ikiwa isinstance(b, _GenericAlias) na b ni sio self:
                    rudisha ()
        rudisha (self.__origin__,)

    eleza __getattr__(self, attr):
        # We are careful kila copy na pickle.
        # Also kila simplicity we just don't relay all dunder names
        ikiwa '__origin__' kwenye self.__dict__ na sio _is_dunder(attr):
            rudisha getattr(self.__origin__, attr)
        ashiria AttributeError(attr)

    eleza __setattr__(self, attr, val):
        ikiwa _is_dunder(attr) ama attr kwenye ('_name', '_inst', '_special'):
            super().__setattr__(attr, val)
        isipokua:
            setattr(self.__origin__, attr, val)

    eleza __instancecheck__(self, obj):
        rudisha self.__subclasscheck__(type(obj))

    eleza __subclasscheck__(self, cls):
        ikiwa self._special:
            ikiwa sio isinstance(cls, _GenericAlias):
                rudisha issubclass(cls, self.__origin__)
            ikiwa cls._special:
                rudisha issubclass(cls.__origin__, self.__origin__)
        ashiria TypeError("Subscripted generics cannot be used with"
                        " kundi na instance checks")

    eleza __reduce__(self):
        ikiwa self._special:
            rudisha self._name

        ikiwa self._name:
            origin = globals()[self._name]
        isipokua:
            origin = self.__origin__
        ikiwa (origin ni Callable and
            sio (len(self.__args__) == 2 na self.__args__[0] ni Ellipsis)):
            args = list(self.__args__[:-1]), self.__args__[-1]
        isipokua:
            args = tuple(self.__args__)
            ikiwa len(args) == 1 na sio isinstance(args[0], tuple):
                args, = args
        rudisha operator.getitem, (origin, args)


kundi _VariadicGenericAlias(_GenericAlias, _root=Kweli):
    """Same kama _GenericAlias above but kila variadic aliases. Currently,
    this ni used only by special internal aliases: Tuple na Callable.
    """
    eleza __getitem__(self, params):
        ikiwa self._name != 'Callable' ama sio self._special:
            rudisha self.__getitem_inner__(params)
        ikiwa sio isinstance(params, tuple) ama len(params) != 2:
            ashiria TypeError("Callable must be used kama "
                            "Callable[[arg, ...], result].")
        args, result = params
        ikiwa args ni Ellipsis:
            params = (Ellipsis, result)
        isipokua:
            ikiwa sio isinstance(args, list):
                ashiria TypeError(f"Callable[args, result]: args must be a list."
                                f" Got {args}")
            params = (tuple(args), result)
        rudisha self.__getitem_inner__(params)

    @_tp_cache
    eleza __getitem_inner__(self, params):
        ikiwa self.__origin__ ni tuple na self._special:
            ikiwa params == ():
                rudisha self.copy_with((_TypingEmpty,))
            ikiwa sio isinstance(params, tuple):
                params = (params,)
            ikiwa len(params) == 2 na params[1] ni ...:
                msg = "Tuple[t, ...]: t must be a type."
                p = _type_check(params[0], msg)
                rudisha self.copy_with((p, _TypingEllipsis))
            msg = "Tuple[t0, t1, ...]: each t must be a type."
            params = tuple(_type_check(p, msg) kila p kwenye params)
            rudisha self.copy_with(params)
        ikiwa self.__origin__ ni collections.abc.Callable na self._special:
            args, result = params
            msg = "Callable[args, result]: result must be a type."
            result = _type_check(result, msg)
            ikiwa args ni Ellipsis:
                rudisha self.copy_with((_TypingEllipsis, result))
            msg = "Callable[[arg, ...], result]: each arg must be a type."
            args = tuple(_type_check(arg, msg) kila arg kwenye args)
            params = args + (result,)
            rudisha self.copy_with(params)
        rudisha super().__getitem__(params)


kundi Generic:
    """Abstract base kundi kila generic types.

    A generic type ni typically declared by inheriting kutoka
    this kundi parameterized with one ama more type variables.
    For example, a generic mapping type might be defined as::

      kundi Mapping(Generic[KT, VT]):
          eleza __getitem__(self, key: KT) -> VT:
              ...
          # Etc.

    This kundi can then be used kama follows::

      eleza lookup_name(mapping: Mapping[KT, VT], key: KT, default: VT) -> VT:
          jaribu:
              rudisha mapping[key]
          tatizo KeyError:
              rudisha default
    """
    __slots__ = ()
    _is_protocol = Uongo

    eleza __new__(cls, *args, **kwds):
        ikiwa cls kwenye (Generic, Protocol):
            ashiria TypeError(f"Type {cls.__name__} cannot be instantiated; "
                            "it can be used only kama a base class")
        ikiwa super().__new__ ni object.__new__ na cls.__init__ ni sio object.__init__:
            obj = super().__new__(cls)
        isipokua:
            obj = super().__new__(cls, *args, **kwds)
        rudisha obj

    @_tp_cache
    eleza __class_getitem__(cls, params):
        ikiwa sio isinstance(params, tuple):
            params = (params,)
        ikiwa sio params na cls ni sio Tuple:
            ashiria TypeError(
                f"Parameter list to {cls.__qualname__}[...] cannot be empty")
        msg = "Parameters to generic types must be types."
        params = tuple(_type_check(p, msg) kila p kwenye params)
        ikiwa cls kwenye (Generic, Protocol):
            # Generic na Protocol can only be subscripted with unique type variables.
            ikiwa sio all(isinstance(p, TypeVar) kila p kwenye params):
                ashiria TypeError(
                    f"Parameters to {cls.__name__}[...] must all be type variables")
            ikiwa len(set(params)) != len(params):
                ashiria TypeError(
                    f"Parameters to {cls.__name__}[...] must all be unique")
        isipokua:
            # Subscripting a regular Generic subclass.
            _check_generic(cls, params)
        rudisha _GenericAlias(cls, params)

    eleza __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        tvars = []
        ikiwa '__orig_bases__' kwenye cls.__dict__:
            error = Generic kwenye cls.__orig_bases__
        isipokua:
            error = Generic kwenye cls.__bases__ na cls.__name__ != 'Protocol'
        ikiwa error:
            ashiria TypeError("Cannot inherit kutoka plain Generic")
        ikiwa '__orig_bases__' kwenye cls.__dict__:
            tvars = _collect_type_vars(cls.__orig_bases__)
            # Look kila Generic[T1, ..., Tn].
            # If found, tvars must be a subset of it.
            # If sio found, tvars ni it.
            # Also check kila na reject plain Generic,
            # na reject multiple Generic[...].
            gvars = Tupu
            kila base kwenye cls.__orig_bases__:
                ikiwa (isinstance(base, _GenericAlias) and
                        base.__origin__ ni Generic):
                    ikiwa gvars ni sio Tupu:
                        ashiria TypeError(
                            "Cannot inherit kutoka Generic[...] multiple types.")
                    gvars = base.__parameters__
            ikiwa gvars ni sio Tupu:
                tvarset = set(tvars)
                gvarset = set(gvars)
                ikiwa sio tvarset <= gvarset:
                    s_vars = ', '.join(str(t) kila t kwenye tvars ikiwa t haiko kwenye gvarset)
                    s_args = ', '.join(str(g) kila g kwenye gvars)
                    ashiria TypeError(f"Some type variables ({s_vars}) are"
                                    f" sio listed kwenye Generic[{s_args}]")
                tvars = gvars
        cls.__parameters__ = tuple(tvars)


kundi _TypingEmpty:
    """Internal placeholder kila () ama []. Used by TupleMeta na CallableMeta
    to allow empty list/tuple kwenye specific places, without allowing them
    to sneak kwenye where prohibited.
    """


kundi _TypingEllipsis:
    """Internal placeholder kila ... (ellipsis)."""


_TYPING_INTERNALS = ['__parameters__', '__orig_bases__',  '__orig_class__',
                     '_is_protocol', '_is_runtime_protocol']

_SPECIAL_NAMES = ['__abstractmethods__', '__annotations__', '__dict__', '__doc__',
                  '__init__', '__module__', '__new__', '__slots__',
                  '__subclasshook__', '__weakref__']

# These special attributes will be sio collected kama protocol members.
EXCLUDED_ATTRIBUTES = _TYPING_INTERNALS + _SPECIAL_NAMES + ['_MutableMapping__marker']


eleza _get_protocol_attrs(cls):
    """Collect protocol members kutoka a protocol kundi objects.

    This includes names actually defined kwenye the kundi dictionary, kama well
    kama names that appear kwenye annotations. Special names (above) are skipped.
    """
    attrs = set()
    kila base kwenye cls.__mro__[:-1]:  # without object
        ikiwa base.__name__ kwenye ('Protocol', 'Generic'):
            endelea
        annotations = getattr(base, '__annotations__', {})
        kila attr kwenye list(base.__dict__.keys()) + list(annotations.keys()):
            ikiwa sio attr.startswith('_abc_') na attr haiko kwenye EXCLUDED_ATTRIBUTES:
                attrs.add(attr)
    rudisha attrs


eleza _is_callable_members_only(cls):
    # PEP 544 prohibits using issubclass() with protocols that have non-method members.
    rudisha all(callable(getattr(cls, attr, Tupu)) kila attr kwenye _get_protocol_attrs(cls))


eleza _no_init(self, *args, **kwargs):
    ikiwa type(self)._is_protocol:
        ashiria TypeError('Protocols cannot be instantiated')


eleza _allow_reckless_class_cheks():
    """Allow instnance na kundi checks kila special stdlib modules.

    The abc na functools modules indiscriminately call isinstance() and
    issubclass() on the whole MRO of a user class, which may contain protocols.
    """
    jaribu:
        rudisha sys._getframe(3).f_globals['__name__'] kwenye ['abc', 'functools']
    tatizo (AttributeError, ValueError):  # For platforms without _getframe().
        rudisha Kweli


_PROTO_WHITELIST = {
    'collections.abc': [
        'Callable', 'Awaitable', 'Iterable', 'Iterator', 'AsyncIterable',
        'Hashable', 'Sized', 'Container', 'Collection', 'Reversible',
    ],
    'contextlib': ['AbstractContextManager', 'AbstractAsyncContextManager'],
}


kundi _ProtocolMeta(ABCMeta):
    # This metakundi ni really unfortunate na exists only because of
    # the lack of __instancehook__.
    eleza __instancecheck__(cls, instance):
        # We need this method kila situations where attributes are
        # assigned kwenye __init__.
        ikiwa ((not getattr(cls, '_is_protocol', Uongo) or
                _is_callable_members_only(cls)) and
                issubclass(instance.__class__, cls)):
            rudisha Kweli
        ikiwa cls._is_protocol:
            ikiwa all(hasattr(instance, attr) and
                    # All *methods* can be blocked by setting them to Tupu.
                    (not callable(getattr(cls, attr, Tupu)) or
                     getattr(instance, attr) ni sio Tupu)
                    kila attr kwenye _get_protocol_attrs(cls)):
                rudisha Kweli
        rudisha super().__instancecheck__(instance)


kundi Protocol(Generic, metaclass=_ProtocolMeta):
    """Base kundi kila protocol classes.

    Protocol classes are defined as::

        kundi Proto(Protocol):
            eleza meth(self) -> int:
                ...

    Such classes are primarily used with static type checkers that recognize
    structural subtyping (static duck-typing), kila example::

        kundi C:
            eleza meth(self) -> int:
                rudisha 0

        eleza func(x: Proto) -> int:
            rudisha x.meth()

        func(C())  # Passes static type check

    See PEP 544 kila details. Protocol classes decorated with
    @typing.runtime_checkable act kama simple-minded runtime protocols that check
    only the presence of given attributes, ignoring their type signatures.
    Protocol classes can be generic, they are defined as::

        kundi GenProto(Protocol[T]):
            eleza meth(self) -> T:
                ...
    """
    __slots__ = ()
    _is_protocol = Kweli
    _is_runtime_protocol = Uongo

    eleza __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)

        # Determine ikiwa this ni a protocol ama a concrete subclass.
        ikiwa sio cls.__dict__.get('_is_protocol', Uongo):
            cls._is_protocol = any(b ni Protocol kila b kwenye cls.__bases__)

        # Set (or override) the protocol subkundi hook.
        eleza _proto_hook(other):
            ikiwa sio cls.__dict__.get('_is_protocol', Uongo):
                rudisha NotImplemented

            # First, perform various sanity checks.
            ikiwa sio getattr(cls, '_is_runtime_protocol', Uongo):
                ikiwa _allow_reckless_class_cheks():
                    rudisha NotImplemented
                ashiria TypeError("Instance na kundi checks can only be used with"
                                " @runtime_checkable protocols")
            ikiwa sio _is_callable_members_only(cls):
                ikiwa _allow_reckless_class_cheks():
                    rudisha NotImplemented
                ashiria TypeError("Protocols with non-method members"
                                " don't support issubclass()")
            ikiwa sio isinstance(other, type):
                # Same error message kama kila issubclass(1, int).
                ashiria TypeError('issubclass() arg 1 must be a class')

            # Second, perform the actual structural compatibility check.
            kila attr kwenye _get_protocol_attrs(cls):
                kila base kwenye other.__mro__:
                    # Check ikiwa the members appears kwenye the kundi dictionary...
                    ikiwa attr kwenye base.__dict__:
                        ikiwa base.__dict__[attr] ni Tupu:
                            rudisha NotImplemented
                        koma

                    # ...or kwenye annotations, ikiwa it ni a sub-protocol.
                    annotations = getattr(base, '__annotations__', {})
                    ikiwa (isinstance(annotations, collections.abc.Mapping) and
                            attr kwenye annotations and
                            issubclass(other, Generic) na other._is_protocol):
                        koma
                isipokua:
                    rudisha NotImplemented
            rudisha Kweli

        ikiwa '__subclasshook__' haiko kwenye cls.__dict__:
            cls.__subclasshook__ = _proto_hook

        # We have nothing more to do kila non-protocols...
        ikiwa sio cls._is_protocol:
            rudisha

        # ... otherwise check consistency of bases, na prohibit instantiation.
        kila base kwenye cls.__bases__:
            ikiwa sio (base kwenye (object, Generic) or
                    base.__module__ kwenye _PROTO_WHITELIST and
                    base.__name__ kwenye _PROTO_WHITELIST[base.__module__] or
                    issubclass(base, Generic) na base._is_protocol):
                ashiria TypeError('Protocols can only inherit kutoka other'
                                ' protocols, got %r' % base)
        cls.__init__ = _no_init


eleza runtime_checkable(cls):
    """Mark a protocol kundi kama a runtime protocol.

    Such protocol can be used with isinstance() na issubclass().
    Raise TypeError ikiwa applied to a non-protocol class.
    This allows a simple-minded structural check very similar to
    one trick ponies kwenye collections.abc such kama Iterable.
    For example::

        @runtime_checkable
        kundi Closable(Protocol):
            eleza close(self): ...

        assert isinstance(open('/some/file'), Closable)

    Warning: this will check only the presence of the required methods,
    sio their type signatures!
    """
    ikiwa sio issubclass(cls, Generic) ama sio cls._is_protocol:
        ashiria TypeError('@runtime_checkable can be only applied to protocol classes,'
                        ' got %r' % cls)
    cls._is_runtime_protocol = Kweli
    rudisha cls


eleza cast(typ, val):
    """Cast a value to a type.

    This rudishas the value unchanged.  To the type checker this
    signals that the rudisha value has the designated type, but at
    runtime we intentionally don't check anything (we want this
    to be kama fast kama possible).
    """
    rudisha val


eleza _get_defaults(func):
    """Internal helper to extract the default arguments, by name."""
    jaribu:
        code = func.__code__
    tatizo AttributeError:
        # Some built-in functions don't have __code__, __defaults__, etc.
        rudisha {}
    pos_count = code.co_argcount
    arg_names = code.co_varnames
    arg_names = arg_names[:pos_count]
    defaults = func.__defaults__ ama ()
    kwdefaults = func.__kwdefaults__
    res = dict(kwdefaults) ikiwa kwdefaults else {}
    pos_offset = pos_count - len(defaults)
    kila name, value kwenye zip(arg_names[pos_offset:], defaults):
        assert name haiko kwenye res
        res[name] = value
    rudisha res


_allowed_types = (types.FunctionType, types.BuiltinFunctionType,
                  types.MethodType, types.ModuleType,
                  WrapperDescriptorType, MethodWrapperType, MethodDescriptorType)


eleza get_type_hints(obj, globalns=Tupu, localns=Tupu):
    """Return type hints kila an object.

    This ni often the same kama obj.__annotations__, but it handles
    forward references encoded kama string literals, na ikiwa necessary
    adds Optional[t] ikiwa a default value equal to Tupu ni set.

    The argument may be a module, class, method, ama function. The annotations
    are rudishaed kama a dictionary. For classes, annotations include also
    inherited members.

    TypeError ni ashiriad ikiwa the argument ni sio of a type that can contain
    annotations, na an empty dictionary ni rudishaed ikiwa no annotations are
    present.

    BEWARE -- the behavior of globalns na localns ni counterintuitive
    (unless you are familiar with how eval() na exec() work).  The
    search order ni locals first, then globals.

    - If no dict arguments are pitaed, an attempt ni made to use the
      globals kutoka obj (or the respective module's globals kila classes),
      na these are also used kama the locals.  If the object does sio appear
      to have globals, an empty dictionary ni used.

    - If one dict argument ni pitaed, it ni used kila both globals and
      locals.

    - If two dict arguments are pitaed, they specify globals and
      locals, respectively.
    """

    ikiwa getattr(obj, '__no_type_check__', Tupu):
        rudisha {}
    # Classes require a special treatment.
    ikiwa isinstance(obj, type):
        hints = {}
        kila base kwenye reversed(obj.__mro__):
            ikiwa globalns ni Tupu:
                base_globals = sys.modules[base.__module__].__dict__
            isipokua:
                base_globals = globalns
            ann = base.__dict__.get('__annotations__', {})
            kila name, value kwenye ann.items():
                ikiwa value ni Tupu:
                    value = type(Tupu)
                ikiwa isinstance(value, str):
                    value = ForwardRef(value, is_argument=Uongo)
                value = _eval_type(value, base_globals, localns)
                hints[name] = value
        rudisha hints

    ikiwa globalns ni Tupu:
        ikiwa isinstance(obj, types.ModuleType):
            globalns = obj.__dict__
        isipokua:
            globalns = getattr(obj, '__globals__', {})
        ikiwa localns ni Tupu:
            localns = globalns
    elikiwa localns ni Tupu:
        localns = globalns
    hints = getattr(obj, '__annotations__', Tupu)
    ikiwa hints ni Tupu:
        # Return empty annotations kila something that _could_ have them.
        ikiwa isinstance(obj, _allowed_types):
            rudisha {}
        isipokua:
            ashiria TypeError('{!r} ni sio a module, class, method, '
                            'or function.'.format(obj))
    defaults = _get_defaults(obj)
    hints = dict(hints)
    kila name, value kwenye hints.items():
        ikiwa value ni Tupu:
            value = type(Tupu)
        ikiwa isinstance(value, str):
            value = ForwardRef(value)
        value = _eval_type(value, globalns, localns)
        ikiwa name kwenye defaults na defaults[name] ni Tupu:
            value = Optional[value]
        hints[name] = value
    rudisha hints


eleza get_origin(tp):
    """Get the unsubscripted version of a type.

    This supports generic types, Callable, Tuple, Union, Literal, Final na ClassVar.
    Return Tupu kila unsupported types. Examples::

        get_origin(Literal[42]) ni Literal
        get_origin(int) ni Tupu
        get_origin(ClassVar[int]) ni ClassVar
        get_origin(Generic) ni Generic
        get_origin(Generic[T]) ni Generic
        get_origin(Union[T, int]) ni Union
        get_origin(List[Tuple[T, T]][int]) == list
    """
    ikiwa isinstance(tp, _GenericAlias):
        rudisha tp.__origin__
    ikiwa tp ni Generic:
        rudisha Generic
    rudisha Tupu


eleza get_args(tp):
    """Get type arguments with all substitutions performed.

    For unions, basic simplifications used by Union constructor are performed.
    Examples::
        get_args(Dict[str, int]) == (str, int)
        get_args(int) == ()
        get_args(Union[int, Union[T, int], str][int]) == (int, str)
        get_args(Union[int, Tuple[T, int]][str]) == (int, Tuple[str, int])
        get_args(Callable[[], T][int]) == ([], int)
    """
    ikiwa isinstance(tp, _GenericAlias):
        res = tp.__args__
        ikiwa get_origin(tp) ni collections.abc.Callable na res[0] ni sio Ellipsis:
            res = (list(res[:-1]), res[-1])
        rudisha res
    rudisha ()


eleza no_type_check(arg):
    """Decorator to indicate that annotations are sio type hints.

    The argument must be a kundi ama function; ikiwa it ni a class, it
    applies recursively to all methods na classes defined kwenye that class
    (but sio to methods defined kwenye its superclasses ama subclasses).

    This mutates the function(s) ama class(es) kwenye place.
    """
    ikiwa isinstance(arg, type):
        arg_attrs = arg.__dict__.copy()
        kila attr, val kwenye arg.__dict__.items():
            ikiwa val kwenye arg.__bases__ + (arg,):
                arg_attrs.pop(attr)
        kila obj kwenye arg_attrs.values():
            ikiwa isinstance(obj, types.FunctionType):
                obj.__no_type_check__ = Kweli
            ikiwa isinstance(obj, type):
                no_type_check(obj)
    jaribu:
        arg.__no_type_check__ = Kweli
    tatizo TypeError:  # built-in classes
        pita
    rudisha arg


eleza no_type_check_decorator(decorator):
    """Decorator to give another decorator the @no_type_check effect.

    This wraps the decorator with something that wraps the decorated
    function kwenye @no_type_check.
    """

    @functools.wraps(decorator)
    eleza wrapped_decorator(*args, **kwds):
        func = decorator(*args, **kwds)
        func = no_type_check(func)
        rudisha func

    rudisha wrapped_decorator


eleza _overload_dummy(*args, **kwds):
    """Helper kila @overload to ashiria when called."""
    ashiria NotImplementedError(
        "You should sio call an overloaded function. "
        "A series of @overload-decorated functions "
        "outside a stub module should always be followed "
        "by an implementation that ni sio @overload-ed.")


eleza overload(func):
    """Decorator kila overloaded functions/methods.

    In a stub file, place two ama more stub definitions kila the same
    function kwenye a row, each decorated with @overload.  For example:

      @overload
      eleza utf8(value: Tupu) -> Tupu: ...
      @overload
      eleza utf8(value: bytes) -> bytes: ...
      @overload
      eleza utf8(value: str) -> bytes: ...

    In a non-stub file (i.e. a regular .py file), do the same but
    follow it with an implementation.  The implementation should *not*
    be decorated with @overload.  For example:

      @overload
      eleza utf8(value: Tupu) -> Tupu: ...
      @overload
      eleza utf8(value: bytes) -> bytes: ...
      @overload
      eleza utf8(value: str) -> bytes: ...
      eleza utf8(value):
          # implementation goes here
    """
    rudisha _overload_dummy


eleza final(f):
    """A decorator to indicate final methods na final classes.

    Use this decorator to indicate to type checkers that the decorated
    method cannot be overridden, na decorated kundi cannot be subclassed.
    For example:

      kundi Base:
          @final
          eleza done(self) -> Tupu:
              ...
      kundi Sub(Base):
          eleza done(self) -> Tupu:  # Error reported by type checker
                ...

      @final
      kundi Leaf:
          ...
      kundi Other(Leaf):  # Error reported by type checker
          ...

    There ni no runtime checking of these properties.
    """
    rudisha f


# Some unconstrained type variables.  These are used by the container types.
# (These are sio kila export.)
T = TypeVar('T')  # Any type.
KT = TypeVar('KT')  # Key type.
VT = TypeVar('VT')  # Value type.
T_co = TypeVar('T_co', covariant=Kweli)  # Any type covariant containers.
V_co = TypeVar('V_co', covariant=Kweli)  # Any type covariant containers.
VT_co = TypeVar('VT_co', covariant=Kweli)  # Value type covariant containers.
T_contra = TypeVar('T_contra', contravariant=Kweli)  # Ditto contravariant.
# Internal type variable used kila Type[].
CT_co = TypeVar('CT_co', covariant=Kweli, bound=type)

# A useful type variable with constraints.  This represents string types.
# (This one *is* kila export!)
AnyStr = TypeVar('AnyStr', bytes, str)


# Various ABCs mimicking those kwenye collections.abc.
eleza _alias(origin, params, inst=Kweli):
    rudisha _GenericAlias(origin, params, special=Kweli, inst=inst)

Hashable = _alias(collections.abc.Hashable, ())  # Not generic.
Awaitable = _alias(collections.abc.Awaitable, T_co)
Coroutine = _alias(collections.abc.Coroutine, (T_co, T_contra, V_co))
AsyncIterable = _alias(collections.abc.AsyncIterable, T_co)
AsyncIterator = _alias(collections.abc.AsyncIterator, T_co)
Iterable = _alias(collections.abc.Iterable, T_co)
Iterator = _alias(collections.abc.Iterator, T_co)
Reversible = _alias(collections.abc.Reversible, T_co)
Sized = _alias(collections.abc.Sized, ())  # Not generic.
Container = _alias(collections.abc.Container, T_co)
Collection = _alias(collections.abc.Collection, T_co)
Callable = _VariadicGenericAlias(collections.abc.Callable, (), special=Kweli)
Callable.__doc__ = \
    """Callable type; Callable[[int], str] ni a function of (int) -> str.

    The subscription syntax must always be used with exactly two
    values: the argument list na the rudisha type.  The argument list
    must be a list of types ama ellipsis; the rudisha type must be a single type.

    There ni no syntax to indicate optional ama keyword arguments,
    such function types are rarely used kama callback types.
    """
AbstractSet = _alias(collections.abc.Set, T_co)
MutableSet = _alias(collections.abc.MutableSet, T)
# NOTE: Mapping ni only covariant kwenye the value type.
Mapping = _alias(collections.abc.Mapping, (KT, VT_co))
MutableMapping = _alias(collections.abc.MutableMapping, (KT, VT))
Sequence = _alias(collections.abc.Sequence, T_co)
MutableSequence = _alias(collections.abc.MutableSequence, T)
ByteString = _alias(collections.abc.ByteString, ())  # Not generic
Tuple = _VariadicGenericAlias(tuple, (), inst=Uongo, special=Kweli)
Tuple.__doc__ = \
    """Tuple type; Tuple[X, Y] ni the cross-product type of X na Y.

    Example: Tuple[T1, T2] ni a tuple of two elements corresponding
    to type variables T1 na T2.  Tuple[int, float, str] ni a tuple
    of an int, a float na a string.

    To specify a variable-length tuple of homogeneous type, use Tuple[T, ...].
    """
List = _alias(list, T, inst=Uongo)
Deque = _alias(collections.deque, T)
Set = _alias(set, T, inst=Uongo)
FrozenSet = _alias(frozenset, T_co, inst=Uongo)
MappingView = _alias(collections.abc.MappingView, T_co)
KeysView = _alias(collections.abc.KeysView, KT)
ItemsView = _alias(collections.abc.ItemsView, (KT, VT_co))
ValuesView = _alias(collections.abc.ValuesView, VT_co)
ContextManager = _alias(contextlib.AbstractContextManager, T_co)
AsyncContextManager = _alias(contextlib.AbstractAsyncContextManager, T_co)
Dict = _alias(dict, (KT, VT), inst=Uongo)
DefaultDict = _alias(collections.defaultdict, (KT, VT))
OrderedDict = _alias(collections.OrderedDict, (KT, VT))
Counter = _alias(collections.Counter, T)
ChainMap = _alias(collections.ChainMap, (KT, VT))
Generator = _alias(collections.abc.Generator, (T_co, T_contra, V_co))
AsyncGenerator = _alias(collections.abc.AsyncGenerator, (T_co, T_contra))
Type = _alias(type, CT_co, inst=Uongo)
Type.__doc__ = \
    """A special construct usable to annotate kundi objects.

    For example, suppose we have the following classes::

      kundi User: ...  # Abstract base kila User classes
      kundi BasicUser(User): ...
      kundi ProUser(User): ...
      kundi TeamUser(User): ...

    And a function that takes a kundi argument that's a subkundi of
    User na rudishas an instance of the corresponding class::

      U = TypeVar('U', bound=User)
      eleza new_user(user_class: Type[U]) -> U:
          user = user_class()
          # (Here we could write the user object to a database)
          rudisha user

      joe = new_user(BasicUser)

    At this point the type checker knows that joe has type BasicUser.
    """


@runtime_checkable
kundi SupportsInt(Protocol):
    """An ABC with one abstract method __int__."""
    __slots__ = ()

    @abstractmethod
    eleza __int__(self) -> int:
        pita


@runtime_checkable
kundi SupportsFloat(Protocol):
    """An ABC with one abstract method __float__."""
    __slots__ = ()

    @abstractmethod
    eleza __float__(self) -> float:
        pita


@runtime_checkable
kundi SupportsComplex(Protocol):
    """An ABC with one abstract method __complex__."""
    __slots__ = ()

    @abstractmethod
    eleza __complex__(self) -> complex:
        pita


@runtime_checkable
kundi SupportsBytes(Protocol):
    """An ABC with one abstract method __bytes__."""
    __slots__ = ()

    @abstractmethod
    eleza __bytes__(self) -> bytes:
        pita


@runtime_checkable
kundi SupportsIndex(Protocol):
    """An ABC with one abstract method __index__."""
    __slots__ = ()

    @abstractmethod
    eleza __index__(self) -> int:
        pita


@runtime_checkable
kundi SupportsAbs(Protocol[T_co]):
    """An ABC with one abstract method __abs__ that ni covariant kwenye its rudisha type."""
    __slots__ = ()

    @abstractmethod
    eleza __abs__(self) -> T_co:
        pita


@runtime_checkable
kundi SupportsRound(Protocol[T_co]):
    """An ABC with one abstract method __round__ that ni covariant kwenye its rudisha type."""
    __slots__ = ()

    @abstractmethod
    eleza __round__(self, ndigits: int = 0) -> T_co:
        pita


eleza _make_nmtuple(name, types):
    msg = "NamedTuple('Name', [(f0, t0), (f1, t1), ...]); each t must be a type"
    types = [(n, _type_check(t, msg)) kila n, t kwenye types]
    nm_tpl = collections.namedtuple(name, [n kila n, t kwenye types])
    # Prior to PEP 526, only _field_types attribute was assigned.
    # Now __annotations__ are used na _field_types ni deprecated (remove kwenye 3.9)
    nm_tpl.__annotations__ = nm_tpl._field_types = dict(types)
    jaribu:
        nm_tpl.__module__ = sys._getframe(2).f_globals.get('__name__', '__main__')
    tatizo (AttributeError, ValueError):
        pita
    rudisha nm_tpl


# attributes prohibited to set kwenye NamedTuple kundi syntax
_prohibited = ('__new__', '__init__', '__slots__', '__getnewargs__',
               '_fields', '_field_defaults', '_field_types',
               '_make', '_replace', '_asdict', '_source')

_special = ('__module__', '__name__', '__annotations__')


kundi NamedTupleMeta(type):

    eleza __new__(cls, typename, bases, ns):
        ikiwa ns.get('_root', Uongo):
            rudisha super().__new__(cls, typename, bases, ns)
        types = ns.get('__annotations__', {})
        nm_tpl = _make_nmtuple(typename, types.items())
        defaults = []
        defaults_dict = {}
        kila field_name kwenye types:
            ikiwa field_name kwenye ns:
                default_value = ns[field_name]
                defaults.append(default_value)
                defaults_dict[field_name] = default_value
            elikiwa defaults:
                ashiria TypeError("Non-default namedtuple field {field_name} cannot "
                                "follow default field(s) {default_names}"
                                .format(field_name=field_name,
                                        default_names=', '.join(defaults_dict.keys())))
        nm_tpl.__new__.__annotations__ = dict(types)
        nm_tpl.__new__.__defaults__ = tuple(defaults)
        nm_tpl._field_defaults = defaults_dict
        # update kutoka user namespace without overriding special namedtuple attributes
        kila key kwenye ns:
            ikiwa key kwenye _prohibited:
                ashiria AttributeError("Cannot overwrite NamedTuple attribute " + key)
            elikiwa key haiko kwenye _special na key haiko kwenye nm_tpl._fields:
                setattr(nm_tpl, key, ns[key])
        rudisha nm_tpl


kundi NamedTuple(metaclass=NamedTupleMeta):
    """Typed version of namedtuple.

    Usage kwenye Python versions >= 3.6::

        kundi Employee(NamedTuple):
            name: str
            id: int

    This ni equivalent to::

        Employee = collections.namedtuple('Employee', ['name', 'id'])

    The resulting kundi has an extra __annotations__ attribute, giving a
    dict that maps field names to types.  (The field names are also in
    the _fields attribute, which ni part of the namedtuple API.)
    Alternative equivalent keyword syntax ni also accepted::

        Employee = NamedTuple('Employee', name=str, id=int)

    In Python versions <= 3.5 use::

        Employee = NamedTuple('Employee', [('name', str), ('id', int)])
    """
    _root = Kweli

    eleza __new__(*args, **kwargs):
        ikiwa sio args:
            ashiria TypeError('NamedTuple.__new__(): sio enough arguments')
        cls, *args = args  # allow the "cls" keyword be pitaed
        ikiwa args:
            typename, *args = args # allow the "typename" keyword be pitaed
        elikiwa 'typename' kwenye kwargs:
            typename = kwargs.pop('typename')
            agiza warnings
            warnings.warn("Passing 'typename' kama keyword argument ni deprecated",
                          DeprecationWarning, stacklevel=2)
        isipokua:
            ashiria TypeError("NamedTuple.__new__() missing 1 required positional "
                            "argument: 'typename'")
        ikiwa args:
            jaribu:
                fields, = args # allow the "fields" keyword be pitaed
            tatizo ValueError:
                ashiria TypeError(f'NamedTuple.__new__() takes kutoka 2 to 3 '
                                f'positional arguments but {len(args) + 2} '
                                f'were given') kutoka Tupu
        elikiwa 'fields' kwenye kwargs na len(kwargs) == 1:
            fields = kwargs.pop('fields')
            agiza warnings
            warnings.warn("Passing 'fields' kama keyword argument ni deprecated",
                          DeprecationWarning, stacklevel=2)
        isipokua:
            fields = Tupu

        ikiwa fields ni Tupu:
            fields = kwargs.items()
        elikiwa kwargs:
            ashiria TypeError("Either list of fields ama keywords"
                            " can be provided to NamedTuple, sio both")
        rudisha _make_nmtuple(typename, fields)
    __new__.__text_signature__ = '($cls, typename, fields=Tupu, /, **kwargs)'


eleza _dict_new(cls, /, *args, **kwargs):
    rudisha dict(*args, **kwargs)


eleza _typeddict_new(cls, typename, fields=Tupu, /, *, total=Kweli, **kwargs):
    ikiwa fields ni Tupu:
        fields = kwargs
    elikiwa kwargs:
        ashiria TypeError("TypedDict takes either a dict ama keyword arguments,"
                        " but sio both")

    ns = {'__annotations__': dict(fields), '__total__': total}
    jaribu:
        # Setting correct module ni necessary to make typed dict classes pickleable.
        ns['__module__'] = sys._getframe(1).f_globals.get('__name__', '__main__')
    tatizo (AttributeError, ValueError):
        pita

    rudisha _TypedDictMeta(typename, (), ns)


eleza _check_fails(cls, other):
    # Typed dicts are only kila static structural subtyping.
    ashiria TypeError('TypedDict does sio support instance na kundi checks')


kundi _TypedDictMeta(type):
    eleza __new__(cls, name, bases, ns, total=Kweli):
        """Create new typed dict kundi object.

        This method ni called directly when TypedDict ni subclassed,
        ama via _typeddict_new when TypedDict ni instantiated. This way
        TypedDict supports all three syntax forms described kwenye its docstring.
        Subclasses na instances of TypedDict rudisha actual dictionaries
        via _dict_new.
        """
        ns['__new__'] = _typeddict_new ikiwa name == 'TypedDict' else _dict_new
        tp_dict = super(_TypedDictMeta, cls).__new__(cls, name, (dict,), ns)

        anns = ns.get('__annotations__', {})
        msg = "TypedDict('Name', {f0: t0, f1: t1, ...}); each t must be a type"
        anns = {n: _type_check(tp, msg) kila n, tp kwenye anns.items()}
        kila base kwenye bases:
            anns.update(base.__dict__.get('__annotations__', {}))
        tp_dict.__annotations__ = anns
        ikiwa sio hasattr(tp_dict, '__total__'):
            tp_dict.__total__ = total
        rudisha tp_dict

    __instancecheck__ = __subclasscheck__ = _check_fails


kundi TypedDict(dict, metaclass=_TypedDictMeta):
    """A simple typed namespace. At runtime it ni equivalent to a plain dict.

    TypedDict creates a dictionary type that expects all of its
    instances to have a certain set of keys, where each key is
    associated with a value of a consistent type. This expectation
    ni sio checked at runtime but ni only enforced by type checkers.
    Usage::

        kundi Point2D(TypedDict):
            x: int
            y: int
            label: str

        a: Point2D = {'x': 1, 'y': 2, 'label': 'good'}  # OK
        b: Point2D = {'z': 3, 'label': 'bad'}           # Fails type check

        assert Point2D(x=1, y=2, label='first') == dict(x=1, y=2, label='first')

    The type info can be accessed via Point2D.__annotations__. TypedDict
    supports two additional equivalent forms::

        Point2D = TypedDict('Point2D', x=int, y=int, label=str)
        Point2D = TypedDict('Point2D', {'x': int, 'y': int, 'label': str})

    The kundi syntax ni only supported kwenye Python 3.6+, wakati two other
    syntax forms work kila Python 2.7 na 3.2+
    """


eleza NewType(name, tp):
    """NewType creates simple unique types with almost zero
    runtime overhead. NewType(name, tp) ni considered a subtype of tp
    by static type checkers. At runtime, NewType(name, tp) rudishas
    a dummy function that simply rudishas its argument. Usage::

        UserId = NewType('UserId', int)

        eleza name_by_id(user_id: UserId) -> str:
            ...

        UserId('user')          # Fails type check

        name_by_id(42)          # Fails type check
        name_by_id(UserId(42))  # OK

        num = UserId(5) + 1     # type: int
    """

    eleza new_type(x):
        rudisha x

    new_type.__name__ = name
    new_type.__supertype__ = tp
    rudisha new_type


# Python-version-specific alias (Python 2: unicode; Python 3: str)
Text = str


# Constant that's Kweli when type checking, but Uongo here.
TYPE_CHECKING = Uongo


kundi IO(Generic[AnyStr]):
    """Generic base kundi kila TextIO na BinaryIO.

    This ni an abstract, generic version of the rudisha of open().

    NOTE: This does sio distinguish between the different possible
    classes (text vs. binary, read vs. write vs. read/write,
    append-only, unbuffered).  The TextIO na BinaryIO subclasses
    below capture the distinctions between text vs. binary, which is
    pervasive kwenye the interface; however we currently do sio offer a
    way to track the other distinctions kwenye the type system.
    """

    __slots__ = ()

    @property
    @abstractmethod
    eleza mode(self) -> str:
        pita

    @property
    @abstractmethod
    eleza name(self) -> str:
        pita

    @abstractmethod
    eleza close(self) -> Tupu:
        pita

    @abstractmethod
    eleza closed(self) -> bool:
        pita

    @abstractmethod
    eleza fileno(self) -> int:
        pita

    @abstractmethod
    eleza flush(self) -> Tupu:
        pita

    @abstractmethod
    eleza isatty(self) -> bool:
        pita

    @abstractmethod
    eleza read(self, n: int = -1) -> AnyStr:
        pita

    @abstractmethod
    eleza readable(self) -> bool:
        pita

    @abstractmethod
    eleza readline(self, limit: int = -1) -> AnyStr:
        pita

    @abstractmethod
    eleza readlines(self, hint: int = -1) -> List[AnyStr]:
        pita

    @abstractmethod
    eleza seek(self, offset: int, whence: int = 0) -> int:
        pita

    @abstractmethod
    eleza seekable(self) -> bool:
        pita

    @abstractmethod
    eleza tell(self) -> int:
        pita

    @abstractmethod
    eleza truncate(self, size: int = Tupu) -> int:
        pita

    @abstractmethod
    eleza writable(self) -> bool:
        pita

    @abstractmethod
    eleza write(self, s: AnyStr) -> int:
        pita

    @abstractmethod
    eleza writelines(self, lines: List[AnyStr]) -> Tupu:
        pita

    @abstractmethod
    eleza __enter__(self) -> 'IO[AnyStr]':
        pita

    @abstractmethod
    eleza __exit__(self, type, value, traceback) -> Tupu:
        pita


kundi BinaryIO(IO[bytes]):
    """Typed version of the rudisha of open() kwenye binary mode."""

    __slots__ = ()

    @abstractmethod
    eleza write(self, s: Union[bytes, bytearray]) -> int:
        pita

    @abstractmethod
    eleza __enter__(self) -> 'BinaryIO':
        pita


kundi TextIO(IO[str]):
    """Typed version of the rudisha of open() kwenye text mode."""

    __slots__ = ()

    @property
    @abstractmethod
    eleza buffer(self) -> BinaryIO:
        pita

    @property
    @abstractmethod
    eleza encoding(self) -> str:
        pita

    @property
    @abstractmethod
    eleza errors(self) -> Optional[str]:
        pita

    @property
    @abstractmethod
    eleza line_buffering(self) -> bool:
        pita

    @property
    @abstractmethod
    eleza newlines(self) -> Any:
        pita

    @abstractmethod
    eleza __enter__(self) -> 'TextIO':
        pita


kundi io:
    """Wrapper namespace kila IO generic classes."""

    __all__ = ['IO', 'TextIO', 'BinaryIO']
    IO = IO
    TextIO = TextIO
    BinaryIO = BinaryIO


io.__name__ = __name__ + '.io'
sys.modules[io.__name__] = io

Pattern = _alias(stdlib_re.Pattern, AnyStr)
Match = _alias(stdlib_re.Match, AnyStr)

kundi re:
    """Wrapper namespace kila re type aliases."""

    __all__ = ['Pattern', 'Match']
    Pattern = Pattern
    Match = Match


re.__name__ = __name__ + '.re'
sys.modules[re.__name__] = re
