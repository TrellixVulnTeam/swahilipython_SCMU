"""
The typing module: Support for gradual typing as defined by PEP 484.

At large scale, the structure of the module is following:
* Imports and exports, all public names should be explicitly added to __all__.
* Internal helper functions: these should never be used in code outside this module.
* _SpecialForm and its instances (special forms): Any, NoReturn, ClassVar, Union, Optional
* Two classes whose instances can be type arguments in addition to types: ForwardRef and TypeVar
* The core of internal generics API: _GenericAlias and _VariadicGenericAlias, the latter is
  currently only used by Tuple and Callable. All subscripted types like X[int], Union[int, str],
  etc., are instances of either of these classes.
* The public counterpart of the generics API consists of two classes: Generic and Protocol.
* Public helper functions: get_type_hints, overload, cast, no_type_check,
  no_type_check_decorator.
* Generic aliases for collections.abc ABCs and few additional protocols.
* Special types: NewType, NamedTuple, TypedDict (may be added soon).
* Wrapper submodules for re and io related types.
"""

kutoka abc agiza abstractmethod, ABCMeta
agiza collections
agiza collections.abc
agiza contextlib
agiza functools
agiza operator
agiza re as stdlib_re  # Avoid confusion with the re we export.
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

# The pseudo-submodules 're' and 'io' are part of the public
# namespace, but excluded kutoka __all__ because they might stomp on
# legitimate agizas of those modules.


eleza _type_check(arg, msg, is_argument=True):
    """Check that the argument is a type, and rudisha it (internal helper).

    As a special case, accept None and rudisha type(None) instead. Also wrap strings
    into ForwardRef instances. Consider several corner cases, for example plain
    special forms like Union are not valid, while Union[int, str] is OK, etc.
    The msg argument is a human-readable error message, e.g::

        "Union[arg, ...]: arg should be a type."

    We append the repr() of the actual value (truncated to 100 chars).
    """
    invalid_generic_forms = (Generic, Protocol)
    ikiwa is_argument:
        invalid_generic_forms = invalid_generic_forms + (ClassVar, Final)

    ikiwa arg is None:
        rudisha type(None)
    ikiwa isinstance(arg, str):
        rudisha ForwardRef(arg)
    ikiwa (isinstance(arg, _GenericAlias) and
            arg.__origin__ in invalid_generic_forms):
        raise TypeError(f"{arg} is not valid as type argument")
    ikiwa (isinstance(arg, _SpecialForm) and arg not in (Any, NoReturn) or
            arg in (Generic, Protocol)):
        raise TypeError(f"Plain {arg} is not valid as type argument")
    ikiwa isinstance(arg, (type, TypeVar, ForwardRef)):
        rudisha arg
    ikiwa not callable(arg):
        raise TypeError(f"{msg} Got {arg!r:.100}.")
    rudisha arg


eleza _type_repr(obj):
    """Return the repr() of an object, special-casing types (internal helper).

    If obj is a type, we rudisha a shorter version than the default
    type.__repr__, based on the module and qualified name, which is
    typically enough to uniquely identify a type.  For everything
    else, we fall back on repr(obj).
    """
    ikiwa isinstance(obj, type):
        ikiwa obj.__module__ == 'builtins':
            rudisha obj.__qualname__
        rudisha f'{obj.__module__}.{obj.__qualname__}'
    ikiwa obj is ...:
        return('...')
    ikiwa isinstance(obj, types.FunctionType):
        rudisha obj.__name__
    rudisha repr(obj)


eleza _collect_type_vars(types):
    """Collect all type variable contained in types in order of
    first appearance (lexicographic order). For example::

        _collect_type_vars((T, List[S, T])) == (T, S)
    """
    tvars = []
    for t in types:
        ikiwa isinstance(t, TypeVar) and t not in tvars:
            tvars.append(t)
        ikiwa isinstance(t, _GenericAlias) and not t._special:
            tvars.extend([t for t in t.__parameters__ ikiwa t not in tvars])
    rudisha tuple(tvars)


eleza _subs_tvars(tp, tvars, subs):
    """Substitute type variables 'tvars' with substitutions 'subs'.
    These two must have the same length.
    """
    ikiwa not isinstance(tp, _GenericAlias):
        rudisha tp
    new_args = list(tp.__args__)
    for a, arg in enumerate(tp.__args__):
        ikiwa isinstance(arg, TypeVar):
            for i, tvar in enumerate(tvars):
                ikiwa arg == tvar:
                    new_args[a] = subs[i]
        else:
            new_args[a] = _subs_tvars(arg, tvars, subs)
    ikiwa tp.__origin__ is Union:
        rudisha Union[tuple(new_args)]
    rudisha tp.copy_with(tuple(new_args))


eleza _check_generic(cls, parameters):
    """Check correct count for parameters of a generic cls (internal helper).
    This gives a nice error message in case of count mismatch.
    """
    ikiwa not cls.__parameters__:
        raise TypeError(f"{cls} is not a generic class")
    alen = len(parameters)
    elen = len(cls.__parameters__)
    ikiwa alen != elen:
        raise TypeError(f"Too {'many' ikiwa alen > elen else 'few'} parameters for {cls};"
                        f" actual {alen}, expected {elen}")


eleza _remove_dups_flatten(parameters):
    """An internal helper for Union creation and substitution: flatten Unions
    among parameters, then remove duplicates.
    """
    # Flatten out Union[Union[...], ...].
    params = []
    for p in parameters:
        ikiwa isinstance(p, _GenericAlias) and p.__origin__ is Union:
            params.extend(p.__args__)
        elikiwa isinstance(p, tuple) and len(p) > 0 and p[0] is Union:
            params.extend(p[1:])
        else:
            params.append(p)
    # Weed out strict duplicates, preserving the first of each occurrence.
    all_params = set(params)
    ikiwa len(all_params) < len(params):
        new_params = []
        for t in params:
            ikiwa t in all_params:
                new_params.append(t)
                all_params.remove(t)
        params = new_params
        assert not all_params, all_params
    rudisha tuple(params)


_cleanups = []


eleza _tp_cache(func):
    """Internal wrapper caching __getitem__ of generic types with a fallback to
    original function for non-hashable arguments.
    """
    cached = functools.lru_cache()(func)
    _cleanups.append(cached.cache_clear)

    @functools.wraps(func)
    eleza inner(*args, **kwds):
        try:
            rudisha cached(*args, **kwds)
        except TypeError:
            pass  # All real errors (not unhashable args) are raised below.
        rudisha func(*args, **kwds)
    rudisha inner


eleza _eval_type(t, globalns, localns):
    """Evaluate all forward reverences in the given type t.
    For use of globalns and localns see the docstring for get_type_hints().
    """
    ikiwa isinstance(t, ForwardRef):
        rudisha t._evaluate(globalns, localns)
    ikiwa isinstance(t, _GenericAlias):
        ev_args = tuple(_eval_type(a, globalns, localns) for a in t.__args__)
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
        ikiwa '_root' not in kwds:
            raise TypeError("Cannot subkundi special typing classes")

kundi _Immutable:
    """Mixin to indicate that object should not be copied."""

    eleza __copy__(self):
        rudisha self

    eleza __deepcopy__(self, memo):
        rudisha self


