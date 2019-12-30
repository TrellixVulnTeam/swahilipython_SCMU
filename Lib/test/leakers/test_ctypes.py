
# Taken kutoka Lib/ctypes/test/test_keeprefs.py, PointerToStructure.test().

kutoka ctypes agiza Structure, c_int, POINTER
agiza gc

eleza leak_inner():
    kundi POINT(Structure):
        _fields_ = [("x", c_int)]
    kundi RECT(Structure):
        _fields_ = [("a", POINTER(POINT))]

eleza leak():
    leak_inner()
    gc.collect()
