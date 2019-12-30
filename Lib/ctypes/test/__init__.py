agiza os
agiza unittest
kutoka test agiza support

# skip tests ikiwa _ctypes was sio built
ctypes = support.import_module('ctypes')
ctypes_symbols = dir(ctypes)

eleza need_symbol(name):
    rudisha unittest.skipUnless(name kwenye ctypes_symbols,
                               '{!r} ni required'.format(name))

eleza load_tests(*args):
    rudisha support.load_package_tests(os.path.dirname(__file__), *args)