kundi _SpecialForm(_Final, _Immutable, _root=True):
    """Internal indicator of special typing constructs.
    See _doc instance attribute for specific docs.
    """

    __slots__ = ('_name', '_doc')

    eleza __new__(cls, *args, **kwds):
        """Constructor.

        This only exists to give a better error message in case
        someone tries to subkundi a special typing object (not a good idea).
        """
        ikiwa (len(args) == 3 and
                isinstance(args[0], str) and
                isinstance(args[1], tuple)):
            # Close enough.
            raise TypeError(f"Cannot subkundi {cls!r}")
        rudisha super().__new__(cls)

    eleza __init__(self, name, doc):
        self._name = name
        self._doc = doc

    eleza __eq__(self, other):
        ikiwa not isinstance(other, _SpecialForm):
            rudisha NotImplemented
        rudisha self._name == other._name

    eleza __hash__(self):
        rudisha hash((self._name,))

    eleza __repr__(self):
        rudisha 'typing.' + self._name

    eleza __reduce__(self):
        rudisha self._name

    eleza __call__(self, *args, **kwds):
        raise TypeError(f"Cannot instantiate {self!r}")

    eleza __instancecheck__(self, obj):
        raise TypeError(f"{self} cannot be used with isinstance()")

    eleza __subclasscheck__(self, cls):
        raise TypeError(f"{self} cannot be used with issubclass()")

    @_tp_cache
    eleza __getitem__(self, parameters):
        ikiwa self._name in ('ClassVar', 'Final'):
            item = _type_check(parameters, f'{self._name} accepts only single type.')
            rudisha _GenericAlias(self, (item,))
        ikiwa self._name == 'Union':
            ikiwa parameters == ():
                raise TypeError("Cannot take a Union of no types.")
            ikiwa not isinstance(parameters, tuple):
                parameters = (parameters,)
            msg = "Union[arg, ...]: each arg must be a type."
            parameters = tuple(_type_check(p, msg) for p in parameters)
            parameters = _remove_dups_flatten(parameters)
            ikiwa len(parameters) == 1:
                rudisha parameters[0]
            rudisha _GenericAlias(self, parameters)
        ikiwa self._name == 'Optional':
            arg = _type_check(parameters, "Optional[t] requires a single type.")
            rudisha Union[arg, type(None)]
        ikiwa self._name == 'Literal':
            # There is no '_type_check' call because arguments to Literal[...] are
            # values, not types.
            rudisha _GenericAlias(self, parameters)
        raise TypeError(f"{self} is not subscriptable")


Any = _SpecialForm('Any', doc=
    """Special type indicating an unconstrained type.

    - Any is compatible with every type.
    - Any assumed to have all methods.
    - All values assumed to be instances of Any.

    Note that all the above statements are true kutoka the point of view of
    static type checkers. At runtime, Any should not be used with instance
    or kundi checks.
    """)

NoReturn = _SpecialForm('NoReturn', doc=
    """Special type indicating functions that never return.
    Example::

      kutoka typing agiza NoReturn

      eleza stop() -> NoReturn:
          raise Exception('no way')

    This type is invalid in other positions, e.g., ``List[NoReturn]``
    will fail in static type checkers.
    """)

ClassVar = _SpecialForm('ClassVar', doc=
    """Special type construct to mark kundi variables.

    An annotation wrapped in ClassVar indicates that a given
    attribute is intended to be used as a kundi variable and
    should not be set on instances of that class. Usage::

      kundi Starship:
          stats: ClassVar[Dict[str, int]] = {} # kundi variable
          damage: int = 10                     # instance variable

    ClassVar accepts only types and cannot be further subscribed.

    Note that ClassVar is not a kundi itself, and should not
    be used with isinstance() or issubclass().
    """)

Final = _SpecialForm('Final', doc=
    """Special typing construct to indicate final names to type checkers.

    A final name cannot be re-assigned or overridden in a subclass.
    For example:

      MAX_SIZE: Final = 9000
      MAX_SIZE += 1  # Error reported by type checker

      kundi Connection:
          TIMEOUT: Final[int] = 10

      kundi FastConnector(Connection):
          TIMEOUT = 1  # Error reported by type checker

    There is no runtime checking of these properties.
    """)

Union = _SpecialForm('Union', doc=
    """Union type; Union[X, Y] means either X or Y.

    To define a union, use e.g. Union[int, str].  Details:
    - The arguments must be types and there must be at least one.
    - None as an argument is a special case and is replaced by
      type(None).
    - Unions of unions are flattened, e.g.::

        Union[Union[int, str], float] == Union[int, str, float]

    - Unions of a single argument vanish, e.g.::

        Union[int] == int  # The constructor actually returns int

    - Redundant arguments are skipped, e.g.::

        Union[int, str, int] == Union[int, str]

    - When comparing unions, the argument order is ignored, e.g.::

        Union[int, str] == Union[str, int]

    - You cannot subkundi or instantiate a union.
    - You can use Optional[X] as a shorthand for Union[X, None].
    """)

Optional = _SpecialForm('Optional', doc=
    """Optional type.

    Optional[X] is equivalent to Union[X, None].
    """)

Literal = _SpecialForm('Literal', doc=
    """Special typing form to define literal types (a.k.a. value types).

    This form can be used to indicate to type checkers that the corresponding
    variable or function parameter has a value equivalent to the provided
    literal (or one of several literals):

      eleza validate_simple(data: Any) -> Literal[True]:  # always returns True
          ...

      MODE = Literal['r', 'rb', 'w', 'wb']
      eleza open_helper(file: str, mode: MODE) -> str:
          ...

      open_helper('/some/path', 'r')  # Passes type check
      open_helper('/other/path', 'typo')  # Error in type checker

   Literal[...] cannot be subclassed. At runtime, an arbitrary value
   is allowed as type argument to Literal[...], but type checkers may
   impose restrictions.
    """)


kundi ForwardRef(_Final, _root=True):
    """Internal wrapper to hold a forward reference."""

    __slots__ = ('__forward_arg__', '__forward_code__',
                 '__forward_evaluated__', '__forward_value__',
                 '__forward_is_argument__')

    eleza __init__(self, arg, is_argument=True):
        ikiwa not isinstance(arg, str):
            raise TypeError(f"Forward reference must be a string -- got {arg!r}")
        try:
            code = compile(arg, '<string>', 'eval')
        except SyntaxError:
            raise SyntaxError(f"Forward reference must be an expression -- got {arg!r}")
        self.__forward_arg__ = arg
        self.__forward_code__ = code
        self.__forward_evaluated__ = False
        self.__forward_value__ = None
        self.__forward_is_argument__ = is_argument

    eleza _evaluate(self, globalns, localns):
        ikiwa not self.__forward_evaluated__ or localns is not globalns:
            ikiwa globalns is None and localns is None:
                globalns = localns = {}
            elikiwa globalns is None:
                globalns = localns
            elikiwa localns is None:
                localns = globalns
            self.__forward_value__ = _type_check(
                eval(self.__forward_code__, globalns, localns),
                "Forward references must evaluate to types.",
                is_argument=self.__forward_is_argument__)
            self.__forward_evaluated__ = True
        rudisha self.__forward_value__

    eleza __eq__(self, other):
        ikiwa not isinstance(other, ForwardRef):
            rudisha NotImplemented
        ikiwa self.__forward_evaluated__ and other.__forward_evaluated__:
            rudisha (self.__forward_arg__ == other.__forward_arg__ and
                    self.__forward_value__ == other.__forward_value__)
        rudisha self.__forward_arg__ == other.__forward_arg__

    eleza __hash__(self):
        rudisha hash(self.__forward_arg__)

    eleza __repr__(self):
        rudisha f'ForwardRef({self.__forward_arg__!r})'


