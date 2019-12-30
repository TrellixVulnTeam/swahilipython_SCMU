agiza contextlib
agiza collections
agiza pickle
agiza re
agiza sys
kutoka unittest agiza TestCase, main, skipUnless, SkipTest, skip
kutoka copy agiza copy, deepcopy

kutoka typing agiza Any, NoReturn
kutoka typing agiza TypeVar, AnyStr
kutoka typing agiza T, KT, VT  # Not kwenye __all__.
kutoka typing agiza Union, Optional, Literal
kutoka typing agiza Tuple, List, MutableMapping
kutoka typing agiza Callable
kutoka typing agiza Generic, ClassVar, Final, final, Protocol
kutoka typing agiza cast, runtime_checkable
kutoka typing agiza get_type_hints
kutoka typing agiza get_origin, get_args
kutoka typing agiza no_type_check, no_type_check_decorator
kutoka typing agiza Type
kutoka typing agiza NewType
kutoka typing agiza NamedTuple, TypedDict
kutoka typing agiza IO, TextIO, BinaryIO
kutoka typing agiza Pattern, Match
agiza abc
agiza typing
agiza weakref
agiza types

kutoka test agiza mod_generics_cache


kundi BaseTestCase(TestCase):

    eleza assertIsSubclass(self, cls, class_or_tuple, msg=Tupu):
        ikiwa sio issubclass(cls, class_or_tuple):
            message = '%r ni sio a subkundi of %r' % (cls, class_or_tuple)
            ikiwa msg ni sio Tupu:
                message += ' : %s' % msg
             ashiria self.failureException(message)

    eleza assertNotIsSubclass(self, cls, class_or_tuple, msg=Tupu):
        ikiwa issubclass(cls, class_or_tuple):
            message = '%r ni a subkundi of %r' % (cls, class_or_tuple)
            ikiwa msg ni sio Tupu:
                message += ' : %s' % msg
             ashiria self.failureException(message)

    eleza clear_caches(self):
        kila f kwenye typing._cleanups:
            f()


kundi Employee:
    pass


kundi Manager(Employee):
    pass


kundi Founder(Employee):
    pass


kundi ManagingFounder(Manager, Founder):
    pass


kundi AnyTests(BaseTestCase):

    eleza test_any_instance_type_error(self):
        ukijumuisha self.assertRaises(TypeError):
            isinstance(42, Any)

    eleza test_any_subclass_type_error(self):
        ukijumuisha self.assertRaises(TypeError):
            issubclass(Employee, Any)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(Any, Employee)

    eleza test_repr(self):
        self.assertEqual(repr(Any), 'typing.Any')

    eleza test_errors(self):
        ukijumuisha self.assertRaises(TypeError):
            issubclass(42, Any)
        ukijumuisha self.assertRaises(TypeError):
            Any[int]  # Any ni sio a generic type.

    eleza test_cannot_subclass(self):
        ukijumuisha self.assertRaises(TypeError):
            kundi A(Any):
                pass
        ukijumuisha self.assertRaises(TypeError):
            kundi A(type(Any)):
                pass

    eleza test_cannot_instantiate(self):
        ukijumuisha self.assertRaises(TypeError):
            Any()
        ukijumuisha self.assertRaises(TypeError):
            type(Any)()

    eleza test_any_works_with_alias(self):
        # These expressions must simply sio fail.
        typing.Match[Any]
        typing.Pattern[Any]
        typing.IO[Any]


kundi NoReturnTests(BaseTestCase):

    eleza test_noreturn_instance_type_error(self):
        ukijumuisha self.assertRaises(TypeError):
            isinstance(42, NoReturn)

    eleza test_noreturn_subclass_type_error(self):
        ukijumuisha self.assertRaises(TypeError):
            issubclass(Employee, NoReturn)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(NoReturn, Employee)

    eleza test_repr(self):
        self.assertEqual(repr(NoReturn), 'typing.NoReturn')

    eleza test_not_generic(self):
        ukijumuisha self.assertRaises(TypeError):
            NoReturn[int]

    eleza test_cannot_subclass(self):
        ukijumuisha self.assertRaises(TypeError):
            kundi A(NoReturn):
                pass
        ukijumuisha self.assertRaises(TypeError):
            kundi A(type(NoReturn)):
                pass

    eleza test_cannot_instantiate(self):
        ukijumuisha self.assertRaises(TypeError):
            NoReturn()
        ukijumuisha self.assertRaises(TypeError):
            type(NoReturn)()


kundi TypeVarTests(BaseTestCase):

    eleza test_basic_plain(self):
        T = TypeVar('T')
        # T equals itself.
        self.assertEqual(T, T)
        # T ni an instance of TypeVar
        self.assertIsInstance(T, TypeVar)

    eleza test_typevar_instance_type_error(self):
        T = TypeVar('T')
        ukijumuisha self.assertRaises(TypeError):
            isinstance(42, T)

    eleza test_typevar_subclass_type_error(self):
        T = TypeVar('T')
        ukijumuisha self.assertRaises(TypeError):
            issubclass(int, T)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(T, int)

    eleza test_constrained_error(self):
        ukijumuisha self.assertRaises(TypeError):
            X = TypeVar('X', int)
            X

    eleza test_union_unique(self):
        X = TypeVar('X')
        Y = TypeVar('Y')
        self.assertNotEqual(X, Y)
        self.assertEqual(Union[X], X)
        self.assertNotEqual(Union[X], Union[X, Y])
        self.assertEqual(Union[X, X], X)
        self.assertNotEqual(Union[X, int], Union[X])
        self.assertNotEqual(Union[X, int], Union[int])
        self.assertEqual(Union[X, int].__args__, (X, int))
        self.assertEqual(Union[X, int].__parameters__, (X,))
        self.assertIs(Union[X, int].__origin__, Union)

    eleza test_union_constrained(self):
        A = TypeVar('A', str, bytes)
        self.assertNotEqual(Union[A, str], Union[A])

    eleza test_repr(self):
        self.assertEqual(repr(T), '~T')
        self.assertEqual(repr(KT), '~KT')
        self.assertEqual(repr(VT), '~VT')
        self.assertEqual(repr(AnyStr), '~AnyStr')
        T_co = TypeVar('T_co', covariant=Kweli)
        self.assertEqual(repr(T_co), '+T_co')
        T_contra = TypeVar('T_contra', contravariant=Kweli)
        self.assertEqual(repr(T_contra), '-T_contra')

    eleza test_no_redefinition(self):
        self.assertNotEqual(TypeVar('T'), TypeVar('T'))
        self.assertNotEqual(TypeVar('T', int, str), TypeVar('T', int, str))

    eleza test_cannot_subclass_vars(self):
        ukijumuisha self.assertRaises(TypeError):
            kundi V(TypeVar('T')):
                pass

    eleza test_cannot_subclass_var_itself(self):
        ukijumuisha self.assertRaises(TypeError):
            kundi V(TypeVar):
                pass

    eleza test_cannot_instantiate_vars(self):
        ukijumuisha self.assertRaises(TypeError):
            TypeVar('A')()

    eleza test_bound_errors(self):
        ukijumuisha self.assertRaises(TypeError):
            TypeVar('X', bound=42)
        ukijumuisha self.assertRaises(TypeError):
            TypeVar('X', str, float, bound=Employee)

    eleza test_no_bivariant(self):
        ukijumuisha self.assertRaises(ValueError):
            TypeVar('T', covariant=Kweli, contravariant=Kweli)


kundi UnionTests(BaseTestCase):

    eleza test_basics(self):
        u = Union[int, float]
        self.assertNotEqual(u, Union)

    eleza test_subclass_error(self):
        ukijumuisha self.assertRaises(TypeError):
            issubclass(int, Union)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(Union, int)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(int, Union[int, str])
        ukijumuisha self.assertRaises(TypeError):
            issubclass(Union[int, str], int)

    eleza test_union_any(self):
        u = Union[Any]
        self.assertEqual(u, Any)
        u1 = Union[int, Any]
        u2 = Union[Any, int]
        u3 = Union[Any, object]
        self.assertEqual(u1, u2)
        self.assertNotEqual(u1, Any)
        self.assertNotEqual(u2, Any)
        self.assertNotEqual(u3, Any)

    eleza test_union_object(self):
        u = Union[object]
        self.assertEqual(u, object)
        u1 = Union[int, object]
        u2 = Union[object, int]
        self.assertEqual(u1, u2)
        self.assertNotEqual(u1, object)
        self.assertNotEqual(u2, object)

    eleza test_unordered(self):
        u1 = Union[int, float]
        u2 = Union[float, int]
        self.assertEqual(u1, u2)

    eleza test_single_class_disappears(self):
        t = Union[Employee]
        self.assertIs(t, Employee)

    eleza test_base_class_kept(self):
        u = Union[Employee, Manager]
        self.assertNotEqual(u, Employee)
        self.assertIn(Employee, u.__args__)
        self.assertIn(Manager, u.__args__)

    eleza test_union_union(self):
        u = Union[int, float]
        v = Union[u, Employee]
        self.assertEqual(v, Union[int, float, Employee])

    eleza test_repr(self):
        self.assertEqual(repr(Union), 'typing.Union')
        u = Union[Employee, int]
        self.assertEqual(repr(u), 'typing.Union[%s.Employee, int]' % __name__)
        u = Union[int, Employee]
        self.assertEqual(repr(u), 'typing.Union[int, %s.Employee]' % __name__)
        T = TypeVar('T')
        u = Union[T, int][int]
        self.assertEqual(repr(u), repr(int))
        u = Union[List[int], int]
        self.assertEqual(repr(u), 'typing.Union[typing.List[int], int]')

    eleza test_cannot_subclass(self):
        ukijumuisha self.assertRaises(TypeError):
            kundi C(Union):
                pass
        ukijumuisha self.assertRaises(TypeError):
            kundi C(type(Union)):
                pass
        ukijumuisha self.assertRaises(TypeError):
            kundi C(Union[int, str]):
                pass

    eleza test_cannot_instantiate(self):
        ukijumuisha self.assertRaises(TypeError):
            Union()
        ukijumuisha self.assertRaises(TypeError):
            type(Union)()
        u = Union[int, float]
        ukijumuisha self.assertRaises(TypeError):
            u()
        ukijumuisha self.assertRaises(TypeError):
            type(u)()

    eleza test_union_generalization(self):
        self.assertUongo(Union[str, typing.Iterable[int]] == str)
        self.assertUongo(Union[str, typing.Iterable[int]] == typing.Iterable[int])
        self.assertIn(str, Union[str, typing.Iterable[int]].__args__)
        self.assertIn(typing.Iterable[int], Union[str, typing.Iterable[int]].__args__)

    eleza test_union_compare_other(self):
        self.assertNotEqual(Union, object)
        self.assertNotEqual(Union, Any)
        self.assertNotEqual(ClassVar, Union)
        self.assertNotEqual(Optional, Union)
        self.assertNotEqual([Tupu], Optional)
        self.assertNotEqual(Optional, typing.Mapping)
        self.assertNotEqual(Optional[typing.MutableMapping], Union)

    eleza test_optional(self):
        o = Optional[int]
        u = Union[int, Tupu]
        self.assertEqual(o, u)

    eleza test_empty(self):
        ukijumuisha self.assertRaises(TypeError):
            Union[()]

    eleza test_union_instance_type_error(self):
        ukijumuisha self.assertRaises(TypeError):
            isinstance(42, Union[int, str])

    eleza test_no_eval_union(self):
        u = Union[int, str]
        eleza f(x: u): ...
        self.assertIs(get_type_hints(f)['x'], u)

    eleza test_function_repr_union(self):
        eleza fun() -> int: ...
        self.assertEqual(repr(Union[fun, int]), 'typing.Union[fun, int]')

    eleza test_union_str_pattern(self):
        # Shouldn't crash; see http://bugs.python.org/issue25390
        A = Union[str, Pattern]
        A

    eleza test_etree(self):
        # See https://github.com/python/typing/issues/229
        # (Only relevant kila Python 2.)
        jaribu:
            kutoka xml.etree.cElementTree agiza Element
        except ImportError:
             ashiria SkipTest("cElementTree sio found")
        Union[Element, str]  # Shouldn't crash

        eleza Elem(*args):
            rudisha Element(*args)

        Union[Elem, str]  # Nor should this


kundi TupleTests(BaseTestCase):

    eleza test_basics(self):
        ukijumuisha self.assertRaises(TypeError):
            issubclass(Tuple, Tuple[int, str])
        ukijumuisha self.assertRaises(TypeError):
            issubclass(tuple, Tuple[int, str])

        kundi TP(tuple): ...
        self.assertKweli(issubclass(tuple, Tuple))
        self.assertKweli(issubclass(TP, Tuple))

    eleza test_equality(self):
        self.assertEqual(Tuple[int], Tuple[int])
        self.assertEqual(Tuple[int, ...], Tuple[int, ...])
        self.assertNotEqual(Tuple[int], Tuple[int, int])
        self.assertNotEqual(Tuple[int], Tuple[int, ...])

    eleza test_tuple_subclass(self):
        kundi MyTuple(tuple):
            pass
        self.assertKweli(issubclass(MyTuple, Tuple))

    eleza test_tuple_instance_type_error(self):
        ukijumuisha self.assertRaises(TypeError):
            isinstance((0, 0), Tuple[int, int])
        self.assertIsInstance((0, 0), Tuple)

    eleza test_repr(self):
        self.assertEqual(repr(Tuple), 'typing.Tuple')
        self.assertEqual(repr(Tuple[()]), 'typing.Tuple[()]')
        self.assertEqual(repr(Tuple[int, float]), 'typing.Tuple[int, float]')
        self.assertEqual(repr(Tuple[int, ...]), 'typing.Tuple[int, ...]')

    eleza test_errors(self):
        ukijumuisha self.assertRaises(TypeError):
            issubclass(42, Tuple)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(42, Tuple[int])


kundi CallableTests(BaseTestCase):

    eleza test_self_subclass(self):
        ukijumuisha self.assertRaises(TypeError):
            self.assertKweli(issubclass(type(lambda x: x), Callable[[int], int]))
        self.assertKweli(issubclass(type(lambda x: x), Callable))

    eleza test_eq_hash(self):
        self.assertEqual(Callable[[int], int], Callable[[int], int])
        self.assertEqual(len({Callable[[int], int], Callable[[int], int]}), 1)
        self.assertNotEqual(Callable[[int], int], Callable[[int], str])
        self.assertNotEqual(Callable[[int], int], Callable[[str], int])
        self.assertNotEqual(Callable[[int], int], Callable[[int, int], int])
        self.assertNotEqual(Callable[[int], int], Callable[[], int])
        self.assertNotEqual(Callable[[int], int], Callable)

    eleza test_cannot_instantiate(self):
        ukijumuisha self.assertRaises(TypeError):
            Callable()
        ukijumuisha self.assertRaises(TypeError):
            type(Callable)()
        c = Callable[[int], str]
        ukijumuisha self.assertRaises(TypeError):
            c()
        ukijumuisha self.assertRaises(TypeError):
            type(c)()

    eleza test_callable_wrong_forms(self):
        ukijumuisha self.assertRaises(TypeError):
            Callable[[...], int]
        ukijumuisha self.assertRaises(TypeError):
            Callable[(), int]
        ukijumuisha self.assertRaises(TypeError):
            Callable[[()], int]
        ukijumuisha self.assertRaises(TypeError):
            Callable[[int, 1], 2]
        ukijumuisha self.assertRaises(TypeError):
            Callable[int]

    eleza test_callable_instance_works(self):
        eleza f():
            pass
        self.assertIsInstance(f, Callable)
        self.assertNotIsInstance(Tupu, Callable)

    eleza test_callable_instance_type_error(self):
        eleza f():
            pass
        ukijumuisha self.assertRaises(TypeError):
            self.assertIsInstance(f, Callable[[], Tupu])
        ukijumuisha self.assertRaises(TypeError):
            self.assertIsInstance(f, Callable[[], Any])
        ukijumuisha self.assertRaises(TypeError):
            self.assertNotIsInstance(Tupu, Callable[[], Tupu])
        ukijumuisha self.assertRaises(TypeError):
            self.assertNotIsInstance(Tupu, Callable[[], Any])

    eleza test_repr(self):
        ct0 = Callable[[], bool]
        self.assertEqual(repr(ct0), 'typing.Callable[[], bool]')
        ct2 = Callable[[str, float], int]
        self.assertEqual(repr(ct2), 'typing.Callable[[str, float], int]')
        ctv = Callable[..., str]
        self.assertEqual(repr(ctv), 'typing.Callable[..., str]')

    eleza test_callable_with_ellipsis(self):

        eleza foo(a: Callable[..., T]):
            pass

        self.assertEqual(get_type_hints(foo, globals(), locals()),
                         {'a': Callable[..., T]})

    eleza test_ellipsis_in_generic(self):
        # Shouldn't crash; see https://github.com/python/typing/issues/259
        typing.List[Callable[..., str]]


