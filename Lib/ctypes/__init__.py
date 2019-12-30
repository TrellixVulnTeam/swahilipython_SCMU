"""create na manipulate C data types kwenye Python"""

agiza os kama _os, sys kama _sys

__version__ = "1.1.0"

kutoka _ctypes agiza Union, Structure, Array
kutoka _ctypes agiza _Pointer
kutoka _ctypes agiza CFuncPtr kama _CFuncPtr
kutoka _ctypes agiza __version__ kama _ctypes_version
kutoka _ctypes agiza RTLD_LOCAL, RTLD_GLOBAL
kutoka _ctypes agiza ArgumentError

kutoka struct agiza calcsize kama _calcsize

ikiwa __version__ != _ctypes_version:
    ashiria Exception("Version number mismatch", __version__, _ctypes_version)

ikiwa _os.name == "nt":
    kutoka _ctypes agiza FormatError

DEFAULT_MODE = RTLD_LOCAL
ikiwa _os.name == "posix" na _sys.platform == "darwin":
    # On OS X 10.3, we use RTLD_GLOBAL kama default mode
    # because RTLD_LOCAL does sio work at least on some
    # libraries.  OS X 10.3 ni Darwin 7, so we check for
    # that.

    ikiwa int(_os.uname().release.split('.')[0]) < 8:
        DEFAULT_MODE = RTLD_GLOBAL

kutoka _ctypes agiza FUNCFLAG_CDECL kama _FUNCFLAG_CDECL, \
     FUNCFLAG_PYTHONAPI kama _FUNCFLAG_PYTHONAPI, \
     FUNCFLAG_USE_ERRNO kama _FUNCFLAG_USE_ERRNO, \
     FUNCFLAG_USE_LASTERROR kama _FUNCFLAG_USE_LASTERROR

# WINOLEAPI -> HRESULT
# WINOLEAPI_(type)
#
# STDMETHODCALLTYPE
#
# STDMETHOD(name)
# STDMETHOD_(type, name)
#
# STDAPICALLTYPE

eleza create_string_buffer(init, size=Tupu):
    """create_string_buffer(aBytes) -> character array
    create_string_buffer(anInteger) -> character array
    create_string_buffer(aBytes, anInteger) -> character array
    """
    ikiwa isinstance(init, bytes):
        ikiwa size ni Tupu:
            size = len(init)+1
        buftype = c_char * size
        buf = buftype()
        buf.value = init
        rudisha buf
    lasivyo isinstance(init, int):
        buftype = c_char * init
        buf = buftype()
        rudisha buf
    ashiria TypeError(init)

eleza c_buffer(init, size=Tupu):
##    "deprecated, use create_string_buffer instead"
##    agiza warnings
##    warnings.warn("c_buffer ni deprecated, use create_string_buffer instead",
##                  DeprecationWarning, stacklevel=2)
    rudisha create_string_buffer(init, size)

_c_functype_cache = {}
eleza CFUNCTYPE(restype, *argtypes, **kw):
    """CFUNCTYPE(restype, *argtypes,
                 use_errno=Uongo, use_last_error=Uongo) -> function prototype.

    restype: the result type
    argtypes: a sequence specifying the argument types

    The function prototype can be called kwenye different ways to create a
    callable object:

    prototype(integer address) -> foreign function
    prototype(callable) -> create na rudisha a C callable function kutoka callable
    prototype(integer index, method name[, paramflags]) -> foreign function calling a COM method
    prototype((ordinal number, dll object)[, paramflags]) -> foreign function exported by ordinal
    prototype((function name, dll object)[, paramflags]) -> foreign function exported by name
    """
    flags = _FUNCFLAG_CDECL
    ikiwa kw.pop("use_errno", Uongo):
        flags |= _FUNCFLAG_USE_ERRNO
    ikiwa kw.pop("use_last_error", Uongo):
        flags |= _FUNCFLAG_USE_LASTERROR
    ikiwa kw:
        ashiria ValueError("unexpected keyword argument(s) %s" % kw.keys())
    jaribu:
        rudisha _c_functype_cache[(restype, argtypes, flags)]
    tatizo KeyError:
        kundi CFunctionType(_CFuncPtr):
            _argtypes_ = argtypes
            _restype_ = restype
            _flags_ = flags
        _c_functype_cache[(restype, argtypes, flags)] = CFunctionType
        rudisha CFunctionType