kundi TypeVar(_Final, _Immutable, _root=True):
    """Type variable.

    Usage::

      T = TypeVar('T')  # Can be anything
      A = TypeVar('A', str, bytes)  # Must be str or bytes

    Type variables exist primarily for the benefit of static type
    checkers.  They serve as the parameters for generic types as well
    as for generic function definitions.  See kundi Generic for more
    information on generic types.  Generic functions work as follows:

      eleza repeat(x: T, n: int) -> List[T]:
          '''Return a list containing n references to x.'''
          rudisha [x]*n

      eleza longest(x: A, y: A) -> A:
          '''Return the longest of two strings.'''
          rudisha x ikiwa len(x) >= len(y) else y

    The latter example's signature is essentially the overloading
    of (str, str) -> str and (bytes, bytes) -> bytes.  Also note
    that ikiwa the arguments are instances of some subkundi of str,
    the rudisha type is still plain str.

    At runtime, isinstance(x, T) and issubclass(C, T) will raise TypeError.

    Type variables defined with covariant=True or contravariant=True
    can be used to declare covariant or contravariant generic types.
    See PEP 484 for more details. By default generic types are invariant
    in all type variables.

    Type variables can be introspected. e.g.:

      T.__name__ == 'T'
      T.__constraints__ == ()
      T.__covariant__ == False
      T.__contravariant__ = False
      A.__constraints__ == (str, bytes)

    Note that only type variables defined in global scope can be pickled.
    """

    __slots__ = ('__name__', '__bound__', '__constraints__',
                 '__covariant__', '__contravariant__')

    eleza __init__(self, name, *constraints, bound=None,
                 covariant=False, contravariant=False):
        self.__name__ = name
        ikiwa covariant and contravariant:
            raise ValueError("Bivariant types are not supported.")
        self.__covariant__ = bool(covariant)
        self.__contravariant__ = bool(contravariant)
        ikiwa constraints and bound is not None:
            raise TypeError("Constraints cannot be combined with bound=...")
        ikiwa constraints and len(constraints) == 1:
            raise TypeError("A single constraint is not allowed")
        msg = "TypeVar(name, constraint, ...): constraints must be types."
        self.__constraints__ = tuple(_type_check(t, msg) for t in constraints)
        ikiwa bound:
            self.__bound__ = _type_check(bound, "Bound must be a type.")
        else:
            self.__bound__ = None
        def_mod = sys._getframe(1).f_globals['__name__']  # for pickling
        ikiwa def_mod != 'typing':
            self.__module__ = def_mod

    eleza __repr__(self):
        ikiwa self.__covariant__:
            prefix = '+'
        elikiwa self.__contravariant__:
            prefix = '-'
        else:
            prefix = '~'
        rudisha prefix + self.__name__

    eleza __reduce__(self):
        rudisha self.__name__


# Special typing constructs Union, Optional, Generic, Callable and Tuple
# use three special attributes for internal bookkeeping of generic types:
# * __parameters__ is a tuple of unique free type parameters of a generic
#   type, for example, Dict[T, T].__parameters__ == (T,);
# * __origin__ keeps a reference to a type that was subscripted,
#   e.g., Union[T, int].__origin__ == Union, or the non-generic version of
#   the type.
# * __args__ is a tuple of all arguments used in subscripting,
#   e.g., Dict[T, int].__args__ == (T, int).


# Mapping kutoka non-generic type names that have a generic alias in typing
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
    rudisha attr.startswith('__') and attr.endswith('__')


kundi _GenericAlias(_Final, _root=True):
    """The central part of internal API.

    This represents a generic version of type 'origin' with type arguments 'params'.
    There are two kind of these aliases: user defined and special. The special ones
    are wrappers around builtin collections and ABCs in collections.abc. These must
    have 'name' always set. If 'inst' is False, then the alias can't be instantiated,
    this is used by e.g. typing.List and typing.Dict.
    """
    eleza __init__(self, origin, params, *, inst=True, special=False, name=None):
        self._inst = inst
        self._special = special
        ikiwa special and name is None:
            orig_name = origin.__name__
            name = _normalize_alias.get(orig_name, orig_name)
        self._name = name
        ikiwa not isinstance(params, tuple):
            params = (params,)
        self.__origin__ = origin
        self.__args__ = tuple(... ikiwa a is _TypingEllipsis else
                              () ikiwa a is _TypingEmpty else
                              a for a in params)
        self.__parameters__ = _collect_type_vars(params)
        self.__slots__ = None  # This is not documented.
        ikiwa not name:
            self.__module__ = origin.__module__

    @_tp_cache
    eleza __getitem__(self, params):
        ikiwa self.__origin__ in (Generic, Protocol):
            # Can't subscript Generic[...] or Protocol[...].
            raise TypeError(f"Cannot subscript already-subscripted {self}")
        ikiwa not isinstance(params, tuple):
            params = (params,)
        msg = "Parameters to generic types must be types."
        params = tuple(_type_check(p, msg) for p in params)
        _check_generic(self, params)
        rudisha _subs_tvars(self, self.__parameters__, params)

    eleza copy_with(self, params):
        # We don't copy self._special.
        rudisha _GenericAlias(self.__origin__, params, name=self._name, inst=self._inst)

    eleza __repr__(self):
        ikiwa (self._name != 'Callable' or
                len(self.__args__) == 2 and self.__args__[0] is Ellipsis):
            ikiwa self._name:
                name = 'typing.' + self._name
            else:
                name = _type_repr(self.__origin__)
            ikiwa not self._special:
                args = f'[{", ".join([_type_repr(a) for a in self.__args__])}]'
            else:
                args = ''
            rudisha (f'{name}{args}')
        ikiwa self._special:
            rudisha 'typing.Callable'
        rudisha (f'typing.Callable'
                f'[[{", ".join([_type_repr(a) for a in self.__args__[:-1]])}], '
                f'{_type_repr(self.__args__[-1])}]')

    eleza __eq__(self, other):
        ikiwa not isinstance(other, _GenericAlias):
            rudisha NotImplemented
        ikiwa self.__origin__ != other.__origin__:
            rudisha False
        ikiwa self.__origin__ is Union and other.__origin__ is Union:
            rudisha frozenset(self.__args__) == frozenset(other.__args__)
        rudisha self.__args__ == other.__args__

    eleza __hash__(self):
        ikiwa self.__origin__ is Union:
            rudisha hash((Union, frozenset(self.__args__)))
        rudisha hash((self.__origin__, self.__args__))

    eleza __call__(self, *args, **kwargs):
        ikiwa not self._inst:
            raise TypeError(f"Type {self._name} cannot be instantiated; "
                            f"use {self._name.lower()}() instead")
        result = self.__origin__(*args, **kwargs)
        try:
            result.__orig_class__ = self
        except AttributeError:
            pass
        rudisha result

    eleza __mro_entries__(self, bases):
        ikiwa self._name:  # generic version of an ABC or built-in class
            res = []
            ikiwa self.__origin__ not in bases:
                res.append(self.__origin__)
            i = bases.index(self)
            ikiwa not any(isinstance(b, _GenericAlias) or issubclass(b, Generic)
                       for b in bases[i+1:]):
                res.append(Generic)
            rudisha tuple(res)
        ikiwa self.__origin__ is Generic:
            ikiwa Protocol in bases:
                rudisha ()
            i = bases.index(self)
            for b in bases[i+1:]:
                ikiwa isinstance(b, _GenericAlias) and b is not self:
                    rudisha ()
        rudisha (self.__origin__,)

    eleza __getattr__(self, attr):
        # We are careful for copy and pickle.
        # Also for simplicity we just don't relay all dunder names
        ikiwa '__origin__' in self.__dict__ and not _is_dunder(attr):
            rudisha getattr(self.__origin__, attr)
        raise AttributeError(attr)

    eleza __setattr__(self, attr, val):
        ikiwa _is_dunder(attr) or attr in ('_name', '_inst', '_special'):
            super().__setattr__(attr, val)
        else:
            setattr(self.__origin__, attr, val)

    eleza __instancecheck__(self, obj):
        rudisha self.__subclasscheck__(type(obj))

    eleza __subclasscheck__(self, cls):
        ikiwa self._special:
            ikiwa not isinstance(cls, _GenericAlias):
                rudisha issubclass(cls, self.__origin__)
            ikiwa cls._special:
                rudisha issubclass(cls.__origin__, self.__origin__)
        raise TypeError("Subscripted generics cannot be used with"
                        " kundi and instance checks")

    eleza __reduce__(self):
        ikiwa self._special:
            rudisha self._name

        ikiwa self._name:
            origin = globals()[self._name]
        else:
            origin = self.__origin__
        ikiwa (origin is Callable and
            not (len(self.__args__) == 2 and self.__args__[0] is Ellipsis)):
            args = list(self.__args__[:-1]), self.__args__[-1]
        else:
            args = tuple(self.__args__)
            ikiwa len(args) == 1 and not isinstance(args[0], tuple):
                args, = args
        rudisha operator.getitem, (origin, args)


