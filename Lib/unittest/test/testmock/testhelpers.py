agiza inspect
agiza time
agiza types
agiza unittest

kutoka unittest.mock agiza (
    call, _Call, create_autospec, MagicMock,
    Mock, ANY, _CallList, patch, PropertyMock, _callable
)

kutoka datetime agiza datetime
kutoka functools agiza partial

kundi SomeClass(object):
    eleza one(self, a, b): pita
    eleza two(self): pita
    eleza three(self, a=Tupu): pita



kundi AnyTest(unittest.TestCase):

    eleza test_any(self):
        self.assertEqual(ANY, object())

        mock = Mock()
        mock(ANY)
        mock.assert_called_with(ANY)

        mock = Mock()
        mock(foo=ANY)
        mock.assert_called_with(foo=ANY)

    eleza test_repr(self):
        self.assertEqual(repr(ANY), '<ANY>')
        self.assertEqual(str(ANY), '<ANY>')


    eleza test_any_and_datetime(self):
        mock = Mock()
        mock(datetime.now(), foo=datetime.now())

        mock.assert_called_with(ANY, foo=ANY)


    eleza test_any_mock_calls_comparison_order(self):
        mock = Mock()
        kundi Foo(object):
            eleza __eq__(self, other): pita
            eleza __ne__(self, other): pita

        kila d kwenye datetime.now(), Foo():
            mock.reset_mock()

            mock(d, foo=d, bar=d)
            mock.method(d, zinga=d, alpha=d)
            mock().method(a1=d, z99=d)

            expected = [
                call(ANY, foo=ANY, bar=ANY),
                call.method(ANY, zinga=ANY, alpha=ANY),
                call(), call().method(a1=ANY, z99=ANY)
            ]
            self.assertEqual(expected, mock.mock_calls)
            self.assertEqual(mock.mock_calls, expected)



