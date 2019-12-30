# Reference cycles involving only the ob_type field are rather uncommon
# but possible.  Inspired by SF bug 1469629.

agiza gc

eleza leak():
    kundi T(type):
        pass
    kundi U(type, metaclass=T):
        pass
    U.__class__ = U
    toa U
    gc.collect(); gc.collect(); gc.collect()
