agiza gc

thingy = object()
kundi A(object):
    eleza f(self):
        rudisha 1
    x = thingy

r = gc.get_referrers(thingy)
ikiwa "__module__" kwenye r[0]:
    dct = r[0]
isipokua:
    dct = r[1]

a = A()
kila i kwenye range(10):
    a.f()
dct["f"] = lambda self: 2

andika(a.f()) # should andika 1
