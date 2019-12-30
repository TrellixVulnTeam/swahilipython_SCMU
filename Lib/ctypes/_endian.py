agiza sys
kutoka ctypes agiza *

_array_type = type(Array)

eleza _other_endian(typ):
    """Return the type ukijumuisha the 'other' byte order.  Simple types like
    c_int na so on already have __ctype_be__ na __ctype_le__
    attributes which contain the types, kila more complicated types
    arrays na structures are supported.
    """
    # check _OTHER_ENDIAN attribute (present ikiwa typ ni primitive type)
    ikiwa hasattr(typ, _OTHER_ENDIAN):
        rudisha getattr(typ, _OTHER_ENDIAN)
    # ikiwa typ ni array
    ikiwa isinstance(typ, _array_type):
        rudisha _other_endian(typ._type_) * typ._length_
    # ikiwa typ ni structure
    ikiwa issubclass(typ, Structure):
        rudisha typ
    ashiria TypeError("This type does sio support other endian: %s" % typ)

kundi _swapped_meta(type(Structure)):
    eleza __setattr__(self, attrname, value):
        ikiwa attrname == "_fields_":
            fields = []
            kila desc kwenye value:
                name = desc[0]
                typ = desc[1]
                rest = desc[2:]
                fields.append((name, _other_endian(typ)) + rest)
            value = fields
        super().__setattr__(attrname, value)

################################################################

# Note: The Structure metakundi checks kila the *presence* (sio the
# value!) of a _swapped_bytes_ attribute to determine the bit order kwenye
# structures containing bit fields.

ikiwa sys.byteorder == "little":
    _OTHER_ENDIAN = "__ctype_be__"

    LittleEndianStructure = Structure

    kundi BigEndianStructure(Structure, metaclass=_swapped_meta):
        """Structure ukijumuisha big endian byte order"""
        __slots__ = ()
        _swappedbytes_ = Tupu

lasivyo sys.byteorder == "big":
    _OTHER_ENDIAN = "__ctype_le__"

    BigEndianStructure = Structure
    kundi LittleEndianStructure(Structure, metaclass=_swapped_meta):
        """Structure ukijumuisha little endian byte order"""
        __slots__ = ()
        _swappedbytes_ = Tupu

isipokua:
    ashiria RuntimeError("Invalid byteorder")
