"""
Some correct syntax kila variable annotation here.
More examples are kwenye test_grammar na test_parser.
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
    eleza __init__(self, x: int) -> Tupu:
        self.x = x

c = C(5)
c.new_attr: int = 10

__annotations__ = {}


@no_type_check
kundi NTC:
    eleza meth(self, param: complex) -> Tupu:
        ...

kundi CV:
    var: ClassVar['CV']

CV.var = CV()
