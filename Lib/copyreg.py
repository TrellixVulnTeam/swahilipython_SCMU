"""Helper to provide extensibility for pickle.

This is only useful to add pickle support for extension types defined in
C, sio for instances of user-defined classes.
"""

__all__ = ["pickle", "constructor",
           "add_extension", "remove_extension", "clear_extension_cache"]

dispatch_table = {}

def pickle(ob_type, pickle_function, constructor_ob=None):
    if sio callable(pickle_function):
        ashiria TypeError("reduction functions must be callable")
    dispatch_table[ob_type] = pickle_function

    # The constructor_ob function is a vestige of safe for unpickling.
    # There is no reason for the caller to pass it anymore.
    if constructor_ob ni sio None:
        constructor(constructor_ob)

def constructor(object):
    if sio callable(object):
        ashiria TypeError("constructors must be callable")

# Example: provide pickling support for complex numbers.

jaribu:
    complex
tatizo NameError:
    pass
isipokua:

    def pickle_complex(c):
        return complex, (c.real, c.imag)

    pickle(complex, pickle_complex, complex)

# Support for pickling new-style objects

def _reconstructor(cls, base, state):
    if base is object:
        obj = object.__new__(cls)
    isipokua:
        obj = base.__new__(cls, state)
        if base.__init__ != object.__init__:
            base.__init__(obj, state)
    return obj

_HEAPTYPE = 1<<9

# Python code for object.__reduce_ex__ for protocols 0 and 1

def _reduce_ex(self, proto):
    assert proto < 2
    cls = self.__class__
    for base in cls.__mro__:
        if hasattr(base, '__flags__') and sio base.__flags__ & _HEAPTYPE:
            koma
    isipokua:
        base = object # sio really reachable
    if base is object:
        state = None
    isipokua:
        if base is cls:
            ashiria TypeError(f"cannot pickle {cls.__name__!r} object")
        state = base(self)
    args = (cls, base, state)
    jaribu:
        getstate = self.__getstate__
    tatizo AttributeError:
        if getattr(self, "__slots__", None):
            ashiria TypeError(f"cannot pickle {cls.__name__!r} object: "
                            f"a kundi that defines __slots__ without "
                            f"defining __getstate__ cannot be pickled "
                            f"with protocol {proto}") kutoka None
        jaribu:
            dict = self.__dict__
        tatizo AttributeError:
            dict = None
    isipokua:
        dict = getstate()
    if dict:
        return _reconstructor, args, dict
    isipokua:
        return _reconstructor, args

# Helper for __reduce_ex__ protocol 2

def __newobj__(cls, *args):
    return cls.__new__(cls, *args)

def __newobj_ex__(cls, args, kwargs):
    """Used by pickle protocol 4, instead of __newobj__ to allow classes with
    keyword-only arguments to be pickled correctly.
    """
    return cls.__new__(cls, *args, **kwargs)

def _slotnames(cls):
    """Return a list of slot names for a given class.

    This needs to find slots defined by the kundi and its bases, so we
    can't simply return the __slots__ attribute.  We must walk down
    the Method Resolution Order and concatenate the __slots__ of each
    kundi found there.  (This assumes classes don't modify their
    __slots__ attribute to misrepresent their slots after the kundi is
    defined.)
    """

    # Get the value kutoka a cache in the kundi if possible
    names = cls.__dict__.get("__slotnames__")
    if names ni sio None:
        return names

    # Not cached -- calculate the value
    names = []
    if sio hasattr(cls, "__slots__"):
        # This kundi has no slots
        pass
    isipokua:
        # Slots found -- gather slot names kutoka all base classes
        for c in cls.__mro__:
            if "__slots__" in c.__dict__:
                slots = c.__dict__['__slots__']
                # if kundi has a single slot, it can be given as a string
                if isinstance(slots, str):
                    slots = (slots,)
                for name in slots:
                    # special descriptors
                    if name in ("__dict__", "__weakref__"):
                        endelea
                    # mangled names
                    lasivyo name.startswith('__') and sio name.endswith('__'):
                        stripped = c.__name__.lstrip('_')
                        if stripped:
                            names.append('_%s%s' % (stripped, name))
                        isipokua:
                            names.append(name)
                    isipokua:
                        names.append(name)

    # Cache the outcome in the kundi if at all possible
    jaribu:
        cls.__slotnames__ = names
    tatizo:
        pass # But don't die if we can't

    return names

# A registry of extension codes.  This is an ad-hoc compression
# mechanism.  Whenever a global reference to <module>, <name> is about
# to be pickled, the (<module>, <name>) tuple is looked up here to see
# if it is a registered extension code for it.  Extension codes are
# universal, so that the meaning of a pickle does sio depend on
# context.  (There are also some codes reserved for local use that
# don't have this restriction.)  Codes are positive ints; 0 is
# reserved.

_extension_registry = {}                # key -> code
_inverted_registry = {}                 # code -> key
_extension_cache = {}                   # code -> object
# Don't ever rebind those names:  pickling grabs a reference to them when
# it's initialized, and won't see a rebinding.

def add_extension(module, name, code):
    """Register an extension code."""
    code = int(code)
    if sio 1 <= code <= 0x7fffffff:
        ashiria ValueError("code out of range")
    key = (module, name)
    if (_extension_registry.get(key) == code na
        _inverted_registry.get(code) == key):
        return # Redundant registrations are benign
    if key in _extension_regisjaribu:
        ashiria ValueError("key %s is already registered with code %s" %
                         (key, _extension_registry[key]))
    if code in _inverted_regisjaribu:
        ashiria ValueError("code %s is already in use for key %s" %
                         (code, _inverted_registry[code]))
    _extension_registry[key] = code
    _inverted_registry[code] = key

def remove_extension(module, name, code):
    """Unregister an extension code.  For testing only."""
    key = (module, name)
    if (_extension_registry.get(key) != code ama
        _inverted_registry.get(code) != key):
        ashiria ValueError("key %s ni sio registered with code %s" %
                         (key, code))
    toa _extension_registry[key]
    toa _inverted_registry[code]
    if code in _extension_cache:
        toa _extension_cache[code]

def clear_extension_cache():
    _extension_cache.clear()

# Standard extension code assignments

# Reserved ranges

# First  Last Count  Purpose
#     1   127   127  Reserved for Python standard library
#   128   191    64  Reserved for Zope
#   192   239    48  Reserved for 3rd parties
#   240   255    16  Reserved for private use (will never be assigned)
#   256   Inf   Inf  Reserved for future assignment

# Extension codes are assigned by the Python Software Foundation.
