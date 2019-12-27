"""
Some correct syntax for variable annotation here.
More examples are in test_grammar and test_parser.
"""

kutoka typing agiza no_type_check, ClassVar

i: int = 1
j: int
x: float = i/10

eleza f():
    kundi C: ...
    rudisha C()

f().new_attr: object = object()

kundi C:
    eleza __init__(self, x: int) -> None:
        self.x = x

c = C(5)
c.new_attr: int = 10

__annotations__ = {}


@no_type_check
kundi NTC:
    eleza meth(self, param: complex) -> None:
        ...

kundi CV:
    var: ClassVar['CV']

CV.var = CV()
