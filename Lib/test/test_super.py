"""Unit tests for zero-argument super() & related machinery."""

agiza unittest


kundi A:
    eleza f(self):
        rudisha 'A'
    @classmethod
    eleza cm(cls):
        rudisha (cls, 'A')

kundi B(A):
    eleza f(self):
        rudisha super().f() + 'B'
    @classmethod
    eleza cm(cls):
        rudisha (cls, super().cm(), 'B')

kundi C(A):
    eleza f(self):
        rudisha super().f() + 'C'
    @classmethod
    eleza cm(cls):
        rudisha (cls, super().cm(), 'C')

kundi D(C, B):
    eleza f(self):
        rudisha super().f() + 'D'
    eleza cm(cls):
        rudisha (cls, super().cm(), 'D')

kundi E(D):
    pass

kundi F(E):
    f = E.f

kundi G(A):
    pass


kundi TestSuper(unittest.TestCase):

    eleza tearDown(self):
        # This fixes the damage that test_various___class___pathologies does.
        nonlocal __class__
        __class__ = TestSuper

    eleza test_basics_working(self):
        self.assertEqual(D().f(), 'ABCD')

    eleza test_class_getattr_working(self):
        self.assertEqual(D.f(D()), 'ABCD')

    eleza test_subclass_no_override_working(self):
        self.assertEqual(E().f(), 'ABCD')
        self.assertEqual(E.f(E()), 'ABCD')

    eleza test_unbound_method_transfer_working(self):
        self.assertEqual(F().f(), 'ABCD')
        self.assertEqual(F.f(F()), 'ABCD')

    eleza test_class_methods_still_working(self):
        self.assertEqual(A.cm(), (A, 'A'))
        self.assertEqual(A().cm(), (A, 'A'))
        self.assertEqual(G.cm(), (G, 'A'))
        self.assertEqual(G().cm(), (G, 'A'))

    eleza test_super_in_class_methods_working(self):
        d = D()
        self.assertEqual(d.cm(), (d, (D, (D, (D, 'A'), 'B'), 'C'), 'D'))
        e = E()
        self.assertEqual(e.cm(), (e, (E, (E, (E, 'A'), 'B'), 'C'), 'D'))

    eleza test_super_with_closure(self):
        # Issue4360: super() did not work in a function that
        # contains a closure
        kundi E(A):
            eleza f(self):
                eleza nested():
                    self
                rudisha super().f() + 'E'

        self.assertEqual(E().f(), 'AE')

    eleza test_various___class___pathologies(self):
        # See issue #12370
        kundi X(A):
            eleza f(self):
                rudisha super().f()
            __class__ = 413
        x = X()
        self.assertEqual(x.f(), 'A')
        self.assertEqual(x.__class__, 413)
        kundi X:
            x = __class__
            eleza f():
                __class__
        self.assertIs(X.x, type(self))
        with self.assertRaises(NameError) as e:
            exec("""kundi X:
                __class__
                eleza f():
                    __class__""", globals(), {})
        self.assertIs(type(e.exception), NameError) # Not UnboundLocalError
        kundi X:
            global __class__
            __class__ = 42
            eleza f():
                __class__
        self.assertEqual(globals()["__class__"], 42)
        del globals()["__class__"]
        self.assertNotIn("__class__", X.__dict__)
        kundi X:
            nonlocal __class__
            __class__ = 42
            eleza f():
                __class__
        self.assertEqual(__class__, 42)

    eleza test___class___instancemethod(self):
        # See issue #14857
        kundi X:
            eleza f(self):
                rudisha __class__
        self.assertIs(X().f(), X)

    eleza test___class___classmethod(self):
        # See issue #14857
        kundi X:
            @classmethod
            eleza f(cls):
                rudisha __class__
        self.assertIs(X.f(), X)

    eleza test___class___staticmethod(self):
        # See issue #14857
        kundi X:
            @staticmethod
            eleza f():
                rudisha __class__
        self.assertIs(X.f(), X)

    eleza test___class___new(self):
        # See issue #23722
        # Ensure zero-arg super() works as soon as type.__new__() is completed
        test_kundi = None

        kundi Meta(type):
            eleza __new__(cls, name, bases, namespace):
                nonlocal test_class
                self = super().__new__(cls, name, bases, namespace)
                test_kundi = self.f()
                rudisha self

        kundi A(metaclass=Meta):
            @staticmethod
            eleza f():
                rudisha __class__

        self.assertIs(test_class, A)

    eleza test___class___delayed(self):
        # See issue #23722
        test_namespace = None

        kundi Meta(type):
            eleza __new__(cls, name, bases, namespace):
                nonlocal test_namespace
                test_namespace = namespace
                rudisha None

        kundi A(metaclass=Meta):
            @staticmethod
            eleza f():
                rudisha __class__

        self.assertIs(A, None)

        B = type("B", (), test_namespace)
        self.assertIs(B.f(), B)

    eleza test___class___mro(self):
        # See issue #23722
        test_kundi = None

        kundi Meta(type):
            eleza mro(self):
                # self.f() doesn't work yet...
                self.__dict__["f"]()
                rudisha super().mro()

        kundi A(metaclass=Meta):
            eleza f():
                nonlocal test_class
                test_kundi = __class__

        self.assertIs(test_class, A)

    eleza test___classcell___expected_behaviour(self):
        # See issue #23722
        kundi Meta(type):
            eleza __new__(cls, name, bases, namespace):
                nonlocal namespace_snapshot
                namespace_snapshot = namespace.copy()
                rudisha super().__new__(cls, name, bases, namespace)

        # __classcell__ is injected into the kundi namespace by the compiler
        # when at least one method needs it, and should be omitted otherwise
        namespace_snapshot = None
        kundi WithoutClassRef(metaclass=Meta):
            pass
        self.assertNotIn("__classcell__", namespace_snapshot)

        # With zero-arg super() or an explicit __class__ reference,
        # __classcell__ is the exact cell reference to be populated by
        # type.__new__
        namespace_snapshot = None
        kundi WithClassRef(metaclass=Meta):
            eleza f(self):
                rudisha __class__

        class_cell = namespace_snapshot["__classcell__"]
        method_closure = WithClassRef.f.__closure__
        self.assertEqual(len(method_closure), 1)
        self.assertIs(class_cell, method_closure[0])
        # Ensure the cell reference *doesn't* get turned into an attribute
        with self.assertRaises(AttributeError):
            WithClassRef.__classcell__

    eleza test___classcell___missing(self):
        # See issue #23722
        # Some metaclasses may not pass the original namespace to type.__new__
        # We test that case here by forcibly deleting __classcell__
        kundi Meta(type):
            eleza __new__(cls, name, bases, namespace):
                namespace.pop('__classcell__', None)
                rudisha super().__new__(cls, name, bases, namespace)

        # The default case should continue to work without any errors
        kundi WithoutClassRef(metaclass=Meta):
            pass

        # With zero-arg super() or an explicit __class__ reference, we expect
        # __build_class__ to raise a RuntimeError complaining that
        # __class__ was not set, and asking ikiwa __classcell__ was propagated
        # to type.__new__.
        expected_error = '__class__ not set.*__classcell__ propagated'
        with self.assertRaisesRegex(RuntimeError, expected_error):
            kundi WithClassRef(metaclass=Meta):
                eleza f(self):
                    rudisha __class__

    eleza test___classcell___overwrite(self):
        # See issue #23722
        # Overwriting __classcell__ with nonsense is explicitly prohibited
        kundi Meta(type):
            eleza __new__(cls, name, bases, namespace, cell):
                namespace['__classcell__'] = cell
                rudisha super().__new__(cls, name, bases, namespace)

        for bad_cell in (None, 0, "", object()):
            with self.subTest(bad_cell=bad_cell):
                with self.assertRaises(TypeError):
                    kundi A(metaclass=Meta, cell=bad_cell):
                        pass

    eleza test___classcell___wrong_cell(self):
        # See issue #23722
        # Pointing the cell reference at the wrong kundi is also prohibited
        kundi Meta(type):
            eleza __new__(cls, name, bases, namespace):
                cls = super().__new__(cls, name, bases, namespace)
                B = type("B", (), namespace)
                rudisha cls

        with self.assertRaises(TypeError):
            kundi A(metaclass=Meta):
                eleza f(self):
                    rudisha __class__

    eleza test_obscure_super_errors(self):
        eleza f():
            super()
        self.assertRaises(RuntimeError, f)
        eleza f(x):
            del x
            super()
        self.assertRaises(RuntimeError, f, None)
        kundi X:
            eleza f(x):
                nonlocal __class__
                del __class__
                super()
        self.assertRaises(RuntimeError, X().f)

    eleza test_cell_as_self(self):
        kundi X:
            eleza meth(self):
                super()

        eleza f():
            k = X()
            eleza g():
                rudisha k
            rudisha g
        c = f().__closure__[0]
        self.assertRaises(TypeError, X.meth, c)

    eleza test_super_init_leaks(self):
        # Issue #26718: super.__init__ leaked memory ikiwa called multiple times.
        # This will be caught by regrtest.py -R ikiwa this leak.
        # NOTE: Despite the use in the test a direct call of super.__init__
        # is not endorsed.
        sp = super(float, 1.0)
        for i in range(1000):
            super.__init__(sp, int, i)


ikiwa __name__ == "__main__":
    unittest.main()