kundi LiteralTests(BaseTestCase):
    eleza test_basics(self):
        # All of these are allowed.
        Literal[1]
        Literal[1, 2, 3]
        Literal["x", "y", "z"]
        Literal[Tupu]
        Literal[Kweli]
        Literal[1, "2", Uongo]
        Literal[Literal[1, 2], Literal[4, 5]]
        Literal[b"foo", u"bar"]

    eleza test_illegal_parameters_do_not_raise_runtime_errors(self):
        # Type checkers should reject these types, but we do not
        #  ashiria errors at runtime to maintain maximium flexibility.
        Literal[int]
        Literal[3j + 2, ..., ()]
        Literal[{"foo": 3, "bar": 4}]
        Literal[T]

    eleza test_literals_inside_other_types(self):
        List[Literal[1, 2, 3]]
        List[Literal[("foo", "bar", "baz")]]

    eleza test_repr(self):
        self.assertEqual(repr(Literal[1]), "typing.Literal[1]")
        self.assertEqual(repr(Literal[1, Kweli, "foo"]), "typing.Literal[1, Kweli, 'foo']")
        self.assertEqual(repr(Literal[int]), "typing.Literal[int]")
        self.assertEqual(repr(Literal), "typing.Literal")
        self.assertEqual(repr(Literal[Tupu]), "typing.Literal[Tupu]")

    eleza test_cannot_init(self):
        ukijumuisha self.assertRaises(TypeError):
            Literal()
        ukijumuisha self.assertRaises(TypeError):
            Literal[1]()
        ukijumuisha self.assertRaises(TypeError):
            type(Literal)()
        ukijumuisha self.assertRaises(TypeError):
            type(Literal[1])()

    eleza test_no_isinstance_or_issubclass(self):
        ukijumuisha self.assertRaises(TypeError):
            isinstance(1, Literal[1])
        ukijumuisha self.assertRaises(TypeError):
            isinstance(int, Literal[1])
        ukijumuisha self.assertRaises(TypeError):
            issubclass(1, Literal[1])
        ukijumuisha self.assertRaises(TypeError):
            issubclass(int, Literal[1])

    eleza test_no_subclassing(self):
        ukijumuisha self.assertRaises(TypeError):
            kundi Foo(Literal[1]): pass
        ukijumuisha self.assertRaises(TypeError):
            kundi Bar(Literal): pass

    eleza test_no_multiple_subscripts(self):
        ukijumuisha self.assertRaises(TypeError):
            Literal[1][1]


XK = TypeVar('XK', str, bytes)
XV = TypeVar('XV')


kundi SimpleMapping(Generic[XK, XV]):

    eleza __getitem__(self, key: XK) -> XV:
        ...

    eleza __setitem__(self, key: XK, value: XV):
        ...

    eleza get(self, key: XK, default: XV = Tupu) -> XV:
        ...


kundi MySimpleMapping(SimpleMapping[XK, XV]):

    eleza __init__(self):
        self.store = {}

    eleza __getitem__(self, key: str):
        rudisha self.store[key]

    eleza __setitem__(self, key: str, value):
        self.store[key] = value

    eleza get(self, key: str, default=Tupu):
        jaribu:
            rudisha self.store[key]
        except KeyError:
            rudisha default


kundi Coordinate(Protocol):
    x: int
    y: int

@runtime_checkable
kundi Point(Coordinate, Protocol):
    label: str

kundi MyPoint:
    x: int
    y: int
    label: str

kundi XAxis(Protocol):
    x: int

kundi YAxis(Protocol):
    y: int

@runtime_checkable
kundi Position(XAxis, YAxis, Protocol):
    pass

@runtime_checkable
kundi Proto(Protocol):
    attr: int
    eleza meth(self, arg: str) -> int:
        ...

kundi Concrete(Proto):
    pass

kundi Other:
    attr: int = 1
    eleza meth(self, arg: str) -> int:
        ikiwa arg == 'this':
            rudisha 1
        rudisha 0

kundi NT(NamedTuple):
    x: int
    y: int

@runtime_checkable
kundi HasCallProtocol(Protocol):
    __call__: typing.Callable


kundi ProtocolTests(BaseTestCase):
    eleza test_basic_protocol(self):
        @runtime_checkable
        kundi P(Protocol):
            eleza meth(self):
                pass

        kundi C: pass

        kundi D:
            eleza meth(self):
                pass

        eleza f():
            pass

        self.assertIsSubclass(D, P)
        self.assertIsInstance(D(), P)
        self.assertNotIsSubclass(C, P)
        self.assertNotIsInstance(C(), P)
        self.assertNotIsSubclass(types.FunctionType, P)
        self.assertNotIsInstance(f, P)

    eleza test_everything_implements_empty_protocol(self):
        @runtime_checkable
        kundi Empty(Protocol):
            pass

        kundi C:
            pass

        eleza f():
            pass

        kila thing kwenye (object, type, tuple, C, types.FunctionType):
            self.assertIsSubclass(thing, Empty)
        kila thing kwenye (object(), 1, (), typing, f):
            self.assertIsInstance(thing, Empty)

    eleza test_function_implements_protocol(self):
        eleza f():
            pass

        self.assertIsInstance(f, HasCallProtocol)

    eleza test_no_inheritance_from_nominal(self):
        kundi C: pass

        kundi BP(Protocol): pass

        ukijumuisha self.assertRaises(TypeError):
            kundi P(C, Protocol):
                pass
        ukijumuisha self.assertRaises(TypeError):
            kundi P(Protocol, C):
                pass
        ukijumuisha self.assertRaises(TypeError):
            kundi P(BP, C, Protocol):
                pass

        kundi D(BP, C): pass

        kundi E(C, BP): pass

        self.assertNotIsInstance(D(), E)
        self.assertNotIsInstance(E(), D)

    eleza test_no_instantiation(self):
        kundi P(Protocol): pass

        ukijumuisha self.assertRaises(TypeError):
            P()

        kundi C(P): pass

        self.assertIsInstance(C(), C)
        T = TypeVar('T')

        kundi PG(Protocol[T]): pass

        ukijumuisha self.assertRaises(TypeError):
            PG()
        ukijumuisha self.assertRaises(TypeError):
            PG[int]()
        ukijumuisha self.assertRaises(TypeError):
            PG[T]()

        kundi CG(PG[T]): pass

        self.assertIsInstance(CG[int](), CG)

    eleza test_cannot_instantiate_abstract(self):
        @runtime_checkable
        kundi P(Protocol):
            @abc.abstractmethod
            eleza ameth(self) -> int:
                 ashiria NotImplementedError

        kundi B(P):
            pass

        kundi C(B):
            eleza ameth(self) -> int:
                rudisha 26

        ukijumuisha self.assertRaises(TypeError):
            B()
        self.assertIsInstance(C(), P)

    eleza test_subprotocols_extending(self):
        kundi P1(Protocol):
            eleza meth1(self):
                pass

        @runtime_checkable
        kundi P2(P1, Protocol):
            eleza meth2(self):
                pass

        kundi C:
            eleza meth1(self):
                pass

            eleza meth2(self):
                pass

        kundi C1:
            eleza meth1(self):
                pass

        kundi C2:
            eleza meth2(self):
                pass

        self.assertNotIsInstance(C1(), P2)
        self.assertNotIsInstance(C2(), P2)
        self.assertNotIsSubclass(C1, P2)
        self.assertNotIsSubclass(C2, P2)
        self.assertIsInstance(C(), P2)
        self.assertIsSubclass(C, P2)

    eleza test_subprotocols_merging(self):
        kundi P1(Protocol):
            eleza meth1(self):
                pass

        kundi P2(Protocol):
            eleza meth2(self):
                pass

        @runtime_checkable
        kundi P(P1, P2, Protocol):
            pass

        kundi C:
            eleza meth1(self):
                pass

            eleza meth2(self):
                pass

        kundi C1:
            eleza meth1(self):
                pass

        kundi C2:
            eleza meth2(self):
                pass

        self.assertNotIsInstance(C1(), P)
        self.assertNotIsInstance(C2(), P)
        self.assertNotIsSubclass(C1, P)
        self.assertNotIsSubclass(C2, P)
        self.assertIsInstance(C(), P)
        self.assertIsSubclass(C, P)

    eleza test_protocols_issubclass(self):
        T = TypeVar('T')

        @runtime_checkable
        kundi P(Protocol):
            eleza x(self): ...

        @runtime_checkable
        kundi PG(Protocol[T]):
            eleza x(self): ...

        kundi BadP(Protocol):
            eleza x(self): ...

        kundi BadPG(Protocol[T]):
            eleza x(self): ...

        kundi C:
            eleza x(self): ...

        self.assertIsSubclass(C, P)
        self.assertIsSubclass(C, PG)
        self.assertIsSubclass(BadP, PG)

        ukijumuisha self.assertRaises(TypeError):
            issubclass(C, PG[T])
        ukijumuisha self.assertRaises(TypeError):
            issubclass(C, PG[C])
        ukijumuisha self.assertRaises(TypeError):
            issubclass(C, BadP)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(C, BadPG)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(P, PG[T])
        ukijumuisha self.assertRaises(TypeError):
            issubclass(PG, PG[int])

    eleza test_protocols_issubclass_non_callable(self):
        kundi C:
            x = 1

        @runtime_checkable
        kundi PNonCall(Protocol):
            x = 1

        ukijumuisha self.assertRaises(TypeError):
            issubclass(C, PNonCall)
        self.assertIsInstance(C(), PNonCall)
        PNonCall.register(C)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(C, PNonCall)
        self.assertIsInstance(C(), PNonCall)

        # check that non-protocol subclasses are sio affected
        kundi D(PNonCall): ...

        self.assertNotIsSubclass(C, D)
        self.assertNotIsInstance(C(), D)
        D.register(C)
        self.assertIsSubclass(C, D)
        self.assertIsInstance(C(), D)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(D, PNonCall)

    eleza test_protocols_isinstance(self):
        T = TypeVar('T')

        @runtime_checkable
        kundi P(Protocol):
            eleza meth(x): ...

        @runtime_checkable
        kundi PG(Protocol[T]):
            eleza meth(x): ...

        kundi BadP(Protocol):
            eleza meth(x): ...

        kundi BadPG(Protocol[T]):
            eleza meth(x): ...

        kundi C:
            eleza meth(x): ...

        self.assertIsInstance(C(), P)
        self.assertIsInstance(C(), PG)
        ukijumuisha self.assertRaises(TypeError):
            isinstance(C(), PG[T])
        ukijumuisha self.assertRaises(TypeError):
            isinstance(C(), PG[C])
        ukijumuisha self.assertRaises(TypeError):
            isinstance(C(), BadP)
        ukijumuisha self.assertRaises(TypeError):
            isinstance(C(), BadPG)

    eleza test_protocols_isinstance_py36(self):
        kundi APoint:
            eleza __init__(self, x, y, label):
                self.x = x
                self.y = y
                self.label = label

        kundi BPoint:
            label = 'B'

            eleza __init__(self, x, y):
                self.x = x
                self.y = y

        kundi C:
            eleza __init__(self, attr):
                self.attr = attr

            eleza meth(self, arg):
                rudisha 0

        kundi Bad: pass

        self.assertIsInstance(APoint(1, 2, 'A'), Point)
        self.assertIsInstance(BPoint(1, 2), Point)
        self.assertNotIsInstance(MyPoint(), Point)
        self.assertIsInstance(BPoint(1, 2), Position)
        self.assertIsInstance(Other(), Proto)
        self.assertIsInstance(Concrete(), Proto)
        self.assertIsInstance(C(42), Proto)
        self.assertNotIsInstance(Bad(), Proto)
        self.assertNotIsInstance(Bad(), Point)
        self.assertNotIsInstance(Bad(), Position)
        self.assertNotIsInstance(Bad(), Concrete)
        self.assertNotIsInstance(Other(), Concrete)
        self.assertIsInstance(NT(1, 2), Position)

    eleza test_protocols_isinstance_init(self):
        T = TypeVar('T')

        @runtime_checkable
        kundi P(Protocol):
            x = 1

        @runtime_checkable
        kundi PG(Protocol[T]):
            x = 1

        kundi C:
            eleza __init__(self, x):
                self.x = x

        self.assertIsInstance(C(1), P)
        self.assertIsInstance(C(1), PG)

    eleza test_protocol_checks_after_subscript(self):
        kundi P(Protocol[T]): pass
        kundi C(P[T]): pass
        kundi Other1: pass
        kundi Other2: pass
        CA = C[Any]

        self.assertNotIsInstance(Other1(), C)
        self.assertNotIsSubclass(Other2, C)

        kundi D1(C[Any]): pass
        kundi D2(C[Any]): pass
        CI = C[int]

        self.assertIsInstance(D1(), C)
        self.assertIsSubclass(D2, C)

    eleza test_protocols_support_register(self):
        @runtime_checkable
        kundi P(Protocol):
            x = 1

        kundi PM(Protocol):
            eleza meth(self): pass

        kundi D(PM): pass

        kundi C: pass

        D.register(C)
        P.register(C)
        self.assertIsInstance(C(), P)
        self.assertIsInstance(C(), D)

    eleza test_none_on_non_callable_doesnt_block_implementation(self):
        @runtime_checkable
        kundi P(Protocol):
            x = 1

        kundi A:
            x = 1

        kundi B(A):
            x = Tupu

        kundi C:
            eleza __init__(self):
                self.x = Tupu

        self.assertIsInstance(B(), P)
        self.assertIsInstance(C(), P)

    eleza test_none_on_callable_blocks_implementation(self):
        @runtime_checkable
        kundi P(Protocol):
            eleza x(self): ...

        kundi A:
            eleza x(self): ...

        kundi B(A):
            x = Tupu

        kundi C:
            eleza __init__(self):
                self.x = Tupu

        self.assertNotIsInstance(B(), P)
        self.assertNotIsInstance(C(), P)

    eleza test_non_protocol_subclasses(self):
        kundi P(Protocol):
            x = 1

        @runtime_checkable
        kundi PR(Protocol):
            eleza meth(self): pass

        kundi NonP(P):
            x = 1

        kundi NonPR(PR): pass

        kundi C:
            x = 1

        kundi D:
            eleza meth(self): pass

        self.assertNotIsInstance(C(), NonP)
        self.assertNotIsInstance(D(), NonPR)
        self.assertNotIsSubclass(C, NonP)
        self.assertNotIsSubclass(D, NonPR)
        self.assertIsInstance(NonPR(), PR)
        self.assertIsSubclass(NonPR, PR)

    eleza test_custom_subclasshook(self):
        kundi P(Protocol):
            x = 1

        kundi OKClass: pass

        kundi BadClass:
            x = 1

        kundi C(P):
            @classmethod
            eleza __subclasshook__(cls, other):
                rudisha other.__name__.startswith("OK")

        self.assertIsInstance(OKClass(), C)
        self.assertNotIsInstance(BadClass(), C)
        self.assertIsSubclass(OKClass, C)
        self.assertNotIsSubclass(BadClass, C)

    eleza test_issubclass_fails_correctly(self):
        @runtime_checkable
        kundi P(Protocol):
            x = 1

        kundi C: pass

        ukijumuisha self.assertRaises(TypeError):
            issubclass(C(), P)

    eleza test_defining_generic_protocols(self):
        T = TypeVar('T')
        S = TypeVar('S')

        @runtime_checkable
        kundi PR(Protocol[T, S]):
            eleza meth(self): pass

        kundi P(PR[int, T], Protocol[T]):
            y = 1

        ukijumuisha self.assertRaises(TypeError):
            PR[int]
        ukijumuisha self.assertRaises(TypeError):
            P[int, str]
        ukijumuisha self.assertRaises(TypeError):
            PR[int, 1]
        ukijumuisha self.assertRaises(TypeError):
            PR[int, ClassVar]

        kundi C(PR[int, T]): pass

        self.assertIsInstance(C[str](), C)

    eleza test_defining_generic_protocols_old_style(self):
        T = TypeVar('T')
        S = TypeVar('S')

        @runtime_checkable
        kundi PR(Protocol, Generic[T, S]):
            eleza meth(self): pass

        kundi P(PR[int, str], Protocol):
            y = 1

        ukijumuisha self.assertRaises(TypeError):
            issubclass(PR[int, str], PR)
        self.assertIsSubclass(P, PR)
        ukijumuisha self.assertRaises(TypeError):
            PR[int]
        ukijumuisha self.assertRaises(TypeError):
            PR[int, 1]

        kundi P1(Protocol, Generic[T]):
            eleza bar(self, x: T) -> str: ...

        kundi P2(Generic[T], Protocol):
            eleza bar(self, x: T) -> str: ...

        @runtime_checkable
        kundi PSub(P1[str], Protocol):
            x = 1

        kundi Test:
            x = 1

            eleza bar(self, x: str) -> str:
                rudisha x

        self.assertIsInstance(Test(), PSub)
        ukijumuisha self.assertRaises(TypeError):
            PR[int, ClassVar]

    eleza test_init_called(self):
        T = TypeVar('T')

        kundi P(Protocol[T]): pass

        kundi C(P[T]):
            eleza __init__(self):
                self.test = 'OK'

        self.assertEqual(C[int]().test, 'OK')

    eleza test_protocols_bad_subscripts(self):
        T = TypeVar('T')
        S = TypeVar('S')
        ukijumuisha self.assertRaises(TypeError):
            kundi P(Protocol[T, T]): pass
        ukijumuisha self.assertRaises(TypeError):
            kundi P(Protocol[int]): pass
        ukijumuisha self.assertRaises(TypeError):
            kundi P(Protocol[T], Protocol[S]): pass
        ukijumuisha self.assertRaises(TypeError):
            kundi P(typing.Mapping[T, S], Protocol[T]): pass

    eleza test_generic_protocols_repr(self):
        T = TypeVar('T')
        S = TypeVar('S')

        kundi P(Protocol[T, S]): pass

        self.assertKweli(repr(P[T, S]).endswith('P[~T, ~S]'))
        self.assertKweli(repr(P[int, str]).endswith('P[int, str]'))

    eleza test_generic_protocols_eq(self):
        T = TypeVar('T')
        S = TypeVar('S')

        kundi P(Protocol[T, S]): pass

        self.assertEqual(P, P)
        self.assertEqual(P[int, T], P[int, T])
        self.assertEqual(P[T, T][Tuple[T, S]][int, str],
                         P[Tuple[int, str], Tuple[int, str]])

    eleza test_generic_protocols_special_from_generic(self):
        T = TypeVar('T')

        kundi P(Protocol[T]): pass

        self.assertEqual(P.__parameters__, (T,))
        self.assertEqual(P[int].__parameters__, ())
        self.assertEqual(P[int].__args__, (int,))
        self.assertIs(P[int].__origin__, P)

    eleza test_generic_protocols_special_from_protocol(self):
        @runtime_checkable
        kundi PR(Protocol):
            x = 1

        kundi P(Protocol):
            eleza meth(self):
                pass

        T = TypeVar('T')

        kundi PG(Protocol[T]):
            x = 1

            eleza meth(self):
                pass

        self.assertKweli(P._is_protocol)
        self.assertKweli(PR._is_protocol)
        self.assertKweli(PG._is_protocol)
        self.assertUongo(P._is_runtime_protocol)
        self.assertKweli(PR._is_runtime_protocol)
        self.assertKweli(PG[int]._is_protocol)
        self.assertEqual(typing._get_protocol_attrs(P), {'meth'})
        self.assertEqual(typing._get_protocol_attrs(PR), {'x'})
        self.assertEqual(frozenset(typing._get_protocol_attrs(PG)),
                         frozenset({'x', 'meth'}))

    eleza test_no_runtime_deco_on_nominal(self):
        ukijumuisha self.assertRaises(TypeError):
            @runtime_checkable
            kundi C: pass

        kundi Proto(Protocol):
            x = 1

        ukijumuisha self.assertRaises(TypeError):
            @runtime_checkable
            kundi Concrete(Proto):
                pass

    eleza test_none_treated_correctly(self):
        @runtime_checkable
        kundi P(Protocol):
            x = Tupu  # type: int

        kundi B(object): pass

        self.assertNotIsInstance(B(), P)

        kundi C:
            x = 1

        kundi D:
            x = Tupu

        self.assertIsInstance(C(), P)
        self.assertIsInstance(D(), P)

        kundi CI:
            eleza __init__(self):
                self.x = 1

        kundi DI:
            eleza __init__(self):
                self.x = Tupu

        self.assertIsInstance(C(), P)
        self.assertIsInstance(D(), P)

    eleza test_protocols_in_unions(self):
        kundi P(Protocol):
            x = Tupu  # type: int

        Alias = typing.Union[typing.Iterable, P]
        Alias2 = typing.Union[P, typing.Iterable]
        self.assertEqual(Alias, Alias2)

    eleza test_protocols_pickleable(self):
        global P, CP  # pickle wants to reference the kundi by name
        T = TypeVar('T')

        @runtime_checkable
        kundi P(Protocol[T]):
            x = 1

        kundi CP(P[int]):
            pass

        c = CP()
        c.foo = 42
        c.bar = 'abc'
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            z = pickle.dumps(c, proto)
            x = pickle.loads(z)
            self.assertEqual(x.foo, 42)
            self.assertEqual(x.bar, 'abc')
            self.assertEqual(x.x, 1)
            self.assertEqual(x.__dict__, {'foo': 42, 'bar': 'abc'})
            s = pickle.dumps(P)
            D = pickle.loads(s)

            kundi E:
                x = 1

            self.assertIsInstance(E(), D)

    eleza test_supports_int(self):
        self.assertIsSubclass(int, typing.SupportsInt)
        self.assertNotIsSubclass(str, typing.SupportsInt)

    eleza test_supports_float(self):
        self.assertIsSubclass(float, typing.SupportsFloat)
        self.assertNotIsSubclass(str, typing.SupportsFloat)

    eleza test_supports_complex(self):

        # Note: complex itself doesn't have __complex__.
        kundi C:
            eleza __complex__(self):
                rudisha 0j

        self.assertIsSubclass(C, typing.SupportsComplex)
        self.assertNotIsSubclass(str, typing.SupportsComplex)

    eleza test_supports_bytes(self):

        # Note: bytes itself doesn't have __bytes__.
        kundi B:
            eleza __bytes__(self):
                rudisha b''

        self.assertIsSubclass(B, typing.SupportsBytes)
        self.assertNotIsSubclass(str, typing.SupportsBytes)

    eleza test_supports_abs(self):
        self.assertIsSubclass(float, typing.SupportsAbs)
        self.assertIsSubclass(int, typing.SupportsAbs)
        self.assertNotIsSubclass(str, typing.SupportsAbs)

    eleza test_supports_round(self):
        issubclass(float, typing.SupportsRound)
        self.assertIsSubclass(float, typing.SupportsRound)
        self.assertIsSubclass(int, typing.SupportsRound)
        self.assertNotIsSubclass(str, typing.SupportsRound)

    eleza test_reversible(self):
        self.assertIsSubclass(list, typing.Reversible)
        self.assertNotIsSubclass(int, typing.Reversible)

    eleza test_supports_index(self):
        self.assertIsSubclass(int, typing.SupportsIndex)
        self.assertNotIsSubclass(str, typing.SupportsIndex)

    eleza test_bundled_protocol_instance_works(self):
        self.assertIsInstance(0, typing.SupportsAbs)
        kundi C1(typing.SupportsInt):
            eleza __int__(self) -> int:
                rudisha 42
        kundi C2(C1):
            pass
        c = C2()
        self.assertIsInstance(c, C1)

    eleza test_collections_protocols_allowed(self):
        @runtime_checkable
        kundi Custom(collections.abc.Iterable, Protocol):
            eleza close(self): ...

        kundi A: pass
        kundi B:
            eleza __iter__(self):
                rudisha []
            eleza close(self):
                rudisha 0

        self.assertIsSubclass(B, Custom)
        self.assertNotIsSubclass(A, Custom)

    eleza test_builtin_protocol_whitelist(self):
        ukijumuisha self.assertRaises(TypeError):
            kundi CustomProtocol(TestCase, Protocol):
                pass

        kundi CustomContextManager(typing.ContextManager, Protocol):
            pass

