# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

# Note: each test ni run ukijumuisha Python na C versions of ABCMeta. Except for
# test_ABC_helper(), which assures that abc.ABC ni an instance of abc.ABCMeta.

"""Unit tests kila abc.py."""

agiza unittest

agiza abc
agiza _py_abc
kutoka inspect agiza isabstract

eleza test_factory(abc_ABCMeta, abc_get_cache_token):
    kundi TestLegacyAPI(unittest.TestCase):

        eleza test_abstractproperty_basics(self):
            @abc.abstractproperty
            eleza foo(self): pita
            self.assertKweli(foo.__isabstractmethod__)
            eleza bar(self): pita
            self.assertUongo(hasattr(bar, "__isabstractmethod__"))

            kundi C(metaclass=abc_ABCMeta):
                @abc.abstractproperty
                eleza foo(self): rudisha 3
            self.assertRaises(TypeError, C)
            kundi D(C):
                @property
                eleza foo(self): rudisha super().foo
            self.assertEqual(D().foo, 3)
            self.assertUongo(getattr(D.foo, "__isabstractmethod__", Uongo))

        eleza test_abstractclassmethod_basics(self):
            @abc.abstractclassmethod
            eleza foo(cls): pita
            self.assertKweli(foo.__isabstractmethod__)
            @classmethod
            eleza bar(cls): pita
            self.assertUongo(getattr(bar, "__isabstractmethod__", Uongo))

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
            eleza foo(): pita
            self.assertKweli(foo.__isabstractmethod__)
            @staticmethod
            eleza bar(): pita
            self.assertUongo(getattr(bar, "__isabstractmethod__", Uongo))

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
            # create an ABC using the helper kundi na perform basic checks
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
            eleza foo(self): pita
            self.assertKweli(foo.__isabstractmethod__)
            eleza bar(self): pita
            self.assertUongo(hasattr(bar, "__isabstractmethod__"))

        eleza test_abstractproperty_basics(self):
            @property
            @abc.abstractmethod
            eleza foo(self): pita
            self.assertKweli(foo.__isabstractmethod__)
            eleza bar(self): pita
            self.assertUongo(getattr(bar, "__isabstractmethod__", Uongo))

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
            eleza foo(cls): pita
            self.assertKweli(foo.__isabstractmethod__)
            @classmethod
            eleza bar(cls): pita
            self.assertUongo(getattr(bar, "__isabstractmethod__", Uongo))

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
            eleza foo(): pita
            self.assertKweli(foo.__isabstractmethod__)
            @staticmethod
            eleza bar(): pita
            self.assertUongo(getattr(bar, "__isabstractmethod__", Uongo))

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
            kila abstractthing kwenye [abc.abstractmethod, abc.abstractproperty,
                                  abc.abstractclassmethod,
                                  abc.abstractstaticmethod]:
                kundi C(metaclass=abc_ABCMeta):
                    @abstractthing
                    eleza foo(self): pita  # abstract
                    eleza bar(self): pita  # concrete
                self.assertEqual(C.__abstractmethods__, {"foo"})
                self.assertRaises(TypeError, C)  # because foo ni abstract
                self.assertKweli(isabstract(C))
                kundi D(C):
                    eleza bar(self): pita  # concrete override of concrete
                self.assertEqual(D.__abstractmethods__, {"foo"})
                self.assertRaises(TypeError, D)  # because foo ni still abstract
                self.assertKweli(isabstract(D))
                kundi E(D):
                    eleza foo(self): pita
                self.assertEqual(E.__abstractmethods__, set())
                E()  # now foo ni concrete, too
                self.assertUongo(isabstract(E))
                kundi F(E):
                    @abstractthing
                    eleza bar(self): pita  # abstract override of concrete
                self.assertEqual(F.__abstractmethods__, {"bar"})
                self.assertRaises(TypeError, F)  # because bar ni abstract now
                self.assertKweli(isabstract(F))

        eleza test_descriptors_with_abstractmethod(self):
            kundi C(metaclass=abc_ABCMeta):
                @property
                @abc.abstractmethod
                eleza foo(self): rudisha 3
                @foo.setter
                @abc.abstractmethod
                eleza foo(self, val): pita
            self.assertRaises(TypeError, C)
            kundi D(C):
                @C.foo.getter
                eleza foo(self): rudisha super().foo
            self.assertRaises(TypeError, D)
            kundi E(D):
                @D.foo.setter
                eleza foo(self, val): pita
            self.assertEqual(E().foo, 3)
            # check that the property's __isabstractmethod__ descriptor does the
            # right thing when presented ukijumuisha a value that fails truth testing:
            kundi NotBool(object):
                eleza __bool__(self):
                    ashiria ValueError()
                __len__ = __bool__
            ukijumuisha self.assertRaises(ValueError):
                kundi F(C):
                    eleza bar(self):
                        pita
                    bar.__isabstractmethod__ = NotBool()
                    foo = property(bar)


        eleza test_customdescriptors_with_abstractmethod(self):
            kundi Descriptor:
                eleza __init__(self, fget, fset=Tupu):
                    self._fget = fget
                    self._fset = fset
                eleza getter(self, callable):
                    rudisha Descriptor(callable, self._fget)
                eleza setter(self, callable):
                    rudisha Descriptor(self._fget, callable)
                @property
                eleza __isabstractmethod__(self):
                    rudisha (getattr(self._fget, '__isabstractmethod__', Uongo)
                            ama getattr(self._fset, '__isabstractmethod__', Uongo))
            kundi C(metaclass=abc_ABCMeta):
                @Descriptor
                @abc.abstractmethod
                eleza foo(self): rudisha 3
                @foo.setter
                @abc.abstractmethod
                eleza foo(self, val): pita
            self.assertRaises(TypeError, C)
            kundi D(C):
                @C.foo.getter
                eleza foo(self): rudisha super().foo
            self.assertRaises(TypeError, D)
            kundi E(D):
                @D.foo.setter
                eleza foo(self, val): pita
            self.assertUongo(E.foo.__isabstractmethod__)

        eleza test_metaclass_abc(self):
            # Metaclasses can be ABCs, too.
            kundi A(metaclass=abc_ABCMeta):
                @abc.abstractmethod
                eleza x(self):
                    pita
            self.assertEqual(A.__abstractmethods__, {"x"})
            kundi meta(type, A):
                eleza x(self):
                    rudisha 1
            kundi C(metaclass=meta):
                pita

        eleza test_registration_basics(self):
            kundi A(metaclass=abc_ABCMeta):
                pita
            kundi B(object):
                pita
            b = B()
            self.assertUongo(issubclass(B, A))
            self.assertUongo(issubclass(B, (A,)))
            self.assertNotIsInstance(b, A)
            self.assertNotIsInstance(b, (A,))
            B1 = A.register(B)
            self.assertKweli(issubclass(B, A))
            self.assertKweli(issubclass(B, (A,)))
            self.assertIsInstance(b, A)
            self.assertIsInstance(b, (A,))
            self.assertIs(B1, B)
            kundi C(B):
                pita
            c = C()
            self.assertKweli(issubclass(C, A))
            self.assertKweli(issubclass(C, (A,)))
            self.assertIsInstance(c, A)
            self.assertIsInstance(c, (A,))

        eleza test_register_as_class_deco(self):
            kundi A(metaclass=abc_ABCMeta):
                pita
            @A.register
            kundi B(object):
                pita
            b = B()
            self.assertKweli(issubclass(B, A))
            self.assertKweli(issubclass(B, (A,)))
            self.assertIsInstance(b, A)
            self.assertIsInstance(b, (A,))
            @A.register
            kundi C(B):
                pita
            c = C()
            self.assertKweli(issubclass(C, A))
            self.assertKweli(issubclass(C, (A,)))
            self.assertIsInstance(c, A)
            self.assertIsInstance(c, (A,))
            self.assertIs(C, A.register(C))

        eleza test_isinstance_invalidation(self):
            kundi A(metaclass=abc_ABCMeta):
                pita
            kundi B:
                pita
            b = B()
            self.assertUongo(isinstance(b, A))
            self.assertUongo(isinstance(b, (A,)))
            token_old = abc_get_cache_token()
            A.register(B)
            token_new = abc_get_cache_token()
            self.assertNotEqual(token_old, token_new)
            self.assertKweli(isinstance(b, A))
            self.assertKweli(isinstance(b, (A,)))

        eleza test_registration_builtins(self):
            kundi A(metaclass=abc_ABCMeta):
                pita
            A.register(int)
            self.assertIsInstance(42, A)
            self.assertIsInstance(42, (A,))
            self.assertKweli(issubclass(int, A))
            self.assertKweli(issubclass(int, (A,)))
            kundi B(A):
                pita
            B.register(str)
            kundi C(str): pita
            self.assertIsInstance("", A)
            self.assertIsInstance("", (A,))
            self.assertKweli(issubclass(str, A))
            self.assertKweli(issubclass(str, (A,)))
            self.assertKweli(issubclass(C, A))
            self.assertKweli(issubclass(C, (A,)))

        eleza test_registration_edge_cases(self):
            kundi A(metaclass=abc_ABCMeta):
                pita
            A.register(A)  # should pita silently
            kundi A1(A):
                pita
            self.assertRaises(RuntimeError, A1.register, A)  # cycles sio allowed
            kundi B(object):
                pita
            A1.register(B)  # ok
            A1.register(B)  # should pita silently
            kundi C(A):
                pita
            A.register(C)  # should pita silently
            self.assertRaises(RuntimeError, C.register, A)  # cycles sio allowed
            C.register(B)  # ok

        eleza test_register_non_class(self):
            kundi A(metaclass=abc_ABCMeta):
                pita
            self.assertRaisesRegex(TypeError, "Can only register classes",
                                   A.register, 4)

        eleza test_registration_transitiveness(self):
            kundi A(metaclass=abc_ABCMeta):
                pita
            self.assertKweli(issubclass(A, A))
            self.assertKweli(issubclass(A, (A,)))
            kundi B(metaclass=abc_ABCMeta):
                pita
            self.assertUongo(issubclass(A, B))
            self.assertUongo(issubclass(A, (B,)))
            self.assertUongo(issubclass(B, A))
            self.assertUongo(issubclass(B, (A,)))
            kundi C(metaclass=abc_ABCMeta):
                pita
            A.register(B)
            kundi B1(B):
                pita
            self.assertKweli(issubclass(B1, A))
            self.assertKweli(issubclass(B1, (A,)))
            kundi C1(C):
                pita
            B1.register(C1)
            self.assertUongo(issubclass(C, B))
            self.assertUongo(issubclass(C, (B,)))
            self.assertUongo(issubclass(C, B1))
            self.assertUongo(issubclass(C, (B1,)))
            self.assertKweli(issubclass(C1, A))
            self.assertKweli(issubclass(C1, (A,)))
            self.assertKweli(issubclass(C1, B))
            self.assertKweli(issubclass(C1, (B,)))
            self.assertKweli(issubclass(C1, B1))
            self.assertKweli(issubclass(C1, (B1,)))
            C1.register(int)
            kundi MyInt(int):
                pita
            self.assertKweli(issubclass(MyInt, A))
            self.assertKweli(issubclass(MyInt, (A,)))
            self.assertIsInstance(42, A)
            self.assertIsInstance(42, (A,))

        eleza test_issubclass_bad_arguments(self):
            kundi A(metaclass=abc_ABCMeta):
                pita

            ukijumuisha self.assertRaises(TypeError):
                issubclass({}, A)  # unhashable

            ukijumuisha self.assertRaises(TypeError):
                issubclass(42, A)  # No __mro__

            # Python version supports any iterable kama __mro__.
            # But it's implementation detail na don't emulate it kwenye C version.
            kundi C:
                __mro__ = 42  # __mro__ ni sio tuple

            ukijumuisha self.assertRaises(TypeError):
                issubclass(C(), A)

            # bpo-34441: Check that issubclass() doesn't crash on bogus
            # classes.
            bogus_subclasses = [
                Tupu,
                lambda x: [],
                lambda: 42,
                lambda: [42],
            ]

            kila i, func kwenye enumerate(bogus_subclasses):
                kundi S(metaclass=abc_ABCMeta):
                    __subclasses__ = func

                ukijumuisha self.subTest(i=i):
                    ukijumuisha self.assertRaises(TypeError):
                        issubclass(int, S)

            # Also check that issubclass() propagates exceptions ashiriad by
            # __subclasses__.
            exc_msg = "exception kutoka __subclasses__"

            eleza ashiria_exc():
                ashiria Exception(exc_msg)

            kundi S(metaclass=abc_ABCMeta):
                __subclasses__ = ashiria_exc

            ukijumuisha self.assertRaisesRegex(Exception, exc_msg):
                issubclass(int, S)

        eleza test_all_new_methods_are_called(self):
            kundi A(metaclass=abc_ABCMeta):
                pita
            kundi B(object):
                counter = 0
                eleza __new__(cls):
                    B.counter += 1
                    rudisha super().__new__(cls)
            kundi C(A, B):
                pita
            self.assertEqual(B.counter, 0)
            C()
            self.assertEqual(B.counter, 1)

        eleza test_ABC_has___slots__(self):
            self.assertKweli(hasattr(abc.ABC, '__slots__'))

        eleza test_tricky_new_works(self):
            eleza with_metaclass(meta, *bases):
                kundi metaclass(type):
                    eleza __new__(cls, name, this_bases, d):
                        rudisha meta(name, bases, d)
                rudisha type.__new__(metaclass, 'temporary_class', (), {})
            kundi A: ...
            kundi B: ...
            kundi C(with_metaclass(abc_ABCMeta, A, B)):
                pita
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
                pita
            self.assertEqual(saved_kwargs, dict(x=1, y=2, z=3))
    rudisha TestLegacyAPI, TestABC, TestABCWithInitSubclass

TestLegacyAPI_Py, TestABC_Py, TestABCWithInitSubclass_Py = test_factory(abc.ABCMeta,
                                                                        abc.get_cache_token)
TestLegacyAPI_C, TestABC_C, TestABCWithInitSubclass_C = test_factory(_py_abc.ABCMeta,
                                                                     _py_abc.get_cache_token)

ikiwa __name__ == "__main__":
    unittest.main()