kundi CallTest(unittest.TestCase):

    eleza test_call_with_call(self):
        kall = _Call()
        self.assertEqual(kall, _Call())
        self.assertEqual(kall, _Call(('',)))
        self.assertEqual(kall, _Call(((),)))
        self.assertEqual(kall, _Call(({},)))
        self.assertEqual(kall, _Call(('', ())))
        self.assertEqual(kall, _Call(('', {})))
        self.assertEqual(kall, _Call(('', (), {})))
        self.assertEqual(kall, _Call(('foo',)))
        self.assertEqual(kall, _Call(('bar', ())))
        self.assertEqual(kall, _Call(('baz', {})))
        self.assertEqual(kall, _Call(('spam', (), {})))

        kall = _Call(((1, 2, 3),))
        self.assertEqual(kall, _Call(((1, 2, 3),)))
        self.assertEqual(kall, _Call(('', (1, 2, 3))))
        self.assertEqual(kall, _Call(((1, 2, 3), {})))
        self.assertEqual(kall, _Call(('', (1, 2, 3), {})))

        kall = _Call(((1, 2, 4),))
        self.assertNotEqual(kall, _Call(('', (1, 2, 3))))
        self.assertNotEqual(kall, _Call(('', (1, 2, 3), {})))

        kall = _Call(('foo', (1, 2, 4),))
        self.assertNotEqual(kall, _Call(('', (1, 2, 4))))
        self.assertNotEqual(kall, _Call(('', (1, 2, 4), {})))
        self.assertNotEqual(kall, _Call(('bar', (1, 2, 4))))
        self.assertNotEqual(kall, _Call(('bar', (1, 2, 4), {})))

        kall = _Call(({'a': 3},))
        self.assertEqual(kall, _Call(('', (), {'a': 3})))
        self.assertEqual(kall, _Call(('', {'a': 3})))
        self.assertEqual(kall, _Call(((), {'a': 3})))
        self.assertEqual(kall, _Call(({'a': 3},)))


    eleza test_empty__Call(self):
        args = _Call()

        self.assertEqual(args, ())
        self.assertEqual(args, ('foo',))
        self.assertEqual(args, ((),))
        self.assertEqual(args, ('foo', ()))
        self.assertEqual(args, ('foo',(), {}))
        self.assertEqual(args, ('foo', {}))
        self.assertEqual(args, ({},))


    eleza test_named_empty_call(self):
        args = _Call(('foo', (), {}))

        self.assertEqual(args, ('foo',))
        self.assertEqual(args, ('foo', ()))
        self.assertEqual(args, ('foo',(), {}))
        self.assertEqual(args, ('foo', {}))

        self.assertNotEqual(args, ((),))
        self.assertNotEqual(args, ())
        self.assertNotEqual(args, ({},))
        self.assertNotEqual(args, ('bar',))
        self.assertNotEqual(args, ('bar', ()))
        self.assertNotEqual(args, ('bar', {}))


    eleza test_call_with_args(self):
        args = _Call(((1, 2, 3), {}))

        self.assertEqual(args, ((1, 2, 3),))
        self.assertEqual(args, ('foo', (1, 2, 3)))
        self.assertEqual(args, ('foo', (1, 2, 3), {}))
        self.assertEqual(args, ((1, 2, 3), {}))
        self.assertEqual(args.args, (1, 2, 3))
        self.assertEqual(args.kwargs, {})


    eleza test_named_call_with_args(self):
        args = _Call(('foo', (1, 2, 3), {}))

        self.assertEqual(args, ('foo', (1, 2, 3)))
        self.assertEqual(args, ('foo', (1, 2, 3), {}))
        self.assertEqual(args.args, (1, 2, 3))
        self.assertEqual(args.kwargs, {})

        self.assertNotEqual(args, ((1, 2, 3),))
        self.assertNotEqual(args, ((1, 2, 3), {}))


    eleza test_call_with_kwargs(self):
        args = _Call(((), dict(a=3, b=4)))

        self.assertEqual(args, (dict(a=3, b=4),))
        self.assertEqual(args, ('foo', dict(a=3, b=4)))
        self.assertEqual(args, ('foo', (), dict(a=3, b=4)))
        self.assertEqual(args, ((), dict(a=3, b=4)))
        self.assertEqual(args.args, ())
        self.assertEqual(args.kwargs, dict(a=3, b=4))


    eleza test_named_call_with_kwargs(self):
        args = _Call(('foo', (), dict(a=3, b=4)))

        self.assertEqual(args, ('foo', dict(a=3, b=4)))
        self.assertEqual(args, ('foo', (), dict(a=3, b=4)))
        self.assertEqual(args.args, ())
        self.assertEqual(args.kwargs, dict(a=3, b=4))

        self.assertNotEqual(args, (dict(a=3, b=4),))
        self.assertNotEqual(args, ((), dict(a=3, b=4)))


    eleza test_call_with_args_call_empty_name(self):
        args = _Call(((1, 2, 3), {}))

        self.assertEqual(args, call(1, 2, 3))
        self.assertEqual(call(1, 2, 3), args)
        self.assertIn(call(1, 2, 3), [args])


    eleza test_call_ne(self):
        self.assertNotEqual(_Call(((1, 2, 3),)), call(1, 2))
        self.assertUongo(_Call(((1, 2, 3),)) != call(1, 2, 3))
        self.assertKweli(_Call(((1, 2), {})) != call(1, 2, 3))


    eleza test_call_non_tuples(self):
        kall = _Call(((1, 2, 3),))
        kila value kwenye 1, Tupu, self, int:
            self.assertNotEqual(kall, value)
            self.assertUongo(kall == value)


    eleza test_repr(self):
        self.assertEqual(repr(_Call()), 'call()')
        self.assertEqual(repr(_Call(('foo',))), 'call.foo()')

        self.assertEqual(repr(_Call(((1, 2, 3), {'a': 'b'}))),
                         "call(1, 2, 3, a='b')")
        self.assertEqual(repr(_Call(('bar', (1, 2, 3), {'a': 'b'}))),
                         "call.bar(1, 2, 3, a='b')")

        self.assertEqual(repr(call), 'call')
        self.assertEqual(str(call), 'call')

        self.assertEqual(repr(call()), 'call()')
        self.assertEqual(repr(call(1)), 'call(1)')
        self.assertEqual(repr(call(zz='thing')), "call(zz='thing')")

        self.assertEqual(repr(call().foo), 'call().foo')
        self.assertEqual(repr(call(1).foo.bar(a=3).bing),
                         'call().foo.bar().bing')
        self.assertEqual(
            repr(call().foo(1, 2, a=3)),
            "call().foo(1, 2, a=3)"
        )
        self.assertEqual(repr(call()()), "call()()")
        self.assertEqual(repr(call(1)(2)), "call()(2)")
        self.assertEqual(
            repr(call()().bar().baz.beep(1)),
            "call()().bar().baz.beep(1)"
        )


    eleza test_call(self):
        self.assertEqual(call(), ('', (), {}))
        self.assertEqual(call('foo', 'bar', one=3, two=4),
                         ('', ('foo', 'bar'), {'one': 3, 'two': 4}))

        mock = Mock()
        mock(1, 2, 3)
        mock(a=3, b=6)
        self.assertEqual(mock.call_args_list,
                         [call(1, 2, 3), call(a=3, b=6)])

    eleza test_attribute_call(self):
        self.assertEqual(call.foo(1), ('foo', (1,), {}))
        self.assertEqual(call.bar.baz(fish='eggs'),
                         ('bar.baz', (), {'fish': 'eggs'}))

        mock = Mock()
        mock.foo(1, 2 ,3)
        mock.bar.baz(a=3, b=6)
        self.assertEqual(mock.method_calls,
                         [call.foo(1, 2, 3), call.bar.baz(a=3, b=6)])


    eleza test_extended_call(self):
        result = call(1).foo(2).bar(3, a=4)
        self.assertEqual(result, ('().foo().bar', (3,), dict(a=4)))

        mock = MagicMock()
        mock(1, 2, a=3, b=4)
        self.assertEqual(mock.call_args, call(1, 2, a=3, b=4))
        self.assertNotEqual(mock.call_args, call(1, 2, 3))

        self.assertEqual(mock.call_args_list, [call(1, 2, a=3, b=4)])
        self.assertEqual(mock.mock_calls, [call(1, 2, a=3, b=4)])

        mock = MagicMock()
        mock.foo(1).bar()().baz.beep(a=6)

        last_call = call.foo(1).bar()().baz.beep(a=6)
        self.assertEqual(mock.mock_calls[-1], last_call)
        self.assertEqual(mock.mock_calls, last_call.call_list())


    eleza test_extended_not_equal(self):
        a = call(x=1).foo
        b = call(x=2).foo
        self.assertEqual(a, a)
        self.assertEqual(b, b)
        self.assertNotEqual(a, b)


    eleza test_nested_calls_not_equal(self):
        a = call(x=1).foo().bar
        b = call(x=2).foo().bar
        self.assertEqual(a, a)
        self.assertEqual(b, b)
        self.assertNotEqual(a, b)


    eleza test_call_list(self):
        mock = MagicMock()
        mock(1)
        self.assertEqual(call(1).call_list(), mock.mock_calls)

        mock = MagicMock()
        mock(1).method(2)
        self.assertEqual(call(1).method(2).call_list(),
                         mock.mock_calls)

        mock = MagicMock()
        mock(1).method(2)(3)
        self.assertEqual(call(1).method(2)(3).call_list(),
                         mock.mock_calls)

        mock = MagicMock()
        int(mock(1).method(2)(3).foo.bar.baz(4)(5))
        kall = call(1).method(2)(3).foo.bar.baz(4)(5).__int__()
        self.assertEqual(kall.call_list(), mock.mock_calls)


    eleza test_call_any(self):
        self.assertEqual(call, ANY)

        m = MagicMock()
        int(m)
        self.assertEqual(m.mock_calls, [ANY])
        self.assertEqual([ANY], m.mock_calls)


    eleza test_two_args_call(self):
        args = _Call(((1, 2), {'a': 3}), two=Kweli)
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0], (1, 2))
        self.assertEqual(args[1], {'a': 3})

        other_args = _Call(((1, 2), {'a': 3}))
        self.assertEqual(args, other_args)

    eleza test_call_with_name(self):
        self.assertEqual(_Call((), 'foo')[0], 'foo')
        self.assertEqual(_Call((('bar', 'barz'),),)[0], '')
        self.assertEqual(_Call((('bar', 'barz'), {'hello': 'world'}),)[0], '')

    eleza test_dunder_call(self):
        m = MagicMock()
        m().foo()['bar']()
        self.assertEqual(
            m.mock_calls,
            [call(), call().foo(), call().foo().__getitem__('bar'), call().foo().__getitem__()()]
        )
        m = MagicMock()
        m().foo()['bar'] = 1
        self.assertEqual(
            m.mock_calls,
            [call(), call().foo(), call().foo().__setitem__('bar', 1)]
        )
        m = MagicMock()
        iter(m().foo())
        self.assertEqual(
            m.mock_calls,
            [call(), call().foo(), call().foo().__iter__()]
        )


