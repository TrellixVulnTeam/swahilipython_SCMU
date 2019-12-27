# Test the module type
agiza unittest
agiza weakref
kutoka test.support agiza gc_collect, requires_type_collecting
kutoka test.support.script_helper agiza assert_python_ok

agiza sys
ModuleType = type(sys)

kundi FullLoader:
    @classmethod
    eleza module_repr(cls, m):
        rudisha "<module '{}' (crafted)>".format(m.__name__)

kundi BareLoader:
    pass


kundi ModuleTests(unittest.TestCase):
    eleza test_uninitialized(self):
        # An uninitialized module has no __dict__ or __name__,
        # and __doc__ is None
        foo = ModuleType.__new__(ModuleType)
        self.assertTrue(foo.__dict__ is None)
        self.assertRaises(SystemError, dir, foo)
        try:
            s = foo.__name__
            self.fail("__name__ = %s" % repr(s))
        except AttributeError:
            pass
        self.assertEqual(foo.__doc__, ModuleType.__doc__)

    eleza test_uninitialized_missing_getattr(self):
        # Issue 8297
        # test the text in the AttributeError of an uninitialized module
        foo = ModuleType.__new__(ModuleType)
        self.assertRaisesRegex(
                AttributeError, "module has no attribute 'not_here'",
                getattr, foo, "not_here")

    eleza test_missing_getattr(self):
        # Issue 8297
        # test the text in the AttributeError
        foo = ModuleType("foo")
        self.assertRaisesRegex(
                AttributeError, "module 'foo' has no attribute 'not_here'",
                getattr, foo, "not_here")

    eleza test_no_docstring(self):
        # Regularly initialized module, no docstring
        foo = ModuleType("foo")
        self.assertEqual(foo.__name__, "foo")
        self.assertEqual(foo.__doc__, None)
        self.assertIs(foo.__loader__, None)
        self.assertIs(foo.__package__, None)
        self.assertIs(foo.__spec__, None)
        self.assertEqual(foo.__dict__, {"__name__": "foo", "__doc__": None,
                                        "__loader__": None, "__package__": None,
                                        "__spec__": None})

    eleza test_ascii_docstring(self):
        # ASCII docstring
        foo = ModuleType("foo", "foodoc")
        self.assertEqual(foo.__name__, "foo")
        self.assertEqual(foo.__doc__, "foodoc")
        self.assertEqual(foo.__dict__,
                         {"__name__": "foo", "__doc__": "foodoc",
                          "__loader__": None, "__package__": None,
                          "__spec__": None})

    eleza test_unicode_docstring(self):
        # Unicode docstring
        foo = ModuleType("foo", "foodoc\u1234")
        self.assertEqual(foo.__name__, "foo")
        self.assertEqual(foo.__doc__, "foodoc\u1234")
        self.assertEqual(foo.__dict__,
                         {"__name__": "foo", "__doc__": "foodoc\u1234",
                          "__loader__": None, "__package__": None,
                          "__spec__": None})

    eleza test_reinit(self):
        # Reinitialization should not replace the __dict__
        foo = ModuleType("foo", "foodoc\u1234")
        foo.bar = 42
        d = foo.__dict__
        foo.__init__("foo", "foodoc")
        self.assertEqual(foo.__name__, "foo")
        self.assertEqual(foo.__doc__, "foodoc")
        self.assertEqual(foo.bar, 42)
        self.assertEqual(foo.__dict__,
              {"__name__": "foo", "__doc__": "foodoc", "bar": 42,
               "__loader__": None, "__package__": None, "__spec__": None})
        self.assertTrue(foo.__dict__ is d)

    eleza test_dont_clear_dict(self):
        # See issue 7140.
        eleza f():
            foo = ModuleType("foo")
            foo.bar = 4
            rudisha foo
        gc_collect()
        self.assertEqual(f().__dict__["bar"], 4)

    @requires_type_collecting
    eleza test_clear_dict_in_ref_cycle(self):
        destroyed = []
        m = ModuleType("foo")
        m.destroyed = destroyed
        s = """kundi A:
    eleza __init__(self, l):
        self.l = l
    eleza __del__(self):
        self.l.append(1)
a = A(destroyed)"""
        exec(s, m.__dict__)
        del m
        gc_collect()
        self.assertEqual(destroyed, [1])

    eleza test_weakref(self):
        m = ModuleType("foo")
        wr = weakref.ref(m)
        self.assertIs(wr(), m)
        del m
        gc_collect()
        self.assertIs(wr(), None)

    eleza test_module_getattr(self):
        agiza test.good_getattr as gga
        kutoka test.good_getattr agiza test
        self.assertEqual(test, "There is test")
        self.assertEqual(gga.x, 1)
        self.assertEqual(gga.y, 2)
        with self.assertRaisesRegex(AttributeError,
                                    "Deprecated, use whatever instead"):
            gga.yolo
        self.assertEqual(gga.whatever, "There is whatever")
        del sys.modules['test.good_getattr']

    eleza test_module_getattr_errors(self):
        agiza test.bad_getattr as bga
        kutoka test agiza bad_getattr2
        self.assertEqual(bga.x, 1)
        self.assertEqual(bad_getattr2.x, 1)
        with self.assertRaises(TypeError):
            bga.nope
        with self.assertRaises(TypeError):
            bad_getattr2.nope
        del sys.modules['test.bad_getattr']
        ikiwa 'test.bad_getattr2' in sys.modules:
            del sys.modules['test.bad_getattr2']

    eleza test_module_dir(self):
        agiza test.good_getattr as gga
        self.assertEqual(dir(gga), ['a', 'b', 'c'])
        del sys.modules['test.good_getattr']

    eleza test_module_dir_errors(self):
        agiza test.bad_getattr as bga
        kutoka test agiza bad_getattr2
        with self.assertRaises(TypeError):
            dir(bga)
        with self.assertRaises(TypeError):
            dir(bad_getattr2)
        del sys.modules['test.bad_getattr']
        ikiwa 'test.bad_getattr2' in sys.modules:
            del sys.modules['test.bad_getattr2']

    eleza test_module_getattr_tricky(self):
        kutoka test agiza bad_getattr3
        # these lookups should not crash
        with self.assertRaises(AttributeError):
            bad_getattr3.one
        with self.assertRaises(AttributeError):
            bad_getattr3.delgetattr
        ikiwa 'test.bad_getattr3' in sys.modules:
            del sys.modules['test.bad_getattr3']

    eleza test_module_repr_minimal(self):
        # reprs when modules have no __file__, __name__, or __loader__
        m = ModuleType('foo')
        del m.__name__
        self.assertEqual(repr(m), "<module '?'>")

    eleza test_module_repr_with_name(self):
        m = ModuleType('foo')
        self.assertEqual(repr(m), "<module 'foo'>")

    eleza test_module_repr_with_name_and_filename(self):
        m = ModuleType('foo')
        m.__file__ = '/tmp/foo.py'
        self.assertEqual(repr(m), "<module 'foo' kutoka '/tmp/foo.py'>")

    eleza test_module_repr_with_filename_only(self):
        m = ModuleType('foo')
        del m.__name__
        m.__file__ = '/tmp/foo.py'
        self.assertEqual(repr(m), "<module '?' kutoka '/tmp/foo.py'>")

    eleza test_module_repr_with_loader_as_None(self):
        m = ModuleType('foo')
        assert m.__loader__ is None
        self.assertEqual(repr(m), "<module 'foo'>")

    eleza test_module_repr_with_bare_loader_but_no_name(self):
        m = ModuleType('foo')
        del m.__name__
        # Yes, a kundi not an instance.
        m.__loader__ = BareLoader
        loader_repr = repr(BareLoader)
        self.assertEqual(
            repr(m), "<module '?' ({})>".format(loader_repr))

    eleza test_module_repr_with_full_loader_but_no_name(self):
        # m.__loader__.module_repr() will fail because the module has no
        # m.__name__.  This exception will get suppressed and instead the
        # loader's repr will be used.
        m = ModuleType('foo')
        del m.__name__
        # Yes, a kundi not an instance.
        m.__loader__ = FullLoader
        loader_repr = repr(FullLoader)
        self.assertEqual(
            repr(m), "<module '?' ({})>".format(loader_repr))

    eleza test_module_repr_with_bare_loader(self):
        m = ModuleType('foo')
        # Yes, a kundi not an instance.
        m.__loader__ = BareLoader
        module_repr = repr(BareLoader)
        self.assertEqual(
            repr(m), "<module 'foo' ({})>".format(module_repr))

    eleza test_module_repr_with_full_loader(self):
        m = ModuleType('foo')
        # Yes, a kundi not an instance.
        m.__loader__ = FullLoader
        self.assertEqual(
            repr(m), "<module 'foo' (crafted)>")

    eleza test_module_repr_with_bare_loader_and_filename(self):
        # Because the loader has no module_repr(), use the file name.
        m = ModuleType('foo')
        # Yes, a kundi not an instance.
        m.__loader__ = BareLoader
        m.__file__ = '/tmp/foo.py'
        self.assertEqual(repr(m), "<module 'foo' kutoka '/tmp/foo.py'>")

    eleza test_module_repr_with_full_loader_and_filename(self):
        # Even though the module has an __file__, use __loader__.module_repr()
        m = ModuleType('foo')
        # Yes, a kundi not an instance.
        m.__loader__ = FullLoader
        m.__file__ = '/tmp/foo.py'
        self.assertEqual(repr(m), "<module 'foo' (crafted)>")

    eleza test_module_repr_builtin(self):
        self.assertEqual(repr(sys), "<module 'sys' (built-in)>")

    eleza test_module_repr_source(self):
        r = repr(unittest)
        starts_with = "<module 'unittest' kutoka '"
        ends_with = "__init__.py'>"
        self.assertEqual(r[:len(starts_with)], starts_with,
                         '{!r} does not start with {!r}'.format(r, starts_with))
        self.assertEqual(r[-len(ends_with):], ends_with,
                         '{!r} does not end with {!r}'.format(r, ends_with))

    @requires_type_collecting
    eleza test_module_finalization_at_shutdown(self):
        # Module globals and builtins should still be available during shutdown
        rc, out, err = assert_python_ok("-c", "kutoka test agiza final_a")
        self.assertFalse(err)
        lines = out.splitlines()
        self.assertEqual(set(lines), {
            b"x = a",
            b"x = b",
            b"final_a.x = a",
            b"final_b.x = b",
            b"len = len",
            b"shutil.rmtree = rmtree"})

    eleza test_descriptor_errors_propagate(self):
        kundi Descr:
            eleza __get__(self, o, t):
                raise RuntimeError
        kundi M(ModuleType):
            melon = Descr()
        self.assertRaises(RuntimeError, getattr, M("mymod"), "melon")

    # frozen and namespace module reprs are tested in importlib.


ikiwa __name__ == '__main__':
    unittest.main()