kundi _VariadicGenericAlias(_GenericAlias, _root=True):
    """Same as _GenericAlias above but for variadic aliases. Currently,
    this is used only by special internal aliases: Tuple and Callable.
    """
    eleza __getitem__(self, params):
        ikiwa self._name != 'Callable' or not self._special:
            rudisha self.__getitem_inner__(params)
        ikiwa not isinstance(params, tuple) or len(params) != 2:
            raise TypeError("Callable must be used as "
                            "Callable[[arg, ...], result].")
        args, result = params
        ikiwa args is Ellipsis:
            params = (Ellipsis, result)
        else:
            ikiwa not isinstance(args, list):
                raise TypeError(f"Callable[args, result]: args must be a list."
                                f" Got {args}")
            params = (tuple(args), result)
        rudisha self.__getitem_inner__(params)

    @_tp_cache
    eleza __getitem_inner__(self, params):
        ikiwa self.__origin__ is tuple and self._special:
            ikiwa params == ():
                rudisha self.copy_with((_TypingEmpty,))
            ikiwa not isinstance(params, tuple):
                params = (params,)
            ikiwa len(params) == 2 and params[1] is ...:
                msg = "Tuple[t, ...]: t must be a type."
                p = _type_check(params[0], msg)
                rudisha self.copy_with((p, _TypingEllipsis))
            msg = "Tuple[t0, t1, ...]: each t must be a type."
            params = tuple(_type_check(p, msg) for p in params)
            rudisha self.copy_with(params)
        ikiwa self.__origin__ is collections.abc.Callable and self._special:
            args, result = params
            msg = "Callable[args, result]: result must be a type."
            result = _type_check(result, msg)
            ikiwa args is Ellipsis:
                rudisha self.copy_with((_TypingEllipsis, result))
            msg = "Callable[[arg, ...], result]: each arg must be a type."
            args = tuple(_type_check(arg, msg) for arg in args)
            params = args + (result,)
            rudisha self.copy_with(params)
        rudisha super().__getitem__(params)


kundi Generic:
    """Abstract base kundi for generic types.

    A generic type is typically declared by inheriting kutoka
    this kundi parameterized with one or more type variables.
    For example, a generic mapping type might be defined as::

      kundi Mapping(Generic[KT, VT]):
          eleza __getitem__(self, key: KT) -> VT:
              ...
          # Etc.

    This kundi can then be used as follows::

      eleza lookup_name(mapping: Mapping[KT, VT], key: KT, default: VT) -> VT:
          try:
              rudisha mapping[key]
          except KeyError:
              rudisha default
    """
    __slots__ = ()
    _is_protocol = False

    eleza __new__(cls, *args, **kwds):
        ikiwa cls in (Generic, Protocol):
            raise TypeError(f"Type {cls.__name__} cannot be instantiated; "
                            "it can be used only as a base class")
        ikiwa super().__new__ is object.__new__ and cls.__init__ is not object.__init__:
            obj = super().__new__(cls)
        else:
            obj = super().__new__(cls, *args, **kwds)
        rudisha obj

    @_tp_cache
    eleza __class_getitem__(cls, params):
        ikiwa not isinstance(params, tuple):
            params = (params,)
        ikiwa not params and cls is not Tuple:
            raise TypeError(
                f"Parameter list to {cls.__qualname__}[...] cannot be empty")
        msg = "Parameters to generic types must be types."
        params = tuple(_type_check(p, msg) for p in params)
        ikiwa cls in (Generic, Protocol):
            # Generic and Protocol can only be subscripted with unique type variables.
            ikiwa not all(isinstance(p, TypeVar) for p in params):
                raise TypeError(
                    f"Parameters to {cls.__name__}[...] must all be type variables")
            ikiwa len(set(params)) != len(params):
                raise TypeError(
                    f"Parameters to {cls.__name__}[...] must all be unique")
        else:
            # Subscripting a regular Generic subclass.
            _check_generic(cls, params)
        rudisha _GenericAlias(cls, params)

    eleza __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        tvars = []
        ikiwa '__orig_bases__' in cls.__dict__:
            error = Generic in cls.__orig_bases__
        else:
            error = Generic in cls.__bases__ and cls.__name__ != 'Protocol'
        ikiwa error:
            raise TypeError("Cannot inherit kutoka plain Generic")
        ikiwa '__orig_bases__' in cls.__dict__:
            tvars = _collect_type_vars(cls.__orig_bases__)
            # Look for Generic[T1, ..., Tn].
            # If found, tvars must be a subset of it.
            # If not found, tvars is it.
            # Also check for and reject plain Generic,
            # and reject multiple Generic[...].
            gvars = None
            for base in cls.__orig_bases__:
                ikiwa (isinstance(base, _GenericAlias) and
                        base.__origin__ is Generic):
                    ikiwa gvars is not None:
                        raise TypeError(
                            "Cannot inherit kutoka Generic[...] multiple types.")
                    gvars = base.__parameters__
            ikiwa gvars is not None:
                tvarset = set(tvars)
                gvarset = set(gvars)
                ikiwa not tvarset <= gvarset:
                    s_vars = ', '.join(str(t) for t in tvars ikiwa t not in gvarset)
                    s_args = ', '.join(str(g) for g in gvars)
                    raise TypeError(f"Some type variables ({s_vars}) are"
                                    f" not listed in Generic[{s_args}]")
                tvars = gvars
        cls.__parameters__ = tuple(tvars)


kundi _TypingEmpty:
    """Internal placeholder for () or []. Used by TupleMeta and CallableMeta
    to allow empty list/tuple in specific places, without allowing them
    to sneak in where prohibited.
    """


kundi _TypingEllipsis:
    """Internal placeholder for ... (ellipsis)."""


_TYPING_INTERNALS = ['__parameters__', '__orig_bases__',  '__orig_class__',
                     '_is_protocol', '_is_runtime_protocol']

_SPECIAL_NAMES = ['__abstractmethods__', '__annotations__', '__dict__', '__doc__',
                  '__init__', '__module__', '__new__', '__slots__',
                  '__subclasshook__', '__weakref__']

# These special attributes will be not collected as protocol members.
EXCLUDED_ATTRIBUTES = _TYPING_INTERNALS + _SPECIAL_NAMES + ['_MutableMapping__marker']