ikiwa _os.name == "nt":
    kutoka _ctypes agiza LoadLibrary kama _dlopen
    kutoka _ctypes agiza FUNCFLAG_STDCALL kama _FUNCFLAG_STDCALL

    _win_functype_cache = {}
    eleza WINFUNCTYPE(restype, *argtypes, **kw):
        # docstring set later (very similar to CFUNCTYPE.__doc__)
        flags = _FUNCFLAG_STDCALL
        ikiwa kw.pop("use_errno", Uongo):
            flags |= _FUNCFLAG_USE_ERRNO
        ikiwa kw.pop("use_last_error", Uongo):
            flags |= _FUNCFLAG_USE_LASTERROR
        ikiwa kw:
            ashiria ValueError("unexpected keyword argument(s) %s" % kw.keys())
        jaribu:
            rudisha _win_functype_cache[(restype, argtypes, flags)]
        tatizo KeyError:
            kundi WinFunctionType(_CFuncPtr):
                _argtypes_ = argtypes
                _restype_ = restype
                _flags_ = flags
            _win_functype_cache[(restype, argtypes, flags)] = WinFunctionType
            rudisha WinFunctionType
    ikiwa WINFUNCTYPE.__doc__:
        WINFUNCTYPE.__doc__ = CFUNCTYPE.__doc__.replace("CFUNCTYPE", "WINFUNCTYPE")

lasivyo _os.name == "posix":
    kutoka _ctypes agiza dlopen kama _dlopen

kutoka _ctypes agiza sizeof, byref, addressof, alignment, resize
kutoka _ctypes agiza get_errno, set_errno
kutoka _ctypes agiza _SimpleCData

eleza _check_size(typ, typecode=Tupu):
    # Check ikiwa sizeof(ctypes_type) against struct.calcsize.  This
    # should protect somewhat against a misconfigured libffi.
    kutoka struct agiza calcsize
    ikiwa typecode ni Tupu:
        # Most _type_ codes are the same kama used kwenye struct
        typecode = typ._type_
    actual, required = sizeof(typ), calcsize(typecode)
    ikiwa actual != required:
        ashiria SystemError("sizeof(%s) wrong: %d instead of %d" % \
                          (typ, actual, required))

kundi py_object(_SimpleCData):
    _type_ = "O"
    eleza __repr__(self):
        jaribu:
            rudisha super().__repr__()
        tatizo ValueError:
            rudisha "%s(<NULL>)" % type(self).__name__
_check_size(py_object, "P")

kundi c_short(_SimpleCData):
    _type_ = "h"
_check_size(c_short)

kundi c_ushort(_SimpleCData):
    _type_ = "H"
_check_size(c_ushort)

kundi c_long(_SimpleCData):
    _type_ = "l"
_check_size(c_long)

kundi c_ulong(_SimpleCData):
    _type_ = "L"
_check_size(c_ulong)

ikiwa _calcsize("i") == _calcsize("l"):
    # ikiwa int na long have the same size, make c_int an alias kila c_long
    c_int = c_long
    c_uint = c_ulong
isipokua:
    kundi c_int(_SimpleCData):
        _type_ = "i"
    _check_size(c_int)

    kundi c_uint(_SimpleCData):
        _type_ = "I"
    _check_size(c_uint)

kundi c_float(_SimpleCData):
    _type_ = "f"
_check_size(c_float)

kundi c_double(_SimpleCData):
    _type_ = "d"
_check_size(c_double)

kundi c_longdouble(_SimpleCData):
    _type_ = "g"
ikiwa sizeof(c_longdouble) == sizeof(c_double):
    c_longdouble = c_double

ikiwa _calcsize("l") == _calcsize("q"):
    # ikiwa long na long long have the same size, make c_longlong an alias kila c_long
    c_longlong = c_long
    c_ulonglong = c_ulong
isipokua:
    kundi c_longlong(_SimpleCData):
        _type_ = "q"
    _check_size(c_longlong)

    kundi c_ulonglong(_SimpleCData):
        _type_ = "Q"
    ##    eleza from_param(cls, val):
    ##        rudisha ('d', float(val), val)
    ##    from_param = classmethod(from_param)
    _check_size(c_ulonglong)

kundi c_ubyte(_SimpleCData):
    _type_ = "B"
