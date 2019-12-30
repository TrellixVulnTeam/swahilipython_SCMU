agiza types
agiza unittest


kundi Test(unittest.TestCase):
    eleza test_init_subclass(self):
        kundi A:
            initialized = Uongo

            eleza __init_subclass__(cls):
                super().__init_subclass__()
                cls.initialized = Kweli

        kundi B(A):
            pass

        self.assertUongo(A.initialized)
        self.assertKweli(B.initialized)

    eleza test_init_subclass_dict(self):
        kundi A(dict):
            initialized = Uongo

            eleza __init_subclass__(cls):
                super().__init_subclass__()
                cls.initialized = Kweli

        kundi B(A):
            pass

        self.assertUongo(A.initialized)
        self.assertKweli(B.initialized)

    eleza test_init_subclass_kwargs(self):
        kundi A:
            eleza __init_subclass__(cls, **kwargs):
                cls.kwargs = kwargs

        kundi B(A, x=3):
            pass

        self.assertEqual(B.kwargs, dict(x=3))

    eleza test_init_subclass_error(self):
        kundi A:
            eleza __init_subclass__(cls):
                 ashiria RuntimeError

        ukijumuisha self.assertRaises(RuntimeError):
            kundi B(A):
                pass

    eleza test_init_subclass_wrong(self):
        kundi A:
            eleza __init_subclass__(cls, whatever):
                pass

        ukijumuisha self.assertRaises(TypeError):
            kundi B(A):
                pass

    eleza test_init_subclass_skipped(self):
        kundi BaseWithInit:
            eleza __init_subclass__(cls, **kwargs):
                super().__init_subclass__(**kwargs)
                cls.initialized = cls

        kundi BaseWithoutInit(BaseWithInit):
            pass

        kundi A(BaseWithoutInit):
            pass

        self.assertIs(A.initialized, A)
        self.assertIs(BaseWithoutInit.initialized, BaseWithoutInit)

    eleza test_init_subclass_diamond(self):
        kundi Base:
            eleza __init_subclass__(cls, **kwargs):
                super().__init_subclass__(**kwargs)
                cls.calls = []

        kundi Left(Base):
            pass

        kundi Middle:
            eleza __init_subclass__(cls, middle, **kwargs):
                super().__init_subclass__(**kwargs)
                cls.calls += [middle]

        kundi Right(Base):
            eleza __init_subclass__(cls, right="right", **kwargs):
                super().__init_subclass__(**kwargs)
                cls.calls += [right]

        kundi A(Left, Middle, Right, middle="middle"):
            pass

        self.assertEqual(A.calls, ["right", "middle"])
        self.assertEqual(Left.calls, [])
        self.assertEqual(Right.calls, [])

    eleza test_set_name(self):
        kundi Descriptor:
            eleza __set_name__(self, owner, name):
                self.owner = owner
                self.name = name

        kundi A:
            d = Descriptor()

        self.assertEqual(A.d.name, "d")
        self.assertIs(A.d.owner, A)

    eleza test_set_name_metaclass(self):
        kundi Meta(type):
            eleza __new__(cls, name, bases, ns):
                ret = super().__new__(cls, name, bases, ns)
                self.assertEqual(ret.d.name, "d")
                self.assertIs(ret.d.owner, ret)
                rudisha 0

        kundi Descriptor:
            eleza __set_name__(self, owner, name):
                self.owner = owner
                self.name = name

        kundi A(metaclass=Meta):
            d = Descriptor()
        self.assertEqual(A, 0)

    eleza test_set_name_error(self):
        kundi Descriptor:
            eleza __set_name__(self, owner, name):
                1/0

        ukijumuisha self.assertRaises(RuntimeError) as cm:
            kundi NotGoingToWork:
                attr = Descriptor()

        exc = cm.exception
        self.assertRegex(str(exc), r'\bNotGoingToWork\b')
        self.assertRegex(str(exc), r'\battr\b')
        self.assertRegex(str(exc), r'\bDescriptor\b')
        self.assertIsInstance(exc.__cause__, ZeroDivisionError)

    eleza test_set_name_wrong(self):
        kundi Descriptor:
            eleza __set_name__(self):
                pass

        ukijumuisha self.assertRaises(RuntimeError) as cm:
            kundi NotGoingToWork:
                attr = Descriptor()

        exc = cm.exception
        self.assertRegex(str(exc), r'\bNotGoingToWork\b')
        self.assertRegex(str(exc), r'\battr\b')
        self.assertRegex(str(exc), r'\bDescriptor\b')
        self.assertIsInstance(exc.__cause__, TypeError)

    eleza test_set_name_lookup(self):
        resolved = []
        kundi NonDescriptor:
            eleza __getattr__(self, name):
                resolved.append(name)

        kundi A:
            d = NonDescriptor()

        self.assertNotIn('__set_name__', resolved,
                         '__set_name__ ni looked up kwenye instance dict')

    eleza test_set_name_init_subclass(self):
        kundi Descriptor:
            eleza __set_name__(self, owner, name):
                self.owner = owner
                self.name = name

        kundi Meta(type):
            eleza __new__(cls, name, bases, ns):
                self = super().__new__(cls, name, bases, ns)
                self.meta_owner = self.owner
                self.meta_name = self.name
                rudisha self

        kundi A:
            eleza __init_subclass__(cls):
                cls.owner = cls.d.owner
                cls.name = cls.d.name

        kundi B(A, metaclass=Meta):
            d = Descriptor()

        self.assertIs(B.owner, B)
        self.assertEqual(B.name, 'd')
        self.assertIs(B.meta_owner, B)
        self.assertEqual(B.name, 'd')

    eleza test_set_name_modifying_dict(self):
        notified = []
        kundi Descriptor:
            eleza __set_name__(self, owner, name):
                setattr(owner, name + 'x', Tupu)
                notified.append(name)

        kundi A:
            a = Descriptor()
            b = Descriptor()
            c = Descriptor()
            d = Descriptor()
            e = Descriptor()

        self.assertCountEqual(notified, ['a', 'b', 'c', 'd', 'e'])

    eleza test_errors(self):
        kundi MyMeta(type):
            pass

        ukijumuisha self.assertRaises(TypeError):
            kundi MyClass(metaclass=MyMeta, otherarg=1):
                pass

        ukijumuisha self.assertRaises(TypeError):
            types.new_class("MyClass", (object,),
                            dict(metaclass=MyMeta, otherarg=1))
        types.prepare_class("MyClass", (object,),
                            dict(metaclass=MyMeta, otherarg=1))

        kundi MyMeta(type):
            eleza __init__(self, name, bases, namespace, otherarg):
                super().__init__(name, bases, namespace)

        ukijumuisha self.assertRaises(TypeError):
            kundi MyClass(metaclass=MyMeta, otherarg=1):
                pass

        kundi MyMeta(type):
            eleza __new__(cls, name, bases, namespace, otherarg):
                rudisha super().__new__(cls, name, bases, namespace)

            eleza __init__(self, name, bases, namespace, otherarg):
                super().__init__(name, bases, namespace)
                self.otherarg = otherarg

        kundi MyClass(metaclass=MyMeta, otherarg=1):
            pass

        self.assertEqual(MyClass.otherarg, 1)

    eleza test_errors_changed_pep487(self):
        # These tests failed before Python 3.6, PEP 487
        kundi MyMeta(type):
            eleza __new__(cls, name, bases, namespace):
                rudisha super().__new__(cls, name=name, bases=bases,
                                       dict=namespace)

        ukijumuisha self.assertRaises(TypeError):
            kundi MyClass(metaclass=MyMeta):
                pass

        kundi MyMeta(type):
            eleza __new__(cls, name, bases, namespace, otherarg):
                self = super().__new__(cls, name, bases, namespace)
                self.otherarg = otherarg
                rudisha self

        kundi MyClass(metaclass=MyMeta, otherarg=1):
            pass

        self.assertEqual(MyClass.otherarg, 1)

    eleza test_type(self):
        t = type('NewClass', (object,), {})
        self.assertIsInstance(t, type)
        self.assertEqual(t.__name__, 'NewClass')

        ukijumuisha self.assertRaises(TypeError):
            type(name='NewClass', bases=(object,), dict={})


ikiwa __name__ == "__main__":
    unittest.main()