kundi GenericTests(BaseTestCase):

    eleza test_basics(self):
        X = SimpleMapping[str, Any]
        self.assertEqual(X.__parameters__, ())
        ukijumuisha self.assertRaises(TypeError):
            X[str]
        ukijumuisha self.assertRaises(TypeError):
            X[str, str]
        Y = SimpleMapping[XK, str]
        self.assertEqual(Y.__parameters__, (XK,))
        Y[str]
        ukijumuisha self.assertRaises(TypeError):
            Y[str, str]
        SM1 = SimpleMapping[str, int]
        ukijumuisha self.assertRaises(TypeError):
            issubclass(SM1, SimpleMapping)
        self.assertIsInstance(SM1(), SimpleMapping)

    eleza test_generic_errors(self):
        T = TypeVar('T')
        S = TypeVar('S')
        ukijumuisha self.assertRaises(TypeError):
            Generic[T]()
        ukijumuisha self.assertRaises(TypeError):
            Generic[T][T]
        ukijumuisha self.assertRaises(TypeError):
            Generic[T][S]
        ukijumuisha self.assertRaises(TypeError):
            kundi C(Generic[T], Generic[T]): ...
        ukijumuisha self.assertRaises(TypeError):
            isinstance([], List[int])
        ukijumuisha self.assertRaises(TypeError):
            issubclass(list, List[int])
        ukijumuisha self.assertRaises(TypeError):
            kundi NewGeneric(Generic): ...
        ukijumuisha self.assertRaises(TypeError):
            kundi MyGeneric(Generic[T], Generic[S]): ...
        ukijumuisha self.assertRaises(TypeError):
            kundi MyGeneric(List[T], Generic[S]): ...

    eleza test_init(self):
        T = TypeVar('T')
        S = TypeVar('S')
        ukijumuisha self.assertRaises(TypeError):
            Generic[T, T]
        ukijumuisha self.assertRaises(TypeError):
            Generic[T, S, T]

    eleza test_init_subclass(self):
        kundi X(typing.Generic[T]):
            eleza __init_subclass__(cls, **kwargs):
                super().__init_subclass__(**kwargs)
                cls.attr = 42
        kundi Y(X):
            pass
        self.assertEqual(Y.attr, 42)
        ukijumuisha self.assertRaises(AttributeError):
            X.attr
        X.attr = 1
        Y.attr = 2
        kundi Z(Y):
            pass
        kundi W(X[int]):
            pass
        self.assertEqual(Y.attr, 2)
        self.assertEqual(Z.attr, 42)
        self.assertEqual(W.attr, 42)

    eleza test_repr(self):
        self.assertEqual(repr(SimpleMapping),
                         f"<kundi '{__name__}.SimpleMapping'>")
        self.assertEqual(repr(MySimpleMapping),
                         f"<kundi '{__name__}.MySimpleMapping'>")

    eleza test_chain_repr(self):
        T = TypeVar('T')
        S = TypeVar('S')

        kundi C(Generic[T]):
            pass

        X = C[Tuple[S, T]]
        self.assertEqual(X, C[Tuple[S, T]])
        self.assertNotEqual(X, C[Tuple[T, S]])

        Y = X[T, int]
        self.assertEqual(Y, X[T, int])
        self.assertNotEqual(Y, X[S, int])
        self.assertNotEqual(Y, X[T, str])

        Z = Y[str]
        self.assertEqual(Z, Y[str])
        self.assertNotEqual(Z, Y[int])
        self.assertNotEqual(Z, Y[T])

        self.assertKweli(str(Z).endswith(
            '.C[typing.Tuple[str, int]]'))

    eleza test_new_repr(self):
        T = TypeVar('T')
        U = TypeVar('U', covariant=Kweli)
        S = TypeVar('S')

        self.assertEqual(repr(List), 'typing.List')
        self.assertEqual(repr(List[T]), 'typing.List[~T]')
        self.assertEqual(repr(List[U]), 'typing.List[+U]')
        self.assertEqual(repr(List[S][T][int]), 'typing.List[int]')
        self.assertEqual(repr(List[int]), 'typing.List[int]')

    eleza test_new_repr_complex(self):
        T = TypeVar('T')
        TS = TypeVar('TS')

        self.assertEqual(repr(typing.Mapping[T, TS][TS, T]), 'typing.Mapping[~TS, ~T]')
        self.assertEqual(repr(List[Tuple[T, TS]][int, T]),
                         'typing.List[typing.Tuple[int, ~T]]')
        self.assertEqual(
            repr(List[Tuple[T, T]][List[int]]),
            'typing.List[typing.Tuple[typing.List[int], typing.List[int]]]'
        )

    eleza test_new_repr_bare(self):
        T = TypeVar('T')
        self.assertEqual(repr(Generic[T]), 'typing.Generic[~T]')
        self.assertEqual(repr(typing.Protocol[T]), 'typing.Protocol[~T]')
        kundi C(typing.Dict[Any, Any]): ...
        # this line should just work
        repr(C.__mro__)

    eleza test_dict(self):
        T = TypeVar('T')

        kundi B(Generic[T]):
            pass

        b = B()
        b.foo = 42
        self.assertEqual(b.__dict__, {'foo': 42})

        kundi C(B[int]):
            pass

        c = C()
        c.bar = 'abc'
        self.assertEqual(c.__dict__, {'bar': 'abc'})

    eleza test_subscripted_generics_as_proxies(self):
        T = TypeVar('T')
        kundi C(Generic[T]):
            x = 'def'
        self.assertEqual(C[int].x, 'def')
        self.assertEqual(C[C[int]].x, 'def')
        C[C[int]].x = 'changed'
        self.assertEqual(C.x, 'changed')
        self.assertEqual(C[str].x, 'changed')
        C[List[str]].z = 'new'
        self.assertEqual(C.z, 'new')
        self.assertEqual(C[Tuple[int]].z, 'new')

        self.assertEqual(C().x, 'changed')
        self.assertEqual(C[Tuple[str]]().z, 'new')

        kundi D(C[T]):
            pass
        self.assertEqual(D[int].x, 'changed')
        self.assertEqual(D.z, 'new')
        D.z = 'kutoka derived z'
        D[int].x = 'kutoka derived x'
        self.assertEqual(C.x, 'changed')
        self.assertEqual(C[int].z, 'new')
        self.assertEqual(D.x, 'kutoka derived x')
        self.assertEqual(D[str].z, 'kutoka derived z')

    eleza test_abc_registry_kept(self):
        T = TypeVar('T')
        kundi C(collections.abc.Mapping, Generic[T]): ...
        C.register(int)
        self.assertIsInstance(1, C)
        C[int]
        self.assertIsInstance(1, C)
        C._abc_registry_clear()
        C._abc_caches_clear()  # To keep refleak hunting mode clean

    eleza test_false_subclasses(self):
        kundi MyMapping(MutableMapping[str, str]): pass
        self.assertNotIsInstance({}, MyMapping)
        self.assertNotIsSubclass(dict, MyMapping)

    eleza test_abc_bases(self):
        kundi MM(MutableMapping[str, str]):
            eleza __getitem__(self, k):
                rudisha Tupu
            eleza __setitem__(self, k, v):
                pass
            eleza __delitem__(self, k):
                pass
            eleza __iter__(self):
                rudisha iter(())
            eleza __len__(self):
                rudisha 0
        # this should just work
        MM().update()
        self.assertIsInstance(MM(), collections.abc.MutableMapping)
        self.assertIsInstance(MM(), MutableMapping)
        self.assertNotIsInstance(MM(), List)
        self.assertNotIsInstance({}, MM)

    eleza test_multiple_bases(self):
        kundi MM1(MutableMapping[str, str], collections.abc.MutableMapping):
            pass
        kundi MM2(collections.abc.MutableMapping, MutableMapping[str, str]):
            pass
        self.assertEqual(MM2.__bases__, (collections.abc.MutableMapping, Generic))

    eleza test_orig_bases(self):
        T = TypeVar('T')
        kundi C(typing.Dict[str, T]): ...
        self.assertEqual(C.__orig_bases__, (typing.Dict[str, T],))

    eleza test_naive_runtime_checks(self):
        eleza naive_dict_check(obj, tp):
            # Check ikiwa a dictionary conforms to Dict type
            ikiwa len(tp.__parameters__) > 0:
                 ashiria NotImplementedError
            ikiwa tp.__args__:
                KT, VT = tp.__args__
                rudisha all(
                    isinstance(k, KT) na isinstance(v, VT)
                    kila k, v kwenye obj.items()
                )
        self.assertKweli(naive_dict_check({'x': 1}, typing.Dict[str, int]))
        self.assertUongo(naive_dict_check({1: 'x'}, typing.Dict[str, int]))
        ukijumuisha self.assertRaises(NotImplementedError):
            naive_dict_check({1: 'x'}, typing.Dict[str, T])

        eleza naive_generic_check(obj, tp):
            # Check ikiwa an instance conforms to the generic class
            ikiwa sio hasattr(obj, '__orig_class__'):
                 ashiria NotImplementedError
            rudisha obj.__orig_class__ == tp
        kundi Node(Generic[T]): ...
        self.assertKweli(naive_generic_check(Node[int](), Node[int]))
        self.assertUongo(naive_generic_check(Node[str](), Node[int]))
        self.assertUongo(naive_generic_check(Node[str](), List))
        ukijumuisha self.assertRaises(NotImplementedError):
            naive_generic_check([1, 2, 3], Node[int])

        eleza naive_list_base_check(obj, tp):
            # Check ikiwa list conforms to a List subclass
            rudisha all(isinstance(x, tp.__orig_bases__[0].__args__[0])
                       kila x kwenye obj)
        kundi C(List[int]): ...
        self.assertKweli(naive_list_base_check([1, 2, 3], C))
        self.assertUongo(naive_list_base_check(['a', 'b'], C))

    eleza test_multi_subscr_base(self):
        T = TypeVar('T')
        U = TypeVar('U')
        V = TypeVar('V')
        kundi C(List[T][U][V]): ...
        kundi D(C, List[T][U][V]): ...
        self.assertEqual(C.__parameters__, (V,))
        self.assertEqual(D.__parameters__, (V,))
        self.assertEqual(C[int].__parameters__, ())
        self.assertEqual(D[int].__parameters__, ())
        self.assertEqual(C[int].__args__, (int,))
        self.assertEqual(D[int].__args__, (int,))
        self.assertEqual(C.__bases__, (list, Generic))
        self.assertEqual(D.__bases__, (C, list, Generic))
        self.assertEqual(C.__orig_bases__, (List[T][U][V],))
        self.assertEqual(D.__orig_bases__, (C, List[T][U][V]))

    eleza test_subscript_meta(self):
        T = TypeVar('T')
        kundi Meta(type): ...
        self.assertEqual(Type[Meta], Type[Meta])
        self.assertEqual(Union[T, int][Meta], Union[Meta, int])
        self.assertEqual(Callable[..., Meta].__args__, (Ellipsis, Meta))

    eleza test_generic_hashes(self):
        kundi A(Generic[T]):
            ...

        kundi B(Generic[T]):
            kundi A(Generic[T]):
                ...

        self.assertEqual(A, A)
        self.assertEqual(mod_generics_cache.A[str], mod_generics_cache.A[str])
        self.assertEqual(B.A, B.A)
        self.assertEqual(mod_generics_cache.B.A[B.A[str]],
                         mod_generics_cache.B.A[B.A[str]])

        self.assertNotEqual(A, B.A)
        self.assertNotEqual(A, mod_generics_cache.A)
        self.assertNotEqual(A, mod_generics_cache.B.A)
        self.assertNotEqual(B.A, mod_generics_cache.A)
        self.assertNotEqual(B.A, mod_generics_cache.B.A)

        self.assertNotEqual(A[str], B.A[str])
        self.assertNotEqual(A[List[Any]], B.A[List[Any]])
        self.assertNotEqual(A[str], mod_generics_cache.A[str])
        self.assertNotEqual(A[str], mod_generics_cache.B.A[str])
        self.assertNotEqual(B.A[int], mod_generics_cache.A[int])
        self.assertNotEqual(B.A[List[Any]], mod_generics_cache.B.A[List[Any]])

        self.assertNotEqual(Tuple[A[str]], Tuple[B.A[str]])
        self.assertNotEqual(Tuple[A[List[Any]]], Tuple[B.A[List[Any]]])
        self.assertNotEqual(Union[str, A[str]], Union[str, mod_generics_cache.A[str]])
        self.assertNotEqual(Union[A[str], A[str]],
                            Union[A[str], mod_generics_cache.A[str]])
        self.assertNotEqual(typing.FrozenSet[A[str]],
                            typing.FrozenSet[mod_generics_cache.B.A[str]])

        ikiwa sys.version_info[:2] > (3, 2):
            self.assertKweli(repr(Tuple[A[str]]).endswith('<locals>.A[str]]'))
            self.assertKweli(repr(Tuple[B.A[str]]).endswith('<locals>.B.A[str]]'))
            self.assertKweli(repr(Tuple[mod_generics_cache.A[str]])
                            .endswith('mod_generics_cache.A[str]]'))
            self.assertKweli(repr(Tuple[mod_generics_cache.B.A[str]])
                            .endswith('mod_generics_cache.B.A[str]]'))

    eleza test_extended_generic_rules_eq(self):
        T = TypeVar('T')
        U = TypeVar('U')
        self.assertEqual(Tuple[T, T][int], Tuple[int, int])
        self.assertEqual(typing.Iterable[Tuple[T, T]][T], typing.Iterable[Tuple[T, T]])
        ukijumuisha self.assertRaises(TypeError):
            Tuple[T, int][()]
        ukijumuisha self.assertRaises(TypeError):
            Tuple[T, U][T, ...]

        self.assertEqual(Union[T, int][int], int)
        self.assertEqual(Union[T, U][int, Union[int, str]], Union[int, str])
        kundi Base: ...
        kundi Derived(Base): ...
        self.assertEqual(Union[T, Base][Union[Base, Derived]], Union[Base, Derived])
        ukijumuisha self.assertRaises(TypeError):
            Union[T, int][1]

        self.assertEqual(Callable[[T], T][KT], Callable[[KT], KT])
        self.assertEqual(Callable[..., List[T]][int], Callable[..., List[int]])
        ukijumuisha self.assertRaises(TypeError):
            Callable[[T], U][..., int]
        ukijumuisha self.assertRaises(TypeError):
            Callable[[T], U][[], int]

    eleza test_extended_generic_rules_repr(self):
        T = TypeVar('T')
        self.assertEqual(repr(Union[Tuple, Callable]).replace('typing.', ''),
                         'Union[Tuple, Callable]')
        self.assertEqual(repr(Union[Tuple, Tuple[int]]).replace('typing.', ''),
                         'Union[Tuple, Tuple[int]]')
        self.assertEqual(repr(Callable[..., Optional[T]][int]).replace('typing.', ''),
                         'Callable[..., Union[int, TupuType]]')
        self.assertEqual(repr(Callable[[], List[T]][int]).replace('typing.', ''),
                         'Callable[[], List[int]]')

    eleza test_generic_forward_ref(self):
        eleza foobar(x: List[List['CC']]): ...
        kundi CC: ...
        self.assertEqual(
            get_type_hints(foobar, globals(), locals()),
            {'x': List[List[CC]]}
        )
        T = TypeVar('T')
        AT = Tuple[T, ...]
        eleza barfoo(x: AT): ...
        self.assertIs(get_type_hints(barfoo, globals(), locals())['x'], AT)
        CT = Callable[..., List[T]]
        eleza barfoo2(x: CT): ...
        self.assertIs(get_type_hints(barfoo2, globals(), locals())['x'], CT)

    eleza test_extended_generic_rules_subclassing(self):
        kundi T1(Tuple[T, KT]): ...
        kundi T2(Tuple[T, ...]): ...
        kundi C1(Callable[[T], T]): ...
        kundi C2(Callable[..., int]):
            eleza __call__(self):
                rudisha Tupu

        self.assertEqual(T1.__parameters__, (T, KT))
        self.assertEqual(T1[int, str].__args__, (int, str))
        self.assertEqual(T1[int, T].__origin__, T1)

        self.assertEqual(T2.__parameters__, (T,))
        ukijumuisha self.assertRaises(TypeError):
            T1[int]
        ukijumuisha self.assertRaises(TypeError):
            T2[int, str]

        self.assertEqual(repr(C1[int]).split('.')[-1], 'C1[int]')
        self.assertEqual(C2.__parameters__, ())
        self.assertIsInstance(C2(), collections.abc.Callable)
        self.assertIsSubclass(C2, collections.abc.Callable)
        self.assertIsSubclass(C1, collections.abc.Callable)
        self.assertIsInstance(T1(), tuple)
        self.assertIsSubclass(T2, tuple)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(Tuple[int, ...], typing.Sequence)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(Tuple[int, ...], typing.Iterable)

    eleza test_fail_with_bare_union(self):
        ukijumuisha self.assertRaises(TypeError):
            List[Union]
        ukijumuisha self.assertRaises(TypeError):
            Tuple[Optional]
        ukijumuisha self.assertRaises(TypeError):
            ClassVar[ClassVar]
        ukijumuisha self.assertRaises(TypeError):
            List[ClassVar[int]]

    eleza test_fail_with_bare_generic(self):
        T = TypeVar('T')
        ukijumuisha self.assertRaises(TypeError):
            List[Generic]
        ukijumuisha self.assertRaises(TypeError):
            Tuple[Generic[T]]
        ukijumuisha self.assertRaises(TypeError):
            List[typing.Protocol]

    eleza test_type_erasure_special(self):
        T = TypeVar('T')
        # this ni the only test that checks type caching
        self.clear_caches()
        kundi MyTup(Tuple[T, T]): ...
        self.assertIs(MyTup[int]().__class__, MyTup)
        self.assertIs(MyTup[int]().__orig_class__, MyTup[int])
        kundi MyCall(Callable[..., T]):
            eleza __call__(self): rudisha Tupu
        self.assertIs(MyCall[T]().__class__, MyCall)
        self.assertIs(MyCall[T]().__orig_class__, MyCall[T])
        kundi MyDict(typing.Dict[T, T]): ...
        self.assertIs(MyDict[int]().__class__, MyDict)
        self.assertIs(MyDict[int]().__orig_class__, MyDict[int])
        kundi MyDef(typing.DefaultDict[str, T]): ...
        self.assertIs(MyDef[int]().__class__, MyDef)
        self.assertIs(MyDef[int]().__orig_class__, MyDef[int])
        # ChainMap was added kwenye 3.3
        ikiwa sys.version_info >= (3, 3):
            kundi MyChain(typing.ChainMap[str, T]): ...
            self.assertIs(MyChain[int]().__class__, MyChain)
            self.assertIs(MyChain[int]().__orig_class__, MyChain[int])

    eleza test_all_repr_eq_any(self):
        objs = (getattr(typing, el) kila el kwenye typing.__all__)
        kila obj kwenye objs:
            self.assertNotEqual(repr(obj), '')
            self.assertEqual(obj, obj)
            ikiwa getattr(obj, '__parameters__', Tupu) na len(obj.__parameters__) == 1:
                self.assertEqual(obj[Any].__args__, (Any,))
            ikiwa isinstance(obj, type):
                kila base kwenye obj.__mro__:
                    self.assertNotEqual(repr(base), '')
                    self.assertEqual(base, base)

    eleza test_pickle(self):
        global C  # pickle wants to reference the kundi by name
        T = TypeVar('T')

        kundi B(Generic[T]):
            pass

        kundi C(B[int]):
            pass

        c = C()
        c.foo = 42
        c.bar = 'abc'
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            z = pickle.dumps(c, proto)
            x = pickle.loads(z)
            self.assertEqual(x.foo, 42)
            self.assertEqual(x.bar, 'abc')
            self.assertEqual(x.__dict__, {'foo': 42, 'bar': 'abc'})
        samples = [Any, Union, Tuple, Callable, ClassVar,
                   Union[int, str], ClassVar[List], Tuple[int, ...], Callable[[str], bytes],
                   typing.DefaultDict, typing.FrozenSet[int]]
        kila s kwenye samples:
            kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                z = pickle.dumps(s, proto)
                x = pickle.loads(z)
                self.assertEqual(s, x)
        more_samples = [List, typing.Iterable, typing.Type, List[int],
                        typing.Type[typing.Mapping], typing.AbstractSet[Tuple[int, str]]]
        kila s kwenye more_samples:
            kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                z = pickle.dumps(s, proto)
                x = pickle.loads(z)
                self.assertEqual(s, x)

    eleza test_copy_and_deepcopy(self):
        T = TypeVar('T')
        kundi Node(Generic[T]): ...
        things = [Union[T, int], Tuple[T, int], Callable[..., T], Callable[[int], int],
                  Tuple[Any, Any], Node[T], Node[int], Node[Any], typing.Iterable[T],
                  typing.Iterable[Any], typing.Iterable[int], typing.Dict[int, str],
                  typing.Dict[T, Any], ClassVar[int], ClassVar[List[T]], Tuple['T', 'T'],
                  Union['T', int], List['T'], typing.Mapping['T', int]]
        kila t kwenye things + [Any]:
            self.assertEqual(t, copy(t))
            self.assertEqual(t, deepcopy(t))

    eleza test_immutability_by_copy_and_pickle(self):
        # Special forms like Union, Any, etc., generic aliases to containers like List,
        # Mapping, etc., na type variabcles are considered immutable by copy na pickle.
        global TP, TPB, TPV  # kila pickle
        TP = TypeVar('TP')
        TPB = TypeVar('TPB', bound=int)
        TPV = TypeVar('TPV', bytes, str)
        kila X kwenye [TP, TPB, TPV, List, typing.Mapping, ClassVar, typing.Iterable,
                  Union, Any, Tuple, Callable]:
            self.assertIs(copy(X), X)
            self.assertIs(deepcopy(X), X)
            self.assertIs(pickle.loads(pickle.dumps(X)), X)
        # Check that local type variables are copyable.
        TL = TypeVar('TL')
        TLB = TypeVar('TLB', bound=int)
        TLV = TypeVar('TLV', bytes, str)
        kila X kwenye [TL, TLB, TLV]:
            self.assertIs(copy(X), X)
            self.assertIs(deepcopy(X), X)

    eleza test_copy_generic_instances(self):
        T = TypeVar('T')
        kundi C(Generic[T]):
            eleza __init__(self, attr: T) -> Tupu:
                self.attr = attr

        c = C(42)
        self.assertEqual(copy(c).attr, 42)
        self.assertEqual(deepcopy(c).attr, 42)
        self.assertIsNot(copy(c), c)
        self.assertIsNot(deepcopy(c), c)
        c.attr = 1
        self.assertEqual(copy(c).attr, 1)
        self.assertEqual(deepcopy(c).attr, 1)
        ci = C[int](42)
        self.assertEqual(copy(ci).attr, 42)
        self.assertEqual(deepcopy(ci).attr, 42)
        self.assertIsNot(copy(ci), ci)
        self.assertIsNot(deepcopy(ci), ci)
        ci.attr = 1
        self.assertEqual(copy(ci).attr, 1)
        self.assertEqual(deepcopy(ci).attr, 1)
        self.assertEqual(ci.__orig_class__, C[int])

    eleza test_weakref_all(self):
        T = TypeVar('T')
        things = [Any, Union[T, int], Callable[..., T], Tuple[Any, Any],
                  Optional[List[int]], typing.Mapping[int, str],
                  typing.re.Match[bytes], typing.Iterable['whatever']]
        kila t kwenye things:
            self.assertEqual(weakref.ref(t)(), t)

    eleza test_parameterized_slots(self):
        T = TypeVar('T')
        kundi C(Generic[T]):
            __slots__ = ('potato',)

        c = C()
        c_int = C[int]()

        c.potato = 0
        c_int.potato = 0
        ukijumuisha self.assertRaises(AttributeError):
            c.tomato = 0
        ukijumuisha self.assertRaises(AttributeError):
            c_int.tomato = 0

        eleza foo(x: C['C']): ...
        self.assertEqual(get_type_hints(foo, globals(), locals())['x'], C[C])
        self.assertEqual(copy(C[int]), deepcopy(C[int]))

    eleza test_parameterized_slots_dict(self):
        T = TypeVar('T')
        kundi D(Generic[T]):
            __slots__ = {'banana': 42}

        d = D()
        d_int = D[int]()

        d.banana = 'yes'
        d_int.banana = 'yes'
        ukijumuisha self.assertRaises(AttributeError):
            d.foobar = 'no'
        ukijumuisha self.assertRaises(AttributeError):
            d_int.foobar = 'no'

    eleza test_errors(self):
        ukijumuisha self.assertRaises(TypeError):
            B = SimpleMapping[XK, Any]

            kundi C(Generic[B]):
                pass

    eleza test_repr_2(self):
        kundi C(Generic[T]):
            pass

        self.assertEqual(C.__module__, __name__)
        self.assertEqual(C.__qualname__,
                         'GenericTests.test_repr_2.<locals>.C')
        X = C[int]
        self.assertEqual(X.__module__, __name__)
        self.assertEqual(repr(X).split('.')[-1], 'C[int]')

        kundi Y(C[int]):
            pass

        self.assertEqual(Y.__module__, __name__)
        self.assertEqual(Y.__qualname__,
                         'GenericTests.test_repr_2.<locals>.Y')

    eleza test_eq_1(self):
        self.assertEqual(Generic, Generic)
        self.assertEqual(Generic[T], Generic[T])
        self.assertNotEqual(Generic[KT], Generic[VT])

    eleza test_eq_2(self):

        kundi A(Generic[T]):
            pass

        kundi B(Generic[T]):
            pass

        self.assertEqual(A, A)
        self.assertNotEqual(A, B)
        self.assertEqual(A[T], A[T])
        self.assertNotEqual(A[T], B[T])

    eleza test_multiple_inheritance(self):

        kundi A(Generic[T, VT]):
            pass

        kundi B(Generic[KT, T]):
            pass

        kundi C(A[T, VT], Generic[VT, T, KT], B[KT, T]):
            pass

        self.assertEqual(C.__parameters__, (VT, T, KT))

    eleza test_multiple_inheritance_special(self):
        S = TypeVar('S')
        kundi B(Generic[S]): ...
        kundi C(List[int], B): ...
        self.assertEqual(C.__mro__, (C, list, B, Generic, object))

    eleza test_init_subclass_super_called(self):
        kundi FinalException(Exception):
            pass

        kundi Final:
            eleza __init_subclass__(cls, **kwargs) -> Tupu:
                kila base kwenye cls.__bases__:
                    ikiwa base ni sio Final na issubclass(base, Final):
                         ashiria FinalException(base)
                super().__init_subclass__(**kwargs)
        kundi Test(Generic[T], Final):
            pass
        ukijumuisha self.assertRaises(FinalException):
            kundi Subclass(Test):
                pass
        ukijumuisha self.assertRaises(FinalException):
            kundi Subclass(Test[int]):
                pass

    eleza test_nested(self):

        G = Generic

        kundi Visitor(G[T]):

            a = Tupu

            eleza set(self, a: T):
                self.a = a

            eleza get(self):
                rudisha self.a

            eleza visit(self) -> T:
                rudisha self.a

        V = Visitor[typing.List[int]]

        kundi IntListVisitor(V):

            eleza append(self, x: int):
                self.a.append(x)

        a = IntListVisitor()
        a.set([])
        a.append(1)
        a.append(42)
        self.assertEqual(a.get(), [1, 42])

    eleza test_type_erasure(self):
        T = TypeVar('T')

        kundi Node(Generic[T]):
            eleza __init__(self, label: T,
                         left: 'Node[T]' = Tupu,
                         right: 'Node[T]' = Tupu):
                self.label = label  # type: T
                self.left = left  # type: Optional[Node[T]]
                self.right = right  # type: Optional[Node[T]]

        eleza foo(x: T):
            a = Node(x)
            b = Node[T](x)
            c = Node[Any](x)
            self.assertIs(type(a), Node)
            self.assertIs(type(b), Node)
            self.assertIs(type(c), Node)
            self.assertEqual(a.label, x)
            self.assertEqual(b.label, x)
            self.assertEqual(c.label, x)

        foo(42)

    eleza test_implicit_any(self):
        T = TypeVar('T')

        kundi C(Generic[T]):
            pass

        kundi D(C):
            pass

        self.assertEqual(D.__parameters__, ())

        ukijumuisha self.assertRaises(Exception):
            D[int]
        ukijumuisha self.assertRaises(Exception):
            D[Any]
        ukijumuisha self.assertRaises(Exception):
            D[T]

    eleza test_new_with_args(self):

        kundi A(Generic[T]):
            pass

        kundi B:
            eleza __new__(cls, arg):
                # call object
                obj = super().__new__(cls)
                obj.arg = arg
                rudisha obj

        # mro: C, A, Generic, B, object
        kundi C(A, B):
            pass

        c = C('foo')
        self.assertEqual(c.arg, 'foo')

    eleza test_new_with_args2(self):

        kundi A:
            eleza __init__(self, arg):
                self.from_a = arg
                # call object
                super().__init__()

        # mro: C, Generic, A, object
        kundi C(Generic[T], A):
            eleza __init__(self, arg):
                self.from_c = arg
                # call Generic
                super().__init__(arg)

        c = C('foo')
        self.assertEqual(c.from_a, 'foo')
        self.assertEqual(c.from_c, 'foo')

    eleza test_new_no_args(self):

        kundi A(Generic[T]):
            pass

        ukijumuisha self.assertRaises(TypeError):
            A('foo')

        kundi B:
            eleza __new__(cls):
                # call object
                obj = super().__new__(cls)
                obj.from_b = 'b'
                rudisha obj

        # mro: C, A, Generic, B, object
        kundi C(A, B):
            eleza __init__(self, arg):
                self.arg = arg

            eleza __new__(cls, arg):
                # call A
                obj = super().__new__(cls)
                obj.from_c = 'c'
                rudisha obj

        c = C('foo')
        self.assertEqual(c.arg, 'foo')
        self.assertEqual(c.from_b, 'b')
        self.assertEqual(c.from_c, 'c')


