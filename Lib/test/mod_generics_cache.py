"""Module kila testing the behavior of generics across different modules."""

agiza sys
kutoka textwrap agiza dedent
kutoka typing agiza TypeVar, Generic, Optional


ikiwa sys.version_info[:2] >= (3, 6):
    exec(dedent("""
    default_a: Optional['A'] = Tupu
    default_b: Optional['B'] = Tupu

    T = TypeVar('T')


    kundi A(Generic[T]):
        some_b: 'B'


    kundi B(Generic[T]):
        kundi A(Generic[T]):
            pita

        my_inner_a1: 'B.A'
        my_inner_a2: A
        my_outer_a: 'A'  # unless somebody calls get_type_hints ukijumuisha localns=B.__dict__
    """))
isipokua:  # This should stay kwenye sync ukijumuisha the syntax above.
    __annotations__ = dict(
        default_a=Optional['A'],
        default_b=Optional['B'],
    )
    default_a = Tupu
    default_b = Tupu

    T = TypeVar('T')


    kundi A(Generic[T]):
        __annotations__ = dict(
            some_b='B'
        )


    kundi B(Generic[T]):
        kundi A(Generic[T]):
            pita

        __annotations__ = dict(
            my_inner_a1='B.A',
            my_inner_a2=A,
            my_outer_a='A'  # unless somebody calls get_type_hints ukijumuisha localns=B.__dict__
        )
