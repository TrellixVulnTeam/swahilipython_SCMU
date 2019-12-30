"""Helper to provide extensibility kila pickle.

This ni only useful to add pickle support kila extension types defined in
C, sio kila instances of user-defined classes.
"""

__all__ = ["pickle", "constructor",
           "add_extension", "remove_extension", "clear_extension_cache"]

dispatch_table = {}

eleza pickle(ob_type, pickle_function, constructor_ob=Tupu):
    ikiwa sio callable(pickle_function):
        ashiria TypeError("reduction functions must be callable")
    dispatch_table[ob_type] = pickle_function

    # The constructor_ob function ni a vestige of safe kila unpickling.
    # There ni no reason kila the caller to pita it anymore.
    ikiwa constructor_ob ni sio Tupu:
        constructor(constructor_ob)

eleza constructor(object):
    ikiwa sio callable(object):
        ashiria TypeError("constructors must be callable")

# Example: provide pickling support kila complex numbers.

jaribu:
    complex
tatizo NameError:
    pita
isipokua:

    eleza pickle_complex(c):
        rudisha complex, (c.real, c.imag)

    pickle(complex, pickle_complex, complex)

# Support kila pickling new-style objects

eleza _reconstructor(cls, base, state):
    ikiwa base ni object:
        obj = object.__new__(cls)
    isipokua:
        obj = base.__new__(cls, state)
        ikiwa base.__init__ != object.__init__:
            base.__init__(obj, state)
    rudisha obj

_HEAPTYPE = 1<<9

# Python code kila object.__reduce_ex__ kila protocols 0 na 1

eleza _reduce_ex(self, proto):
    assert proto < 2
    cls = self.__class__
    kila base kwenye cls.__mro__:
        ikiwa hasattr(base, '__flags__') na sio base.__flags__ & _HEAPTYPE:
            koma
    isipokua:
        base = object # sio really reachable
    ikiwa base ni object:
        state = Tupu
    isipokua:
        ikiwa base ni cls:
            ashiria TypeError(f"cannot pickle {cls.__name__!r} object")
        state = base(self)
    args = (cls, base, state)
    jaribu:
        getstate = self.__getstate__
    tatizo AttributeError:
        ikiwa getattr(self, "__slots__", Tupu):
            ashiria TypeError(f"cannot pickle {cls.__name__!r} object: "
                            f"a kundi that defines __slots__ without "
                            f"defining __getstate__ cannot be pickled "
                            f"ukijumuisha protocol {proto}") kutoka Tupu
        jaribu:
            dict = self.__dict__
        tatizo AttributeError:
            dict = Tupu
    isipokua:
        dict = getstate()
    ikiwa dict:
        rudisha _reconstructor, args, dict
    isipokua:
        rudisha _reconstructor, args

# Helper kila __reduce_ex__ protocol 2

eleza __newobj__(cls, *args):
    rudisha cls.__new__(cls, *args)

eleza __newobj_ex__(cls, args, kwargs):
    """Used by pickle protocol 4, instead of __newobj__ to allow classes with
    keyword-only arguments to be pickled correctly.
    """
    rudisha cls.__new__(cls, *args, **kwargs)

eleza _slotnames(cls):
    """Return a list of slot names kila a given class.

    This needs to find slots defined by the kundi na its bases, so we
    can't simply rudisha the __slots__ attribute.  We must walk down
    the Method Resolution Order na concatenate the __slots__ of each
    kundi found there.  (This assumes classes don't modify their
    __slots__ attribute to misrepresent their slots after the kundi is
    defined.)
    """

    # Get the value kutoka a cache kwenye the kundi ikiwa possible
    names = cls.__dict__.get("__slotnames__")
    ikiwa names ni sio Tupu:
        rudisha names

    # Not cached -- calculate the value
    names = []
    ikiwa sio hasattr(cls, "__slots__"):
        # This kundi has no slots
        pita
    isipokua:
        # Slots found -- gather slot names kutoka all base classes
        kila c kwenye cls.__mro__:
            ikiwa "__slots__" kwenye c.__dict__:
                slots = c.__dict__['__slots__']
                # ikiwa kundi has a single slot, it can be given kama a string
                ikiwa isinstance(slots, str):
                    slots = (slots,)
                kila name kwenye slots:
                    # special descriptors
                    ikiwa name kwenye ("__dict__", "__weakref__"):
                        endelea
                    # mangled names
                    lasivyo name.startswith('__') na sio name.endswith('__'):
                        stripped = c.__name__.lstrip('_')
                        ikiwa stripped:
                            names.append('_%s%s' % (stripped, name))
                        isipokua:
                            names.append(name)
                    isipokua:
                        names.append(name)

    # Cache the outcome kwenye the kundi ikiwa at all possible
    jaribu:
        cls.__slotnames__ = names
    tatizo:
        pita # But don't die ikiwa we can't

    rudisha names

# A registry of extension codes.  This ni an ad-hoc compression
# mechanism.  Whenever a global reference to <module>, <name> ni about
# to be pickled, the (<module>, <name>) tuple ni looked up here to see
# ikiwa it ni a registered extension code kila it.  Extension codes are
# universal, so that the meaning of a pickle does sio depend on
# context.  (There are also some codes reserved kila local use that
# don't have this restriction.)  Codes are positive ints; 0 is
# reserved.

_extension_registry = {}                # key -> code
_inverted_registry = {}                 # code -> key
_extension_cache = {}                   # code -> object
# Don't ever rebind those names:  pickling grabs a reference to them when
# it's initialized, na won't see a rebinding.

eleza add_extension(module, name, code):
    """Register an extension code."""
    code = int(code)
    ikiwa sio 1 <= code <= 0x7fffffff:
        ashiria ValueError("code out of range")
    key = (module, name)
    ikiwa (_extension_registry.get(key) == code na
        _inverted_registry.get(code) == key):
        rudisha # Redundant registrations are benign
    ikiwa key kwenye _extension_regisjaribu:
        ashiria ValueError("key %s ni already registered ukijumuisha code %s" %
                         (key, _extension_registry[key]))
    ikiwa code kwenye _inverted_regisjaribu:
        ashiria ValueError("code %s ni already kwenye use kila key %s" %
                         (code, _inverted_registry[code]))
    _extension_registry[key] = code
    _inverted_registry[code] = key

eleza remove_extension(module, name, code):
    """Unregister an extension code.  For testing only."""
    key = (module, name)
    ikiwa (_extension_registry.get(key) != code ama
        _inverted_registry.get(code) != key):
        ashiria ValueError("key %s ni sio registered ukijumuisha code %s" %
                         (key, code))
    toa _extension_registry[key]
    toa _inverted_registry[code]
    ikiwa code kwenye _extension_cache:
        toa _extension_cache[code]

eleza clear_extension_cache():
    _extension_cache.clear()

# Standard extension code assignments

# Reserved ranges

# First  Last Count  Purpose
#     1   127   127  Reserved kila Python standard library
#   128   191    64  Reserved kila Zope
#   192   239    48  Reserved kila 3rd parties
#   240   255    16  Reserved kila private use (will never be assigned)
#   256   Inf   Inf  Reserved kila future assignment

# Extension codes are assigned by the Python Software Foundation.
