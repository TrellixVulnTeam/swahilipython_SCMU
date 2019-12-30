kutoka _weakrefset agiza WeakSet


eleza get_cache_token():
    """Returns the current ABC cache token.

    The token ni an opaque object (supporting equality testing) identifying the
    current version of the ABC cache kila virtual subclasses. The token changes
    ukijumuisha every call to ``register()`` on any ABC.
    """
    rudisha ABCMeta._abc_invalidation_counter


kundi ABCMeta(type):
    """Metakundi kila defining Abstract Base Classes (ABCs).

    Use this metakundi to create an ABC.  An ABC can be subclassed
    directly, na then acts as a mix-in class.  You can also register
    unrelated concrete classes (even built-in classes) na unrelated
    ABCs as 'virtual subclasses' -- these na their descendants will
    be considered subclasses of the registering ABC by the built-in
    issubclass() function, but the registering ABC won't show up in
    their MRO (Method Resolution Order) nor will method
    implementations defined by the registering ABC be callable (not
    even via super()).
    """

    # A global counter that ni incremented each time a kundi is
    # registered as a virtual subkundi of anything.  It forces the
    # negative cache to be cleared before its next use.
    # Note: this counter ni private. Use `abc.get_cache_token()` for
    #       external code.
    _abc_invalidation_counter = 0

    eleza __new__(mcls, name, bases, namespace, /, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        # Compute set of abstract method names
        abstracts = {name
                     kila name, value kwenye namespace.items()
                     ikiwa getattr(value, "__isabstractmethod__", Uongo)}
        kila base kwenye bases:
            kila name kwenye getattr(base, "__abstractmethods__", set()):
                value = getattr(cls, name, Tupu)
                ikiwa getattr(value, "__isabstractmethod__", Uongo):
                    abstracts.add(name)
        cls.__abstractmethods__ = frozenset(abstracts)
        # Set up inheritance registry
        cls._abc_registry = WeakSet()
        cls._abc_cache = WeakSet()
        cls._abc_negative_cache = WeakSet()
        cls._abc_negative_cache_version = ABCMeta._abc_invalidation_counter
        rudisha cls

    eleza register(cls, subclass):
        """Register a virtual subkundi of an ABC.

        Returns the subclass, to allow usage as a kundi decorator.
        """
        ikiwa sio isinstance(subclass, type):
             ashiria TypeError("Can only register classes")
        ikiwa issubclass(subclass, cls):
            rudisha subkundi  # Already a subclass
        # Subtle: test kila cycles *after* testing kila "already a subclass";
        # this means we allow X.register(X) na interpret it as a no-op.
        ikiwa issubclass(cls, subclass):
            # This would create a cycle, which ni bad kila the algorithm below
             ashiria RuntimeError("Refusing to create an inheritance cycle")
        cls._abc_registry.add(subclass)
        ABCMeta._abc_invalidation_counter += 1  # Invalidate negative cache
        rudisha subclass

    eleza _dump_registry(cls, file=Tupu):
        """Debug helper to print the ABC registry."""
        andika(f"Class: {cls.__module__}.{cls.__qualname__}", file=file)
        andika(f"Inv. counter: {get_cache_token()}", file=file)
        kila name kwenye cls.__dict__:
            ikiwa name.startswith("_abc_"):
                value = getattr(cls, name)
                ikiwa isinstance(value, WeakSet):
                    value = set(value)
                andika(f"{name}: {value!r}", file=file)

    eleza _abc_registry_clear(cls):
        """Clear the registry (kila debugging ama testing)."""
        cls._abc_registry.clear()

    eleza _abc_caches_clear(cls):
        """Clear the caches (kila debugging ama testing)."""
        cls._abc_cache.clear()
        cls._abc_negative_cache.clear()

    eleza __instancecheck__(cls, instance):
        """Override kila isinstance(instance, cls)."""
        # Inline the cache checking
        subkundi = instance.__class__
        ikiwa subkundi kwenye cls._abc_cache:
            rudisha Kweli
        subtype = type(instance)
        ikiwa subtype ni subclass:
            ikiwa (cls._abc_negative_cache_version ==
                ABCMeta._abc_invalidation_counter and
                subkundi kwenye cls._abc_negative_cache):
                rudisha Uongo
            # Fall back to the subkundi check.
            rudisha cls.__subclasscheck__(subclass)
        rudisha any(cls.__subclasscheck__(c) kila c kwenye (subclass, subtype))

    eleza __subclasscheck__(cls, subclass):
        """Override kila issubclass(subclass, cls)."""
        ikiwa sio isinstance(subclass, type):
             ashiria TypeError('issubclass() arg 1 must be a class')
        # Check cache
        ikiwa subkundi kwenye cls._abc_cache:
            rudisha Kweli
        # Check negative cache; may have to invalidate
        ikiwa cls._abc_negative_cache_version < ABCMeta._abc_invalidation_counter:
            # Invalidate the negative cache
            cls._abc_negative_cache = WeakSet()
            cls._abc_negative_cache_version = ABCMeta._abc_invalidation_counter
        elikiwa subkundi kwenye cls._abc_negative_cache:
            rudisha Uongo
        # Check the subkundi hook
        ok = cls.__subclasshook__(subclass)
        ikiwa ok ni sio NotImplemented:
            assert isinstance(ok, bool)
            ikiwa ok:
                cls._abc_cache.add(subclass)
            isipokua:
                cls._abc_negative_cache.add(subclass)
            rudisha ok
        # Check ikiwa it's a direct subclass
        ikiwa cls kwenye getattr(subclass, '__mro__', ()):
            cls._abc_cache.add(subclass)
            rudisha Kweli
        # Check ikiwa it's a subkundi of a registered kundi (recursive)
        kila rcls kwenye cls._abc_regisjaribu:
            ikiwa issubclass(subclass, rcls):
                cls._abc_cache.add(subclass)
                rudisha Kweli
        # Check ikiwa it's a subkundi of a subkundi (recursive)
        kila scls kwenye cls.__subclasses__():
            ikiwa issubclass(subclass, scls):
                cls._abc_cache.add(subclass)
                rudisha Kweli
        # No dice; update negative cache
        cls._abc_negative_cache.add(subclass)
        rudisha Uongo
