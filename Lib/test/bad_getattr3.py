eleza __getattr__(name):
    ikiwa name != 'delgetattr':
        raise AttributeError
    del globals()['__getattr__']
    raise AttributeError