eleza _get_protocol_attrs(cls):
    """Collect protocol members kutoka a protocol kundi objects.

    This includes names actually defined in the kundi dictionary, as well
    as names that appear in annotations. Special names (above) are skipped.
    """
    attrs = set()
    for base in cls.__mro__[:-1]:  # without object
        ikiwa base.__name__ in ('Protocol', 'Generic'):
            continue
        annotations = getattr(base, '__annotations__', {})
        for attr in list(base.__dict__.keys()) + list(annotations.keys()):
            ikiwa not attr.startswith('_abc_') and attr not in EXCLUDED_ATTRIBUTES:
                attrs.add(attr)
    rudisha attrs


eleza _is_callable_members_only(cls):
    # PEP 544 prohibits using issubclass() with protocols that have non-method members.
    rudisha all(callable(getattr(cls, attr, None)) for attr in _get_protocol_attrs(cls))


eleza _no_init(self, *args, **kwargs):
    ikiwa type(self)._is_protocol:
        raise TypeError('Protocols cannot be instantiated')


eleza _allow_reckless_class_cheks():
    """Allow instnance and kundi checks for special stdlib modules.

    The abc and functools modules indiscriminately call isinstance() and
    issubclass() on the whole MRO of a user class, which may contain protocols.
    """
    try:
        rudisha sys._getframe(3).f_globals['__name__'] in ['abc', 'functools']
    except (AttributeError, ValueError):  # For platforms without _getframe().
        rudisha True


_PROTO_WHITELIST = {
    'collections.abc': [
        'Callable', 'Awaitable', 'Iterable', 'Iterator', 'AsyncIterable',
        'Hashable', 'Sized', 'Container', 'Collection', 'Reversible',
    ],
    'contextlib': ['AbstractContextManager', 'AbstractAsyncContextManager'],
}


kundi _ProtocolMeta(ABCMeta):
    # This metakundi is really unfortunate and exists only because of
    # the lack of __instancehook__.
    eleza __instancecheck__(cls, instance):
        # We need this method for situations where attributes are
        # assigned in __init__.
        ikiwa ((not getattr(cls, '_is_protocol', False) or
                _is_callable_members_only(cls)) and
                issubclass(instance.__class__, cls)):
            rudisha True
        ikiwa cls._is_protocol:
            ikiwa all(hasattr(instance, attr) and
                    # All *methods* can be blocked by setting them to None.
                    (not callable(getattr(cls, attr, None)) or
                     getattr(instance, attr) is not None)
                    for attr in _get_protocol_attrs(cls)):
                rudisha True
        rudisha super().__instancecheck__(instance)


kundi Protocol(Generic, metaclass=_ProtocolMeta):
    """Base kundi for protocol classes.

    Protocol classes are defined as::

        kundi Proto(Protocol):
            eleza meth(self) -> int:
                ...

    Such classes are primarily used with static type checkers that recognize
    structural subtyping (static duck-typing), for example::

        kundi C:
            eleza meth(self) -> int:
                rudisha 0

        eleza func(x: Proto) -> int:
            rudisha x.meth()

        func(C())  # Passes static type check

    See PEP 544 for details. Protocol classes decorated with
    @typing.runtime_checkable act as simple-minded runtime protocols that check
    only the presence of given attributes, ignoring their type signatures.
    Protocol classes can be generic, they are defined as::

        kundi GenProto(Protocol[T]):
            eleza meth(self) -> T:
                ...
    """
    __slots__ = ()
    _is_protocol = True
    _is_runtime_protocol = False

    eleza __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)

        # Determine ikiwa this is a protocol or a concrete subclass.
        ikiwa not cls.__dict__.get('_is_protocol', False):
            cls._is_protocol = any(b is Protocol for b in cls.__bases__)

        # Set (or override) the protocol subkundi hook.
        eleza _proto_hook(other):
            ikiwa not cls.__dict__.get('_is_protocol', False):
                rudisha NotImplemented

            # First, perform various sanity checks.
            ikiwa not getattr(cls, '_is_runtime_protocol', False):
                ikiwa _allow_reckless_class_cheks():
                    rudisha NotImplemented
                raise TypeError("Instance and kundi checks can only be used with"
                                " @runtime_checkable protocols")
            ikiwa not _is_callable_members_only(cls):
                ikiwa _allow_reckless_class_cheks():
                    rudisha NotImplemented
                raise TypeError("Protocols with non-method members"
                                " don't support issubclass()")
            ikiwa not isinstance(other, type):
                # Same error message as for issubclass(1, int).
                raise TypeError('issubclass() arg 1 must be a class')

            # Second, perform the actual structural compatibility check.
            for attr in _get_protocol_attrs(cls):
                for base in other.__mro__:
                    # Check ikiwa the members appears in the kundi dictionary...
                    ikiwa attr in base.__dict__:
                        ikiwa base.__dict__[attr] is None:
                            rudisha NotImplemented
                        break

                    # ...or in annotations, ikiwa it is a sub-protocol.
                    annotations = getattr(base, '__annotations__', {})
                    ikiwa (isinstance(annotations, collections.abc.Mapping) and
                            attr in annotations and
                            issubclass(other, Generic) and other._is_protocol):
                        break
                else:
                    rudisha NotImplemented
            rudisha True

        ikiwa '__subclasshook__' not in cls.__dict__:
            cls.__subclasshook__ = _proto_hook

        # We have nothing more to do for non-protocols...
        ikiwa not cls._is_protocol:
            return

        # ... otherwise check consistency of bases, and prohibit instantiation.
        for base in cls.__bases__:
            ikiwa not (base in (object, Generic) or
                    base.__module__ in _PROTO_WHITELIST and
                    base.__name__ in _PROTO_WHITELIST[base.__module__] or
                    issubclass(base, Generic) and base._is_protocol):
                raise TypeError('Protocols can only inherit kutoka other'
                                ' protocols, got %r' % base)
        cls.__init__ = _no_init


eleza runtime_checkable(cls):
    """Mark a protocol kundi as a runtime protocol.

    Such protocol can be used with isinstance() and issubclass().
    Raise TypeError ikiwa applied to a non-protocol class.
    This allows a simple-minded structural check very similar to
    one trick ponies in collections.abc such as Iterable.
    For example::

        @runtime_checkable
        kundi Closable(Protocol):
            eleza close(self): ...

        assert isinstance(open('/some/file'), Closable)

    Warning: this will check only the presence of the required methods,
    not their type signatures!
    """
    ikiwa not issubclass(cls, Generic) or not cls._is_protocol:
        raise TypeError('@runtime_checkable can be only applied to protocol classes,'
                        ' got %r' % cls)
    cls._is_runtime_protocol = True
    rudisha cls


eleza cast(typ, val):
    """Cast a value to a type.

    This returns the value unchanged.  To the type checker this
    signals that the rudisha value has the designated type, but at
    runtime we intentionally don't check anything (we want this
    to be as fast as possible).
    """
    rudisha val


eleza _get_defaults(func):
    """Internal helper to extract the default arguments, by name."""
    try:
        code = func.__code__
    except AttributeError:
        # Some built-in functions don't have __code__, __defaults__, etc.
        rudisha {}
    pos_count = code.co_argcount
    arg_names = code.co_varnames
    arg_names = arg_names[:pos_count]
    defaults = func.__defaults__ or ()
    kwdefaults = func.__kwdefaults__
    res = dict(kwdefaults) ikiwa kwdefaults else {}
    pos_offset = pos_count - len(defaults)
    for name, value in zip(arg_names[pos_offset:], defaults):
        assert name not in res
        res[name] = value
    rudisha res


