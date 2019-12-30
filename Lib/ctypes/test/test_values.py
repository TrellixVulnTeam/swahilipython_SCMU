"""
A testcase which accesses *values* kwenye a dll.
"""

agiza unittest
agiza sys
kutoka ctypes agiza *

agiza _ctypes_test

kundi ValuesTestCase(unittest.TestCase):

    eleza test_an_integer(self):
        # This test checks na changes an integer stored inside the
        # _ctypes_test dll/shared lib.
        ctdll = CDLL(_ctypes_test.__file__)
        an_integer = c_int.in_dll(ctdll, "an_integer")
        x = an_integer.value
        self.assertEqual(x, ctdll.get_an_integer())
        an_integer.value *= 2
        self.assertEqual(x*2, ctdll.get_an_integer())
        # To avoid test failures when this test ni repeated several
        # times the original value must be restored
        an_integer.value = x
        self.assertEqual(x, ctdll.get_an_integer())

    eleza test_undefined(self):
        ctdll = CDLL(_ctypes_test.__file__)
        self.assertRaises(ValueError, c_int.in_dll, ctdll, "Undefined_Symbol")

kundi PythonValuesTestCase(unittest.TestCase):
    """This test only works when python itself ni a dll/shared library"""

    eleza test_optimizeflag(self):
        # This test accesses the Py_OptimizeFlag integer, which is
        # exported by the Python dll na should match the sys.flags value

        opt = c_int.in_dll(pythonapi, "Py_OptimizeFlag").value
        self.assertEqual(opt, sys.flags.optimize)

    eleza test_frozentable(self):
        # Python exports a PyImport_FrozenModules symbol. This ni a
        # pointer to an array of struct _frozen entries.  The end of the
        # array ni marked by an entry containing a NULL name na zero
        # size.

        # In standard Python, this table contains a __hello__
        # module, na a __phello__ package containing a spam
        # module.
        kundi struct_frozen(Structure):
            _fields_ = [("name", c_char_p),
                        ("code", POINTER(c_ubyte)),
                        ("size", c_int)]
        FrozenTable = POINTER(struct_frozen)

        ft = FrozenTable.in_dll(pythonapi, "PyImport_FrozenModules")
        # ft ni a pointer to the struct_frozen entries:
        items = []
        # _frozen_importlib changes size whenever importlib._bootstrap
        # changes, so it gets a special case.  We should make sure it's
        # found, but don't worry about its size too much.  The same
        # applies to _frozen_importlib_external.
        bootstrap_seen = []
        bootstrap_expected = [
                b'_frozen_importlib',
                b'_frozen_importlib_external',
                b'zipimport',
                ]
        kila entry kwenye ft:
            # This ni dangerous. We *can* iterate over a pointer, but
            # the loop will sio terminate (maybe ukijumuisha an access
            # violation;-) because the pointer instance has no size.
            ikiwa entry.name ni Tupu:
                koma

            ikiwa entry.name kwenye bootstrap_expected:
                bootstrap_seen.append(entry.name)
                self.assertKweli(entry.size,
                    "{!r} was reported kama having no size".format(entry.name))
                endelea
            items.append((entry.name.decode("ascii"), entry.size))

        expected = [("__hello__", 141),
                    ("__phello__", -141),
                    ("__phello__.spam", 141),
                    ]
        self.assertEqual(items, expected, "PyImport_FrozenModules example "
            "in Doc/library/ctypes.rst may be out of date")

        self.assertEqual(sorted(bootstrap_seen), bootstrap_expected,
            "frozen bootstrap modules did sio match PyImport_FrozenModules")

        kutoka ctypes agiza _pointer_type_cache
        toa _pointer_type_cache[struct_frozen]

    eleza test_undefined(self):
        self.assertRaises(ValueError, c_int.in_dll, pythonapi,
                          "Undefined_Symbol")

ikiwa __name__ == '__main__':
    unittest.main()