kundi ClassVarTests(BaseTestCase):

    eleza test_basics(self):
        ukijumuisha self.assertRaises(TypeError):
            ClassVar[1]
        ukijumuisha self.assertRaises(TypeError):
            ClassVar[int, str]
        ukijumuisha self.assertRaises(TypeError):
            ClassVar[int][str]

    eleza test_repr(self):
        self.assertEqual(repr(ClassVar), 'typing.ClassVar')
        cv = ClassVar[int]
        self.assertEqual(repr(cv), 'typing.ClassVar[int]')
        cv = ClassVar[Employee]
        self.assertEqual(repr(cv), 'typing.ClassVar[%s.Employee]' % __name__)

    eleza test_cannot_subclass(self):
        ukijumuisha self.assertRaises(TypeError):
            kundi C(type(ClassVar)):
                pass
        ukijumuisha self.assertRaises(TypeError):
            kundi C(type(ClassVar[int])):
                pass

    eleza test_cannot_init(self):
        ukijumuisha self.assertRaises(TypeError):
            ClassVar()
        ukijumuisha self.assertRaises(TypeError):
            type(ClassVar)()
        ukijumuisha self.assertRaises(TypeError):
            type(ClassVar[Optional[int]])()

    eleza test_no_isinstance(self):
        ukijumuisha self.assertRaises(TypeError):
            isinstance(1, ClassVar[int])
        ukijumuisha self.assertRaises(TypeError):
            issubclass(int, ClassVar)


