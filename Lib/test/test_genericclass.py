agiza unittest
kutoka test agiza support


kundi TestMROEntry(unittest.TestCase):
    eleza test_mro_entry_signature(self):
        tested = []
        kundi B: ...
        kundi C:
            eleza __mro_entries__(self, *args, **kwargs):
                tested.extend([args, kwargs])
                rudisha (C,)
        c = C()
        self.assertEqual(tested, [])
        kundi D(B, c): ...
        self.assertEqual(tested[0], ((B, c),))
        self.assertEqual(tested[1], {})

    eleza test_mro_entry(self):
        tested = []
        kundi A: ...
        kundi B: ...
        kundi C:
            eleza __mro_entries__(self, bases):
                tested.append(bases)
                rudisha (self.__class__,)
        c = C()
        self.assertEqual(tested, [])
        kundi D(A, c, B): ...
        self.assertEqual(tested[-1], (A, c, B))
        self.assertEqual(D.__bases__, (A, C, B))
        self.assertEqual(D.__orig_bases__, (A, c, B))
        self.assertEqual(D.__mro__, (D, A, C, B, object))
        d = D()
        kundi E(d): ...
        self.assertEqual(tested[-1], (d,))
        self.assertEqual(E.__bases__, (D,))

    eleza test_mro_entry_none(self):
        tested = []
        kundi A: ...
        kundi B: ...
        kundi C:
            eleza __mro_entries__(self, bases):
                tested.append(bases)
                rudisha ()
        c = C()
        self.assertEqual(tested, [])
        kundi D(A, c, B): ...
        self.assertEqual(tested[-1], (A, c, B))
        self.assertEqual(D.__bases__, (A, B))
        self.assertEqual(D.__orig_bases__, (A, c, B))
        self.assertEqual(D.__mro__, (D, A, B, object))
        kundi E(c): ...
        self.assertEqual(tested[-1], (c,))
        self.assertEqual(E.__bases__, (object,))
        self.assertEqual(E.__orig_bases__, (c,))
        self.assertEqual(E.__mro__, (E, object))

    eleza test_mro_entry_with_builtins(self):
        tested = []
        kundi A: ...
        kundi C:
            eleza __mro_entries__(self, bases):
                tested.append(bases)
                rudisha (dict,)
        c = C()
        self.assertEqual(tested, [])
        kundi D(A, c): ...
        self.assertEqual(tested[-1], (A, c))
        self.assertEqual(D.__bases__, (A, dict))
        self.assertEqual(D.__orig_bases__, (A, c))
        self.assertEqual(D.__mro__, (D, A, dict, object))

    eleza test_mro_entry_with_builtins_2(self):
        tested = []
        kundi C:
            eleza __mro_entries__(self, bases):
                tested.append(bases)
                rudisha (C,)
        c = C()
        self.assertEqual(tested, [])
        kundi D(c, dict): ...
        self.assertEqual(tested[-1], (c, dict))
        self.assertEqual(D.__bases__, (C, dict))
        self.assertEqual(D.__orig_bases__, (c, dict))
        self.assertEqual(D.__mro__, (D, C, dict, object))

    eleza test_mro_entry_errors(self):
        kundi C_too_many:
            eleza __mro_entries__(self, bases, something, other):
                rudisha ()
        c = C_too_many()
        with self.assertRaises(TypeError):
            kundi D(c): ...
        kundi C_too_few:
            eleza __mro_entries__(self):
                rudisha ()
        d = C_too_few()
        with self.assertRaises(TypeError):
            kundi D(d): ...

    eleza test_mro_entry_errors_2(self):
        kundi C_not_callable:
            __mro_entries__ = "Surprise!"
        c = C_not_callable()
        with self.assertRaises(TypeError):
            kundi D(c): ...
        kundi C_not_tuple:
            eleza __mro_entries__(self):
                rudisha object
        c = C_not_tuple()
        with self.assertRaises(TypeError):
            kundi D(c): ...

    eleza test_mro_entry_metaclass(self):
        meta_args = []
        kundi Meta(type):
            eleza __new__(mcls, name, bases, ns):
                meta_args.extend([mcls, name, bases, ns])
                rudisha super().__new__(mcls, name, bases, ns)
        kundi A: ...
        kundi C:
            eleza __mro_entries__(self, bases):
                rudisha (A,)
        c = C()
        kundi D(c, metaclass=Meta):
            x = 1
        self.assertEqual(meta_args[0], Meta)
        self.assertEqual(meta_args[1], 'D')
        self.assertEqual(meta_args[2], (A,))
        self.assertEqual(meta_args[3]['x'], 1)
        self.assertEqual(D.__bases__, (A,))
        self.assertEqual(D.__orig_bases__, (c,))
        self.assertEqual(D.__mro__, (D, A, object))
        self.assertEqual(D.__class__, Meta)

    eleza test_mro_entry_type_call(self):
        # Substitution should _not_ happen kwenye direct type call
        kundi C:
            eleza __mro_entries__(self, bases):
                rudisha ()
        c = C()
        with self.assertRaisesRegex(TypeError,
                                    "MRO entry resolution; "
                                    "use types.new_class()"):
            type('Bad', (c,), {})