c_ubyte.__ctype_le__ = c_ubyte.__ctype_be__ = c_ubyte
# backward compatibility:
##c_uchar = c_ubyte
_check_size(c_ubyte)

kundi c_byte(_SimpleCData):
    _type_ = "b"
c_byte.__ctype_le__ = c_byte.__ctype_be__ = c_byte
_check_size(c_byte)

kundi c_char(_SimpleCData):
    _type_ = "c"
c_char.__ctype_le__ = c_char.__ctype_be__ = c_char
_check_size(c_char)

kundi c_char_p(_SimpleCData):
    _type_ = "z"
    eleza __repr__(self):
        rudisha "%s(%s)" % (self.__class__.__name__, c_void_p.from_buffer(self).value)
_check_size(c_char_p, "P")

kundi c_void_p(_SimpleCData):
    _type_ = "P"
c_voidp = c_void_p # backwards compatibility (to a bug)
_check_size(c_void_p)

kundi c_bool(_SimpleCData):
    _type_ = "?"

kutoka _ctypes agiza POINTER, pointer, _pointer_type_cache

kundi c_wchar_p(_SimpleCData):
    _type_ = "Z"
    eleza __repr__(self):
        rudisha "%s(%s)" % (self.__class__.__name__, c_void_p.from_buffer(self).value)

kundi c_wchar(_SimpleCData):
    _type_ = "u"

eleza _reset_cache():
    _pointer_type_cache.clear()
    _c_functype_cache.clear()
    ikiwa _os.name == "nt":
        _win_functype_cache.clear()
    # _SimpleCData.c_wchar_p_from_param
    POINTER(c_wchar).from_param = c_wchar_p.from_param
    # _SimpleCData.c_char_p_from_param
    POINTER(c_char).from_param = c_char_p.from_param
    _pointer_type_cache[Tupu] = c_void_p

eleza create_unicode_buffer(init, size=Tupu):
    """create_unicode_buffer(aString) -> character array
    create_unicode_buffer(anInteger) -> character array
    create_unicode_buffer(aString, anInteger) -> character array
    """
    ikiwa isinstance(init, str):
        ikiwa size ni Tupu:
            ikiwa sizeof(c_wchar) == 2:
                # UTF-16 requires a surrogate pair (2 wchar_t) kila non-BMP
                # characters (outside [U+0000; U+FFFF] range). +1 kila trailing
                # NUL character.
                size = sum(2 ikiwa ord(c) > 0xFFFF isipokua 1 kila c kwenye init) + 1
            isipokua:
                # 32-bit wchar_t (1 wchar_t per Unicode character). +1 for
                # trailing NUL character.
                size = len(init) + 1
        buftype = c_wchar * size
        buf = buftype()
        buf.value = init
        rudisha buf
    lasivyo isinstance(init, int):
        buftype = c_wchar * init
        buf = buftype()
        rudisha buf
    ashiria TypeError(init)


# XXX Deprecated
eleza SetPointerType(pointer, cls):
    ikiwa _pointer_type_cache.get(cls, Tupu) ni sio Tupu:
        ashiria RuntimeError("This type already exists kwenye the cache")
    ikiwa id(pointer) haiko kwenye _pointer_type_cache:
        ashiria RuntimeError("What's this???")
    pointer.set_type(cls)
    _pointer_type_cache[cls] = pointer
    toa _pointer_type_cache[id(pointer)]

# XXX Deprecated
eleza ARRAY(typ, len):
    rudisha typ * len

################################################################


