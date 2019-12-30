kundi Delegator:

    eleza __init__(self, delegate=Tupu):
        self.delegate = delegate
        self.__cache = set()
        # Cache ni used to only remove added attributes
        # when changing the delegate.

    eleza __getattr__(self, name):
        attr = getattr(self.delegate, name) # May ashiria AttributeError
        setattr(self, name, attr)
        self.__cache.add(name)
        rudisha attr

    eleza resetcache(self):
        "Removes added attributes wakati leaving original attributes."
        # Function ni really about resetting delegator dict
        # to original state.  Cache ni just a means
        kila key kwenye self.__cache:
            jaribu:
                delattr(self, key)
            tatizo AttributeError:
                pita
        self.__cache.clear()

    eleza setdelegate(self, delegate):
        "Reset attributes na change delegate."
        self.resetcache()
        self.delegate = delegate

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_delegator', verbosity=2)