kundi TestClassGetitem(unittest.TestCase):
    eleza test_class_getitem(self):
        getitem_args = []
        kundi C:
            eleza __class_getitem__(*args, **kwargs):
                getitem_args.extend([args, kwargs])
                rudisha Tupu
        C[int, str]
        self.assertEqual(getitem_args[0], (C, (int, str)))
        self.assertEqual(getitem_args[1], {})

    eleza test_class_getitem_format(self):
        kundi C:
            eleza __class_getitem__(cls, item):
                rudisha f'C[{item.__name__}]'
        self.assertEqual(C[int], 'C[int]')
        self.assertEqual(C[C], 'C[C]')

    eleza test_class_getitem_inheritance(self):
        kundi C:
            eleza __class_getitem__(cls, item):
                rudisha f'{cls.__name__}[{item.__name__}]'
        kundi D(C): ...
        self.assertEqual(D[int], 'D[int]')
        self.assertEqual(D[D], 'D[D]')

    eleza test_class_getitem_inheritance_2(self):
        kundi C:
            eleza __class_getitem__(cls, item):
                rudisha 'Should sio see this'
        kundi D(C):
            eleza __class_getitem__(cls, item):
                rudisha f'{cls.__name__}[{item.__name__}]'
        self.assertEqual(D[int], 'D[int]')
        self.assertEqual(D[D], 'D[D]')

    eleza test_class_getitem_classmethod(self):
        kundi C:
            @classmethod
            eleza __class_getitem__(cls, item):
                rudisha f'{cls.__name__}[{item.__name__}]'
        kundi D(C): ...
        self.assertEqual(D[int], 'D[int]')
        self.assertEqual(D[D], 'D[D]')

    eleza test_class_getitem_patched(self):
        kundi C:
            eleza __init_subclass__(cls):
                eleza __class_getitem__(cls, item):
                    rudisha f'{cls.__name__}[{item.__name__}]'
                cls.__class_getitem__ = classmethod(__class_getitem__)
        kundi D(C): ...
        self.assertEqual(D[int], 'D[int]')
        self.assertEqual(D[D], 'D[D]')

    eleza test_class_getitem_with_builtins(self):
        kundi A(dict):
            called_with = Tupu

            eleza __class_getitem__(cls, item):
                cls.called_with = item
        kundi B(A):
            pita
        self.assertIs(B.called_with, Tupu)
        B[int]
        self.assertIs(B.called_with, int)

    eleza test_class_getitem_errors(self):
        kundi C_too_few:
            eleza __class_getitem__(cls):
                rudisha Tupu
        with self.assertRaises(TypeError):
            C_too_few[int]
        kundi C_too_many:
            eleza __class_getitem__(cls, one, two):
                rudisha Tupu
        with self.assertRaises(TypeError):
            C_too_many[int]

    eleza test_class_getitem_errors_2(self):
        kundi C:
            eleza __class_getitem__(cls, item):
                rudisha Tupu
        with self.assertRaises(TypeError):
            C()[int]
        kundi E: ...
        e = E()
        e.__class_getitem__ = lambda cls, item: 'This will sio work'
        with self.assertRaises(TypeError):
            e[int]
        kundi C_not_callable:
            __class_getitem__ = "Surprise!"
        with self.assertRaises(TypeError):
            C_not_callable[int]

    eleza test_class_getitem_metaclass(self):
        kundi Meta(type):
            eleza __class_getitem__(cls, item):
                rudisha f'{cls.__name__}[{item.__name__}]'
        self.assertEqual(Meta[int], 'Meta[int]')

    eleza test_class_getitem_with_metaclass(self):
        kundi Meta(type): pita
        kundi C(metaclass=Meta):
            eleza __class_getitem__(cls, item):
                rudisha f'{cls.__name__}[{item.__name__}]'
        self.assertEqual(C[int], 'C[int]')

    eleza test_class_getitem_metaclass_first(self):
        kundi Meta(type):
            eleza __getitem__(cls, item):
                rudisha 'kutoka metaclass'
        kundi C(metaclass=Meta):
            eleza __class_getitem__(cls, item):
                rudisha 'kutoka __class_getitem__'
        self.assertEqual(C[int], 'kutoka metaclass')


@support.cpython_only
kundi CAPITest(unittest.TestCase):

    eleza test_c_class(self):
        kutoka _testcapi agiza Generic, GenericAlias
        self.assertIsInstance(Generic.__class_getitem__(int), GenericAlias)

        IntGeneric = Generic[int]
        self.assertIs(type(IntGeneric), GenericAlias)
        self.assertEqual(IntGeneric.__mro_entries__(()), (int,))
        kundi C(IntGeneric):
            pita
        self.assertEqual(C.__bases__, (int,))
        self.assertEqual(C.__orig_bases__, (IntGeneric,))
        self.assertEqual(C.__mro__, (C, int, object))


ikiwa __name__ == "__main__":
    unittest.main()