kundi SpecSignatureTest(unittest.TestCase):

    eleza _check_someclass_mock(self, mock):
        self.assertRaises(AttributeError, getattr, mock, 'foo')
        mock.one(1, 2)
        mock.one.assert_called_with(1, 2)
        self.assertRaises(AssertionError,
                          mock.one.assert_called_with, 3, 4)
        self.assertRaises(TypeError, mock.one, 1)

        mock.two()
        mock.two.assert_called_with()
        self.assertRaises(AssertionError,
                          mock.two.assert_called_with, 3)
        self.assertRaises(TypeError, mock.two, 1)

        mock.three()
        mock.three.assert_called_with()
        self.assertRaises(AssertionError,
                          mock.three.assert_called_with, 3)
        self.assertRaises(TypeError, mock.three, 3, 2)

        mock.three(1)
        mock.three.assert_called_with(1)

        mock.three(a=1)
        mock.three.assert_called_with(a=1)


    eleza test_basic(self):
        mock = create_autospec(SomeClass)
        self._check_someclass_mock(mock)
        mock = create_autospec(SomeClass())
        self._check_someclass_mock(mock)


    eleza test_create_autospec_rudisha_value(self):
        eleza f(): pita
        mock = create_autospec(f, rudisha_value='foo')
        self.assertEqual(mock(), 'foo')

        kundi Foo(object):
            pita

        mock = create_autospec(Foo, rudisha_value='foo')
        self.assertEqual(mock(), 'foo')


    eleza test_autospec_reset_mock(self):
        m = create_autospec(int)
        int(m)
        m.reset_mock()
        self.assertEqual(m.__int__.call_count, 0)


    eleza test_mocking_unbound_methods(self):
        kundi Foo(object):
            eleza foo(self, foo): pita
        p = patch.object(Foo, 'foo')
        mock_foo = p.start()
        Foo().foo(1)

        mock_foo.assert_called_with(1)


    eleza test_create_autospec_keyword_arguments(self):
        kundi Foo(object):
            a = 3
        m = create_autospec(Foo, a='3')
        self.assertEqual(m.a, '3')


    eleza test_create_autospec_keyword_only_arguments(self):
        eleza foo(a, *, b=Tupu): pita

        m = create_autospec(foo)
        m(1)
        m.assert_called_with(1)
        self.assertRaises(TypeError, m, 1, 2)

        m(2, b=3)
        m.assert_called_with(2, b=3)


    eleza test_function_as_instance_attribute(self):
        obj = SomeClass()
        eleza f(a): pita
        obj.f = f

        mock = create_autospec(obj)
        mock.f('bing')
        mock.f.assert_called_with('bing')


    eleza test_spec_as_list(self):
        # because spec kama a list of strings kwenye the mock constructor means
        # something very different we treat a list instance kama the type.
        mock = create_autospec([])
        mock.append('foo')
        mock.append.assert_called_with('foo')

        self.assertRaises(AttributeError, getattr, mock, 'foo')

        kundi Foo(object):
            foo = []

        mock = create_autospec(Foo)
        mock.foo.append(3)
        mock.foo.append.assert_called_with(3)
        self.assertRaises(AttributeError, getattr, mock.foo, 'foo')


    eleza test_attributes(self):
        kundi Sub(SomeClass):
            attr = SomeClass()

        sub_mock = create_autospec(Sub)

        kila mock kwenye (sub_mock, sub_mock.attr):
            self._check_someclass_mock(mock)


    eleza test_spec_has_descriptor_rudishaing_function(self):

        kundi CrazyDescriptor(object):

            eleza __get__(self, obj, type_):
                ikiwa obj ni Tupu:
                    rudisha lambda x: Tupu

        kundi MyClass(object):

            some_attr = CrazyDescriptor()

        mock = create_autospec(MyClass)
        mock.some_attr(1)
        ukijumuisha self.assertRaises(TypeError):
            mock.some_attr()
        ukijumuisha self.assertRaises(TypeError):
            mock.some_attr(1, 2)


    eleza test_spec_has_function_not_in_bases(self):

        kundi CrazyClass(object):

            eleza __dir__(self):
                rudisha super(CrazyClass, self).__dir__()+['crazy']

            eleza __getattr__(self, item):
                ikiwa item == 'crazy':
                    rudisha lambda x: x
                ashiria AttributeError(item)

        inst = CrazyClass()
        ukijumuisha self.assertRaises(AttributeError):
            inst.other
        self.assertEqual(inst.crazy(42), 42)

        mock = create_autospec(inst)
        mock.crazy(42)
        ukijumuisha self.assertRaises(TypeError):
            mock.crazy()
        ukijumuisha self.assertRaises(TypeError):
            mock.crazy(1, 2)


    eleza test_builtin_functions_types(self):
        # we could replace builtin functions / methods ukijumuisha a function
        # ukijumuisha *args / **kwargs signature. Using the builtin method type
        # kama a spec seems to work fairly well though.
        kundi BuiltinSubclass(list):
            eleza bar(self, arg): pita
            sorted = sorted
            attr = {}

        mock = create_autospec(BuiltinSubclass)
        mock.append(3)
        mock.append.assert_called_with(3)
        self.assertRaises(AttributeError, getattr, mock.append, 'foo')

        mock.bar('foo')
        mock.bar.assert_called_with('foo')
        self.assertRaises(TypeError, mock.bar, 'foo', 'bar')
        self.assertRaises(AttributeError, getattr, mock.bar, 'foo')

        mock.sorted([1, 2])
        mock.sorted.assert_called_with([1, 2])
        self.assertRaises(AttributeError, getattr, mock.sorted, 'foo')

        mock.attr.pop(3)
        mock.attr.pop.assert_called_with(3)
        self.assertRaises(AttributeError, getattr, mock.attr, 'foo')


    eleza test_method_calls(self):
        kundi Sub(SomeClass):
            attr = SomeClass()

        mock = create_autospec(Sub)
        mock.one(1, 2)
        mock.two()
        mock.three(3)

        expected = [call.one(1, 2), call.two(), call.three(3)]
        self.assertEqual(mock.method_calls, expected)

        mock.attr.one(1, 2)
        mock.attr.two()
        mock.attr.three(3)

        expected.extend(
            [call.attr.one(1, 2), call.attr.two(), call.attr.three(3)]
        )
        self.assertEqual(mock.method_calls, expected)


    eleza test_magic_methods(self):
        kundi BuiltinSubclass(list):
            attr = {}

        mock = create_autospec(BuiltinSubclass)
        self.assertEqual(list(mock), [])
        self.assertRaises(TypeError, int, mock)
        self.assertRaises(TypeError, int, mock.attr)
        self.assertEqual(list(mock), [])

        self.assertIsInstance(mock['foo'], MagicMock)
        self.assertIsInstance(mock.attr['foo'], MagicMock)


    eleza test_spec_set(self):
        kundi Sub(SomeClass):
            attr = SomeClass()

        kila spec kwenye (Sub, Sub()):
            mock = create_autospec(spec, spec_set=Kweli)
            self._check_someclass_mock(mock)

            self.assertRaises(AttributeError, setattr, mock, 'foo', 'bar')
            self.assertRaises(AttributeError, setattr, mock.attr, 'foo', 'bar')


    eleza test_descriptors(self):
        kundi Foo(object):
            @classmethod
            eleza f(cls, a, b): pita
            @staticmethod
            eleza g(a, b): pita

        kundi Bar(Foo): pita

        kundi Baz(SomeClass, Bar): pita

        kila spec kwenye (Foo, Foo(), Bar, Bar(), Baz, Baz()):
            mock = create_autospec(spec)
            mock.f(1, 2)
            mock.f.assert_called_once_with(1, 2)

            mock.g(3, 4)
            mock.g.assert_called_once_with(3, 4)


    eleza test_recursive(self):
        kundi A(object):
            eleza a(self): pita
            foo = 'foo bar baz'
            bar = foo

        A.B = A
        mock = create_autospec(A)

        mock()
        self.assertUongo(mock.B.called)

        mock.a()
        mock.B.a()
        self.assertEqual(mock.method_calls, [call.a(), call.B.a()])

        self.assertIs(A.foo, A.bar)
        self.assertIsNot(mock.foo, mock.bar)
        mock.foo.lower()
        self.assertRaises(AssertionError, mock.bar.lower.assert_called_with)


    eleza test_spec_inheritance_for_classes(self):
        kundi Foo(object):
            eleza a(self, x): pita
            kundi Bar(object):
                eleza f(self, y): pita

        class_mock = create_autospec(Foo)

        self.assertIsNot(class_mock, class_mock())

        kila this_mock kwenye class_mock, class_mock():
            this_mock.a(x=5)
            this_mock.a.assert_called_with(x=5)
            this_mock.a.assert_called_with(5)
            self.assertRaises(TypeError, this_mock.a, 'foo', 'bar')
            self.assertRaises(AttributeError, getattr, this_mock, 'b')

        instance_mock = create_autospec(Foo())
        instance_mock.a(5)
        instance_mock.a.assert_called_with(5)
        instance_mock.a.assert_called_with(x=5)
        self.assertRaises(TypeError, instance_mock.a, 'foo', 'bar')
        self.assertRaises(AttributeError, getattr, instance_mock, 'b')

        # The rudisha value isn't isn't callable
        self.assertRaises(TypeError, instance_mock)

        instance_mock.Bar.f(6)
        instance_mock.Bar.f.assert_called_with(6)
        instance_mock.Bar.f.assert_called_with(y=6)
        self.assertRaises(AttributeError, getattr, instance_mock.Bar, 'g')

        instance_mock.Bar().f(6)
        instance_mock.Bar().f.assert_called_with(6)
        instance_mock.Bar().f.assert_called_with(y=6)
        self.assertRaises(AttributeError, getattr, instance_mock.Bar(), 'g')


    eleza test_inherit(self):
        kundi Foo(object):
            a = 3

        Foo.Foo = Foo

        # class
        mock = create_autospec(Foo)
        instance = mock()
        self.assertRaises(AttributeError, getattr, instance, 'b')

        attr_instance = mock.Foo()
        self.assertRaises(AttributeError, getattr, attr_instance, 'b')

        # instance
        mock = create_autospec(Foo())
        self.assertRaises(AttributeError, getattr, mock, 'b')
        self.assertRaises(TypeError, mock)

        # attribute instance
        call_result = mock.Foo()
        self.assertRaises(AttributeError, getattr, call_result, 'b')


    eleza test_builtins(self):
        # used to fail ukijumuisha infinite recursion
        create_autospec(1)

        create_autospec(int)
        create_autospec('foo')
        create_autospec(str)
        create_autospec({})
        create_autospec(dict)
        create_autospec([])
        create_autospec(list)
        create_autospec(set())
        create_autospec(set)
        create_autospec(1.0)
        create_autospec(float)
        create_autospec(1j)
        create_autospec(complex)
        create_autospec(Uongo)
        create_autospec(Kweli)


    eleza test_function(self):
        eleza f(a, b): pita

        mock = create_autospec(f)
        self.assertRaises(TypeError, mock)
        mock(1, 2)
        mock.assert_called_with(1, 2)
        mock.assert_called_with(1, b=2)
        mock.assert_called_with(a=1, b=2)

        f.f = f
        mock = create_autospec(f)
        self.assertRaises(TypeError, mock.f)
        mock.f(3, 4)
        mock.f.assert_called_with(3, 4)
        mock.f.assert_called_with(a=3, b=4)


    eleza test_skip_attributeerrors(self):
        kundi Raiser(object):
            eleza __get__(self, obj, type=Tupu):
                ikiwa obj ni Tupu:
                    ashiria AttributeError('Can only be accessed via an instance')

        kundi RaiserClass(object):
            ashiriar = Raiser()

            @staticmethod
            eleza existing(a, b):
                rudisha a + b

        self.assertEqual(RaiserClass.existing(1, 2), 3)
        s = create_autospec(RaiserClass)
        self.assertRaises(TypeError, lambda x: s.existing(1, 2, 3))
        self.assertEqual(s.existing(1, 2), s.existing.rudisha_value)
        self.assertRaises(AttributeError, lambda: s.nonexisting)

        # check we can fetch the ashiriar attribute na it has no spec
        obj = s.ashiriar
        obj.foo, obj.bar


    eleza test_signature_class(self):
        kundi Foo(object):
            eleza __init__(self, a, b=3): pita

        mock = create_autospec(Foo)

        self.assertRaises(TypeError, mock)
        mock(1)
        mock.assert_called_once_with(1)
        mock.assert_called_once_with(a=1)
        self.assertRaises(AssertionError, mock.assert_called_once_with, 2)

        mock(4, 5)
        mock.assert_called_with(4, 5)
        mock.assert_called_with(a=4, b=5)
        self.assertRaises(AssertionError, mock.assert_called_with, a=5, b=4)


    eleza test_class_with_no_init(self):
        # this used to ashiria an exception
        # due to trying to get a signature kutoka object.__init__
        kundi Foo(object):
            pita
        create_autospec(Foo)


    eleza test_signature_callable(self):
        kundi Callable(object):
            eleza __init__(self, x, y): pita
            eleza __call__(self, a): pita

        mock = create_autospec(Callable)
        mock(1, 2)
        mock.assert_called_once_with(1, 2)
        mock.assert_called_once_with(x=1, y=2)
        self.assertRaises(TypeError, mock, 'a')

        instance = mock(1, 2)
        self.assertRaises(TypeError, instance)
        instance(a='a')
        instance.assert_called_once_with('a')
        instance.assert_called_once_with(a='a')
        instance('a')
        instance.assert_called_with('a')
        instance.assert_called_with(a='a')

        mock = create_autospec(Callable(1, 2))
        mock(a='a')
        mock.assert_called_once_with(a='a')
        self.assertRaises(TypeError, mock)
        mock('a')
        mock.assert_called_with('a')


    eleza test_signature_noncallable(self):
        kundi NonCallable(object):
            eleza __init__(self):
                pita

        mock = create_autospec(NonCallable)
        instance = mock()
        mock.assert_called_once_with()
        self.assertRaises(TypeError, mock, 'a')
        self.assertRaises(TypeError, instance)
        self.assertRaises(TypeError, instance, 'a')

        mock = create_autospec(NonCallable())
        self.assertRaises(TypeError, mock)
        self.assertRaises(TypeError, mock, 'a')


    eleza test_create_autospec_none(self):
        kundi Foo(object):
            bar = Tupu

        mock = create_autospec(Foo)
        none = mock.bar
        self.assertNotIsInstance(none, type(Tupu))

        none.foo()
        none.foo.assert_called_once_with()


    eleza test_autospec_functions_with_self_in_odd_place(self):
        kundi Foo(object):
            eleza f(a, self): pita

        a = create_autospec(Foo)
        a.f(10)
        a.f.assert_called_with(10)
        a.f.assert_called_with(self=10)
        a.f(self=10)
        a.f.assert_called_with(10)
        a.f.assert_called_with(self=10)


    eleza test_autospec_data_descriptor(self):
        kundi Descriptor(object):
            eleza __init__(self, value):
                self.value = value

            eleza __get__(self, obj, cls=Tupu):
                rudisha self

            eleza __set__(self, obj, value): pita

        kundi MyProperty(property):
            pita

        kundi Foo(object):
            __slots__ = ['slot']

            @property
            eleza prop(self): pita

            @MyProperty
            eleza subprop(self): pita

            desc = Descriptor(42)

        foo = create_autospec(Foo)

        eleza check_data_descriptor(mock_attr):
            # Data descriptors don't have a spec.
            self.assertIsInstance(mock_attr, MagicMock)
            mock_attr(1, 2, 3)
            mock_attr.abc(4, 5, 6)
            mock_attr.assert_called_once_with(1, 2, 3)
            mock_attr.abc.assert_called_once_with(4, 5, 6)

        # property
        check_data_descriptor(foo.prop)
        # property subclass
        check_data_descriptor(foo.subprop)
        # kundi __slot__
        check_data_descriptor(foo.slot)
        # plain data descriptor
        check_data_descriptor(foo.desc)


    eleza test_autospec_on_bound_builtin_function(self):
        meth = types.MethodType(time.ctime, time.time())
        self.assertIsInstance(meth(), str)
        mocked = create_autospec(meth)

        # no signature, so no spec to check against
        mocked()
        mocked.assert_called_once_with()
        mocked.reset_mock()
        mocked(4, 5, 6)
        mocked.assert_called_once_with(4, 5, 6)


    eleza test_autospec_getattr_partial_function(self):
        # bpo-32153 : getattr rudishaing partial functions without
        # __name__ should sio create AttributeError kwenye create_autospec
        kundi Foo:

            eleza __getattr__(self, attribute):
                rudisha partial(lambda name: name, attribute)

        proxy = Foo()
        autospec = create_autospec(proxy)
        self.assertUongo(hasattr(autospec, '__name__'))


    eleza test_spec_inspect_signature(self):

        eleza myfunc(x, y): pita

        mock = create_autospec(myfunc)
        mock(1, 2)
        mock(x=1, y=2)

        self.assertEqual(inspect.signature(mock), inspect.signature(myfunc))
        self.assertEqual(mock.mock_calls, [call(1, 2), call(x=1, y=2)])
        self.assertRaises(TypeError, mock, 1)


    eleza test_spec_inspect_signature_annotations(self):

        eleza foo(a: int, b: int=10, *, c:int) -> int:
            rudisha a + b + c

        self.assertEqual(foo(1, 2 , c=3), 6)
        mock = create_autospec(foo)
        mock(1, 2, c=3)
        mock(1, c=3)

        self.assertEqual(inspect.signature(mock), inspect.signature(foo))
        self.assertEqual(mock.mock_calls, [call(1, 2, c=3), call(1, c=3)])
        self.assertRaises(TypeError, mock, 1)
        self.assertRaises(TypeError, mock, 1, 2, 3, c=4)


    eleza test_spec_function_no_name(self):
        func = lambda: 'nope'
        mock = create_autospec(func)
        self.assertEqual(mock.__name__, 'funcopy')


    eleza test_spec_function_assert_has_calls(self):
        eleza f(a): pita
        mock = create_autospec(f)
        mock(1)
        mock.assert_has_calls([call(1)])
        ukijumuisha self.assertRaises(AssertionError):
            mock.assert_has_calls([call(2)])


    eleza test_spec_function_assert_any_call(self):
        eleza f(a): pita
        mock = create_autospec(f)
        mock(1)
        mock.assert_any_call(1)
        ukijumuisha self.assertRaises(AssertionError):
            mock.assert_any_call(2)


    eleza test_spec_function_reset_mock(self):
        eleza f(a): pita
        rv = Mock()
        mock = create_autospec(f, rudisha_value=rv)
        mock(1)(2)
        self.assertEqual(mock.mock_calls, [call(1)])
        self.assertEqual(rv.mock_calls, [call(2)])
        mock.reset_mock()
        self.assertEqual(mock.mock_calls, [])
        self.assertEqual(rv.mock_calls, [])