kundi CDLL(object):
    """An instance of this kundi represents a loaded dll/shared
    library, exporting functions using the standard C calling
    convention (named 'cdecl' on Windows).

    The exported functions can be accessed kama attributes, ama by
    indexing ukijumuisha the function name.  Examples:

    <obj>.qsort -> callable object
    <obj>['qsort'] -> callable object

    Calling the functions releases the Python GIL during the call na
    reacquires it afterwards.
    """
    _func_flags_ = _FUNCFLAG_CDECL
    _func_restype_ = c_int
    # default values kila repr
    _name = '<uninitialized>'
    _handle = 0
    _FuncPtr = Tupu

    eleza __init__(self, name, mode=DEFAULT_MODE, handle=Tupu,
                 use_errno=Uongo,
                 use_last_error=Uongo,
                 winmode=Tupu):
        self._name = name
        flags = self._func_flags_
        ikiwa use_errno:
            flags |= _FUNCFLAG_USE_ERRNO
        ikiwa use_last_error:
            flags |= _FUNCFLAG_USE_LASTERROR
        ikiwa _sys.platform.startswith("aix"):
            """When the name contains ".a(" na ends ukijumuisha ")",
               e.g., "libFOO.a(libFOO.so)" - this ni taken to be an
               archive(member) syntax kila dlopen(), na the mode ni adjusted.
               Otherwise, name ni presented to dlopen() kama a file argument.
            """
            ikiwa name na name.endswith(")") na ".a(" kwenye name:
                mode |= ( _os.RTLD_MEMBER | _os.RTLD_NOW )
        ikiwa _os.name == "nt":
            ikiwa winmode ni sio Tupu:
                mode = winmode
            isipokua:
                agiza nt
                mode = nt._LOAD_LIBRARY_SEARCH_DEFAULT_DIRS
                ikiwa '/' kwenye name ama '\\' kwenye name:
                    self._name = nt._getfullpathname(self._name)
                    mode |= nt._LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR

        kundi _FuncPtr(_CFuncPtr):
            _flags_ = flags
            _restype_ = self._func_restype_
        self._FuncPtr = _FuncPtr

        ikiwa handle ni Tupu:
            self._handle = _dlopen(self._name, mode)
        isipokua:
            self._handle = handle

    eleza __repr__(self):
        rudisha "<%s '%s', handle %x at %#x>" % \
               (self.__class__.__name__, self._name,
                (self._handle & (_sys.maxsize*2 + 1)),
                id(self) & (_sys.maxsize*2 + 1))

    eleza __getattr__(self, name):
        ikiwa name.startswith('__') na name.endswith('__'):
            ashiria AttributeError(name)
        func = self.__getitem__(name)
        setattr(self, name, func)
        rudisha func

    eleza __getitem__(self, name_or_ordinal):
        func = self._FuncPtr((name_or_ordinal, self))
        ikiwa sio isinstance(name_or_ordinal, int):
            func.__name__ = name_or_ordinal
        rudisha func

kundi PyDLL(CDLL):
    """This kundi represents the Python library itself.  It allows
    accessing Python API functions.  The GIL ni sio released, na
    Python exceptions are handled correctly.
    """
    _func_flags_ = _FUNCFLAG_CDECL | _FUNCFLAG_PYTHONAPI

ikiwa _os.name == "nt":

    kundi WinDLL(CDLL):
        """This kundi represents a dll exporting functions using the
        Windows stdcall calling convention.
        """
        _func_flags_ = _FUNCFLAG_STDCALL

    # XXX Hm, what about HRESULT kama normal parameter?
    # Mustn't it derive kutoka c_long then?
    kutoka _ctypes agiza _check_HRESULT, _SimpleCData
    kundi HRESULT(_SimpleCData):
        _type_ = "l"
        # _check_retval_ ni called ukijumuisha the function's result when it
        # ni used kama restype.  It checks kila the FAILED bit, na
        # raises an OSError ikiwa it ni set.
        #
        # The _check_retval_ method ni implemented kwenye C, so that the
        # method definition itself ni sio inluded kwenye the traceback
        # when it raises an error - that ni what we want (and Python
        # doesn't have a way to ashiria an exception kwenye the caller's
        # frame).
        _check_retval_ = _check_HRESULT

    kundi OleDLL(CDLL):
        """This kundi represents a dll exporting functions using the
        Windows stdcall calling convention, na returning HRESULT.
        HRESULT error values are automatically raised kama OSError
        exceptions.
        """
        _func_flags_ = _FUNCFLAG_STDCALL
        _func_restype_ = HRESULT

kundi LibraryLoader(object):
    eleza __init__(self, dlltype):
        self._dlltype = dlltype

    eleza __getattr__(self, name):
        ikiwa name[0] == '_':
            ashiria AttributeError(name)
        dll = self._dlltype(name)
        setattr(self, name, dll)
        rudisha dll

    eleza __getitem__(self, name):
        rudisha getattr(self, name)

    eleza LoadLibrary(self, name):
        rudisha self._dlltype(name)

cdll = LibraryLoader(CDLL)
pydll = LibraryLoader(PyDLL)