_allowed_types = (types.FunctionType, types.BuiltinFunctionType,
                  types.MethodType, types.ModuleType,
                  WrapperDescriptorType, MethodWrapperType, MethodDescriptorType)


eleza get_type_hints(obj, globalns=None, localns=None):
    """Return type hints for an object.

    This is often the same as obj.__annotations__, but it handles
    forward references encoded as string literals, and ikiwa necessary
    adds Optional[t] ikiwa a default value equal to None is set.

    The argument may be a module, class, method, or function. The annotations
    are returned as a dictionary. For classes, annotations include also
    inherited members.

    TypeError is raised ikiwa the argument is not of a type that can contain
    annotations, and an empty dictionary is returned ikiwa no annotations are
    present.

    BEWARE -- the behavior of globalns and localns is counterintuitive
    (unless you are familiar with how eval() and exec() work).  The
    search order is locals first, then globals.

    - If no dict arguments are passed, an attempt is made to use the
      globals kutoka obj (or the respective module's globals for classes),
      and these are also used as the locals.  If the object does not appear
      to have globals, an empty dictionary is used.

    - If one dict argument is passed, it is used for both globals and
      locals.

    - If two dict arguments are passed, they specify globals and
      locals, respectively.
    """

    ikiwa getattr(obj, '__no_type_check__', None):
        rudisha {}
    # Classes require a special treatment.
    ikiwa isinstance(obj, type):
        hints = {}
        for base in reversed(obj.__mro__):
            ikiwa globalns is None:
                base_globals = sys.modules[base.__module__].__dict__
            else:
                base_globals = globalns
            ann = base.__dict__.get('__annotations__', {})
            for name, value in ann.items():
                ikiwa value is None:
                    value = type(None)
                ikiwa isinstance(value, str):
                    value = ForwardRef(value, is_argument=False)
                value = _eval_type(value, base_globals, localns)
                hints[name] = value
        rudisha hints

    ikiwa globalns is None:
        ikiwa isinstance(obj, types.ModuleType):
            globalns = obj.__dict__
        else:
            globalns = getattr(obj, '__globals__', {})
        ikiwa localns is None:
            localns = globalns
    elikiwa localns is None:
        localns = globalns
    hints = getattr(obj, '__annotations__', None)
    ikiwa hints is None:
        # Return empty annotations for something that _could_ have them.
        ikiwa isinstance(obj, _allowed_types):
            rudisha {}
        else:
            raise TypeError('{!r} is not a module, class, method, '
                            'or function.'.format(obj))
    defaults = _get_defaults(obj)
    hints = dict(hints)
    for name, value in hints.items():
        ikiwa value is None:
            value = type(None)
        ikiwa isinstance(value, str):
            value = ForwardRef(value)
        value = _eval_type(value, globalns, localns)
        ikiwa name in defaults and defaults[name] is None:
            value = Optional[value]
        hints[name] = value
    rudisha hints


eleza get_origin(tp):
    """Get the unsubscripted version of a type.

    This supports generic types, Callable, Tuple, Union, Literal, Final and ClassVar.
    Return None for unsupported types. Examples::

        get_origin(Literal[42]) is Literal
        get_origin(int) is None
        get_origin(ClassVar[int]) is ClassVar
        get_origin(Generic) is Generic
        get_origin(Generic[T]) is Generic
        get_origin(Union[T, int]) is Union
        get_origin(List[Tuple[T, T]][int]) == list
    """
    ikiwa isinstance(tp, _GenericAlias):
        rudisha tp.__origin__
    ikiwa tp is Generic:
        rudisha Generic
    rudisha None


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
        ikiwa get_origin(tp) is collections.abc.Callable and res[0] is not Ellipsis:
            res = (list(res[:-1]), res[-1])
        rudisha res
    rudisha ()


eleza no_type_check(arg):
    """Decorator to indicate that annotations are not type hints.

    The argument must be a kundi or function; ikiwa it is a class, it
    applies recursively to all methods and classes defined in that class
    (but not to methods defined in its superclasses or subclasses).

    This mutates the function(s) or class(es) in place.
    """
    ikiwa isinstance(arg, type):
        arg_attrs = arg.__dict__.copy()
        for attr, val in arg.__dict__.items():
            ikiwa val in arg.__bases__ + (arg,):
                arg_attrs.pop(attr)
        for obj in arg_attrs.values():
            ikiwa isinstance(obj, types.FunctionType):
                obj.__no_type_check__ = True
            ikiwa isinstance(obj, type):
                no_type_check(obj)
    try:
        arg.__no_type_check__ = True
    except TypeError:  # built-in classes
        pass
    rudisha arg


eleza no_type_check_decorator(decorator):
    """Decorator to give another decorator the @no_type_check effect.

    This wraps the decorator with something that wraps the decorated
    function in @no_type_check.
    """

    @functools.wraps(decorator)
    eleza wrapped_decorator(*args, **kwds):
        func = decorator(*args, **kwds)
        func = no_type_check(func)
        rudisha func

    rudisha wrapped_decorator


eleza _overload_dummy(*args, **kwds):
    """Helper for @overload to raise when called."""
    raise NotImplementedError(
        "You should not call an overloaded function. "
        "A series of @overload-decorated functions "
        "outside a stub module should always be followed "
        "by an implementation that is not @overload-ed.")


eleza overload(func):
    """Decorator for overloaded functions/methods.

    In a stub file, place two or more stub definitions for the same
    function in a row, each decorated with @overload.  For example:

      @overload
      eleza utf8(value: None) -> None: ...
      @overload
      eleza utf8(value: bytes) -> bytes: ...
      @overload
      eleza utf8(value: str) -> bytes: ...

    In a non-stub file (i.e. a regular .py file), do the same but
    follow it with an implementation.  The implementation should *not*
    be decorated with @overload.  For example:

      @overload
      eleza utf8(value: None) -> None: ...
      @overload
      eleza utf8(value: bytes) -> bytes: ...
      @overload
      eleza utf8(value: str) -> bytes: ...
      eleza utf8(value):
          # implementation goes here
    """
    rudisha _overload_dummy


eleza final(f):
    """A decorator to indicate final methods and final classes.

    Use this decorator to indicate to type checkers that the decorated
    method cannot be overridden, and decorated kundi cannot be subclassed.
    For example:

      kundi Base:
          @final
          eleza done(self) -> None:
              ...
      kundi Sub(Base):
          eleza done(self) -> None:  # Error reported by type checker
                ...

      @final
      kundi Leaf:
          ...
      kundi Other(Leaf):  # Error reported by type checker
          ...

    There is no runtime checking of these properties.
    """
    rudisha f


# Some unconstrained type variables.  These are used by the container types.
# (These are not for export.)
T = TypeVar('T')  # Any type.
KT = TypeVar('KT')  # Key type.
VT = TypeVar('VT')  # Value type.
T_co = TypeVar('T_co', covariant=True)  # Any type covariant containers.
V_co = TypeVar('V_co', covariant=True)  # Any type covariant containers.
VT_co = TypeVar('VT_co', covariant=True)  # Value type covariant containers.
T_contra = TypeVar('T_contra', contravariant=True)  # Ditto contravariant.
# Internal type variable used for Type[].
CT_co = TypeVar('CT_co', covariant=True, bound=type)

# A useful type variable with constraints.  This represents string types.
# (This one *is* for export!)
AnyStr = TypeVar('AnyStr', bytes, str)


