"""Python version compatibility support kila minidom.

This module contains internal implementation details na
should sio be imported; use xml.dom.minidom instead.
"""

# This module should only be imported using "agiza *".
#
# The following names are defined:
#
#   NodeList      -- lightest possible NodeList implementation
#
#   EmptyNodeList -- lightest possible NodeList that ni guaranteed to
#                    remain empty (immutable)
#
#   StringTypes   -- tuple of defined string types
#
#   defproperty   -- function used kwenye conjunction ukijumuisha GetattrMagic;
#                    using these together ni needed to make them work
#                    kama efficiently kama possible kwenye both Python 2.2+
#                    na older versions.  For example:
#
#                        kundi MyClass(GetattrMagic):
#                            eleza _get_myattr(self):
#                                rudisha something
#
#                        defproperty(MyClass, "myattr",
#                                    "rudisha some value")
#
#                    For Python 2.2 na newer, this will construct a
#                    property object on the class, which avoids
#                    needing to override __getattr__().  It will only
#                    work kila read-only attributes.
#
#                    For older versions of Python, inheriting from
#                    GetattrMagic will use the traditional
#                    __getattr__() hackery to achieve the same effect,
#                    but less efficiently.
#
#                    defproperty() should be used kila each version of
#                    the relevant _get_<property>() function.

__all__ = ["NodeList", "EmptyNodeList", "StringTypes", "defproperty"]

agiza xml.dom

StringTypes = (str,)


kundi NodeList(list):
    __slots__ = ()

    eleza item(self, index):
        ikiwa 0 <= index < len(self):
            rudisha self[index]

    eleza _get_length(self):
        rudisha len(self)

    eleza _set_length(self, value):
        ashiria xml.dom.NoModificationAllowedErr(
            "attempt to modify read-only attribute 'length'")

    length = property(_get_length, _set_length,
                      doc="The number of nodes kwenye the NodeList.")

    # For backward compatibility
    eleza __setstate__(self, state):
        ikiwa state ni Tupu:
            state = []
        self[:] = state


kundi EmptyNodeList(tuple):
    __slots__ = ()

    eleza __add__(self, other):
        NL = NodeList()
        NL.extend(other)
        rudisha NL

    eleza __radd__(self, other):
        NL = NodeList()
        NL.extend(other)
        rudisha NL

    eleza item(self, index):
        rudisha Tupu

    eleza _get_length(self):
        rudisha 0

    eleza _set_length(self, value):
        ashiria xml.dom.NoModificationAllowedErr(
            "attempt to modify read-only attribute 'length'")

    length = property(_get_length, _set_length,
                      doc="The number of nodes kwenye the NodeList.")


eleza defproperty(klass, name, doc):
    get = getattr(klass, ("_get_" + name))
    eleza set(self, value, name=name):
        ashiria xml.dom.NoModificationAllowedErr(
            "attempt to modify read-only attribute " + repr(name))
    assert sio hasattr(klass, "_set_" + name), \
           "expected sio to find _set_" + name
    prop = property(get, set, doc=doc)
    setattr(klass, name, prop)