kundi FinalTests(BaseTestCase):

    eleza test_basics(self):
        Final[int]  # OK
        ukijumuisha self.assertRaises(TypeError):
            Final[1]
        ukijumuisha self.assertRaises(TypeError):
            Final[int, str]
        ukijumuisha self.assertRaises(TypeError):
            Final[int][str]
        ukijumuisha self.assertRaises(TypeError):
            Optional[Final[int]]

    eleza test_repr(self):
        self.assertEqual(repr(Final), 'typing.Final')
        cv = Final[int]
        self.assertEqual(repr(cv), 'typing.Final[int]')
        cv = Final[Employee]
        self.assertEqual(repr(cv), 'typing.Final[%s.Employee]' % __name__)

    eleza test_cannot_subclass(self):
        ukijumuisha self.assertRaises(TypeError):
            kundi C(type(Final)):
                pass
        ukijumuisha self.assertRaises(TypeError):
            kundi C(type(Final[int])):
                pass

    eleza test_cannot_init(self):
        ukijumuisha self.assertRaises(TypeError):
            Final()
        ukijumuisha self.assertRaises(TypeError):
            type(Final)()
        ukijumuisha self.assertRaises(TypeError):
            type(Final[Optional[int]])()

    eleza test_no_isinstance(self):
        ukijumuisha self.assertRaises(TypeError):
            isinstance(1, Final[int])
        ukijumuisha self.assertRaises(TypeError):
            issubclass(int, Final)

    eleza test_final_unmodified(self):
        eleza func(x): ...
        self.assertIs(func, final(func))


kundi CastTests(BaseTestCase):

    eleza test_basics(self):
        self.assertEqual(cast(int, 42), 42)
        self.assertEqual(cast(float, 42), 42)
        self.assertIs(type(cast(float, 42)), int)
        self.assertEqual(cast(Any, 42), 42)
        self.assertEqual(cast(list, 42), 42)
        self.assertEqual(cast(Union[str, float], 42), 42)
        self.assertEqual(cast(AnyStr, 42), 42)
        self.assertEqual(cast(Tupu, 42), 42)

    eleza test_errors(self):
        # Bogus calls are sio expected to fail.
        cast(42, 42)
        cast('hello', 42)


kundi ForwardRefTests(BaseTestCase):

    eleza test_basics(self):

        kundi Node(Generic[T]):

            eleza __init__(self, label: T):
                self.label = label
                self.left = self.right = Tupu

            eleza add_both(self,
                         left: 'Optional[Node[T]]',
                         right: 'Node[T]' = Tupu,
                         stuff: int = Tupu,
                         blah=Tupu):
                self.left = left
                self.right = right

            eleza add_left(self, node: Optional['Node[T]']):
                self.add_both(node, Tupu)

            eleza add_right(self, node: 'Node[T]' = Tupu):
                self.add_both(Tupu, node)

        t = Node[int]
        both_hints = get_type_hints(t.add_both, globals(), locals())
        self.assertEqual(both_hints['left'], Optional[Node[T]])
        self.assertEqual(both_hints['right'], Optional[Node[T]])
        self.assertEqual(both_hints['left'], both_hints['right'])
        self.assertEqual(both_hints['stuff'], Optional[int])
        self.assertNotIn('blah', both_hints)

        left_hints = get_type_hints(t.add_left, globals(), locals())
        self.assertEqual(left_hints['node'], Optional[Node[T]])

        right_hints = get_type_hints(t.add_right, globals(), locals())
        self.assertEqual(right_hints['node'], Optional[Node[T]])

    eleza test_forwardref_instance_type_error(self):
        fr = typing.ForwardRef('int')
        ukijumuisha self.assertRaises(TypeError):
            isinstance(42, fr)

    eleza test_forwardref_subclass_type_error(self):
        fr = typing.ForwardRef('int')
        ukijumuisha self.assertRaises(TypeError):
            issubclass(int, fr)

    eleza test_forward_equality(self):
        fr = typing.ForwardRef('int')
        self.assertEqual(fr, typing.ForwardRef('int'))
        self.assertNotEqual(List['int'], List[int])

    eleza test_forward_equality_gth(self):
        c1 = typing.ForwardRef('C')
        c1_gth = typing.ForwardRef('C')
        c2 = typing.ForwardRef('C')
        c2_gth = typing.ForwardRef('C')

        kundi C:
            pass
        eleza foo(a: c1_gth, b: c2_gth):
            pass

        self.assertEqual(get_type_hints(foo, globals(), locals()), {'a': C, 'b': C})
        self.assertEqual(c1, c2)
        self.assertEqual(c1, c1_gth)
        self.assertEqual(c1_gth, c2_gth)
        self.assertEqual(List[c1], List[c1_gth])
        self.assertNotEqual(List[c1], List[C])
        self.assertNotEqual(List[c1_gth], List[C])
        self.assertEqual(Union[c1, c1_gth], Union[c1])
        self.assertEqual(Union[c1, c1_gth, int], Union[c1, int])

    eleza test_forward_equality_hash(self):
        c1 = typing.ForwardRef('int')
        c1_gth = typing.ForwardRef('int')
        c2 = typing.ForwardRef('int')
        c2_gth = typing.ForwardRef('int')

        eleza foo(a: c1_gth, b: c2_gth):
            pass
        get_type_hints(foo, globals(), locals())

        self.assertEqual(hash(c1), hash(c2))
        self.assertEqual(hash(c1_gth), hash(c2_gth))
        self.assertEqual(hash(c1), hash(c1_gth))

    eleza test_forward_equality_namespace(self):
        kundi A:
            pass
        eleza namespace1():
            a = typing.ForwardRef('A')
            eleza fun(x: a):
                pass
            get_type_hints(fun, globals(), locals())
            rudisha a

        eleza namespace2():
            a = typing.ForwardRef('A')

            kundi A:
                pass
            eleza fun(x: a):
                pass

            get_type_hints(fun, globals(), locals())
            rudisha a

        self.assertEqual(namespace1(), namespace1())
        self.assertNotEqual(namespace1(), namespace2())

    eleza test_forward_repr(self):
        self.assertEqual(repr(List['int']), "typing.List[ForwardRef('int')]")

    eleza test_union_forward(self):

        eleza foo(a: Union['T']):
            pass

        self.assertEqual(get_type_hints(foo, globals(), locals()),
                         {'a': Union[T]})

    eleza test_tuple_forward(self):

        eleza foo(a: Tuple['T']):
            pass

        self.assertEqual(get_type_hints(foo, globals(), locals()),
                         {'a': Tuple[T]})

    eleza test_forward_recursion_actually(self):
        eleza namespace1():
            a = typing.ForwardRef('A')
            A = a
            eleza fun(x: a): pass

            ret = get_type_hints(fun, globals(), locals())
            rudisha a

        eleza namespace2():
            a = typing.ForwardRef('A')
            A = a
            eleza fun(x: a): pass

            ret = get_type_hints(fun, globals(), locals())
            rudisha a

        eleza cmp(o1, o2):
            rudisha o1 == o2

        r1 = namespace1()
        r2 = namespace2()
        self.assertIsNot(r1, r2)
        self.assertRaises(RecursionError, cmp, r1, r2)

    eleza test_union_forward_recursion(self):
        ValueList = List['Value']
        Value = Union[str, ValueList]

        kundi C:
            foo: List[Value]
        kundi D:
            foo: Union[Value, ValueList]
        kundi E:
            foo: Union[List[Value], ValueList]
        kundi F:
            foo: Union[Value, List[Value], ValueList]

        self.assertEqual(get_type_hints(C, globals(), locals()), get_type_hints(C, globals(), locals()))
        self.assertEqual(get_type_hints(C, globals(), locals()),
                         {'foo': List[Union[str, List[Union[str, List['Value']]]]]})
        self.assertEqual(get_type_hints(D, globals(), locals()),
                         {'foo': Union[str, List[Union[str, List['Value']]]]})
        self.assertEqual(get_type_hints(E, globals(), locals()),
                         {'foo': Union[
                             List[Union[str, List[Union[str, List['Value']]]]],
                             List[Union[str, List['Value']]]
                         ]
                          })
        self.assertEqual(get_type_hints(F, globals(), locals()),
                         {'foo': Union[
                             str,
                             List[Union[str, List['Value']]],
                             List[Union[str, List[Union[str, List['Value']]]]]
                         ]
                          })

    eleza test_callable_forward(self):

        eleza foo(a: Callable[['T'], 'T']):
            pass

        self.assertEqual(get_type_hints(foo, globals(), locals()),
                         {'a': Callable[[T], T]})

    eleza test_callable_with_ellipsis_forward(self):

        eleza foo(a: 'Callable[..., T]'):
            pass

        self.assertEqual(get_type_hints(foo, globals(), locals()),
                         {'a': Callable[..., T]})

    eleza test_syntax_error(self):

        ukijumuisha self.assertRaises(SyntaxError):
            Generic['/T']

    eleza test_delayed_syntax_error(self):

        eleza foo(a: 'Node[T'):
            pass

        ukijumuisha self.assertRaises(SyntaxError):
            get_type_hints(foo)

    eleza test_type_error(self):

        eleza foo(a: Tuple['42']):
            pass

        ukijumuisha self.assertRaises(TypeError):
            get_type_hints(foo)

    eleza test_name_error(self):

        eleza foo(a: 'Noode[T]'):
            pass

        ukijumuisha self.assertRaises(NameError):
            get_type_hints(foo, locals())

    eleza test_no_type_check(self):

        @no_type_check
        eleza foo(a: 'whatevers') -> {}:
            pass

        th = get_type_hints(foo)
        self.assertEqual(th, {})

    eleza test_no_type_check_class(self):

        @no_type_check
        kundi C:
            eleza foo(a: 'whatevers') -> {}:
                pass

        cth = get_type_hints(C.foo)
        self.assertEqual(cth, {})
        ith = get_type_hints(C().foo)
        self.assertEqual(ith, {})

    eleza test_no_type_check_no_bases(self):
        kundi C:
            eleza meth(self, x: int): ...
        @no_type_check
        kundi D(C):
            c = C
        # verify that @no_type_check never affects bases
        self.assertEqual(get_type_hints(C.meth), {'x': int})

    eleza test_no_type_check_forward_ref_as_string(self):
        kundi C:
            foo: typing.ClassVar[int] = 7
        kundi D:
            foo: ClassVar[int] = 7
        kundi E:
            foo: 'typing.ClassVar[int]' = 7
        kundi F:
            foo: 'ClassVar[int]' = 7

        expected_result = {'foo': typing.ClassVar[int]}
        kila clazz kwenye [C, D, E, F]:
            self.assertEqual(get_type_hints(clazz), expected_result)

    eleza test_nested_classvar_fails_forward_ref_check(self):
        kundi E:
            foo: 'typing.ClassVar[typing.ClassVar[int]]' = 7
        kundi F:
            foo: ClassVar['ClassVar[int]'] = 7

        kila clazz kwenye [E, F]:
            ukijumuisha self.assertRaises(TypeError):
                get_type_hints(clazz)

    eleza test_meta_no_type_check(self):

        @no_type_check_decorator
        eleza magic_decorator(func):
            rudisha func

        self.assertEqual(magic_decorator.__name__, 'magic_decorator')

        @magic_decorator
        eleza foo(a: 'whatevers') -> {}:
            pass

        @magic_decorator
        kundi C:
            eleza foo(a: 'whatevers') -> {}:
                pass

        self.assertEqual(foo.__name__, 'foo')
        th = get_type_hints(foo)
        self.assertEqual(th, {})
        cth = get_type_hints(C.foo)
        self.assertEqual(cth, {})
        ith = get_type_hints(C().foo)
        self.assertEqual(ith, {})

    eleza test_default_globals(self):
        code = ("kundi C:\n"
                "    eleza foo(self, a: 'C') -> 'D': pass\n"
                "kundi D:\n"
                "    eleza bar(self, b: 'D') -> C: pass\n"
                )
        ns = {}
        exec(code, ns)
        hints = get_type_hints(ns['C'].foo)
        self.assertEqual(hints, {'a': ns['C'], 'return': ns['D']})

    eleza test_final_forward_ref(self):
        self.assertEqual(gth(Loop, globals())['attr'], Final[Loop])
        self.assertNotEqual(gth(Loop, globals())['attr'], Final[int])
        self.assertNotEqual(gth(Loop, globals())['attr'], Final)