# Various ABCs mimicking those in collections.abc.
eleza _alias(origin, params, inst=True):
    rudisha _GenericAlias(origin, params, special=True, inst=inst)

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
Callable = _VariadicGenericAlias(collections.abc.Callable, (), special=True)
Callable.__doc__ = \
    """Callable type; Callable[[int], str] is a function of (int) -> str.

    The subscription syntax must always be used with exactly two
    values: the argument list and the rudisha type.  The argument list
    must be a list of types or ellipsis; the rudisha type must be a single type.

    There is no syntax to indicate optional or keyword arguments,
    such function types are rarely used as callback types.
    """
AbstractSet = _alias(collections.abc.Set, T_co)
MutableSet = _alias(collections.abc.MutableSet, T)
# NOTE: Mapping is only covariant in the value type.
Mapping = _alias(collections.abc.Mapping, (KT, VT_co))
MutableMapping = _alias(collections.abc.MutableMapping, (KT, VT))
Sequence = _alias(collections.abc.Sequence, T_co)
MutableSequence = _alias(collections.abc.MutableSequence, T)
ByteString = _alias(collections.abc.ByteString, ())  # Not generic
Tuple = _VariadicGenericAlias(tuple, (), inst=False, special=True)
Tuple.__doc__ = \
    """Tuple type; Tuple[X, Y] is the cross-product type of X and Y.

    Example: Tuple[T1, T2] is a tuple of two elements corresponding
    to type variables T1 and T2.  Tuple[int, float, str] is a tuple
    of an int, a float and a string.

    To specify a variable-length tuple of homogeneous type, use Tuple[T, ...].
    """
List = _alias(list, T, inst=False)
Deque = _alias(collections.deque, T)
Set = _alias(set, T, inst=False)
FrozenSet = _alias(frozenset, T_co, inst=False)
MappingView = _alias(collections.abc.MappingView, T_co)
KeysView = _alias(collections.abc.KeysView, KT)
ItemsView = _alias(collections.abc.ItemsView, (KT, VT_co))
ValuesView = _alias(collections.abc.ValuesView, VT_co)
ContextManager = _alias(contextlib.AbstractContextManager, T_co)
AsyncContextManager = _alias(contextlib.AbstractAsyncContextManager, T_co)
Dict = _alias(dict, (KT, VT), inst=False)
DefaultDict = _alias(collections.defaultdict, (KT, VT))
OrderedDict = _alias(collections.OrderedDict, (KT, VT))
Counter = _alias(collections.Counter, T)
ChainMap = _alias(collections.ChainMap, (KT, VT))
Generator = _alias(collections.abc.Generator, (T_co, T_contra, V_co))
AsyncGenerator = _alias(collections.abc.AsyncGenerator, (T_co, T_contra))
Type = _alias(type, CT_co, inst=False)
Type.__doc__ = \
    """A special construct usable to annotate kundi objects.

    For example, suppose we have the following classes::

      kundi User: ...  # Abstract base for User classes
      kundi BasicUser(User): ...
      kundi ProUser(User): ...
      kundi TeamUser(User): ...

    And a function that takes a kundi argument that's a subkundi of
    User and returns an instance of the corresponding class::

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
        pass


@runtime_checkable
kundi SupportsFloat(Protocol):
    """An ABC with one abstract method __float__."""
    __slots__ = ()

    @abstractmethod
    eleza __float__(self) -> float:
        pass


@runtime_checkable
kundi SupportsComplex(Protocol):
    """An ABC with one abstract method __complex__."""
    __slots__ = ()

    @abstractmethod
    eleza __complex__(self) -> complex:
        pass


@runtime_checkable
kundi SupportsBytes(Protocol):
    """An ABC with one abstract method __bytes__."""
    __slots__ = ()

    @abstractmethod
    eleza __bytes__(self) -> bytes:
        pass


@runtime_checkable
kundi SupportsIndex(Protocol):
    """An ABC with one abstract method __index__."""
    __slots__ = ()

    @abstractmethod
    eleza __index__(self) -> int:
        pass


@runtime_checkable
kundi SupportsAbs(Protocol[T_co]):
    """An ABC with one abstract method __abs__ that is covariant in its rudisha type."""
    __slots__ = ()

    @abstractmethod
    eleza __abs__(self) -> T_co:
        pass


@runtime_checkable
kundi SupportsRound(Protocol[T_co]):
    """An ABC with one abstract method __round__ that is covariant in its rudisha type."""
    __slots__ = ()

    @abstractmethod
    eleza __round__(self, ndigits: int = 0) -> T_co:
        pass


eleza _make_nmtuple(name, types):
    msg = "NamedTuple('Name', [(f0, t0), (f1, t1), ...]); each t must be a type"
    types = [(n, _type_check(t, msg)) for n, t in types]
    nm_tpl = collections.namedtuple(name, [n for n, t in types])
    # Prior to PEP 526, only _field_types attribute was assigned.
    # Now __annotations__ are used and _field_types is deprecated (remove in 3.9)
    nm_tpl.__annotations__ = nm_tpl._field_types = dict(types)
    try:
        nm_tpl.__module__ = sys._getframe(2).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass
    rudisha nm_tpl


# attributes prohibited to set in NamedTuple kundi syntax
_prohibited = ('__new__', '__init__', '__slots__', '__getnewargs__',
               '_fields', '_field_defaults', '_field_types',
               '_make', '_replace', '_asdict', '_source')

_special = ('__module__', '__name__', '__annotations__')


kundi NamedTupleMeta(type):

    eleza __new__(cls, typename, bases, ns):
        ikiwa ns.get('_root', False):
            rudisha super().__new__(cls, typename, bases, ns)
        types = ns.get('__annotations__', {})
        nm_tpl = _make_nmtuple(typename, types.items())
        defaults = []
        defaults_dict = {}
        for field_name in types:
            ikiwa field_name in ns:
                default_value = ns[field_name]
                defaults.append(default_value)
                defaults_dict[field_name] = default_value
            elikiwa defaults:
                raise TypeError("Non-default namedtuple field {field_name} cannot "
                                "follow default field(s) {default_names}"
                                .format(field_name=field_name,
                                        default_names=', '.join(defaults_dict.keys())))
        nm_tpl.__new__.__annotations__ = dict(types)
        nm_tpl.__new__.__defaults__ = tuple(defaults)
        nm_tpl._field_defaults = defaults_dict
        # update kutoka user namespace without overriding special namedtuple attributes
        for key in ns:
            ikiwa key in _prohibited:
                raise AttributeError("Cannot overwrite NamedTuple attribute " + key)
            elikiwa key not in _special and key not in nm_tpl._fields:
                setattr(nm_tpl, key, ns[key])
        rudisha nm_tpl


kundi NamedTuple(metaclass=NamedTupleMeta):
    """Typed version of namedtuple.

    Usage in Python versions >= 3.6::

        kundi Employee(NamedTuple):
            name: str
            id: int

    This is equivalent to::

        Employee = collections.namedtuple('Employee', ['name', 'id'])

    The resulting kundi has an extra __annotations__ attribute, giving a
    dict that maps field names to types.  (The field names are also in
    the _fields attribute, which is part of the namedtuple API.)
    Alternative equivalent keyword syntax is also accepted::

        Employee = NamedTuple('Employee', name=str, id=int)

    In Python versions <= 3.5 use::

        Employee = NamedTuple('Employee', [('name', str), ('id', int)])
    """
    _root = True

    eleza __new__(*args, **kwargs):
        ikiwa not args:
            raise TypeError('NamedTuple.__new__(): not enough arguments')
        cls, *args = args  # allow the "cls" keyword be passed
        ikiwa args:
            typename, *args = args # allow the "typename" keyword be passed
        elikiwa 'typename' in kwargs:
            typename = kwargs.pop('typename')
            agiza warnings
            warnings.warn("Passing 'typename' as keyword argument is deprecated",
                          DeprecationWarning, stacklevel=2)
        else:
            raise TypeError("NamedTuple.__new__() missing 1 required positional "
                            "argument: 'typename'")
        ikiwa args:
            try:
                fields, = args # allow the "fields" keyword be passed
            except ValueError:
                raise TypeError(f'NamedTuple.__new__() takes kutoka 2 to 3 '
                                f'positional arguments but {len(args) + 2} '
                                f'were given') kutoka None
        elikiwa 'fields' in kwargs and len(kwargs) == 1:
            fields = kwargs.pop('fields')
            agiza warnings
            warnings.warn("Passing 'fields' as keyword argument is deprecated",
                          DeprecationWarning, stacklevel=2)
        else:
            fields = None

        ikiwa fields is None:
            fields = kwargs.items()
        elikiwa kwargs:
            raise TypeError("Either list of fields or keywords"
                            " can be provided to NamedTuple, not both")
        rudisha _make_nmtuple(typename, fields)
    __new__.__text_signature__ = '($cls, typename, fields=None, /, **kwargs)'


eleza _dict_new(cls, /, *args, **kwargs):
    rudisha dict(*args, **kwargs)


eleza _typeddict_new(cls, typename, fields=None, /, *, total=True, **kwargs):
    ikiwa fields is None:
        fields = kwargs
    elikiwa kwargs:
        raise TypeError("TypedDict takes either a dict or keyword arguments,"
                        " but not both")

    ns = {'__annotations__': dict(fields), '__total__': total}
    try:
        # Setting correct module is necessary to make typed dict classes pickleable.
        ns['__module__'] = sys._getframe(1).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    rudisha _TypedDictMeta(typename, (), ns)


eleza _check_fails(cls, other):
    # Typed dicts are only for static structural subtyping.
    raise TypeError('TypedDict does not support instance and kundi checks')


kundi _TypedDictMeta(type):
    eleza __new__(cls, name, bases, ns, total=True):
        """Create new typed dict kundi object.

        This method is called directly when TypedDict is subclassed,
        or via _typeddict_new when TypedDict is instantiated. This way
        TypedDict supports all three syntax forms described in its docstring.
        Subclasses and instances of TypedDict rudisha actual dictionaries
        via _dict_new.
        """
        ns['__new__'] = _typeddict_new ikiwa name == 'TypedDict' else _dict_new
        tp_dict = super(_TypedDictMeta, cls).__new__(cls, name, (dict,), ns)

        anns = ns.get('__annotations__', {})
        msg = "TypedDict('Name', {f0: t0, f1: t1, ...}); each t must be a type"
        anns = {n: _type_check(tp, msg) for n, tp in anns.items()}
        for base in bases:
            anns.update(base.__dict__.get('__annotations__', {}))
        tp_dict.__annotations__ = anns
        ikiwa not hasattr(tp_dict, '__total__'):
            tp_dict.__total__ = total
        rudisha tp_dict

    __instancecheck__ = __subclasscheck__ = _check_fails


kundi TypedDict(dict, metaclass=_TypedDictMeta):
    """A simple typed namespace. At runtime it is equivalent to a plain dict.

    TypedDict creates a dictionary type that expects all of its
    instances to have a certain set of keys, where each key is
    associated with a value of a consistent type. This expectation
    is not checked at runtime but is only enforced by type checkers.
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

    The kundi syntax is only supported in Python 3.6+, while two other
    syntax forms work for Python 2.7 and 3.2+
    """


eleza NewType(name, tp):
    """NewType creates simple unique types with almost zero
    runtime overhead. NewType(name, tp) is considered a subtype of tp
    by static type checkers. At runtime, NewType(name, tp) returns
    a dummy function that simply returns its argument. Usage::

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


