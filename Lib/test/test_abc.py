# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

# Note: each test is run with Python and C versions of ABCMeta. Except for
# test_ABC_helper(), which assures that abc.ABC is an instance of abc.ABCMeta.

"""Unit tests for abc.py."""

agiza unittest

agiza abc
agiza _py_abc
kutoka inspect agiza isabstract

eleza test_factory(abc_ABCMeta, abc_get_cache_token):
    kundi TestLegacyAPI(unittest.TestCase):

        eleza test_abstractproperty_basics(self):
            @abc.abstractproperty
            eleza foo(self): pass
            self.assertTrue(foo.__isabstractmethod__)
            eleza bar(self): pass
            self.assertFalse(hasattr(bar, "__isabstractmethod__"))

            kundi C(metaclass=abc_ABCMeta):
                @abc.abstractproperty
                eleza foo(self): rudisha 3
            self.assertRaises(TypeError, C)
            kundi D(C):
                @property
                eleza foo(self): rudisha super().foo
            self.assertEqual(D().foo, 3)
            self.assertFalse(getattr(D.foo, "__isabstractmethod__", False))

        eleza test_abstractclassmethod_basics(self):
            @abc.abstractclassmethod
            eleza foo(cls): pass
            self.assertTrue(foo.__isabstractmethod__)
            @classmethod
            eleza bar(cls): pass
            self.assertFalse(getattr(bar, "__isabstractmethod__", False))

            kundi C(metaclass=abc_ABCMeta):
                @abc.abstractclassmethod
                eleza foo(cls): rudisha cls.__name__
            self.assertRaises(TypeError, C)
            kundi D(C):
                @classmethod
                eleza foo(cls): rudisha super().foo()
            self.assertEqual(D.foo(), 'D')
            self.assertEqual(D().foo(), 'D')

        eleza test_abstractstaticmethod_basics(self):
            @abc.abstractstaticmethod
            eleza foo(): pass
            self.assertTrue(foo.__isabstractmethod__)
            @staticmethod
            eleza bar(): pass
            self.assertFalse(getattr(bar, "__isabstractmethod__", False))

            kundi C(metaclass=abc_ABCMeta):
                @abc.abstractstaticmethod
                eleza foo(): rudisha 3
            self.assertRaises(TypeError, C)
            kundi D(C):
                @staticmethod
                eleza foo(): rudisha 4
            self.assertEqual(D.foo(), 4)
            self.assertEqual(D().foo(), 4)


    kundi TestABC(unittest.TestCase):

        eleza test_ABC_helper(self):
            # create an ABC using the helper kundi and perform basic checks
            kundi C(abc.ABC):
                @classmethod
                @abc.abstractmethod
                eleza foo(cls): rudisha cls.__name__
            self.assertEqual(type(C), abc.ABCMeta)
            self.assertRaises(TypeError, C)
            kundi D(C):
                @classmethod
                eleza foo(cls): rudisha super().foo()
            self.assertEqual(D.foo(), 'D')

        eleza test_abstractmethod_basics(self):
            @abc.abstractmethod
            eleza foo(self): pass
            self.assertTrue(foo.__isabstractmethod__)
            eleza bar(self): pass
            self.assertFalse(hasattr(bar, "__isabstractmethod__"))

        eleza test_abstractproperty_basics(self):
            @property
            @abc.abstractmethod
            eleza foo(self): pass
            self.assertTrue(foo.__isabstractmethod__)
            eleza bar(self): pass
            self.assertFalse(getattr(bar, "__isabstractmethod__", False))

            kundi C(metaclass=abc_ABCMeta):
                @property
                @abc.abstractmethod
                eleza foo(self): rudisha 3
            self.assertRaises(TypeError, C)
            kundi D(C):
                @C.foo.getter
                eleza foo(self): rudisha super().foo
            self.assertEqual(D().foo, 3)

        eleza test_abstractclassmethod_basics(self):
            @classmethod
            @abc.abstractmethod
            eleza foo(cls): pass
            self.assertTrue(foo.__isabstractmethod__)
            @classmethod
            eleza bar(cls): pass
            self.assertFalse(getattr(bar, "__isabstractmethod__", False))

            kundi C(metaclass=abc_ABCMeta):
                @classmethod
                @abc.abstractmethod
                eleza foo(cls): rudisha cls.__name__
            self.assertRaises(TypeError, C)
            kundi D(C):
                @classmethod
                eleza foo(cls): rudisha super().foo()
            self.assertEqual(D.foo(), 'D')
            self.assertEqual(D().foo(), 'D')

        eleza test_abstractstaticmethod_basics(self):
            @staticmethod
            @abc.abstractmethod
            eleza foo(): pass
            self.assertTrue(foo.__isabstractmethod__)
            @staticmethod
            eleza bar(): pass
            self.assertFalse(getattr(bar, "__isabstractmethod__", False))

            kundi C(metaclass=abc_ABCMeta):
                @staticmethod
                @abc.abstractmethod
                eleza foo(): rudisha 3
            self.assertRaises(TypeError, C)
            kundi D(C):
                @staticmethod
                eleza foo(): rudisha 4
            self.assertEqual(D.foo(), 4)
            self.assertEqual(D().foo(), 4)

        eleza test_abstractmethod_integration(self):
            for abstractthing in [abc.abstractmethod, abc.abstractproperty,
                                  abc.abstractclassmethod,
                                  abc.abstractstaticmethod]:
                kundi C(metaclass=abc_ABCMeta):
                    @abstractthing
                    eleza foo(self): pass  # abstract
                    eleza bar(self): pass  # concrete
                self.assertEqual(C.__abstractmethods__, {"foo"})
                self.assertRaises(TypeError, C)  # because foo is abstract
                self.assertTrue(isabstract(C))
                kundi D(C):
                    eleza bar(self): pass  # concrete override of concrete
                self.assertEqual(D.__abstractmethods__, {"foo"})
                self.assertRaises(TypeError, D)  # because foo is still abstract
                self.assertTrue(isabstract(D))
                kundi E(D):
                    eleza foo(self): pass
                self.assertEqual(E.__abstractmethods__, set())
                E()  # now foo is concrete, too
                self.assertFalse(isabstract(E))
                kundi F(E):
                    @abstractthing
                    eleza bar(self): pass  # abstract override of concrete
                self.assertEqual(F.__abstractmethods__, {"bar"})
                self.assertRaises(TypeError, F)  # because bar is abstract now
                self.assertTrue(isabstract(F))

        eleza test_descriptors_with_abstractmethod(self):
            kundi C(metaclass=abc_ABCMeta):
                @property
                @abc.abstractmethod
                eleza foo(self): rudisha 3
                @foo.setter
                @abc.abstractmethod
                eleza foo(self, val): pass
            self.assertRaises(TypeError, C)
            kundi D(C):
                @C.foo.getter
                eleza foo(self): rudisha super().foo
            self.assertRaises(TypeError, D)
            kundi E(D):
                @D.foo.setter
                eleza foo(self, val): pass
            self.assertEqual(E().foo, 3)
            # check that the property's __isabstractmethod__ descriptor does the
            # right thing when presented with a value that fails truth testing:
            kundi NotBool(object):
                eleza __bool__(self):
                    raise ValueError()
                __len__ = __bool__
            with self.assertRaises(ValueError):
                kundi F(C):
                    eleza bar(self):
                        pass
                    bar.__isabstractmethod__ = NotBool()
                    foo = property(bar)


        eleza test_customdescriptors_with_abstractmethod(self):
            kundi Descriptor:
                eleza __init__(self, fget, fset=None):
                    self._fget = fget
                    self._fset = fset
                eleza getter(self, callable):
                    rudisha Descriptor(callable, self._fget)
                eleza setter(self, callable):
                    rudisha Descriptor(self._fget, callable)
                @property
                eleza __isabstractmethod__(self):
                    rudisha (getattr(self._fget, '__isabstractmethod__', False)
                            or getattr(self._fset, '__isabstractmethod__', False))
            kundi C(metaclass=abc_ABCMeta):
                @Descriptor
                @abc.abstractmethod
                eleza foo(self): rudisha 3
                @foo.setter
                @abc.abstractmethod
                eleza foo(self, val): pass
            self.assertRaises(TypeError, C)
            kundi D(C):
                @C.foo.getter
                eleza foo(self): rudisha super().foo
            self.assertRaises(TypeError, D)
            kundi E(D):
                @D.foo.setter
                eleza foo(self, val): pass
            self.assertFalse(E.foo.__isabstractmethod__)

        eleza test_metaclass_abc(self):
            # Metaclasses can be ABCs, too.
            kundi A(metaclass=abc_ABCMeta):
                @abc.abstractmethod
                eleza x(self):
                    pass
            self.assertEqual(A.__abstractmethods__, {"x"})
            kundi meta(type, A):
                eleza x(self):
                    rudisha 1
            kundi C(metaclass=meta):
                pass

        eleza test_registration_basics(self):
            kundi A(metaclass=abc_ABCMeta):
                pass
            kundi B(object):
                pass
            b = B()
            self.assertFalse(issubclass(B, A))
            self.assertFalse(issubclass(B, (A,)))
            self.assertNotIsInstance(b, A)
            self.assertNotIsInstance(b, (A,))
            B1 = A.register(B)
            self.assertTrue(issubclass(B, A))
            self.assertTrue(issubclass(B, (A,)))
            self.assertIsInstance(b, A)
            self.assertIsInstance(b, (A,))
            self.assertIs(B1, B)
            kundi C(B):
                pass
            c = C()
            self.assertTrue(issubclass(C, A))
            self.assertTrue(issubclass(C, (A,)))
            self.assertIsInstance(c, A)
            self.assertIsInstance(c, (A,))

        eleza test_register_as_class_deco(self):
            kundi A(metaclass=abc_ABCMeta):
                pass
            @A.register
            kundi B(object):
                pass
            b = B()
            self.assertTrue(issubclass(B, A))
            self.assertTrue(issubclass(B, (A,)))
            self.assertIsInstance(b, A)
            self.assertIsInstance(b, (A,))
            @A.register
            kundi C(B):
                pass
            c = C()
            self.assertTrue(issubclass(C, A))
            self.assertTrue(issubclass(C, (A,)))
            self.assertIsInstance(c, A)
            self.assertIsInstance(c, (A,))
            self.assertIs(C, A.register(C))

        eleza test_isinstance_invalidation(self):
            kundi A(metaclass=abc_ABCMeta):
                pass
            kundi B:
                pass
            b = B()
            self.assertFalse(isinstance(b, A))
            self.assertFalse(isinstance(b, (A,)))
            token_old = abc_get_cache_token()
            A.register(B)
            token_new = abc_get_cache_token()
            self.assertNotEqual(token_old, token_new)
            self.assertTrue(isinstance(b, A))
            self.assertTrue(isinstance(b, (A,)))

        eleza test_registration_builtins(self):
            kundi A(metaclass=abc_ABCMeta):
                pass
            A.register(int)
            self.assertIsInstance(42, A)
            self.assertIsInstance(42, (A,))
            self.assertTrue(issubclass(int, A))
            self.assertTrue(issubclass(int, (A,)))
            kundi B(A):
                pass
            B.register(str)
            kundi C(str): pass
            self.assertIsInstance("", A)
            self.assertIsInstance("", (A,))
            self.assertTrue(issubclass(str, A))
            self.assertTrue(issubclass(str, (A,)))
            self.assertTrue(issubclass(C, A))
            self.assertTrue(issubclass(C, (A,)))

        eleza test_registration_edge_cases(self):
            kundi A(metaclass=abc_ABCMeta):
                pass
            A.register(A)  # should pass silently
            kundi A1(A):
                pass
            self.assertRaises(RuntimeError, A1.register, A)  # cycles not allowed
            kundi B(object):
                pass
            A1.register(B)  # ok
            A1.register(B)  # should pass silently
            kundi C(A):
                pass
            A.register(C)  # should pass silently
            self.assertRaises(RuntimeError, C.register, A)  # cycles not allowed
            C.register(B)  # ok

        eleza test_register_non_class(self):
            kundi A(metaclass=abc_ABCMeta):
                pass
            self.assertRaisesRegex(TypeError, "Can only register classes",
                                   A.register, 4)

        eleza test_registration_transitiveness(self):
            kundi A(metaclass=abc_ABCMeta):
                pass
            self.assertTrue(issubclass(A, A))
            self.assertTrue(issubclass(A, (A,)))
            kundi B(metaclass=abc_ABCMeta):
                pass
            self.assertFalse(issubclass(A, B))
            self.assertFalse(issubclass(A, (B,)))
            self.assertFalse(issubclass(B, A))
            self.assertFalse(issubclass(B, (A,)))
            kundi C(metaclass=abc_ABCMeta):
                pass
            A.register(B)
            kundi B1(B):
                pass
            self.assertTrue(issubclass(B1, A))
            self.assertTrue(issubclass(B1, (A,)))
            kundi C1(C):
                pass
            B1.register(C1)
            self.assertFalse(issubclass(C, B))
            self.assertFalse(issubclass(C, (B,)))
            self.assertFalse(issubclass(C, B1))
            self.assertFalse(issubclass(C, (B1,)))
            self.assertTrue(issubclass(C1, A))
            self.assertTrue(issubclass(C1, (A,)))
            self.assertTrue(issubclass(C1, B))
            self.assertTrue(issubclass(C1, (B,)))
            self.assertTrue(issubclass(C1, B1))
            self.assertTrue(issubclass(C1, (B1,)))
            C1.register(int)
            kundi MyInt(int):
                pass
            self.assertTrue(issubclass(MyInt, A))
            self.assertTrue(issubclass(MyInt, (A,)))
            self.assertIsInstance(42, A)
            self.assertIsInstance(42, (A,))

        eleza test_issubclass_bad_arguments(self):
            kundi A(metaclass=abc_ABCMeta):
                pass

            with self.assertRaises(TypeError):
                issubclass({}, A)  # unhashable

            with self.assertRaises(TypeError):
                issubclass(42, A)  # No __mro__

            # Python version supports any iterable as __mro__.
            # But it's implementation detail and don't emulate it in C version.
            kundi C:
                __mro__ = 42  # __mro__ is not tuple

            with self.assertRaises(TypeError):
                issubclass(C(), A)

            # bpo-34441: Check that issubclass() doesn't crash on bogus
            # classes.
            bogus_subclasses = [
                None,
                lambda x: [],
                lambda: 42,
                lambda: [42],
            ]

            for i, func in enumerate(bogus_subclasses):
                kundi S(metaclass=abc_ABCMeta):
                    __subclasses__ = func

                with self.subTest(i=i):
                    with self.assertRaises(TypeError):
                        issubclass(int, S)

            # Also check that issubclass() propagates exceptions raised by
            # __subclasses__.
            exc_msg = "exception kutoka __subclasses__"

            eleza raise_exc():
                raise Exception(exc_msg)

            kundi S(metaclass=abc_ABCMeta):
                __subclasses__ = raise_exc

            with self.assertRaisesRegex(Exception, exc_msg):
                issubclass(int, S)

        eleza test_all_new_methods_are_called(self):
            kundi A(metaclass=abc_ABCMeta):
                pass
            kundi B(object):
                counter = 0
                eleza __new__(cls):
                    B.counter += 1
                    rudisha super().__new__(cls)
            kundi C(A, B):
                pass
            self.assertEqual(B.counter, 0)
            C()
            self.assertEqual(B.counter, 1)

        eleza test_ABC_has___slots__(self):
            self.assertTrue(hasattr(abc.ABC, '__slots__'))

        eleza test_tricky_new_works(self):
            eleza with_metaclass(meta, *bases):
                kundi metaclass(type):
                    eleza __new__(cls, name, this_bases, d):
                        rudisha meta(name, bases, d)
                rudisha type.__new__(metaclass, 'temporary_class', (), {})
            kundi A: ...
            kundi B: ...
            kundi C(with_metaclass(abc_ABCMeta, A, B)):
                pass
            self.assertEqual(C.__class__, abc_ABCMeta)


    kundi TestABCWithInitSubclass(unittest.TestCase):
        eleza test_works_with_init_subclass(self):
            kundi abc_ABC(metaclass=abc_ABCMeta):
                __slots__ = ()
            saved_kwargs = {}
            kundi ReceivesClassKwargs:
                eleza __init_subclass__(cls, **kwargs):
                    super().__init_subclass__()
                    saved_kwargs.update(kwargs)
            kundi Receiver(ReceivesClassKwargs, abc_ABC, x=1, y=2, z=3):
                pass
            self.assertEqual(saved_kwargs, dict(x=1, y=2, z=3))
    rudisha TestLegacyAPI, TestABC, TestABCWithInitSubclass

TestLegacyAPI_Py, TestABC_Py, TestABCWithInitSubclass_Py = test_factory(abc.ABCMeta,
                                                                        abc.get_cache_token)
TestLegacyAPI_C, TestABC_C, TestABCWithInitSubclass_C = test_factory(_py_abc.ABCMeta,
                                                                     _py_abc.get_cache_token)

ikiwa __name__ == "__main__":
    unittest.main()