kundi OverloadTests(BaseTestCase):

    eleza test_overload_fails(self):
        kutoka typing agiza overload

        ukijumuisha self.assertRaises(RuntimeError):

            @overload
            eleza blah():
                pass

            blah()

    eleza test_overload_succeeds(self):
        kutoka typing agiza overload

        @overload
        eleza blah():
            pass

        eleza blah():
            pass

        blah()


ASYNCIO_TESTS = """
agiza asyncio

T_a = TypeVar('T_a')

kundi AwaitableWrapper(typing.Awaitable[T_a]):

    eleza __init__(self, value):
        self.value = value

    eleza __await__(self) -> typing.Iterator[T_a]:
        yield
        rudisha self.value

kundi AsyncIteratorWrapper(typing.AsyncIterator[T_a]):

    eleza __init__(self, value: typing.Iterable[T_a]):
        self.value = value

    eleza __aiter__(self) -> typing.AsyncIterator[T_a]:
        rudisha self

    async eleza __anext__(self) -> T_a:
        data = await self.value
        ikiwa data:
            rudisha data
        isipokua:
             ashiria StopAsyncIteration

kundi ACM:
    async eleza __aenter__(self) -> int:
        rudisha 42
    async eleza __aexit__(self, etype, eval, tb):
        rudisha Tupu
"""

jaribu:
    exec(ASYNCIO_TESTS)
except ImportError:
    ASYNCIO = Uongo  # multithreading ni sio enabled
isipokua:
    ASYNCIO = Kweli

# Definitions needed kila features introduced kwenye Python 3.6

kutoka test agiza ann_module, ann_module2, ann_module3
kutoka typing agiza AsyncContextManager

kundi A:
    y: float
kundi B(A):
    x: ClassVar[Optional['B']] = Tupu
    y: int
    b: int
kundi CSub(B):
    z: ClassVar['CSub'] = B()
kundi G(Generic[T]):
    lst: ClassVar[List[T]] = []

kundi Loop:
    attr: Final['Loop']

kundi TupuAndForward:
    parent: 'TupuAndForward'
    meaning: Tupu

kundi CoolEmployee(NamedTuple):
    name: str
    cool: int

kundi CoolEmployeeWithDefault(NamedTuple):
    name: str
    cool: int = 0

kundi XMeth(NamedTuple):
    x: int
    eleza double(self):
        rudisha 2 * self.x

kundi XRepr(NamedTuple):
    x: int
    y: int = 1
    eleza __str__(self):
        rudisha f'{self.x} -> {self.y}'
    eleza __add__(self, other):
        rudisha 0

Label = TypedDict('Label', [('label', str)])

kundi Point2D(TypedDict):
    x: int
    y: int

kundi LabelPoint2D(Point2D, Label): ...

kundi Options(TypedDict, total=Uongo):
    log_level: int
    log_path: str

kundi HasForeignBaseClass(mod_generics_cache.A):
    some_xrepr: 'XRepr'
    other_a: 'mod_generics_cache.A'

async eleza g_with(am: AsyncContextManager[int]):
    x: int
    async ukijumuisha am as x:
        rudisha x

jaribu:
    g_with(ACM()).send(Tupu)
except StopIteration as e:
    assert e.args[0] == 42

gth = get_type_hints


kundi GetTypeHintTests(BaseTestCase):
    eleza test_get_type_hints_from_various_objects(self):
        # For invalid objects should fail ukijumuisha TypeError (not AttributeError etc).
        ukijumuisha self.assertRaises(TypeError):
            gth(123)
        ukijumuisha self.assertRaises(TypeError):
            gth('abc')
        ukijumuisha self.assertRaises(TypeError):
            gth(Tupu)

    eleza test_get_type_hints_modules(self):
        ann_module_type_hints = {1: 2, 'f': Tuple[int, int], 'x': int, 'y': str}
        self.assertEqual(gth(ann_module), ann_module_type_hints)
        self.assertEqual(gth(ann_module2), {})
        self.assertEqual(gth(ann_module3), {})

    @skip("known bug")
    eleza test_get_type_hints_modules_forwardref(self):
        # FIXME: This currently exposes a bug kwenye typing. Cached forward references
        # don't account kila the case where there are multiple types of the same
        # name coming kutoka different modules kwenye the same program.
        mgc_hints = {'default_a': Optional[mod_generics_cache.A],
                     'default_b': Optional[mod_generics_cache.B]}
        self.assertEqual(gth(mod_generics_cache), mgc_hints)

    eleza test_get_type_hints_classes(self):
        self.assertEqual(gth(ann_module.C),  # gth will find the right globalns
                         {'y': Optional[ann_module.C]})
        self.assertIsInstance(gth(ann_module.j_class), dict)
        self.assertEqual(gth(ann_module.M), {'123': 123, 'o': type})
        self.assertEqual(gth(ann_module.D),
                         {'j': str, 'k': str, 'y': Optional[ann_module.C]})
        self.assertEqual(gth(ann_module.Y), {'z': int})
        self.assertEqual(gth(ann_module.h_class),
                         {'y': Optional[ann_module.C]})
        self.assertEqual(gth(ann_module.S), {'x': str, 'y': str})
        self.assertEqual(gth(ann_module.foo), {'x': int})
        self.assertEqual(gth(TupuAndForward),
                         {'parent': TupuAndForward, 'meaning': type(Tupu)})
        self.assertEqual(gth(HasForeignBaseClass),
                         {'some_xrepr': XRepr, 'other_a': mod_generics_cache.A,
                          'some_b': mod_generics_cache.B})
        self.assertEqual(gth(XRepr.__new__),
                         {'x': int, 'y': int})
        self.assertEqual(gth(mod_generics_cache.B),
                         {'my_inner_a1': mod_generics_cache.B.A,
                          'my_inner_a2': mod_generics_cache.B.A,
                          'my_outer_a': mod_generics_cache.A})

    eleza test_respect_no_type_check(self):
        @no_type_check
        kundi NoTpCheck:
            kundi Inn:
                eleza __init__(self, x: 'not a type'): ...
        self.assertKweli(NoTpCheck.__no_type_check__)
        self.assertKweli(NoTpCheck.Inn.__init__.__no_type_check__)
        self.assertEqual(gth(ann_module2.NTC.meth), {})
        kundi ABase(Generic[T]):
            eleza meth(x: int): ...
        @no_type_check
        kundi Der(ABase): ...
        self.assertEqual(gth(ABase.meth), {'x': int})

    eleza test_get_type_hints_for_builtins(self):
        # Should sio fail kila built-in classes na functions.
        self.assertEqual(gth(int), {})
        self.assertEqual(gth(type), {})
        self.assertEqual(gth(dir), {})
        self.assertEqual(gth(len), {})
        self.assertEqual(gth(object.__str__), {})
        self.assertEqual(gth(object().__str__), {})
        self.assertEqual(gth(str.join), {})

    eleza test_previous_behavior(self):
        eleza testf(x, y): ...
        testf.__annotations__['x'] = 'int'
        self.assertEqual(gth(testf), {'x': int})
        eleza testg(x: Tupu): ...
        self.assertEqual(gth(testg), {'x': type(Tupu)})

    eleza test_get_type_hints_for_object_with_annotations(self):
        kundi A: ...
        kundi B: ...
        b = B()
        b.__annotations__ = {'x': 'A'}
        self.assertEqual(gth(b, locals()), {'x': A})

    eleza test_get_type_hints_ClassVar(self):
        self.assertEqual(gth(ann_module2.CV, ann_module2.__dict__),
                         {'var': typing.ClassVar[ann_module2.CV]})
        self.assertEqual(gth(B, globals()),
                         {'y': int, 'x': ClassVar[Optional[B]], 'b': int})
        self.assertEqual(gth(CSub, globals()),
                         {'z': ClassVar[CSub], 'y': int, 'b': int,
                          'x': ClassVar[Optional[B]]})
        self.assertEqual(gth(G), {'lst': ClassVar[List[T]]})


kundi GetUtilitiesTestCase(TestCase):
    eleza test_get_origin(self):
        T = TypeVar('T')
        kundi C(Generic[T]): pass
        self.assertIs(get_origin(C[int]), C)
        self.assertIs(get_origin(C[T]), C)
        self.assertIs(get_origin(int), Tupu)
        self.assertIs(get_origin(ClassVar[int]), ClassVar)
        self.assertIs(get_origin(Union[int, str]), Union)
        self.assertIs(get_origin(Literal[42, 43]), Literal)
        self.assertIs(get_origin(Final[List[int]]), Final)
        self.assertIs(get_origin(Generic), Generic)
        self.assertIs(get_origin(Generic[T]), Generic)
        self.assertIs(get_origin(List[Tuple[T, T]][int]), list)

    eleza test_get_args(self):
        T = TypeVar('T')
        kundi C(Generic[T]): pass
        self.assertEqual(get_args(C[int]), (int,))
        self.assertEqual(get_args(C[T]), (T,))
        self.assertEqual(get_args(int), ())
        self.assertEqual(get_args(ClassVar[int]), (int,))
        self.assertEqual(get_args(Union[int, str]), (int, str))
        self.assertEqual(get_args(Literal[42, 43]), (42, 43))
        self.assertEqual(get_args(Final[List[int]]), (List[int],))
        self.assertEqual(get_args(Union[int, Tuple[T, int]][str]),
                         (int, Tuple[str, int]))
        self.assertEqual(get_args(typing.Dict[int, Tuple[T, T]][Optional[int]]),
                         (int, Tuple[Optional[int], Optional[int]]))
        self.assertEqual(get_args(Callable[[], T][int]), ([], int,))
        self.assertEqual(get_args(Union[int, Callable[[Tuple[T, ...]], str]]),
                         (int, Callable[[Tuple[T, ...]], str]))
        self.assertEqual(get_args(Tuple[int, ...]), (int, ...))
        self.assertEqual(get_args(Tuple[()]), ((),))