# Constant that's True when type checking, but False here.
TYPE_CHECKING = False


kundi IO(Generic[AnyStr]):
    """Generic base kundi for TextIO and BinaryIO.

    This is an abstract, generic version of the rudisha of open().

    NOTE: This does not distinguish between the different possible
    classes (text vs. binary, read vs. write vs. read/write,
    append-only, unbuffered).  The TextIO and BinaryIO subclasses
    below capture the distinctions between text vs. binary, which is
    pervasive in the interface; however we currently do not offer a
    way to track the other distinctions in the type system.
    """

    __slots__ = ()

    @property
    @abstractmethod
    eleza mode(self) -> str:
        pass

    @property
    @abstractmethod
    eleza name(self) -> str:
        pass

    @abstractmethod
    eleza close(self) -> None:
        pass

    @abstractmethod
    eleza closed(self) -> bool:
        pass

    @abstractmethod
    eleza fileno(self) -> int:
        pass

    @abstractmethod
    eleza flush(self) -> None:
        pass

    @abstractmethod
    eleza isatty(self) -> bool:
        pass

    @abstractmethod
    eleza read(self, n: int = -1) -> AnyStr:
        pass

    @abstractmethod
    eleza readable(self) -> bool:
        pass

    @abstractmethod
    eleza readline(self, limit: int = -1) -> AnyStr:
        pass

    @abstractmethod
    eleza readlines(self, hint: int = -1) -> List[AnyStr]:
        pass

    @abstractmethod
    eleza seek(self, offset: int, whence: int = 0) -> int:
        pass

    @abstractmethod
    eleza seekable(self) -> bool:
        pass

    @abstractmethod
    eleza tell(self) -> int:
        pass

    @abstractmethod
    eleza truncate(self, size: int = None) -> int:
        pass

    @abstractmethod
    eleza writable(self) -> bool:
        pass

    @abstractmethod
    eleza write(self, s: AnyStr) -> int:
        pass

    @abstractmethod
    eleza writelines(self, lines: List[AnyStr]) -> None:
        pass

    @abstractmethod
    eleza __enter__(self) -> 'IO[AnyStr]':
        pass

    @abstractmethod
    eleza __exit__(self, type, value, traceback) -> None:
        pass


kundi BinaryIO(IO[bytes]):
    """Typed version of the rudisha of open() in binary mode."""

    __slots__ = ()

    @abstractmethod
    eleza write(self, s: Union[bytes, bytearray]) -> int:
        pass

    @abstractmethod
    eleza __enter__(self) -> 'BinaryIO':
        pass


kundi TextIO(IO[str]):
    """Typed version of the rudisha of open() in text mode."""

    __slots__ = ()

    @property
    @abstractmethod
    eleza buffer(self) -> BinaryIO:
        pass

    @property
    @abstractmethod
    eleza encoding(self) -> str:
        pass

    @property
    @abstractmethod
    eleza errors(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    eleza line_buffering(self) -> bool:
        pass

    @property
    @abstractmethod
    eleza newlines(self) -> Any:
        pass

    @abstractmethod
    eleza __enter__(self) -> 'TextIO':
        pass


kundi io:
    """Wrapper namespace for IO generic classes."""

    __all__ = ['IO', 'TextIO', 'BinaryIO']
    IO = IO
    TextIO = TextIO
    BinaryIO = BinaryIO


io.__name__ = __name__ + '.io'
sys.modules[io.__name__] = io

Pattern = _alias(stdlib_re.Pattern, AnyStr)
Match = _alias(stdlib_re.Match, AnyStr)

kundi re:
    """Wrapper namespace for re type aliases."""

    __all__ = ['Pattern', 'Match']
    Pattern = Pattern
    Match = Match


re.__name__ = __name__ + '.re'
sys.modules[re.__name__] = re
