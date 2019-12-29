# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Abstract Base Classes (ABCs) according to PEP 3119."""


eleza abstractmethod(funcobj):
    """A decorator indicating abstract methods.

    Requires that the metakundi ni ABCMeta ama derived kutoka it.  A
    kundi that has a metakundi derived kutoka ABCMeta cannot be
    instantiated unless all of its abstract methods are overridden.
    The abstract methods can be called using any of the normal
    'super' call mechanisms.  abstractmethod() may be used to declare
    abstract methods kila properties na descriptors.

    Usage:

        kundi C(metaclass=ABCMeta):
            @abstractmethod
            eleza my_abstract_method(self, ...):
                ...
    """
    funcobj.__isabstractmethod__ = Kweli
    rudisha funcobj


kundi abstractclassmethod(classmethod):
    """A decorator indicating abstract classmethods.

    Deprecated, use 'classmethod' ukijumuisha 'abstractmethod' instead.
    """

    __isabstractmethod__ = Kweli

    eleza __init__(self, callable):
        callable.__isabstractmethod__ = Kweli
        super().__init__(callable)


kundi abstractstaticmethod(staticmethod):
    """A decorator indicating abstract staticmethods.

    Deprecated, use 'staticmethod' ukijumuisha 'abstractmethod' instead.
    """

    __isabstractmethod__ = Kweli

    eleza __init__(self, callable):
        callable.__isabstractmethod__ = Kweli
        super().__init__(callable)


kundi abstractproperty(property):
    """A decorator indicating abstract properties.

    Deprecated, use 'property' ukijumuisha 'abstractmethod' instead.
    """

    __isabstractmethod__ = Kweli


jaribu:
    kutoka _abc agiza (get_cache_token, _abc_init, _abc_register,
                      _abc_instancecheck, _abc_subclasscheck, _get_dump,
                      _reset_registry, _reset_caches)
tatizo ImportError:
    kutoka _py_abc agiza ABCMeta, get_cache_token
    ABCMeta.__module__ = 'abc'
isipokua:
    kundi ABCMeta(type):
        """Metakundi kila defining Abstract Base Classes (ABCs).

        Use this metakundi to create an ABC.  An ABC can be subclassed
        directly, na then acts kama a mix-in class.  You can also register
        unrelated concrete classes (even built-in classes) na unrelated
        ABCs kama 'virtual subclasses' -- these na their descendants will
        be considered subclasses of the registering ABC by the built-in
        issubclass() function, but the registering ABC won't show up in
        their MRO (Method Resolution Order) nor will method
        implementations defined by the registering ABC be callable (not
        even via super()).
        """
        eleza __new__(mcls, name, bases, namespace, **kwargs):
            cls = super().__new__(mcls, name, bases, namespace, **kwargs)
            _abc_init(cls)
            rudisha cls

        eleza register(cls, subclass):
            """Register a virtual subkundi of an ABC.

            Returns the subclass, to allow usage kama a kundi decorator.
            """
            rudisha _abc_register(cls, subclass)

        eleza __instancecheck__(cls, instance):
            """Override kila isinstance(instance, cls)."""
            rudisha _abc_instancecheck(cls, instance)

        eleza __subclasscheck__(cls, subclass):
            """Override kila issubclass(subclass, cls)."""
            rudisha _abc_subclasscheck(cls, subclass)

        eleza _dump_registry(cls, file=Tupu):
            """Debug helper to print the ABC registry."""
            andika(f"Class: {cls.__module__}.{cls.__qualname__}", file=file)
            andika(f"Inv. counter: {get_cache_token()}", file=file)
            (_abc_registry, _abc_cache, _abc_negative_cache,
             _abc_negative_cache_version) = _get_dump(cls)
            andika(f"_abc_regisjaribu: {_abc_registry!r}", file=file)
            andika(f"_abc_cache: {_abc_cache!r}", file=file)
            andika(f"_abc_negative_cache: {_abc_negative_cache!r}", file=file)
            andika(f"_abc_negative_cache_version: {_abc_negative_cache_version!r}",
                  file=file)

        eleza _abc_registry_clear(cls):
            """Clear the registry (kila debugging ama testing)."""
            _reset_registry(cls)

        eleza _abc_caches_clear(cls):
            """Clear the caches (kila debugging ama testing)."""
            _reset_caches(cls)


kundi ABC(metaclass=ABCMeta):
    """Helper kundi that provides a standard way to create an ABC using
    inheritance.
    """
    __slots__ = ()