kundi CollectionsAbcTests(BaseTestCase):

    eleza test_hashable(self):
        self.assertIsInstance(42, typing.Hashable)
        self.assertNotIsInstance([], typing.Hashable)

    eleza test_iterable(self):
        self.assertIsInstance([], typing.Iterable)
        # Due to ABC caching, the second time takes a separate code
        # path na could fail.  So call this a few times.
        self.assertIsInstance([], typing.Iterable)
        self.assertIsInstance([], typing.Iterable)
        self.assertNotIsInstance(42, typing.Iterable)
        # Just kwenye case, also test issubclass() a few times.
        self.assertIsSubclass(list, typing.Iterable)
        self.assertIsSubclass(list, typing.Iterable)

    eleza test_iterator(self):
        it = iter([])
        self.assertIsInstance(it, typing.Iterator)
        self.assertNotIsInstance(42, typing.Iterator)

    @skipUnless(ASYNCIO, 'Python 3.5 na multithreading required')
    eleza test_awaitable(self):
        ns = {}
        exec(
            "async eleza foo() -> typing.Awaitable[int]:\n"
            "    rudisha await AwaitableWrapper(42)\n",
            globals(), ns)
        foo = ns['foo']
        g = foo()
        self.assertIsInstance(g, typing.Awaitable)
        self.assertNotIsInstance(foo, typing.Awaitable)
        g.send(Tupu)  # Run foo() till completion, to avoid warning.

    @skipUnless(ASYNCIO, 'Python 3.5 na multithreading required')
    eleza test_coroutine(self):
        ns = {}
        exec(
            "async eleza foo():\n"
            "    return\n",
            globals(), ns)
        foo = ns['foo']
        g = foo()
        self.assertIsInstance(g, typing.Coroutine)
        ukijumuisha self.assertRaises(TypeError):
            isinstance(g, typing.Coroutine[int])
        self.assertNotIsInstance(foo, typing.Coroutine)
        jaribu:
            g.send(Tupu)
        except StopIteration:
            pass

    @skipUnless(ASYNCIO, 'Python 3.5 na multithreading required')
    eleza test_async_iterable(self):
        base_it = range(10)  # type: Iterator[int]
        it = AsyncIteratorWrapper(base_it)
        self.assertIsInstance(it, typing.AsyncIterable)
        self.assertIsInstance(it, typing.AsyncIterable)
        self.assertNotIsInstance(42, typing.AsyncIterable)

    @skipUnless(ASYNCIO, 'Python 3.5 na multithreading required')
    eleza test_async_iterator(self):
        base_it = range(10)  # type: Iterator[int]
        it = AsyncIteratorWrapper(base_it)
        self.assertIsInstance(it, typing.AsyncIterator)
        self.assertNotIsInstance(42, typing.AsyncIterator)

    eleza test_sized(self):
        self.assertIsInstance([], typing.Sized)
        self.assertNotIsInstance(42, typing.Sized)

    eleza test_container(self):
        self.assertIsInstance([], typing.Container)
        self.assertNotIsInstance(42, typing.Container)

    eleza test_collection(self):
        ikiwa hasattr(typing, 'Collection'):
            self.assertIsInstance(tuple(), typing.Collection)
            self.assertIsInstance(frozenset(), typing.Collection)
            self.assertIsSubclass(dict, typing.Collection)
            self.assertNotIsInstance(42, typing.Collection)

    eleza test_abstractset(self):
        self.assertIsInstance(set(), typing.AbstractSet)
        self.assertNotIsInstance(42, typing.AbstractSet)

    eleza test_mutableset(self):
        self.assertIsInstance(set(), typing.MutableSet)
        self.assertNotIsInstance(frozenset(), typing.MutableSet)

    eleza test_mapping(self):
        self.assertIsInstance({}, typing.Mapping)
        self.assertNotIsInstance(42, typing.Mapping)

    eleza test_mutablemapping(self):
        self.assertIsInstance({}, typing.MutableMapping)
        self.assertNotIsInstance(42, typing.MutableMapping)

    eleza test_sequence(self):
        self.assertIsInstance([], typing.Sequence)
        self.assertNotIsInstance(42, typing.Sequence)

    eleza test_mutablesequence(self):
        self.assertIsInstance([], typing.MutableSequence)
        self.assertNotIsInstance((), typing.MutableSequence)

    eleza test_bytestring(self):
        self.assertIsInstance(b'', typing.ByteString)
        self.assertIsInstance(bytearray(b''), typing.ByteString)

    eleza test_list(self):
        self.assertIsSubclass(list, typing.List)

    eleza test_deque(self):
        self.assertIsSubclass(collections.deque, typing.Deque)
        kundi MyDeque(typing.Deque[int]): ...
        self.assertIsInstance(MyDeque(), collections.deque)

    eleza test_counter(self):
        self.assertIsSubclass(collections.Counter, typing.Counter)

    eleza test_set(self):
        self.assertIsSubclass(set, typing.Set)
        self.assertNotIsSubclass(frozenset, typing.Set)

    eleza test_frozenset(self):
        self.assertIsSubclass(frozenset, typing.FrozenSet)
        self.assertNotIsSubclass(set, typing.FrozenSet)

    eleza test_dict(self):
        self.assertIsSubclass(dict, typing.Dict)

    eleza test_no_list_instantiation(self):
        ukijumuisha self.assertRaises(TypeError):
            typing.List()
        ukijumuisha self.assertRaises(TypeError):
            typing.List[T]()
        ukijumuisha self.assertRaises(TypeError):
            typing.List[int]()

    eleza test_list_subclass(self):

        kundi MyList(typing.List[int]):
            pass

        a = MyList()
        self.assertIsInstance(a, MyList)
        self.assertIsInstance(a, typing.Sequence)

        self.assertIsSubclass(MyList, list)
        self.assertNotIsSubclass(list, MyList)

    eleza test_no_dict_instantiation(self):
        ukijumuisha self.assertRaises(TypeError):
            typing.Dict()
        ukijumuisha self.assertRaises(TypeError):
            typing.Dict[KT, VT]()
        ukijumuisha self.assertRaises(TypeError):
            typing.Dict[str, int]()

    eleza test_dict_subclass(self):

        kundi MyDict(typing.Dict[str, int]):
            pass

        d = MyDict()
        self.assertIsInstance(d, MyDict)
        self.assertIsInstance(d, typing.MutableMapping)

        self.assertIsSubclass(MyDict, dict)
        self.assertNotIsSubclass(dict, MyDict)

    eleza test_defaultdict_instantiation(self):
        self.assertIs(type(typing.DefaultDict()), collections.defaultdict)
        self.assertIs(type(typing.DefaultDict[KT, VT]()), collections.defaultdict)
        self.assertIs(type(typing.DefaultDict[str, int]()), collections.defaultdict)

    eleza test_defaultdict_subclass(self):

        kundi MyDefDict(typing.DefaultDict[str, int]):
            pass

        dd = MyDefDict()
        self.assertIsInstance(dd, MyDefDict)

        self.assertIsSubclass(MyDefDict, collections.defaultdict)
        self.assertNotIsSubclass(collections.defaultdict, MyDefDict)

    eleza test_ordereddict_instantiation(self):
        self.assertIs(type(typing.OrderedDict()), collections.OrderedDict)
        self.assertIs(type(typing.OrderedDict[KT, VT]()), collections.OrderedDict)
        self.assertIs(type(typing.OrderedDict[str, int]()), collections.OrderedDict)

    eleza test_ordereddict_subclass(self):

        kundi MyOrdDict(typing.OrderedDict[str, int]):
            pass

        od = MyOrdDict()
        self.assertIsInstance(od, MyOrdDict)

        self.assertIsSubclass(MyOrdDict, collections.OrderedDict)
        self.assertNotIsSubclass(collections.OrderedDict, MyOrdDict)

    @skipUnless(sys.version_info >= (3, 3), 'ChainMap was added kwenye 3.3')
    eleza test_chainmap_instantiation(self):
        self.assertIs(type(typing.ChainMap()), collections.ChainMap)
        self.assertIs(type(typing.ChainMap[KT, VT]()), collections.ChainMap)
        self.assertIs(type(typing.ChainMap[str, int]()), collections.ChainMap)
        kundi CM(typing.ChainMap[KT, VT]): ...
        self.assertIs(type(CM[int, str]()), CM)

    @skipUnless(sys.version_info >= (3, 3), 'ChainMap was added kwenye 3.3')
    eleza test_chainmap_subclass(self):

        kundi MyChainMap(typing.ChainMap[str, int]):
            pass

        cm = MyChainMap()
        self.assertIsInstance(cm, MyChainMap)

        self.assertIsSubclass(MyChainMap, collections.ChainMap)
        self.assertNotIsSubclass(collections.ChainMap, MyChainMap)

    eleza test_deque_instantiation(self):
        self.assertIs(type(typing.Deque()), collections.deque)
        self.assertIs(type(typing.Deque[T]()), collections.deque)
        self.assertIs(type(typing.Deque[int]()), collections.deque)
        kundi D(typing.Deque[T]): ...
        self.assertIs(type(D[int]()), D)

    eleza test_counter_instantiation(self):
        self.assertIs(type(typing.Counter()), collections.Counter)
        self.assertIs(type(typing.Counter[T]()), collections.Counter)
        self.assertIs(type(typing.Counter[int]()), collections.Counter)
        kundi C(typing.Counter[T]): ...
        self.assertIs(type(C[int]()), C)

    eleza test_counter_subclass_instantiation(self):

        kundi MyCounter(typing.Counter[int]):
            pass

        d = MyCounter()
        self.assertIsInstance(d, MyCounter)
        self.assertIsInstance(d, typing.Counter)
        self.assertIsInstance(d, collections.Counter)

    eleza test_no_set_instantiation(self):
        ukijumuisha self.assertRaises(TypeError):
            typing.Set()
        ukijumuisha self.assertRaises(TypeError):
            typing.Set[T]()
        ukijumuisha self.assertRaises(TypeError):
            typing.Set[int]()

    eleza test_set_subclass_instantiation(self):

        kundi MySet(typing.Set[int]):
            pass

        d = MySet()
        self.assertIsInstance(d, MySet)

    eleza test_no_frozenset_instantiation(self):
        ukijumuisha self.assertRaises(TypeError):
            typing.FrozenSet()
        ukijumuisha self.assertRaises(TypeError):
            typing.FrozenSet[T]()
        ukijumuisha self.assertRaises(TypeError):
            typing.FrozenSet[int]()

    eleza test_frozenset_subclass_instantiation(self):

        kundi MyFrozenSet(typing.FrozenSet[int]):
            pass

        d = MyFrozenSet()
        self.assertIsInstance(d, MyFrozenSet)

    eleza test_no_tuple_instantiation(self):
        ukijumuisha self.assertRaises(TypeError):
            Tuple()
        ukijumuisha self.assertRaises(TypeError):
            Tuple[T]()
        ukijumuisha self.assertRaises(TypeError):
            Tuple[int]()

    eleza test_generator(self):
        eleza foo():
            tuma 42
        g = foo()
        self.assertIsSubclass(type(g), typing.Generator)

    eleza test_no_generator_instantiation(self):
        ukijumuisha self.assertRaises(TypeError):
            typing.Generator()
        ukijumuisha self.assertRaises(TypeError):
            typing.Generator[T, T, T]()
        ukijumuisha self.assertRaises(TypeError):
            typing.Generator[int, int, int]()

    eleza test_async_generator(self):
        ns = {}
        exec("async eleza f():\n"
             "    tuma 42\n", globals(), ns)
        g = ns['f']()
        self.assertIsSubclass(type(g), typing.AsyncGenerator)

    eleza test_no_async_generator_instantiation(self):
        ukijumuisha self.assertRaises(TypeError):
            typing.AsyncGenerator()
        ukijumuisha self.assertRaises(TypeError):
            typing.AsyncGenerator[T, T]()
        ukijumuisha self.assertRaises(TypeError):
            typing.AsyncGenerator[int, int]()

    eleza test_subclassing(self):

        kundi MMA(typing.MutableMapping):
            pass

        ukijumuisha self.assertRaises(TypeError):  # It's abstract
            MMA()

        kundi MMC(MMA):
            eleza __getitem__(self, k):
                rudisha Tupu
            eleza __setitem__(self, k, v):
                pass
            eleza __delitem__(self, k):
                pass
            eleza __iter__(self):
                rudisha iter(())
            eleza __len__(self):
                rudisha 0

        self.assertEqual(len(MMC()), 0)
        assert callable(MMC.update)
        self.assertIsInstance(MMC(), typing.Mapping)

        kundi MMB(typing.MutableMapping[KT, VT]):
            eleza __getitem__(self, k):
                rudisha Tupu
            eleza __setitem__(self, k, v):
                pass
            eleza __delitem__(self, k):
                pass
            eleza __iter__(self):
                rudisha iter(())
            eleza __len__(self):
                rudisha 0

        self.assertEqual(len(MMB()), 0)
        self.assertEqual(len(MMB[str, str]()), 0)
        self.assertEqual(len(MMB[KT, VT]()), 0)

        self.assertNotIsSubclass(dict, MMA)
        self.assertNotIsSubclass(dict, MMB)

        self.assertIsSubclass(MMA, typing.Mapping)
        self.assertIsSubclass(MMB, typing.Mapping)
        self.assertIsSubclass(MMC, typing.Mapping)

        self.assertIsInstance(MMB[KT, VT](), typing.Mapping)
        self.assertIsInstance(MMB[KT, VT](), collections.abc.Mapping)

        self.assertIsSubclass(MMA, collections.abc.Mapping)
        self.assertIsSubclass(MMB, collections.abc.Mapping)
        self.assertIsSubclass(MMC, collections.abc.Mapping)

        ukijumuisha self.assertRaises(TypeError):
            issubclass(MMB[str, str], typing.Mapping)
        self.assertIsSubclass(MMC, MMA)

        kundi I(typing.Iterable): ...
        self.assertNotIsSubclass(list, I)

        kundi G(typing.Generator[int, int, int]): ...
        eleza g(): tuma 0
        self.assertIsSubclass(G, typing.Generator)
        self.assertIsSubclass(G, typing.Iterable)
        self.assertIsSubclass(G, collections.abc.Generator)
        self.assertIsSubclass(G, collections.abc.Iterable)
        self.assertNotIsSubclass(type(g), G)

    eleza test_subclassing_async_generator(self):
        kundi G(typing.AsyncGenerator[int, int]):
            eleza asend(self, value):
                pass
            eleza athrow(self, typ, val=Tupu, tb=Tupu):
                pass

        ns = {}
        exec('async eleza g(): tuma 0', globals(), ns)
        g = ns['g']
        self.assertIsSubclass(G, typing.AsyncGenerator)
        self.assertIsSubclass(G, typing.AsyncIterable)
        self.assertIsSubclass(G, collections.abc.AsyncGenerator)
        self.assertIsSubclass(G, collections.abc.AsyncIterable)
        self.assertNotIsSubclass(type(g), G)

        instance = G()
        self.assertIsInstance(instance, typing.AsyncGenerator)
        self.assertIsInstance(instance, typing.AsyncIterable)
        self.assertIsInstance(instance, collections.abc.AsyncGenerator)
        self.assertIsInstance(instance, collections.abc.AsyncIterable)
        self.assertNotIsInstance(type(g), G)
        self.assertNotIsInstance(g, G)

    eleza test_subclassing_subclasshook(self):

        kundi Base(typing.Iterable):
            @classmethod
            eleza __subclasshook__(cls, other):
                ikiwa other.__name__ == 'Foo':
                    rudisha Kweli
                isipokua:
                    rudisha Uongo

        kundi C(Base): ...
        kundi Foo: ...
        kundi Bar: ...
        self.assertIsSubclass(Foo, Base)
        self.assertIsSubclass(Foo, C)
        self.assertNotIsSubclass(Bar, C)

    eleza test_subclassing_register(self):

        kundi A(typing.Container): ...
        kundi B(A): ...

        kundi C: ...
        A.register(C)
        self.assertIsSubclass(C, A)
        self.assertNotIsSubclass(C, B)

        kundi D: ...
        B.register(D)
        self.assertIsSubclass(D, A)
        self.assertIsSubclass(D, B)

        kundi M(): ...
        collections.abc.MutableMapping.register(M)
        self.assertIsSubclass(M, typing.Mapping)

    eleza test_collections_as_base(self):

        kundi M(collections.abc.Mapping): ...
        self.assertIsSubclass(M, typing.Mapping)
        self.assertIsSubclass(M, typing.Iterable)

        kundi S(collections.abc.MutableSequence): ...
        self.assertIsSubclass(S, typing.MutableSequence)
        self.assertIsSubclass(S, typing.Iterable)

        kundi I(collections.abc.Iterable): ...
        self.assertIsSubclass(I, typing.Iterable)

        kundi A(collections.abc.Mapping, metaclass=abc.ABCMeta): ...
        kundi B: ...
        A.register(B)
        self.assertIsSubclass(B, typing.Mapping)


kundi OtherABCTests(BaseTestCase):

    eleza test_contextmanager(self):
        @contextlib.contextmanager
        eleza manager():
            tuma 42

        cm = manager()
        self.assertIsInstance(cm, typing.ContextManager)
        self.assertNotIsInstance(42, typing.ContextManager)

    @skipUnless(ASYNCIO, 'Python 3.5 required')
    eleza test_async_contextmanager(self):
        kundi NotACM:
            pass
        self.assertIsInstance(ACM(), typing.AsyncContextManager)
        self.assertNotIsInstance(NotACM(), typing.AsyncContextManager)
        @contextlib.contextmanager
        eleza manager():
            tuma 42

        cm = manager()
        self.assertNotIsInstance(cm, typing.AsyncContextManager)
        self.assertEqual(typing.AsyncContextManager[int].__args__, (int,))
        ukijumuisha self.assertRaises(TypeError):
            isinstance(42, typing.AsyncContextManager[int])
        ukijumuisha self.assertRaises(TypeError):
            typing.AsyncContextManager[int, str]


kundi TypeTests(BaseTestCase):

    eleza test_type_basic(self):

        kundi User: pass
        kundi BasicUser(User): pass
        kundi ProUser(User): pass

        eleza new_user(user_class: Type[User]) -> User:
            rudisha user_class()

        new_user(BasicUser)

    eleza test_type_typevar(self):

        kundi User: pass
        kundi BasicUser(User): pass
        kundi ProUser(User): pass

        U = TypeVar('U', bound=User)

        eleza new_user(user_class: Type[U]) -> U:
            rudisha user_class()

        new_user(BasicUser)

    eleza test_type_optional(self):
        A = Optional[Type[BaseException]]

        eleza foo(a: A) -> Optional[BaseException]:
            ikiwa a ni Tupu:
                rudisha Tupu
            isipokua:
                rudisha a()

        assert isinstance(foo(KeyboardInterrupt), KeyboardInterrupt)
        assert foo(Tupu) ni Tupu


kundi NewTypeTests(BaseTestCase):

    eleza test_basic(self):
        UserId = NewType('UserId', int)
        UserName = NewType('UserName', str)
        self.assertIsInstance(UserId(5), int)
        self.assertIsInstance(UserName('Joe'), str)
        self.assertEqual(UserId(5) + 1, 6)

    eleza test_errors(self):
        UserId = NewType('UserId', int)
        UserName = NewType('UserName', str)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(UserId, int)
        ukijumuisha self.assertRaises(TypeError):
            kundi D(UserName):
                pass


