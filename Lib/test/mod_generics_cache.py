"""Module for testing the behavior of generics across different modules."""

agiza sys
kutoka textwrap agiza dedent
kutoka typing agiza TypeVar, Generic, Optional


ikiwa sys.version_info[:2] >= (3, 6):
    exec(dedent("""
    default_a: Optional['A'] = None
    default_b: Optional['B'] = None

    T = TypeVar('T')


    kundi A(Generic[T]):
        some_b: 'B'


    kundi B(Generic[T]):
        kundi A(Generic[T]):
            pass

        my_inner_a1: 'B.A'
        my_inner_a2: A
        my_outer_a: 'A'  # unless somebody calls get_type_hints with localns=B.__dict__
    """))
else:  # This should stay in sync with the syntax above.
    __annotations__ = dict(
        default_a=Optional['A'],
        default_b=Optional['B'],
    )
    default_a = None
    default_b = None

    T = TypeVar('T')


    kundi A(Generic[T]):
        __annotations__ = dict(
            some_b='B'
        )


    kundi B(Generic[T]):
        kundi A(Generic[T]):
            pass

        __annotations__ = dict(
            my_inner_a1='B.A',
            my_inner_a2=A,
            my_outer_a='A'  # unless somebody calls get_type_hints with localns=B.__dict__
        )
