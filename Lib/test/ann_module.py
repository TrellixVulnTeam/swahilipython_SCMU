

"""
The module for testing variable annotations.
Empty lines above are for good reason (testing for correct line numbers)
"""

kutoka typing agiza Optional

__annotations__[1] = 2

kundi C:

    x = 5; y: Optional['C'] = None

kutoka typing agiza Tuple
x: int = 5; y: str = x; f: Tuple[int, int]

kundi M(type):

    __annotations__['123'] = 123
    o: type = object

(pars): bool = True

kundi D(C):
    j: str = 'hi'; k: str= 'bye'

kutoka types agiza new_class
h_kundi = new_class('H', (C,))
j_kundi = new_class('J')

kundi F():
    z: int = 5
    eleza __init__(self, x):
        pass

kundi Y(F):
    eleza __init__(self):
        super(F, self).__init__(123)

kundi Meta(type):
    eleza __new__(meta, name, bases, namespace):
        rudisha super().__new__(meta, name, bases, namespace)

kundi S(metakundi = Meta):
    x: str = 'something'
    y: str = 'something else'

eleza foo(x: int = 10):
    eleza bar(y: List[str]):
        x: str = 'yes'
    bar()