kundi TestCallList(unittest.TestCase):

    eleza test_args_list_contains_call_list(self):
        mock = Mock()
        self.assertIsInstance(mock.call_args_list, _CallList)

        mock(1, 2)
        mock(a=3)
        mock(3, 4)
        mock(b=6)

        kila kall kwenye call(1, 2), call(a=3), call(3, 4), call(b=6):
            self.assertIn(kall, mock.call_args_list)

        calls = [call(a=3), call(3, 4)]
        self.assertIn(calls, mock.call_args_list)
        calls = [call(1, 2), call(a=3)]
        self.assertIn(calls, mock.call_args_list)
        calls = [call(3, 4), call(b=6)]
        self.assertIn(calls, mock.call_args_list)
        calls = [call(3, 4)]
        self.assertIn(calls, mock.call_args_list)

        self.assertNotIn(call('fish'), mock.call_args_list)
        self.assertNotIn([call('fish')], mock.call_args_list)


    eleza test_call_list_str(self):
        mock = Mock()
        mock(1, 2)
        mock.foo(a=3)
        mock.foo.bar().baz('fish', cat='dog')

        expected = (
            "[call(1, 2),\n"
            " call.foo(a=3),\n"
            " call.foo.bar(),\n"
            " call.foo.bar().baz('fish', cat='dog')]"
        )
        self.assertEqual(str(mock.mock_calls), expected)


    eleza test_propertymock(self):
        p = patch('%s.SomeClass.one' % __name__, new_callable=PropertyMock)
        mock = p.start()
        jaribu:
            SomeClass.one
            mock.assert_called_once_with()

            s = SomeClass()
            s.one
            mock.assert_called_with()
            self.assertEqual(mock.mock_calls, [call(), call()])

            s.one = 3
            self.assertEqual(mock.mock_calls, [call(), call(), call(3)])
        mwishowe:
            p.stop()


    eleza test_propertymock_rudishavalue(self):
        m = MagicMock()
        p = PropertyMock()
        type(m).foo = p

        rudishaed = m.foo
        p.assert_called_once_with()
        self.assertIsInstance(rudishaed, MagicMock)
        self.assertNotIsInstance(rudishaed, PropertyMock)


kundi TestCallablePredicate(unittest.TestCase):

    eleza test_type(self):
        kila obj kwenye [str, bytes, int, list, tuple, SomeClass]:
            self.assertKweli(_callable(obj))

    eleza test_call_magic_method(self):
        kundi Callable:
            eleza __call__(self): pita
        instance = Callable()
        self.assertKweli(_callable(instance))

    eleza test_staticmethod(self):
        kundi WithStaticMethod:
            @staticmethod
            eleza staticfunc(): pita
        self.assertKweli(_callable(WithStaticMethod.staticfunc))

    eleza test_non_callable_staticmethod(self):
        kundi BadStaticMethod:
            not_callable = staticmethod(Tupu)
        self.assertUongo(_callable(BadStaticMethod.not_callable))

    eleza test_classmethod(self):
        kundi WithClassMethod:
            @classmethod
            eleza classfunc(cls): pita
        self.assertKweli(_callable(WithClassMethod.classfunc))

    eleza test_non_callable_classmethod(self):
        kundi BadClassMethod:
            not_callable = classmethod(Tupu)
        self.assertUongo(_callable(BadClassMethod.not_callable))


ikiwa __name__ == '__main__':
    unittest.main()
