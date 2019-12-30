kutoka multiprocessing agiza freeze_support
kutoka multiprocessing.managers agiza BaseManager, BaseProxy
agiza operator

##

kundi Foo:
    eleza f(self):
        andika('you called Foo.f()')
    eleza g(self):
        andika('you called Foo.g()')
    eleza _h(self):
        andika('you called Foo._h()')

# A simple generator function
eleza baz():
    kila i kwenye range(10):
        tuma i*i

# Proxy type kila generator objects
kundi GeneratorProxy(BaseProxy):
    _exposed_ = ['__next__']
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
        rudisha self._callmethod('__next__')

# Function to rudisha the operator module
eleza get_operator_module():
    rudisha operator

##

kundi MyManager(BaseManager):
    pita

# register the Foo class; make `f()` na `g()` accessible via proxy
MyManager.register('Foo1', Foo)

# register the Foo class; make `g()` na `_h()` accessible via proxy
MyManager.register('Foo2', Foo, exposed=('g', '_h'))

# register the generator function baz; use `GeneratorProxy` to make proxies
MyManager.register('baz', baz, proxytype=GeneratorProxy)

# register get_operator_module(); make public functions accessible via proxy
MyManager.register('operator', get_operator_module)

##

eleza test():
    manager = MyManager()
    manager.start()

    andika('-' * 20)

    f1 = manager.Foo1()
    f1.f()
    f1.g()
    assert sio hasattr(f1, '_h')
    assert sorted(f1._exposed_) == sorted(['f', 'g'])

    andika('-' * 20)

    f2 = manager.Foo2()
    f2.g()
    f2._h()
    assert sio hasattr(f2, 'f')
    assert sorted(f2._exposed_) == sorted(['g', '_h'])

    andika('-' * 20)

    it = manager.baz()
    kila i kwenye it:
        andika('<%d>' % i, end=' ')
    andika()

    andika('-' * 20)

    op = manager.operator()
    andika('op.add(23, 45) =', op.add(23, 45))
    andika('op.pow(2, 94) =', op.pow(2, 94))
    andika('op._exposed_ =', op._exposed_)

##

ikiwa __name__ == '__main__':
    freeze_support()
    test()