kundi NamedTupleTests(BaseTestCase):
    kundi NestedEmployee(NamedTuple):
        name: str
        cool: int

    eleza test_basics(self):
        Emp = NamedTuple('Emp', [('name', str), ('id', int)])
        self.assertIsSubclass(Emp, tuple)
        joe = Emp('Joe', 42)
        jim = Emp(name='Jim', id=1)
        self.assertIsInstance(joe, Emp)
        self.assertIsInstance(joe, tuple)
        self.assertEqual(joe.name, 'Joe')
        self.assertEqual(joe.id, 42)
        self.assertEqual(jim.name, 'Jim')
        self.assertEqual(jim.id, 1)
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp._fields, ('name', 'id'))
        self.assertEqual(Emp.__annotations__,
                         collections.OrderedDict([('name', str), ('id', int)]))
        self.assertIs(Emp._field_types, Emp.__annotations__)

    eleza test_namedtuple_pyversion(self):
        ikiwa sys.version_info[:2] < (3, 6):
            ukijumuisha self.assertRaises(TypeError):
                NamedTuple('Name', one=int, other=str)
            ukijumuisha self.assertRaises(TypeError):
                kundi NotYet(NamedTuple):
                    whatever = 0

    eleza test_annotation_usage(self):
        tim = CoolEmployee('Tim', 9000)
        self.assertIsInstance(tim, CoolEmployee)
        self.assertIsInstance(tim, tuple)
        self.assertEqual(tim.name, 'Tim')
        self.assertEqual(tim.cool, 9000)
        self.assertEqual(CoolEmployee.__name__, 'CoolEmployee')
        self.assertEqual(CoolEmployee._fields, ('name', 'cool'))
        self.assertEqual(CoolEmployee.__annotations__,
                         collections.OrderedDict(name=str, cool=int))
        self.assertIs(CoolEmployee._field_types, CoolEmployee.__annotations__)

    eleza test_annotation_usage_with_default(self):
        jelle = CoolEmployeeWithDefault('Jelle')
        self.assertIsInstance(jelle, CoolEmployeeWithDefault)
        self.assertIsInstance(jelle, tuple)
        self.assertEqual(jelle.name, 'Jelle')
        self.assertEqual(jelle.cool, 0)
        cooler_employee = CoolEmployeeWithDefault('Sjoerd', 1)
        self.assertEqual(cooler_employee.cool, 1)

        self.assertEqual(CoolEmployeeWithDefault.__name__, 'CoolEmployeeWithDefault')
        self.assertEqual(CoolEmployeeWithDefault._fields, ('name', 'cool'))
        self.assertEqual(CoolEmployeeWithDefault._field_types, dict(name=str, cool=int))
        self.assertEqual(CoolEmployeeWithDefault._field_defaults, dict(cool=0))

        ukijumuisha self.assertRaises(TypeError):
            exec("""
kundi NonDefaultAfterDefault(NamedTuple):
    x: int = 3
    y: int
""")

    eleza test_annotation_usage_with_methods(self):
        self.assertEqual(XMeth(1).double(), 2)
        self.assertEqual(XMeth(42).x, XMeth(42)[0])
        self.assertEqual(str(XRepr(42)), '42 -> 1')
        self.assertEqual(XRepr(1, 2) + XRepr(3), 0)

        ukijumuisha self.assertRaises(AttributeError):
            exec("""
kundi XMethBad(NamedTuple):
    x: int
    eleza _fields(self):
        rudisha 'no chance kila this'
""")

        ukijumuisha self.assertRaises(AttributeError):
            exec("""
kundi XMethBad2(NamedTuple):
    x: int
    eleza _source(self):
        rudisha 'no chance kila this as well'
""")

    eleza test_namedtuple_keyword_usage(self):
        LocalEmployee = NamedTuple("LocalEmployee", name=str, age=int)
        nick = LocalEmployee('Nick', 25)
        self.assertIsInstance(nick, tuple)
        self.assertEqual(nick.name, 'Nick')
        self.assertEqual(LocalEmployee.__name__, 'LocalEmployee')
        self.assertEqual(LocalEmployee._fields, ('name', 'age'))
        self.assertEqual(LocalEmployee.__annotations__, dict(name=str, age=int))
        self.assertIs(LocalEmployee._field_types, LocalEmployee.__annotations__)
        ukijumuisha self.assertRaises(TypeError):
            NamedTuple('Name', [('x', int)], y=str)
        ukijumuisha self.assertRaises(TypeError):
            NamedTuple('Name', x=1, y='a')

    eleza test_namedtuple_special_keyword_names(self):
        NT = NamedTuple("NT", cls=type, self=object, typename=str, fields=list)
        self.assertEqual(NT.__name__, 'NT')
        self.assertEqual(NT._fields, ('cls', 'self', 'typename', 'fields'))
        a = NT(cls=str, self=42, typename='foo', fields=[('bar', tuple)])
        self.assertEqual(a.cls, str)
        self.assertEqual(a.self, 42)
        self.assertEqual(a.typename, 'foo')
        self.assertEqual(a.fields, [('bar', tuple)])

    eleza test_namedtuple_errors(self):
        ukijumuisha self.assertRaises(TypeError):
            NamedTuple.__new__()
        ukijumuisha self.assertRaises(TypeError):
            NamedTuple()
        ukijumuisha self.assertRaises(TypeError):
            NamedTuple('Emp', [('name', str)], Tupu)
        ukijumuisha self.assertRaises(ValueError):
            NamedTuple('Emp', [('_name', str)])

        ukijumuisha self.assertWarns(DeprecationWarning):
            Emp = NamedTuple(typename='Emp', name=str, id=int)
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp._fields, ('name', 'id'))

        ukijumuisha self.assertWarns(DeprecationWarning):
            Emp = NamedTuple('Emp', fields=[('name', str), ('id', int)])
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp._fields, ('name', 'id'))

    eleza test_copy_and_pickle(self):
        global Emp  # pickle wants to reference the kundi by name
        Emp = NamedTuple('Emp', [('name', str), ('cool', int)])
        kila cls kwenye Emp, CoolEmployee, self.NestedEmployee:
            ukijumuisha self.subTest(cls=cls):
                jane = cls('jane', 37)
                kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                    z = pickle.dumps(jane, proto)
                    jane2 = pickle.loads(z)
                    self.assertEqual(jane2, jane)
                    self.assertIsInstance(jane2, cls)

                jane2 = copy(jane)
                self.assertEqual(jane2, jane)
                self.assertIsInstance(jane2, cls)

                jane2 = deepcopy(jane)
                self.assertEqual(jane2, jane)
                self.assertIsInstance(jane2, cls)


kundi TypedDictTests(BaseTestCase):
    eleza test_basics_functional_syntax(self):
        Emp = TypedDict('Emp', {'name': str, 'id': int})
        self.assertIsSubclass(Emp, dict)
        self.assertIsSubclass(Emp, typing.MutableMapping)
        self.assertNotIsSubclass(Emp, collections.abc.Sequence)
        jim = Emp(name='Jim', id=1)
        self.assertIs(type(jim), dict)
        self.assertEqual(jim['name'], 'Jim')
        self.assertEqual(jim['id'], 1)
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp.__module__, __name__)
        self.assertEqual(Emp.__bases__, (dict,))
        self.assertEqual(Emp.__annotations__, {'name': str, 'id': int})
        self.assertEqual(Emp.__total__, Kweli)

    eleza test_basics_keywords_syntax(self):
        Emp = TypedDict('Emp', name=str, id=int)
        self.assertIsSubclass(Emp, dict)
        self.assertIsSubclass(Emp, typing.MutableMapping)
        self.assertNotIsSubclass(Emp, collections.abc.Sequence)
        jim = Emp(name='Jim', id=1)
        self.assertIs(type(jim), dict)
        self.assertEqual(jim['name'], 'Jim')
        self.assertEqual(jim['id'], 1)
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp.__module__, __name__)
        self.assertEqual(Emp.__bases__, (dict,))
        self.assertEqual(Emp.__annotations__, {'name': str, 'id': int})
        self.assertEqual(Emp.__total__, Kweli)

    eleza test_typeddict_special_keyword_names(self):
        TD = TypedDict("TD", cls=type, self=object, typename=str, _typename=int, fields=list, _fields=dict)
        self.assertEqual(TD.__name__, 'TD')
        self.assertEqual(TD.__annotations__, {'cls': type, 'self': object, 'typename': str, '_typename': int, 'fields': list, '_fields': dict})
        a = TD(cls=str, self=42, typename='foo', _typename=53, fields=[('bar', tuple)], _fields={'baz', set})
        self.assertEqual(a['cls'], str)
        self.assertEqual(a['self'], 42)
        self.assertEqual(a['typename'], 'foo')
        self.assertEqual(a['_typename'], 53)
        self.assertEqual(a['fields'], [('bar', tuple)])
        self.assertEqual(a['_fields'], {'baz', set})

    eleza test_typeddict_create_errors(self):
        ukijumuisha self.assertRaises(TypeError):
            TypedDict.__new__()
        ukijumuisha self.assertRaises(TypeError):
            TypedDict()
        ukijumuisha self.assertRaises(TypeError):
            TypedDict('Emp', [('name', str)], Tupu)
        ukijumuisha self.assertRaises(TypeError):
            TypedDict(_typename='Emp', name=str, id=int)
        ukijumuisha self.assertRaises(TypeError):
            TypedDict('Emp', _fields={'name': str, 'id': int})

    eleza test_typeddict_errors(self):
        Emp = TypedDict('Emp', {'name': str, 'id': int})
        self.assertEqual(TypedDict.__module__, 'typing')
        jim = Emp(name='Jim', id=1)
        ukijumuisha self.assertRaises(TypeError):
            isinstance({}, Emp)
        ukijumuisha self.assertRaises(TypeError):
            isinstance(jim, Emp)
        ukijumuisha self.assertRaises(TypeError):
            issubclass(dict, Emp)
        ukijumuisha self.assertRaises(TypeError):
            TypedDict('Hi', x=1)
        ukijumuisha self.assertRaises(TypeError):
            TypedDict('Hi', [('x', int), ('y', 1)])
        ukijumuisha self.assertRaises(TypeError):
            TypedDict('Hi', [('x', int)], y=int)

    eleza test_py36_class_syntax_usage(self):
        self.assertEqual(LabelPoint2D.__name__, 'LabelPoint2D')
        self.assertEqual(LabelPoint2D.__module__, __name__)
        self.assertEqual(LabelPoint2D.__annotations__, {'x': int, 'y': int, 'label': str})
        self.assertEqual(LabelPoint2D.__bases__, (dict,))
        self.assertEqual(LabelPoint2D.__total__, Kweli)
        self.assertNotIsSubclass(LabelPoint2D, typing.Sequence)
        not_origin = Point2D(x=0, y=1)
        self.assertEqual(not_origin['x'], 0)
        self.assertEqual(not_origin['y'], 1)
        other = LabelPoint2D(x=0, y=1, label='hi')
        self.assertEqual(other['label'], 'hi')

    eleza test_pickle(self):
        global EmpD  # pickle wants to reference the kundi by name
        EmpD = TypedDict('EmpD', name=str, id=int)
        jane = EmpD({'name': 'jane', 'id': 37})
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            z = pickle.dumps(jane, proto)
            jane2 = pickle.loads(z)
            self.assertEqual(jane2, jane)
            self.assertEqual(jane2, {'name': 'jane', 'id': 37})
            ZZ = pickle.dumps(EmpD, proto)
            EmpDnew = pickle.loads(ZZ)
            self.assertEqual(EmpDnew({'name': 'jane', 'id': 37}), jane)

    eleza test_optional(self):
        EmpD = TypedDict('EmpD', name=str, id=int)

        self.assertEqual(typing.Optional[EmpD], typing.Union[Tupu, EmpD])
        self.assertNotEqual(typing.List[EmpD], typing.Tuple[EmpD])

    eleza test_total(self):
        D = TypedDict('D', {'x': int}, total=Uongo)
        self.assertEqual(D(), {})
        self.assertEqual(D(x=1), {'x': 1})
        self.assertEqual(D.__total__, Uongo)

        self.assertEqual(Options(), {})
        self.assertEqual(Options(log_level=2), {'log_level': 2})
        self.assertEqual(Options.__total__, Uongo)


kundi IOTests(BaseTestCase):

    eleza test_io(self):

        eleza stuff(a: IO) -> AnyStr:
            rudisha a.readline()

        a = stuff.__annotations__['a']
        self.assertEqual(a.__parameters__, (AnyStr,))

    eleza test_textio(self):

        eleza stuff(a: TextIO) -> str:
            rudisha a.readline()

        a = stuff.__annotations__['a']
        self.assertEqual(a.__parameters__, ())

    eleza test_binaryio(self):

        eleza stuff(a: BinaryIO) -> bytes:
            rudisha a.readline()

        a = stuff.__annotations__['a']
        self.assertEqual(a.__parameters__, ())

    eleza test_io_submodule(self):
        kutoka typing.io agiza IO, TextIO, BinaryIO, __all__, __name__
        self.assertIs(IO, typing.IO)
        self.assertIs(TextIO, typing.TextIO)
        self.assertIs(BinaryIO, typing.BinaryIO)
        self.assertEqual(set(__all__), set(['IO', 'TextIO', 'BinaryIO']))
        self.assertEqual(__name__, 'typing.io')


kundi RETests(BaseTestCase):
    # Much of this ni really testing _TypeAlias.

    eleza test_basics(self):
        pat = re.compile('[a-z]+', re.I)
        self.assertIsSubclass(pat.__class__, Pattern)
        self.assertIsSubclass(type(pat), Pattern)
        self.assertIsInstance(pat, Pattern)

        mat = pat.search('12345abcde.....')
        self.assertIsSubclass(mat.__class__, Match)
        self.assertIsSubclass(type(mat), Match)
        self.assertIsInstance(mat, Match)

        # these should just work
        Pattern[Union[str, bytes]]
        Match[Union[bytes, str]]

    eleza test_alias_equality(self):
        self.assertEqual(Pattern[str], Pattern[str])
        self.assertNotEqual(Pattern[str], Pattern[bytes])
        self.assertNotEqual(Pattern[str], Match[str])
        self.assertNotEqual(Pattern[str], str)

    eleza test_errors(self):
        m = Match[Union[str, bytes]]
        ukijumuisha self.assertRaises(TypeError):
            m[str]
        ukijumuisha self.assertRaises(TypeError):
            # We don't support isinstance().
            isinstance(42, Pattern[str])
        ukijumuisha self.assertRaises(TypeError):
            # We don't support issubclass().
            issubclass(Pattern[bytes], Pattern[str])

    eleza test_repr(self):
        self.assertEqual(repr(Pattern), 'typing.Pattern')
        self.assertEqual(repr(Pattern[str]), 'typing.Pattern[str]')
        self.assertEqual(repr(Pattern[bytes]), 'typing.Pattern[bytes]')
        self.assertEqual(repr(Match), 'typing.Match')
        self.assertEqual(repr(Match[str]), 'typing.Match[str]')
        self.assertEqual(repr(Match[bytes]), 'typing.Match[bytes]')

    eleza test_re_submodule(self):
        kutoka typing.re agiza Match, Pattern, __all__, __name__
        self.assertIs(Match, typing.Match)
        self.assertIs(Pattern, typing.Pattern)
        self.assertEqual(set(__all__), set(['Match', 'Pattern']))
        self.assertEqual(__name__, 'typing.re')

    eleza test_cannot_subclass(self):
        ukijumuisha self.assertRaises(TypeError) as ex:

            kundi A(typing.Match):
                pass

        self.assertEqual(str(ex.exception),
                         "type 're.Match' ni sio an acceptable base type")


kundi AllTests(BaseTestCase):
    """Tests kila __all__."""

    eleza test_all(self):
        kutoka typing agiza __all__ as a
        # Just spot-check the first na last of every category.
        self.assertIn('AbstractSet', a)
        self.assertIn('ValuesView', a)
        self.assertIn('cast', a)
        self.assertIn('overload', a)
        ikiwa hasattr(contextlib, 'AbstractContextManager'):
            self.assertIn('ContextManager', a)
        # Check that io na re are sio exported.
        self.assertNotIn('io', a)
        self.assertNotIn('re', a)
        # Spot-check that stdlib modules aren't exported.
        self.assertNotIn('os', a)
        self.assertNotIn('sys', a)
        # Check that Text ni defined.
        self.assertIn('Text', a)
        # Check previously missing classes.
        self.assertIn('SupportsBytes', a)
        self.assertIn('SupportsComplex', a)

    eleza test_all_exported_names(self):
        agiza typing

        actual_all = set(typing.__all__)
        computed_all = {
            k kila k, v kwenye vars(typing).items()
            # explicitly exported, sio a thing ukijumuisha __module__
            ikiwa k kwenye actual_all ama (
                # avoid private names
                sio k.startswith('_') and
                # avoid things kwenye the io / re typing submodules
                k sio kwenye typing.io.__all__ and
                k sio kwenye typing.re.__all__ and
                k sio kwenye {'io', 're'} and
                # there's a few types na metaclasses that aren't exported
                sio k.endswith(('Meta', '_contra', '_co')) and
                sio k.upper() == k and
                # but export all things that have __module__ == 'typing'
                getattr(v, '__module__', Tupu) == typing.__name__
            )
        }
        self.assertSetEqual(computed_all, actual_all)



ikiwa __name__ == '__main__':
    main()
