agiza asyncio
agiza math
agiza unittest
agiza os
agiza sys
kutoka unittest.mock agiza AsyncMock, Mock, MagicMock, _magics



kundi TestMockingMagicMethods(unittest.TestCase):

    eleza test_deleting_magic_methods(self):
        mock = Mock()
        self.assertUongo(hasattr(mock, '__getitem__'))

        mock.__getitem__ = Mock()
        self.assertKweli(hasattr(mock, '__getitem__'))

        toa mock.__getitem__
        self.assertUongo(hasattr(mock, '__getitem__'))


    eleza test_magicmock_del(self):
        mock = MagicMock()
        # before using getitem
        toa mock.__getitem__
        self.assertRaises(TypeError, lambda: mock['foo'])

        mock = MagicMock()
        # this time use it first
        mock['foo']
        toa mock.__getitem__
        self.assertRaises(TypeError, lambda: mock['foo'])


    eleza test_magic_method_wrapping(self):
        mock = Mock()
        eleza f(self, name):
            rudisha self, 'fish'

        mock.__getitem__ = f
        self.assertIsNot(mock.__getitem__, f)
        self.assertEqual(mock['foo'], (mock, 'fish'))
        self.assertEqual(mock.__getitem__('foo'), (mock, 'fish'))

        mock.__getitem__ = mock
        self.assertIs(mock.__getitem__, mock)


    eleza test_magic_methods_isolated_between_mocks(self):
        mock1 = Mock()
        mock2 = Mock()

        mock1.__iter__ = Mock(return_value=iter([]))
        self.assertEqual(list(mock1), [])
        self.assertRaises(TypeError, lambda: list(mock2))


    eleza test_repr(self):
        mock = Mock()
        self.assertEqual(repr(mock), "<Mock id='%s'>" % id(mock))
        mock.__repr__ = lambda s: 'foo'
        self.assertEqual(repr(mock), 'foo')


    eleza test_str(self):
        mock = Mock()
        self.assertEqual(str(mock), object.__str__(mock))
        mock.__str__ = lambda s: 'foo'
        self.assertEqual(str(mock), 'foo')


    eleza test_dict_methods(self):
        mock = Mock()

        self.assertRaises(TypeError, lambda: mock['foo'])
        eleza _del():
            toa mock['foo']
        eleza _set():
            mock['foo'] = 3
        self.assertRaises(TypeError, _del)
        self.assertRaises(TypeError, _set)

        _dict = {}
        eleza getitem(s, name):
            rudisha _dict[name]
        eleza setitem(s, name, value):
            _dict[name] = value
        eleza delitem(s, name):
            toa _dict[name]

        mock.__setitem__ = setitem
        mock.__getitem__ = getitem
        mock.__delitem__ = delitem

        self.assertRaises(KeyError, lambda: mock['foo'])
        mock['foo'] = 'bar'
        self.assertEqual(_dict, {'foo': 'bar'})
        self.assertEqual(mock['foo'], 'bar')
        toa mock['foo']
        self.assertEqual(_dict, {})


    eleza test_numeric(self):
        original = mock = Mock()
        mock.value = 0

        self.assertRaises(TypeError, lambda: mock + 3)

        eleza add(self, other):
            mock.value += other
            rudisha self
        mock.__add__ = add
        self.assertEqual(mock + 3, mock)
        self.assertEqual(mock.value, 3)

        toa mock.__add__
        eleza iadd(mock):
            mock += 3
        self.assertRaises(TypeError, iadd, mock)
        mock.__iadd__ = add
        mock += 6
        self.assertEqual(mock, original)
        self.assertEqual(mock.value, 9)

        self.assertRaises(TypeError, lambda: 3 + mock)
        mock.__radd__ = add
        self.assertEqual(7 + mock, mock)
        self.assertEqual(mock.value, 16)

    eleza test_division(self):
        original = mock = Mock()
        mock.value = 32
        self.assertRaises(TypeError, lambda: mock / 2)

        eleza truediv(self, other):
            mock.value /= other
            rudisha self
        mock.__truediv__ = truediv
        self.assertEqual(mock / 2, mock)
        self.assertEqual(mock.value, 16)

        toa mock.__truediv__
        eleza itruediv(mock):
            mock /= 4
        self.assertRaises(TypeError, itruediv, mock)
        mock.__itruediv__ = truediv
        mock /= 8
        self.assertEqual(mock, original)
        self.assertEqual(mock.value, 2)

        self.assertRaises(TypeError, lambda: 8 / mock)
        mock.__rtruediv__ = truediv
        self.assertEqual(0.5 / mock, mock)
        self.assertEqual(mock.value, 4)

    eleza test_hash(self):
        mock = Mock()
        # test delegation
        self.assertEqual(hash(mock), Mock.__hash__(mock))

        eleza _hash(s):
            rudisha 3
        mock.__hash__ = _hash
        self.assertEqual(hash(mock), 3)


    eleza test_nonzero(self):
        m = Mock()
        self.assertKweli(bool(m))

        m.__bool__ = lambda s: Uongo
        self.assertUongo(bool(m))


    eleza test_comparison(self):
        mock = Mock()
        eleza comp(s, o):
            rudisha Kweli
        mock.__lt__ = mock.__gt__ = mock.__le__ = mock.__ge__ = comp
        self. assertKweli(mock < 3)
        self. assertKweli(mock > 3)
        self. assertKweli(mock <= 3)
        self. assertKweli(mock >= 3)

        self.assertRaises(TypeError, lambda: MagicMock() < object())
        self.assertRaises(TypeError, lambda: object() < MagicMock())
        self.assertRaises(TypeError, lambda: MagicMock() < MagicMock())
        self.assertRaises(TypeError, lambda: MagicMock() > object())
        self.assertRaises(TypeError, lambda: object() > MagicMock())
        self.assertRaises(TypeError, lambda: MagicMock() > MagicMock())
        self.assertRaises(TypeError, lambda: MagicMock() <= object())
        self.assertRaises(TypeError, lambda: object() <= MagicMock())
        self.assertRaises(TypeError, lambda: MagicMock() <= MagicMock())
        self.assertRaises(TypeError, lambda: MagicMock() >= object())
        self.assertRaises(TypeError, lambda: object() >= MagicMock())
        self.assertRaises(TypeError, lambda: MagicMock() >= MagicMock())


    eleza test_equality(self):
        kila mock kwenye Mock(), MagicMock():
            self.assertEqual(mock == mock, Kweli)
            self.assertIsInstance(mock == mock, bool)
            self.assertEqual(mock != mock, Uongo)
            self.assertIsInstance(mock != mock, bool)
            self.assertEqual(mock == object(), Uongo)
            self.assertEqual(mock != object(), Kweli)

            eleza eq(self, other):
                rudisha other == 3
            mock.__eq__ = eq
            self.assertKweli(mock == 3)
            self.assertUongo(mock == 4)

            eleza ne(self, other):
                rudisha other == 3
            mock.__ne__ = ne
            self.assertKweli(mock != 3)
            self.assertUongo(mock != 4)

        mock = MagicMock()
        mock.__eq__.return_value = Kweli
        self.assertIsInstance(mock == 3, bool)
        self.assertEqual(mock == 3, Kweli)

        mock.__ne__.return_value = Uongo
        self.assertIsInstance(mock != 3, bool)
        self.assertEqual(mock != 3, Uongo)


    eleza test_len_contains_iter(self):
        mock = Mock()

        self.assertRaises(TypeError, len, mock)
        self.assertRaises(TypeError, iter, mock)
        self.assertRaises(TypeError, lambda: 'foo' kwenye mock)

        mock.__len__ = lambda s: 6
        self.assertEqual(len(mock), 6)

        mock.__contains__ = lambda s, o: o == 3
        self.assertIn(3, mock)
        self.assertNotIn(6, mock)

        mock.__iter__ = lambda s: iter('foobarbaz')
        self.assertEqual(list(mock), list('foobarbaz'))


    eleza test_magicmock(self):
        mock = MagicMock()

        mock.__iter__.return_value = iter([1, 2, 3])
        self.assertEqual(list(mock), [1, 2, 3])

        getattr(mock, '__bool__').return_value = Uongo
        self.assertUongo(hasattr(mock, '__nonzero__'))
        self.assertUongo(bool(mock))

        kila entry kwenye _magics:
            self.assertKweli(hasattr(mock, entry))
        self.assertUongo(hasattr(mock, '__imaginary__'))


    eleza test_magic_mock_equality(self):
        mock = MagicMock()
        self.assertIsInstance(mock == object(), bool)
        self.assertIsInstance(mock != object(), bool)

        self.assertEqual(mock == object(), Uongo)
        self.assertEqual(mock != object(), Kweli)
        self.assertEqual(mock == mock, Kweli)
        self.assertEqual(mock != mock, Uongo)

    eleza test_asyncmock_defaults(self):
        mock = AsyncMock()
        self.assertEqual(int(mock), 1)
        self.assertEqual(complex(mock), 1j)
        self.assertEqual(float(mock), 1.0)
        self.assertNotIn(object(), mock)
        self.assertEqual(len(mock), 0)
        self.assertEqual(list(mock), [])
        self.assertEqual(hash(mock), object.__hash__(mock))
        self.assertEqual(str(mock), object.__str__(mock))
        self.assertKweli(bool(mock))
        self.assertEqual(round(mock), mock.__round__())
        self.assertEqual(math.trunc(mock), mock.__trunc__())
        self.assertEqual(math.floor(mock), mock.__floor__())
        self.assertEqual(math.ceil(mock), mock.__ceil__())
        self.assertKweli(asyncio.iscoroutinefunction(mock.__aexit__))
        self.assertKweli(asyncio.iscoroutinefunction(mock.__aenter__))
        self.assertIsInstance(mock.__aenter__, AsyncMock)
        self.assertIsInstance(mock.__aexit__, AsyncMock)

        # kwenye Python 3 oct na hex use __index__
        # so these tests are kila __index__ kwenye py3k
        self.assertEqual(oct(mock), '0o1')
        self.assertEqual(hex(mock), '0x1')
        # how to test __sizeof__ ?

    eleza test_magicmock_defaults(self):
        mock = MagicMock()
        self.assertEqual(int(mock), 1)
        self.assertEqual(complex(mock), 1j)
        self.assertEqual(float(mock), 1.0)
        self.assertNotIn(object(), mock)
        self.assertEqual(len(mock), 0)
        self.assertEqual(list(mock), [])
        self.assertEqual(hash(mock), object.__hash__(mock))
        self.assertEqual(str(mock), object.__str__(mock))
        self.assertKweli(bool(mock))
        self.assertEqual(round(mock), mock.__round__())
        self.assertEqual(math.trunc(mock), mock.__trunc__())
        self.assertEqual(math.floor(mock), mock.__floor__())
        self.assertEqual(math.ceil(mock), mock.__ceil__())
        self.assertKweli(asyncio.iscoroutinefunction(mock.__aexit__))
        self.assertKweli(asyncio.iscoroutinefunction(mock.__aenter__))
        self.assertIsInstance(mock.__aenter__, AsyncMock)
        self.assertIsInstance(mock.__aexit__, AsyncMock)

        # kwenye Python 3 oct na hex use __index__
        # so these tests are kila __index__ kwenye py3k
        self.assertEqual(oct(mock), '0o1')
        self.assertEqual(hex(mock), '0x1')
        # how to test __sizeof__ ?


    eleza test_magic_methods_fspath(self):
        mock = MagicMock()
        expected_path = mock.__fspath__()
        mock.reset_mock()

        self.assertEqual(os.fspath(mock), expected_path)
        mock.__fspath__.assert_called_once()


    eleza test_magic_methods_and_spec(self):
        kundi Iterable(object):
            eleza __iter__(self): pass

        mock = Mock(spec=Iterable)
        self.assertRaises(AttributeError, lambda: mock.__iter__)

        mock.__iter__ = Mock(return_value=iter([]))
        self.assertEqual(list(mock), [])

        kundi NonIterable(object):
            pass
        mock = Mock(spec=NonIterable)
        self.assertRaises(AttributeError, lambda: mock.__iter__)

        eleza set_int():
            mock.__int__ = Mock(return_value=iter([]))
        self.assertRaises(AttributeError, set_int)

        mock = MagicMock(spec=Iterable)
        self.assertEqual(list(mock), [])
        self.assertRaises(AttributeError, set_int)


    eleza test_magic_methods_and_spec_set(self):
        kundi Iterable(object):
            eleza __iter__(self): pass

        mock = Mock(spec_set=Iterable)
        self.assertRaises(AttributeError, lambda: mock.__iter__)

        mock.__iter__ = Mock(return_value=iter([]))
        self.assertEqual(list(mock), [])

        kundi NonIterable(object):
            pass
        mock = Mock(spec_set=NonIterable)
        self.assertRaises(AttributeError, lambda: mock.__iter__)

        eleza set_int():
            mock.__int__ = Mock(return_value=iter([]))
        self.assertRaises(AttributeError, set_int)

        mock = MagicMock(spec_set=Iterable)
        self.assertEqual(list(mock), [])
        self.assertRaises(AttributeError, set_int)


    eleza test_setting_unsupported_magic_method(self):
        mock = MagicMock()
        eleza set_setattr():
            mock.__setattr__ = lambda self, name: Tupu
        self.assertRaisesRegex(AttributeError,
            "Attempting to set unsupported magic method '__setattr__'.",
            set_setattr
        )


    eleza test_attributes_and_return_value(self):
        mock = MagicMock()
        attr = mock.foo
        eleza _get_type(obj):
            # the type of every mock (or magicmock) ni a custom subclass
            # so the real type ni the second kwenye the mro
            rudisha type(obj).__mro__[1]
        self.assertEqual(_get_type(attr), MagicMock)

        returned = mock()
        self.assertEqual(_get_type(returned), MagicMock)


    eleza test_magic_methods_are_magic_mocks(self):
        mock = MagicMock()
        self.assertIsInstance(mock.__getitem__, MagicMock)

        mock[1][2].__getitem__.return_value = 3
        self.assertEqual(mock[1][2][3], 3)


    eleza test_magic_method_reset_mock(self):
        mock = MagicMock()
        str(mock)
        self.assertKweli(mock.__str__.called)
        mock.reset_mock()
        self.assertUongo(mock.__str__.called)


    eleza test_dir(self):
        # overriding the default implementation
        kila mock kwenye Mock(), MagicMock():
            eleza _dir(self):
                rudisha ['foo']
            mock.__dir__ = _dir
            self.assertEqual(dir(mock), ['foo'])


    @unittest.skipIf('PyPy' kwenye sys.version, "This fails differently on pypy")
    eleza test_bound_methods(self):
        m = Mock()

        # XXXX should this be an expected failure instead?

        # this seems like it should work, but ni hard to do without introducing
        # other api inconsistencies. Failure message could be better though.
        m.__iter__ = [3].__iter__
        self.assertRaises(TypeError, iter, m)


    eleza test_magic_method_type(self):
        kundi Foo(MagicMock):
            pass

        foo = Foo()
        self.assertIsInstance(foo.__int__, Foo)


    eleza test_descriptor_from_class(self):
        m = MagicMock()
        type(m).__str__.return_value = 'foo'
        self.assertEqual(str(m), 'foo')


    eleza test_iterable_as_iter_return_value(self):
        m = MagicMock()
        m.__iter__.return_value = [1, 2, 3]
        self.assertEqual(list(m), [1, 2, 3])
        self.assertEqual(list(m), [1, 2, 3])

        m.__iter__.return_value = iter([4, 5, 6])
        self.assertEqual(list(m), [4, 5, 6])
        self.assertEqual(list(m), [])


    eleza test_matmul(self):
        m = MagicMock()
        self.assertIsInstance(m @ 1, MagicMock)
        m.__matmul__.return_value = 42
        m.__rmatmul__.return_value = 666
        m.__imatmul__.return_value = 24
        self.assertEqual(m @ 1, 42)
        self.assertEqual(1 @ m, 666)
        m @= 24
        self.assertEqual(m, 24)

    eleza test_divmod_and_rdivmod(self):
        m = MagicMock()
        self.assertIsInstance(divmod(5, m), MagicMock)
        m.__divmod__.return_value = (2, 1)
        self.assertEqual(divmod(m, 2), (2, 1))
        m = MagicMock()
        foo = divmod(2, m)
        self.assertIsInstance(foo, MagicMock)
        foo_direct = m.__divmod__(2)
        self.assertIsInstance(foo_direct, MagicMock)
        bar = divmod(m, 2)
        self.assertIsInstance(bar, MagicMock)
        bar_direct = m.__rdivmod__(2)
        self.assertIsInstance(bar_direct, MagicMock)

    # http://bugs.python.org/issue23310
    # Check ikiwa you can change behaviour of magic methods kwenye MagicMock init
    eleza test_magic_in_initialization(self):
        m = MagicMock(**{'__str__.return_value': "12"})
        self.assertEqual(str(m), "12")

    eleza test_changing_magic_set_in_initialization(self):
        m = MagicMock(**{'__str__.return_value': "12"})
        m.__str__.return_value = "13"
        self.assertEqual(str(m), "13")
        m = MagicMock(**{'__str__.return_value': "12"})
        m.configure_mock(**{'__str__.return_value': "14"})
        self.assertEqual(str(m), "14")


ikiwa __name__ == '__main__':
    unittest.main()