ikiwa _os.name == "nt":
    pythonapi = PyDLL("python dll", Tupu, _sys.dllhandle)
lasivyo _sys.platform == "cygwin":
    pythonapi = PyDLL("libpython%d.%d.dll" % _sys.version_info[:2])
isipokua:
    pythonapi = PyDLL(Tupu)


ikiwa _os.name == "nt":
    windll = LibraryLoader(WinDLL)
    oledll = LibraryLoader(OleDLL)

    GetLastError = windll.kernel32.GetLastError
    kutoka _ctypes agiza get_last_error, set_last_error

    eleza WinError(code=Tupu, descr=Tupu):
        ikiwa code ni Tupu:
            code = GetLastError()
        ikiwa descr ni Tupu:
            descr = FormatError(code).strip()
        rudisha OSError(Tupu, descr, Tupu, code)

ikiwa sizeof(c_uint) == sizeof(c_void_p):
    c_size_t = c_uint
    c_ssize_t = c_int
lasivyo sizeof(c_ulong) == sizeof(c_void_p):
    c_size_t = c_ulong
    c_ssize_t = c_long
lasivyo sizeof(c_ulonglong) == sizeof(c_void_p):
    c_size_t = c_ulonglong
    c_ssize_t = c_longlong

# functions

kutoka _ctypes agiza _memmove_addr, _memset_addr, _string_at_addr, _cast_addr

## void *memmove(void *, const void *, size_t);
memmove = CFUNCTYPE(c_void_p, c_void_p, c_void_p, c_size_t)(_memmove_addr)

## void *memset(void *, int, size_t)
memset = CFUNCTYPE(c_void_p, c_void_p, c_int, c_size_t)(_memset_addr)

eleza PYFUNCTYPE(restype, *argtypes):
    kundi CFunctionType(_CFuncPtr):
        _argtypes_ = argtypes
        _restype_ = restype
        _flags_ = _FUNCFLAG_CDECL | _FUNCFLAG_PYTHONAPI
    rudisha CFunctionType

_cast = PYFUNCTYPE(py_object, c_void_p, py_object, py_object)(_cast_addr)
eleza cast(obj, typ):
    rudisha _cast(obj, obj, typ)

_string_at = PYFUNCTYPE(py_object, c_void_p, c_int)(_string_at_addr)
eleza string_at(ptr, size=-1):
    """string_at(addr[, size]) -> string

    Return the string at addr."""
    rudisha _string_at(ptr, size)

jaribu:
    kutoka _ctypes agiza _wstring_at_addr
tatizo ImportError:
    pita
isipokua:
    _wstring_at = PYFUNCTYPE(py_object, c_void_p, c_int)(_wstring_at_addr)
    eleza wstring_at(ptr, size=-1):
        """wstring_at(addr[, size]) -> string

        Return the string at addr."""
        rudisha _wstring_at(ptr, size)


ikiwa _os.name == "nt": # COM stuff
    eleza DllGetClassObject(rclsid, riid, ppv):
        jaribu:
            ccom = __import__("comtypes.server.inprocserver", globals(), locals(), ['*'])
        tatizo ImportError:
            rudisha -2147221231 # CLASS_E_CLASSNOTAVAILABLE
        isipokua:
            rudisha ccom.DllGetClassObject(rclsid, riid, ppv)

    eleza DllCanUnloadNow():
        jaribu:
            ccom = __import__("comtypes.server.inprocserver", globals(), locals(), ['*'])
        tatizo ImportError:
            rudisha 0 # S_OK
        rudisha ccom.DllCanUnloadNow()

kutoka ctypes._endian agiza BigEndianStructure, LittleEndianStructure

# Fill kwenye specifically-sized types
c_int8 = c_byte
c_uint8 = c_ubyte
kila kind kwenye [c_short, c_int, c_long, c_longlong]:
    ikiwa sizeof(kind) == 2: c_int16 = kind
    lasivyo sizeof(kind) == 4: c_int32 = kind
    lasivyo sizeof(kind) == 8: c_int64 = kind
kila kind kwenye [c_ushort, c_uint, c_ulong, c_ulonglong]:
    ikiwa sizeof(kind) == 2: c_uint16 = kind
    lasivyo sizeof(kind) == 4: c_uint32 = kind
    lasivyo sizeof(kind) == 8: c_uint64 = kind
del(kind)

_reset_cache()
